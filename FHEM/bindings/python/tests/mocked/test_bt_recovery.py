import pytest
from fhempy.lib.core import bt_recovery

MAC = "AA:BB:CC:DD:EE:FF"
# keep the real implementation, the fixture replaces it
restart_bluetoothd = bt_recovery.restart_bluetoothd


@pytest.fixture(autouse=True)
def recovery(mocker):
    bt_recovery._states.clear()
    bt_recovery._lock = None
    mocker.patch.object(bt_recovery, "SETTLE_TIME", 0)
    calls = []

    def stage(name, result=True):
        async def run(*args):
            calls.append(name)
            return result

        return run

    mocks = {
        "alive": mocker.patch.object(
            bt_recovery, "bluetoothd_alive", side_effect=stage("alive")
        ),
        "power_cycle": mocker.patch.object(
            bt_recovery, "power_cycle", side_effect=stage("power_cycle")
        ),
        "adapter_reset": mocker.patch.object(
            bt_recovery, "adapter_reset", side_effect=stage("adapter_reset")
        ),
        "restart": mocker.patch.object(
            bt_recovery, "restart_bluetoothd", side_effect=stage("restart")
        ),
    }
    return calls, mocks, stage


async def fail(times):
    """Report failures, return the recovery result if one was executed."""
    results = [await bt_recovery.report_failure("hci0", MAC) for _ in range(times)]
    executed = [r for r in results if r is not None]
    assert len(executed) <= 1
    return executed[0] if executed else None


def expire_cooldown():
    bt_recovery._states["hci0"].last_recovery -= bt_recovery.MAX_COOLDOWN


@pytest.mark.asyncio
async def test_recovery_after_three_failures(recovery):
    calls, _, _ = recovery
    assert await fail(2) is None
    assert calls == []
    assert await fail(1) == "power cycle: ok"
    assert calls == ["alive", "power_cycle"]


@pytest.mark.asyncio
async def test_escalates_and_respects_cooldown(recovery):
    calls, _, _ = recovery
    await fail(3)
    # cooldown active, no further recovery
    assert await fail(3) is None
    expire_cooldown()
    assert await fail(3) == "adapter reset: ok"
    expire_cooldown()
    assert await fail(3) == "bluetoothd restart: ok"
    expire_cooldown()
    assert await fail(3) == "power cycle: ok"
    assert [c for c in calls if c != "alive"] == [
        "power_cycle",
        "adapter_reset",
        "restart",
        "power_cycle",
    ]


@pytest.mark.asyncio
async def test_cooldown_doubles_and_resets_on_success(recovery):
    await fail(3)
    expire_cooldown()
    await fail(3)
    assert bt_recovery._states["hci0"].cooldown == 2 * bt_recovery.COOLDOWN
    bt_recovery.report_success("hci0")
    assert "hci0" not in bt_recovery._states
    assert await fail(3) == "power cycle: ok"


@pytest.mark.asyncio
async def test_falls_through_stages_without_permission(recovery):
    calls, mocks, stage = recovery
    mocks["power_cycle"].side_effect = stage("power_cycle", False)
    mocks["adapter_reset"].side_effect = stage("adapter_reset", False)
    assert await fail(3) == "power cycle, adapter reset, bluetoothd restart: ok"


@pytest.mark.asyncio
async def test_all_stages_fail(recovery):
    _, mocks, stage = recovery
    for name, key in [
        ("power_cycle", "power_cycle"),
        ("adapter_reset", "adapter_reset"),
        ("restart", "restart"),
    ]:
        mocks[key].side_effect = stage(name, False)
    assert await fail(3) == "power cycle, adapter reset, bluetoothd restart: failed"
    assert bt_recovery._states["hci0"].stage == 0


@pytest.mark.asyncio
async def test_hung_bluetoothd_is_restarted_directly(recovery):
    calls, mocks, stage = recovery
    mocks["alive"].side_effect = stage("alive", False)
    assert await fail(3) == "bluetoothd restart (bluetoothd not responding): ok"
    assert calls == ["alive", "restart"]


@pytest.mark.asyncio
async def test_restart_bluetoothd_without_sudoers(mocker):
    # sudo -n fails if no sudoers entry exists
    mocker.patch.object(bt_recovery.shutil, "which", return_value="/bin/false")
    assert await restart_bluetoothd() is False


def test_hci_index():
    assert bt_recovery.hci_index("hci0") == 0
    assert bt_recovery.hci_index("hci12") == 12
