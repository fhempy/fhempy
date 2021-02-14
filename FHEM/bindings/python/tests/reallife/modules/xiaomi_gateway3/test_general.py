import pytest
import logging
import os
import asyncio
from tests.utils import mock_fhem
from fhempy.lib.xiaomi_gateway3.xiaomi_gateway3 import xiaomi_gateway3
from fhempy.lib.xiaomi_gateway3_device.xiaomi_gateway3_device import (
    xiaomi_gateway3_device,
)


@pytest.mark.asyncio
async def test_general(mocker):
    """
    This test requires following environment variables defined
    in pytest.ini:
        XIAOMI_GATEWAY3_IP
        XIAOMI_GATEWAY3_TOKEN
        XIAOMI_GATEWAY3_MAC
        XIAOMI_GATEWAY3_lumiweatherv1=did
        XIAOMI_GATEWAY3_sensormagnetaq2=did
        XIAOMI_GATEWAY3_sensormotionv2=did
    """
    # prepare
    mock_fhem.mock_module(mocker)
    mocker.patch("socket.socket.connect_ex", return_value=0)

    testhash = {"NAME": "testdevice"}
    logger = logging.getLogger(__name__)
    xg_module = xiaomi_gateway3(logger)
    await xg_module.Define(
        testhash,
        [
            "testdevice",
            "PythonModule",
            "xiaomi_gateway3",
            os.environ["XIAOMI_GATEWAY3_IP"],
            os.environ["XIAOMI_GATEWAY3_TOKEN"],
        ],
        {},
    )

    mocker.patch(
        "fhempy.lib.fhem_pythonbinding.getFhemPyDeviceByName", return_value=xg_module
    )
    # wait for connection setup and device creation
    await asyncio.sleep(3)
    # remove duplicates
    mock_fhem.command_define = list(dict.fromkeys(mock_fhem.command_define))
    assert (
        mock_fhem.command_define.index(
            f"lumigatewaymgl03_0x{os.environ['XIAOMI_GATEWAY3_MAC']} "
            f"PythonModule xiaomi_gateway3_device testdevice "
            f"lumi.0x{os.environ['XIAOMI_GATEWAY3_MAC']}"
        )
        > -1
    )

    for dev_define in mock_fhem.command_define:
        defarr = dev_define.split(" ")
        devname = defarr[0]
        devhash = {"NAME": devname}
        dev_module = xiaomi_gateway3_device(logger)
        await dev_module.Define(devhash, defarr, {})

    await asyncio.sleep(5)

    # weather test
    weather_readings = mock_fhem.readings[
        "lumiweatherv1_0x" + os.environ["XIAOMI_GATEWAY3_lumiweatherv1"]
    ]
    assert weather_readings["state"] == "online"
    assert (
        weather_readings["did"] == "lumi." + os.environ["XIAOMI_GATEWAY3_lumiweatherv1"]
    )
    assert weather_readings["mac"] == "0x" + os.environ["XIAOMI_GATEWAY3_lumiweatherv1"]
    assert weather_readings["model"] == "lumi.weather.v1"
    assert weather_readings["type"] == "zigbee"
    assert weather_readings["zb_ver"] == "1.2"
    assert float(weather_readings["temperature"]) > 0
    assert float(weather_readings["humidity"]) > 0
    assert float(weather_readings["pressure"]) > 0
    assert int(weather_readings["battery"]) > 0
    assert weather_readings["online"] is True
    assert weather_readings["device_manufacturer"] == "Aqara"
    assert weather_readings["device_model"] == "lumi.weather WSDCGQ11LM"

    # sensor magnet test
    sensor_readings = mock_fhem.readings[
        "lumisensormagnetaq2_0x" + os.environ["XIAOMI_GATEWAY3_sensormagnetaq2"]
    ]
    assert sensor_readings["state"] == "online"
    assert (
        sensor_readings["did"]
        == "lumi." + os.environ["XIAOMI_GATEWAY3_sensormagnetaq2"]
    )
    assert (
        sensor_readings["mac"] == "0x" + os.environ["XIAOMI_GATEWAY3_sensormagnetaq2"]
    )
    assert sensor_readings["model"] == "lumi.sensor_magnet.aq2"
    assert sensor_readings["type"] == "zigbee"
    assert sensor_readings["zb_ver"] == "1.2"
    assert int(sensor_readings["contact"]) >= 0
    assert int(sensor_readings["battery"]) > 0
    assert sensor_readings["online"] is True
    assert sensor_readings["device_manufacturer"] == "Aqara"
    assert sensor_readings["device_model"] == "lumi.sensor_magnet.aq2 MCCGQ11LM"

    # sensor motion test
    sensor_readings = mock_fhem.readings[
        "lumisensormotionv2_0x" + os.environ["XIAOMI_GATEWAY3_sensormotionv2"]
    ]
    assert sensor_readings["state"] == "online"
    assert (
        sensor_readings["did"] == "lumi." + os.environ["XIAOMI_GATEWAY3_sensormotionv2"]
    )
    assert sensor_readings["mac"] == "0x" + os.environ["XIAOMI_GATEWAY3_sensormotionv2"]
    assert sensor_readings["model"] == "lumi.sensor_motion.v2"
    assert sensor_readings["type"] == "zigbee"
    assert sensor_readings["zb_ver"] == "1.2"
    assert int(sensor_readings["battery"]) > 0
    assert sensor_readings["online"] is True
    assert sensor_readings["device_manufacturer"] == "Xiaomi"
    assert sensor_readings["device_model"] == "lumi.sensor_motion RTCGQ01LM"
