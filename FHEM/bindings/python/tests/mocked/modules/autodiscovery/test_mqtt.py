import json
import logging

import pytest
from tests.utils import mock_fhem

from fhempy.lib.autodiscovery import catalog
from fhempy.lib.autodiscovery import mqtt as mqtt_module
from fhempy.lib.autodiscovery.engine import STATUS_EXISTS, STATUS_NEW, Engine
from fhempy.lib.pkg_installer import check_and_install_dependencies

from .test_engine import FakeFrontend

BROKER = ("127.0.0.1", 1883)


def z2m_entity(ieee, name, component="sensor", **extra):
    payload = {
        "device": {
            "identifiers": [f"zigbee2mqtt_{ieee}"],
            "manufacturer": "Xiaomi",
            "model": "WSDCGQ11LM",
            "name": "Wohnzimmer Temp",
        },
        "name": name,
        "state_topic": "zigbee2mqtt/wohnzimmer_temp",
        "value_template": "{{ value_json.%s }}" % name.lower(),
        **extra,
    }
    topic = f"homeassistant/{component}/{ieee}/{name.lower()}/config"
    return topic, json.dumps(payload).encode()


@pytest.fixture
def fhem_calls(mocker):
    """FHEM has a MQTT2_SERVER on 1883 unless no_server is set."""
    mock_fhem.mock_module(mocker)
    mock_fhem.command_define.clear()
    mock_fhem.command_attr.clear()
    mock_fhem.attributes.clear()
    state = {"server": True, "existing": "", "commands": []}

    async def send(hash, cmd):
        state["commands"].append(cmd)
        if "MQTT2_SERVER" in cmd:
            return "1" if state["server"] else "0"
        if "while (defined" in cmd:
            return cmd.split("my $n = ")[1].split(";;")[0].strip("\"'")
        if "grep { !defined" in cmd:
            return state.get("deleted", "")
        return ""

    async def command_list(hash, listcmd):
        return state["existing"]

    mocker.patch("fhempy.lib.fhem.sendCommandHash", side_effect=send)
    mocker.patch("fhempy.lib.fhem.CommandList", command_list)
    return state


@pytest.fixture
def engine():
    eng = Engine(logging.getLogger(__name__))
    eng.catalog = catalog.load()
    eng.running = True
    eng.frontends.append(FakeFrontend())
    return eng


@pytest.mark.asyncio
async def test_each_device_offered_once_and_created_on_click(engine, fhem_calls):
    await engine.mqtt.handle_message(
        BROKER, *z2m_entity("0x01", "Temperature", device_class="temperature")
    )
    await engine.mqtt.handle_message(BROKER, *z2m_entity("0x01", "Humidity"))
    await engine.mqtt.handle_message(BROKER, *z2m_entity("0x02", "Temperature"))

    # one candidate per device, nothing created yet
    assert sorted(engine.candidates) == [
        "mqtt:zigbee2mqtt_0x01",
        "mqtt:zigbee2mqtt_0x02",
    ]
    candidate = engine.candidates["mqtt:zigbee2mqtt_0x01"]
    assert candidate["status"] == STATUS_NEW
    assert candidate["title"] == "Wohnzimmer Temp"
    assert candidate["model"] == "Xiaomi WSDCGQ11LM"
    assert candidate["logo"] == "mqtt_ha_discovery.png"
    assert candidate["action"] == "callback"
    assert mock_fhem.command_define == []

    published = []

    class Client:
        async def publish(self, topic, payload):
            published.append((topic, payload))

    engine.mqtt._clients[BROKER] = Client()
    assert await engine.create({"NAME": "x"}, candidate["id"], "", {}) == ""
    assert mock_fhem.command_define == [
        "MQTT2_Wohnzimmer_Temp_zigbee2mqtt_0x01 MQTT2_DEVICE"
    ]
    assert candidate["device"] == "MQTT2_Wohnzimmer_Temp_zigbee2mqtt_0x01"
    # the devices send their states again: readings right after the creation
    assert published == [("homeassistant/status", "online")]
    # one JSON topic with temperature and humidity, the friendly name of
    # Zigbee2MQTT as alias, icon and events only on changes
    assert mock_fhem.command_attr == [
        "MQTT2_Wohnzimmer_Temp_zigbee2mqtt_0x01 readingList "
        "zigbee2mqtt/wohnzimmer_temp:.* { json2nameValue($EVENT) }",
        "MQTT2_Wohnzimmer_Temp_zigbee2mqtt_0x01 stateFormat temperature",
        "MQTT2_Wohnzimmer_Temp_zigbee2mqtt_0x01 alias Wohnzimmer Temp",
        "MQTT2_Wohnzimmer_Temp_zigbee2mqtt_0x01 icon temp_temperature",
        "MQTT2_Wohnzimmer_Temp_zigbee2mqtt_0x01 event-on-change-reading .*",
    ]
    setreadings = [c for c in fhem_calls["commands"] if "CommandSetReading" in c]
    assert setreadings == [
        "CommandSetReading(undef, "
        "'MQTT2_Wohnzimmer_Temp_zigbee2mqtt_0x01 model WSDCGQ11LM')",
        "CommandSetReading(undef, "
        "'MQTT2_Wohnzimmer_Temp_zigbee2mqtt_0x01 manufacturer Xiaomi')",
    ]

    # entities after the creation are added to the device
    mock_fhem.attributes["MQTT2_Wohnzimmer_Temp_zigbee2mqtt_0x01"] = {
        "readingList": mock_fhem.command_attr[0].split(" ", 2)[2],
        "alias": "Wohnzimmer Temp",
        "stateFormat": "temperature",
    }
    mock_fhem.command_attr.clear()
    await engine.mqtt.handle_message(
        BROKER,
        *z2m_entity(
            "0x01",
            "Battery",
            state_topic="zigbee2mqtt/wohnzimmer_temp/battery",
            value_template=None,
        ),
    )
    assert mock_fhem.command_attr == [
        "MQTT2_Wohnzimmer_Temp_zigbee2mqtt_0x01 readingList "
        "zigbee2mqtt/wohnzimmer_temp:.* { json2nameValue($EVENT) }\n"
        "zigbee2mqtt/wohnzimmer_temp/battery:.* { { Battery=>$EVENT } }"
    ]


