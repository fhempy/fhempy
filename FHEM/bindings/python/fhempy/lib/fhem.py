import asyncio
import json
import logging
import os
import platform
import random
import socket
import time
import traceback
from datetime import datetime

import aiohttp
import websockets

from .version import __version__

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

function_active = []
update_locks = {}
wsconnection = None

# TODO use run_coroutine_threadsafe if asyncio.get_event_loop() == None
# this would make all functions threadsafe


def updateConnection(ws):
    global wsconnection
    wsconnection = ws


def setFunctionActive(hash):
    function_active.append(hash["NAME"])


def setFunctionInactive(hash):
    element = function_active.pop()
    if element != hash["NAME"]:
        logger.error(
            f"Set wrong function inactive, tried {hash['NAME']}, "
            f"current function_active: {function_active},{element}"
        )


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
    return await sendCommandHash(hash, cmd)


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
    attr_list += " IODev"
    cmd = "setDevAttrList('" + name + "', '" + attr_list + " '.$readingFnAttributes)"
    return await sendCommandName(name, cmd)


async def readingsBeginUpdate(hash):
    if hash["NAME"] not in update_locks:
        update_locks[hash["NAME"]] = asyncio.Lock()
    await update_locks[hash["NAME"]].acquire()
    cmd = "readingsBeginUpdate($defs{'" + hash["NAME"] + "'});;"
    return await sendCommandHash(hash, cmd)


async def readingsBulkUpdateIfChanged(hash, reading, value):
    try:
        value = convertValue(value)
        cmd = (
            "readingsBulkUpdateIfChanged($defs{'"
            + hash["NAME"]
            + "'},'"
            + reading
            + "','"
            + value.replace("'", "\\'")
            + "');;"
        )
        return await sendCommandHash(hash, cmd)
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
                + value.replace("'", "\\'")
                + "');;"
            )
        else:
            cmd = (
                "readingsBulkUpdate($defs{'"
                + hash["NAME"]
                + "'},'"
                + reading
                + "','"
                + value.replace("'", "\\'")
                + "', "
                + str(changed)
                + ");;"
            )
        return await sendCommandHash(hash, cmd)
    except Exception:
        logger.exception("Failed to do readingsBulkUpdate")


async def readingsEndUpdate(hash, do_trigger):
    cmd = "readingsEndUpdate($defs{'" + hash["NAME"] + "'}," + str(do_trigger) + ");;"
    res = await sendCommandHash(hash, cmd)
    update_locks[hash["NAME"]].release()
    return res


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
            + value.replace("'", "\\'")
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
            + value.replace("'", "\\'")
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


async def CommandAttr(hash, attrdef):
    cmd = 'CommandAttr(undef, "' + attrdef.replace('"', '\\"') + '")'
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
        + "' && $main::defs{$fhem_dev}{"
        + internal
        + "} eq '"
        + value
        + "');;"
        + "}"
        + "return 0;;"
    )
    return await sendCommandHash(hash, cmd)


# UTILS FUNCTIONS TO SEND COMMAND TO FHEM
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
            msg = {
                "msgtype": "version",
                "version_available": github_data["name"][1:],
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


async def send_and_wait(name, cmd):
    fut = asyncio.get_running_loop().create_future()
    msg = {
        "awaitId": random.randint(10000000, 99999999),
        "NAME": name,
        "msgtype": "command",
        "command": cmd,
    }
    sent_time = time.time()

    def listener(rmsg):
        try:
            recv_time = time.time()
            fhem_time = (recv_time - sent_time) * 1000
            if fhem_time > 20000:
                # log error message if fhem took too long to handle cmd
                logger.error(f"FHEM took {fhem_time:.0f}ms for {cmd}")
            fut.set_result(rmsg)
        except Exception:
            logger.error("Failed to set result, received: " + rmsg)

    global wsconnection
    wsconnection.register_msg_listener(listener, msg["awaitId"])
    msg = json.dumps(msg, ensure_ascii=False)
    logger.debug("<<< WS: " + msg)
    try:
        await wsconnection.send(msg)
        logger.debug("message sent successfully")
    except websockets.exceptions.ConnectionClosed:
        logger.error("Connection closed, can't send message.")
    except Exception as e:
        logger.error("Failed to send message via websocket: " + e)
        fut.set_exception(Exception("Failed to send message via websocket"))

    return await fut


async def sendCommandName(name, cmd, hash=None):
    ret = ""
    timeout = 60
    try:
        logger.debug("sendCommandName START")
        start = time.time()
        while len(function_active) != 0:
            if function_active[-1] == name:
                break
            await asyncio.sleep(0.1)
        end = time.time()
        duration = end - start
        if duration > 5:
            logger.error(f"sendCommandName took {duration}s to send: {cmd}")
        # wait max 60s for reply from FHEM
        jsonmsg = await asyncio.wait_for(send_and_wait(name, cmd), timeout)
        logger.debug("sendCommandName END")
        ret = json.loads(jsonmsg)["result"]
    except asyncio.TimeoutError:
        logger.error(f"NO RESPONSE since {timeout}s: " + cmd)
        ret = ""
    except asyncio.CancelledError:
        # task was cancelled
        pass
    except Exception as e:
        logger.error("Exception while waiting for reply: " + e)
        traceback.format_exc()
        ret = str(e)

    return ret


async def sendCommandHash(hash, cmd):
    return await sendCommandName(hash["NAME"], cmd, hash)
