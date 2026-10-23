"""Push notifications to phones and tablets, without app and without cloud
account (replacement for Pushbullet).

The browser of the phone subscribes once on the FHEMWEB page of this device
(Web Push, works in Chrome, Firefox, Edge, Samsung Internet and in the iPhone
home screen app since iOS 16.4). fhempy encrypts every message and hands it
to the push service of the browser (Google, Apple, Mozilla), which delivers
it even when the browser is closed. Browsers allow this only on https pages:
the Tailscale address of remote_access or a local https address which this
module sets up.
"""

import asyncio
import base64
import binascii
import hashlib
import html
import json
import re
import secrets
import time
from urllib.parse import urlsplit, urlunsplit

from .. import fhem, generic
from ..remote_access.remote_access import LOOK_ATTRIBUTES, fhem_address, qr_image
from . import certs

ICON = "it_smartphone"
# the subject of the VAPID token, push services contact it on problems
VAPID_SUBJECT = "mailto:fhempy@users.noreply.github.com"
# seconds a message waits at the push service if the phone is offline
TTL = 24 * 3600
ACTION_SECONDS = 24 * 3600
MAX_ACTIONS = 2
MAX_DEVICE_NAME = 40
# push services accept about 4 KB of encrypted data
MAX_BODY = 1500
SEND_TIMEOUT = 30
FIRST_HTTPS_PORT = 8443
LAST_HTTPS_PORT = 8452
OPTIONS = ("title", "to", "image", "url", "action", "action2")
USAGE = (
    "Usage: set <name> message [title=...] [to=...] [image=...] [url=...] "
    '[action="Label:FHEM command"] [action2=...] text'
)


def b64url_decode(text):
    text = str(text).strip()
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def device_id(endpoint):
    return hashlib.sha256(endpoint.encode()).hexdigest()[:12]


def clean_device_name(name):
    name = re.sub(r"[\s,]+", " ", str(name or "")).strip()
    return name[:MAX_DEVICE_NAME].strip()


def split_message(args, argsh):
    """text and options of set message, also accepts the Pushbullet way
    'text | title'. Words with = which are no option belong to the text."""
    options = {}
    words = list(args)
    for key, value in argsh.items():
        if key in OPTIONS:
            options[key] = str(value)
        else:
            words.append(f"{key}={value}")
    text = " ".join(str(w) for w in words).strip()
    if "|" in text and "title" not in options:
        text, title = (part.strip() for part in text.split("|", 1))
        if title:
            options["title"] = title
    return text, options


def parse_action(text):
    """'Label:FHEM command' -> (label, command)"""
    label, sep, command = str(text).partition(":")
    label, command = label.strip(), command.strip()
    if not sep or not label or not command:
        raise ValueError(f'action needs "Label:FHEM command", got "{text}"')
    return label[:30], command


def valid_subscription(sub):
    if not isinstance(sub, dict):
        return False
    keys = sub.get("keys") or {}
    endpoint = str(sub.get("endpoint") or "")
    try:
        parts = urlsplit(endpoint)
    except ValueError:
        return False
    return (
        parts.scheme == "https"
        and bool(parts.hostname)
        and bool(keys.get("p256dh"))
        and bool(keys.get("auth"))
    )


