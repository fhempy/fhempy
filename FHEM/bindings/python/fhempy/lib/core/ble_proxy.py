"""
Bluetooth proxies as additional Bluetooth adapters of fhempy.

An esphome_ble_proxy device connects to one ESP32 with the bluetooth_proxy
component (core/ble_proxy only knows the proxies, not the ESPHome API). A
smlight_ble_proxy device receives the advertisements of the BLE proxy of
SLZB-OS (SMLIGHT gateways, scan only, no connections). Their
advertisements go to the same callbacks as the ones of the local adapters
(core/ble_scanner), and core/bluetoothle connects through a proxy if a proxy
receives the device better than the local adapters, or there is no local
adapter at all.

habluetooth and bleak-esphome (the libraries of Home Assistant) choose the
proxy with the best signal and a free connection slot. They are only imported
once a proxy is defined. fhempy doesn't use habluetooth for the local
adapters, they stay with core/ble_scanner and bt_recovery.

    proxy = ble_proxy.register(logger, cli, device_info, name)
    proxy = ble_proxy.register_smlight(logger, host, port, source, name)
    ...
    ble_proxy.unregister(proxy)
"""

import time

# devices seen by a proxy within this time are connected through it
RECENT_MAX_AGE = 60
# a local adapter is used if the proxy doesn't receive the device clearly
# better, the local connection has less latency and doesn't use a proxy slot
PREFER_LOCAL_DB = 10

_manager = None
_proxies = {}
# callback(address, address_type, rssi, data, proxy_name) for every raw
# advertisement, e.g. ble_monitor parses them like HCI packets
_raw_callbacks = []


def active(connectable=False):
    """True if at least one proxy is connected (connectable: one which can
    connect to devices, SMLIGHT proxies only scan)."""
    if connectable:
        return any(proxy.connectable for proxy in _proxies.values())
    return bool(_proxies)


def proxies():
    return list(_proxies.values())


def _get_manager():
    global _manager
    if _manager is None:
        # import only with a proxy, habluetooth isn't installed otherwise
        import asyncio

        from habluetooth import BluetoothManager, set_manager

        class _FhempyBluetoothManager(BluetoothManager):
            """Only the proxies, the advertisements are dispatched by
            Proxy itself (the manager skips repeated ones)."""

            def _discover_service_info(self, service_info):
                return None

        manager = _FhempyBluetoothManager()
        # no async_setup(): it would patch bleak's BleakScanner/BleakClient
        # for every module and take over the local adapters
        manager._loop = asyncio.get_running_loop()
        manager.async_setup_unavailable_tracking()
        set_manager(manager)
        _manager = manager
    return _manager


def load_libraries():
    """Imports the libraries of the proxies, takes a while on a Raspberry
    Pi: call it via utils.run_blocking before register()."""
    import aioesphomeapi  # noqa: F401
    import bleak_esphome.backend.client  # noqa: F401
    import bleak_esphome.backend.scanner  # noqa: F401
    import habluetooth  # noqa: F401


def load_smlight_libraries():
    """Imports bleak-smlight, call it via utils.run_blocking before
    register_smlight()."""
    import bleak_smlight  # noqa: F401
    import habluetooth  # noqa: F401
    import pysmlight  # noqa: F401


def add_raw_callback(callback):
    if callback not in _raw_callbacks:
        _raw_callbacks.append(callback)


def remove_raw_callback(callback):
    if callback in _raw_callbacks:
        _raw_callbacks.remove(callback)


class _BaseProxy:
    """Advertisements and devices of one proxy, self.scanner is its
    habluetooth scanner."""

    logger = None
    name = None
    scanner = None
    connectable = False
    advertisements = 0

    def _raw(self, address, address_type, rssi, data):
        for callback in list(_raw_callbacks):
            try:
                callback(address, address_type, rssi, data, self.name)
            except Exception:
                self.logger.exception("Failed to handle raw advertisement")

    def _dispatch(self, address):
        # the scanner merged advertisement and scan response (name)
        info = self.scanner._previous_service_info.get(address)
        if info is None:
            return
        self.advertisements += 1
        from . import ble_scanner

        scanner = ble_scanner.BleScanner.instance
        if scanner is not None:
            scanner.proxy_detection(info.device, info.advertisement)

    def recent_device(self, address, max_age=RECENT_MAX_AGE):
        """(BLEDevice, rssi) seen within max_age seconds, otherwise None."""
        info = self.scanner._previous_service_info.get(address.upper())
        if info is None or time.monotonic() - info.time > max_age:
            return None
        return info.device, info.rssi


