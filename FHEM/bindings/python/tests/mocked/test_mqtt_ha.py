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
