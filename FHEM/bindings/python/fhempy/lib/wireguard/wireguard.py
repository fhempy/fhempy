"""WireGuard VPN server for people without network know-how.

fhempy creates all keys, finds a VPN network which doesn't collide with the
home network, the public address (or the name of a ddnssde device) and asks
the router via UPnP for the port forwarding. A new device (phone, laptop)
gets a QR code for the WireGuard app. Connected devices, last handshake and
traffic are readings.

Root rights (interface, IP forwarding, NAT) only through the small helper
helper.py, installed once with sudo (command on the device page).
"""

import asyncio
import base64
import collections
import functools
import html
import ipaddress
import json
import os
import pwd
import re
import shlex
import socket
import time

import aiohttp

from .. import fhem, fhem_pythonbinding, generic, utils
from . import helper, keys, network, remote

ICON = "secur_locked"
DEFAULT_PORT = 51820
TOOL_DIRS = ("/usr/bin", "/bin", "/usr/sbin", "/sbin")
# WireGuard sends a handshake every 2 minutes while traffic flows, clients
# get PersistentKeepalive, without handshake for this long it's disconnected
CONNECTED_SECONDS = 180
KEEPALIVE = 25
# while the one-time setup is missing: check if it's done
SETUP_INTERVAL = 10
# public address, DynDNS and port forwarding
NETWORK_INTERVAL = 3600
# devices of another site with internet through home: routing table and
# priority of the ip rules on the Pi of that site
VIA_TABLE = 51820
VIA_PRIORITY = 5180
MAX_VIA_HOME = 16
# an address of a device at another site instead of its network: home
# routers give out /24 networks
DEVICE_PREFIX = 24
# via_home: every device which uses the Pi of the site as gateway
VIA_HOME_ALL = "all"
# access=internet: only the internet through home, no device at home
ACCESS_INTERNET = "internet"
ACCESS_OPTIONS = (ACCESS_INTERNET, "all")
# the installed helper must be at least this version, internet only peers
# need the firewall rules of version 2 (an older helper would ignore them)
MIN_HELPER_VERSION = 1
ISOLATION_HELPER_VERSION = 2
CLIENT_NAME = re.compile(r"^[A-Za-z0-9_-]{1,24}$")
RESERVED_NAMES = {"state", "clients", "port", "endpoint", "public"}
# live log of the setup via SSH (reading setup_log, terminal on the page)
LOG_LINES = 80
LOG_LINE_LENGTH = 200
LOG_DELAY = 0.3
# live speed on the device page: it asks every TRAFFIC_POLL seconds, more
# pages at the same time share one wg show within TRAFFIC_CACHE seconds
TRAFFIC_POLL = 2
TRAFFIC_CACHE = 1


def is_root():
    return os.geteuid() == 0


def current_user():
    try:
        return pwd.getpwuid(os.geteuid()).pw_name
    except KeyError:
        return str(os.geteuid())


def tool(name):
    for directory in TOOL_DIRS:
        path = os.path.join(directory, name)
        if os.access(path, os.X_OK):
            return path
    return None


async def run_command(args, stdin=None, limit=120):
    """(exit code, output), 127 if the program doesn't exist"""
    if args[0] is None:
        return 127, "program not found"
    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdin=asyncio.subprocess.PIPE if stdin else asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env={"PATH": ":".join(TOOL_DIRS), "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8"},
        )
    except OSError as err:
        return 127, str(err)
    try:
        async with asyncio.timeout(limit):
            out, _ = await proc.communicate(stdin.encode() if stdin else None)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        return 124, f"{os.path.basename(args[0])} did not finish within {limit}s"
    return proc.returncode, out.decode("utf-8", "replace")


def last_line(text):
    lines = [line.strip() for line in str(text).splitlines() if line.strip()]
    return lines[-1] if lines else ""


def parse_dump(text):
    """peers of wg show <interface> dump: {public_key: info}"""
    peers = {}
    for line in text.splitlines()[1:]:
        fields = line.split("\t")
        if len(fields) < 8:
            continue
        endpoint = fields[2] if fields[2] != "(none)" else ""
        peers[fields[0]] = {
            "endpoint": endpoint,
            "handshake": int(fields[4] or 0),
            "rx": int(fields[5] or 0),
            "tx": int(fields[6] or 0),
        }
    return peers


def endpoint_ip(endpoint):
    """IP of '1.2.3.4:5678' or '[2001:db8::1]:5678'"""
    host = endpoint.rsplit(":", 1)[0].strip("[]")
    try:
        return ipaddress.ip_address(host)
    except ValueError:
        return None


def megabytes(value):
    return round(value / 1_000_000, 1)


def format_time(timestamp):
    if not timestamp:
        return "never"
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))