class push(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self._vapid = None
        self._devices = {}
        self._actions = {}
        self._unique_id = None
        self._session = None
        self.https = LocalHttps(self)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        self.hash = hash
        await super().Define(hash, args, argsh)
        await self.set_set_config(
            {
                "message": {
                    "args": ["text"],
                    "help": "<b>message [title=...] [to=...] [image=...] [url=...] "
                    '[action="Label:FHEM command"] [action2=...] text</b><br>'
                    "Sends the text to all phones (or only to=name1,name2).<br>"
                    "image: picture shown below the text (Android).<br>"
                    "url: page opened by a tap on the message, default FHEM.<br>"
                    "action: button which runs the FHEM command (Android).<br>"
                    "Example: <code>set push message title=Door "
                    'action="Light on:set light on" Somebody rings</code>',
                },
                "test": {"help": "Sends a test message to all phones."},
                "remove_device": {
                    "args": ["device"],
                    "options": "",
                    "help": "Stops the notifications on this phone.",
                },
                "local_https": {
                    "args": ["hostname"],
                    "params": {"hostname": {"default": ""}},
                    "help": "<b>local_https [hostname]</b><br>Sets up an https "
                    "address of FHEMWEB in the home network (without Tailscale). "
                    "The button on this page does it for you.",
                },
            }
        )
        await self.set_icon(ICON)
        self._unique_id = await fhem.getUniqueId(hash)
        await self.load_vapid()
        await self.load_devices()
        await self.update_device_readings()
        self.create_async_task(self.https.renew_if_needed())

    # FHEM FUNCTION
    async def Undefine(self, hash):
        await super().Undefine(hash)
        if self._session is not None:
            await self._session.close()
            self._session = None

    # FHEM FUNCTION
    async def Set(self, hash, args, argsh):
        cmd = args[1] if len(args) > 1 else ""
        # message text may contain anything, it isn't split into parameters
        if cmd in ("message", "msg"):
            return await self.send_command(args[2:], argsh)
        # used by the browser, not shown in the set list
        if cmd == "register" and len(args) == 3:
            return await self.register(args[2])
        if cmd == "unregister" and len(args) == 3:
            return await self.unregister(args[2])
        if cmd == "action" and len(args) == 3:
            return await self.run_action(args[2])
        return await super().Set(hash, args, argsh)

    # FHEM FUNCTION
    async def FW_detailFn(self, hash, args, argsh):
        detail = await super().FW_detailFn(hash, args, argsh)
        return await self.setup_html(args[0] if args else None) + str(detail or "")

    # --- keys of this FHEM (VAPID) ---

    async def load_vapid(self):
        from py_vapid import Vapid
        from .. import utils

        stored = await fhem.ReadingsVal(self.hash["NAME"], ".vapid_key", "")
        if stored:
            try:
                pem = utils.decrypt_string(stored, self._unique_id)
                self._vapid = Vapid.from_pem(pem.encode())
                return
            except Exception:
                self.logger.error(
                    "Stored push key can't be read, a new one is created. "
                    "Phones need to enable notifications again."
                )
        vapid = Vapid()
        vapid.generate_keys()
        pem = vapid.private_pem().decode()
        await fhem.readingsSingleUpdate(
            self.hash, ".vapid_key", utils.encrypt_string(pem, self._unique_id), 0
        )
        self._vapid = vapid
        # old subscriptions belong to the old key
        self._devices = {}
        await self.save_devices()

    @property
    def public_key(self):
        from cryptography.hazmat.primitives import serialization

        raw = self._vapid.public_key.public_bytes(
            serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint
        )
        return b64url(raw)

    # --- registered phones ---

    async def load_devices(self):
        stored = await fhem.ReadingsVal(self.hash["NAME"], ".devices", "")
        try:
            devices = json.loads(stored) if stored else {}
        except ValueError:
            devices = {}
        if isinstance(devices, dict):
            self._devices = {
                key: dev
                for key, dev in devices.items()
                if isinstance(dev, dict) and valid_subscription(dev.get("sub"))
            }

    async def save_devices(self):
        await fhem.readingsSingleUpdate(
            self.hash, ".devices", json.dumps(self._devices, separators=(",", ":")), 0
        )
        await self.update_device_readings()

    async def update_device_readings(self):
        names = [dev["name"] for dev in self._devices.values()]
        await fhem.readingsBeginUpdate(self.hash)
        try:
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "devices", ", ".join(names) if names else "-"
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "state", self.state_text()
            )
        finally:
            await fhem.readingsEndUpdate(self.hash, 1)
        options = ",".join(name.replace(" ", "#") for name in names)
        self._conf_set["remove_device"]["options"] = options

    def state_text(self):
        count = len(self._devices)
        if count == 0:
            return "no phone yet"
        return f"ready, {count} phone" + ("s" if count > 1 else "")

    def unique_name(self, name, key):
        names = {dev["name"].lower() for k, dev in self._devices.items() if k != key}
        result, number = name, 2
        while result.lower() in names:
            result = f"{name} {number}"
            number += 1
        return result

    async def register(self, data):
        try:
            info = json.loads(b64url_decode(data))
        except (ValueError, binascii.Error):
            return "Invalid registration"
        sub = info.get("sub") if isinstance(info, dict) else None
        if not valid_subscription(sub):
            return "Invalid registration"
        sub = {
            "endpoint": sub["endpoint"],
            "keys": {"p256dh": sub["keys"]["p256dh"], "auth": sub["keys"]["auth"]},
        }
        key = device_id(sub["endpoint"])
        name = clean_device_name(info.get("name")) or "Phone"
        name = self.unique_name(name, key)
        self._devices[key] = {"name": name, "sub": sub, "added": int(time.time())}
        await self.save_devices()
        self.logger.info(f"Notifications enabled on {name}")
        await self.send(
            {"title": "FHEM", "body": f"Notifications work on {name} 👍"},
            [key],
        )
        return None

    async def unregister(self, key):
        if key in self._devices:
            name = self._devices.pop(key)["name"]
            self.logger.info(f"Notifications disabled on {name}")
            await self.save_devices()
        return None

    async def set_remove_device(self, hash, params):
        wanted = str(params["device"]).replace("#", " ").lower()
        for key, dev in list(self._devices.items()):
            if dev["name"].lower() == wanted:
                del self._devices[key]
                await self.save_devices()
                return None
        return f"Unknown phone {params['device']}"

    def find_targets(self, to):
        if not to:
            return list(self._devices)
        keys = []
        for wanted in (part.strip().lower() for part in to.split(",")):
            if not wanted:
                continue
            found = [
                k for k, d in self._devices.items() if d["name"].lower() == wanted
            ] or [
                k
                for k, d in self._devices.items()
                if d["name"].lower().startswith(wanted)
            ]
            if not found:
                raise ValueError(f"No phone named {wanted}")
            keys += [k for k in found if k not in keys]
        return keys

    # --- sending ---

    async def send_command(self, args, argsh):
        text, options = split_message(args, argsh)
        if not text and not options.get("title"):
            return USAGE
        if not self._devices:
            return (
                "No phone receives notifications yet: open this device in "
                "FHEMWEB on the phone and tap Enable notifications"
            )
        try:
            targets = self.find_targets(options.get("to"))
            payload = self.build_payload(text, options)
        except ValueError as err:
            return str(err)
        await fhem.readingsSingleUpdate(self.hash, "message", text, 1)
        self.create_async_task(self.send(payload, targets))
        return None

    async def set_test(self, hash, params):
        return await self.send_command(["This is a test message from FHEM 👋"], {})

    def build_payload(self, text, options):
        payload = {
            "title": options.get("title") or "FHEM",
            "body": text[:MAX_BODY],
            "tag": secrets.token_hex(4),
        }
        for key in ("image", "url"):
            if options.get(key):
                if urlsplit(options[key]).scheme not in ("https", "http", ""):
                    raise ValueError(f"{key} must be a web address")
                payload[key] = options[key]
        actions = []
        for key in ("action", "action2")[:MAX_ACTIONS]:
            if options.get(key):
                label, command = parse_action(options[key])
                actions.append({"action": self.add_action(command), "title": label})
        if actions:
            payload["actions"] = actions
        return payload

    def add_action(self, command):
        now = time.monotonic()
        self._actions = {t: a for t, a in self._actions.items() if a["expires"] > now}
        token = secrets.token_urlsafe(16)
        self._actions[token] = {"command": command, "expires": now + ACTION_SECONDS}
        return token

    async def run_action(self, token):
        action = self._actions.pop(token, None)
        if action is None or action["expires"] < time.monotonic():
            return "This button was already used or is too old"
        command = action["command"]
        self.logger.info(f"Button of a notification runs: {command}")
        await fhem.readingsSingleUpdate(self.hash, "last_action", command, 1)
        result = await fhem.sendCommandHash(
            self.hash,
            f"AnalyzeCommandChain(undef, {fhem.perlString(command)}) // ''",
        )
        return str(result or "") or None

    async def http_session(self):
        import aiohttp

        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def send(self, payload, targets):
        """sends to all targets in parallel, returns the number delivered"""
        payload = dict(payload, dev=self.hash["NAME"])
        data = json.dumps(payload, ensure_ascii=False)
        results = await asyncio.gather(
            *(self.send_one(key, data) for key in targets if key in self._devices)
        )
        delivered = sum(1 for ok in results if ok)
        await fhem.readingsSingleUpdate(
            self.hash, "delivered", f"{delivered} of {len(results)}", 1
        )
        if any(ok is None for ok in results):
            await self.save_devices()
        return delivered

    async def send_one(self, key, data):
        """True if delivered, None if the phone is gone, False on errors"""
        import aiohttp
        from pywebpush import WebPushException, webpush_async

        dev = self._devices[key]
        try:
            await webpush_async(
                subscription_info=dev["sub"],
                data=data,
                vapid_private_key=self._vapid,
                vapid_claims={"sub": VAPID_SUBJECT},
                ttl=TTL,
                headers={"Urgency": "high"},
                timeout=aiohttp.ClientTimeout(total=SEND_TIMEOUT),
                aiohttp_session=await self.http_session(),
            )
            return True
        except WebPushException as err:
            status = getattr(err.response, "status", None)
            if status in (404, 410):
                # browser data deleted, app removed or notifications turned off
                self.logger.warning(
                    f"{dev['name']} doesn't receive notifications anymore, removed"
                )
                self._devices.pop(key, None)
                return None
            error = f"{dev['name']}: {err.message.splitlines()[0]}"
        except Exception as err:
            error = f"{dev['name']}: {err or type(err).__name__}"
        self.logger.error(f"Notification failed: {error}")
        await fhem.readingsSingleUpdate(self.hash, "last_error", error, 1)
        return False

    # --- local https ---

    async def set_local_https(self, hash, params):
        hostname = None
        if params["hostname"]:
            hostname = certs.valid_hostname(params["hostname"])
        elif await self.https.names():
            hostname = (await self.https.names())[0]
        if hostname is None:
            return f"Invalid hostname {params['hostname']}"
        try:
            await self.https.setup(hostname)
        except RuntimeError as err:
            return str(err)
        await self.page_changed()
        return None

    async def page_changed(self):
        await fhem.FW_runJavascript(
            self.hash, "location.reload()", detail=self.hash["NAME"]
        )

    # --- FHEMWEB page ---

    async def remote_access(self):
        """(defined, https addresses) of the remote_access devices"""
        result = await fhem.sendCommandHash(
            self.hash,
            "my @d = grep { defined($defs{$_}) }"
            " devspec2array('FHEMPYTYPE=remote_access');"
            " join(' ', scalar(@d), grep { /^https:/ }"
            " map { ReadingsVal($_, 'url', '') } @d)",
        )
        parts = str(result or "").split()
        urls = [url for url in parts[1:] if url.startswith("https://")]
        return parts[:1] not in ([], ["0"]), urls

    async def page_url(self, fw_wname, host):
        """http address of this detail page in FHEMWEB fw_wname, the phone
        shows the steps for the local https address there"""
        if not fw_wname or not host:
            return None
        result = await fhem.sendCommandHash(
            self.hash,
            f"my $w = {fhem.perlString(fw_wname)};"
            " defined($defs{$w}) && !AttrVal($w, 'HTTPS', 0)"
            " ? $defs{$w}{PORT} . ' ' . AttrVal($w, 'webname', 'fhem') : ''",
        )
        match = re.fullmatch(r"(\d+) (\S+)", str(result or "").strip())
        if not match:
            return None
        netloc = f"{LocalHttps.url_host(host)}:{match.group(1)}"
        query = f"detail={self.hash['NAME']}"
        return urlunsplit(("http", netloc, "/" + match.group(2), query, ""))

    async def setup_html(self, fw_wname=None):
        if not hasattr(self, "hash") or self._vapid is None:
            return ""
        name = self.hash["NAME"]
        remote_defined, remote_urls = await self.remote_access()
        addresses = [
            {"url": f"{url}/fhem?detail={name}", "kind": "remote"}
            for url in remote_urls
        ]
        if self.https.url:
            addresses.append(
                {
                    "url": f"{self.https.url}/fhem?detail={name}",
                    "kind": "local",
                    "ca": self.https.ca_file,
                }
            )
            page = await self.page_url(fw_wname, self.https.host)
            if page:
                addresses[-1]["page"] = page
        for address in addresses:
            address["qr"] = qr_image(address.get("page") or address["url"])
        config = {
            "dev": name,
            "key": self.public_key,
            "devices": [
                {"id": key, "name": dev["name"]} for key, dev in self._devices.items()
            ],
            "addresses": addresses,
            "remote_access": remote_defined,
        }
        config_json = json.dumps(config).replace("<", "\\u003c")
        return (
            '<div class="makeTable wide"><span class="mkTitle">'
            "Notifications on your phone</span>"
            '<table class="block wide"><tr class="odd"><td>'
            f'<div id="fhempyPush">{html.escape("Loading...")}</div>'
            "</td></tr></table></div>"
            "<script>jQuery.getScript(FW_root+'/fhempy/push.js',function(){"
            f"fhempyPush({config_json})}});</script>"
        )


