import logging

import pytest

from fhempy.lib.autodiscovery import residents


def test_known_neighbours_accepts_probe_state():
    neighbours = {
        ("192.0.2.1", 1): ("aa:00:00:00:00:01", 0x02),  # REACHABLE
        ("192.0.2.2", 1): ("aa:00:00:00:00:02", 0x10),  # PROBE
        ("192.0.2.3", 1): ("aa:00:00:00:00:03", 0x04),  # STALE
        ("192.0.2.4", 1): ("", 0x01),  # INCOMPLETE
        ("192.0.2.5", 1): ("aa:00:00:00:00:05", 0x20),  # FAILED
        ("192.0.2.6", 1): ("00:00:00:00:00:00", 0x02),
    }
    assert sorted(residents.known_neighbours(neighbours)) == [
        "aa:00:00:00:00:01",
        "aa:00:00:00:00:02",
        "aa:00:00:00:00:03",
    ]


@pytest.mark.asyncio
async def test_phone_answering_in_a_later_round_is_found(mocker):
    probes = []
    tables = [
        {},
        {},
        {("192.0.2.7", 1): ("6a:00:00:00:00:07", 0x02)},
        {},
        {},
    ]

    async def run_blocking(func):
        return func()

    mocker.patch.object(residents.utils, "run_blocking", run_blocking)
    mocker.patch.object(residents, "local_networks", return_value=[])
    mocker.patch.object(residents, "_probe", lambda networks: probes.append(1))
    mocker.patch.object(residents.Host, "find_with_netlink", lambda: tables.pop(0))
    mocker.patch.object(residents, "_hostname", return_value="")
    mocker.patch.object(
        residents, "companion_names", mocker.AsyncMock(return_value={})
    )
    mocker.patch.object(residents, "used_addresses", mocker.AsyncMock(return_value=set()))
    mocker.patch.object(residents.asyncio, "sleep", mocker.AsyncMock())

    phones = await residents.find_phones({"NAME": "x"}, logging.getLogger("t"))
    assert len(probes) == residents.PROBE_ROUNDS
    assert [p["mac"] for p in phones] == ["6a:00:00:00:00:07"]
