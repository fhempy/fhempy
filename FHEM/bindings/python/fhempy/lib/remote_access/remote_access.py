"""Remote access: FHEMWEB on the phone from anywhere with Tailscale Funnel.

The module creates its own FHEMWEB instance with password (allowed device),
starts Tailscale and forwards https://<name>.<tailnet>.ts.net to this
FHEMWEB. The phone only needs a browser: no VPN app, no port forwarding in
the router. The other FHEMWEB instances stay in the home network.
"""

import asyncio
import base64
import hashlib
import html
import ipaddress
import re
import secrets

from .. import fhem, generic
from . import tailscale

DEFAULT_HOSTNAME = "fhem"
DEFAULT_USERNAME = "fhem"
MIN_PASSWORD_LENGTH = 10
FIRST_PORT = 8089
LAST_PORT = 8120
ICON = "it_internet"
# seconds between the checks while waiting for the user / while online
WAIT_INTERVAL = 3
ONLINE_INTERVAL = 60
SOCKET_TIMEOUT = 30
LOGIN_HELP = (
    "Log in with Google, Microsoft, Apple or GitHub, a free Tailscale account "
    "is created automatically."
)


def valid_hostname(name):
    """Tailscale machine name: lowercase letters, digits and -"""
    name = re.sub(r"[^a-z0-9-]+", "-", str(name or "").lower()).strip("-")
    return name[:63] or DEFAULT_HOSTNAME


def fhem_address():
    """IP of FHEM as seen by fhempy, None if FHEM runs on this computer"""
    conn = getattr(fhem, "wsconnection", None)
    ws = getattr(conn, "wsconnection", None)
    try:
        ip = ipaddress.ip_address(ws.remote_address[0])
    except (AttributeError, IndexError, TypeError, ValueError):
        return None
    if getattr(ip, "ipv4_mapped", None):
        ip = ip.ipv4_mapped
    if ip.is_loopback:
        return None
    return str(ip)


def qr_image(text):
    import segno

    uri = segno.make(text, micro=False, error="m").png_data_uri(
        scale=5, border=4, dark="#000", light="#fff"
    )
    return (
        f'<img src="{uri}" alt="QR code" '
        'style="width:180px;height:180px;max-width:none;image-rendering:pixelated">'
    )


