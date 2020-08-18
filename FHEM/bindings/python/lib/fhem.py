
import json
import random
import asyncio
import logging
import traceback
import concurrent.futures
import websockets

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

function_active = []

def updateConnection(ws):
    global wsconnection
    wsconnection = ws

def setFunctionActive(hash):
    function_active.append(hash["NAME"])

def setFunctionInactive(hash):
    name = hash["NAME"]
    element = function_active.pop()
    if element != hash["NAME"]:
        logger.error(f"Set wrong function inactive, tried {hash['NAME']}, current function_active: {function_active},{element}")

async def ReadingsVal(name, reading, default):
    cmd = "ReadingsVal('" + name + "', '" + reading + "', '" + default + "')"
    return await sendCommandName(name, cmd)

async def readingsBeginUpdate(hash):
    cmd = "readingsBeginUpdate($defs{'" + hash["NAME"] + "'});;"
    return await sendCommandHash(hash, cmd)

async def readingsBulkUpdateIfChanged(hash, reading, value):
    value = convertValue(value)
    cmd = "readingsBulkUpdateIfChanged($defs{'" + hash["NAME"] + "'},'" + \
        reading + "','" + value.replace("'", "\\'") + "');;"
    return await sendCommandHash(hash, cmd)

async def readingsEndUpdate(hash, do_trigger):
    cmd = "readingsEndUpdate($defs{'" + hash["NAME"] + "'}," + str(do_trigger) + ");;"
    return await sendCommandHash(hash,cmd)

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
        "  return 1 if(defined($main::defs{$fhem_dev}{" + typeinternal + "}) && $main::defs{$fhem_dev}{" + typeinternal + "} eq '" + typevalue + "' && $main::defs{$fhem_dev}{" + internal + "} eq '" + value + "');;" + \
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


async def send_and_wait(name, cmd):
    fut = asyncio.get_running_loop().create_future()
    msg = {
        "awaitId": random.randint(10000000, 99999999),
        "NAME": name,
        "msgtype": "command",
        "command": cmd
    }

    def listener(rmsg):
        try:
            fut.set_result(rmsg)
        except:
            logger.error("Failed to set result, received: " + rmsg)

    wsconnection.registerMsgListener(listener, msg['awaitId'])
    msg = json.dumps(msg)
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
            await asyncio.sleep(0.1)
        # wait max 1s for reply from FHEM
        jsonmsg = await asyncio.wait_for(send_and_wait(name, cmd), 1)
        logger.debug("sendCommandName END")
        ret = json.loads(jsonmsg)['result']
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
