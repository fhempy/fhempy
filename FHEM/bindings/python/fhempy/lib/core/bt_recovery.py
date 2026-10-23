"""
Staged recovery for stuck Bluetooth adapters.

BluetoothLE reports failed connection attempts per adapter. After
FAILURES_BEFORE_RECOVERY failures in a row the adapter gets recovered,
each recovery escalating one stage further:
 1. power cycle the adapter via BlueZ D-Bus (no extra privileges)
 2. bluetooth-auto-recovery: MGMT power cycle / USB reset (CAP_NET_ADMIN)
 3. restart bluetoothd via `sudo -n systemctl restart bluetooth` (sudoers)
A stage which isn't permitted or fails falls through to the next one.
If bluetoothd doesn't answer on D-Bus at all, it gets restarted right away.

Independent of the stages, drop_stale_connection() disconnects a device
which BlueZ still holds connected although fhempy has no connection to it.
"""

import asyncio
import logging
import shutil
import time

FAILURES_BEFORE_RECOVERY = 3
# minimum time between two recoveries of the same adapter, doubles after
# each recovery which didn't lead to a successful connection
COOLDOWN = 300
MAX_COOLDOWN = 3600
DBUS_TIMEOUT = 10
# time to wait for BlueZ to settle after a recovery
SETTLE_TIME = 5

STAGE_POWER_CYCLE = "power cycle"
STAGE_ADAPTER_RESET = "adapter reset"
STAGE_RESTART_BLUETOOTHD = "bluetoothd restart"
STAGES = [STAGE_POWER_CYCLE, STAGE_ADAPTER_RESET, STAGE_RESTART_BLUETOOTHD]

logger = logging.getLogger(__name__)


class _AdapterState:
    def __init__(self):
        self.failures = 0
        self.stage = 0
        self.cooldown = COOLDOWN
        self.last_recovery = None


_states = {}
_lock = None
_net_admin_warned = False

CAP_NET_ADMIN = 12


def _state(adapter):
    if adapter not in _states:
        _states[adapter] = _AdapterState()
    return _states[adapter]


def hci_index(adapter):
    """Return 0 for hci0."""
    return int(adapter[3:])


def report_success(adapter):
    """A connection via adapter was established."""
    _states.pop(adapter, None)


async def report_failure(adapter, mac):
    """
    A connection attempt via adapter failed.
    Returns a description of the recovery if one was executed, else None.
    """
    global _lock
    if _lock is None:
        _lock = asyncio.Lock()

    state = _state(adapter)
    state.failures += 1
    if state.failures < FAILURES_BEFORE_RECOVERY:
        return None

    async with _lock:
        # another device might have recovered this adapter in the meantime
        if (
            state.last_recovery is not None
            and time.monotonic() - state.last_recovery < state.cooldown
        ):
            return None
        if state.last_recovery is not None:
            state.cooldown = min(state.cooldown * 2, MAX_COOLDOWN)
        state.last_recovery = time.monotonic()
        state.failures = 0

        result = await _recover(adapter, mac, state)
        await asyncio.sleep(SETTLE_TIME)
        return result


async def _recover(adapter, mac, state):
    if not await bluetoothd_alive():
        logger.error("bluetoothd doesn't respond on D-Bus")
        if await restart_bluetoothd():
            return f"{STAGE_RESTART_BLUETOOTHD} (bluetoothd not responding): ok"
        return f"{STAGE_RESTART_BLUETOOTHD} (bluetoothd not responding): failed"

    stage_funcs = {
        STAGE_POWER_CYCLE: lambda: power_cycle(adapter),
        STAGE_ADAPTER_RESET: lambda: adapter_reset(adapter, mac),
        STAGE_RESTART_BLUETOOTHD: restart_bluetoothd,
    }
    tried = []
    for i in range(state.stage, len(STAGES)):
        stage = STAGES[i]
        logger.warning(f"Bluetooth adapter {adapter} seems stuck, trying {stage}")
        tried.append(stage)
        if await stage_funcs[stage]():
            # next recovery escalates to the following stage
            state.stage = (i + 1) % len(STAGES)
            return f"{', '.join(tried)}: ok"
    state.stage = 0
    return f"{', '.join(tried)}: failed"


async def _dbus_call(member, path, interface, signature="", body=None):
    from dbus_fast import BusType, Message, MessageType
    from dbus_fast.aio import MessageBus

    bus = await asyncio.wait_for(
        MessageBus(bus_type=BusType.SYSTEM).connect(), DBUS_TIMEOUT
    )
    try:
        reply = await asyncio.wait_for(
            bus.call(
                Message(
                    destination="org.bluez",
                    path=path,
                    interface=interface,
                    member=member,
                    signature=signature,
                    body=body or [],
                )
            ),
            DBUS_TIMEOUT,
        )
    finally:
        bus.disconnect()
    if reply.message_type == MessageType.ERROR:
        raise RuntimeError(f"{reply.error_name}: {reply.body}")
    return reply.body


def device_path(adapter, address):
    return f"/org/bluez/{adapter}/dev_{address.upper().replace(':', '_')}"