@pytest.mark.asyncio
async def test_existing_and_unsupported_devices_are_not_offered(engine, fhem_calls):
    fhem_calls["existing"] = "MyTempSensor"
    await engine.mqtt.handle_message(BROKER, *z2m_entity("0x01", "Temperature"))
    # listed as in FHEM, offered again when deleted
    candidate = engine.candidates.pop("mqtt:zigbee2mqtt_0x01")
    assert candidate["status"] == STATUS_EXISTS
    assert candidate["device"] == "MyTempSensor"

    fhem_calls["existing"] = ""
    # no topics and components without state or command topic
    await engine.mqtt.handle_message(
        BROKER,
        "homeassistant/sensor/x/y/config",
        b'{"name": "no topics"}',
    )
    await engine.mqtt.handle_message(
        BROKER,
        *z2m_entity(
            "0x03",
            "Action",
            component="device_automation",
            state_topic=None,
            topic="zigbee2mqtt/wohnzimmer_temp/action",
        ),
    )
    await engine.mqtt.handle_message(BROKER, "homeassistant/status", b"online")
    await engine.mqtt.handle_message(
        BROKER, "homeassistant/sensor/x/z/config", b"not json"
    )
    assert engine.candidates == {}


@pytest.mark.asyncio
async def test_existing_device_set_up_again_keeps_its_name(engine, fhem_calls):
    """e.g. created by Zigbee2MQTT autocreate with an attrTemplate"""
    fhem_calls["existing"] = "MQTT2_zigbee_wohnzimmer"
    await engine.mqtt.handle_message(
        BROKER, *z2m_entity("0x01", "Temperature", device_class="temperature")
    )
    candidate = engine.candidates["mqtt:zigbee2mqtt_0x01"]
    assert candidate["status"] == STATUS_EXISTS
    assert candidate["can_recreate"] is True
    name = "MQTT2_zigbee_wohnzimmer"
    mock_fhem.attributes[name] = {
        "readingList": "zigbee2mqtt/wohnzimmer_temp:.* { json2nameValue($EVENT,'',$JSONMAP) }\n"
        "zigbee2mqtt/wohnzimmer_temp:.* { {own=>$EVENT} }",
        "setList": "attrTemplate:... x",
        "stateFormat": "battery % voltage mV",
        "model": "zigbee2mqtt_temp",
        "room": "Wohnzimmer",
        "alias": "Temperatur",
        "icon": "temperature_humidity",
    }
    published = []

    class Client:
        async def publish(self, topic, payload):
            published.append((topic, payload))

    engine.mqtt._clients[BROKER] = Client()
    assert await engine.recreate(candidate["id"]) == ""
    # nothing defined, the name stays, room and alias of the user are kept,
    # the icon like for a new device
    assert mock_fhem.command_define == []
    assert mock_fhem.command_attr == [
        f"{name} readingList zigbee2mqtt/wohnzimmer_temp:.* "
        "{ json2nameValue($EVENT) }",
        f"{name} stateFormat temperature",
        f"{name} icon temp_temperature",
        f"{name} event-on-change-reading .*",
    ]
    deleted = [c for c in fhem_calls["commands"] if "CommandDeleteAttr" in c]
    assert deleted == [
        f"CommandDeleteAttr(undef, '{name} setList')",
        f"CommandDeleteAttr(undef, '{name} model')",
    ]
    assert published == [("homeassistant/status", "online")]

    # further entities of the device update it
    mock_fhem.command_attr.clear()
    mock_fhem.attributes[name][
        "readingList"
    ] = "zigbee2mqtt/wohnzimmer_temp:.* { json2nameValue($EVENT) }"
    await engine.mqtt.handle_message(
        BROKER,
        *z2m_entity(
            "0x01",
            "Battery",
            state_topic="zigbee2mqtt/wohnzimmer_temp/battery",
            value_template=None,
        ),
    )
    assert mock_fhem.command_attr[0].startswith(f"{name} readingList")

    # only devices in FHEM
    fhem_calls["existing"] = ""
    await engine.mqtt.handle_message(BROKER, *z2m_entity("0x02", "Temperature"))
    assert engine.recreatable() == [candidate]
    assert "isn't in FHEM" in await engine.recreate("mqtt:zigbee2mqtt_0x02")
    assert "isn't found" in await engine.recreate("mqtt:unknown")


