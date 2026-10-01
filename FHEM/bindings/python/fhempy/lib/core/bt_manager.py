import enum
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib


AGENT_PATH = "/fhempy/agent"
AGENT_INTERFACE = "org.bluez.Agent1"
BUS_NAME = "org.bluez"


class PairingState(enum.Enum):
    SUCCESS = 0
    WRONG_PIN = 1
    TIMEOUT = 2
    FAILED = 3


class AutoAgent(dbus.service.Object):
    """
    BlueZ Agent1 implementation that automatically responds with
    a predefined PIN during pairing.
    """

    def __init__(self, bus, path, logger, pin_code):
        super().__init__(bus, path)
        self.logger = logger
        self.pin_code = pin_code

    @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
    def Release(self):
        self.logger.info("[Agent] Released")

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        self.logger.info(f"[Agent] RequestPinCode for device {device}")
        self.logger.info(f"[Agent] Using PIN: {self.pin_code}")
        return self.pin_code
    
    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="u")
    def RequestPasskey(self, device):
        self.logger.info(f"[Agent] RequestPasskey for {device}")
        self.logger.info(f"[Agent] Using PIN: {self.pin_code}")
        return dbus.UInt32(int(self.pin_code))

    @dbus.service.method(AGENT_INTERFACE, in_signature="ou", out_signature="")
    def RequestConfirmation(self, device, passkey):
        self.logger.info(f"[Agent] RequestConfirmation for {device} (Passkey: {passkey:06d}) -> Auto-confirming")
        return

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="")
    def RequestAuthorization(self, device):
        self.logger.info(f"[Agent] RequestAuthorization for {device} -> Auto-confirming")
        return

    @dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
    def AuthorizeService(self, device, uuid):
        self.logger.info(f"[Agent] Request Service Authorization for {device}, Service: {uuid} -> Auto-confirming")
        return

    @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
    def Cancel(self):
        self.logger.info("[Agent] Pairing cancelled by remote device")