class Proxy(_BaseProxy):
    """One connected ESPHome Bluetooth proxy."""

    def __init__(self, logger, cli, device_info, name):
        from aioesphomeapi import BluetoothProxyFeature
        from bleak_esphome.backend.client import ESPHomeClient, ESPHomeClientData
        from bleak_esphome.backend.device import ESPHomeBluetoothDevice
        from bleak_esphome.backend.scanner import ESPHomeScanner
        from bluetooth_data_tools import int_to_bluetooth_address
        from habluetooth import HaBluetoothConnector

        manager = _get_manager()
        self.logger = logger
        self.name = name
        self.source = device_info.bluetooth_mac_address or device_info.mac_address
        self._int_to_address = int_to_bluetooth_address
        flags = device_info.bluetooth_proxy_feature_flags_compat(cli.api_version)
        self.connectable = bool(flags & BluetoothProxyFeature.ACTIVE_CONNECTIONS)
        self.advertisements = 0

        # like bleak_esphome.connect_scanner(), but every advertisement is
        # dispatched to the fhempy modules as well
        self.device = ESPHomeBluetoothDevice(name, self.source, available=True)
        self.device.async_subscribe_connection_slots(
            manager.async_on_allocation_changed
        )
        client_data = ESPHomeClientData(
            bluetooth_device=self.device,
            client=cli,
            device_info=device_info,
            api_version=cli.api_version,
            title=name,
            scanner=None,
        )
        self._client_data = client_data
        connector = HaBluetoothConnector(
            client=lambda *args, **kwargs: ESPHomeClient(
                *args, client_data=client_data, **kwargs
            ),
            source=self.source,
            can_connect=self._can_connect,
        )
        self.scanner = ESPHomeScanner(self.source, name, connector, self.connectable)
        self.scanner.set_bluetooth_device(self.device)
        client_data.scanner = self.scanner

        if self.connectable:
            cli.subscribe_bluetooth_connections_free(
                self.device.async_update_ble_connection_limits
            )
        if flags & BluetoothProxyFeature.FEATURE_STATE_AND_MODE:
            cli.subscribe_bluetooth_scanner_state(
                self.scanner.async_update_scanner_state
            )
            self.scanner.set_client(cli)
        if flags & BluetoothProxyFeature.RAW_ADVERTISEMENTS:

            def subscribe():
                return cli.subscribe_bluetooth_le_raw_advertisements(self._on_raw)

            subscribe()
            if flags & BluetoothProxyFeature.FEATURE_STATE_AND_MODE:
                # only one API client may receive the advertisements, a
                # stale connection holds the subscription for a while
                self.scanner.set_resubscribe_advertisements(subscribe)
        else:
            cli.subscribe_bluetooth_le_advertisements(self._on_advertisement)

        self._unsetup = self.scanner.async_setup()
        self._unregister = manager.async_register_scanner(self.scanner)

    def _can_connect(self):
        return bool(self.device.available and self.device.ble_connections_free)

    @property
    def connections_free(self):
        return self.device.ble_connections_free

    @property
    def connections_limit(self):
        return self.device.ble_connections_limit

    def close(self):
        self.device.async_set_unavailable()
        for callback in list(self._client_data.disconnect_callbacks):
            try:
                callback()
            except Exception:
                self.logger.debug("Failed to run disconnect callback", exc_info=True)
        self._client_data.disconnect_callbacks.clear()
        self._unregister()
        self._unsetup()

    # --- advertisements ---

    def _on_raw(self, raw):
        self.scanner.async_on_raw_advertisements(raw)
        advertisements = raw.advertisements
        # no iteration over the protobuf field, see bleak_esphome
        for i in range(len(advertisements)):
            adv = advertisements[i]
            address = self._int_to_address(adv.address)
            self._raw(address, adv.address_type, adv.rssi, adv.data)
            self._dispatch(address)

    def _on_advertisement(self, adv):
        self.scanner.async_on_advertisement(adv)
        self._dispatch(self._int_to_address(adv.address))


