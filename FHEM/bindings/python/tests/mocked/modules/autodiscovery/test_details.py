import json
import logging

import pytest
from tests.utils import mock_fhem

from fhempy.lib.autodiscovery import catalog
from fhempy.lib.autodiscovery import details as details_module
from fhempy.lib.autodiscovery import mqtt as mqtt_module
from fhempy.lib.autodiscovery.autodiscovery import public
from fhempy.lib.autodiscovery.engine import Engine

from .test_engine import FakeFrontend

BROKER = ("127.0.0.1", 1883)
LAMP = "0x0017880100aabbcc"
SENSOR = "0x00158d0001a2b3c4"


def entity(ieee, component, object_id, name, device, **extra):
    payload = {
        "device": {"identifiers": [f"zigbee2mqtt_{ieee}"], **device},
        "origin": {"name": "Zigbee2MQTT"},
        "name": name,
        **extra,
    }
    topic = f"homeassistant/{component}/{ieee}/{object_id}/config"
    return topic, json.dumps(payload).encode()


LAMP_DEVICE = {
    "manufacturer": "Philips",
    "model": "Hue White and color ambiance E27",
    "name": "Floor lamp",
    "sw_version": "1.104.2",
    "via_device": "zigbee2mqtt_bridge_0x00124b0012345678",
}
SENSOR_DEVICE = {
    "manufacturer": "Aqara",
    "model": "WSDCGQ11LM",
    "name": "Bathroom sensor",
}


def lamp_entities():
    state = "zigbee2mqtt/Floor lamp".replace(" ", "_")
    return [
        entity(
            LAMP,
            "light",
            "light",
            None,
            LAMP_DEVICE,
            schema="json",
            state_topic=state,
            command_topic=state + "/set",
            brightness=True,
            supported_color_modes=["xy", "color_temp"],
            max_mireds=500,
            min_mireds=153,
            effect=True,
            effect_list=["blink", "breathe", "okay", "channel_change", "finish"],
        ),
        entity(
            LAMP,
            "select",
            "power_on_behavior",
            "Power-on behavior",
            LAMP_DEVICE,
            entity_category="config",
            state_topic=state,
            command_topic=state + "/set/power_on_behavior",
            value_template="{{ value_json.power_on_behavior }}",
            options=["off", "on", "toggle", "previous"],
        ),
        entity(
            LAMP,
            "sensor",
            "linkquality",
            "Linkquality",
            LAMP_DEVICE,
            entity_category="diagnostic",
            state_topic=state,
            unit_of_measurement="lqi",
            value_template="{{ value_json.linkquality }}",
        ),
    ]


def sensor_entities():
    state = "zigbee2mqtt/bathroom_sensor"

    def sensor(object_id, name, unit, **extra):
        return entity(
            SENSOR,
            "sensor",
            object_id,
            name,
            SENSOR_DEVICE,
            state_topic=state,
            unit_of_measurement=unit,
            value_template="{{ value_json.%s }}" % object_id,
            **extra,
        )

    return [
        sensor("temperature", "Temperature", "°C", device_class="temperature"),
        sensor("humidity", "Humidity", "%", device_class="humidity"),
        sensor("pressure", "Pressure", "hPa", device_class="atmospheric_pressure"),
        sensor(
            "battery",
            "Battery",
            "%",
            device_class="battery",
            entity_category="diagnostic",
        ),
        sensor("linkquality", "Linkquality", "lqi", entity_category="diagnostic"),
    ]


class Client:
    def __init__(self):
        self.subscribed = []
        self.unsubscribed = []
        self.published = []

    async def subscribe(self, topic):
        self.subscribed.append(topic)

    async def unsubscribe(self, topic):
        self.unsubscribed.append(topic)

    async def publish(self, topic, payload):
        self.published.append((topic, payload))


@pytest.fixture
def engine(mocker):
    mock_fhem.mock_module(mocker)
    mock_fhem.command_define.clear()
    mock_fhem.command_attr.clear()

    async def send(hash, cmd):
        return "1" if "MQTT2_SERVER" in cmd else ""

    mocker.patch("fhempy.lib.fhem.sendCommandHash", side_effect=send)
    mocker.patch("fhempy.lib.fhem.CommandList", return_value="")
    mocker.patch.object(mqtt_module, "STATES_DELAY", 0)
    eng = Engine(logging.getLogger(__name__))
    eng.catalog = catalog.load()
    eng.running = True
    eng.frontends.append(FakeFrontend())
    return eng


async def offer(engine, entities):
    for topic, payload in entities:
        await engine.mqtt.handle_message(BROKER, topic, payload)


