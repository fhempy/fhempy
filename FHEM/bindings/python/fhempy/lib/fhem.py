import asyncio
import itertools
import logging
import os
import platform
import socket
import time
from datetime import datetime

import websockets

from . import updates
from .json_utils import json_dumps, json_loads
from .version import __version__

logger = logging.getLogger(__name__)

function_active = []
# futures of commands waiting for a change of function_active
function_waiters = []
update_locks = {}
# task which called readingsBeginUpdate, to detect a missing readingsEndUpdate
update_lock_owners = {}
# readings commands collected between readingsBeginUpdate and readingsEndUpdate,
# they are sent to FHEM in one roundtrip on readingsEndUpdate
bulk_updates = {}
wsconnection = None
release_check_lock = asyncio.Lock()
# callbacks for events of other FHEM devices: {device name: [callback]}
event_listeners = {}
# recorder device name -> callback, see setEventRecorder
recorder_listeners = {}
# ids to match FHEM replies to commands sent by fhempy
await_ids = itertools.count(1)

# TODO use run_coroutine_threadsafe if asyncio.get_event_loop() == None
# this would make all functions threadsafe


def updateConnection(ws):
    global wsconnection
    wsconnection = ws


def fhempy_stopping():
    """True while fhempy undefines all devices for a restart, update or
    shutdown, False if a single device is deleted, modified or disabled"""
    return bool(getattr(wsconnection, "_stopping", False))


# FHEM waits this long (ms) for a function reply if it doesn't send its timeout,
# see BindingsIo_Write in 10_BindingsIo.pm
DEFAULT_FUNCTION_TIMEOUT = 3000
DEFAULT_DEFINE_TIMEOUT = 30000


def setFunctionActive(hash):
    entry = {"NAME": hash["NAME"], "id": hash.get("id"), "timer": None}
    timeout = hash.get("timeout")
    if timeout is None:
        if hash.get("function") == "Define":
            timeout = DEFAULT_DEFINE_TIMEOUT
        else:
            timeout = DEFAULT_FUNCTION_TIMEOUT
    try:
        entry["timer"] = asyncio.get_running_loop().call_later(
            int(timeout) / 1000, expireFunction, entry
        )
    except RuntimeError:
        # no running loop, the function stays active until it finishes
        pass
    function_active.append(entry)
    notifyFunctionWaiters()


def removeActiveFunction(entry):
    for i, active in enumerate(function_active):
        if active is entry:
            del function_active[i]
            return True
    return False


def expireFunction(entry):
    # FHEM stopped waiting for the reply, it handles commands of all devices again
    if removeActiveFunction(entry):
        if wsconnection is None or not wsconnection.is_closed():
            logger.warning(
                f"FHEM stopped waiting for {entry['NAME']}, "
                "commands of other devices are sent again"
            )
        notifyFunctionWaiters()


def setFunctionInactive(hash):
    entry = None
    for active in reversed(function_active):
        if active["NAME"] == hash.get("NAME") and active["id"] == hash.get("id"):
            entry = active
            break
    if entry is None:
        # function already expired or wasn't a function call
        return
    if entry["timer"] is not None:
        entry["timer"].cancel()
    removeActiveFunction(entry)
    notifyFunctionWaiters()


def notifyFunctionWaiters():
    for waiter in function_waiters:
        if not waiter.done():
            waiter.set_result(None)
    function_waiters.clear()


async def waitForFunction(name):
    # while FHEM waits for a function reply, it only handles
    # commands of the device which called the function
    while len(function_active) != 0 and function_active[-1]["NAME"] != name:
        waiter = asyncio.get_running_loop().create_future()
        function_waiters.append(waiter)
        try:
            await waiter
        finally:
            if waiter in function_waiters:
                function_waiters.remove(waiter)


