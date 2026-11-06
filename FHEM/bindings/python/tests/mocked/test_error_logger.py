"""utils.ErrorLogger and utils.RepeatedLogFilter: a device that keeps
retrying must not flood the log."""

import asyncio
import logging

import pytest
from fhempy.lib import utils

from ..utils import mock_fhem


class Clock:
    def __init__(self, monkeypatch):
        self.now = 1_000_000.0
        monkeypatch.setattr(utils.time, "time", lambda: self.now)


def messages(caplog, level=logging.INFO):
    return [r.getMessage() for r in caplog.records if r.levelno >= level]


def fail(errors, exc, msg="Failed to connect", key=None):
    try:
        raise exc
    except Exception:
        errors.failed(msg, key=key)


def test_first_failure_once_then_summaries(monkeypatch, caplog):
    clock = Clock(monkeypatch)
    logger = logging.getLogger("errlog_summary")
    logger.setLevel(logging.INFO)
    errors = utils.ErrorLogger(logger)
    caplog.set_level(logging.INFO, logger="errlog_summary")

    # one attempt every 10s for 30 hours
    for _ in range(30 * 360):
        fail(errors, ConnectionRefusedError("refused"))
        clock.now += 10

    logged = messages(caplog)
    assert logged[0] == "Failed to connect: ConnectionRefusedError: refused"
    summaries = [m for m in logged if m.startswith("Still failing")]
    # after 1h, 6h, 24h
    assert len(summaries) == 3
    assert summaries[0].startswith("Still failing since 1h (361 attempts)")
    assert summaries[2].startswith("Still failing since 1d (")
    assert len(logged) == 4
    assert errors.attempts() == 30 * 360

    errors.success()
    assert messages(caplog)[-1] == (
        "Works again after 1d6h and 10800 failed attempts: Failed to connect"
    )
    assert not errors.is_failing()
    assert errors.attempts() == 0


def test_daily_summary_after_first_day(monkeypatch, caplog):
    clock = Clock(monkeypatch)
    logger = logging.getLogger("errlog_daily")
    errors = utils.ErrorLogger(logger)
    caplog.set_level(logging.INFO, logger="errlog_daily")
    for _ in range(4 * 24):
        fail(errors, TimeoutError())
        clock.now += 3600
    summaries = [m for m in messages(caplog) if m.startswith("Still failing")]
    # 1h, 6h, 24h, 48h, 72h
    assert len(summaries) == 5


def test_new_error_type_logged_once(monkeypatch, caplog):
    Clock(monkeypatch)
    logger = logging.getLogger("errlog_types")
    errors = utils.ErrorLogger(logger)
    caplog.set_level(logging.INFO, logger="errlog_types")
    for _ in range(5):
        fail(errors, ConnectionRefusedError("refused"))
        fail(errors, TimeoutError("timeout"))
    assert messages(caplog) == [
        "Failed to connect: ConnectionRefusedError: refused",
        "Failed to connect: TimeoutError: timeout",
    ]


def test_unexpected_error_with_traceback(monkeypatch, caplog):
    Clock(monkeypatch)
    logger = logging.getLogger("errlog_tb")
    errors = utils.ErrorLogger(logger)
    caplog.set_level(logging.INFO, logger="errlog_tb")
    fail(errors, ValueError("bad"))
    fail(errors, ValueError("bad"))
    errors_logged = [r for r in caplog.records if r.levelno >= logging.INFO]
    assert len(errors_logged) == 1
    assert errors_logged[0].levelno == logging.ERROR
    assert errors_logged[0].exc_info is not None


def test_next_delay_backoff(monkeypatch):
    Clock(monkeypatch)
    errors = utils.ErrorLogger(logging.getLogger("errlog_delay"))
    assert 4.5 <= errors.next_delay() <= 5.5
    delays = []
    for _ in range(12):
        fail(errors, OSError("down"))
        delays.append(errors.next_delay())
    assert 4.5 <= delays[0] <= 5.5
    assert 9 <= delays[1] <= 11
    assert 18 <= delays[2] <= 22
    assert 540 <= delays[-1] <= 660
    errors.success()
    assert errors.next_delay() <= 5.5


def test_format_duration():
    assert utils.format_duration(45) == "45s"
    assert utils.format_duration(12 * 60 + 5) == "12m"
    assert utils.format_duration(3 * 3600 + 12 * 60) == "3h12m"
    assert utils.format_duration(2 * 86400 + 3 * 3600) == "2d3h"
    assert utils.format_duration(86400) == "1d"


