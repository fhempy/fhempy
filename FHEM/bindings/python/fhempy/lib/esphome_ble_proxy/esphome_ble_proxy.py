"""ESPHome Bluetooth proxy: an ESP32 as additional Bluetooth adapter for all
Bluetooth modules of fhempy (see core/ble_proxy)."""

import asyncio
import functools
import ipaddress

from aioesphomeapi import APIClient, ReconnectLogic
from aioesphomeapi.core import (
    InvalidAuthAPIError,
    InvalidEncryptionKeyAPIError,
    RequiresEncryptionAPIError,
)

from .. import fhem, generic, utils
from ..core import ble_proxy
from ..core.zeroconf import zeroconf

USAGE = "Usage: define <name> fhempy esphome_ble_proxy <host>[:port] [encryption_key]"
DEFAULT_PORT = 6053
READINGS_INTERVAL = 60


def _is_ip(text):
    try:
        ipaddress.ip_address(text)
    except ValueError:
        return False
    return True


def _parse_host(text):
    host, sep, port = text.rpartition(":")
    if sep and port.isdigit() and "]" not in port:
        return host.strip("[]"), int(port)
    return text, DEFAULT_PORT


def _encryption_key(args, argsh):
    """Return the encryption key from the define arguments.

    FHEM's parseParams() treats every word containing "=" as key=value, so a
    Base64 key with padding ("...xyz=") arrives in argsh as {"...xyz": ""}.
    Join it back to the original string.
    """
    if len(args) > 4:
        return args[4] or None
    if argsh:
        name, value = next(iter(argsh.items()))
        return f"{name}={value}"
    return None


class esphome_ble_proxy(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self._errors = utils.ErrorLogger(logger)
        self._cli = None
        self._reconnect = None
        self._proxy = None
        self._readings_task = None
        self._last_advertisements = 0

    @staticmethod
    def validate_define(args, argsh):
        if len(args) == 5 and not argsh:
            return None
        if len(args) == 4 and len(argsh) <= 1:
            return None
        return USAGE

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        error = self.validate_define(args, argsh)
        if error:
            return error
        await super().Define(hash, args, argsh)
        await self.set_icon("bluetooth")

        self._host, self._port = _parse_host(args[3])
        self._key = _encryption_key(args, argsh)
        await fhem.readingsSingleUpdate(self.hash, "state", "connecting", 1)
        self.create_async_task(self._start())

    async def _start(self):
        azc = zeroconf.get_instance(self.logger).get_async_zeroconf()
        self._cli = APIClient(
            self._host,
            self._port,
            "",
            client_info="fhempy",
            zeroconf_instance=azc,
            noise_psk=self._key,
        )
        name = self._host.removesuffix(".local")
        self._reconnect = ReconnectLogic(
            client=self._cli,
            on_connect=self._on_connect,
            on_disconnect=self._on_disconnect,
            on_connect_error=self._on_connect_error,
            zeroconf_instance=azc,
            name=None if _is_ip(name) else name,
        )
        await self._reconnect.start()

    async def _on_connect(self):
        try:
            info = await self._cli.device_info()
        except Exception as exc:
            self._errors.failed("Failed to read device info", exc=exc)
            return
        flags = info.bluetooth_proxy_feature_flags_compat(self._cli.api_version)
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdateIfChanged(self.hash, "name", info.name)
        await fhem.readingsBulkUpdateIfChanged(self.hash, "model", info.model)
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "esphome_version", info.esphome_version
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "bluetooth_mac", info.bluetooth_mac_address or info.mac_address
        )
        await fhem.readingsEndUpdate(self.hash, 1)
        if not flags:
            await fhem.readingsSingleUpdate(
                self.hash, "state", "no bluetooth_proxy configured", 1
            )
            self.logger.error(
                f"{info.name} has no bluetooth_proxy, add 'bluetooth_proxy:' "
                "(and 'active: true' for connections) to its ESPHome YAML"
            )
            return
        await utils.run_blocking(functools.partial(ble_proxy.load_libraries))
        self._drop_proxy()
        self._proxy = ble_proxy.register(
            self.logger, self._cli, info, info.friendly_name or info.name
        )
        self._errors.success()
        await fhem.readingsSingleUpdate(
            self.hash,
            "active_connections",
            "yes" if self._proxy.connectable else "no (active: false)",
            1,
        )
        await fhem.readingsSingleUpdate(self.hash, "state", "connected", 1)
        if self._readings_task is None or self._readings_task.done():
            self._readings_task = self.create_async_task(self._update_readings())

    async def _on_disconnect(self, expected_disconnect):
        self._drop_proxy()
        await fhem.readingsSingleUpdate(self.hash, "state", "disconnected", 1)

    async def _on_connect_error(self, exc):
        if isinstance(exc, RequiresEncryptionAPIError):
            state = "encryption key required"
        elif isinstance(exc, (InvalidEncryptionKeyAPIError, InvalidAuthAPIError)):
            state = "wrong encryption key"
        else:
            state = "disconnected"
        await fhem.readingsSingleUpdateIfChanged(self.hash, "state", state, 1)
        self._errors.failed(
            f"Connection to {self._host} failed", exc=exc, traceback=False
        )

    def _drop_proxy(self):
        if self._proxy is not None:
            ble_proxy.unregister(self._proxy)
            self._proxy = None

    async def _update_readings(self):
        while True:
            await asyncio.sleep(READINGS_INTERVAL)
            proxy = self._proxy
            if proxy is None:
                continue
            count = proxy.advertisements
            per_minute = max(0, count - self._last_advertisements)
            self._last_advertisements = count
            await fhem.readingsBeginUpdate(self.hash)
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "advertisements_per_minute", per_minute
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "connections_free", proxy.connections_free
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "connections_limit", proxy.connections_limit
            )
            await fhem.readingsEndUpdate(self.hash, 1)

    # FHEM FUNCTION
    async def Undefine(self, hash):
        self._drop_proxy()
        reconnect, self._reconnect = self._reconnect, None
        cli, self._cli = self._cli, None
        if reconnect is not None:
            await reconnect.stop()
        if cli is not None:
            try:
                await cli.disconnect()
            except Exception:
                self.logger.debug("Failed to disconnect", exc_info=True)
        await super().Undefine(hash)
