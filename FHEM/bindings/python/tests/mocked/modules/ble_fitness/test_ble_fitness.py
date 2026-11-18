import asyncio
import logging
import struct

import pytest
import pytest_asyncio
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies

MAC = "A0:9E:1A:12:34:56"
NAME = "polar"


# --- parser ---


def test_heart_rate_uint8_with_contact_and_rr():
    from fhempy.lib.ble_fitness import parser

    # flags: contact supported + detected, RR present; 72 bpm, RR 1024 and 512
    data = bytes([0x16, 72]) + struct.pack("<HH", 1024, 512)
    assert parser.heart_rate(data) == {
        "heart_rate": 72,
        "sensor_contact": True,
        "rr": [1000, 500],
    }


def test_heart_rate_uint16_without_contact():
    from fhempy.lib.ble_fitness import parser

    data = bytes([0x05]) + struct.pack("<H", 301)
    assert parser.heart_rate(data) == {"heart_rate": 301, "sensor_contact": False}


def test_heart_rate_too_short():
    from fhempy.lib.ble_fitness import parser

    with pytest.raises(ValueError):
        parser.heart_rate(bytes([0x01, 0x50]))


def test_cycling_power_with_crank_and_energy():
    from fhempy.lib.ble_fitness import parser

    flags = 0x0020 | 0x0800 | 0x0001
    data = struct.pack("<HhBHHH", flags, 250, 100, 12, 2048, 7)
    assert parser.cycling_power(data) == {
        "power": 250,
        "balance": 50.0,
        "crank_revolutions": 12,
        "crank_time": 2048,
        "accumulated_energy": 7,
    }


def test_indoor_bike_kickr_style():
    from fhempy.lib.ble_fitness import parser

    # speed (more data bit 0 = 0), cadence, power, heart rate
    flags = 0x0004 | 0x0040 | 0x0200
    data = struct.pack("<HHHhB", flags, 3250, 180, 215, 140)
    assert parser.indoor_bike(data) == {
        "speed": 32.5,
        "cadence": 90.0,
        "power": 215,
        "heart_rate": 140,
    }


def test_indoor_bike_distance_and_more_data():
    from fhempy.lib.ble_fitness import parser

    flags = 0x0001 | 0x0010 | 0x0100
    data = struct.pack("<H", flags) + (70000).to_bytes(3, "little")
    data += struct.pack("<HHB", 0xFFFF, 0xFFFF, 0xFF)
    assert parser.indoor_bike(data) == {"distance": 70000}


def test_revolution_rate_wraps_and_stops():
    from fhempy.lib.ble_fitness import parser

    rate = parser.RevolutionRate(16, 1024)
    assert rate.update(65535, 65000, now=0) is None
    # 2 revolutions in 1.5 s across both wrap arounds -> 80 rpm
    assert rate.update(1, (65000 + 1536) % 65536, now=1.5) == pytest.approx(80)
    # same event repeated: rpm stays, after 3 s without revolution 0
    assert rate.update(1, (65000 + 1536) % 65536, now=2) == pytest.approx(80)
    assert rate.update(1, (65000 + 1536) % 65536, now=5) == 0


def test_control_commands():
    from fhempy.lib.ble_fitness import parser

    assert parser.control_target_power(200) == bytes([0x05, 200, 0])
    assert parser.control_simulation(5) == bytes([0x11, 0, 0, 0xF4, 0x01, 40, 51])
    assert parser.control_response(bytes([0x80, 0x05, 0x01])) == (5, "ok")
    assert parser.control_response(bytes([0x80, 0x00, 0x05])) == (
        0,
        "control not permitted",
    )
    assert parser.control_response(bytes([0x05])) is None


# --- workout ---