async def getDeviceHashName(hash, typeinternal, typevalue, internal, value):
    cmd = (
        "foreach my $fhem_dev (sort keys %main::defs) {"
        + "  return $main::defs{$fhem_dev}{NAME} if("
        + _perlDeviceMatch(typeinternal, typevalue, internal, value)
        + ");;"
        + "}"
        + "return 0;;"
    )
    return await sendCommandHash(hash, cmd)


async def getUniqueId(hash):
    cmd = "getUniqueId()"
    return await sendCommandHash(hash, cmd)


async def init_done(hash):
    cmd = "$init_done"
    res = await sendCommandHash(hash, cmd)
    return int(res)


async def ReadingsVal(name, reading, default):
    cmd = (
        f"ReadingsVal({perlString(name)}, {perlString(reading)}, {perlString(default)})"
    )
    return await sendCommandName(name, cmd)


async def AttrVal(name, attr, default):
    cmd = f"AttrVal({perlString(name)}, {perlString(attr)}, {perlString(default)})"
    return await sendCommandName(name, cmd)


async def InternalVal(name, internal, default):
    cmd = (
        f"InternalVal({perlString(name)}, {perlString(internal)}, "
        f"{perlString(default)})"
    )
    return await sendCommandName(name, cmd)


async def addToDevAttrList(name, attr_list):
    cmd = f"addToDevAttrList({perlString(name)}, {perlString(attr_list)})"
    return await sendCommandName(name, cmd)


def _setDevAttrListCmd(name, attr_list):
    attr_list += " IODev disable:0,1 "
    return (
        f"setDevAttrList({perlString(name)}, "
        f"{perlString(attr_list)}.$readingFnAttributes)"
    )


async def setDevAttrList(name, attr_list):
    return await sendCommandName(name, _setDevAttrListCmd(name, attr_list))


async def getDeviceInfo(name, attrs, dev_attr_list=None):
    """Get $init_done and attribute values of a device in one roundtrip.

    attrs maps attribute names to their default values. If dev_attr_list is
    given, setDevAttrList is executed within the same roundtrip.
    Returns {"init_done": int, "attr": {attribute: value}}.
    """
    name_esc = escapeValue(name)
    attr_vals = ",".join(
        f"'{escapeValue(attr)}'=>AttrVal('{name_esc}','{escapeValue(attr)}',"
        f"'{escapeValue(str(default))}')"
        for attr, default in attrs.items()
    )
    cmd = ""
    if dev_attr_list is not None:
        # needs to be the first command, BindingsIo adds the IODev list to it
        cmd = _setDevAttrListCmd(name, dev_attr_list) + ";;"
    cmd += "to_json({init_done=>$init_done,attr=>{" + attr_vals + "}})"

    info = {"init_done": 0, "attr": {attr: str(d) for attr, d in attrs.items()}}
    res = await sendCommandName(name, cmd)
    try:
        reply = json_loads(res)
        info["init_done"] = int(reply["init_done"])
        for attr, value in reply["attr"].items():
            if attr in info["attr"] and value is not None:
                info["attr"][attr] = str(value)
    except Exception:
        logger.error(f"{name}: failed to get attribute values from FHEM")
    return info


def _get_update_lock(name):
    lock = update_locks.get(name)
    if lock is None:
        lock = update_locks[name] = asyncio.Lock()
    owner = update_lock_owners.get(name)
    if (
        lock.locked()
        and owner is not None
        and (owner is asyncio.current_task() or owner.done())
    ):
        # readingsBeginUpdate without readingsEndUpdate, usually caused by an
        # exception in the module between both calls. Waiting for the lock
        # would block all readings updates of this device for 120s.
        logger.debug(f"{name}: dropping unfinished readingsBeginUpdate")
        update_lock_owners.pop(name, None)
        bulk_updates.pop(name, None)
        lock.release()
    return lock


