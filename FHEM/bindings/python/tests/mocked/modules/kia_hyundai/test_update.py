import asyncio
import logging
from unittest.mock import MagicMock

import pytest
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies


async def setup_device(mocker):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("kia_hyundai")

    from fhempy.lib.kia_hyundai.kia_hyundai import kia_hyundai

    testhash = {"NAME": "testcar", "FHEMPYTYPE": "kia_hyundai"}
    device = kia_hyundai(logging.getLogger(__name__))
    # define without parameters only sets up the config
    await device.Define(testhash, ["testcar", "fhempy", "kia_hyundai"], {})

    calls = []
    vehicle = MagicMock()
    vehicle.id = "vehicle1"
    vehicle.data = {"ev_battery_percentage": 80}
    vehicle.geocode = ["home"]
    vm = MagicMock()
    vm.vehicles = {"vehicle1": vehicle}
    for name in [
        "check_and_refresh_token",
        "force_refresh_vehicle_state",
        "update_all_vehicles_with_cached_state",
    ]:
        getattr(vm, name).side_effect = (
            lambda name: lambda *args: calls.append((name,) + args)
        )(name)
    device.vm = vm
    return device, testhash, calls


@pytest.mark.asyncio
async def test_update_data(mocker):
    device, testhash, calls = await setup_device(mocker)

    await device.Set(testhash, ["testcar", "update_data"], {})
    await asyncio.sleep(1)

    assert ("force_refresh_vehicle_state", "vehicle1") not in calls
    assert ("update_all_vehicles_with_cached_state",) in calls
    assert mock_fhem.readings["testcar"]["ev_battery_percentage"] == 80


@pytest.mark.asyncio
async def test_force_update(mocker):
    device, testhash, calls = await setup_device(mocker)

    assert "force_update:noArg" in await device.Set(testhash, ["testcar", "?"], {})

    await device.Set(testhash, ["testcar", "force_update"], {})
    await asyncio.sleep(1)

    assert calls.index(("force_refresh_vehicle_state", "vehicle1")) < calls.index(
        ("update_all_vehicles_with_cached_state",)
    )
    assert mock_fhem.readings["testcar"]["ev_battery_percentage"] == 80
    assert mock_fhem.readings["testcar"]["state"] == "online"
