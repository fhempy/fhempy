import json
import logging

import pytest
from tests.utils import mock_fhem

from fhempy.lib.core import mqtt_ha
from fhempy.lib.pkg_installer import check_and_install_dependencies

ESPHOME_SWITCH = {
    "name": "yellow",
    "stat_t": "baerli/switch/yellow/state",
    "cmd_t": "baerli/switch/yellow/command",
    "avty_t": "baerli/status",
    "uniq_id": "ESPswitchyellow",
    "dev": {"ids": "b4e62d451d0d", "name": "baerli", "mdl": "d1_mini"},
}

Z2M_SENSOR = {
    "device": {
        "identifiers": ["zigbee2mqtt_0x00158d0001"],
        "manufacturer": "Xiaomi",
        "model": "Temperature sensor",
        "name": "Wohnzimmer Temp",
    },
    "name": "Temperature",
    "state_topic": "zigbee2mqtt/Wohnzimmer Temp",
    "unique_id": "0x00158d0001_temperature_zigbee2mqtt",
    "unit_of_measurement": "°C",
    "value_template": "{{ value_json.temperature }}",
}
AVAILABILITY = (
    "baerli/status:.* { my $p = $EVENT; return undef if ($p ne 'online' && "
    "$p ne 'offline'); my $v = $p eq 'online' ? 1 : 0; return { "
    "'.availability0' => $v, availability => $v ? 'online' : 'offline' } }"
)


class Msg:
    def __init__(self, topic, payload):
        self.topic = type("Topic", (), {"value": topic})()
        self.payload = payload


async def define_device(mocker, existing=None):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("mqtt_ha_discovery")
    from fhempy.lib.mqtt_ha_discovery.mqtt_ha_discovery import mqtt_ha_discovery

    mqtt_ha_discovery.existing_devices.clear()
    mock_fhem.command_define.clear()
    mock_fhem.command_attr.clear()
    mock_fhem.attributes.clear()
    mqtt_ha._entities.clear()

    async def command_attr(hash, attrdef):
        name, attr, value = attrdef.split(" ", 2)
        mock_fhem.attributes.setdefault(name, {})[attr] = value
        mock_fhem.command_attr.append(attrdef)

    async def command_list(hash, listcmd):
        return existing or ""

    mocker.patch("fhempy.lib.fhem.CommandList", command_list)
    mocker.patch("fhempy.lib.fhem.CommandAttr", command_attr)
    device = mqtt_ha_discovery(logging.getLogger(__name__))
    mocker.patch.object(device, "create_async_task", lambda coro: coro.close())
    await device.Define(
        {"NAME": "mqttha", "FHEMPYTYPE": "mqtt_ha_discovery"},
        ["mqttha", "fhempy", "mqtt_ha_discovery"],
        {},
    )
    mock_fhem.command_attr.clear()
    return device


@pytest.mark.asyncio
async def test_esphome_switch(mocker):
    device = await define_device(mocker)
    await device.handle_ha_msg(
        Msg(
            "homeassistant/switch/baerli/yellow/config",
            json.dumps(ESPHOME_SWITCH).encode(),
        )
    )
    assert mock_fhem.command_define == ["MQTT2_baerli_b4e62d451d0d MQTT2_DEVICE"]
    assert mock_fhem.command_attr == [
        "MQTT2_baerli_b4e62d451d0d readingList "
        "baerli/switch/yellow/state:.* { { yellow=>lc($EVENT) } }\n" + AVAILABILITY,
        "MQTT2_baerli_b4e62d451d0d setList "
        "yellow_on:noArg baerli/switch/yellow/command ON\n"
        "yellow_off:noArg baerli/switch/yellow/command OFF",
    ]