async def readingsBeginUpdate(hash):
    lock = _get_update_lock(hash["NAME"])
    try:
        await asyncio.wait_for(lock.acquire(), 120)
    except asyncio.TimeoutError:
        logger.error(
            f"{hash['NAME']}: readingsBeginUpdate couldn't acquire lock,"
            + " caused by readingsBeginUpdate without End or Single update inbetween"
        )
    update_lock_owners[hash["NAME"]] = asyncio.current_task()
    bulk_updates[hash["NAME"]] = [
        "readingsBeginUpdate($defs{'" + escapeValue(hash["NAME"]) + "'});;"
    ]


async def readingsBulkUpdateIfChanged(hash, reading, value):
    try:
        value = convertValue(value)
        cmd = (
            "readingsBulkUpdateIfChanged($defs{'"
            + escapeValue(hash["NAME"])
            + "'},'"
            + escapeValue(reading)
            + "','"
            + escapeValue(value)
            + "');;"
        )
        if hash["NAME"] not in bulk_updates:
            logger.error(
                f"{hash['NAME']}: readingsBulkUpdateIfChanged of reading {reading} "
                + "without readingsBeginUpdate"
            )
            return
        bulk_updates[hash["NAME"]].append(cmd)
    except Exception:
        logger.exception("Failed to do readingsBulkUpdateIfChanged")


async def readingsBulkUpdate(hash, reading, value, changed=None):
    try:
        value = convertValue(value)
        if changed is None:
            cmd = (
                "readingsBulkUpdate($defs{'"
                + escapeValue(hash["NAME"])
                + "'},'"
                + escapeValue(reading)
                + "','"
                + escapeValue(value)
                + "');;"
            )
        else:
            cmd = (
                "readingsBulkUpdate($defs{'"
                + escapeValue(hash["NAME"])
                + "'},'"
                + escapeValue(reading)
                + "','"
                + escapeValue(value)
                + "', "
                + str(changed)
                + ");;"
            )
        if hash["NAME"] not in bulk_updates:
            logger.error(
                f"{hash['NAME']}: readingsBulkUpdate of reading {reading} "
                + "without readingsBeginUpdate"
            )
            return
        bulk_updates[hash["NAME"]].append(cmd)
    except Exception:
        logger.exception("Failed to do readingsBulkUpdate")


async def readingsEndUpdate(hash, do_trigger):
    if hash["NAME"] not in bulk_updates:
        logger.error(f"{hash['NAME']}: readingsEndUpdate without readingsBeginUpdate")
        return None
    cmds = bulk_updates.pop(hash["NAME"])
    cmds.append(
        "readingsEndUpdate($defs{'"
        + escapeValue(hash["NAME"])
        + "'},"
        + str(do_trigger)
        + ");;"
    )
    try:
        return await sendCommandHash(hash, "".join(cmds))
    finally:
        update_lock_owners.pop(hash["NAME"], None)
        lock = update_locks.get(hash["NAME"])
        if lock is not None and lock.locked():
            lock.release()


async def readingsSingleUpdate(hash, reading, value, do_trigger):
    async with _get_update_lock(hash["NAME"]):
        value = convertValue(value)
        cmd = (
            "readingsSingleUpdate($defs{'"
            + escapeValue(hash["NAME"])
            + "'},'"
            + escapeValue(reading)
            + "','"
            + escapeValue(value)
            + "',"
            + str(do_trigger)
            + ")"
        )
        return await sendCommandHash(hash, cmd)


async def readingsSingleUpdateIfChanged(hash, reading, value, do_trigger):
    async with _get_update_lock(hash["NAME"]):
        value = convertValue(value)
        cmd = (
            "readingsBeginUpdate($defs{'"
            + escapeValue(hash["NAME"])
            + "'});;readingsBulkUpdateIfChanged($defs{'"
            + escapeValue(hash["NAME"])
            + "'},'"
            + escapeValue(reading)
            + "','"
            + escapeValue(value)
            + "');;readingsEndUpdate($defs{'"
            + escapeValue(hash["NAME"])
            + "'},"
            + str(do_trigger)
            + ");;"
        )
        return await sendCommandHash(hash, cmd)


