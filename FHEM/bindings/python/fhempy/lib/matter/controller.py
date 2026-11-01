"""Matter controller: runs the Matter server and creates the FHEM devices"""

import asyncio
import functools
import signal

from .. import fhem, utils
from ..core import child_process, fhemweb, pending_restore
from . import clusters, server, system_check
from .client import MatterClient, MatterServerError

COMMISSION_TIMEOUT = 600
# all paired Matter devices are put into this room
MATTER_ROOM = "Matter"
ROOM_ICON = "it_net"
CONTROLLER_ICON = "control_building_control"
RECONNECT_DELAY = 10
# restart of the Matter server after attr bluetooth_adapter was set
BLUETOOTH_RESTART_TIMEOUT = 180

PAIR_HELP = (
    "Pair a Matter device with FHEM.<br>"
    "Enter the pairing code, either the 11 digit number (e.g. 3497-011-2332) "
    "or the text of the QR code (starts with MT:).<br>"
    "<b>Device is already used in another app</b> (Apple Home, Google Home, "
    "Alexa, SmartThings, Hue, IKEA...): open the device in that app, choose "
    "'Turn on pairing mode', 'Share' or 'Connect to other apps' and use the "
    "code shown there. The device keeps working in the other app.<br>"
    "<b>New device</b>: use the code printed on the device or its box. "
    "The device must already be in your WiFi/Thread network, otherwise use "
    "pair_new_device.<br>"
    "Pairing can take up to a few minutes, see reading 'pairing'."
)

PAIR_NEW_HELP = (
    "Pair a brand-new Matter device which isn't in your network yet, via "
    "Bluetooth.<br>"
    "Uses the Bluetooth adapter of this computer (attribute "
    "bluetooth_adapter is set automatically). Needs for WiFi devices "
    "'set wifi_credentials' or for Thread devices 'set thread_dataset' "
    "first. The reading bluetooth_check shows if Bluetooth is ready.<br>"
    "Code: the text of the QR code (MT:...) or the 11 digit number, "
    "without quotes.<br>"
    "Easier alternative: add the device with the app of your phone "
    "(Apple Home, Google Home...) and then use 'set pair' with a code "
    "from 'Connect to other apps'."
)


