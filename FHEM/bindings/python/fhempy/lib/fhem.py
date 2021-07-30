import asyncio
import concurrent.futures
import json
import logging
import random
import traceback

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


async def readingsBulkUpdate(hash, reading, value, changed=None):
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


async def CommandDefine(hash, definition):
    cmd = 'CommandDefine(undef, "' + definition + '")'
    ret = await sendCommandHash(hash, cmd)
    if ret is not None:
        return ret

    iodev = await AttrVal(hash["NAME"], "IODev", "")
    if iodev != "":
        await CommandAttr(hash, f"{definition.split(' ')[0]} IODev {iodev}")


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

    return str(value)


async def send_version():
    msg = {
        "msgtype": "version",
        "version": __version__,
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

    def listener(rmsg):
        try:
            fut.set_result(rmsg)
        except Exception:
            logger.error("Failed to set result, received: " + rmsg)

    global wsconnection
    wsconnection.registerMsgListener(listener, msg["awaitId"])
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
    try:
        logger.debug("sendCommandName START")
        while len(function_active) != 0:
            if function_active[-1] == name:
                break
            await asyncio.sleep(0.001)
        # wait max 1s for reply from FHEM
        jsonmsg = await asyncio.wait_for(send_and_wait(name, cmd), 15)
        logger.debug("sendCommandName END")
        ret = json.loads(jsonmsg)["result"]
    except asyncio.TimeoutError:
        logger.error("Timeout - NO RESPONSE for command: " + cmd)
        ret = ""
    except concurrent.futures.CancelledError:
        # function timeout
        pass
    except Exception as e:
        logger.error("Exception while waiting for reply: " + e)
        traceback.format_exc()
        ret = str(e)

    return ret


async def sendCommandHash(hash, cmd):
    return await sendCommandName(hash["NAME"], cmd, hash)