def test_workout_summary_with_power_and_zones():
    from fhempy.lib.ble_fitness.workout import Workout

    workout = Workout(0)
    profile = {"max_heart_rate": 200, "age": 40, "weight": 75, "sex": "male"}
    for second in range(1, 601):
        workout.add(second, {"heart_rate": 150, "power": 200}, profile)
    summary = workout.summary()
    assert summary["workout_duration"] == 10.0
    assert summary["workout_heart_rate_avg"] == 150
    assert summary["workout_power_avg"] == 200
    assert summary["workout_energy"] == 120
    # 120 kJ at the pedals, about 120 kcal
    assert summary["workout_calories"] == 120
    assert summary["workout_zone3"] == 10.0
    assert summary["workout_zone1"] == 0


def test_workout_calories_from_heart_rate_and_gaps():
    from fhempy.lib.ble_fitness.workout import Workout, calories_per_minute

    workout = Workout(0)
    profile = {"max_heart_rate": None, "age": 30, "weight": 70, "sex": "female"}
    for second in range(1, 61):
        workout.add(second, {"heart_rate": 140}, profile)
    # a pause of 10 minutes doesn't count
    workout.add(660, {"heart_rate": 140}, profile)
    summary = workout.summary()
    assert summary["workout_duration"] == 1.0
    assert summary["workout_calories"] == round(
        calories_per_minute(140, 70, 30, "female")
    )
    assert "workout_power_avg" not in summary


def test_hrv_rmssd():
    from fhempy.lib.ble_fitness.workout import rmssd

    assert rmssd([800, 810, 790, 800]) == pytest.approx(14.1, abs=0.1)
    # artefacts are dropped
    assert rmssd([800, 100, 810]) is None


# --- module ---


class FakeCharacteristic:
    def __init__(self, uuid, properties):
        self.uuid = uuid
        self.properties = properties


class FakeService:
    def __init__(self, characteristics):
        self.characteristics = characteristics


class FakeClient:
    def __init__(self, uuids, battery=b"\x55"):
        from fhempy.lib.ble_fitness import parser

        self.services = [
            FakeService([FakeCharacteristic(uuid, ["notify"]) for uuid in uuids])
        ]
        self.services[0].characteristics.append(
            FakeCharacteristic(parser.BATTERY_LEVEL, ["read"])
        )
        self.battery = battery
        self.notify = {}
        self.writes = []
        self.is_connected = True

    async def start_notify(self, uuid, callback):
        self.notify[uuid] = callback

    async def read_gatt_char(self, uuid):
        return self.battery

    async def write_gatt_char(self, uuid, data, response=False):
        self.writes.append(bytes(data))


@pytest_asyncio.fixture
async def module(mocker):
    mock_fhem.mock_module(mocker)
    mock_fhem.readings.pop(NAME, None)
    await check_and_install_dependencies("ble_fitness")
    from fhempy.lib.ble_fitness import ble_fitness

    scanner = mocker.MagicMock()
    mocker.patch.object(
        ble_fitness.ble_scanner.BleScanner, "get_instance", return_value=scanner
    )
    mocker.patch.object(ble_fitness, "UPDATE_INTERVAL", 0)
    device = ble_fitness.ble_fitness(logging.getLogger(__name__))
    hash = {"NAME": NAME, "FHEMPYTYPE": "ble_fitness"}
    assert (
        await device.Define(hash, ["polar", "fhempy", "ble_fitness", MAC], {}) is None
    )
    device._scanner_mock = scanner
    yield device
    await device.Undefine(hash)


async def settle():
    for _ in range(5):
        await asyncio.sleep(0)


def readings():
    return mock_fhem.readings[NAME]


@pytest.mark.asyncio
async def test_define_usage():
    await check_and_install_dependencies("ble_fitness")
    from fhempy.lib.ble_fitness import ble_fitness

    device = ble_fitness.ble_fitness(logging.getLogger(__name__))
    hash = {"NAME": NAME, "FHEMPYTYPE": "ble_fitness"}
    result = await device.Define(hash, ["x", "fhempy", "ble_fitness", "nomac"], {})
    assert result.startswith("Usage:")


