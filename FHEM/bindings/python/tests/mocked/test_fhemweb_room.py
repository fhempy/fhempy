import pytest

from fhempy.lib import fhem
from fhempy.lib.core import fhemweb


async def setup_command(mocker, **kwargs):
    commands = []

    async def send(hash, cmd):
        commands.append(cmd)
        return "ok"

    async def readings_val(name, reading, default):
        return default

    async def update(*args):
        return None

    mocker.patch.object(fhem, "sendCommandHash", side_effect=send)
    mocker.patch.object(fhem, "ReadingsVal", side_effect=readings_val)
    mocker.patch.object(fhem, "readingsSingleUpdate", side_effect=update)
    await fhemweb.setup_room({"NAME": "tl"}, "Timeline", "icon_a", "icon_b", **kwargs)
    return commands[0]


@pytest.mark.asyncio
async def test_setup_room_moves_from_fhempy(mocker):
    cmd = await setup_command(mocker)
    assert "$cur eq '' || $cur eq 'fhempy'" in cmd


@pytest.mark.asyncio
async def test_setup_room_keeps_fhempy(mocker):
    cmd = await setup_command(mocker, keep_fhempy=True)
    assert "my $rooms = ($cur eq '')" in cmd
    assert "'fhempy'" not in cmd