class SmlightProxy(_BaseProxy):
    """BLE proxy of SLZB-OS (SMLIGHT): advertisements via UDP, no
    connections. pysmlight's client sends a keepalive every 2s and retries
    on its own, see bleak-smlight."""

    def __init__(self, logger, host, port, source, name, active_scan=False):
        from bleak_smlight import connect_scanner
        from habluetooth import BluetoothScanningMode

        manager = _get_manager()
        self.logger = logger
        self.name = name
        self.source = source
        self.connectable = False
        self.advertisements = 0
        data = connect_scanner(source, name, host, port)
        self.scanner = data.scanner
        self.client = data.client
        self._handle = self.scanner._handle_raw_advertisement
        # every advertisement goes to the fhempy modules as well
        data.client.callback = self._on_raw
        self._unsetup = self.scanner.async_setup()
        self._unregister = manager.async_register_scanner(self.scanner)
        self._mode = (
            BluetoothScanningMode.ACTIVE
            if active_scan
            else BluetoothScanningMode.PASSIVE
        )

    async def start(self):
        await self.client.start()

    def send_scan_mode(self):
        """Tells the proxy to scan passive or active. Only works once the
        proxy answered (connected), it forgets it after a reboot: call it
        regularly."""
        if self.connected:
            self.scanner.async_set_scanning_mode(self._mode)

    @property
    def connected(self):
        """The proxy answered the keepalive."""
        return self.client._connected_evt.is_set()

    def _on_raw(self, mac_bytes, rssi, address_type, raw_data):
        self._handle(mac_bytes, rssi, address_type, raw_data)
        address = ":".join(f"{b:02X}" for b in reversed(mac_bytes))
        self._raw(address, address_type, rssi, raw_data)
        self._dispatch(address)

    @property
    def connections_free(self):
        return 0

    @property
    def connections_limit(self):
        return 0

    def close(self):
        try:
            self.client.stop()
        finally:
            self._unregister()
            self._unsetup()


def register_smlight(logger, host, port, source, name, active_scan=False):
    """Registers a SMLIGHT proxy, call await proxy.start() afterwards."""
    old = _proxies.get(source)
    if old is not None:
        unregister(old)
    proxy = SmlightProxy(logger, host, port, source, name, active_scan)
    _proxies[proxy.source] = proxy
    return proxy


def register(logger, cli, device_info, name):
    proxy = Proxy(logger, cli, device_info, name)
    _proxies[proxy.source] = proxy
    return proxy


def unregister(proxy):
    if _proxies.get(proxy.source) is proxy:
        del _proxies[proxy.source]
    proxy.close()


def best_device(address, connectable=True):
    """(BLEDevice, rssi, proxy) of the proxy with the best signal, None if no
    proxy saw the device recently."""
    best = None
    for proxy in _proxies.values():
        if connectable and not proxy.connectable:
            continue
        found = proxy.recent_device(address)
        if found is not None and (best is None or found[1] > best[1]):
            best = (found[0], found[1], proxy)
    return best


def use_proxy(proxy_rssi, local_rssi):
    """Connect through the proxy instead of the local adapter?"""
    if local_rssi is None:
        return True
    return proxy_rssi > local_rssi + PREFER_LOCAL_DB


def is_proxy_device(device):
    """The BLEDevice was received by an ESPHome proxy (not by BlueZ)."""
    details = getattr(device, "details", None)
    return isinstance(details, dict) and details.get("source") in _proxies


def bleak_client(device, disconnected_callback=None, timeout=10.0):
    """BleakClient for a device of the shared scan: via BlueZ or via the
    proxy which received it."""
    if is_proxy_device(device):
        return client(device, disconnected_callback, timeout)
    from bleak import BleakClient

    return BleakClient(
        device, disconnected_callback=disconnected_callback, timeout=timeout
    )


def client(device, disconnected_callback, timeout):
    """BleakClient connecting through the best proxy with a free slot."""
    from habluetooth import HaBleakClientWrapper

    return HaBleakClientWrapper(
        device,
        disconnected_callback=disconnected_callback,
        timeout=timeout,
        # bluetoothle has its own retry loop
        _is_retry_client=True,
    )
