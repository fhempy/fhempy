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
from . import helper, keys, network

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
CLIENT_NAME = re.compile(r"^[A-Za-z0-9_-]{1,24}$")
RESERVED_NAMES = {"state", "clients", "port", "endpoint", "public"}


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
        self.user = current_user()
        self.router = network.Router(logger)
        self.session = None
        self._started = False

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
                    "argsh": ["network"],
                    "help": "Add a device (phone, laptop...), e.g. "
                    "<code>add_client Phone</code>. Shows the QR code for the "
                    "WireGuard app.<br>Another site (e.g. a Raspberry Pi in a "
                    "holiday home) with its home network: <code>add_client "
                    "Holiday network=192.168.2.0/24</code>",
                },
                "remove_client": {
                    "args": ["name"],
                    "help": "Remove a device, it can't connect anymore.",
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
                }
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

    def allowed_ips(self, name):
        site = bool(self.config["clients"][name].get("networks"))
        if self._attr_client_traffic == "all" and not site:
            return "0.0.0.0/0, ::/0"
        nets = [str(self.vpn_network)]
        if self.net.get("home_network"):
            nets.append(self.net["home_network"])
        return ", ".join(nets + self.site_networks(exclude=name))

    def check_site_network(self, value, name):
        """the home network of another site, None if invalid"""
        try:
            net = ipaddress.IPv4Network(str(value), strict=False)
        except ValueError:
            return None, f"Invalid network {value}, e.g. 192.168.2.0/24"
        if not net.is_private or net.prefixlen < 8:
            return None, f"{net} is not a private home network"
        others = [self.vpn_network] + [
            ipaddress.IPv4Network(n) for n in self.site_networks(exclude=name)
        ]
        if self.net.get("home_network"):
            others.append(ipaddress.IPv4Network(self.net["home_network"]))
        for other in others:
            if net.overlaps(other):
                return None, (
                    f"{net} overlaps {other}: every site needs its own "
                    "network, change it in the router of that site"
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
        site = bool(client.get("networks"))
        if self._attr_client_traffic == "all" and self.net.get("gateway") and not site:
            lines.append(f"DNS = {self.net['gateway']}")
        if site:
            # the Pi of the other site forwards into its home network
            out = "$(ip -4 route show default | awk '{print $5; exit}')"
            vpn = self.vpn_network
            for action, word in (("A", "PostUp"), ("D", "PostDown")):
                if action == "A":
                    lines.append(f"{word} = sysctl -q -w net.ipv4.ip_forward=1")
                lines += [
                    f"{word} = iptables -{action} FORWARD -i %i -j ACCEPT",
                    f"{word} = iptables -{action} FORWARD -o %i -j ACCEPT",
                    f"{word} = iptables -t nat -{action} POSTROUTING -s {vpn} "
                    f"-o {out} -j MASQUERADE",
                ]
                if self.net.get("home_network"):
                    lines.append(
                        f"{word} = iptables -t nat -{action} POSTROUTING -s "
                        f"{self.net['home_network']} -o {out} -j MASQUERADE"
                    )
                lines.append(
                    f"{word} = iptables -t mangle -{action} FORWARD -p tcp "
                    "--tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu"
                )
        lines += [
            "",
            "[Peer]",
            f"PublicKey = {keys.public_key(self.config['private_key'])}",
            f"PresharedKey = {client['preshared_key']}",
            f"Endpoint = {host}:{self.port}",
            f"AllowedIPs = {self.allowed_ips(name)}",
            f"PersistentKeepalive = {KEEPALIVE}",
        ]
        return "\n".join(lines) + "\n"

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
            elif not out.strip().isdigit() or int(out) < helper.HELPER_VERSION:
                problem = "helper is outdated"
            else:
                problem = ""
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
        await self.set_readings(
            "starting",
            vpn_network=str(self.vpn_network),
            home_network=self.net.get("home_network") or "-",
            port=self.port,
            clients=len(self.config["clients"]),
        )
        self._started = True
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

    async def set_add_client(self, hash, params):
        if not self.config:
            return "Please wait, the VPN server is starting"
        name = str(params["name"])
        error = self.check_name(name, exists=False)
        if error:
            return error
        networks = []
        if params.get("network"):
            net, error = self.check_site_network(params["network"], name)
            if error:
                return error
            networks.append(net)
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
            "created": int(time.time()),
            "endpoint": self.endpoint_host(),
        }
        await self.save_config()
        async with self._lock:
            if not self.helper_problem:
                await self.apply()
        await self.update_status()
        return "<html>" + self.client_html(name, open_qr=True) + "</html>"

    async def set_remove_client(self, hash, params):
        name = str(params["name"])
        error = self.check_name(name, exists=True)
        if error:
            return error
        del self.config["clients"][name]
        await self.save_config()
        async with self._lock:
            if not self.helper_problem:
                await self.apply()
        await fhem.CommandDeleteReading(self.hash, f"{self.hash['NAME']} {name}_.*")
        await self.update_status()
        return ""

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

    # --- FHEMWEB ---

    def client_html(self, name, open_qr=False):
        client = self.config["clients"][name]
        conf = self.client_config(name)
        data = base64.b64encode(conf.encode()).decode()
        download = (
            '<a download="{0}" href="data:application/octet-stream;base64,{1}">'
            "Download {0}</a>"
        )
        if client.get("networks"):
            nets = html.escape(", ".join(client["networks"]))
            filename = helper.INTERFACE + ".conf"
            how = (
                f"Site with home network <b>{nets}</b>. On the Raspberry Pi "
                "(Linux) of that site:<br>1. <code>sudo apt install "
                "wireguard-tools iptables</code><br>2. "
                f"{download.format(filename, data)} and copy it to "
                f"<code>/etc/wireguard/{filename}</code> (or <code>get "
                f"{html.escape(self.hash['NAME'])} client_config "
                f"{html.escape(name)}</code>)<br>3. <code>sudo systemctl "
                f"enable --now wg-quick@{helper.INTERFACE}</code><br>The "
                "devices of both sites reach each other, also after a reboot."
            )
            qr = ""
        else:
            # the app names the tunnel after the file, at most 15 characters
            filename = name[:15] + ".conf"
            how = (
                "1. Install the <b>WireGuard</b> app (Android, iPhone, Windows, "
                "macOS, Linux)<br>2. Tap <b>+</b> and <b>Scan from QR code</b>"
                "<br>3. Switch the tunnel on: you are at home.<br><br>"
                f"{download.format(html.escape(filename), data)} (for "
                "computers: import tunnel from file)"
            )
            qr = f"<td style='vertical-align:top'>{qr_image(conf)}</td>"
        return (
            f"<div style='margin:4px 0'><b>{html.escape(name)}</b>"
            f"<details{' open' if open_qr else ''}><summary>QR code and "
            f"configuration</summary><table><tr>{qr}"
            f"<td style='vertical-align:top;padding-left:12px'>{how}<br><br>"
            "Keep it private, it's the key to your home network."
            "</td></tr></table></details></div>"
        )

    def setup_html(self):
        return (
            '<div style="border:1px solid #c80;padding:8px;margin:8px 0">'
            "<b>One-time setup needed</b> "
            f"({html.escape(self.helper_problem)})<br>A VPN server needs root "
            "rights. Log in to this computer (e.g. with ssh) and run once:<br>"
            "<code style='user-select:all'>"
            f"{html.escape(self.setup_command())}</code><br>It installs "
            "WireGuard and a small helper "
            f"({html.escape(helper.INSTALL_PATH)}), fhempy may only run this "
            "helper as root. fhempy continues by itself afterwards.</div>"
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
            parts.append("<div style='margin:8px 0'><b>Devices</b>")
            parts += [self.client_html(name) for name in clients]
            parts.append("</div>")
        else:
            parts.append(
                "<div style='margin:8px 0'>Add your first device: "
                f"<code>set {html.escape(self.hash['NAME'])} add_client Phone"
                "</code></div>"
            )
        return "".join(parts)
