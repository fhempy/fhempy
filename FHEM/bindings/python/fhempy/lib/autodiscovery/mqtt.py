"""Home Assistant MQTT discovery for autodiscovery.

Listens on the MQTT brokers found (local port 1883, mDNS _mqtt._tcp, the
broker of a mqtt_ha_discovery device or attribute mqtt) for the discovery
messages of ESPHome, Zigbee2MQTT, Tasmota... Every new device is offered on
its own, a click on Create defines the MQTT2_DEVICE with readingList and
setList. Nothing is created without asking.
"""

import asyncio

import ifaddr

from .. import fhem, utils
from ..core import mqtt_ha
from . import details as details_module

MDNS_TYPE = "_mqtt._tcp.local."
LOCAL_HOST = "127.0.0.1"
LOCAL_PORT = 1883
LOCAL_INTERVAL = 600
RECONNECT_DELAY = 60
# devices republish their discovery messages when Home Assistant starts
BIRTH_TOPIC = "homeassistant/status"
LOGO = "mqtt_ha_discovery.png"
# Zigbee2MQTT publishes its devices (description, power source) retained here
BRIDGE_DEVICES_TOPIC = "+/bridge/devices"
# new devices offered within this time share one request for their states
STATES_DELAY = 5
# candidate status of a device not in FHEM (engine.STATUS_NEW)
STATUS_NEW = "new"


def local_addresses():
    addresses = {"127.0.0.1", "localhost"}
    try:
        for adapter in ifaddr.get_adapters():
            for ip in adapter.ips:
                if ip.is_IPv4:
                    addresses.add(ip.ip)
    except Exception:
        pass
    return addresses


def supported(component, payload_json):
    """mqtt_ha creates readings or sets for the entity"""
    return mqtt_ha.supported(component, payload_json)


def entity_list(device):
    return [(c, o, p) for (c, o), p in device["entities"].items()]