async def CommandDefine(hash, definition: str):
    cmd = f"CommandDefine(undef, {perlString(definition)})"
    ret = await sendCommandHash(hash, cmd)
    if ret is not None:
        return ret

    pos_fhempy = definition.find(" fhempy ")
    if pos_fhempy == -1:
        pos_fhempy = definition.find(" PythonModule ")
    if pos_fhempy > 0:
        devname = definition.split(" ")[0]
        iodev = await AttrVal(hash["NAME"], "IODev", "")
        if iodev != "":
            await CommandAttr(hash, f"{devname} IODev {iodev}")

        fhempytype = definition.split(" ")[2]
        await CommandAttr(hash, f"{devname} group {fhempytype}")

        room = await AttrVal(hash["NAME"], "room", "")
        if room != "":
            await CommandAttr(hash, f"{devname} room fhempy")


async def CommandList(hash, listcmd):
    cmd = f"CommandList(undef, {perlString(listcmd)})"
    return await sendCommandHash(hash, cmd)


async def CommandAttr(hash, attrdef):
    cmd = f"CommandAttr(undef, {perlString(attrdef)})"
    return await sendCommandHash(hash, cmd)


async def CommandDeleteAttr(hash, deldef):
    cmd = f"CommandDeleteAttr(undef, {perlString(deldef)})"
    return await sendCommandHash(hash, cmd)


async def CommandDeleteReading(hash, deldef):
    cmd = f"CommandDeleteReading(undef, {perlString(deldef)})"
    return await sendCommandHash(hash, cmd)


async def FW_runJavascript(hash, javascript, detail=None):
    """Runs javascript in the open FHEMWEB pages, only on the detail page of
    the device `detail` if given."""
    pagefilter = f"'FILTER=' . {perlString(detail)}, " if detail else ""
    cmd = (
        "if(defined(&FW_directNotify)) { "
        'foreach my $fw (devspec2array("TYPE=FHEMWEB:FILTER=TEMPORARY!=1")) { '
        f'FW_directNotify({pagefilter}"#FHEMWEB:$fw", '
        f'{perlString(javascript)}, ""); }} }} ""'
    )
    return await sendCommandHash(hash, cmd)


async def setEventDevices(hash, devices):
    """FHEM sends the events of these devices to fhempy, they are passed to
    the callbacks registered with register_event_listener.
    Returns False if the FHEM modules are too old (update all needed)."""
    devspec = ",".join(devices)
    cmd = (
        "defined(&fhempy_setEventDevices) ? "
        f"(fhempy_setEventDevices({perlString(hash['NAME'])}, {perlString(devspec)})"
        " // 'ok') : 'old'"
    )
    return await sendCommandHash(hash, cmd) != "old"


def register_event_listener(device, callback):
    """callback(device, reading, value) is awaited for every event of device,
    events without reading name (e.g. "on") are passed as reading state.
    Keep it short, it runs in the loop which receives the messages from FHEM."""
    event_listeners.setdefault(device, []).append(callback)


def unregister_event_listener(device, callback):
    callbacks = event_listeners.get(device, [])
    if callback in callbacks:
        callbacks.remove(callback)
    if not callbacks:
        event_listeners.pop(device, None)


async def dispatch_event(device, event):
    parts = event.split(": ", 1)
    if len(parts) > 1:
        reading, value = parts
    else:
        reading, value = "state", parts[0]
    for callback in list(event_listeners.get(device, [])):
        try:
            await callback(device, reading, value)
        except Exception:
            logger.exception(f"Failed to handle event of {device}: {event}")


