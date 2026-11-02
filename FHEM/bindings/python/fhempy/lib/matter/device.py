"""One Matter device (node or bridged device) in FHEM"""

import asyncio
import json

from .. import fhem
from .. import fhem_pythonbinding as fhempy
from . import clusters

SWITCH = 59
SWITCH_EVENTS = {
    1: "pressed",
    2: "long",
    3: "short",
    4: "long_release",
}

# OTA Software Update Requestor cluster on endpoint 0 of a node
OTA_REQUESTOR = 42
UPDATE_STATE = 2
UPDATE_PROGRESS = 3
UPDATE_STATES = {
    2: "checking",
    3: "waiting for the update server",
    4: "downloading",
    5: "installing",
    6: "waiting to install",
    7: "rolling back",
    8: "waiting for confirmation on the device",
}
# software version (number) in the Basic Information cluster
SOFTWARE_VERSION_PATH = f"0/{clusters.BASIC_INFORMATION}/9"
FIRMWARE_CHECK_INTERVAL = 24 * 3600
FIRMWARE_CHECK_DELAY = 300

CHECK_FIRMWARE_HELP = (
    "Asks the Matter server whether the manufacturer published a newer "
    "firmware (Matter DCL), result in reading firmware_update. fhempy also "
    "checks once a day."
)
UPDATE_FIRMWARE_HELP = (
    "Installs the newer firmware shown in reading firmware_update. The "
    "device downloads it over the network, this can take a long time "
    "(Thread devices up to an hour), progress in reading firmware_update. "
    "Don't unplug the device meanwhile."
)

SHARE_HELP = (
    "Shows a pairing code (reading share_code) for 3 minutes to add this "
    "device to another app as well, e.g. Apple Home, Google Home or Alexa. "
    "The device stays in FHEM."
)