@pytest.mark.asyncio
async def test_deleted_mqtt_device_is_offered_again(engine, fhem_calls):
    fhem_calls["existing"] = "MyTempSensor"
    await engine.mqtt.handle_message(BROKER, *z2m_entity("0x01", "Temperature"))
    candidate = engine.candidates["mqtt:zigbee2mqtt_0x01"]
    assert candidate["status"] == STATUS_EXISTS

    fhem_calls["existing"] = ""
    fhem_calls["deleted"] = "MyTempSensor"
    await engine.recheck()
    assert candidate["status"] == STATUS_NEW
    assert candidate["deleted"] is True
    assert await engine.create({"NAME": "x"}, candidate["id"], "", {}) == ""
    assert mock_fhem.command_define[-1] == (
        "MQTT2_Wohnzimmer_Temp_zigbee2mqtt_0x01 MQTT2_DEVICE"
    )


@pytest.mark.asyncio
async def test_mqtt2_client_created_without_mqtt_in_fhem(engine, fhem_calls):
    fhem_calls["server"] = False
    engine.mqtt.username = "fhem"
    engine.mqtt.password = "secret"
    broker = ("192.168.1.5", 1883)
    await engine.mqtt.handle_message(broker, *z2m_entity("0x01", "Temperature"))
    assert await engine.create({"NAME": "x"}, "mqtt:zigbee2mqtt_0x01", "", {}) == ""
    assert mock_fhem.command_define == [
        "mqtt_broker MQTT2_CLIENT 192.168.1.5:1883",
        "MQTT2_Wohnzimmer_Temp_zigbee2mqtt_0x01 MQTT2_DEVICE",
    ]
    assert mock_fhem.command_attr[:2] == [
        "mqtt_broker autocreate no",
        "mqtt_broker username fhem",
    ]
    assert any("set mqtt_broker password secret" in c for c in fhem_calls["commands"])


def test_brokers(engine, mocker):
    started = []
    mocker.patch.object(
        engine.mqtt,
        "_broker_loop",
        new=lambda key: started.append(key) or mocker.MagicMock(),
    )
    mocker.patch.object(mqtt_module.asyncio, "create_task", lambda coro: coro)
    mocker.patch.object(mqtt_module, "local_addresses", lambda: {"192.168.1.2"})

    engine.mqtt.add_broker("127.0.0.1", 1883)
    # the local broker announced via mDNS isn't connected twice
    engine.mqtt.found_broker("192.168.1.2", 1883)
    engine.mqtt.found_broker("192.168.1.9", 1883)
    engine.mqtt.add_broker("127.0.0.1", 1883, "user", "pw")
    assert started == [("127.0.0.1", 1883), ("192.168.1.9", 1883)]
    assert engine.mqtt.credentials(("127.0.0.1", 1883)) == ("user", "pw")

    # only the broker of attribute mqtt
    engine.mqtt.stop()
    started.clear()
    engine.mqtt.configure("10.0.0.1:1884")
    engine.mqtt.found_broker("192.168.1.9", 1883)
    engine.mqtt.add_broker("127.0.0.1", 1883)
    assert started == [("10.0.0.1", 1884)]

    engine.mqtt.configure("off")
    assert engine.mqtt.brokers == []


@pytest.mark.asyncio
async def test_mqtt_ha_discovery_leaves_new_devices_to_autodiscovery(
    engine, fhem_calls, mocker
):
    await check_and_install_dependencies("mqtt_ha_discovery")
    from fhempy.lib.mqtt_ha_discovery.mqtt_ha_discovery import mqtt_ha_discovery

    mqtt_ha_discovery.existing_devices.clear()
    mocker.patch.object(Engine, "instance", engine)
    added = []
    mocker.patch.object(
        engine.mqtt, "add_broker", side_effect=lambda *args: added.append(args)
    )
    device = mqtt_ha_discovery(logging.getLogger(__name__))
    mocker.patch.object(device, "create_async_task", lambda coro: coro.close())
    await device.Define(
        {"NAME": "mqttha", "FHEMPYTYPE": "mqtt_ha_discovery"},
        ["mqttha", "fhempy", "mqtt_ha_discovery", "10.0.0.2", "1883", "u", "p"],
        {},
    )

    class Msg:
        def __init__(self, topic, payload):
            self.topic = type("Topic", (), {"value": topic})()
            self.payload = payload

    await device.handle_ha_msg(Msg(*z2m_entity("0x01", "Temperature")))
    assert mock_fhem.command_define == []
    assert added == [("10.0.0.2", 1883, "u", "p")]