async def setEventRecorder(hash, enable, skip=""):
    """FHEM sends the events of all devices to fhempy, collected once per
    second, they are passed to the callback registered with
    register_recorder_listener. Events matching the regexp skip
    ("device:reading: value") are only counted.
    Returns "ok", "old" if the FHEM modules are too old (update all needed)
    or an error message."""
    cmd = (
        "defined(&fhempy_setEventRecorder) ? "
        f"(fhempy_setEventRecorder({perlString(hash['NAME'])}, "
        f"{1 if enable else 0}, {perlString(skip)}) // 'ok') : 'old'"
    )
    return await sendCommandHash(hash, cmd)


def register_recorder_listener(device, callback):
    """callback(events, skipped) is awaited for each batch of events of the
    recorder device: events is a list of (time, device, reading, value),
    skipped maps device names to the number of skipped events."""
    recorder_listeners[device] = callback


def unregister_recorder_listener(device, callback):
    if recorder_listeners.get(device) == callback:
        del recorder_listeners[device]


async def dispatch_recorded_events(device, args):
    callback = recorder_listeners.get(device)
    if callback is None or not args:
        return
    events = []
    for entry in args[0] or []:
        try:
            timestamp, name, event = entry
            parts = event.split(": ", 1)
            if len(parts) > 1:
                reading, value = parts
            else:
                reading, value = "state", parts[0]
            events.append((float(timestamp), name, reading, value))
        except (TypeError, ValueError):
            logger.debug(f"Invalid recorded event: {entry}")
    skipped = args[1] if len(args) > 1 and isinstance(args[1], dict) else {}
    try:
        await callback(events, skipped)
    except Exception:
        logger.exception(f"Failed to handle recorded events of {device}")


async def checkIfDeviceExists(hash, typeinternal, typevalue, internal, value):
    cmd = (
        "foreach my $fhem_dev (sort keys %main::defs) {"
        + "  return 1 if("
        + _perlDeviceMatch(typeinternal, typevalue, internal, value)
        + ");;"
        + "}"
        + "return 0;;"
    )
    return await sendCommandHash(hash, cmd)


def _perlDeviceMatch(typeinternal, typevalue, internal, value):
    dev = "$main::defs{$fhem_dev}"
    return (
        f"defined({dev}{{{perlString(typeinternal)}}})"
        f" && {dev}{{{perlString(typeinternal)}}} eq {perlString(typevalue)}"
        f" && defined({dev}{{{perlString(internal)}}})"
        f" && {dev}{{{perlString(internal)}}} eq {perlString(value)}"
    )


# UTILS FUNCTIONS TO SEND COMMAND TO FHEM
def escapeValue(value):
    # escape value for a single quoted perl string
    return value.replace("\\", "\\\\").replace("'", "\\'")


def perlString(value):
    # single quoted perl string literal, perl doesn't interpolate its content
    return "'" + escapeValue(str(value)) + "'"


def convertValue(value):
    if value is None:
        value = ""
    if value is True:
        value = 1
    if value is False:
        value = 0
    if isinstance(value, datetime):
        value = value.strftime("%Y-%m-%d %H:%M:%S")

    return str(value)


async def _send_version_message(**fields):
    msg = json_dumps({"msgtype": "version", **fields})
    logger.debug("<<< WS: " + msg)
    await wsconnection.send(msg)


async def check_update():
    """Refresh release readings once, without installing or blocking FHEM."""
    if release_check_lock.locked():
        return
    async with release_check_lock:
        await _send_version_message(update_check="checking")
        try:
            versions = await updates.get_versions(__version__)
        except Exception as error:
            logger.error("Failed to check fhempy updates: %s", error)
            # Preserve the last successful version information on network errors.
            reason = str(error) or type(error).__name__
            await _send_version_message(update_check=f"failed: {reason}")
            return
        await _send_version_message(
            version_available=versions[0],
            version_options=",".join(versions),
            update_check="ok",
            version_release_notes=(
                '<html><a href="https://github.com/fhempy/fhempy/releases" target="_blank">'
                "Release Notes</a></html>"
            ),
        )