FORM_STYLE = """<style>
.wgForms{display:flex;flex-wrap:wrap;align-items:flex-start;gap:12px;margin:12px 0}
.wgCard{flex:1 1 300px;max-width:460px;border:1px solid #ccc;border-radius:8px;
padding:12px 14px;box-sizing:border-box}
.wgCard h4{margin:0 0 4px}
.wgCard p{margin:0 0 10px;opacity:.8}
.wgCard label{display:block;margin:8px 0 2px;font-weight:bold}
.wgCard input,.wgCard select{display:block;width:100%;box-sizing:border-box;margin-top:3px;
padding:6px 8px;font-weight:normal}
.wgCard small{display:block;opacity:.7}
.wgCard [hidden]{display:none}
.wgDevices{border-collapse:collapse;margin:4px 0;min-width:min(100%,520px)}
.wgDevices th,.wgDevices td{padding:4px 10px;text-align:left;vertical-align:top}
.wgDevices thead th{border-bottom:1px solid #ccc}
.wgDevices tbody.wgDev{border-bottom:1px solid #ccc}
.wgDevices td.wgDown,.wgDevices td.wgUp,.wgDevices th.wgNum{text-align:right;font-family:monospace;white-space:nowrap}
.wgDevices tfoot td{font-weight:bold;border-top:2px solid #ccc}
.wgDevices small{display:block;opacity:.7}
.wgDevices tr.wgMore td{padding-top:0}
.wgWhere{border:1px solid #ccc;border-radius:6px;margin:10px 0 4px;padding:4px 10px 8px}
.wgWhere legend{font-weight:bold;padding:0 4px}
.wgNote{border:1px solid #c80;border-radius:6px;padding:6px 10px;margin:4px 0}
.wgNote button{margin-left:6px;cursor:pointer}
.wgCard label.wgCheck{font-weight:bold;display:flex;gap:6px;align-items:center}
.wgCard label.wgCheck input{display:inline;width:auto;margin:0}
.wgRow{display:flex;gap:8px}
.wgGrow{flex:1}
.wgPort{width:90px}
.wgCard button{margin-top:12px;padding:7px 16px;cursor:pointer}
.wgShell{background:#1e1e1e;color:#d4d4d4;font:12px/1.4 monospace;padding:8px 10px;
border-radius:6px;max-height:320px;overflow:auto;white-space:pre-wrap;
word-break:break-all;margin:12px 0;max-width:932px;box-sizing:border-box}
.wgLogBack{position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:10000;
display:none;align-items:center;justify-content:center}
.wgLogBack.wgOpen{display:flex}
.wgLogBox{background:#1e1e1e;border-radius:8px;width:min(920px,94vw);
box-shadow:0 8px 32px rgba(0,0,0,.5);overflow:hidden}
.wgLogHead{display:flex;align-items:center;gap:8px;padding:8px 12px;
background:#333;color:#eee;font:bold 13px sans-serif}
.wgLogHead span{flex:1}
.wgLogHead button{background:none;border:0;color:#eee;font-size:20px;
line-height:1;cursor:pointer;padding:0 4px}
.wgLogBox .wgShell{margin:0;border-radius:0;height:min(480px,70vh);
max-height:none;max-width:none;overflow-y:scroll}
.wgShell>span{display:block}
.wgShell .wgCmd{color:#fff;font-weight:bold;background:#2a2d2e;
border-left:3px solid #4ec94e;margin:6px -10px 2px;padding:1px 10px 1px 7px}
.wgShell .wgPrompt{color:#4ec94e}
.wgShell .wgInfo{color:#6a9fb5;font-style:italic}
.wgShell .wgOk{color:#4ec94e;font-weight:bold}
.wgShell .wgErr{color:#f14c4c;font-weight:bold}
.wgLogBtn{margin:8px 0;padding:5px 12px;cursor:pointer}
.wgShell pre{margin:0;font:inherit;white-space:pre-wrap}
</style>"""
# popup with the live log: opens when a setup starts (form) or when new
# lines arrive, closed it stays closed until the next setup (new first line)
LOG_SCRIPT = """<script>
(function() {
  var back = document.querySelector(".wgLogBack");
  if (!back) return;
  var pre = back.querySelector("pre.wgShell");
  var closedRun = null, text = pre.textContent;
  function firstLine() { return text.split("\\n")[0]; }
  function esc(t) {
    return t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
  /* commands like in a terminal: prompt user@host:~$ in green, command bold
     on a highlighted line, comments of fhempy (#) blue, done green, errors red */
  function render() {
    var prompt = "$";
    pre.innerHTML = text.split("\\n").map(function(line) {
      var ssh = /^# ssh (\\S+)/.exec(line), kind = "", body = esc(line) || " ";
      if (ssh) prompt = ssh[1] + ":~$";
      if (line.slice(0, 2) == "$ ") {
        kind = "wgCmd";
        body = "<span class='wgPrompt'>" + esc(prompt) + "</span> "
          + esc(line.slice(2));
      } else if (/^# (done|connected)/.test(line)) {
        kind = "wgOk";
      } else if (/^# (failed|took too long)|^(E:|error|Error)/.test(line)) {
        kind = "wgErr";
      } else if (line.charAt(0) == "#") {
        kind = "wgInfo";
      }
      return "<span class='" + kind + "'>" + body + "</span>";
    }).join("");
    pre.scrollTop = pre.scrollHeight;
  }
  window.wgLogOpen = function() {
    closedRun = null;
    back.classList.add("wgOpen");
    pre.scrollTop = pre.scrollHeight;
  };
  window.wgLogClose = function() {
    closedRun = firstLine();
    back.classList.remove("wgOpen");
  };
  document.addEventListener("keydown", function(e) {
    if (e.key == "Escape" && back.classList.contains("wgOpen")) wgLogClose();
  });
  /* FHEMWEB hands new values of the reading to setValueFn (newlines as
     U+2424) instead of replacing the content */
  pre.setValueFn = function(value) {
    text = String(value).replace(/\\u2424/g, "\\n");
    render();
    if (closedRun === null || firstLine() != closedRun) {
      back.classList.add("wgOpen");
    }
  };
  render();
})();
</script>"""
# live speed of the connected devices while the page is open and visible
SPEED_SCRIPT = """<script>
(function() {
  var last = null;
  function rate(bytes, seconds) {
    var bit = bytes * 8 / seconds;
    if (bit >= 1e6) return (bit / 1e6).toFixed(1) + " Mbit/s";
    return Math.round(bit / 1e3) + " kbit/s";
  }
  function set(selector, text) {
    var e = document.querySelector(selector);
    if (e) e.textContent = text;
  }
  function show(data) {
    var seconds = last ? data.time - last.time : 0;
    var down = 0, up = 0, measured = false;
    document.querySelectorAll(".wgDevices td.wgDown").forEach(function(e) {
      var name = e.dataset.client, up_cell = e.nextElementSibling;
      var now = data.clients[name], before = last && last.clients[name];
      if (!now) { e.textContent = "\u2013"; up_cell.textContent = "\u2013"; return; }
      if (!before || seconds <= 0) return;
      var d = Math.max(0, now.down - before.down), u = Math.max(0, now.up - before.up);
      down += d; up += u; measured = true;
      e.textContent = rate(d, seconds);
      up_cell.textContent = rate(u, seconds);
    });
    if (seconds > 0) {
      set(".wgDevices .wgTotalDown", measured ? rate(down, seconds) : "\u2013");
      set(".wgDevices .wgTotalUp", measured ? rate(up, seconds) : "\u2013");
    }
    if (!last || data.time > last.time) last = data;
  }
  function poll() {
    if (!document.querySelector(".wgDevices")) return;
    if (document.visibilityState == "visible") {
      FW_cmd(FW_root + "?cmd=" + encodeURIComponent("get " + DEVICE + " traffic")
        + "&XHR=1", function(r) {
          try { show(JSON.parse(r)); } catch (err) {}
        });
    }
    setTimeout(poll, POLL);
  }
  poll();
})();
</script>"""
# sends the form as set command, values with spaces in quotes, ; doubled
FORM_SCRIPT = """<script>
function wgWhere(radio) {
  var form = radio.form, home = radio.value == "home";
  form.querySelectorAll(".wgHome").forEach(function(e) { e.hidden = !home; });
  form.querySelectorAll(".wgThere").forEach(function(e) { e.hidden = home; });
  if (!home) form.elements.namedItem("network").value = "";
}
function wgFillSite(name, host) {
  var form = document.querySelector("form.wgSite");
  if (!form) return;
  form.elements.namedItem("name").value = name;
  form.elements.namedItem("host").value = host;
  var there = form.querySelector("input[name=wg_where][value=there]");
  there.checked = true;
  wgWhere(there);
  form.scrollIntoView({block: "center"});
  form.elements.namedItem("password").focus();
}
function wgSend(form, dev, cmd) {
  var parts = ["set", dev, cmd, form.elements.namedItem("name").value];
  for (var i = 0; i < form.elements.length; i++) {
    var e = form.elements[i];
    if (!e.name || e.name == "name" || !e.value) continue;
    if (e.type == "checkbox" && !e.checked) continue;
    if (/^wg_/.test(e.name)) continue;
    var v = e.value.replace(/;/g, ";;");
    if (/[\\s"]/.test(v)) v = '"' + v.replace(/"/g, '\\\\"') + '"';
    parts.push(e.name + "=" + v);
  }
  FW_cmd(FW_root + "?cmd=" + encodeURIComponent(parts.join(" ")) + "&XHR=1",
    function(r) {
      if (r && /^Setting up/.test(r) && window.wgLogOpen) {
        wgLogOpen();
      } else if (r) {
        if (!/^<html>/.test(r)) r = "<pre>" + FW_htmlQuote(r) + "</pre>";
        FW_okDialog(r);
      }
      var pw = form.elements.namedItem("password");
      if (pw) pw.value = "";
    });
  return false;
}
</script>"""


SITE_MODES = ("networks", "internet_only")


def is_site(client):
    return bool(client.get("networks") or client.get("internet_only"))


def site_network(client):
    """network of a site, also when it isn't routed (internet_only)"""
    return client.get("site_network") or client["networks"][0]


def ssh_port(value):
    if value in (None, ""):
        return remote.DEFAULT_SSH_PORT
    try:
        port = int(str(value))
    except ValueError:
        raise remote.RemoteError(f"invalid SSH port {value}") from None
    if not 1 <= port <= 65535:
        raise remote.RemoteError(f"invalid SSH port {value}")
    return port


def valid_port(value):
    value = str(value or "").strip()
    if not value:
        return None
    port = int(value)
    if not 1 <= port <= 65535:
        raise ValueError("port must be 1-65535")
    return port


def udp_port_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        try:
            sock.bind(("0.0.0.0", port))
        except OSError:
            return False
    return True


def free_port():
    for port in range(DEFAULT_PORT, DEFAULT_PORT + 20):
        if udp_port_free(port):
            return port
    return DEFAULT_PORT


def data_directory():
    return os.path.join(os.getcwd(), ".fhempy", "wireguard")


def read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def write_private_json(path, data):
    """keys inside: only readable for the fhempy user"""
    os.makedirs(os.path.dirname(path), mode=0o700, exist_ok=True)
    tmp = path + ".tmp"
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
    os.replace(tmp, path)


def resolve(host):
    try:
        infos = socket.getaddrinfo(host, None, socket.AF_INET)
    except OSError:
        return set()
    return {info[4][0] for info in infos}


def qr_image(text):
    import segno

    uri = segno.make(text, micro=False, error="l").png_data_uri(
        scale=4, border=4, dark="#000", light="#fff"
    )
    return (
        f'<img src="{uri}" alt="QR code" '
        'style="width:240px;height:240px;max-width:none;image-rendering:pixelated">'
    )