@pytest.mark.asyncio
async def test_connects_only_when_advertising(module, mocker):
    module._scanner_mock.add_callback.assert_called_once_with(module._advertisement)
    connect_once = mocker.patch.object(module._conn, "connect_once", mocker.AsyncMock())
    other = mocker.MagicMock(address="11:22:33:44:55:66")
    module._advertisement(other, mocker.MagicMock())
    await settle()
    connect_once.assert_not_called()

    strap = mocker.MagicMock(address=MAC.lower())
    module._advertisement(strap, mocker.MagicMock())
    module._advertisement(strap, mocker.MagicMock())
    await settle()
    assert connect_once.await_count == 1
    # failed: not again right away
    assert readings()["state"] == "off"
    module._advertisement(strap, mocker.MagicMock())
    await settle()
    assert connect_once.await_count == 1


@pytest.mark.asyncio
async def test_heart_rate_strap(module, mocker):
    from fhempy.lib.ble_fitness import parser

    mock_fhem.attributes[NAME] = {}
    module._attr_age = 40
    client = FakeClient([parser.HEART_RATE_MEASUREMENT])
    module._conn._client = client
    await module._connected()
    await settle()
    assert readings()["batteryPercent"] == 85
    assert readings()["trainer_control"] == "none"
    assert "target_power" not in module._conf_set

    notify = client.notify[parser.HEART_RATE_MEASUREMENT]
    notify(
        FakeCharacteristic(parser.HEART_RATE_MEASUREMENT, []),
        bytes([0x16, 150]) + struct.pack("<H", 820),
    )
    await settle()
    assert readings()["heart_rate"] == 150
    assert readings()["rr_interval"] == 801
    assert readings()["sensor_contact"] == "yes"
    # max 208 - 0.7 * 40 = 180, 150 is 83 % -> zone 4
    assert readings()["heart_rate_zone"] == 4
    assert readings()["workout"] == "active"
    assert readings()["state"] == "150 bpm"

    client.is_connected = False
    await module._disconnected(client)
    assert readings()["heart_rate"] == 0
    assert readings()["state"] == "off"
    assert module._workout_end_handle is not None
    await module._finish_workout()
    assert readings()["workout"] == "finished"
    assert readings()["workout_heart_rate_max"] == 150


@pytest.mark.asyncio
async def test_trainer_erg_mode(module, mocker):
    from fhempy.lib.ble_fitness import parser

    client = FakeClient([parser.INDOOR_BIKE_DATA, parser.FITNESS_MACHINE_CONTROL_POINT])
    module._conn._client = client
    await module._connected()
    assert readings()["trainer_control"] == "available"
    assert "target_power" in module._conf_set

    flags = 0x0004 | 0x0040
    client.notify[parser.INDOOR_BIKE_DATA](
        parser.INDOOR_BIKE_DATA, struct.pack("<HHHh", flags, 3000, 170, 180)
    )
    await settle()
    assert readings()["power"] == 180
    assert readings()["cadence"] == 85
    assert readings()["speed"] == 30.0
    assert readings()["state"] == "180 W"

    assert await module.set_target_power(module.hash, {"watts": 200}) is None
    assert client.writes == [parser.CONTROL_REQUEST, bytes([0x05, 200, 0])]
    assert readings()["target_power"] == 200

    client.notify[parser.FITNESS_MACHINE_CONTROL_POINT](
        parser.FITNESS_MACHINE_CONTROL_POINT, bytes([0x80, 0x05, 0x05])
    )
    await settle()
    assert readings()["trainer_control"] == "control not permitted"