async def send_latest_release():
    while True:
        try:
            await check_update()
        except Exception:
            logger.exception("Failed to update latest release infos")
        await asyncio.sleep(updates.CHECK_INTERVAL)


async def send_version():
    msg = {
        "version": __version__,
        "update_version_supported": 1,
        "install_peer_supported": 1,
        "python": platform.python_version(),
        "os": os.name,
        "system": platform.system(),
        "release": platform.release(),
        "hostname": socket.gethostname(),
    }
    await _send_version_message(**msg)


async def send_default_response(hash, set_default_response):
    msg = {
        "msgtype": "set_update",
        "NAME": hash["NAME"],
        "set_default_response": set_default_response,
    }
    msg = json_dumps(msg)
    logger.debug("<<< WS: " + msg)
    global wsconnection
    await wsconnection.send(msg)


def describeCommand(cmd):
    """Short command description for error logs, the full command can contain
    reading values like tokens and is only logged on debug level."""
    return cmd.split("(", 1)[0].split(" ", 1)[0][:50]


async def send_and_wait(name, cmd):
    fut = asyncio.get_running_loop().create_future()
    msg = {
        "awaitId": next(await_ids),
        "NAME": name,
        "msgtype": "command",
        "command": cmd,
    }
    sent_time = time.time()

    def listener(rmsg):
        if rmsg is None:
            if not fut.done():
                fut.set_exception(ConnectionError("FHEM connection closed"))
            return
        try:
            recv_time = time.time()
            fhem_time = (recv_time - sent_time) * 1000
            if fhem_time > 5000:
                # log error message if fhem took too long to handle cmd
                logger.error(
                    f"FHEM took {fhem_time:.0f}ms for {describeCommand(cmd)} "
                    + f"of {name}"
                )
                logger.debug(f"Slow command: {cmd}")
            logger.debug(f">>> {rmsg['awaitId']:08d} {fhem_time:.2f}ms: {rmsg}")
            fut.set_result(rmsg)
        except Exception:
            logger.error(f"Failed to set result, received: {rmsg}")

    connection = wsconnection
    if connection.is_closed():
        raise ConnectionError("FHEM connection closed")
    connection.register_msg_listener(listener, msg["awaitId"])
    logger.debug(f"<<< {msg['awaitId']:08d}: {msg}")
    try:
        try:
            await connection.send(json_dumps(msg))
        except websockets.exceptions.ConnectionClosed:
            fut.set_exception(ConnectionError("FHEM connection closed"))
        except Exception as e:
            logger.exception(f"Failed to send message via websocket: {e}")
            fut.set_exception(Exception("Failed to send message via websocket"))

        return await fut
    finally:
        # also cleans up when the reply didn't arrive in time
        connection.unregister_msg_listener(msg["awaitId"])


async def sendCommandName(name, cmd, hash=None):
    ret = ""
    timeout = 180
    try:
        start = time.time()
        await waitForFunction(name)
        end = time.time()
        duration = end - start
        if duration > 5:
            logger.error(
                f"{name}: waited {duration:.0f}s for FHEM before sending "
                + describeCommand(cmd)
            )
        # wait max 180s for reply from FHEM
        jsonmsg = await asyncio.wait_for(send_and_wait(name, cmd), timeout)
        ret = jsonmsg["result"]
    except asyncio.TimeoutError:
        logger.error(
            f"{name}: no response from FHEM since {timeout}s for "
            + describeCommand(cmd)
        )
        logger.debug(f"Command without response: {cmd}")
        ret = ""
    except ConnectionError:
        # the closed connection itself is logged by the binding
        logger.debug("FHEM connection closed, command not sent")
        ret = ""
    except Exception as e:
        logger.exception(f"Exception while waiting for reply: {e}")
        ret = str(e)

    return ret


async def sendCommandHash(hash, cmd):
    return await sendCommandName(hash["NAME"], cmd, hash)