class matter_device:
    def __init__(self, logger, fhemdev):
        self.logger = logger
        self.fhemdev = fhemdev
        self.hash = None
        self.controller = None
        self.controller_name = None
        self.node_id = None
        self.endpoint = None
        self.model = None
        self.values = {}
        self.available_firmware = None
        self._updating = False
        self._firmware_task = None

    async def Define(self, hash, args, argsh):
        self.hash = hash
        if len(args) < 5 or not args[4].isdigit():
            return (
                "Usage: define <name> fhempy matter <controller> <node_id> "
                "[<endpoint>]\nMatter devices are created automatically by "
                "the Matter controller (define matter fhempy matter)."
            )
        self.controller_name = args[3]
        self.node_id = int(args[4])
        if len(args) > 5:
            self.endpoint = int(args[5])
            hash["MATTER_ID"] = f"{self.node_id}-{self.endpoint}"
            hash["MATTER_ENDPOINT"] = str(self.endpoint)
        else:
            hash["MATTER_ID"] = str(self.node_id)
        hash["MATTER_NODE"] = str(self.node_id)
        hash["MATTER_CONTROLLER"] = self.controller_name

        await self.fhemdev.set_attr_config(
            {
                "rawReadings": {
                    "default": "0",
                    "options": "0,1",
                    "format": "int",
                    "help": "1: show all Matter attributes as readings "
                    "(raw_<endpoint>_<cluster>_<attribute>). Useful to find "
                    "values of devices which aren't fully supported yet.",
                },
            }
        )
        await self.update_set_config()
        await fhem.readingsSingleUpdate(
            self.hash, "state", "waiting for Matter controller", 1
        )
        self.fhemdev.create_async_task(self.connect_controller())

    async def Undefine(self, hash):
        if self._firmware_task is not None:
            self._firmware_task.cancel()
            self._firmware_task = None
        if self.controller is not None:
            self.controller.unregister_device(self)

    async def connect_controller(self):
        while self.controller is None:
            dev = fhempy.getFhemPyDeviceByName(self.controller_name)
            controller = getattr(dev, "impl", None)
            if controller is not None and hasattr(controller, "register_device"):
                self.controller = controller
                controller.register_device(self)
                await self.node_updated()
                if self._firmware_task is None:
                    self._firmware_task = self.fhemdev.create_async_task(
                        self.check_firmware_regularly()
                    )
                return
            await asyncio.sleep(2)

    @property
    def node(self):
        if self.controller is None:
            return None
        return self.controller.nodes.get(self.node_id)

    # --- updates from the controller ---

    async def node_updated(self):
        node = self.node
        if node is None:
            if self.controller is not None and self.controller.client is not None:
                await fhem.readingsSingleUpdate(
                    self.hash, "state", "unknown node, not paired anymore?", 1
                )
            return
        attributes = node.get("attributes", {})
        self.model = clusters.DeviceModel(
            attributes, clusters.device_endpoints(attributes, self.endpoint)
        )
        await self.update_set_config()
        await fhem.readingsBeginUpdate(self.hash)
        for path, value in attributes.items():
            await self._bulk_attribute(path, value)
        await fhem.readingsBulkUpdateIfChanged(self.hash, "state", self.state())
        await fhem.readingsEndUpdate(self.hash, 1)

    async def attribute_updated(self, path, value):
        if self.model is None:
            return
        endpoint = clusters.parse_path(path)[0]
        if endpoint not in self.model.endpoints:
            return
        await fhem.readingsBeginUpdate(self.hash)
        changed = await self._bulk_attribute(path, value)
        if changed:
            await fhem.readingsBulkUpdateIfChanged(self.hash, "state", self.state())
        await fhem.readingsEndUpdate(self.hash, 1)

    async def _bulk_attribute(self, path, value):
        endpoint, cluster, attribute = clusters.parse_path(path)
        if endpoint not in self.model.endpoints:
            return False
        if (
            endpoint == 0
            and cluster == OTA_REQUESTOR
            and self.supports_firmware_update()
        ):
            await self._bulk_update_state()
        converted = self.model.convert(path, value)
        if converted is not None:
            name, reading_value = converted
            self.values[name] = reading_value
            await fhem.readingsBulkUpdateIfChanged(self.hash, name, reading_value)
            return True
        if self.fhemdev._attr_rawReadings == 1 and attribute < 0xFFF0:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, f"raw_{endpoint}_{cluster}_{attribute}", value
            )
        return False

    async def node_event(self, data):
        if self.model is None:
            return
        endpoint = data.get("endpoint_id")
        if endpoint not in self.model.endpoints or data.get("cluster_id") != SWITCH:
            return
        event_id = data.get("event_id")
        if event_id == 6:
            presses = (data.get("data") or {}).get("totalNumberOfPressesCounted", 1)
            value = {1: "short", 2: "double", 3: "triple"}.get(presses, f"{presses}x")
        elif event_id in SWITCH_EVENTS:
            value = SWITCH_EVENTS[event_id]
        else:
            return
        switch_endpoints = [
            ep
            for ep in self.model.endpoints
            if f"{ep}/{SWITCH}/0" in self.node.get("attributes", {})
        ]
        name = "button"
        if switch_endpoints and endpoint != switch_endpoints[0]:
            name = f"button_{endpoint}"
        await fhem.readingsSingleUpdate(self.hash, name, value, 1)

    async def set_attr_rawReadings(self, hash):
        self.fhemdev.create_async_task(self.node_updated())

    async def node_removed(self):
        await fhem.readingsSingleUpdate(
            self.hash, "state", "removed from Matter, delete this device", 1
        )

    async def server_disconnected(self):
        await fhem.readingsSingleUpdate(
            self.hash, "state", "Matter server disconnected", 1
        )

    def state(self):
        node = self.node
        if node is not None and not node.get("available", True):
            return "offline"
        if self.values.get("reachable") == "offline":
            return "offline"
        return self.model.state(self.values)

    # --- firmware update (OTA) ---

    def supports_firmware_update(self):
        """Only the FHEM device of the node itself (not bridged devices) and
        only if the node can be updated over Matter"""
        node = self.node
        if self.endpoint is not None or node is None:
            return False
        return f"0/{OTA_REQUESTOR}/{UPDATE_STATE}" in node.get("attributes", {})

    def _node_attribute(self, path):
        node = self.node
        if node is None:
            return None
        return node.get("attributes", {}).get(path)

    def update_state_text(self):
        """None if no update is running"""
        state = self._node_attribute(f"0/{OTA_REQUESTOR}/{UPDATE_STATE}")
        if state not in UPDATE_STATES:
            return None
        text = UPDATE_STATES[state]
        progress = self._node_attribute(f"0/{OTA_REQUESTOR}/{UPDATE_PROGRESS}")
        if isinstance(progress, int) and state in (4, 5):
            text += f" {progress}%"
        return text

    def available_text(self):
        update = self.available_firmware
        if update is None:
            return "up to date"
        version = update.get("software_version_string") or str(
            update.get("software_version")
        )
        return f"{version} available"

    async def _bulk_update_state(self):
        text = self.update_state_text()
        if text is not None:
            self._updating = True
            await fhem.readingsBulkUpdateIfChanged(self.hash, "firmware_update", text)
            return
        if self._updating:
            # back to idle: the update finished (or failed), check again
            self._updating = False
            self.fhemdev.create_async_task(self.check_firmware())

    def _newer(self, update):
        if not update or update.get("software_version") is None:
            return None
        current = self._node_attribute(SOFTWARE_VERSION_PATH)
        if isinstance(current, int) and update["software_version"] <= current:
            # the server caches the answer of the last check
            return None
        return update

    async def check_firmware(self):
        """Asks the Matter server for a newer firmware, returns an error
        text or None"""
        if not self.supports_firmware_update():
            return "This device can't be updated via Matter"
        try:
            result = await self._require_controller().run_command(
                "check_node_update", node_id=self.node_id, timeout=120
            )
        except Exception as exc:
            self.logger.warning(f"Firmware check failed: {exc}")
            await fhem.readingsSingleUpdate(
                self.hash, "firmware_update", f"check failed: {exc}", 1
            )
            return str(exc)
        self.available_firmware = self._newer(result)
        if self.update_state_text() is None:
            await fhem.readingsSingleUpdateIfChanged(
                self.hash, "firmware_update", self.available_text(), 1
            )
        return None

    async def check_firmware_regularly(self):
        await asyncio.sleep(FIRMWARE_CHECK_DELAY)
        while True:
            controller = self.controller
            if (
                self.supports_firmware_update()
                and controller is not None
                and controller.client is not None
                and controller.client.connected
            ):
                await self.check_firmware()
            await asyncio.sleep(FIRMWARE_CHECK_INTERVAL)

    async def set_check_firmware_update(self, hash, params):
        self.fhemdev.create_async_task(self.check_firmware())

    async def set_update_firmware(self, hash, params):
        if not self.supports_firmware_update():
            return "This device can't be updated via Matter"
        self.fhemdev.create_async_task(self.update_firmware())

    async def update_firmware(self):
        if self.available_firmware is None:
            if await self.check_firmware() is not None:
                return
            if self.available_firmware is None:
                return
        version = self.available_firmware["software_version"]
        self.logger.info(f"Starting firmware update to {self.available_text()}")
        await fhem.readingsSingleUpdate(
            self.hash, "firmware_update", "update requested", 1
        )
        try:
            await self._require_controller().run_command(
                "update_node",
                node_id=self.node_id,
                software_version=version,
                timeout=300,
            )
        except Exception as exc:
            self.logger.warning(f"Firmware update failed: {exc}")
            await fhem.readingsSingleUpdate(
                self.hash, "firmware_update", f"update failed: {exc}", 1
            )
            return
        # the device reports progress via the OTA requestor cluster
        self._updating = True

    # --- set commands ---

    async def update_set_config(self):
        set_config = {}
        if self.model is not None:
            for name, definition in self.model.sets.items():
                entry = {"help": definition["help"]}
                if "options" in definition:
                    entry["options"] = definition["options"]
                    entry["args"] = ["value"]
                entry["function"] = "set_matter"
                set_config[name] = entry
        set_config["share"] = {"help": SHARE_HELP, "function": "set_matter_share"}
        set_config["refresh"] = {
            "help": "Reads all information of the device again "
            "(e.g. after a firmware update).",
            "function": "set_matter_refresh",
        }
        if self.supports_firmware_update():
            set_config["check_firmware_update"] = {
                "help": CHECK_FIRMWARE_HELP,
                "function": "set_check_firmware_update",
            }
            set_config["update_firmware"] = {
                "help": UPDATE_FIRMWARE_HELP,
                "function": "set_update_firmware",
            }
        set_config["command"] = {
            "args": ["endpoint", "cluster", "command", "payload"],
            "params": {"payload": {"default": "{}"}},
            "help": "For experts: send any Matter command, e.g. "
            "'set &lt;name&gt; command 1 6 Toggle'. payload is JSON, "
            'e.g. {"identifyTime":5}.',
            "function": "set_matter_command",
        }
        set_config["write_attribute"] = {
            "args": ["path", "value"],
            "help": "For experts: write a Matter attribute, path is "
            "endpoint/cluster/attribute, value is JSON, "
            "e.g. 'set &lt;name&gt; write_attribute 1/513/18 2100'.",
            "function": "set_matter_write",
        }
        if set_config != self.fhemdev._conf_set:
            await self.fhemdev.set_set_config(set_config)

    def _require_controller(self):
        if self.controller is None:
            raise ConnectionError("Matter controller not found")
        return self.controller

    async def set_matter(self, hash, params):
        if self.model is None:
            return "Device not ready yet, see state"
        args = self.model.command_args(params["cmd"], params.get("value"))
        self.fhemdev.create_async_task(self._run(args))

    async def _run(self, args):
        controller = self._require_controller()
        try:
            if args["kind"] == "write":
                await controller.run_command(
                    "write_attribute",
                    node_id=self.node_id,
                    attribute_path=args["attribute_path"],
                    value=args["value"],
                )
            else:
                await controller.run_command(
                    "device_command",
                    node_id=self.node_id,
                    endpoint_id=args["endpoint_id"],
                    cluster_id=args["cluster_id"],
                    command_name=args["command_name"],
                    payload=args["payload"],
                    response_type=None,
                    timed_request_timeout_ms=10000 if args["timed"] else None,
                )
            await fhem.readingsSingleUpdateIfChanged(self.hash, "lastError", "none", 1)
        except Exception as exc:
            self.logger.warning(f"Matter command failed: {exc}")
            await fhem.readingsSingleUpdate(self.hash, "lastError", str(exc), 1)

    async def set_matter_command(self, hash, params):
        try:
            payload = json.loads(params["payload"])
        except ValueError:
            return 'payload must be JSON, e.g. {} or {"identifyTime":5}'
        self.fhemdev.create_async_task(
            self._run(
                {
                    "kind": "command",
                    "endpoint_id": int(params["endpoint"]),
                    "cluster_id": int(params["cluster"]),
                    "command_name": params["command"],
                    "payload": payload,
                    "timed": False,
                }
            )
        )

    async def set_matter_write(self, hash, params):
        try:
            value = json.loads(params["value"])
        except ValueError:
            value = params["value"]
        self.fhemdev.create_async_task(
            self._run(
                {
                    "kind": "write",
                    "attribute_path": params["path"],
                    "value": value,
                }
            )
        )

    async def set_matter_share(self, hash, params):
        self.fhemdev.create_async_task(self.share())

    async def share(self):
        try:
            result = await self._require_controller().run_command(
                "open_commissioning_window", node_id=self.node_id, timeout=180
            )
        except Exception as exc:
            await fhem.readingsSingleUpdate(
                self.hash, "share_code", f"failed: {exc}", 1
            )
            return
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdate(
            self.hash, "share_code", result.get("setup_manual_code", "")
        )
        await fhem.readingsBulkUpdate(
            self.hash, "share_qr", result.get("setup_qr_code", "")
        )
        await fhem.readingsEndUpdate(self.hash, 1)

    async def set_matter_refresh(self, hash, params):
        self.fhemdev.create_async_task(
            self._require_controller().run_command(
                "interview_node", node_id=self.node_id, timeout=300
            )
        )