class BluetoothManager:
    def __init__(self, logger):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.loop = GLib.MainLoop()

        self.logger = logger
        self.bus = dbus.SystemBus()
        self.adapter = self._get_adapter()
        self.adapter_props = dbus.Interface(
            self.adapter, "org.freedesktop.DBus.Properties"
        )
        self.adapter_obj = dbus.Interface(self.adapter, "org.bluez.Adapter1")
        self.object_manager = dbus.Interface(
            self.bus.get_object(BUS_NAME, "/"), "org.freedesktop.DBus.ObjectManager"
        )
        self.agent = None

    def _get_adapter(self, adapter_name="hci0"):
        """Fetches the default adapter object."""
        try:
            return self.bus.get_object(BUS_NAME, f"/org/bluez/{adapter_name}")
        except dbus.DBusException as e:
            self.logger.error(f"Error: Adapter {adapter_name} not found.")
            raise e

    def _run_loop(self, timeout_sec):
        """Helper to run the GLib event loop until loop.quit() or timeout."""
        def on_timeout():
            if self.loop.is_running():
                self.loop.quit()
            return False  # Destroy timeout source

        GLib.timeout_add_seconds(timeout_sec, on_timeout)
        self.loop.run()

    def register_agent(self, pin):
        """Registers the custom PIN agent with BlueZ AgentManager1."""
        self.agent = AutoAgent(self.bus, AGENT_PATH, self.logger, pin)
        capability = "KeyboardOnly" if pin else "NoInputNoOutput"

        agent_manager = dbus.Interface(
            self.bus.get_object(BUS_NAME, "/org/bluez"), "org.bluez.AgentManager1"
        )
        agent_manager.RegisterAgent(dbus.ObjectPath(AGENT_PATH), dbus.String(capability))
        agent_manager.RequestDefaultAgent(AGENT_PATH)
        self.logger.info(f"[Manager] Agent registered with capability {capability} at {AGENT_PATH}")

    def is_device_paired(self, mac_address):
        """Checks if a given MAC address is already in the paired devices list."""
        managed_objects = self.object_manager.GetManagedObjects()
        for path, interfaces in managed_objects.items():
            if "org.bluez.Device1" in interfaces:
                props = interfaces["org.bluez.Device1"]
                if (
                    props.get("Address", "").upper() == mac_address.upper()
                    and props.get("Paired", False)
                ):
                    return True
        return False

    def find_device_path(self, mac_address):
        """Finds DBus object path for a MAC address if already discovered."""
        managed_objects = self.object_manager.GetManagedObjects()
        for path, interfaces in managed_objects.items():
            if "org.bluez.Device1" in interfaces:
                props = interfaces["org.bluez.Device1"]
                if props.get("Address", "").upper() == mac_address.upper():
                    return path
        return None

    def discover_device_path(self, mac_address, timeout=10):
        """Scans for devices up to `timeout` seconds and returns the DBus object path."""
        found_path = [self.find_device_path(mac_address)]
        if found_path[0]:
            return found_path[0]

        def interfaces_added_cb(object_path, interfaces):
            if "org.bluez.Device1" in interfaces:
                props = interfaces["org.bluez.Device1"]
                if props.get("Address", "").upper() == mac_address.upper():
                    found_path[0] = object_path
                    self.loop.quit()

        receiver_handle = self.bus.add_signal_receiver(
            interfaces_added_cb,
            dbus_interface="org.freedesktop.DBus.ObjectManager",
            signal_name="InterfacesAdded",
        )

        try:
            self.start_discovery()
            self._run_loop(timeout)
        finally:
            self.stop_discovery()
            receiver_handle.remove()

        return found_path[0]

    def trust_device(self, device_path):
        """Sets the Trusted property of a Bluetooth device to True."""
        try:
            device_props = dbus.Interface(
                self.bus.get_object(BUS_NAME, device_path),
                "org.freedesktop.DBus.Properties",
            )
            device_props.Set("org.bluez.Device1", "Trusted", dbus.Boolean(True))
            self.logger.info(f"[Manager] Device {device_path} set to Trusted.")
        except dbus.DBusException as e:
            self.logger.error(f"[Manager] Failed to trust device {device_path}: {e}")

    def remove_device(self, device_path):
        """Removes a device from the adapter's known list."""
        try:
            self.adapter_obj.RemoveDevice(device_path)
            self.logger.info(f"[Manager] Removed existing device state: {device_path}")
        except dbus.DBusException:
            pass

    def start_discovery(self):
        """Starts scanning for nearby Bluetooth devices."""
        self.logger.info("[Manager] Starting Discovery...")
        self.adapter_obj.StartDiscovery()

    def stop_discovery(self):
        """Stops scanning for devices."""
        self.logger.info("[Manager] Stopping Discovery...")
        try:
            self.adapter_obj.StopDiscovery()
        except dbus.DBusException:
            pass

    def disconnect_device(self, device_path, timeout=10):
        """Disconnects an active Bluetooth connection for the given device path."""
        self.logger.info(f"[Manager] Disconnecting {device_path}...")
        device_obj = dbus.Interface(
            self.bus.get_object(BUS_NAME, device_path), "org.bluez.Device1"
        )

        def disconnect_reply():
            self.logger.info(f"[Manager] Successfully disconnected from {device_path}")
            self.loop.quit()

        def disconnect_error(error):
            self.logger.error(f"[Manager] Disconnect failed: {error}")
            self.loop.quit()

        device_obj.Disconnect(
            reply_handler=disconnect_reply,
            error_handler=disconnect_error,
            timeout=timeout * 1000,
        )
        self._run_loop(timeout)


    def pair_device(self, device_path, timeout=60):
        """Synchronously pairs, trusts, and disconnects from a device."""
        result = {"success": False, "error": None}

        device_obj = dbus.Interface(
            self.bus.get_object(BUS_NAME, device_path), "org.bluez.Device1"
        )

        def pair_reply():
            result["success"] = True
            self.loop.quit()

        def pair_error(error):
            result["error"] = error
            self.loop.quit()

        device_obj.Pair(
            reply_handler=pair_reply, error_handler=pair_error, timeout=timeout * 1000
        )

        self._run_loop(timeout)

        if result["success"]:
            self.trust_device(device_path)
            self.disconnect_device(device_path)
            return PairingState.SUCCESS
        else:
            self.logger.error(f"Pairing failed for {device_path}: {result['error']}")
            if result['error'].get_dbus_name() == "org.bluez.Error.AuthenticationCanceled":
                return PairingState.WRONG_PIN
            elif result['error'].get_dbus_name() == "org.bluez.Error.org.bluez.Error.ConnectionAttemptFailed":
                return PairingState.TIMEOUT
            return PairingState.FAILED