@pytest.mark.asyncio
async def test_power_meter_cadence_from_crank(module, mocker):
    from fhempy.lib.ble_fitness import parser

    client = FakeClient([parser.CYCLING_POWER_MEASUREMENT])
    module._conn._client = client
    await module._connected()
    notify = client.notify[parser.CYCLING_POWER_MEASUREMENT]
    from fhempy.lib.ble_fitness import ble_fitness

    times = iter([100.0, 101.0])
    clock = mocker.MagicMock()
    clock.monotonic.side_effect = lambda: next(times, 101.0)
    mocker.patch.object(ble_fitness, "time", clock)
    notify(
        parser.CYCLING_POWER_MEASUREMENT,
        struct.pack("<HhHH", 0x0020, 200, 10, 1024),
    )
    notify(
        parser.CYCLING_POWER_MEASUREMENT,
        struct.pack("<HhHH", 0x0020, 210, 11, 1024 + 683),
    )
    await settle()
    assert readings()["power"] == 210
    # one revolution in 683/1024 s -> 90 rpm
    assert readings()["cadence"] == 90


def test_discovery_finds_strap_and_trainer():
    from fhempy.lib.autodiscovery import catalog

    entries = catalog.load()
    strap = list(
        catalog.match_ble(
            entries,
            "Polar H10 A1B2C3D4",
            {107: b"\x00"},
            {"0000180d-0000-1000-8000-00805f9b34fb"},
            -70,
        )
    )
    assert [entry["module"] for entry, _ in strap] == ["ble_fitness"]
    trainer = list(
        catalog.match_ble(
            entries,
            "KICKR CORE 1A2B",
            {},
            {
                "00001818-0000-1000-8000-00805f9b34fb",
                "00001826-0000-1000-8000-00805f9b34fb",
            },
            -70,
        )
    )
    assert [entry["module"] for entry, _ in trainer] == ["ble_fitness"]


@pytest.mark.asyncio
async def test_bluetoothle_without_reconnect(mocker):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("ble_fitness")
    from fhempy.lib.core import bluetoothle

    conn = bluetoothle.BluetoothLE(
        logging.getLogger(__name__), {"NAME": NAME}, MAC, reconnect=False
    )
    connect = mocker.patch.object(conn, "connect", mocker.AsyncMock())
    client = mocker.MagicMock(is_connected=False)
    client.disconnect = mocker.AsyncMock()
    conn._client = client
    await conn.async_disconnected(client)
    connect.assert_not_called()


@pytest.mark.asyncio
async def test_trainer_uses_only_fitness_machine_data(module, mocker):
    """KICKR CORE: Cycling Power and Indoor Bike Data at the same time, the
    readings mustn't alternate between both (cadence 0 / 0.0)."""
    from fhempy.lib.ble_fitness import parser

    client = FakeClient(
        [
            parser.CYCLING_POWER_MEASUREMENT,
            parser.INDOOR_BIKE_DATA,
            parser.FITNESS_MACHINE_CONTROL_POINT,
        ]
    )
    module._conn._client = client
    await module._connected()
    assert parser.INDOOR_BIKE_DATA in client.notify
    assert parser.CYCLING_POWER_MEASUREMENT not in client.notify

    # standing still: cadence 0 (resolution 0.5), speed 0
    client.notify[parser.INDOOR_BIKE_DATA](
        parser.INDOOR_BIKE_DATA, struct.pack("<HHHh", 0x0044, 0, 0, 0)
    )
    await settle()
    assert repr(readings()["cadence"]) == "0"
    assert repr(readings()["speed"]) == "0.0"
    assert repr(readings()["power"]) == "0"

    client.is_connected = False
    await module._disconnected(client)
    # the same text after the disconnect, no event
    assert repr(readings()["cadence"]) == "0"
    assert repr(readings()["speed"]) == "0.0"


def test_normalize_fixed_decimals():
    from fhempy.lib.ble_fitness import ble_fitness

    assert ble_fitness.normalize(
        {"cadence": 87.5, "speed": 30.12, "power": 210, "heart_rate": 140}
    ) == {"cadence": 88, "speed": 30.1, "power": 210, "heart_rate": 140}
    assert repr(ble_fitness.normalize({"speed": 0})["speed"]) == "0.0"
