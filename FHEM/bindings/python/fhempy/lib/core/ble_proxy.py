"""
ESPHome Bluetooth proxies as additional Bluetooth adapters of fhempy.

An esphome_ble_proxy device connects to one ESP32 with the bluetooth_proxy
component (core/ble_proxy only knows the proxies, not the ESPHome API). Its
advertisements go to the same callbacks as the ones of the local adapters
(core/ble_scanner), and core/bluetoothle connects through a proxy if a proxy
receives the device better than the local adapters, or there is no local
adapter at all.

habluetooth and bleak-esphome (the libraries of Home Assistant) choose the
proxy with the best signal and a free connection slot. They are only imported
once a proxy is defined. fhempy doesn't use habluetooth for the local
adapters, they stay with core/ble_scanner and bt_recovery.

    proxy = ble_proxy.register(logger, cli, device_info, name)
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


def active():
    """True if at least one proxy is connected."""
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


def add_raw_callback(callback):
    if callback not in _raw_callbacks:
        _raw_callbacks.append(callback)


def remove_raw_callback(callback):
    if callback in _raw_callbacks:
        _raw_callbacks.remove(callback)


class Proxy:
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
            for callback in list(_raw_callbacks):
                try:
                    callback(address, adv.address_type, adv.rssi, adv.data, self.name)
                except Exception:
                    self.logger.exception("Failed to handle raw advertisement")
            self._dispatch(address)

    def _on_advertisement(self, adv):
        self.scanner.async_on_advertisement(adv)
        self._dispatch(self._int_to_address(adv.address))

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

    # --- devices ---

    def recent_device(self, address, max_age=RECENT_MAX_AGE):
        """(BLEDevice, rssi) seen within max_age seconds, otherwise None."""
        info = self.scanner._previous_service_info.get(address.upper())
        if info is None or time.monotonic() - info.time > max_age:
            return None
        return info.device, info.rssi


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
