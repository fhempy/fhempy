import json
from pathlib import Path

import pytest
from tests.utils import mock_fhem

from fhempy.lib.core import mqtt_ha

# the same devices are tested with MQTT2_DEVICE in FHEM by
# t/FHEM/MQTT2_DEVICE/01_mqtt_ha.t (readings and published messages)
FIXTURE = (
    Path(__file__).parents[5] / "t" / "FHEM" / "MQTT2_DEVICE" / "mqtt_ha_devices.json"
)
SCENARIOS = json.loads(FIXTURE.read_text(encoding="utf-8"))


def entities(scenario):
    result = []
    for topic, payload in scenario["discovery"]:
        for component, _, object_id, payload_json in mqtt_ha.parse_discovery(
            topic, json.dumps(payload)
        ):
            result.append((component, object_id, payload_json))
    return result


@pytest.mark.parametrize("scenario", SCENARIOS, ids=[s["name"] for s in SCENARIOS])
def test_attributes_tested_in_fhem(scenario):
    assert mqtt_ha.generate_attributes(entities(scenario)) == scenario["attributes"]


def test_icons_tested_in_fhem():
    # 01_mqtt_ha.t checks that FHEMWEB has these icons
    icons = json.loads(FIXTURE.with_name("mqtt_ha_icons.json").read_text())
    assert mqtt_ha.all_icons() == icons


@pytest.mark.asyncio
async def test_legacy_state_format_is_replaced(mocker):
    """stateFormat of older versions showed battery, voltage and linkquality"""
    mock_fhem.mock_module(mocker)
    mock_fhem.command_attr.clear()
    scenario = next(s for s in SCENARIOS if s["name"] == "z2m_contact")
    name = "MQTT2_Contact"
    attrs = scenario["attributes"]
    mock_fhem.attributes[name] = {
        "readingList": "\n".join(attrs["readingList"]),
        "stateFormat": "battery % voltage mV linkquality lqi",
    }
    await mqtt_ha.set_device_attributes({"NAME": "x"}, name, entities(scenario))
    assert mock_fhem.command_attr == [
        f"{name} stateFormat {attrs['stateFormat']}",
        f"{name} devStateIcon {attrs['devStateIcon']}",
    ]

    # stateFormat of the user is kept
    mock_fhem.command_attr.clear()
    mock_fhem.attributes[name]["stateFormat"] = "contact"
    mock_fhem.attributes[name]["devStateIcon"] = "true:fts_door"
    await mqtt_ha.set_device_attributes({"NAME": "x"}, name, entities(scenario))
    assert mock_fhem.command_attr == []


def test_zigbee2mqtt_light_like_home_assistant():
    attrs = mqtt_ha.generate_attributes(entities(SCENARIOS[0]))
    # one JSON topic for the light and all other entities of the device
    assert attrs["readingList"][0].startswith(
        "zigbee2mqtt/Wandlampe:.* { my $r = json2nameValue($EVENT);"
    )
    assert [line.split(" ")[0] for line in attrs["setList"]] == [
        "on:noArg",
        "off:noArg",
        "brightness:colorpicker,BRI,0,1,254",
        "color_temp:colorpicker,CT,153,1,454",
        "color:colorpicker,RGB",
        "effect:blink,breathe,okay,channel_change,finish_effect,stop_effect",
        "power_on_behavior:off,on,toggle,previous",
    ]
    assert attrs["webCmd"] == "on:off:brightness"
    assert len([line for line in attrs["readingList"] if "availability" in line]) == 2


def test_template_key():
    assert mqtt_ha.template_key(None) is None
    assert mqtt_ha.template_key("{{ value }}") is None
    assert mqtt_ha.template_key("{{ value_json.temperature }}") == "temperature"
    assert mqtt_ha.template_key('{{ value_json["power_on_behavior"] }}') == (
        "power_on_behavior"
    )
    assert mqtt_ha.template_key("{{ value_json['update']['state'] }}") == (
        "update_state"
    )
    assert mqtt_ha.template_key("{{ value_json.a | default(0) }}") == "a"
    assert mqtt_ha.template_key("{% if value_json.x %}1{% endif %}") is (
        mqtt_ha.JSON_MESSAGE
    )


def test_topic_with_space_and_regex_characters():
    assert mqtt_ha.topic_regex("zigbee2mqtt/Wohnzimmer Temp") == (
        "zigbee2mqtt/Wohnzimmer.Temp"
    )
    assert mqtt_ha.topic_regex("a/b+(c)") == "a/b\\+\\(c\\)"
    # MQTT2 can't publish to a topic with spaces
    attrs = mqtt_ha.generate_attributes(
        [("switch", "x", {"state_topic": "a b", "command_topic": "a b/set"})]
    )
    assert attrs["setList"] == []