class wireguard(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self._lock = asyncio.Lock()
        self.config = {}
        self.net = {}
        self.peers = {}
        self.public_ip = None
        self.router_ip = None
        self.forwarding = ""
        self.problem = ""
        self.running = False
        self.internet_ok = 0
        self.helper_problem = "not checked yet"
        self.helper_version = 0
        self.user = current_user()
        self.router = network.Router(logger)
        self.session = None
        self._started = False
        self.setup_task = None
        self.setup_state = ""
        self.log_lines = collections.deque(maxlen=LOG_LINES)
        self.traffic_time = 0
        self.log_pending = False

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        self.hash = hash
        await super().Define(hash, args, argsh)
        await self.set_attr_config(
            {
                "client_traffic": {
                    "default": "home",
                    "options": "home,all",
                    "help": "What the devices send through the VPN:<br>"
                    "home: only to the home network, internet traffic goes "
                    "directly (default, fast)<br>all: everything, also "
                    "internet traffic (safe in public WiFi, slower). "
                    "Devices must be set up again (new QR code).",
                },
                "endpoint": {
                    "default": "",
                    "help": "Internet address of your home for the devices, "
                    "e.g. a DynDNS name like myhome.ddnss.de. Empty "
                    "(default): name of a ddnssde device, otherwise the "
                    "current public IP address.",
                },
                "port": {
                    "default": "",
                    "format": valid_port,
                    "help": "UDP port of the VPN server, empty (default): "
                    "51820 or the next free one.",
                },
                "port_forwarding": {
                    "default": "upnp",
                    "options": "upnp,manual",
                    "help": "upnp (default): fhempy asks the router to forward "
                    "the port (FRITZ!Box: allow independent port sharing for "
                    "this device). manual: you set it up in the router.",
                },
                "interval": {
                    "default": 30,
                    "format": "int",
                    "help": "Seconds between the updates of the connected "
                    "devices, default 30.",
                },
            }
        )
        await self.set_set_config(
            {
                "add_client": {
                    "args": ["name"],
                    "argsh": ["network", "access"],
                    "help": "Add a device (phone, laptop...), e.g. "
                    "<code>add_client Phone</code>. Shows the QR code for the "
                    "WireGuard app.<br>access=internet: only the internet "
                    "goes through home, no access to the devices at home "
                    "(e.g. for guests).<br>Another site (e.g. a Raspberry Pi in a "
                    "holiday home) with its home network: <code>add_client "
                    "Holiday network=192.168.2.0/24</code>",
                },
                "remove_client": {
                    "args": ["name"],
                    "help": "Remove a device, it can't connect anymore.",
                },
                "add_site": {
                    "args": ["name"],
                    "argsh": [
                        "host",
                        "port",
                        "user",
                        "password",
                        "network",
                        "via_home",
                        "mode",
                        "access",
                    ],
                    "help": "Connect another site automatically: fhempy logs "
                    "in to its Raspberry Pi via SSH, installs WireGuard and "
                    "connects it, e.g. <code>add_site Holiday "
                    "host=192.168.1.77 user=pi password=secret</code>.<br>"
                    "host: address of that Pi from here (e.g. while it is "
                    "still in your home network), port: SSH port (22).<br>"
                    "The home network of the site is detected (network="
                    "192.168.2.0/24 sets it by hand), the same network as at "
                    "home gives a warning: only the Pi is connected. The "
                    "password is not stored. Easier: the form on the device "
                    "page."
                    "<br>via_home=all: every device which uses the Pi as "
                    "gateway / router (e.g. a TV) gets its internet through "
                    "your home, the Pi itself and all other devices stay "
                    "direct. Or only some addresses: via_home=192.168.2.50,"
                    "192.168.2.51. Run add_site again to change it."
                    "<br>mode=internet_only: only the internet of the "
                    "via_home devices goes through home, the two home networks "
                    "aren't connected. For sites with the same network as "
                    "home (e.g. both 192.168.178.0/24), chosen automatically "
                    "then. mode=networks: connect both networks (default)."
                    "<br>access=internet: the via_home devices only get "
                    "internet through home, no access to the devices at home "
                    "(needs via_home, the networks aren't connected).",
                },
                "setup": {
                    "argsh": ["user", "password"],
                    "help": "One-time setup of this computer without "
                    "command line: <code>setup user=pi password=secret</code> "
                    "(a user with sudo rights, SSH must be enabled). The "
                    "password is not stored.",
                },
                "start": {"help": "Start the VPN server (again)."},
                "stop": {
                    "help": "Stop the VPN server, also after a reboot. Run it "
                    "before you delete this device."
                },
            }
        )
        await self.set_get_config(
            {
                "client_config": {
                    "args": ["name"],
                    "help": "WireGuard configuration of a device as text.",
                },
                "traffic": {
                    "help": "Byte counters of the connected devices as JSON "
                    "(for the live speed on the device page).",
                },
            }
        )
        await self.set_icon(ICON)
        self.create_async_task(self.start())

    # FHEM FUNCTION
    async def Undefine(self, hash):
        # the VPN keeps running: Undefine also happens on every restart of
        # fhempy, clients must not lose the connection
        await super().Undefine(hash)
        if self.session is not None:
            await self.session.close()
            self.session = None

    # FHEM FUNCTION
    async def FW_detailFn(self, hash, args, argsh):
        detail = await super().FW_detailFn(hash, args, argsh)
        return self.detail_html() + str(detail or "")

    def set_attr_client_traffic(self, hash):
        if self._started:
            self.create_async_task(self.update_problem())

    def set_attr_port(self, hash):
        if self._started:
            self.create_async_task(self.restart_server())

    def set_attr_endpoint(self, hash):
        if self._started:
            self.create_async_task(self.check_network())

    def set_attr_port_forwarding(self, hash):
        if self._started:
            self.create_async_task(self.check_network())

    # --- state file ---

    def state_file(self):
        return os.path.join(data_directory(), self.hash["NAME"] + ".json")

    async def load_log(self):
        text = await fhem.ReadingsVal(self.hash["NAME"], "setup_log", "")
        self.log_lines.extend(str(text or "").splitlines())

    def start_log(self, title):
        """new live log, returns the function which adds a line"""
        self.log_lines.clear()
        self.log_lines.append(f"# {title} ({time.strftime('%Y-%m-%d %H:%M:%S')})")
        self.schedule_log()
        return self.log_line

    def log_line(self, line):
        self.log_lines.append(str(line)[:LOG_LINE_LENGTH])
        self.schedule_log()

    def schedule_log(self):
        """at most one reading update every LOG_DELAY seconds"""
        if not self.log_pending:
            self.log_pending = True
            self.create_async_task(self.flush_log(LOG_DELAY))

    async def flush_log(self, delay=0):
        if delay:
            await asyncio.sleep(delay)
        self.log_pending = False
        await self.set_readings(setup_log="\n".join(self.log_lines))

    async def load_config(self):
        config = await utils.run_blocking(
            functools.partial(read_json, self.state_file())
        )
        changed = False
        if not config.get("private_key"):
            config["private_key"] = keys.private_key()
            changed = True
        if not config.get("network"):
            config["network"] = self.net["vpn_network"]
            changed = True
        if not config.get("port"):
            config["port"] = await utils.run_blocking(functools.partial(free_port))
            changed = True
        config.setdefault("clients", {})
        config.setdefault("stopped", False)
        self.config = config
        if changed:
            await self.save_config()

    async def save_config(self):
        await utils.run_blocking(
            functools.partial(write_private_json, self.state_file(), self.config)
        )

    # --- addresses ---

    @property
    def port(self):
        return self._attr_port or self.config["port"]

    @property
    def vpn_network(self):
        return ipaddress.IPv4Network(self.config["network"])

    def server_address(self):
        net = self.vpn_network
        return f"{net.network_address + 1}/{net.prefixlen}"

    def next_client_ip(self):
        used = {c["ip"] for c in self.config["clients"].values()}
        hosts = list(self.vpn_network.hosts())[1:]
        for ip in hosts:
            if str(ip) not in used:
                return str(ip)
        return None

    def ddns_hostname(self):
        """hostname of a ddnssde device of fhempy which points to us"""
        names = []
        for inst in fhem_pythonbinding.loadedModuleInstances.copy().values():
            if getattr(inst, "hash", {}).get("FHEMPYTYPE") != "ddnssde":
                continue
            hostnames = getattr(inst, "hostnames", None) or {}
            selected = str(getattr(inst, "_attr_hostname", "") or "")
            for host, info in hostnames.items():
                ip = (info or {}).get("ip") if isinstance(info, dict) else None
                score = 2 if host.replace(".", "_") == selected else 0
                score += 1 if ip and ip == self.public_ip else 0
                names.append((score, host))
        names.sort(reverse=True)
        return names[0][1] if names else None

    def endpoint_host(self):
        return self._attr_endpoint or self.ddns_hostname() or self.public_ip

    def site_networks(self, exclude=None):
        return [
            net
            for name, client in self.config.get("clients", {}).items()
            if name != exclude
            for net in client.get("networks", [])
        ]

    def full_tunnel(self, name):
        """the device sends everything through home"""
        client = self.config["clients"][name]
        if is_site(client):
            return False
        return self._attr_client_traffic == "all" or bool(client.get("access"))

    def client_dns(self, name):
        gateway = self.net.get("gateway")
        if self.config["clients"][name].get("access"):
            # internet only: the router at home (DNS allowed) or a public one
            return gateway or "1.1.1.1"
        return gateway

    def allowed_ips(self, name):
        if self.full_tunnel(name):
            return "0.0.0.0/0, ::/0"
        nets = [str(self.vpn_network)]
        if self.net.get("home_network"):
            nets.append(self.net["home_network"])
        return ", ".join(nets + self.site_networks(exclude=name))

    def overlapping_network(self, net, name):
        """home network or network of another site which collides with net"""
        others = [ipaddress.IPv4Network(n) for n in self.site_networks(exclude=name)]
        if self.net.get("home_network"):
            others.insert(0, ipaddress.IPv4Network(self.net["home_network"]))
        net = ipaddress.IPv4Network(str(net), strict=False)
        return next((other for other in others if net.overlaps(other)), None)

    def check_site_network(self, value, name, internet_only=False):
        """the home network of another site, None if invalid. With
        internet_only it isn't routed, it may be the same as at home. The
        address of a device there means its /24 network (home routers)."""
        text = str(value).strip()
        if "/" not in text:
            text += f"/{DEVICE_PREFIX}"
        try:
            net = ipaddress.IPv4Network(text, strict=False)
        except ValueError:
            return None, (
                f"Invalid address or network {value}, e.g. 192.168.2.34 (a "
                "device at the other place) or 192.168.2.0/24"
            )
        if not net.is_private or net.prefixlen < 8:
            return None, f"{net} is not a private home network"
        other = self.vpn_network if net.overlaps(self.vpn_network) else None
        if other is None and not internet_only:
            other = self.overlapping_network(net, name)
        if other is not None:
            return None, (
                f"{net} overlaps {other}: every site needs its own network, "
                "change it in the router of that site (or mode=internet_only "
                "with via_home devices, if only their internet goes through "
                "home)"
            )
        return str(net), None

    def client_config(self, name):
        client = self.config["clients"][name]
        host = self.endpoint_host() or "YOUR-PUBLIC-ADDRESS"
        if ":" in host:
            host = f"[{host}]"
        lines = [
            "[Interface]",
            f"PrivateKey = {client['private_key']}",
            f"Address = {client['ip']}/32",
        ]
        site = is_site(client)
        if self.full_tunnel(name) and self.client_dns(name):
            lines.append(f"DNS = {self.client_dns(name)}")
        if site:
            lines += self.site_lines(name)
        lines += [
            "",
            "[Peer]",
            f"PublicKey = {keys.public_key(self.config['private_key'])}",
            f"PresharedKey = {client['preshared_key']}",
            f"Endpoint = {host}:{self.port}",
            f"AllowedIPs = {self.site_allowed_ips(name)}",
            f"PersistentKeepalive = {KEEPALIVE}",
        ]
        return "\n".join(lines) + "\n"

    def site_allowed_ips(self, name):
        client = self.config["clients"][name]
        if client.get("via_home"):
            return "0.0.0.0/0"
        if client.get("internet_only"):
            # same network as home: only the VPN
            return str(self.vpn_network)
        return self.allowed_ips(name)

    def site_lines(self, name):
        """the Pi of the other site forwards into its home network, devices
        in via_home use it as router: their internet goes through home"""
        client = self.config["clients"][name]
        out = "$(ip -4 route show default | awk '{print $5; exit}')"
        via_home = client.get("via_home") or []
        if client.get("internet_only"):
            return self.internet_only_lines(name)
        lines = []
        if via_home:
            # no default route for the Pi itself, only for these devices
            lines.append("Table = off")
        sources = [str(self.vpn_network)]
        if self.net.get("home_network"):
            sources.append(self.net["home_network"])
        for action, word in (("A", "PostUp"), ("D", "PostDown")):
            if action == "A":
                lines.append(f"{word} = sysctl -q -w net.ipv4.ip_forward=1")
            lines += [
                f"{word} = iptables -{action} FORWARD -i %i -j ACCEPT",
                f"{word} = iptables -{action} FORWARD -o %i -j ACCEPT",
            ]
            lines += [
                f"{word} = iptables -t nat -{action} POSTROUTING -s {net} "
                f"-o {out} -j MASQUERADE"
                for net in sources
            ]
            lines.append(
                f"{word} = iptables -t mangle -{action} FORWARD -p tcp "
                "--tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu"
            )
            if via_home:
                lines += self.via_home_lines(name, action, word)
        return lines

    def internet_only_lines(self, name):
        """the networks aren't connected: the Pi of the site sends the
        traffic of the via_home devices with its own VPN address (NAT), the
        VPN server doesn't need to know the network of the site"""
        lines = ["Table = off"]
        if not self.config["clients"][name].get("via_home"):
            # only the Pi itself is connected
            return lines + [f"PostUp = ip route add {self.vpn_network} dev %i"]
        for action, word in (("A", "PostUp"), ("D", "PostDown")):
            if action == "A":
                lines.append(f"{word} = sysctl -q -w net.ipv4.ip_forward=1")
            lines += [
                # nothing from home into the network of the site, only answers
                f"{word} = iptables -{action} FORWARD -i %i -m conntrack "
                "--ctstate RELATED,ESTABLISHED -j ACCEPT",
                f"{word} = iptables -{action} FORWARD -o %i -j ACCEPT",
                f"{word} = iptables -t nat -{action} POSTROUTING -o %i -j MASQUERADE",
                f"{word} = iptables -t mangle -{action} FORWARD -p tcp "
                "--tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu",
            ]
            lines += self.via_home_lines(name, action, word)
        return lines

    def via_home_lines(self, name, action, word):
        client = self.config["clients"][name]
        lines = []
        if action == "A":
            # answers from the internet come in on the VPN (loose reverse path)
            lines.append(
                f"{word} = sysctl -q -w net.ipv4.conf.all.rp_filter=2 "
                "net.ipv4.conf.%i.rp_filter=2"
            )
            if client.get("internet_only"):
                # the home network may be the network of the site itself
                nets = [str(self.vpn_network)]
            else:
                nets = self.allowed_ips(name).split(", ")
            lines += [f"{word} = ip route add {net} dev %i" for net in nets]
            lines.append(f"{word} = ip route add default dev %i table {VIA_TABLE}")
        verb = "add" if action == "A" else "del"
        for match in self.via_home_matches(client):
            # local destinations (network of the site) stay in the main table
            lines += [
                f"{word} = ip rule {verb} {match} lookup main "
                f"suppress_prefixlength 0 priority {VIA_PRIORITY}",
                f"{word} = ip rule {verb} {match} table {VIA_TABLE} "
                f"priority {VIA_PRIORITY + 1}",
            ]
        return lines

    @staticmethod
    def via_home_matches(client):
        """ip rule selectors: all = everything the Pi forwards from its home
        network (comes in on its network interface, its own traffic doesn't),
        else the addresses of single devices"""
        if client["via_home"] == VIA_HOME_ALL:
            dev = client.get("site_dev") or (
                "$(ip -4 route show default | awk '{print $5; exit}')"
            )
            return [f"iif {dev}"]
        return [f"from {ip}" for ip in client["via_home"]]

    def check_via_home(self, value, network, site_ip):
        """devices of the other site whose internet goes through home"""
        if not value:
            return [], None
        if str(value).strip().lower() in ("all", "yes", "on", "1", "true"):
            return VIA_HOME_ALL, None
        net = ipaddress.IPv4Network(network)
        ips = []
        for part in str(value).replace(";", ",").split(","):
            part = part.strip()
            if not part:
                continue
            try:
                ip = ipaddress.IPv4Address(part)
            except ValueError:
                return None, f"Invalid address {part} in via_home"
            if ip not in net or ip in (net.network_address, net.broadcast_address):
                return None, f"{ip} is not in the network {net} of the site"
            if site_ip and str(ip) == site_ip:
                return None, f"{ip} is the Pi of the site itself"
            if str(ip) not in ips:
                ips.append(str(ip))
        if len(ips) > MAX_VIA_HOME:
            return None, f"At most {MAX_VIA_HOME} devices in via_home"
        return ips, None

    # --- helper ---

    @staticmethod
    def helper_source():
        return os.path.abspath(helper.__file__)

    def setup_command(self):
        return (
            f"sudo python3 {shlex.quote(self.helper_source())} install "
            f"{shlex.quote(self.user)}"
        )

    def helper_command(self, *args):
        if is_root():
            return [tool("python3"), "-I", self.helper_source(), *args]
        return [tool("sudo"), "-n", helper.INSTALL_PATH, *args]

    async def run_helper(self, *args, stdin=None, limit=120):
        return await run_command(self.helper_command(*args), stdin, limit)

    async def check_helper(self):
        installed = await utils.run_blocking(
            functools.partial(os.path.exists, helper.INSTALL_PATH)
        )
        if not is_root() and not installed:
            problem = "helper not installed"
        elif not is_root() and tool("sudo") is None:
            problem = "sudo is not installed"
        else:
            code, out = await self.run_helper("version", limit=30)
            if code != 0:
                problem = "no sudo permission: " + last_line(out)
            elif not out.strip().isdigit() or int(out) < MIN_HELPER_VERSION:
                problem = "helper is outdated"
            else:
                self.helper_version = int(out)
                problem = ""
                if self.isolated_clients() and not self.supports_isolation():
                    # an old helper would connect them without the firewall
                    problem = "helper is outdated (needed for access=internet)"
        changed = problem != self.helper_problem
        self.helper_problem = problem
        if problem and changed:
            await self.set_readings(
                "setup needed: run the command shown on the device page",
                setup_problem=problem,
            )
        elif not problem and changed:
            await fhem.CommandDeleteReading(
                self.hash, f"{self.hash['NAME']} setup_problem"
            )
        return not problem

    def isolated_clients(self):
        return [
            name
            for name, c in self.config.get("clients", {}).items()
            if c.get("access") == ACCESS_INTERNET
        ]

    def supports_isolation(self):
        return is_root() or self.helper_version >= ISOLATION_HELPER_VERSION

    def check_access(self, params):
        """access parameter, error if invalid or the helper is too old"""
        access = params.get("access") or "all"
        if access not in ACCESS_OPTIONS:
            return None, "access: internet or all"
        if access == ACCESS_INTERNET and not self.supports_isolation():
            return None, (
                "access=internet needs the new helper, run the setup once "
                f"more: set {self.hash['NAME']} setup user=pi password=..."
            )
        return (ACCESS_INTERNET if access == ACCESS_INTERNET else None), None

    def helper_config(self):
        return {
            "private_key": self.config["private_key"],
            "port": self.port,
            "address": self.server_address(),
            "peers": [
                {
                    "public_key": c["public_key"],
                    "preshared_key": c["preshared_key"],
                    "ip": c["ip"],
                    "networks": c.get("networks", []),
                    **({"isolated": True} if c.get("access") else {}),
                }
                for c in self.config["clients"].values()
            ],
        }

    async def apply(self):
        """writes the server configuration and starts or updates it"""
        if self.config.get("stopped"):
            return False
        code, out = await self.run_helper(
            "apply", stdin=json.dumps(self.helper_config())
        )
        if code != 0:
            self.running = False
            await self.set_readings("error: " + last_line(out), last_error=out[-500:])
            return False
        self.running = True
        return True

    # --- readings ---

    async def set_readings(self, state=None, **readings):
        await fhem.readingsBeginUpdate(self.hash)
        if state is not None:
            await fhem.readingsBulkUpdateIfChanged(self.hash, "state", state)
        for name, value in readings.items():
            await fhem.readingsBulkUpdateIfChanged(self.hash, name, value)
        await fhem.readingsEndUpdate(self.hash, 1)

    # --- main loop ---

    async def start(self):
        self.session = aiohttp.ClientSession()
        self.net = await utils.run_blocking(functools.partial(network.detect))
        await self.load_config()
        await self.load_log()
        await self.set_readings(
            "starting",
            vpn_network=str(self.vpn_network),
            home_network=self.net.get("home_network") or "-",
            port=self.port,
            clients=len(self.config["clients"]),
        )
        self._started = True
        if not await self.check_helper():
            await self.try_sudo_setup()
        while not await self.check_helper():
            await asyncio.sleep(SETUP_INTERVAL)
        if self.config.get("stopped"):
            await self.set_readings("stopped")
        else:
            await self.apply()
            self.create_async_task(self.network_loop())
        while True:
            await self.update_status()
            await asyncio.sleep(max(5, int(self._attr_interval or 30)))

    async def network_loop(self):
        while True:
            await self.check_network()
            await asyncio.sleep(NETWORK_INTERVAL)

    async def restart_server(self):
        async with self._lock:
            if self.helper_problem:
                return
            await self.apply()
        await self.check_network()
        await self.update_status()

    # --- network checks ---

    async def check_network(self):
        """public address, router port forwarding, DynDNS name"""
        if self.config.get("stopped") or self.session is None:
            return
        self.net = await utils.run_blocking(functools.partial(network.detect))
        self.public_ip = await network.public_ip(self.session)
        self.router_ip = None
        self.forwarding = ""
        local = self.net.get("local_ip")
        if self._attr_port_forwarding == "upnp" and local:
            if await self.router.find(self.session):
                self.router_ip = await self.router.external_ip()
                if await self.router.forward(self.port, local, "fhempy WireGuard"):
                    self.forwarding = "router (UPnP)"
        if not self.forwarding:
            self.forwarding = f"needed: UDP port {self.port} to {local or '?'}"
        await self.update_problem()

    async def update_problem(self):
        problems = []
        cgnat = network.public_address_problem(self.router_ip or "")
        if cgnat:
            problems.append(cgnat)
        endpoint = self.endpoint_host()
        if not endpoint:
            problems.append("public address unknown, set attr endpoint")
        elif endpoint != self.public_ip and self.public_ip:
            ips = await utils.run_blocking(functools.partial(resolve, endpoint))
            if ips and self.public_ip not in ips:
                problems.append(
                    f"{endpoint} points to {', '.join(sorted(ips))}, "
                    f"not to your public address {self.public_ip}"
                )
        elif endpoint == self.public_ip:
            used = {c.get("endpoint") for c in self.config["clients"].values()}
            used.discard(None)
            if used and used != {endpoint}:
                problems.append(
                    "your public address changed, devices set up before "
                    "can't connect: use a DynDNS name (attr endpoint)"
                )
        self.problem = "; ".join(problems)
        await self.set_readings(
            public_ip=self.public_ip or "-",
            endpoint=f"{endpoint or '?'}:{self.port}",
            port_forwarding=self.forwarding or "-",
            problem=self.problem or "none",
        )

    # --- monitoring ---

    async def update_status(self):
        if self.helper_problem:
            return
        if self.config.get("stopped"):
            await self.set_readings("stopped")
            return
        code, out = await self.run_helper("status", limit=30)
        if code != 0:
            self.running = False
            await self.set_readings("not running: " + last_line(out))
            return
        self.running = True
        self.peers = parse_dump(out)
        await self.update_client_readings()

    def connected(self, peer):
        return bool(peer) and time.time() - peer["handshake"] < CONNECTED_SECONDS

    def from_internet(self, peer):
        ip = endpoint_ip(peer.get("endpoint") or "")
        home = self.net.get("home_network")
        if ip is None or ip.version != 4:
            return ip is not None
        return not (home and ip in ipaddress.IPv4Network(home))

    async def update_client_readings(self):
        clients = self.config["clients"]
        connected = []
        readings = {}
        for name, client in clients.items():
            peer = self.peers.get(client["public_key"]) or {}
            online = self.connected(peer)
            if online:
                connected.append(name)
                if self.from_internet(peer):
                    self.internet_ok = time.time()
            readings[f"{name}_state"] = "connected" if online else "disconnected"
            if peer.get("handshake"):
                readings[f"{name}_last_seen"] = format_time(peer["handshake"])
                readings[f"{name}_from"] = endpoint_ip(peer["endpoint"]) or "-"
            readings[f"{name}_received_mb"] = megabytes(peer.get("rx", 0))
            readings[f"{name}_sent_mb"] = megabytes(peer.get("tx", 0))
        if not clients:
            state = "running, add a device: set add_client"
        elif connected:
            state = f"{len(connected)} of {len(clients)} connected"
        else:
            state = "running, no device connected"
        await self.set_readings(
            state,
            clients=len(clients),
            clients_connected=len(connected),
            connected=", ".join(connected) or "-",
            **readings,
        )

    # --- set / get ---

    def check_name(self, name, exists):
        if not CLIENT_NAME.match(name or ""):
            return "Name: letters, digits, _ and -, at most 24 characters"
        if name.lower() in RESERVED_NAMES:
            return f"{name} is not possible as name"
        if exists and name not in self.config.get("clients", {}):
            known = ", ".join(self.config.get("clients", {})) or "none"
            return f"Unknown device {name}, known: {known}"
        if not exists and name in self.config.get("clients", {}):
            return f"{name} exists already"
        return None

    async def create_client(self, name, networks, access=None):
        """new peer, None or the error"""
        ip = self.next_client_ip()
        if ip is None:
            return "No address left in the VPN network"
        private = keys.private_key()
        self.config["clients"][name] = {
            "private_key": private,
            "public_key": keys.public_key(private),
            "preshared_key": keys.preshared_key(),
            "ip": ip,
            "networks": networks,
            **({"access": access} if access else {}),
            "created": int(time.time()),
            "endpoint": self.endpoint_host(),
        }
        await self.save_config()
        async with self._lock:
            if not self.helper_problem:
                await self.apply()
        await self.update_status()
        return None

    async def set_add_client(self, hash, params):
        if not self.config:
            return "Please wait, the VPN server is starting"
        name = str(params["name"])
        error = self.check_name(name, exists=False)
        if error:
            return error
        access, error = self.check_access(params)
        if error:
            return error
        networks = []
        if params.get("network"):
            net, error = self.check_site_network(params["network"], name)
            if error:
                return error
            networks.append(net)
        error = await self.create_client(name, networks, access)
        if error:
            return error
        return "<html>" + self.client_html(name, open_qr=True) + "</html>"

    # --- automatic setup via SSH ---

    async def set_setup(self, hash, params):
        if not params.get("user") or not params.get("password"):
            return "Usage: set NAME setup user=pi password=..."
        if self.setup_task and not self.setup_task.done():
            return "The setup is already running"
        self.setup_task = self.create_async_task(
            self.setup_via_ssh(str(params["user"]), str(params["password"]))
        )
        return ""

    async def setup_via_ssh(self, user, password):
        await self.report_setup("connecting to this computer via SSH")
        log = self.start_log("One-time setup of this computer")
        try:
            await self.install_requirements()
            await remote.install_helper(
                "127.0.0.1", user, password, self.helper_source(), self.user, log
            )
        except remote.RemoteError as err:
            log(f"# failed: {err}")
            await self.flush_log()
            await self.report_setup(f"failed: {err}")
            return
        log("# done")
        await self.flush_log()
        await self.report_setup("done")
        await self.check_helper()

    async def report_setup(self, text):
        self.setup_state = text
        await self.set_readings(setup=text)

    async def install_requirements(self):
        from ..pkg_installer import check_and_install_dependencies

        await check_and_install_dependencies("core/peer_installer")

    async def try_sudo_setup(self):
        """fhempy may already use sudo (or runs as root): no question"""
        if self.helper_problem != "helper not installed" or tool("sudo") is None:
            return
        code, out = await run_command(
            [
                tool("sudo"),
                "-n",
                tool("python3"),
                "-I",
                self.helper_source(),
                "install",
                self.user,
            ],
            limit=remote.INSTALL_TIMEOUT,
        )
        if code == 0:
            await self.report_setup("done (sudo)")
        else:
            self.logger.debug(f"automatic setup with sudo -n: {last_line(out)}")

    async def set_add_site(self, hash, params):
        if not self.config:
            return "Please wait, the VPN server is starting"
        name = str(params["name"])
        client = self.config["clients"].get(name)
        if client is not None and not is_site(client):
            return f"{name} is a device, not a site"
        error = None if client else self.check_name(name, exists=False)
        if error:
            return error
        missing = [p for p in ("host", "user", "password") if not params.get(p)]
        if params.get("mode") not in (None, "", *SITE_MODES):
            return "mode: networks or internet_only"
        access, error = self.check_access(params)
        if error:
            return error
        if access and not params.get("via_home"):
            return (
                "access=internet needs via_home (e.g. via_home=all): only "
                "those devices get internet through home"
            )
        if access and params.get("mode") == "networks":
            return "access=internet doesn't connect the networks (no mode=networks)"
        if missing:
            return (
                f"Usage: set {self.hash['NAME']} add_site {name} host=192.168.1.77 [port=22] "
                "user=pi password=... [network=192.168.2.0/24] "
                "[via_home=all|192.168.2.50] [mode=networks|internet_only]"
            )
        self.create_async_task(self.setup_site(name, params))
        return (
            f"Setting up {name}, this takes a few minutes. Progress: reading "
            f"{name}_setup"
        )

    async def setup_site(self, name, params):
        reading = f"{name}_setup"
        log = self.start_log(f"Setup of site {name}")
        try:
            await self.set_readings(**{reading: f"connecting to {params['host']}"})
            await self.install_requirements()
            text = await self.connect_and_setup_site(name, params, log)
        except remote.RemoteError as err:
            text = f"failed: {err}"
        except Exception as err:  # noqa: BLE001 asyncssh errors while running
            self.logger.exception(f"Setup of site {name} failed")
            text = f"failed: {err}"
        log(f"# {text}")
        await self.flush_log()
        await self.set_readings(**{reading: text})

    async def connect_and_setup_site(self, name, params, log=remote.nolog):
        user, password = str(params["user"]), str(params["password"])
        host = str(params["host"])
        port = ssh_port(params.get("port"))
        conn = await remote.connect(host, user, password, port, log)
        async with conn:
            found = await remote.site_info(conn, log)
            net = params.get("network") or found.get("network")
            if not net:
                raise remote.RemoteError(
                    "home network of the site not found, enter it (network=...)"
                )
            access, error = self.check_access(params)
            if error:
                raise remote.RemoteError(error)
            internet_only = bool(access) or self.site_mode(name, params, net)
            net, error = self.check_site_network(net, name, internet_only)
            if error:
                raise remote.RemoteError(error)
            via_home, error = self.check_via_home(
                params.get("via_home"), net, found.get("ip")
            )
            if error:
                raise remote.RemoteError(error)
            existing = name in self.config["clients"]
            await self.store_site(
                name,
                net,
                via_home,
                found.get("ip"),
                internet_only,
                found.get("dev"),
                access,
            )
            await self.set_readings(
                **{f"{name}_setup": f"installing WireGuard on {host} ({net})"}
            )
            try:
                await remote.setup_site(
                    conn, user, password, self.client_config(name), log
                )
            except remote.RemoteError:
                if not existing:
                    await self.remove_client(name)
                raise
        text = f"done, network {net}"
        if internet_only and not via_home:
            text += (
                f" - warning: same network as at home, the networks aren't "
                f"connected, only the Pi is reachable (VPN address "
                f"{self.config['clients'][name]['ip']}), see device page"
            )
        elif access:
            text += " (internet only, no access to the devices at home)"
        elif internet_only:
            text += " (internet only, networks not connected)"
        if via_home == VIA_HOME_ALL:
            text += ", internet through home for devices with the Pi as gateway"
        elif via_home:
            text += f", internet through home for {', '.join(via_home)}"
        return text

    def site_mode(self, name, params, net):
        """True for internet_only. Without mode: internet_only if the
        network of the site collides with home or another site (e.g. both
        sites use 192.168.178.0/24, or the Pi is still at home): only the
        Pi and the devices with internet through home are connected"""
        mode = params.get("mode")
        if mode:
            return mode == "internet_only"
        try:
            return self.overlapping_network(net, name) is not None
        except ValueError:
            return False

    async def store_site(
        self,
        name,
        net,
        via_home,
        site_ip,
        internet_only=False,
        site_dev=None,
        access=None,
    ):
        """new site, or new settings of an existing one (keys stay)"""
        networks = [] if internet_only else [net]
        client = self.config["clients"].get(name)
        if client is None:
            error = await self.create_client(name, networks, access)
            if error:
                raise remote.RemoteError(error)
            client = self.config["clients"][name]
        if site_dev:
            client["site_dev"] = site_dev
        client.update(
            networks=networks,
            via_home=via_home,
            site_ip=site_ip,
            site_network=net,
            internet_only=internet_only,
        )
        if access:
            client["access"] = access
        else:
            client.pop("access", None)
        await self.save_config()
        async with self._lock:
            if not self.helper_problem:
                await self.apply()

    async def set_remove_client(self, hash, params):
        name = str(params["name"])
        error = self.check_name(name, exists=True)
        if error:
            return error
        await self.remove_client(name)
        return ""

    async def remove_client(self, name):
        del self.config["clients"][name]
        await self.save_config()
        async with self._lock:
            if not self.helper_problem:
                await self.apply()
        await fhem.CommandDeleteReading(self.hash, f"{self.hash['NAME']} {name}_.*")
        await self.update_status()

    async def set_start(self, hash, params):
        self.config["stopped"] = False
        await self.save_config()
        if self.helper_problem:
            return "Please run the setup command shown on the device page first"
        await self.restart_server()
        if not any(t.get_name() == "wireguard.network_loop" for t in self._tasks):
            self.create_async_task(self.network_loop())
        return ""

    async def set_stop(self, hash, params):
        self.config["stopped"] = True
        await self.save_config()
        self.running = False
        if not self.helper_problem:
            code, out = await self.run_helper("stop")
            if code != 0:
                return "Stop failed: " + last_line(out)
        await self.router.remove(self.port)
        await self.set_readings("stopped")
        return ""

    async def get_client_config(self, hash, params):
        name = str(params["name"])
        error = self.check_name(name, exists=True)
        return error or self.client_config(name)

    async def get_traffic(self, hash, params):
        """byte counters for the live speed on the device page: the page
        asks every TRAFFIC_POLL seconds while it is open, nothing is stored"""
        now = time.time()
        if now - self.traffic_time >= TRAFFIC_CACHE and not self.helper_problem:
            code, out = await self.run_helper("status", limit=10)
            if code == 0:
                self.peers = parse_dump(out)
                self.traffic_time = now
        clients = {}
        for name, client in self.config.get("clients", {}).items():
            peer = self.peers.get(client["public_key"])
            if self.connected(peer):
                # rx: received by the server = upload of the device
                clients[name] = {"down": peer["tx"], "up": peer["rx"]}
        return json.dumps({"time": self.traffic_time or now, "clients": clients})

    # --- FHEMWEB ---

    def client_setup(self, name):
        """QR code cell and the instructions of one device"""
        client = self.config["clients"][name]
        conf = self.client_config(name)
        data = base64.b64encode(conf.encode()).decode()
        download = (
            '<a download="{0}" href="data:application/octet-stream;base64,{1}">'
            "Download {0}</a>"
        )
        if is_site(client):
            nets = html.escape(site_network(client))
            filename = helper.INTERFACE + ".conf"
            if client.get("access"):
                kind = (
                    "Site, internet only: the devices below use the internet "
                    "of your home, but they can't reach any device at home."
                )
                together = ""
            elif client.get("internet_only") and not client.get("via_home"):
                kind = "Site, only the Pi is connected (see the note above)."
                together = ""
            elif client.get("internet_only"):
                kind = (
                    "Site, internet only: the networks aren't connected, the "
                    "devices below use the internet of your home."
                )
                together = ""
            else:
                kind = f"Site with home network <b>{nets}</b>."
                together = "The devices of both sites reach each other, "
            how = (
                f"{kind} On the Raspberry Pi "
                "(Linux) of that site:<br>1. <code>sudo apt install "
                "wireguard-tools iptables</code><br>2. "
                f"{download.format(filename, data)} and copy it to "
                f"<code>/etc/wireguard/{filename}</code> (or <code>get "
                f"{html.escape(self.hash['NAME'])} client_config "
                f"{html.escape(name)}</code>)<br>3. <code>sudo systemctl "
                f"enable --now wg-quick@{helper.INTERFACE}</code><br>{together}"
                "also after a reboot." + self.via_home_html(client)
            )
            qr = ""
        else:
            # the app names the tunnel after the file, at most 15 characters
            filename = name[:15] + ".conf"
            how = (
                "1. Install the <b>WireGuard</b> app (Android, iPhone, Windows, "
                "macOS, Linux)<br>2. Tap <b>+</b> and <b>Scan from QR code</b>"
                "<br>3. Switch the tunnel on: you are at home.<br><br>"
                + (
                    "<b>Internet only:</b> the device uses the internet of your "
                    "home, but it can't reach any device at home.<br><br>"
                    if client.get("access")
                    else ""
                )
                + f"{download.format(html.escape(filename), data)} (for "
                "computers: import tunnel from file)"
            )
            qr = f"<td style='vertical-align:top'>{qr_image(conf)}</td>"
        return qr, how

    def client_html(self, name, open_qr=False):
        return (
            f"<div style='margin:4px 0'><b>{html.escape(name)}</b>"
            f"{self.client_details(name, open_qr)}</div>"
        )

    def client_details(self, name, open_qr=False):
        """note of the site and the collapsed QR code and configuration"""
        client = self.config["clients"][name]
        qr, how = self.client_setup(name)
        return (
            f"{self.site_warning_html(name, client)}"
            f"<details{' open' if open_qr else ''}><summary>QR code and "
            f"configuration</summary><table><tr>{qr}"
            f"<td style='vertical-align:top;padding-left:12px'>{how}<br><br>"
            "Keep it private, it's the key to your home network."
            "</td></tr></table></details>"
        )

    def site_warning_html(self, name, client):
        """the network of the site was the home network (Pi set up at home):
        only the Pi is connected, explains the second step"""
        if not client.get("internet_only") or client.get("via_home"):
            return ""
        args = html.escape(json.dumps([name, client["ip"]]))
        return (
            "<div class='wgNote'>Only the Pi is connected so far: it was in "
            f"the same network as your home ({html.escape(site_network(client))})"
            ", e.g. because it was set up here at home. <b>When the Pi is at "
            "the other place</b> and shows <i>connected</i> here, set it up "
            "again with its VPN address "
            f"<b>{html.escape(client['ip'])}</b>, then fhempy detects the "
            "network there and connects both networks. "
            f"<button type='button' onclick='wgFillSite.apply(null,{args})'>"
            "Set up again</button><br><small>If both places really use the "
            "same network, they can't be connected: then only "
            "<i>internet through home</i> is possible.</small></div>"
        )

    def via_home_html(self, client):
        if not client.get("via_home"):
            return ""
        net = ipaddress.IPv4Network(site_network(client))
        gateway = html.escape(client.get("site_ip") or "IP of the Pi")
        dns = self.net.get("gateway") or "1.1.1.1"
        if client.get("internet_only") and ipaddress.IPv4Address(dns) in net:
            # the router at home has an address of the site itself
            dns = "1.1.1.1"
        dns = html.escape(dns)
        if client["via_home"] == VIA_HOME_ALL and client.get("internet_only"):
            # the network may have been detected while the Pi was still at
            # home, it doesn't matter for internet only
            return (
                "<br><br><b>Internet through home</b> for every device which "
                "uses the Pi as gateway. Set such a device (e.g. TV: network "
                "settings, manual / static) to: a free address of the network "
                "at the site, its subnet mask, gateway / router = the address "
                f"of the Pi at the site (<b>{gateway}</b> when it was set up), "
                f"DNS <b>{dns}</b>. Devices which keep the router of the site "
                "as gateway stay direct. If the VPN service of the Pi is "
                "stopped, they use the internet of the site directly."
            )
        if client["via_home"] == VIA_HOME_ALL:
            which = (
                "<br><br><b>Internet through home</b> for every device which "
                "uses the Pi as gateway. Set such a device (e.g. TV: network "
                "settings, manual / static) to: a free address of the network "
                f"{html.escape(str(net))}, subnet mask <b>{net.netmask}</b>, "
            )
        else:
            rows = "".join(
                f"<li><b>{html.escape(ip)}</b></li>" for ip in client["via_home"]
            )
            which = (
                "<br><br><b>Internet through home</b> for:<ul>"
                f"{rows}</ul>Set these devices (e.g. TV: network settings, "
                f"manual / static) to: subnet mask <b>{net.netmask}</b>, "
            )
        return (
            f"{which}gateway / router <b>{gateway}</b>, DNS <b>{dns}</b>. Use "
            "an address the router of the site doesn't give out, or a fixed "
            "DHCP address. Devices which keep the router of the site as "
            "gateway stay direct. If the VPN service of the Pi is stopped, "
            "they use the internet of the site directly."
        )

    def setup_html(self):
        name = json.dumps(self.hash["NAME"]).replace("<", "\\u003c")
        form = (
            '<form onsubmit=\'var f=this;FW_cmd(FW_root+"?cmd="+'
            'encodeURIComponent("set "+' + html.escape(name) + '+" setup user="+'
            'f.user.value+" password="+f.pw.value)+"&XHR=1",'
            "function(r){if(r)FW_okDialog(r);});return false;'>"
            "User <input name='user' value='pi' size='8'> Password "
            "<input name='pw' type='password' size='12'> "
            "<input type='submit' value='Set up'></form>"
        )
        return (
            '<div style="border:1px solid #c80;padding:8px;margin:8px 0">'
            "<b>One-time setup needed</b> "
            f"({html.escape(self.helper_problem)})<br>A VPN server needs root "
            "rights. Enter the user of this computer which may use sudo (e.g. "
            "pi), fhempy logs in via SSH and does everything. The password is "
            f"not stored.{form}"
            f"Setup: {html.escape(str(self.setup_state or '-'))}<br><br>"
            "Or log in yourself (e.g. with ssh) and run once:<br>"
            "<code style='user-select:all'>"
            f"{html.escape(self.setup_command())}</code><br>Both install "
            "WireGuard and a small helper "
            f"({html.escape(helper.INSTALL_PATH)}), fhempy may only run this "
            "helper as root. fhempy continues by itself afterwards.</div>"
            + FORM_STYLE
            + self.log_html()
        )

    def router_html(self):
        if not self.forwarding.startswith("needed"):
            return ""
        local = html.escape(self.net.get("local_ip") or "this computer")
        return (
            '<div style="border:1px solid #c80;padding:8px;margin:8px 0">'
            "<b>Port forwarding in the router needed</b><br>So that your "
            "devices reach the VPN from the internet, the router must forward "
            f"<b>UDP port {self.port}</b> to <b>{local}</b>.<br>FRITZ!Box: "
            "Internet &gt; Permit Access &gt; Port Sharing &gt; Add Device for "
            f"Sharing &gt; {local} &gt; New Sharing &gt; Port sharing, "
            f"protocol UDP, port {self.port}. Or allow <i>independent port "
            "sharing</i> for this device there, fhempy then does it by itself "
            f"(UPnP).<br>Other routers: <i>port forwarding</i> or <i>virtual "
            f"server</i>, UDP {self.port} to {local}.</div>"
        )

    def detail_html(self):
        if not self._started:
            return ""
        if self.helper_problem and self.helper_problem != "not checked yet":
            return self.setup_html()
        parts = []
        if self.problem:
            parts.append(
                '<div style="border:1px solid #c00;padding:8px;margin:8px 0">'
                f"<b>Problem:</b> {html.escape(self.problem)}</div>"
            )
        parts.append(self.router_html())
        if self.internet_ok:
            parts.append(
                "<div style='margin:4px 0'>✓ A device connected from the "
                "internet, the VPN works from outside.</div>"
            )
        clients = self.config.get("clients", {})
        if clients:
            parts.append(self.devices_html(clients))
        parts.append(self.forms_html())
        parts.append(self.log_html())
        return "".join(parts)

    def log_html(self):
        """terminal with the commands of the setup via SSH, FHEMWEB updates
        it live (informId of the reading setup_log)"""
        name = self.hash["NAME"]
        inform = html.escape(f"{name}-setup_log")
        button = (
            "<button type='button' class='wgLogBtn' onclick='wgLogOpen()'>"
            "Show setup log</button>"
            if self.log_lines
            else ""
        )
        return (
            # the reading itself is shown here, not in the readings table
            f"<style>table.readings tr:has([informId='{inform}'])"
            "{display:none}</style>"
            f"{button}<div class='wgLogBack' onclick='if(event.target==this)"
            "wgLogClose()'><div class='wgLogBox'><div class='wgLogHead'><span>"
            "Setup log</span><button type='button' title='Close' "
            "onclick='wgLogClose()'>&times;</button></div>"
            f"<pre class='wgShell' informId='{inform}'>"
            f"{html.escape(chr(10).join(self.log_lines))}</pre></div></div>"
            + LOG_SCRIPT
        )

    def devices_html(self, clients):
        """table of the devices: status and live speed, total of all"""
        rows = []
        count = f"{len(clients)} device" + ("s" if len(clients) != 1 else "")
        for name in clients:
            peer = self.peers.get(clients[name]["public_key"]) or {}
            esc = html.escape(name)
            inform = html.escape(f"{self.hash['NAME']}-{name}")
            state = "connected" if self.connected(peer) else "disconnected"
            seen = format_time(peer["handshake"]) if peer.get("handshake") else "never"
            kind = "Site" if is_site(clients[name]) else "Device"
            if clients[name].get("access"):
                kind += ", internet only"
            rows.append(
                f"<tbody class='wgDev'><tr><td><b>{esc}</b><small>{kind}</small>"
                f"</td><td><span informId='{inform}_state'>{state}</span><small>"
                f"last seen <span informId='{inform}_last_seen'>{seen}</span>"
                f"</small></td><td class='wgDown' data-client='{esc}'>\u2013</td>"
                f"<td class='wgUp' data-client='{esc}'>\u2013</td></tr>"
                f"<tr class='wgMore'><td colspan='4'>{self.client_details(name)}"
                "</td></tr></tbody>"
            )
        return (
            "<div style='margin:8px 0'><b>Devices</b><table class='wgDevices'>"
            "<thead><tr><th>Device</th><th>Status</th><th class='wgNum'>"
            "\u2193 Download</th><th class='wgNum'>\u2191 Upload</th></tr></thead>"
            + "".join(rows)
            + f"<tfoot><tr><td colspan='2'>Total ({count})</td>"
            "<td class='wgDown wgTotalDown'>\u2013</td>"
            "<td class='wgUp wgTotalUp'>\u2013</td></tr></tfoot></table></div>"
            + self.speed_script()
        )

    def speed_script(self):
        device = json.dumps(self.hash["NAME"]).replace("<", "\\u003c")
        return SPEED_SCRIPT.replace("DEVICE", device).replace(
            "POLL", str(TRAFFIC_POLL * 1000)
        )

    def forms_html(self):
        """forms for add_client and add_site, they send the set command"""
        name = html.escape(json.dumps(self.hash["NAME"]).replace("<", "\\u003c"))
        return (
            FORM_STYLE + FORM_SCRIPT + "<div class='wgForms'>"
            "<form class='wgCard' onsubmit='return wgSend(this," + name + ","
            '"add_client")\'><h4>Add a device</h4><p>Phone, tablet or laptop: '
            "you get a QR code for the WireGuard app.</p>"
            "<label>Name<input name='name' required pattern='[A-Za-z0-9_-]{1,24}'"
            " placeholder='Phone'></label>"
            "<label class='wgCheck'><input type='checkbox' name='access' "
            "value='internet'> Internet only, no access to the devices at "
            "home</label>"
            "<small>e.g. for guests: they use the internet of your home, but "
            "can't reach FHEM, your router or any other device.</small>"
            "<button type='submit'>Add device</button></form>"
            "<form class='wgCard wgSite' onsubmit='return wgSend(this," + name + ","
            '"add_site")\'><h4>Add a site</h4><p>A Raspberry Pi at another '
            "place (e.g. holiday home): fhempy logs in via SSH, installs "
            "WireGuard and connects both home networks. The password is not "
            "stored.</p>"
            "<label>Name<input name='name' required pattern='[A-Za-z0-9_-]{1,24}'"
            " placeholder='Holiday'></label>"
            "<fieldset class='wgWhere'><legend>Where is the Pi right now?"
            "</legend><label class='wgCheck'><input type='radio' "
            "name='wg_where' value='home' checked onchange='wgWhere(this)'> "
            "Here at home, I'll bring it to the other place later</label>"
            "<label class='wgCheck'><input type='radio' name='wg_where' "
            "value='there' onchange='wgWhere(this)'> Already at the other "
            "place and connected (set up again)</label></fieldset>"
            "<div class='wgRow'><label class='wgGrow'>Address of the Pi<input "
            "name='host' required placeholder='192.168.1.77'></label>"
            "<label class='wgPort'>SSH port<input name='port' type='number' "
            "min='1' max='65535' value='22'></label></div>"
            "<small class='wgHome'>Its address here at home, e.g. from the "
            "list of devices in your router.</small>"
            "<small class='wgThere' hidden>Its VPN address (10.x.x.x), shown "
            "above at the site. fhempy detects the network there by itself."
            "</small>"
            "<div class='wgRow'><label class='wgGrow'>User<input name='user' "
            "required value='pi' autocomplete='off'></label>"
            "<label class='wgGrow'>Password<input name='password' "
            "type='password' required autocomplete='new-password'></label></div>"
            "<div class='wgHome'><label>Address of a device at the other place"
            "<input name='network' placeholder='e.g. 192.168.2.34'></label>"
            "<small>Here at home fhempy can't see the network of the other "
            "place. Look at any phone, laptop or TV connected to the WiFi "
            "there: its network settings show its IP address, e.g. "
            "192.168.2.34. Enter it here. Don't know it? Leave it empty and "
            "use <i>Set up again</i> once the Pi is there. Not needed if you "
            "only want internet through home.</small></div>"
            "<label class='wgCheck'><input type='checkbox' name='via_home' "
            "value='all'> Internet through home for devices which use the Pi "
            "as gateway</label>"
            "<small>e.g. a TV: set the address of the Pi as gateway / router "
            "on the TV, its internet goes through your home. The Pi itself "
            "and all other devices stay direct.</small>"
            "<label class='wgCheck'><input type='checkbox' name='access' "
            "value='internet' onchange='if(this.checked)this.form.elements."
            'namedItem("via_home").checked=true\'> Internet only, no access '
            "to the devices at home</label>"
            "<small>The site gets only the internet of your home, it can't "
            "reach FHEM, your router or any other device here (and the devices "
            "at home can't reach the site).</small>"
            "<button type='submit'>Set up site</button></form></div>"
        )