class matter_controller:
    def __init__(self, logger, fhemdev):
        self.logger = logger
        self.fhemdev = fhemdev
        self.hash = None
        self.client = None
        self.nodes = {}
        self.devices = []
        self.proc = None
        self.node = None
        self.node_env = None
        self.external_url = None
        self._errors = utils.ErrorLogger(logger)
        # held while the server is updated, the run loop doesn't restart it
        self._maintenance = asyncio.Lock()
        self._started_with = None
        self._stopping = False
        self._log_offset = 0
        # reasons why Bluetooth pairing won't work, see system_check
        self._ble_problems = []

    async def Define(self, hash, args, argsh):
        self.hash = hash
        if len(args) > 3:
            if not args[3].startswith(("ws://", "wss://")):
                return (
                    "Usage: define matter fhempy matter [ws://IP:5580/ws]\n"
                    "Without the URL fhempy installs and starts its own Matter "
                    "server (recommended)."
                )
            self.external_url = args[3]
            hash["MATTER_SERVER"] = self.external_url

        set_config = {
            "pair": {"args": ["code"], "help": PAIR_HELP},
            "pair_new_device": {"args": ["code"], "help": PAIR_NEW_HELP},
            "wifi_credentials": {
                "args": ["ssid", "password"],
                "help": "WiFi name and password which are given to new WiFi "
                "devices during 'set pair_new_device'.<br>"
                "Example: set matter wifi_credentials MyWiFi MyPassword",
            },
            "thread_dataset": {
                "args": ["dataset"],
                "help": "Thread network (active operational dataset as hex "
                "string) for new Thread devices during 'set pair_new_device'. "
                "You find it in the settings of your Thread border router "
                "(e.g. Home Assistant, OpenThread Border Router).",
            },
            "discover": {
                "help": "Search for Matter devices in your network which are "
                "currently in pairing mode. Result in reading 'discovered'."
            },
            "create_devices": {
                "help": "Creates missing FHEM devices for all paired Matter "
                "devices. Normally this happens automatically."
            },
            "remove_node": {
                "args": ["node_id"],
                "help": "Removes a device from FHEM's Matter network (factory "
                "reset might be needed to pair it again). The node id is the "
                "internal MATTER_NODE of the FHEM device. Delete the FHEM "
                "device afterwards.",
            },
        }
        if self.external_url is None:
            set_config["restart"] = {"help": "Restart the Matter server."}
            set_config["update"] = {
                "help": "Install the newest Matter server version and restart. "
                "The tested version is installed automatically, use this only "
                "if a device doesn't work."
            }
        await self.fhemdev.set_set_config(set_config)

        attr_config = {
            "port": {
                "default": "5580",
                "format": "int",
                "help": "Port of the Matter server (only reachable from this "
                "computer). Change it only if 5580 is already used.",
            },
            "bluetooth_adapter": {
                "default": "",
                "help": "Number of the Bluetooth adapter (0 for hci0) to pair "
                "brand-new devices via Bluetooth. Set automatically to the "
                "first adapter on the first 'set pair_new_device'. fhempy checks "
                "Bluetooth when the Matter server starts, see reading "
                "bluetooth_check.",
            },
            "primary_interface": {
                "default": "",
                "help": "Network interface (e.g. eth0, wlan0) the Matter server "
                "uses for IPv6 link-local addresses. Only needed if pairing "
                "fails and the computer has several network interfaces.",
            },
            "test_dcl": {
                "default": "0",
                "options": "0,1",
                "format": "int",
                "help": "1: also pair devices with a test/development "
                "certificate (e.g. beta firmware). Only enable this if you "
                "trust the vendor.",
            },
            "autocreate": {
                "default": "1",
                "options": "0,1",
                "format": "int",
                "help": "1: create a FHEM device for each paired Matter device "
                "automatically (default). 0: only via 'set create_devices'.",
            },
        }
        await self.fhemdev.set_attr_config(attr_config)
        await fhem.readingsSingleUpdate(self.hash, "state", "starting", 1)
        await fhemweb.setup_room(self.hash, MATTER_ROOM, ROOM_ICON, CONTROLLER_ICON)
        self.fhemdev.create_async_task(self.run())

    async def Undefine(self, hash):
        # the run loop must not start the server again
        self._stopping = True
        if self.client is not None:
            await self.client.close()
        await self.stop_server()

    # --- server process ---

    async def run(self):
        if self.external_url is None:
            if not await self.install_server():
                return
            if not await self.start_server():
                return
        while True:
            await self.connect_and_listen()
            await asyncio.sleep(RECONNECT_DELAY)
            async with self._maintenance:
                if self.external_url is None and (
                    self.proc is None or self.proc.poll() is not None
                ):
                    self.logger.info("Matter server stopped, starting it again")
                    await self.start_server()

    async def install_server(self):
        await self.update_state("installing Node.js")
        try:
            self.node, version, self.node_env = await server.prepare_node(self.logger)
        except server.NodeNotFound as exc:
            found = (
                f"found Node.js {exc.args[0][0]}.{exc.args[0][1]}"
                if exc.args and exc.args[0]
                else "no Node.js found"
            )
            await fhem.readingsSingleUpdate(
                self.hash, "node_version", f"{found}, 22.13 or newer needed", 1
            )
            await self.update_state(
                "Node.js 22.13 or newer needed",
                "Install Node.js 22 or newer (https://nodejs.org or "
                "'curl -fsSL https://deb.nodesource.com/setup_22.x | sudo bash - "
                "&& sudo apt install nodejs') and restart fhempy.",
            )
            return False
        await fhem.readingsSingleUpdate(
            self.hash, "node_version", f"{version[0]}.{version[1]}", 1
        )

        installed = await utils.run_blocking(
            functools.partial(server.installed_version)
        )
        if server.needs_install(installed):
            if not await self.npm_install(server.MATTER_SERVER_VERSION):
                return False
        else:
            await fhem.readingsSingleUpdateIfChanged(
                self.hash, "server_version", installed, 1
            )
        return True

    async def npm_install(self, version):
        await self.update_state(
            "installing Matter server, this takes a few minutes",
            "Please wait until the installation is finished.",
        )
        try:
            await utils.run_blocking(
                functools.partial(server.install, self.node, self.node_env, version)
            )
        except Exception as exc:
            self.logger.error(f"Matter server installation failed: {exc}")
            await self.update_state(
                "installation failed, check fhempy log",
                "Check internet connection and free disk space, then 'set restart'.",
            )
            return False
        installed = await utils.run_blocking(
            functools.partial(server.installed_version)
        )
        await fhem.readingsSingleUpdate(self.hash, "server_version", installed, 1)
        return True

    async def start_server(self):
        if self._stopping:
            return False
        if self.node is None:
            return await self.install_server() and await self.start_server()
        await self.apply_restored_backup()
        settings = self.server_settings()
        port, _, interface, test_dcl = settings
        if test_dcl == 1:
            self.logger.warning(
                "Matter server accepts devices with test certificates "
                "(attr test_dcl 1), only use this if you trust the vendor"
            )
        self._log_offset = await utils.run_blocking(functools.partial(server.log_size))
        await self.check_bluetooth()
        try:
            self.proc = server.start(
                self.node,
                self.node_env,
                port,
                bluetooth_adapter=self.bluetooth_adapter(),
                primary_interface=interface or None,
                test_dcl=test_dcl == 1,
                logger=self.logger,
            )
            self._started_with = settings
        except Exception:
            self.logger.exception("Failed to start Matter server")
            await self.update_state("failed to start, check fhempy log")
            return False
        await self.update_state("starting Matter server")
        return True

    async def apply_restored_backup(self):
        # storage restored by github_restore replaces the current one before
        # the server starts, a running server would overwrite it
        try:
            applied = await utils.run_blocking(
                functools.partial(
                    pending_restore.apply_matter_restore, server.storage_directory()
                )
            )
        except Exception:
            self.logger.exception("Failed to apply restored Matter backup")
            await fhem.readingsSingleUpdate(
                self.hash, "restore", "failed to apply backup, check log", 1
            )
            return
        if applied:
            self.logger.info(f"Applied restored Matter backup ({len(applied)} files)")
            await fhem.readingsSingleUpdate(
                self.hash, "restore", f"backup applied ({len(applied)} files)", 1
            )

    def bluetooth_adapter(self):
        adapter = str(self.fhemdev._attr_bluetooth_adapter).strip()
        return int(adapter) if adapter.isdigit() else None

    async def check_bluetooth(self):
        """Looks for the usual reasons why pairing via Bluetooth fails
        (rfkill, missing adapter, no rights for Node.js), result in reading
        bluetooth_check and next_step"""
        adapter = self.bluetooth_adapter()
        if adapter is None or self.external_url is not None:
            self._ble_problems = []
            await fhem.CommandDeleteReading(
                self.hash, self.hash["NAME"] + " bluetooth_check"
            )
            return []
        self._ble_problems = await utils.run_blocking(
            functools.partial(system_check.bluetooth_problems, adapter, self.node)
        )
        for problem in self._ble_problems:
            self.logger.warning(f"Bluetooth pairing won't work: {problem}")
        await fhem.readingsSingleUpdateIfChanged(
            self.hash,
            "bluetooth_check",
            " ".join(str(p) for p in self._ble_problems) or "ok",
            1,
        )
        return self._ble_problems

    def server_settings(self):
        return (
            self.fhemdev._attr_port,
            self.fhemdev._attr_bluetooth_adapter,
            self.fhemdev._attr_primary_interface,
            self.fhemdev._attr_test_dcl,
        )

    async def _settings_changed(self, hash):
        if (
            self.proc is not None
            and self._started_with is not None
            and self.server_settings() != self._started_with
        ):
            self.fhemdev.create_async_task(self.restart_server())

    set_attr_port = _settings_changed
    set_attr_bluetooth_adapter = _settings_changed
    set_attr_primary_interface = _settings_changed
    set_attr_test_dcl = _settings_changed

    async def stop_server(self):
        if self.proc is None:
            return True
        proc = self.proc
        self.proc = None
        return await child_process.stop(proc, signal.SIGTERM, timeout=15)

    @property
    def url(self):
        if self.external_url is not None:
            return self.external_url
        return f"ws://127.0.0.1:{self.fhemdev._attr_port}/ws"

    # --- connection ---

    async def connect_and_listen(self):
        client = MatterClient(self.url, self.logger, self.handle_event)
        connected = False
        last_error = None
        # the server needs a few seconds after start
        for _ in range(12):
            try:
                await client.connect()
                connected = True
                break
            except (OSError, asyncio.TimeoutError, ValueError) as exc:
                last_error = exc
                await asyncio.sleep(5)
        if not connected:
            self._errors.failed(
                f"Can't connect to Matter server {self.url}", exc=last_error
            )
            error = None
            if self.external_url is None:
                error = await utils.run_blocking(
                    functools.partial(server.startup_error, self._log_offset)
                )
            await self.update_state(
                "Matter server not reachable",
                error
                or "Check the fhempy log and .fhempy/matter_server/matter_server.log",
            )
            return
        self._errors.success()
        self.client = client
        listen_task = asyncio.create_task(client.listen())
        try:
            nodes = await client.send_command("start_listening", timeout=120)
            await self.set_fabric_label(client)
            await self.handle_server_info(client.server_info)
            self.nodes = {node["node_id"]: node for node in nodes}
            await self.update_nodes_reading()
            for device in list(self.devices):
                await device.node_updated()
            if self.fhemdev._attr_autocreate == 1:
                await self.create_devices()
            await listen_task
        except Exception:
            self.logger.exception("Matter server connection failed")
        finally:
            listen_task.cancel()
            await client.close()
            self.client = None
            for device in list(self.devices):
                await device.server_disconnected()
            await self.update_state("disconnected, reconnecting")

    async def set_fabric_label(self, client):
        # name of this controller in other apps (Apple Home, Google Home...),
        # the server's default is "HomeAssistant". The server also renames it
        # on the devices which are already paired. An external server (e.g.
        # Home Assistant) keeps its name.
        if self.external_url is not None:
            return
        try:
            current = await client.send_command("get_fabric_label")
            if (current or {}).get("fabric_label") != server.FABRIC_LABEL:
                await client.send_command(
                    "set_default_fabric_label", label=server.FABRIC_LABEL
                )
        except (MatterServerError, asyncio.TimeoutError) as exc:
            self.logger.warning(f"Can't set the name shown in other apps: {exc}")

    async def handle_server_info(self, info):
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "fabric_id", info.get("fabric_id", "")
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "server_sdk", info.get("sdk_version", "")
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash,
            "bluetooth",
            "enabled" if info.get("bluetooth_enabled") else "disabled",
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash,
            "wifi_credentials",
            "set" if info.get("wifi_credentials_set") else "not set",
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash,
            "thread_dataset",
            "set" if info.get("thread_credentials_set") else "not set",
        )
        await fhem.readingsEndUpdate(self.hash, 1)

    async def update_nodes_reading(self):
        await fhem.readingsSingleUpdateIfChanged(self.hash, "nodes", len(self.nodes), 1)
        if self._ble_problems:
            await self.update_state(
                "connected, Bluetooth pairing not possible",
                "Bluetooth pairing (pair_new_device) won't work: "
                + " ".join(str(p) for p in self._ble_problems)
                + f" Then 'set {self.hash['NAME']} restart'.",
            )
        elif self.nodes:
            await self.update_state(
                "connected",
                f"Ready. Pair more devices with 'set {self.hash['NAME']} pair "
                "<code>'. Click 'Device specific help' for details.",
            )
        else:
            await self.update_state(
                "connected, no devices paired yet",
                f"Pair your first device: 'set {self.hash['NAME']} pair <code>'. "
                "Click 'Device specific help' to learn where to get the code.",
            )

    async def update_state(self, state, next_step=None):
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdateIfChanged(self.hash, "state", state)
        if next_step is not None:
            await fhem.readingsBulkUpdateIfChanged(self.hash, "next_step", next_step)
        await fhem.readingsEndUpdate(self.hash, 1)

    # --- events from the Matter server ---

    async def handle_event(self, event, data):
        # runs in the receive loop, don't wait for Matter commands here
        handler = {
            "attribute_updated": self._attribute_updated,
            "node_event": self._node_event,
            "node_added": self._node_updated,
            "node_updated": self._node_updated,
            "node_removed": self._node_removed,
        }.get(event)
        if handler is not None:
            await handler(data)

    async def _attribute_updated(self, data):
        node_id, path, value = data
        node = self.nodes.get(node_id)
        if node is not None:
            node["attributes"][path] = value
        for device in self.devices_of(node_id):
            await device.attribute_updated(path, value)

    async def _node_event(self, data):
        for device in self.devices_of(data.get("node_id")):
            await device.node_event(data)

    async def _node_updated(self, node):
        is_new = node["node_id"] not in self.nodes
        self.nodes[node["node_id"]] = node
        for device in self.devices_of(node["node_id"]):
            await device.node_updated()
        if is_new:
            await self.update_nodes_reading()
            if self.fhemdev._attr_autocreate == 1:
                await self.create_devices_for_node(node)

    async def _node_removed(self, node_id):
        self.nodes.pop(node_id, None)
        for device in self.devices_of(node_id):
            await device.node_removed()
        await self.update_nodes_reading()

    def devices_of(self, node_id):
        return [device for device in self.devices if device.node_id == node_id]

    def register_device(self, device):
        if device not in self.devices:
            self.devices.append(device)

    def unregister_device(self, device):
        if device in self.devices:
            self.devices.remove(device)

    # --- FHEM devices ---

    async def create_devices(self):
        for node in list(self.nodes.values()):
            await self.create_devices_for_node(node)

    async def create_devices_for_node(self, node):
        node_id = node["node_id"]
        attributes = node.get("attributes", {})
        await self.create_device(node_id, None, attributes)
        for endpoint in clusters.bridged_endpoints(attributes):
            await self.create_device(node_id, endpoint, attributes)

    async def create_device(self, node_id, endpoint, attributes):
        matter_id = str(node_id) if endpoint is None else f"{node_id}-{endpoint}"
        if await fhem.checkIfDeviceExists(
            self.hash, "FHEMPYTYPE", "matter", "MATTER_ID", matter_id
        ):
            return
        name = utils.gen_fhemdev_name(f"matter_{matter_id}")
        definition = f"{name} fhempy matter {self.hash['NAME']} {node_id}"
        if endpoint is not None:
            definition += f" {endpoint}"
        self.logger.info(f"create: {definition}")
        await fhem.CommandDefine(self.hash, definition)
        alias = device_label(attributes, endpoint)
        if alias:
            await fhem.CommandAttr(self.hash, f"{name} alias {alias}")
        webcmd = default_webcmd(attributes, endpoint)
        if webcmd:
            await fhem.CommandAttr(self.hash, f"{name} webCmd {webcmd}")
        # overview of all Matter devices, can be changed like any room
        await fhem.CommandAttr(self.hash, f"{name} room {MATTER_ROOM}")
        icon = clusters.default_icon(
            attributes, clusters.device_endpoints(attributes, endpoint)
        )
        if icon:
            await fhem.CommandAttr(self.hash, f"{name} icon {icon}")

    # --- set commands ---

    async def run_command(self, command, timeout=60, **args):
        if self.client is None or not self.client.connected:
            raise ConnectionError(
                "Matter server is not connected, see state of " + self.hash["NAME"]
            )
        return await self.client.send_command(command, timeout=timeout, **args)

    async def set_pair(self, hash, params):
        self.fhemdev.create_async_task(self.commission(params["code"], True))

    async def set_pair_new_device(self, hash, params):
        self.fhemdev.create_async_task(self.commission(params["code"], False))

    async def commission(self, code, network_only):
        code = normalize_code(code)
        if not network_only:
            if not await self.enable_bluetooth():
                return
            # rfkill or a Node.js update might have changed since the start
            await self.check_bluetooth()
        await fhem.readingsSingleUpdate(
            self.hash, "pairing", "running, this can take a few minutes", 1
        )
        try:
            node = await self.run_command(
                "commission_with_code",
                timeout=COMMISSION_TIMEOUT,
                code=code,
                network_only=network_only,
            )
        except Exception as exc:
            self.logger.warning(f"Pairing failed: {exc}")
            hints = await self.pairing_hints(network_only)
            text = f"failed: {pairing_error(exc)}"
            if hints:
                text += " Possible cause: " + " ".join(str(h) for h in hints)
            await fhem.readingsSingleUpdate(self.hash, "pairing", text, 1)
            return
        await fhem.readingsSingleUpdate(
            self.hash, "pairing", f"successful, node {node['node_id']}", 1
        )
        self.nodes[node["node_id"]] = node
        await self.update_nodes_reading()
        await self.create_devices_for_node(node)

    async def enable_bluetooth(self):
        """Sets attr bluetooth_adapter to the adapter of this computer if it
        isn't set yet and waits until the Matter server runs with it.
        Bluetooth stays off until it is needed: the server takes over the
        adapter and needs extra rights for it."""
        if self.external_url is not None or self.bluetooth_adapter() is not None:
            return True
        adapters = await utils.run_blocking(
            functools.partial(system_check.bluetooth_adapters)
        )
        if not adapters:
            await fhem.readingsSingleUpdate(
                self.hash,
                "pairing",
                "failed: no Bluetooth adapter found on this computer, "
                "pair_new_device needs one. Alternative: add the device with "
                "the app of your phone and use 'set pair' with a code from "
                "'Connect to other apps'.",
                1,
            )
            return False
        adapter = adapters[0]
        self.logger.info(f"Using Bluetooth adapter hci{adapter} for pairing")
        await fhem.readingsSingleUpdate(
            self.hash,
            "pairing",
            f"enabling Bluetooth adapter hci{adapter}, restarting Matter server",
            1,
        )
        problems = await utils.run_blocking(
            functools.partial(system_check.bluetooth_problems, adapter, self.node)
        )
        await fhem.CommandAttr(
            self.hash, f"{self.hash['NAME']} bluetooth_adapter {adapter}"
        )
        if problems:
            # the attribute stays set, after the fix only a restart is needed
            await fhem.readingsSingleUpdate(
                self.hash,
                "pairing",
                "failed: Bluetooth isn't ready. "
                + " ".join(str(p) for p in problems)
                + f" Then 'set {self.hash['NAME']} restart' and pair again.",
                1,
            )
            return False
        if await self.wait_for_server(BLUETOOTH_RESTART_TIMEOUT):
            return True
        await fhem.readingsSingleUpdate(
            self.hash,
            "pairing",
            "failed: Matter server didn't start with Bluetooth, see state and "
            "reading bluetooth_check",
            1,
        )
        return False

    async def wait_for_server(self, timeout):
        """Waits until the server runs with the current attributes and is
        connected"""
        loop = asyncio.get_running_loop()
        end = loop.time() + timeout
        while loop.time() < end:
            if (
                self._started_with == self.server_settings()
                and self.client is not None
                and self.client.connected
            ):
                return True
            await asyncio.sleep(1)
        return False

    async def pairing_hints(self, network_only):
        """Problems of this computer which explain a failed pairing"""
        if self.external_url is not None:
            # the server runs elsewhere, this computer's settings don't matter
            return []
        hints = [] if network_only else list(self._ble_problems)
        try:
            hints += await utils.run_blocking(
                functools.partial(
                    system_check.thread_route_problems,
                    self.fhemdev._attr_primary_interface or None,
                )
            )
        except Exception:
            self.logger.exception("Failed to check the Thread route")
        return hints

    async def set_wifi_credentials(self, hash, params):
        await self.run_command(
            "set_wifi_credentials",
            ssid=params["ssid"],
            credentials=params["password"],
        )
        await fhem.readingsSingleUpdate(self.hash, "wifi_credentials", "set", 1)

    async def set_thread_dataset(self, hash, params):
        await self.run_command("set_thread_dataset", dataset=params["dataset"])
        await fhem.readingsSingleUpdate(self.hash, "thread_dataset", "set", 1)

    async def set_discover(self, hash, params):
        self.fhemdev.create_async_task(self.discover())

    async def discover(self):
        await fhem.readingsSingleUpdate(self.hash, "discovered", "searching...", 1)
        try:
            found = await self.run_command("discover", timeout=120)
        except Exception as exc:
            await fhem.readingsSingleUpdate(
                self.hash, "discovered", f"failed: {exc}", 1
            )
            return
        if not found:
            text = "no device in pairing mode found"
        else:
            text = ", ".join(describe_commissionable(entry) for entry in found)
        await fhem.readingsSingleUpdate(self.hash, "discovered", text, 1)

    async def set_create_devices(self, hash, params):
        self.fhemdev.create_async_task(self.create_devices())

    async def set_remove_node(self, hash, params):
        node_id = int(params["node_id"])
        await self.run_command("remove_node", timeout=120, node_id=node_id)
        self.nodes.pop(node_id, None)
        await self.update_nodes_reading()

    async def set_restart(self, hash, params):
        self.fhemdev.create_async_task(self.restart_server())

    async def restart_server(self):
        await self.update_state("restarting")
        # the run loop starts the server again
        await self.stop_server()
        if self.client is not None:
            await self.client.close()

    async def set_update(self, hash, params):
        self.fhemdev.create_async_task(self.update_server())

    async def update_server(self):
        if self.node is None:
            await self.update_state("Node.js missing, can't update")
            return
        async with self._maintenance:
            await self.stop_server()
            if self.client is not None:
                await self.client.close()
            await self.npm_install("latest")