async def drop_stale_connection(adapter, address):
    """
    BlueZ keeps a connection open when the process which opened it is gone
    (e.g. fhempy restart) or missed the disconnect. A connected device doesn't
    advertise, so a scan never finds it until bluetoothd is restarted.
    Returns a description if a stale connection was found, else None.
    """
    path = device_path(adapter, address)
    try:
        connected = await _dbus_call(
            "Get",
            path,
            "org.freedesktop.DBus.Properties",
            "ss",
            ["org.bluez.Device1", "Connected"],
        )
    except Exception:
        # device unknown to BlueZ or bluetoothd not reachable
        return None
    if not connected or not connected[0].value:
        return None

    logger.warning(
        f"{address} is still connected in BlueZ via {adapter} without fhempy "
        "using it, disconnecting"
    )
    try:
        await _dbus_call("Disconnect", path, "org.bluez.Device1")
        return "stale connection dropped: ok"
    except Exception as ex:
        logger.warning(f"Disconnect of {address} failed: {ex}")
        return "stale connection dropped: failed"


async def drop_stale_connections(address):
    """
    drop_stale_connection() on every adapter which knows the device, for
    callers which don't choose the adapter themselves (bleak default).
    Returns the descriptions of the stale connections found.
    """
    suffix = device_path("", address).rsplit("/", 1)[1]
    try:
        objects = await _dbus_call(
            "GetManagedObjects", "/", "org.freedesktop.DBus.ObjectManager"
        )
    except Exception:
        return []
    results = []
    for path in objects[0] if objects else {}:
        parts = path.split("/")
        if len(parts) == 5 and parts[4] == suffix:
            result = await drop_stale_connection(parts[3], address)
            if result:
                results.append(f"{parts[3]} {result}")
    return results


async def bluetoothd_alive():
    try:
        await _dbus_call("GetManagedObjects", "/", "org.freedesktop.DBus.ObjectManager")
        return True
    except asyncio.TimeoutError:
        return False
    except RuntimeError as ex:
        # bluetoothd not running at all
        if "ServiceUnknown" in str(ex):
            return False
        # e.g. access denied, bluetoothd answered at least
        logger.warning(f"Unable to check bluetoothd: {ex}")
        return True
    except Exception:
        # system bus not reachable, nothing to recover here
        logger.exception("Unable to check bluetoothd")
        return True


async def _set_powered(adapter, powered):
    from dbus_fast import Variant

    await _dbus_call(
        "Set",
        f"/org/bluez/{adapter}",
        "org.freedesktop.DBus.Properties",
        "ssv",
        ["org.bluez.Adapter1", "Powered", Variant("b", powered)],
    )


async def power_cycle(adapter):
    try:
        await _set_powered(adapter, False)
        await asyncio.sleep(2)
        await _set_powered(adapter, True)
        return True
    except Exception as ex:
        logger.warning(f"Power cycle of {adapter} via D-Bus failed: {ex}")
        return False


def has_net_admin(status_file="/proc/self/status"):
    """True if the process has CAP_NET_ADMIN, also if it can't be checked."""
    try:
        with open(status_file, encoding="ascii") as status:
            for line in status:
                if line.startswith("CapEff:"):
                    return bool(int(line.split()[1], 16) & (1 << CAP_NET_ADMIN))
    except (OSError, ValueError):
        pass
    return True


async def adapter_reset(adapter, mac):
    global _net_admin_warned
    if not has_net_admin():
        if not _net_admin_warned:
            _net_admin_warned = True
            logger.warning(
                f"Reset of {adapter} skipped, fhempy needs CAP_NET_ADMIN for this. "
                "Run the fhempy peer installer again (set fhempy_local installPeer "
                "or install_systemd_fhempy.sh) or add AmbientCapabilities=CAP_NET_ADMIN "
                "with sudo systemctl edit fhempy, see Bluetooth auto recovery in README"
            )
        return False
    try:
        from bluetooth_auto_recovery import recover_adapter

        if await recover_adapter(hci_index(adapter), mac):
            return True
        logger.warning(
            f"Reset of {adapter} failed, fhempy needs CAP_NET_ADMIN for this"
        )
    except Exception as ex:
        logger.warning(f"Reset of {adapter} failed: {ex}")
    return False


async def restart_bluetoothd():
    sudo = shutil.which("sudo")
    systemctl = shutil.which("systemctl")
    if sudo is None or systemctl is None:
        logger.warning("Unable to restart bluetoothd, sudo or systemctl missing")
        return False
    try:
        proc = await asyncio.create_subprocess_exec(
            sudo,
            "-n",
            systemctl,
            "restart",
            "bluetooth",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        output, _ = await asyncio.wait_for(proc.communicate(), 60)
    except Exception as ex:
        logger.warning(f"Restart of bluetoothd failed: {ex}")
        return False
    if proc.returncode != 0:
        logger.warning(
            f"Restart of bluetoothd failed ({output.decode(errors='replace').strip()})"
            f", add '<fhempy user> ALL=NOPASSWD: {systemctl} restart bluetooth' "
            "via visudo to allow it"
        )
        return False
    return True
