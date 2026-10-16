"""Matter controller: runs the Matter server and creates the FHEM devices"""

import asyncio
import functools
import signal

from .. import fhem, utils
from ..core import child_process, pending_restore
from . import clusters, server
from .client import MatterClient, MatterServerError

COMMISSION_TIMEOUT = 600
RECONNECT_DELAY = 10

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
    "Needs: attribute bluetooth_adapter (e.g. 0), and for WiFi devices "
    "'set wifi_credentials' or for Thread devices 'set thread_dataset' "
    "first.<br>"
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
                "brand-new devices via Bluetooth. Leave empty if you pair "
                "devices with a code from another app.",
            },
            "primary_interface": {
                "default": "",
                "help": "Network interface (e.g. eth0, wlan0) the Matter server "
                "uses for IPv6 link-local addresses. Only needed if pairing "
                "fails and the computer has several network interfaces.",
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
        port, adapter, interface = settings
        self._log_offset = await utils.run_blocking(functools.partial(server.log_size))
        try:
            self.proc = server.start(
                self.node,
                self.node_env,
                port,
                bluetooth_adapter=int(adapter) if str(adapter).isdigit() else None,
                primary_interface=interface or None,
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

    def server_settings(self):
        return (
            self.fhemdev._attr_port,
            self.fhemdev._attr_bluetooth_adapter,
            self.fhemdev._attr_primary_interface,
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
        if self.nodes:
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
        code = code.strip()
        if not code.upper().startswith("MT:"):
            code = code.replace("-", "").replace(" ", "")
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
            await fhem.readingsSingleUpdate(
                self.hash, "pairing", f"failed: {pairing_error(exc)}", 1
            )
            return
        await fhem.readingsSingleUpdate(
            self.hash, "pairing", f"successful, node {node['node_id']}", 1
        )
        self.nodes[node["node_id"]] = node
        await self.update_nodes_reading()
        await self.create_devices_for_node(node)

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
        return (
            f"{text}. Check the code, put the device in pairing mode again "
            "and retry. IPv6 must be enabled in your network."
        )
    return text
