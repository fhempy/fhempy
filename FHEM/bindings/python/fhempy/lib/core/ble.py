"""
A simple wrapper for bluepy's btle.Connection.
Handles Connection duties (reconnecting etc.) transparently.
"""
import codecs
import logging
import re

import dbus
from bluepy import btle

DEFAULT_TIMEOUT = 1

_LOGGER = logging.getLogger("core.ble")


class Peripheral(btle.Peripheral):
    def __init__(
        self, deviceAddr=None, addrType=btle.ADDR_TYPE_PUBLIC, iface=None, timeout=None
    ):
        btle.BluepyHelper.__init__(self)
        self._serviceMap = None  # Indexed by UUID
        (self.deviceAddr, self.addrType, self.iface) = (None, None, None)

        if isinstance(deviceAddr, btle.ScanEntry):
            self._connect(
                deviceAddr.addr, deviceAddr.addrType, deviceAddr.iface, timeout
            )
        elif deviceAddr is not None:
            self._connect(deviceAddr, addrType, iface, timeout)

    def _connect(self, addr, addrType=btle.ADDR_TYPE_PUBLIC, iface=None, timeout=None):
        if len(addr.split(":")) != 6:
            raise ValueError("Expected MAC address, got %s" % repr(addr))
        if addrType not in (btle.ADDR_TYPE_PUBLIC, btle.ADDR_TYPE_RANDOM):
            raise ValueError(
                "Expected address type public or random, got {}".format(addrType)
            )
        self._startHelper(iface)
        self.addr = addr
        self.addrType = addrType
        self.iface = iface
        if iface is not None:
            self._writeCmd("conn %s %s %s\n" % (addr, addrType, "hci" + str(iface)))
        else:
            self._writeCmd("conn %s %s\n" % (addr, addrType))
        rsp = self._getResp("stat", timeout)
        if rsp is None:
            raise btle.BTLEDisconnectError(
                "Timed out while trying to connect to peripheral %s, addr type: %s"
                % (addr, addrType),
                rsp,
            )
        while rsp["state"][0] == "tryconn":
            rsp = self._getResp("stat", timeout)
        if rsp["state"][0] != "conn":
            self._stopHelper()
            raise btle.BTLEDisconnectError(
                "Failed to connect to peripheral %s, addr type: %s" % (addr, addrType),
                rsp,
            )

    def connect(self, addr, addrType=btle.ADDR_TYPE_PUBLIC, iface=None, timeout=None):
        if isinstance(addr, btle.ScanEntry):
            self._connect(addr.addr, addr.addrType, addr.iface, timeout)
        elif addr is not None:
            self._connect(addr, addrType, iface, timeout)


class BTLEConnection(btle.DefaultDelegate):
    """Representation of a BTLE Connection."""

    def __init__(self, mac, keep_connected=False, connection_established_callback=None):
        """Initialize the connection."""
        btle.DefaultDelegate.__init__(self)

        self._ifaces = self.get_hci_ifaces()
        self._iface_idx = 0

        self._conn = None
        self._mac = mac
        self._callbacks = {}
        self._keep_connected = keep_connected
        self._connection_etablished_callback = connection_established_callback

    def set_keep_connected(self, new_state):
        self._keep_connected = new_state
        if new_state == False:
            if self._conn:
                try:
                    self._conn.disconnect()
                except Exception:
                    pass

    def next_iface(self):
        self._nr_conn_errors += 1
        self._iface_idx = (self._iface_idx + 1) % len(self._ifaces)
        if self._nr_conn_errors >= len(self._ifaces) * 5:
            return False
        return True

    def get_hci_ifaces(self):
        iface_list = []
        bus = dbus.SystemBus()
        manager = dbus.Interface(
            bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager"
        )
        objects = manager.GetManagedObjects()
        for path, interfaces in objects.items():
            adapter = interfaces.get("org.bluez.Adapter1")
            if adapter is None:
                continue
            iface_list.append(re.search(r"\d+$", path)[0])
        return iface_list

    def __enter__(self):
        """
        Context manager __enter__ for connecting the device
        :rtype: btle.Peripheral
        :return:
        """
        conn_state = ""
        try:
            if self._conn:
                conn_state = self._conn.getState()
        except (btle.BTLEInternalError, btle.BTLEDisconnectError):
            self._conn = None

        if self._conn is None or conn_state != "conn":
            self._conn = Peripheral()
            self._conn.withDelegate(self)
            self._nr_conn_errors = 0
            _LOGGER.debug("Trying to connect to %s", self._mac)
            while True:
                # try to connect with all ifaces
                try:
                    self._conn.connect(
                        self._mac, iface=self._ifaces[self._iface_idx], timeout=10
                    )
                    if self._connection_etablished_callback is not None:
                        self._connection_etablished_callback(self._mac)
                    break
                except btle.BTLEException as ex:
                    _LOGGER.debug(
                        "Unable to connect to the device %s using iface %s, retrying: %s",
                        self._mac,
                        self._ifaces[self._iface_idx],
                        ex,
                    )
                    try:
                        self._conn.connect(
                            self._mac, iface=self._ifaces[self._iface_idx], timeout=10
                        )
                        if self._connection_etablished_callback is not None:
                            self._connection_etablished_callback(self._mac)
                        break
                    except Exception as ex2:
                        _LOGGER.debug(
                            "Second connection try to %s using ifaces %s failed: %s",
                            self._mac,
                            self._ifaces[self._iface_idx],
                            ex2,
                        )
                        if self.next_iface() is False:
                            # tried all ifaces, raise exception
                            raise

        _LOGGER.debug("Connected to %s", self._mac)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._conn and self._keep_connected is False:
            self._conn.disconnect()
            self._conn = None

    def handleNotification(self, handle, data):
        """Handle Callback from a Bluetooth (GATT) request."""
        _LOGGER.debug(
            "Got notification from %s: %s", handle, codecs.encode(data, "hex")
        )
        if handle in self._callbacks:
            for callback in self._callbacks[handle]:
                callback(data)

    @property
    def mac(self):
        """Return the MAC address of the connected device."""
        return self._mac

    def set_callback(self, handle, function):
        """Set the callback for a Notification handle. It will be called with the parameter data, which is binary."""
        if handle not in self._callbacks:
            self._callbacks[handle] = []
        self._callbacks[handle].append(function)

    def read_characteristic(self, handle):
        with self:
            return self._conn.readCharacteristic(handle)

    def write_characteristic(
        self, handle, value, timeout=DEFAULT_TIMEOUT, with_response=True
    ):
        """Write a GATT Command without callback - not utf-8."""
        try:
            with self:
                _LOGGER.debug(
                    "Writing %s to %s with with_response=%s",
                    codecs.encode(value, "hex"),
                    handle,
                    with_response,
                )
                self._conn.writeCharacteristic(
                    handle, value, withResponse=with_response
                )
                if timeout:
                    _LOGGER.debug("Waiting for notifications for %s", timeout)
                    self._conn.waitForNotifications(timeout)
        except btle.BTLEException as ex:
            _LOGGER.debug("Got exception from bluepy while making a request: %s", ex)
            raise