class remote_access(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.ts = tailscale.Tailscale(logger)
        self.password = ""
        self.url = ""
        self.login_url = ""
        self.enable_url = ""
        self.port = None
        self.fhem_ip = None
        self.status = "starting"
        self.problem = ""
        self._unique_id = None
        self._wakeup = asyncio.Event()

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        self.hash = hash
        await super().Define(hash, args, argsh)
        await self.set_attr_config(
            {
                "hostname": {
                    "default": DEFAULT_HOSTNAME,
                    "help": "First part of the address https://<hostname>."
                    "<your tailnet>.ts.net, default fhem.",
                },
                "username": {
                    "default": DEFAULT_USERNAME,
                    "help": "User name for the login on the phone, default fhem.",
                },
            }
        )
        await self.set_set_config(
            {
                "password": {
                    "args": ["password"],
                    "help": f"Set your own password (at least "
                    f"{MIN_PASSWORD_LENGTH} characters, no spaces).",
                },
                "new_password": {"help": "Create a new random password."},
                "restart": {"help": "Restart Tailscale."},
                "logout": {
                    "help": "Log out of Tailscale, e.g. to use another account. "
                    "The remote access stops until you log in again."
                },
            }
        )
        if await fhem.AttrVal(hash["NAME"], "icon", "") == "":
            await fhem.CommandAttr(hash, f"{hash['NAME']} icon {ICON}")
        self._unique_id = await fhem.getUniqueId(hash)
        await self.load_password()
        self.create_async_task(self.run())

    # FHEM FUNCTION
    async def Undefine(self, hash):
        await super().Undefine(hash)
        await self.ts.stop()

    # FHEM FUNCTION
    async def FW_detailFn(self, hash, args, argsh):
        detail = await super().FW_detailFn(hash, args, argsh)
        return self.setup_html() + str(detail or "")

    # --- names of the devices created by the module ---

    @property
    def web_name(self):
        return "WEB" + self.hash["NAME"]

    @property
    def allowed_name(self):
        return "allowed_" + self.web_name

    # --- password ---

    async def load_password(self):
        from .. import utils

        stored = await fhem.ReadingsVal(self.hash["NAME"], ".password", "")
        if stored:
            try:
                self.password = utils.decrypt_string(stored, self._unique_id)
            except Exception:
                self.password = ""
        if not self.password:
            await self.store_password(secrets.token_urlsafe(12))

    async def store_password(self, password):
        from .. import utils

        self.password = password
        await fhem.readingsSingleUpdate(
            self.hash,
            ".password",
            utils.encrypt_string(password, self._unique_id),
            0,
        )

    def credentials_hash(self):
        """changes when username or password change, the hash is stored
        instead of the password to know if allowed needs the new one"""
        text = f"{self._attr_username}:{self.password}:{self._unique_id}"
        return hashlib.sha256(text.encode()).hexdigest()

    async def set_password(self, hash, params):
        password = params["password"]
        if len(password) < MIN_PASSWORD_LENGTH or " " in password:
            return (
                f"The password needs at least {MIN_PASSWORD_LENGTH} characters "
                "and no spaces"
            )
        await self.store_password(password)
        await self.apply_password()
        return None

    async def set_new_password(self, hash, params):
        await self.store_password(secrets.token_urlsafe(12))
        await self.apply_password()

    async def set_attr_username(self, hash):
        if self.port is not None:
            self.create_async_task(self.apply_password())

    async def apply_password(self):
        await self.set_basic_auth()
        await self.page_changed()

    # --- FHEMWEB with password ---

    async def setup_fhemweb(self):
        """Own FHEMWEB instance for the remote access, protected by an
        allowed device. Returns the port of the FHEMWEB."""
        self.fhem_ip = fhem_address()
        listen = " global" if self.fhem_ip else ""
        comment = (
            f"Remote access of {self.hash['NAME']} (Tailscale Funnel), "
            "only reachable with password"
        )
        result = await fhem.sendCommandHash(
            self.hash,
            f"my $web = {fhem.perlString(self.web_name)};"
            f" my $al = {fhem.perlString(self.allowed_name)};"
            f" my $comment = {fhem.perlString(comment)};"
            " return 'error: ' . $web . ' already exists and is no FHEMWEB'"
            " if (defined($defs{$web}) && $defs{$web}{TYPE} ne 'FHEMWEB');"
            " return 'error: ' . $al . ' already exists and is no allowed device'"
            " if (defined($defs{$al}) && $defs{$al}{TYPE} ne 'allowed');"
            # the password protection first, FHEMWEB isn't reachable without
            ' CommandDefine(undef, "$al allowed") if (!defined($defs{$al}));'
            " return 'error: allowed device could not be created'"
            " if (!defined($defs{$al}));"
            ' CommandAttr(undef, "$al validFor $web")'
            " if (AttrVal($al, 'validFor', '') ne $web);"
            ' CommandAttr(undef, "$al basicAuthExpiry 30")'
            " if (AttrVal($al, 'basicAuthExpiry', '') eq '');"
            ' CommandAttr(undef, "$al comment $comment");'
            " my $err = '';"
            " if (!defined($defs{$web})) {"
            f" foreach my $p ({FIRST_PORT}..{LAST_PORT}) {{"
            f' $err = CommandDefine(undef, "$web FHEMWEB $p{listen}") // "";'
            " last if (defined($defs{$web})); } }"
            " return 'error: FHEMWEB could not be created: ' . $err"
            " if (!defined($defs{$web}));"
            ' CommandAttr(undef, "$web comment $comment");'
            " 'port ' . $defs{$web}{PORT}",
        )
        match = re.match(r"port (\d+)", str(result or ""))
        if not match:
            raise RuntimeError(str(result or "FHEMWEB could not be created"))
        self.port = int(match.group(1))
        if (
            await fhem.ReadingsVal(self.hash["NAME"], ".auth", "")
            != self.credentials_hash()
            or not await self.basic_auth_set()
        ):
            await self.set_basic_auth()
        return self.port

    async def basic_auth_set(self):
        result = await fhem.sendCommandHash(
            self.hash,
            f"AttrVal({fhem.perlString(self.allowed_name)}, 'basicAuth', '')"
            " ne '' ? 'yes' : 'no'",
        )
        return result == "yes"

    async def set_basic_auth(self):
        # allowed stores a salted SHA256 hash of user:password
        await fhem.sendCommandHash(
            self.hash,
            "CommandSet(undef, "
            + fhem.perlString(
                f"{self.allowed_name} basicAuth {self._attr_username} {self.password}"
            )
            + ") // ''",
        )
        await fhem.readingsSingleUpdate(self.hash, ".auth", self.credentials_hash(), 0)

    def fhemweb_url(self):
        # plain http inside the home network, Tailscale adds https
        host = self.fhem_ip or "127.0.0.1"
        return f"http://{host}:{self.port}"  # NOSONAR

    async def check_password_protection(self):
        """FHEMWEB must refuse requests without password before it is
        reachable from the internet, raises RuntimeError otherwise"""
        import aiohttp

        url = self.fhemweb_url() + "/fhem"
        timeout = aiohttp.ClientTimeout(total=15)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, allow_redirects=False) as resp:
                    without = resp.status
                login = f"{self._attr_username}:{self.password}".encode()
                auth = {"Authorization": "Basic " + base64.b64encode(login).decode()}
                async with session.get(url, headers=auth) as resp:
                    with_password = resp.status
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise RuntimeError(f"FHEMWEB {url} is not reachable: {err}") from err
        if without != 401:
            raise RuntimeError(
                f"{self.web_name} doesn't ask for a password, remote access "
                f"stays off. Check {self.allowed_name}."
            )
        if with_password != 200:
            self.logger.warning(
                f"{self.web_name} answers {with_password} with password"
            )

    # --- main loop ---

    async def run(self):
        try:
            await self.update_status("installing Tailscale")
            version = await tailscale.install(self.logger)
            await fhem.readingsSingleUpdateIfChanged(
                self.hash, "tailscale_version", version, 1
            )
            await self.update_status("preparing FHEMWEB with password")
            await self.setup_fhemweb()
            await self.check_password_protection()
        except Exception as err:
            self.logger.error(f"Remote access can't start: {err}")
            await self.update_status("error", str(err))
            return
        while True:
            try:
                online = await self.step()
            except asyncio.CancelledError:
                raise
            except Exception as err:
                self.logger.exception("Remote access check failed")
                await self.update_status("error", str(err))
                online = False
            self._wakeup.clear()
            try:
                await asyncio.wait_for(
                    self._wakeup.wait(), ONLINE_INTERVAL if online else WAIT_INTERVAL
                )
            except asyncio.TimeoutError:
                pass

    async def ensure_daemon(self):
        if self.ts.daemon_running():
            return True
        await self.update_status("starting Tailscale")
        self.ts.start_daemon()
        for _ in range(SOCKET_TIMEOUT * 2):
            await asyncio.sleep(0.5)
            if not self.ts.daemon_running():
                break
            if await self.ts.status() is not None:
                return True
        await self.update_status(
            "error", "Tailscale doesn't start, see .fhempy/log/tailscale.log"
        )
        return False

    async def step(self):
        """One check of Tailscale, returns True if the remote access works"""
        if not await self.ensure_daemon():
            return False
        status = await self.ts.status()
        if status is None:
            return False
        backend = status.get("BackendState")
        if backend in ("NeedsLogin", "NoState", "Stopped"):
            await self.ts.start_login(valid_hostname(self._attr_hostname))
            self.login_url = status.get("AuthURL") or ""
            await self.update_status("login required")
            return False
        self.login_url = ""
        if backend == "NeedsMachineAuth":
            await self.update_status("waiting for approval")
            return False
        if backend != "Running":
            await self.update_status("connecting")
            return False
        dns = ((status.get("Self") or {}).get("DNSName") or "").rstrip(".")
        if not dns:
            await self.update_status("connecting")
            return False
        return await self.check_funnel(dns)

    async def check_funnel(self, dns):
        if self.ts.funnel_busy():
            # waits until the user enabled Funnel in the tailnet
            self.enable_url = self.ts.funnel_enable_url() or ""
            await self.update_status(
                "enable funnel" if self.enable_url else "enabling funnel"
            )
            return False
        if tailscale.funnel_active(await self.ts.funnel_status()):
            self.enable_url = ""
            self.url = f"https://{dns}"
            await fhem.readingsSingleUpdateIfChanged(self.hash, "url", self.url, 1)
            await self.update_status("online")
            return True
        output = self.ts.funnel_output.strip()
        if output and self.ts.funnel_proc is not None:
            self.logger.info(f"tailscale funnel: {output}")
        # check the password again, it might have been removed meanwhile
        await self.check_password_protection()
        await self.ts.start_funnel(self.fhemweb_url())
        await self.update_status("enabling funnel")
        return False

    async def update_status(self, status, problem=""):
        changed = (status, problem) != (self.status, self.problem)
        self.status = status
        self.problem = problem
        state = f"{status}: {problem}" if problem else status
        if status == "online":
            state = f"online: {self.url}"
        await fhem.readingsSingleUpdateIfChanged(self.hash, "state", state, 1)
        if changed:
            await self.page_changed()

    async def page_changed(self):
        """reload the open detail page, it shows the next step"""
        await fhem.FW_runJavascript(
            self.hash, "location.reload()", detail=self.hash["NAME"]
        )

    # --- set commands ---

    async def set_restart(self, hash, params):
        self.create_async_task(self.restart())

    async def set_logout(self, hash, params):
        self.create_async_task(self.logout())

    async def restart(self):
        await self.ts.stop()
        self.url = ""
        self._wakeup.set()

    async def logout(self):
        await self.ts.stop_funnel()
        await self.ts.logout()
        self.url = ""
        await fhem.readingsSingleUpdate(self.hash, "url", "-", 1)
        self._wakeup.set()

    async def set_attr_hostname(self, hash):
        if self.ts.daemon_running():
            self.create_async_task(self.change_hostname())

    async def change_hostname(self):
        await self.ts.set_hostname(valid_hostname(self._attr_hostname))
        self._wakeup.set()

    # --- FHEMWEB page ---

    def setup_html(self):
        if not hasattr(self, "hash"):
            return ""
        body = self.step_html()
        return (
            '<div class="makeTable wide">'
            '<span class="mkTitle">Remote access</span>'
            '<table class="block wide"><tr class="odd"><td>'
            f"{body}</td></tr></table></div>"
        )

    @staticmethod
    def button(url, label):
        url = html.escape(url)
        return (
            f'<a href="{url}" target="_blank" rel="noopener" '
            'style="display:inline-block;padding:8px 16px;margin:6px 0;'
            "border-radius:6px;background:#2a6ebb;color:#fff;"
            f'text-decoration:none;font-weight:bold">{label}</a>'
        )

    def step_html(self):
        status = self.status
        if status == "online":
            return self.online_html()
        if status == "error":
            return (
                "<b style='color:#c00'>Remote access is off:</b> "
                f"{html.escape(self.problem)}<br>Fix the problem and use "
                "<i>set restart</i>."
            )
        if status == "login required":
            if not self.login_url:
                return "Preparing the Tailscale login..."
            return (
                "<b>Step 1 of 2: Log in to Tailscale</b><br>"
                f"{LOGIN_HELP}<br>"
                + self.button(self.login_url, "Log in to Tailscale")
                + "<br>This page continues by itself afterwards."
            )
        if status == "enable funnel":
            return (
                "<b>Step 2 of 2: Allow access from the internet</b><br>"
                "Tailscale asks once if this device may be reachable from the "
                "internet (Funnel). Click <i>Enable</i> there.<br>"
                + self.button(self.enable_url, "Allow Funnel")
                + "<br>This page continues by itself afterwards."
            )
        if status == "waiting for approval":
            return (
                "Approve the new device <b>"
                f"{html.escape(valid_hostname(self._attr_hostname))}</b> in the "
                + '<a href="https://login.tailscale.com/admin/machines" '
                'target="_blank" rel="noopener">Tailscale admin console</a>.'
            )
        return f"{html.escape(status[:1].upper() + status[1:])}..."

    def online_html(self):
        url = html.escape(self.url)
        user = html.escape(self._attr_username)
        password = html.escape(self.password)
        box = 'style="font-family:monospace;width:16em"'
        return (
            '<table><tr><td style="vertical-align:top;padding-right:16px">'
            "<b>FHEM is reachable from anywhere:</b><br>"
            f'<a href="{url}" target="_blank" rel="noopener" '
            f'style="font-size:1.2em">{url}</a><br><br>'
            "Scan the QR code with your phone and save the page on the home "
            "screen. No app and no VPN needed.<br><br>"
            f"User: <input type='text' readonly value='{user}' {box} "
            "onclick='this.select()'><br>"
            f"Password: <input type='password' readonly value='{password}' "
            f"{box} onclick='this.type=\"text\";this.select()'> "
            "<small>(click to show)</small><br><br>"
            "<small>Only this address needs the password, FHEMWEB in your home "
            "network stays as it is. Change the password with "
            "<i>set password</i>.</small>"
            f'</td><td style="vertical-align:top">{qr_image(self.url)}</td>'
            "</tr></table>"
        )
