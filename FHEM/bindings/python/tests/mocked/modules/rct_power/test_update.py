import logging
from datetime import datetime

import pytest
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies


async def define_device(mocker):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("rct_power")
    from fhempy.lib.rct_power.rct_power import rct_power

    mock_fhem.readings.pop("testrct", None)
    testhash = {"NAME": "testrct", "FHEMPYTYPE": "rct_power"}
    device = rct_power(logging.getLogger(__name__))
    # don't start the endless update loop
    mocker.patch.object(device, "create_async_task", lambda coro: coro.close())
    await device.Define(testhash, ["testrct", "fhempy", "rct_power", "127.0.0.1"], {})
    await device.setup_rct()
    return device


def mock_get_data(requested):
    from fhempy.lib.rct_power.api import ValidApiResponse
    from rctclient.registry import REGISTRY

    async def get_data(object_ids):
        requested.extend(object_ids)
        return {
            oid: ValidApiResponse(
                object_id=oid,
                object_name=REGISTRY.get_by_id(oid).name,
                time=datetime.now(),
                value=1.5,
            )
            for oid in object_ids
        }

    return get_data


@pytest.mark.asyncio
async def test_all_default_objects_are_read(mocker):
    device = await define_device(mocker)
    from fhempy.lib.rct_power.rct_power import rct_power
    from rctclient.registry import REGISTRY

    requested = []
    mocker.patch.object(device.rctclient, "async_get_data", mock_get_data(requested))

    await device.update_readings()

    assert len(requested) == len(rct_power.DEFAULT_OBJECTS)
    for name in rct_power.DEFAULT_OBJECTS:
        assert REGISTRY.get_by_name(name).object_id in requested
    readings = mock_fhem.readings["testrct"]
    assert readings["battery.temperature"] == "1.50"
    assert readings["power_mng.soc_max"] == "1.50"
    assert readings["state"] == "connected"


@pytest.mark.asyncio
async def test_connection_error_ends_update(mocker):
    device = await define_device(mocker)
    mocker.patch.object(device.rctclient, "async_get_data", side_effect=TimeoutError())
    end_update = mocker.patch("fhempy.lib.fhem.readingsEndUpdate")

    await device.update_readings()

    assert mock_fhem.readings["testrct"]["state"] == "connection error"
    end_update.assert_awaited_once()