class LocalHttps:
    """FHEMWEB WEB<name> with https on a port of its own, certificate signed
    by the CA of this device. The normal FHEMWEB stays as it is."""

    def __init__(self, module):
        self.module = module
        self.url = ""

    @property
    def host(self):
        return urlsplit(self.url).hostname if self.url else None

    @property
    def hash(self):
        return self.module.hash

    @property
    def web_name(self):
        return "WEB" + self.hash["NAME"]

    @property
    def ca_file(self):
        return f"fhempy/{self.hash['NAME']}-ca.crt"

    @property
    def cert_prefix(self):
        return f"certs/fhempy-{self.hash['NAME']}-"

    async def reading(self, name):
        return await fhem.ReadingsVal(self.hash["NAME"], name, "")

    async def load_ca(self):
        from .. import utils

        key_text = await self.reading(".ca_key")
        cert_text = await self.reading(".ca_cert")
        if key_text and cert_text:
            try:
                key = certs.load_key(
                    utils.decrypt_string(key_text, self.module._unique_id)
                )
                return key, certs.load_cert(cert_text.replace("\\n", "\n"))
            except Exception:
                self.module.logger.exception("CA of the local https address broken")
        key, cert = certs.create_ca(f"{self.hash['NAME']} (FHEM)")
        await fhem.readingsSingleUpdate(
            self.hash,
            ".ca_key",
            utils.encrypt_string(certs.key_pem(key), self.module._unique_id),
            0,
        )
        await fhem.readingsSingleUpdate(
            self.hash, ".ca_cert", certs.cert_pem(cert).replace("\n", "\\n"), 0
        )
        return key, cert

    async def names(self, hostname=None):
        stored = (await self.reading(".https_names")).split()
        fhem_ip = fhem_address()
        detected = [fhem_ip] if fhem_ip else certs.local_names()
        names = []
        for name in ([hostname] if hostname else []) + stored + detected:
            if name and name not in names:
                names.append(name)
        return names

    async def setup(self, hostname):
        names = await self.names(hostname)
        await fhem.readingsSingleUpdate(self.hash, ".https_names", " ".join(names), 0)
        await self.write_certificates(names)
        port = await self.setup_fhemweb()
        self.url = f"https://{self.url_host(hostname)}:{port}"
        await fhem.readingsSingleUpdate(self.hash, "local_https", self.url, 1)

    @staticmethod
    def url_host(hostname):
        return f"[{hostname}]" if ":" in hostname else hostname

    async def renew_if_needed(self):
        """on start: certificate expires soon or new IP address"""
        url = await self.reading("local_https")
        if not url.startswith("https://"):
            return
        self.url = url
        try:
            names = await self.names()
            current = await fhem.sendCommandHash(
                self.hash,
                "my $f = AttrVal('global', 'modpath', '.') . '/' . "
                f"{fhem.perlString(self.cert_prefix + 'cert.pem')};"
                " open(my $fh, '<', $f) or return ''; local $/; my $c = <$fh>;"
                " close($fh); $c",
            )
            if current and not certs.needs_renewal(certs.load_cert(current), names):
                return
            self.module.logger.info("Renewing the certificate of the https address")
            await fhem.readingsSingleUpdate(
                self.hash, ".https_names", " ".join(names), 0
            )
            await self.write_certificates(names)
        except Exception:
            self.module.logger.exception("Renewing the https certificate failed")

    async def write_certificates(self, names):
        ca_key, ca_cert = await self.load_ca()
        key, cert = certs.create_server_cert(ca_key, ca_cert, names)
        result = await fhem.sendCommandHash(
            self.hash,
            "my $mp = AttrVal('global', 'modpath', '.');"
            f" my $prefix = $mp . '/' . {fhem.perlString(self.cert_prefix)};"
            f" my $ca = $mp . '/www/' . {fhem.perlString(self.ca_file)};"
            " my %files = ($prefix . 'key.pem' =>"
            f" {fhem.perlString(certs.key_pem(key))},"
            f" $prefix . 'cert.pem' => {fhem.perlString(certs.cert_pem(cert))},"
            f" $ca => {fhem.perlString(certs.cert_pem(ca_cert))});"
            " foreach my $f (sort keys %files) {"
            " my ($dir) = $f =~ m,^(.*)/,; mkdir($dir) if (!-d $dir);"
            " open(my $fh, '>', $f) or return 'error: ' . $f . ': ' . $!;"
            " print $fh $files{$f}; close($fh); }"
            " chmod(0600, $prefix . 'key.pem'); 'ok'",
        )
        if result != "ok":
            raise RuntimeError(f"Certificate files can't be written: {result}")

    async def setup_fhemweb(self):
        web = self.web_name
        comment = f"https address of {self.hash['NAME']} for notifications on the phone"
        result = await fhem.sendCommandHash(
            self.hash,
            f"my $web = {fhem.perlString(web)};"
            f" my $comment = {fhem.perlString(comment)};"
            f" my $prefix = {fhem.perlString(self.cert_prefix)};"
            " return 'error: ' . $web . ' already exists and is no FHEMWEB'"
            " if (defined($defs{$web}) && $defs{$web}{TYPE} ne 'FHEMWEB');"
            " eval { require IO::Socket::SSL; 1 } or return 'error: Perl can not"
            " use https, install it with: sudo apt install libio-socket-ssl-perl';"
            " my ($src) = grep { $_ ne $web && defined($defs{$_})"
            " && $defs{$_}{TYPE} eq 'FHEMWEB' }"
            " ('WEB', devspec2array('TYPE=FHEMWEB:FILTER=TEMPORARY!=1'));"
            " my $global = (!$src || ($defs{$src}{DEF} // '') =~ m/global/)"
            " ? ' global' : '';"
            " my $err = '';"
            " if (!defined($defs{$web})) {"
            f" foreach my $p ({FIRST_HTTPS_PORT}..{LAST_HTTPS_PORT}) {{"
            ' $err = CommandDefine(undef, "$web FHEMWEB $p$global") // "";'
            " last if (defined($defs{$web})); } }"
            " return 'error: FHEMWEB could not be created: ' . $err"
            " if (!defined($defs{$web}));"
            ' CommandAttr(undef, "$web comment $comment");'
            ' CommandAttr(undef, "$web sslCertPrefix $prefix")'
            " if (AttrVal($web, 'sslCertPrefix', '') ne $prefix);"
            # same password as the FHEMWEB in the home network
            " if ($src) { foreach my $al (devspec2array('TYPE=allowed')) {"
            " my $vf = AttrVal($al, 'validFor', ''); next if ($vf eq '');"
            " my @v = split(',', $vf);"
            ' CommandAttr(undef, "$al validFor $vf,$web")'
            " if ((grep { $_ eq $src } @v) && !(grep { $_ eq $web } @v)); }"
            f" foreach my $an (qw({LOOK_ATTRIBUTES})) {{"
            " my $v = AttrVal($src, $an, undef);"
            ' if (!defined($v)) { CommandDeleteAttr(undef, "$web $an")'
            " if (defined($attr{$web}{$an})); }"
            " elsif (AttrVal($web, $an, '') ne $v) {"
            ' CommandAttr(undef, "$web $an $v"); } } }'
            ' CommandAttr(undef, "$web HTTPS 1") if (!AttrVal($web, "HTTPS", 0));'
            " 'port ' . $defs{$web}{PORT}",
        )
        match = re.match(r"port (\d+)", str(result or ""))
        if not match:
            raise RuntimeError(str(result or "FHEMWEB could not be created"))
        return int(match.group(1))
