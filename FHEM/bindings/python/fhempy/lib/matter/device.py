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
