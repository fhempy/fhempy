"""SMLIGHT BLE proxy: the Bluetooth of a SLZB gateway (SLZB-OS) as additional
Bluetooth receiver for the Bluetooth modules of fhempy (see core/ble_proxy).

SLZB-OS forwards BLE advertisements via UDP (port 5050, bleak-smlight and
pysmlight). It only scans, connections (e.g. eq3bt) still need a local adapter
or an ESPHome proxy. The gateway keeps running its own firmware (Zigbee,
Thread border router).
"""

import asyncio
import functools
import ipaddress
import socket

from .. import fhem, generic, utils
from ..core import ble_proxy

USAGE = "Usage: define <name> fhempy smlight_ble_proxy <host>"
DEFAULT_PORT = 5050
READINGS_INTERVAL = 60
INFO_TIMEOUT = 10
# no advertisement for this long: the BLE proxy is probably off in SLZB-OS
SILENT_AFTER = 180
# seconds to wait for the first answer of the proxy
CONNECT_WAIT = 5


def _parse_host(text):
    host, sep, port = text.rpartition(":")
    if sep and port.isdigit() and "]" not in port:
        return host.strip("[]"), int(port)
    return text, DEFAULT_PORT


def _format_mac(mac):
    if not mac:
        return None
    digits = "".join(c for c in str(mac) if c.isalnum()).upper()
    if len(digits) != 12:
        return None
    return ":".join(digits[i : i + 2] for i in range(0, 12, 2))


async def resolve(host):
    """IPv4 address of the host: pysmlight sends a keepalive every 2s, with a
    hostname every send would resolve it (blocking)."""
    try:
        ipaddress.ip_address(host)
        return host
    except ValueError:
        pass
    infos = await asyncio.get_running_loop().getaddrinfo(
        host, None, family=socket.AF_INET, type=socket.SOCK_DGRAM
    )
    return infos[0][4][0]


async def read_info(host):
    """Device info of the SLZB web API: dict with mac, model, firmware,
    hostname and ble_proxy (True/False/None), None if it can't be read (e.g.
    password protected web interface, which isn't needed for the proxy)."""
    from pysmlight import Api2

    api = Api2(host)
    try:
        info = await asyncio.wait_for(api.get_info(), INFO_TIMEOUT)
    finally:
        await api.close()
    ble = getattr(info, "ble", None)
    return {
        "mac": _format_mac(info.MAC),
        "model": info.model,
        "firmware": info.sw_version,
        "hostname": info.hostname,
        "ble_proxy": None if ble is None else ble.proxy_enabled,
    }


class smlight_ble_proxy(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self._errors = utils.ErrorLogger(logger)
        self._proxy = None
        self._readings_task = None
        self._last_advertisements = 0
        self._silent_since = None
        self._ble_proxy_enabled = None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        if len(args) != 4 or argsh:
            return USAGE
        await super().Define(hash, args, argsh)
        await self.set_icon("bluetooth")
        await self.set_attr_config(
            {
                "scan_mode": {
                    "default": "passive",
                    "options": "passive,active",
                    "help": "passive: only listen (default). active: also ask "
                    "the devices for their scan response (e.g. the name), "
                    "uses a bit more battery of the devices.",
                },
            }
        )
        self._host, self._port = _parse_host(args[3])
        await fhem.readingsSingleUpdate(self.hash, "state", "connecting", 1)
        self.create_async_task(self._start())

    async def set_attr_scan_mode(self, hash):
        if self._proxy is not None:
            # the mode is passed to the scanner when it's created
            await self._start()

    async def _start(self):
        while True:
            try:
                ip = await resolve(self._host)
                break
            except OSError as exc:
                await fhem.readingsSingleUpdateIfChanged(
                    self.hash, "state", f"{self._host} not found", 1
                )
                self._errors.failed(
                    f"Can't resolve {self._host}", exc=exc, traceback=False
                )
                await asyncio.sleep(self._errors.next_delay(minimum=10, maximum=300))
        self._errors.success()
        info = None
        try:
            info = await read_info(ip)
        except Exception as exc:
            self.logger.info(
                f"Couldn't read the device info of {self._host} ({exc}), "
                "the BLE proxy works without it"
            )
        if info is not None:
            self._ble_proxy_enabled = info["ble_proxy"]
            await fhem.readingsBeginUpdate(self.hash)
            for reading in ("model", "firmware", "hostname"):
                if info[reading]:
                    await fhem.readingsBulkUpdateIfChanged(
                        self.hash, reading, info[reading]
                    )
            if info["mac"]:
                await fhem.readingsBulkUpdateIfChanged(self.hash, "mac", info["mac"])
            await fhem.readingsEndUpdate(self.hash, 1)
        source = (info or {}).get("mac") or await fhem.ReadingsVal(
            self.hash["NAME"], "mac", ""
        )
        if not source:
            source = f"smlight-{self._host}"
        await utils.run_blocking(functools.partial(ble_proxy.load_smlight_libraries))
        self._drop_proxy()
        self._proxy = ble_proxy.register_smlight(
            self.logger,
            ip,
            self._port,
            source,
            self.hash["NAME"],
            active_scan=self._attr_scan_mode == "active",
        )
        proxy = self._proxy
        await proxy.start()
        self._last_advertisements = 0
        self._silent_since = asyncio.get_running_loop().time()
        if self._readings_task is None or self._readings_task.done():
            self._readings_task = self.create_async_task(self._update_readings())
        # the scan mode can only be sent once the proxy answered
        for _ in range(CONNECT_WAIT * 2):
            if proxy.connected or proxy is not self._proxy:
                break
            await asyncio.sleep(0.5)
        proxy.send_scan_mode()
        await self._update_state()

    def _drop_proxy(self):
        if self._proxy is not None:
            ble_proxy.unregister(self._proxy)
            self._proxy = None

    def _state(self, per_minute=None):
        proxy = self._proxy
        if proxy is None:
            return "connecting"
        if self._ble_proxy_enabled is False:
            return "BLE proxy disabled in SLZB-OS"
        if not proxy.connected:
            return "connecting"
        now = asyncio.get_running_loop().time()
        if per_minute:
            self._silent_since = None
        elif self._silent_since is None:
            self._silent_since = now
        if self._silent_since is not None and now - self._silent_since > SILENT_AFTER:
            return "no advertisements, BLE proxy enabled in SLZB-OS?"
        return "connected"

    async def _update_state(self, per_minute=None):
        state = self._state(per_minute)
        await fhem.readingsSingleUpdateIfChanged(self.hash, "state", state, 1)
        if state == "BLE proxy disabled in SLZB-OS":
            self._errors.failed(
                f"The BLE proxy of {self._host} is disabled, enable it in the "
                "SLZB-OS web interface (Bluetooth)",
                exc=None,
            )

    async def _update_readings(self):
        while True:
            await asyncio.sleep(READINGS_INTERVAL)
            proxy = self._proxy
            if proxy is None:
                continue
            # SLZB-OS forgets the scan mode after a reboot
            proxy.send_scan_mode()
            count = proxy.advertisements
            per_minute = max(0, count - self._last_advertisements)
            self._last_advertisements = count
            await fhem.readingsSingleUpdateIfChanged(
                self.hash, "advertisements_per_minute", per_minute, 1
            )
            await self._update_state(per_minute)

    # FHEM FUNCTION
    async def Undefine(self, hash):
        self._drop_proxy()
        await super().Undefine(hash)