@pytest.mark.asyncio
async def test_readings_state_and_last_error(mocker, monkeypatch):
    mock_fhem.mock_module(mocker)
    Clock(monkeypatch)
    hash = {"NAME": "errlog_device"}
    mock_fhem.readings[hash["NAME"]] = {"state": "online"}
    sent = []
    original = mock_fhem.readingsSingleUpdateIfChanged

    async def track(h, reading, value, trigger):
        sent.append((reading, value))
        await original(h, reading, value, trigger)

    mocker.patch("fhempy.lib.fhem.readingsSingleUpdateIfChanged", track)
    errors = utils.ErrorLogger(logging.getLogger("errlog_dev"), hash, "disconnected")

    for _ in range(20):
        fail(errors, ConnectionRefusedError("refused"))
    await asyncio.sleep(0.05)
    readings = mock_fhem.readings[hash["NAME"]]
    assert readings["state"] == "disconnected"
    assert readings["lastError"] == "Failed to connect: ConnectionRefusedError: refused"
    # no update per attempt
    assert sent == [
        ("lastError", "Failed to connect: ConnectionRefusedError: refused"),
        ("state", "disconnected"),
    ]

    errors.success()
    await asyncio.sleep(0.05)
    assert readings["state"] == "online"
    # lastError stays, its timestamp tells when it happened
    assert readings["lastError"].startswith("Failed to connect")


@pytest.mark.asyncio
async def test_state_not_restored_if_module_changed_it(mocker, monkeypatch):
    mock_fhem.mock_module(mocker)
    Clock(monkeypatch)
    hash = {"NAME": "errlog_device2"}
    mock_fhem.readings[hash["NAME"]] = {"state": "online"}
    errors = utils.ErrorLogger(logging.getLogger("errlog_dev2"), hash, "disconnected")
    fail(errors, OSError("down"))
    await asyncio.sleep(0.05)
    mock_fhem.readings[hash["NAME"]]["state"] = "playing"
    errors.success()
    await asyncio.sleep(0.05)
    assert mock_fhem.readings[hash["NAME"]]["state"] == "playing"


def make_record(name, msg, created, level=logging.WARNING, args=()):
    record = logging.LogRecord(name, level, __file__, 1, msg, args, None)
    record.created = created
    return record


def test_repeated_log_filter():
    logging.getLogger("lib.flood").setLevel(logging.INFO)
    flt = utils.RepeatedLogFilter()
    passed = []
    t = 1000.0
    # a library logs a failed reconnect every 5s for 3 hours
    for i in range(3 * 720):
        record = make_record("lib.flood", "Reconnect to %s failed", t, args=("host",))
        if flt.filter(record):
            passed.append(record.getMessage())
        t += 5
    assert passed[0] == "Reconnect to host failed"
    assert passed[1] == (
        "Reconnect to host failed (repeated 119x in the last 10m, suppressed)"
    )
    # 0, 10m, 30m, 70m, 150m
    assert len(passed) == 5

    # other messages pass
    assert flt.filter(make_record("lib.flood", "Something else", t))
    assert flt.filter(make_record("other", "Reconnect to %s failed", t))
    # info and debug: info filtered too, debug never
    for _ in range(3):
        assert flt.filter(make_record("lib.flood", "dbg", t, logging.DEBUG))

    # quiet for a long time: logged again without suffix
    t += 24 * 3600
    record = make_record("lib.flood", "Reconnect to %s failed", t, args=("host",))
    assert flt.filter(record)
    assert record.getMessage() == "Reconnect to host failed"


def test_repeated_log_filter_verbose5_shows_everything():
    logging.getLogger("lib.verbose").setLevel(logging.DEBUG)
    flt = utils.RepeatedLogFilter()
    for i in range(5):
        assert flt.filter(make_record("lib.verbose", "same", 1000.0 + i))


def test_expected_error_logged_as_warning(monkeypatch, caplog):
    Clock(monkeypatch)
    logger = logging.getLogger("errlog_expected")
    errors = utils.ErrorLogger(logger)
    caplog.set_level(logging.INFO, logger="errlog_expected")
    errors.failed("Device offline", exc=ValueError("lib specific"), expected=True)
    assert caplog.records[0].levelno == logging.WARNING
    assert caplog.records[0].exc_info is None
