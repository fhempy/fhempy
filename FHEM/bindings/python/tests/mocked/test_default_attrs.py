import pytest
from tests.utils import mock_fhem

from fhempy.lib import fhem


def setup(mocker):
    mock_fhem.mock_module(mocker)
    mock_fhem.attributes.clear()
    mock_fhem.readings.clear()

    async def command_attr(hash, attrdef):
        name, attr, value = attrdef.split(" ", 2)
        mock_fhem.attributes.setdefault(name, {})[attr] = value
        mock_fhem.command_attr.append(attrdef)

    mocker.patch("fhempy.lib.fhem.CommandAttr", command_attr)
    mock_fhem.command_attr.clear()


def restart():
    # FHEM restores attributes from fhem.cfg and readings from the statefile
    mock_fhem.command_attr.clear()


@pytest.mark.asyncio
async def test_new_device_gets_defaults_once(mocker):
    setup(mocker)
    hash = {"NAME": "car"}
    await fhem.setDefaultAttrs(hash, {"icon": "car", "devStateIcon": "ok:on"})
    assert mock_fhem.attributes["car"] == {"icon": "car", "devStateIcon": "ok:on"}

    # deleted icon stays deleted after restart/update
    del mock_fhem.attributes["car"]["icon"]
    restart()
    await fhem.setDefaultAttrs(hash, {"icon": "car", "devStateIcon": "ok:on"})
    assert mock_fhem.command_attr == []
    assert "icon" not in mock_fhem.attributes["car"]


@pytest.mark.asyncio
async def test_custom_attribute_is_kept(mocker):
    setup(mocker)
    mock_fhem.attributes["car"] = {"icon": "my_car"}
    await fhem.setDefaultAttrs({"NAME": "car"}, {"icon": "car"})
    assert mock_fhem.command_attr == []
    # also when the user deletes it later
    del mock_fhem.attributes["car"]["icon"]
    await fhem.setDefaultAttrs({"NAME": "car"}, {"icon": "car"})
    assert mock_fhem.command_attr == []


@pytest.mark.asyncio
async def test_new_default_attribute_is_set_once(mocker):
    # a later fhempy version may add a default attribute
    setup(mocker)
    await fhem.setDefaultAttrs({"NAME": "car"}, {"icon": "car"})
    await fhem.setDefaultAttrs({"NAME": "car"}, {"icon": "car", "webCmd": "on:off"})
    assert mock_fhem.command_attr == ["car icon car", "car webCmd on:off"]
    assert mock_fhem.readings["car"][fhem.DEFAULT_ATTRS_READING] == "icon,webCmd"


@pytest.mark.asyncio
async def test_other_device(mocker):
    setup(mocker)
    await fhem.setDefaultAttrs({"NAME": "io"}, {"webCmd": "on:off"}, "MQTT2_lamp")
    assert mock_fhem.command_attr == ["MQTT2_lamp webCmd on:off"]
    assert mock_fhem.readings["MQTT2_lamp"][fhem.DEFAULT_ATTRS_READING] == "webCmd"
