"""
A simple wrapper for bluepy's btle.Connection.
Handles Connection duties (reconnecting etc.) transparently.
"""
import logging
import codecs
import dbus
import re

from bluepy import btle

DEFAULT_TIMEOUT = 1

_LOGGER = logging.getLogger(__name__)

class BTLEConnection(btle.DefaultDelegate):
    """Representation of a BTLE Connection."""

    def __init__(self, mac):
        """Initialize the connection."""
        btle.DefaultDelegate.__init__(self)

        self._ifaces = self.get_hci_ifaces()
        self._iface_idx = 0

        self._conn = None
        self._mac = mac
        self._callbacks = {}
    
    def next_iface(self):
        self._iface_idx += 1
        if self._iface_idx >= len(self._ifaces):
            self._iface_idx = 0
            return False
        return True

    def get_hci_ifaces(self):
        iface_list = []
        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager")
        objects = manager.GetManagedObjects()
        for path, interfaces in objects.items():
            adapter = interfaces.get("org.bluez.Adapter1")
            if adapter is None:
                continue
            iface_list.append(re.search(r'\d+$', path)[0])
        return iface_list

    def __enter__(self):
        """
        Context manager __enter__ for connecting the device
        :rtype: btle.Peripheral
        :return:
        """
        self._conn = btle.Peripheral()
        self._conn.withDelegate(self)
        _LOGGER.debug("Trying to connect to %s", self._mac)
        while True:
            # try to connect with all ifaces
          try:
              self._conn.connect(self._mac, iface=self._ifaces[self._iface_idx])
              break
          except btle.BTLEException as ex:
              _LOGGER.debug("Unable to connect to the device %s using iface %s, retrying: %s", self._mac, self._ifaces[self._iface_idx], ex)
              try:
                  self._conn.connect(self._mac, iface=self._ifaces[self._iface_idx])
                  break
              except Exception as ex2:
                  _LOGGER.debug("Second connection try to %s using ifaces %s failed: %s", self._mac, self._ifaces[self._iface_idx],ex2)
                  if self.next_iface() is False:
                      raise

        _LOGGER.debug("Connected to %s", self._mac)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._conn:
            self._conn.disconnect()
            self._conn = None

    def handleNotification(self, handle, data):
        """Handle Callback from a Bluetooth (GATT) request."""
        _LOGGER.debug("Got notification from %s: %s", handle, codecs.encode(data, 'hex'))
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

    def make_request(self, handle, value, timeout=DEFAULT_TIMEOUT, with_response=True):
        """Write a GATT Command without callback - not utf-8."""
        try:
            with self:
                _LOGGER.debug("Writing %s to %s with with_response=%s", codecs.encode(value, 'hex'), handle, with_response)
                self._conn.writeCharacteristic(handle, value, withResponse=with_response)
                if timeout:
                    _LOGGER.debug("Waiting for notifications for %s", timeout)
                    self._conn.waitForNotifications(timeout)
        except btle.BTLEException as ex:
            _LOGGER.debug("Got exception from bluepy while making a request: %s", ex)
            raise