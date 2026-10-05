import asyncio
import itertools
import json
import logging
import os
import platform
import socket
import time
from datetime import datetime

import aiohttp
import websockets

from .version import __version__

logger = logging.getLogger(__name__)

function_active = []
# futures of commands waiting for a change of function_active
function_waiters = []
update_locks = {}
# readings commands collected between readingsBeginUpdate and readingsEndUpdate,
# they are sent to FHEM in one roundtrip on readingsEndUpdate
bulk_updates = {}
wsconnection = None
# ids to match FHEM replies to commands sent by fhempy
await_ids = itertools.count(1)

# TODO use run_coroutine_threadsafe if asyncio.get_event_loop() == None
# this would make all functions threadsafe


def updateConnection(ws):
    global wsconnection
    wsconnection = ws


def setFunctionActive(hash):
    function_active.append(hash["NAME"])
    notifyFunctionWaiters()


def setFunctionInactive(hash):
    element = function_active.pop()
    if element != hash["NAME"]:
        logger.error(
            f"Set wrong function inactive, tried {hash['NAME']}, "
            f"current function_active: {function_active},{element}"
        )
    notifyFunctionWaiters()


def notifyFunctionWaiters():
    for waiter in function_waiters:
        if not waiter.done():
            waiter.set_result(None)
    function_waiters.clear()


async def waitForFunction(name):
    # while FHEM waits for a function reply, it only handles
    # commands of the device which called the function
    while len(function_active) != 0 and function_active[-1] != name:
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
        + "  return $main::defs($fhem_dev}{NAME}) if(defined($main::defs{$fhem_dev}{"
        + typeinternal
        + "}) && $main::defs{$fhem_dev}{"
        + typeinternal
        + "} eq '"
        + typevalue
        + "' && $main::defs{$fhem_dev}{"
        + internal
        + "} eq '"
        + value
        + "');;"
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
    cmd = "ReadingsVal('" + name + "', '" + reading + "', '" + default + "')"
    return await sendCommandName(name, cmd)


async def AttrVal(name, attr, default):
    cmd = "AttrVal('" + name + "', '" + attr + "', '" + default + "')"
    return await sendCommandName(name, cmd)


async def InternalVal(name, internal, default):
    cmd = "InternalVal('" + name + "', '" + internal + "', '" + default + "')"
    return await sendCommandName(name, cmd)


async def addToDevAttrList(name, attr_list):
    cmd = "addToDevAttrList('" + name + "', '" + attr_list + "')"
    return await sendCommandName(name, cmd)


async def setDevAttrList(name, attr_list):
    attr_list += " IODev disable:0,1"
    cmd = "setDevAttrList('" + name + "', '" + attr_list + " '.$readingFnAttributes)"
    return await sendCommandName(name, cmd)


async def readingsBeginUpdate(hash):
    if hash["NAME"] not in update_locks:
        update_locks[hash["NAME"]] = asyncio.Lock()
    try:
        await asyncio.wait_for(update_locks[hash["NAME"]].acquire(), 120)
    except asyncio.TimeoutError:
        logging.error(
            f"{hash['NAME']}: readingsBeginUpdate couldn't acquire lock,"
            + " caused by readingsBeginUpdate without End or Single update inbetween"
        )
    bulk_updates[hash["NAME"]] = [
        "readingsBeginUpdate($defs{'" + hash["NAME"] + "'});;"
    ]


async def readingsBulkUpdateIfChanged(hash, reading, value):
    try:
        value = convertValue(value)
        cmd = (
            "readingsBulkUpdateIfChanged($defs{'"
            + hash["NAME"]
            + "'},'"
            + reading
            + "','"
            + escapeValue(value)
            + "');;"
        )
        if hash["NAME"] not in update_locks or not update_locks[hash["NAME"]].locked():
            logging.error(
                f"{hash['NAME']}: readingsBulkUpdateIfChanged without "
                + f"readingsBeginUpdate: {cmd}"
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
                + hash["NAME"]
                + "'},'"
                + reading
                + "','"
                + escapeValue(value)
                + "');;"
            )
        else:
            cmd = (
                "readingsBulkUpdate($defs{'"
                + hash["NAME"]
                + "'},'"
                + reading
                + "','"
                + escapeValue(value)
                + "', "
                + str(changed)
                + ");;"
            )
        if hash["NAME"] not in update_locks or not update_locks[hash["NAME"]].locked():
            logging.error(
                f"{hash['NAME']}: readingsBulkUpdate without "
                + f"readingsBeginUpdate: {cmd}"
            )
            return
        bulk_updates[hash["NAME"]].append(cmd)
    except Exception:
        logger.exception("Failed to do readingsBulkUpdate")


async def readingsEndUpdate(hash, do_trigger):
    if hash["NAME"] not in update_locks:
        logger.error("readingsEndUpdate without active readingsBeginUpdate")
    cmds = bulk_updates.pop(hash["NAME"], [])
    cmds.append(
        "readingsEndUpdate($defs{'" + hash["NAME"] + "'}," + str(do_trigger) + ");;"
    )
    try:
        return await sendCommandHash(hash, "".join(cmds))
    finally:
        update_locks[hash["NAME"]].release()