def test_device_of_older_version_is_repaired():
    attrs = mqtt_ha.generate_attributes(entities(SCENARIOS[0]))
    reading_list = mqtt_ha.merge_reading_list(
        "zigbee2mqtt/Wandlampe:.* { { light=>lc($EVENT) } }\nmy/topic:.* mine",
        attrs["readingList"],
    )
    assert reading_list.split("\n")[0] == attrs["readingList"][0]
    assert "my/topic:.* mine" in reading_list
    assert "light=>" not in reading_list

    set_list = mqtt_ha.merge_set_list(
        'light_on zigbee2mqtt/Wandlampe/set {"state": "ON", "transition": 1}\n'
        'light_off zigbee2mqtt/Wandlampe/set {"state": "OFF", "transition": 1}\n'
        "light_brightness:colorpicker,BRI,0,5,255 zigbee2mqtt/Wandlampe/set "
        '{"state":"ON","brightness":$EVTPART1}\n'
        "on:noArg my/own on",
        attrs["setList"],
    )
    assert "light_" not in set_list
    # commands of the user are kept
    assert set_list.split("\n")[0] == "on:noArg my/own on"
    assert set_list.split("\n")[1:] == attrs["setList"][1:]


@pytest.mark.asyncio
async def test_set_attributes_collects_entities(mocker):
    mock_fhem.mock_module(mocker)
    mock_fhem.command_attr.clear()
    mock_fhem.attributes.clear()
    mqtt_ha._entities.clear()

    async def command_attr(hash, attrdef):
        name, attr, value = attrdef.split(" ", 2)
        mock_fhem.attributes.setdefault(name, {})[attr] = value
        mock_fhem.command_attr.append(attrdef)

    mocker.patch("fhempy.lib.fhem.CommandAttr", command_attr)
    for component, object_id, payload in entities(SCENARIOS[0]):
        await mqtt_ha.set_attributes({}, "lamp", component, object_id, payload)
    attrs = SCENARIOS[0]["attributes"]
    assert mock_fhem.attributes["lamp"] == {
        "readingList": "\n".join(attrs["readingList"]),
        "setList": "\n".join(attrs["setList"]),
        "webCmd": attrs["webCmd"],
    }
    # nothing is written again
    count = len(mock_fhem.command_attr)
    await mqtt_ha.set_attributes({}, "lamp", *entities(SCENARIOS[0])[0])
    assert len(mock_fhem.command_attr) == count


def test_climate_cover_fan_lock_siren_are_supported():
    # climate has no state_topic or command_topic
    assert mqtt_ha.supported("climate", {"mode_command_topic": "x/set/mode"})
    assert not mqtt_ha.supported("climate", {"availability_topic": "x/status"})
    assert mqtt_ha.supported("lock", {"command_topic": "x/set"})


def test_command_template_variables():
    assert mqtt_ha.command_payload('{ "position": {{ position }} }') == (
        '{ "position": $EVTPART1 }'
    )
    assert mqtt_ha.command_payload("{{ tilt_position }}") == "$EVTPART1"
    assert mqtt_ha.command_payload("{{ value | int }}") is None


def test_default_icon_of_new_devices():
    assert mqtt_ha.default_icon([("sensor", "a", {}), ("light", "b", {})]) == (
        "light_light"
    )
    # battery is diagnostic, the device is a contact sensor
    entities = [
        (
            "sensor",
            "battery",
            {"device_class": "battery", "entity_category": "diagnostic"},
        ),
        ("binary_sensor", "contact", {"device_class": "door"}),
    ]
    assert mqtt_ha.default_icon(entities) == "fts_door"
    assert mqtt_ha.default_icon([("sensor", "x", {"device_class": "battery"})]) is (
        None
    )


def test_device_readings_with_zigbee_model():
    device = {
        "identifiers": ["zigbee2mqtt_0x001788010301ba38"],
        "manufacturer": "Philips",
        "model": "Hue white and color ambiance E26/E27/E14",
        "model_id": "9290022166",
    }
    assert mqtt_ha.device_readings([("light", "light", {"device": device})]) == {
        "model": "Hue white and color ambiance E26/E27/E14",
        "zigbeeModel": "9290022166",
        "manufacturer": "Philips",
    }
    # older Zigbee2MQTT versions put the model id in brackets
    device = {
        "identifiers": ["zigbee2mqtt_0x01"],
        "model": "Hue white and color ambiance (9290012573A)",
    }
    assert mqtt_ha.device_readings([("light", "light", {"device": device})]) == {
        "model": "Hue white and color ambiance",
        "zigbeeModel": "9290012573A",
    }
    # ESPHome
    device = {"identifiers": ["abc"], "model": "esp32dev", "manufacturer": "espressif"}
    assert mqtt_ha.device_readings([("switch", "s", {"device": device})]) == {
        "model": "esp32dev",
        "manufacturer": "espressif",
    }
    assert mqtt_ha.device_readings([("switch", "s", {})]) == {}