class MqttDiscovery:
    def __init__(self, engine):
        self.engine = engine
        self.logger = engine.logger
        self._errors = utils.ErrorLogger(engine.logger)
        # (host, port) -> task
        self._brokers = {}
        self._credentials = {}
        self._local_task = None
        # (host, port) -> connected aiomqtt client
        self._clients = {}
        # device_id -> name, fhem_name, entities, broker, created/exists
        self.devices = {}
        # state topic -> device_ids of offered devices (current values)
        self._topics = {}
        # ieee address -> Zigbee2MQTT description and power source
        self.bridge = {}
        self._states_task = None
        self._watch_tasks = set()
        self.mode = "auto"
        self.username = ""
        self.password = ""

    @property
    def brokers(self):
        return sorted(f"{host}:{port}" for host, port in self._brokers)

    # --- start/stop ---

    def configure(self, mode="auto", username="", password=""):
        """mode: auto (local broker, mDNS, mqtt_ha_discovery), off or
        host[:port] of the broker."""
        mode = (mode or "auto").strip()
        changed = (mode, username, password) != (
            self.mode,
            self.username,
            self.password,
        )
        self.mode, self.username, self.password = mode, username, password
        if changed or not self._brokers:
            self.stop()
            if self.engine.running:
                self.start()

    def start(self):
        if self.mode == "off":
            return
        if self.mode != "auto":
            host, _, port = self.mode.partition(":")
            self.add_broker(host, int(port) if port.isdigit() else LOCAL_PORT)
            return
        if self._local_task is None:
            self._local_task = asyncio.create_task(self._local_loop())

    def stop(self):
        if self._local_task is not None:
            self._local_task.cancel()
            self._local_task = None
        for task in self._brokers.values():
            task.cancel()
        self._brokers = {}
        self._clients = {}
        self._topics = {}
        if self._states_task is not None:
            self._states_task.cancel()
            self._states_task = None

    async def _local_loop(self):
        """A broker on this computer, e.g. Mosquitto or MQTT2_SERVER"""
        while True:
            if (LOCAL_HOST, LOCAL_PORT) not in self._brokers:
                try:
                    _, writer = await asyncio.wait_for(
                        asyncio.open_connection(LOCAL_HOST, LOCAL_PORT), 2
                    )
                    writer.close()
                    self.add_broker(LOCAL_HOST, LOCAL_PORT)
                except (OSError, asyncio.TimeoutError):
                    pass
            await asyncio.sleep(LOCAL_INTERVAL)

    def found_broker(self, host, port):
        """A broker announced via mDNS"""
        if self.mode != "auto" or not host:
            return
        port = int(port or LOCAL_PORT)
        if (
            port == LOCAL_PORT
            and (LOCAL_HOST, LOCAL_PORT) in self._brokers
            and host in local_addresses()
        ):
            return
        self.add_broker(host, port)

    def add_broker(self, host, port, username=None, password=None):
        """Also called by mqtt_ha_discovery for its broker"""
        if not self.engine.running or self.mode == "off":
            return
        if self.mode not in ("auto", f"{host}:{port}", host):
            return
        key = (host, int(port))
        if username:
            self._credentials[key] = (username, password)
        if key in self._brokers:
            return
        self._brokers[key] = asyncio.create_task(self._broker_loop(key))

    def credentials(self, key):
        if key in self._credentials:
            return self._credentials[key]
        return (self.username or None, self.password or None)

    async def _broker_loop(self, key):
        try:
            import aiomqtt
        except ImportError:
            self.logger.warning("MQTT discovery needs aiomqtt")
            return
        host, port = key
        while True:
            username, password = self.credentials(key)
            try:
                async with aiomqtt.Client(
                    host, port, username=username, password=password
                ) as client:
                    async with client.messages() as messages:
                        await client.subscribe(mqtt_ha.DISCOVERY_TOPIC)
                        await client.subscribe(BRIDGE_DEVICES_TOPIC)
                        # ESPHome, Zigbee2MQTT... send their discovery again
                        await client.publish(BIRTH_TOPIC, "online")
                        self._clients[key] = client
                        # after a reconnect: values of the offered devices
                        for topic in self._topics:
                            await client.subscribe(topic)
                        self._errors.success(f"{host}:{port}")
                        async for message in messages:
                            try:
                                await self.handle_message(
                                    key, message.topic.value, message.payload
                                )
                            except Exception:
                                self.logger.exception(
                                    f"Failed to handle MQTT discovery message on "
                                    f"{message.topic}"
                                )
            except aiomqtt.MqttError as exc:
                self._clients.pop(key, None)
                # MqttError isn't an OSError, log it without traceback
                self._errors.failed(
                    f"MQTT discovery: connection to {host}:{port} failed, retry "
                    f"every {RECONNECT_DELAY}s (attributes mqtt_username, "
                    "mqtt_password)",
                    key=f"{host}:{port}",
                    exc=ConnectionError(str(exc)),
                )
                await asyncio.sleep(RECONNECT_DELAY)

    # --- discovery messages ---

    async def handle_message(self, broker, topic, payload):
        if topic in self._topics:
            self.handle_state(topic, payload)
        if topic.endswith("/bridge/devices"):
            self.bridge.update(details_module.bridge_devices(payload))
            return
        if topic.startswith("homeassistant/"):
            await self._handle_discovery(broker, topic, payload)

    async def _handle_discovery(self, broker, topic, payload):
        try:
            entities = mqtt_ha.parse_discovery(topic, payload)
        except ValueError:
            self.logger.debug(f"Ignore invalid discovery payload on {topic}")
            return
        for component, node_id, object_id, payload_json in entities:
            if not supported(component, payload_json):
                continue
            device_name, device_id = mqtt_ha.device_info(
                node_id, object_id, payload_json
            )
            device = self.devices.get(device_id)
            if device is not None:
                device["entities"][(component, object_id)] = payload_json
                if self._watched(device_id):
                    await self.watch(device_id)
                if device.get("created"):
                    await mqtt_ha.set_device_attributes(
                        self.engine.hash, device["created"], entity_list(device)
                    )
                continue
            device = {
                "name": device_name,
                "fhem_name": mqtt_ha.fhem_device_name(device_name, device_id),
                "broker": broker,
                "entities": {(component, object_id): payload_json},
                "details": details_module.DeviceDetails(),
            }
            self.devices[device_id] = device
            try:
                await self._offer(device_id, device, payload_json)
            except Exception:
                # check again with the next message of the device
                del self.devices[device_id]
                raise

    async def _offer(self, device_id, device, payload_json):
        """Offered also if it exists in FHEM: shown again when deleted"""

        async def check():
            existing = await mqtt_ha.existing_device(
                self.engine.hash, device["fhem_name"], payload_json
            )
            if not existing:
                # deleted: no updates of its attributes anymore
                device.pop("created", None)
            return existing or ""

        async def create():
            return await self.create(device_id)

        async def recreate(name):
            return await self.recreate(device_id, name)

        def details():
            return self.details(device_id)

        await self.engine.report(
            "mqtt",
            device_id,
            device["name"],
            "MQTT device",
            create,
            check=check,
            recreate=recreate,
            details=details,
            model=mqtt_ha.device_model(payload_json),
            hint="Found via Home Assistant MQTT discovery (e.g. ESPHome, "
            "Zigbee2MQTT, Tasmota), creates a MQTT2_DEVICE",
            logo=LOGO,
        )
        candidate = self.engine.candidates.get(f"mqtt:{device_id}")
        if candidate is not None and candidate.get("status") == STATUS_NEW:
            await self.watch(device_id)

    # --- current values of offered devices ---

    def details(self, device_id):
        """What the device can do and its current values for the tile"""
        device = self.devices.get(device_id)
        if device is None:
            return {}
        candidate = self.engine.candidates.get(f"mqtt:{device_id}") or {}
        if candidate.get("status") == STATUS_NEW and not self._watched(device_id):
            # e.g. deleted in FHEM and offered again
            task = asyncio.create_task(self.watch(device_id))
            self._watch_tasks.add(task)
            task.add_done_callback(self._watch_tasks.discard)
        bridge = self.bridge.get(details_module.ieee_of(device_id), {})
        return device["details"].summary(entity_list(device), device_id, bridge)

    def _watched(self, device_id):
        return any(device_id in ids for ids in self._topics.values())

    async def watch(self, device_id):
        """Subscribes the state topics of the offered device, its current
        values are shown before it is created"""
        device = self.devices[device_id]
        new = False
        for topic in device["details"].state_topics(entity_list(device)):
            if topic not in self._topics:
                self._topics[topic] = set()
                new = True
                client = self._clients.get(tuple(device["broker"]))
                if client is not None:
                    try:
                        await client.subscribe(topic)
                    except Exception as exc:
                        self.logger.debug(f"Failed to subscribe {topic}: {exc}")
            self._topics[topic].add(device_id)
        if new and self._states_task is None:
            self._states_task = asyncio.create_task(
                self._request_states_later(device["broker"])
            )

    async def unwatch(self, device_id):
        """The device is in FHEM: no more values for the tile"""
        for topic, ids in list(self._topics.items()):
            ids.discard(device_id)
            if ids:
                continue
            del self._topics[topic]
            for client in self._clients.values():
                try:
                    await client.unsubscribe(topic)
                except Exception as exc:
                    self.logger.debug(f"Failed to unsubscribe {topic}: {exc}")

    async def _request_states_later(self, broker):
        """Zigbee2MQTT... send their states after the birth message, one
        request for all devices found in the meantime"""
        try:
            await asyncio.sleep(STATES_DELAY)
            await self.request_states(broker)
        finally:
            self._states_task = None

    def handle_state(self, topic, payload):
        changed = False
        for device_id in self._topics.get(topic, ()):
            device = self.devices.get(device_id)
            if device is not None and device["details"].message(topic, payload):
                changed = True
        return changed

    async def create(self, device_id):
        """Defines the MQTT2_DEVICE, returns an error text or ''."""
        device = self.devices.get(device_id)
        if device is None:
            return f"MQTT device {device_id} isn't known anymore"
        hash = self.engine.hash
        ret = await self.ensure_mqtt_client(hash, device["broker"])
        if ret:
            return str(ret)
        name = device["fhem_name"]
        ret = await fhem.CommandDefine(hash, f"{name} MQTT2_DEVICE")
        if ret:
            return str(ret)
        device["created"] = name
        await self.unwatch(device_id)
        candidate = self.engine.candidates.get(f"mqtt:{device_id}")
        if candidate is not None:
            candidate["device"] = name
        entities = entity_list(device)
        await mqtt_ha.set_device_attributes(hash, name, entities)
        await mqtt_ha.set_new_device_details(hash, name, device["name"], entities)
        await self.request_states(device["broker"])
        return ""

    async def recreate(self, device_id, name):
        """Sets up the existing MQTT2_DEVICE again like a new device, the
        FHEM name stays (DOIFs and notifies use it). Returns an error text or
        ''."""
        device = self.devices.get(device_id)
        if device is None:
            return f"MQTT device {device_id} isn't known anymore"
        hash = self.engine.hash
        ret = await self.ensure_mqtt_client(hash, device["broker"])
        if ret:
            return str(ret)
        # further entities of the device are added to it
        device["created"] = name
        entities = entity_list(device)
        await mqtt_ha.reset_device_attributes(hash, name, entities)
        # alias (friendly name), icon and model readings like for a new device
        await mqtt_ha.set_new_device_details(
            hash, name, device["name"], entities, replace=("alias", "icon")
        )
        await self.request_states(device["broker"])
        return ""

    async def request_states(self, broker):
        """Devices send their states (and discovery) again after Home
        Assistant's birth message: the new device gets its readings now and
        not only with the next change."""
        client = self._clients.get(tuple(broker))
        if client is None:
            return
        try:
            await client.publish(BIRTH_TOPIC, "online")
        except Exception as exc:
            self.logger.debug(f"Failed to request the states: {exc}")

    async def ensure_mqtt_client(self, hash, broker):
        """FHEM receives the messages of the broker: it is the MQTT2_SERVER of
        FHEM or a MQTT2_CLIENT exists, otherwise a MQTT2_CLIENT is created
        (without autocreate, only the offered devices are created)."""
        host, port = broker
        local = host in local_addresses()
        cmd = (
            f"my $p = {fhem.perlString(str(port))};; my $l = {1 if local else 0};; "
            "foreach my $d (keys %main::defs) { "
            "my $t = $main::defs{$d}{TYPE} // '';; "
            "return 1 if ($t eq 'MQTT2_CLIENT');; "
            "return 1 if ($l && $t eq 'MQTT2_SERVER' && "
            "(split(' ', $main::defs{$d}{DEF} // ''))[0] eq $p);; "
            "} return 0;;"
        )
        if str(await fhem.sendCommandHash(hash, cmd)).strip() == "1":
            return ""
        name = await self.engine.free_name(hash, "mqtt_broker")
        ret = await fhem.CommandDefine(hash, f"{name} MQTT2_CLIENT {host}:{port}")
        if ret:
            return ret
        await fhem.CommandAttr(hash, f"{name} autocreate no")
        username, password = self.credentials(broker)
        if username:
            await fhem.CommandAttr(hash, f"{name} username {username}")
            await fhem.sendCommandHash(
                hash,
                f"fhem({fhem.perlString(f'set {name} password {password}')}, 1)",
            )
        return ""