def device_label(attributes, endpoint):
    if endpoint is None:
        info = clusters.BASIC_INFORMATION
        ep = 0
    else:
        info = clusters.BRIDGED_DEVICE_BASIC_INFORMATION
        ep = endpoint
    for attribute in (5, 3):
        value = attributes.get(f"{ep}/{info}/{attribute}")
        if value:
            return str(value)
    return None


def default_webcmd(attributes, endpoint):
    model = clusters.DeviceModel(
        attributes, clusters.device_endpoints(attributes, endpoint)
    )
    if "on" in model.sets and "pct" in model.sets:
        return "on:off:pct"
    if "on" in model.sets:
        return "on:off"
    if "open" in model.sets:
        return "open:stop:close:position"
    if "lock" in model.sets:
        return "lock:unlock"
    if "desired-temp" in model.sets:
        return "desired-temp"
    return None


def normalize_code(code):
    """Pairing code as the Matter server expects it: QR code text (MT:...)
    or the 11/21 digit number without dashes, spaces and quotes"""
    code = code.strip().strip("\"'“”„").strip()
    if code.upper().startswith("MT:"):
        return "MT:" + code[3:]
    return code.replace("-", "").replace(" ", "").replace(".", "")


def describe_commissionable(entry):
    name = entry.get("device_name") or entry.get("instance_name") or "device"
    addresses = entry.get("addresses") or []
    if addresses:
        return f"{name} ({addresses[0]})"
    return name


def pairing_error(exc):
    text = str(exc) or exc.__class__.__name__
    if isinstance(exc, asyncio.TimeoutError):
        return (
            "timeout. Is the device in pairing mode and in the same network? "
            "Codes from other apps are only valid for a few minutes."
        )
    if isinstance(exc, MatterServerError):
        if "test/development certificate" in text:
            return (
                "the device uses a test/development certificate (e.g. beta "
                "firmware). If you trust the vendor, set attr test_dcl 1 "
                "and pair again."
            )
        return (
            f"{text}. Check the code, put the device in pairing mode again "
            "and retry. IPv6 must be enabled in your network."
        )
    return text