async def readingsSingleUpdate(hash, reading, value, do_trigger):
    if hash["NAME"] not in update_locks:
        update_locks[hash["NAME"]] = asyncio.Lock()
    async with update_locks[hash["NAME"]]:
        value = convertValue(value)
        cmd = (
            "readingsSingleUpdate($defs{'"
            + hash["NAME"]
            + "'},'"
            + reading
            + "','"
            + escapeValue(value)
            + "',"
            + str(do_trigger)
            + ")"
        )
        return await sendCommandHash(hash, cmd)


async def readingsSingleUpdateIfChanged(hash, reading, value, do_trigger):
    if hash["NAME"] not in update_locks:
        update_locks[hash["NAME"]] = asyncio.Lock()
    async with update_locks[hash["NAME"]]:
        value = convertValue(value)
        cmd = (
            "readingsBeginUpdate($defs{'"
            + hash["NAME"]
            + "'});;readingsBulkUpdateIfChanged($defs{'"
            + hash["NAME"]
            + "'},'"
            + reading
            + "','"
            + escapeValue(value)
            + "');;readingsEndUpdate($defs{'"
            + hash["NAME"]
            + "'},"
            + str(do_trigger)
            + ");;"
        )
        return await sendCommandHash(hash, cmd)


async def CommandDefine(hash, definition: str):
    cmd = 'CommandDefine(undef, "' + definition + '")'
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
    cmd = 'CommandList(undef, "' + listcmd + '")'
    return await sendCommandHash(hash, cmd)


async def CommandAttr(hash, attrdef):
    cmd = 'CommandAttr(undef, "' + attrdef.replace('"', '\\"') + '")'
    return await sendCommandHash(hash, cmd)


async def CommandDeleteAttr(hash, deldef):
    cmd = 'CommandDeleteAttr(undef, "' + deldef + '")'
    return await sendCommandHash(hash, cmd)


async def CommandDeleteReading(hash, deldef):
    cmd = 'CommandDeleteReading(undef, "' + deldef + '")'
    return await sendCommandHash(hash, cmd)


async def checkIfDeviceExists(hash, typeinternal, typevalue, internal, value):
    cmd = (
        "foreach my $fhem_dev (sort keys %main::defs) {"
        + "  return 1 if(defined($main::defs{$fhem_dev}{"
        + typeinternal
        + "}) && $main::defs{$fhem_dev}{"
        + typeinternal
        + "} eq '"
        + typevalue
        + "' && defined($main::defs{$fhem_dev}{"
        + internal
        + "}) && $main::defs{$fhem_dev}{"
        + internal
        + "} eq '"
        + value
        + "');;"
        + "}"
        + "return 0;;"
    )
    return await sendCommandHash(hash, cmd)


# UTILS FUNCTIONS TO SEND COMMAND TO FHEM
def escapeValue(value):
    # escape value for a single quoted perl string
    return value.replace("\\", "\\\\").replace("'", "\\'")


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


async def get_github_data():
    res_json = {}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.github.com/repos/fhempy/fhempy/releases/latest"
            ) as resp:
                res_json = await resp.json()
    except Exception:
        logger.exception("Failed to get github fhempy data")
    return res_json


async def send_latest_release():
    while True:
        try:
            github_data = await get_github_data()
            try:
                latest_version = github_data["name"][1:]
            except Exception:
                latest_version = "unknown"

            msg = {
                "msgtype": "version",
                "version_available": latest_version,
                "version_release_notes": (
                    '<html><a href="https://github.com/fhempy/fhempy/releases" target="_blank">'
                    "Release Notes</a></html>"
                ),
            }
            msg = json.dumps(msg, ensure_ascii=False)
            logger.debug("<<< WS: " + msg)
            global wsconnection
            await wsconnection.send(msg)
        except Exception:
            logger.exception("Failed to update latest release infos")
        await asyncio.sleep(3600 * 12)


async def send_version():
    msg = {
        "msgtype": "version",
        "version": __version__,
        "python": platform.python_version(),
        "os": os.name,
        "system": platform.system(),
        "release": platform.release(),
        "hostname": socket.gethostname(),
    }
    msg = json.dumps(msg, ensure_ascii=False)
    logger.debug("<<< WS: " + msg)
    global wsconnection
    await wsconnection.send(msg)


async def send_default_response(hash, set_default_response):
    msg = {
        "msgtype": "set_update",
        "NAME": hash["NAME"],
        "set_default_response": set_default_response,
    }
    msg = json.dumps(msg, ensure_ascii=False)
    logger.debug("<<< WS: " + msg)
    global wsconnection
    await wsconnection.send(msg)


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
                logger.error(f"FHEM took {fhem_time:.0f}ms for {cmd}")
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
            await connection.send(json.dumps(msg, ensure_ascii=False))
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
            logger.error(f"sendCommandName took {duration}s to send: {cmd}")
        # wait max 180s for reply from FHEM
        jsonmsg = await asyncio.wait_for(send_and_wait(name, cmd), timeout)
        ret = jsonmsg["result"]
    except asyncio.TimeoutError:
        logger.error(f"NO RESPONSE since {timeout}s: " + cmd)
        ret = ""
    except ConnectionError:
        logger.error(f"FHEM connection closed, can't send: {cmd}")
        ret = ""
    except Exception as e:
        logger.exception(f"Exception while waiting for reply: {e}")
        ret = str(e)

    return ret


async def sendCommandHash(hash, cmd):
    return await sendCommandName(hash["NAME"], cmd, hash)
