
import json
import random
import asyncio
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def updateConnection(ws):
    global wsconnection
    wsconnection = ws

async def ReadingsVal(name, reading, default):
    cmd = "ReadingsVal('" + name + "', '" + reading + "', '" + default + "')"
    return await sendCommandName(name, cmd)

async def readingsBeginUpdate(hash):
    cmd = "readingsBeginUpdate($defs{'" + hash["NAME"] + "'})"
    return await sendCommandHash(hash, cmd)

async def readingsBulkUpdateIfChanged(hash, reading, value):
    value = convertValue(value)
    cmd = "readingsBulkUpdateIfChanged($defs{'" + hash["NAME"] + "'},'" + \
        reading + "','" + value.replace("'", "\\'") + "')"
    return await sendCommandHash(hash, cmd)

async def readingsEndUpdate(hash, do_trigger):
    cmd = "readingsEndUpdate($defs{'" + hash["NAME"] + "'}," + str(do_trigger) + ")"
    return await sendCommandHash(hash, cmd)

async def readingsSingleUpdate(hash, reading, value, do_trigger):
    value = convertValue(value)
    cmd = "readingsSingleUpdate($defs{'" + hash["NAME"] + "'},'" + \
        reading + "','" + value.replace("'", "\\'") + "'," + str(do_trigger) + ")"
    return await sendCommandHash(hash, cmd)

async def readingsSingleUpdateIfChanged(hash, reading, value, do_trigger):
    value = convertValue(value)
    cmd = "readingsBeginUpdate($defs{'" + hash["NAME"] + "'});;readingsBulkUpdateIfChanged($defs{'" + hash["NAME"] + "'},'" + \
        reading + "','" + value.replace("'", "\\'") + \
        "');;readingsEndUpdate($defs{'" + \
        hash["NAME"] + "'}," + str(do_trigger) + ");;"
    return await sendCommandHash(hash, cmd)

async def CommandDefine(hash, definition):
    cmd = "CommandDefine(undef, \"" + definition + "\")"
    return await sendCommandHash(hash, cmd)

async def checkIfDeviceExists(hash, typeinternal, typevalue, internal, value):
    cmd = "foreach my $fhem_dev (sort keys %main::defs) {" + \
        "  return 1 if($main::defs{$fhem_dev}{" + typeinternal + "} eq '" + typevalue + "' && $main::defs{$fhem_dev}{" + internal + "} eq '" + value + "');;" + \
        "}" + \
        "return 0;;"
    return await sendCommandHash(hash, cmd)

# UTILS FUNCTIONS TO SEND COMMAND TO FHEM
def convertValue(value):
    if (value == None):
        value = ""
    if (value == True):
        value = 1
    if (value == False):
        value = 0

    return str(value)


def send_and_wait(name, cmd):
    future = asyncio.get_event_loop().create_future()

    msg = {
        "awaitId": random.randint(10000000, 99999999),
        "NAME": name,
        "msgtype": "command",
        "command": cmd
    }

    def listener(rmsg):
        logger.debug("RECEIVED awaitid")
        future.set_result(rmsg)

    wsconnection.msg_listeners.append(
        {"func": listener, "awaitId": msg['awaitId']})
    msg = json.dumps(msg)
    logger.debug("<<< WS: " + msg)
    try:
        wsconnection.sendMessage(msg.encode("utf-8"))
    except Exception as e:
        logger.error("Failed to send message via websocket: " + e)
        future.set_exception(Exception("Failed to send message via web"))

    return future


async def sendCommandName(name, cmd):
    try:
        res = await asyncio.wait_for(send_and_wait(name, cmd), 3)
        return json.loads(res)['result']
    except Exception as e:
        return str(e)

async def sendCommandHash(hash, cmd):
    return await sendCommandName(hash["NAME"], cmd)