@pytest.mark.asyncio
async def test_full_key_names_without_node_id(mocker):
    # Zigbee2MQTT uses full key names ("device" instead of "dev"), issue #626
    device = await define_device(mocker)
    await device.handle_ha_msg(
        Msg(
            "homeassistant/sensor/0x00158d0001/temperature/config",
            json.dumps(Z2M_SENSOR).encode(),
        )
    )
    assert mock_fhem.command_define == [
        "MQTT2_Wohnzimmer_Temp_zigbee2mqtt_0x00158d0001 MQTT2_DEVICE"
    ]
    # topic with space, JSON message: a reading for each value
    assert mock_fhem.command_attr == [
        "MQTT2_Wohnzimmer_Temp_zigbee2mqtt_0x00158d0001 readingList "
        "zigbee2mqtt/Wohnzimmer.Temp:.* { json2nameValue($EVENT) }",
        "MQTT2_Wohnzimmer_Temp_zigbee2mqtt_0x00158d0001 stateFormat temperature °C",
    ]

    # topic without node_id and without device
    mock_fhem.command_define.clear()
    await device.handle_ha_msg(
        Msg(
            "homeassistant/sensor/outside_temp/config",
            json.dumps({"name": None, "stat_t": "~/temp", "~": "garden"}).encode(),
        )
    )
    assert mock_fhem.command_define == ["MQTT2_outside_temp_outside_temp MQTT2_DEVICE"]
    assert mock_fhem.command_attr[-1] == (
        "MQTT2_outside_temp_outside_temp readingList "
        "garden/temp:.* { { outside_temp=>$EVENT } }"
    )


@pytest.mark.asyncio
async def test_ignored_messages(mocker):
    device = await define_device(mocker)
    for topic, payload in [
        ("homeassistant/status", b"online"),
        ("homeassistant/switch/baerli/yellow/config", b""),
        ("homeassistant/switch/baerli/yellow/config", b"not json"),
        ("homeassistant/sensor/baerli/x/config", b'{"name": "no topics"}'),
    ]:
        await device.handle_ha_msg(Msg(topic, payload))
    assert mock_fhem.command_attr == []


@pytest.mark.asyncio
async def test_device_discovery(mocker):
    device = await define_device(mocker)
    payload = {
        "dev": {"ids": "ea334450945afc", "name": "Kitchen"},
        "o": {"name": "bla2mqtt"},
        "cmps": {
            "temp": {"p": "sensor", "name": "Temp", "state_topic": "kitchen/temp"},
            "lamp": {
                "p": "light",
                "schema": "json",
                "name": "Lamp",
                "stat_t": "kitchen/lamp",
                "cmd_t": "kitchen/lamp/set",
                "supported_color_modes": ["brightness"],
            },
        },
    }
    await device.handle_ha_msg(
        Msg("homeassistant/device/kitchen/config", json.dumps(payload).encode())
    )
    # one device for all components
    assert mock_fhem.command_define == ["MQTT2_Kitchen_ea334450945afc MQTT2_DEVICE"]
    reading_list = mock_fhem.attributes["MQTT2_Kitchen_ea334450945afc"][
        "readingList"
    ].split("\n")
    assert sorted(reading_list) == [
        "kitchen/lamp:.* { my $r = json2nameValue($EVENT); $r->{state} = "
        "lc($r->{state}) if (($r->{state} // '') =~ /^(ON|OFF)$/); $r }",
        "kitchen/temp:.* { { Temp=>$EVENT } }",
    ]
    # the only light is the device itself: on, off, brightness
    assert mock_fhem.attributes["MQTT2_Kitchen_ea334450945afc"]["setList"] == (
        'on:noArg kitchen/lamp/set {"state":"ON"}\n'
        'off:noArg kitchen/lamp/set {"state":"OFF"}\n'
        "brightness:colorpicker,BRI,0,1,255 kitchen/lamp/set "
        '{"state":"ON","brightness":$EVTPART1}'
    )
    assert mock_fhem.attributes["MQTT2_Kitchen_ea334450945afc"]["webCmd"] == (
        "on:off:brightness"
    )


@pytest.mark.asyncio
async def test_existing_device_from_readinglist(mocker):
    device = await define_device(mocker, existing="myswitch")
    mock_fhem.attributes["myswitch"] = {
        "readingList": "baerli/switch/yellow/state:.* { { yellow=>lc(\\$EVENT) } }"
    }
    await device.handle_ha_msg(
        Msg(
            "homeassistant/switch/baerli/yellow/config",
            json.dumps(ESPHOME_SWITCH).encode(),
        )
    )
    assert mock_fhem.command_define == []
    # broken \$EVENT is repaired, topic isn't added twice
    assert mock_fhem.command_attr[0] == (
        "myswitch readingList baerli/switch/yellow/state:.* { { yellow=>lc($EVENT) } }"
    )
    assert mock_fhem.command_attr[1] == (
        "myswitch readingList baerli/switch/yellow/state:.* "
        "{ { yellow=>lc($EVENT) } }\n" + AVAILABILITY
    )
    assert mock_fhem.command_attr[2].startswith("myswitch setList yellow_on")
    assert len(mock_fhem.command_attr) == 3