@pytest.mark.asyncio
async def test_light_details_before_it_is_created(engine):
    client = Client()
    engine.mqtt._clients[BROKER] = client
    engine.mqtt.bridge = details_module.bridge_devices(
        json.dumps(
            [
                {
                    "ieee_address": LAMP,
                    "power_source": "Mains (single phase)",
                    "definition": {
                        "description": "Hue White and color ambiance E26/E27"
                    },
                }
            ]
        )
    )
    await offer(engine, lamp_entities())

    # the state topic of the offered lamp is subscribed, its states requested
    assert client.subscribed == ["zigbee2mqtt/Floor_lamp"]
    await engine.mqtt._states_task
    assert client.published == [("homeassistant/status", "online")]

    await engine.mqtt.handle_message(
        BROKER,
        "zigbee2mqtt/Floor_lamp",
        b'{"state":"ON","brightness":204,"color_temp":370,'
        b'"linkquality":156,"power_on_behavior":"previous"}',
    )
    [candidate] = public(engine.candidates.values())
    details = candidate["details"]
    assert details["chips"] == [
        {"icon": "power", "label": "On / off", "value": "on"},
        {"icon": "sun", "label": "Brightness", "value": "80 %", "range": "0–100 %"},
        {
            "icon": "ctemp",
            "label": "Color temperature",
            "value": "2700 K",
            "range": "2000–6500 K",
        },
        {"icon": "palette", "label": "Color"},
    ]
    assert details["more"] == 1
    groups = {g["title"]: g["items"] for g in details["groups"]}
    assert list(groups) == ["Can do", "Settings", "Status"]
    assert groups["Can do"][-1] == {
        "icon": "spark",
        "label": "Effects",
        "range": "blink, breathe, okay, +2",
    }
    assert groups["Settings"] == [
        {
            "icon": "list",
            "label": "Power-on behavior",
            "value": "previous",
            "range": "off, on, toggle, +1",
        }
    ]
    assert details["signal"] == "156"
    assert details["power"] == "mains"
    assert "battery" not in details
    assert details["device"] == {
        "manufacturer": "Philips",
        "model": "Hue White and color ambiance E27",
        "firmware": "1.104.2",
        "via": "Zigbee2MQTT",
        "description": "Hue White and color ambiance E26/E27",
    }
    assert details["commands"][:5] == ["on", "off", "brightness", "color_temp", "color"]
    assert details["last_message"] > 0

    # created: the values aren't needed anymore
    assert await engine.create({"NAME": "x"}, candidate["id"], "", {}) == ""
    assert client.unsubscribed == ["zigbee2mqtt/Floor_lamp"]
    assert engine.mqtt._topics == {}


@pytest.mark.asyncio
async def test_sensor_values_and_battery(engine):
    await offer(engine, sensor_entities())
    details = engine.mqtt.details(f"zigbee2mqtt_{SENSOR}")
    # no values yet: what it measures
    assert [c["label"] for c in details["chips"]] == [
        "Temperature",
        "Humidity",
        "Pressure",
    ]
    assert "value" not in details["chips"][0]
    assert "last_message" not in details

    await engine.mqtt.handle_message(
        BROKER,
        "zigbee2mqtt/bathroom_sensor",
        b'{"temperature":21.37,"humidity":54,"pressure":1012.4,'
        b'"battery":87,"linkquality":72}',
    )
    details = engine.mqtt.details(f"zigbee2mqtt_{SENSOR}")
    assert [c.get("value") for c in details["chips"]] == [
        "21.37 °C",
        "54 %",
        "1012.4 hPa",
    ]
    assert details["battery"] == "87 %"
    assert details["signal"] == "72"
    assert "power" not in details
    groups = {g["title"]: g["items"] for g in details["groups"]}
    assert list(groups) == ["Measures", "Status"]
    assert [i["label"] for i in groups["Status"]] == ["Battery", "Linkquality"]
    assert details["commands"] == []


def test_binary_sensor_texts():
    item = details_module._items(
        "binary_sensor",
        "contact",
        {
            "name": "Door",
            "device_class": "door",
            "state_topic": "zigbee2mqtt/door",
            "value_template": "{{ value_json.contact }}",
            "payload_on": False,
            "payload_off": True,
        },
    )[0]
    assert item.public({"zigbee2mqtt/door": {"contact": False}})["value"] == "open"
    assert item.public({"zigbee2mqtt/door": {"contact": True}})["value"] == "closed"
    assert item.icon == "door"


def test_unknown_templates_and_messages():
    dev = details_module.DeviceDetails()
    assert dev.message("a/b", b"not json") is True
    assert dev.message("a/b", b"not json") is False
    assert dev.messages["a/b"] == "not json"
    item = details_module._items(
        "sensor",
        "x",
        {"name": "X", "state_topic": "a/b", "value_template": "{{ value | int }}"},
    )[0]
    # Jinja isn't evaluated: no value instead of a wrong one
    assert "value" not in item.public(dev.messages)
    assert details_module.bridge_devices(b"garbage") == {}
    assert details_module.ieee_of("zigbee2mqtt_0xABC") == "0xABC"
    assert details_module.ieee_of("esphome_kitchen") == ""
