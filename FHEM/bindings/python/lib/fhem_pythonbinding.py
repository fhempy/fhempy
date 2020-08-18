
import asyncio
import websockets
import json
import traceback
import logging

# import all modules for faster loading during runtime
import lib.googlecast.googlecast
import lib.mdnsscanner.mdnsscanner
import lib.helloworld.helloworld

from importlib import import_module
from . import fhem

logging.basicConfig(format='%(asctime)s - %(levelname)-8s - %(message)s', level=logging.ERROR)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

loadedModuleInstances = {}
wsconnection = None

async def pybinding(websocket, path):
        logger.info("FHEM connection started: " + websocket.remote_address[0])
        pb = PyBinding(websocket)
        fhem.updateConnection(pb)
        try:
            async for message in websocket:
                asyncio.create_task(pb.onMessage(message))
        except websockets.exceptions.ConnectionClosedError:
            logger.error("Connection closed error")
            logger.info("Waiting for new FHEM connection...")


class PyBinding:

    msg_listeners = []

    def __init__(self, websocket):
        self.wsconnection = websocket

    def registerMsgListener(self, listener, awaitid):
        self.msg_listeners.append({"func": listener, "awaitId": awaitid})

    async def send(self, msg):
        await self.wsconnection.send(msg)

    async def sendBackReturn(self, hash, ret):
        retHash = hash.copy()
        retHash['finished'] = 1
        retHash['returnval'] = ret
        retHash['id'] = hash['id']
        msg = json.dumps(retHash)
        logger.debug("<<< WS: " + msg)
        await self.wsconnection.send(msg)
        fhem.setFunctionInactive(hash)
        

    async def sendBackError(self, hash, error):
        logger.error(error + "(id: " + hash['id'] + ")")
        retHash = hash.copy()
        retHash['finished'] = 1
        retHash['error'] = error
        retHash['id'] = hash['id']
        msg = json.dumps(retHash)
        logger.debug("<<< WS: " + msg)
        await self.wsconnection.send(msg)
        fhem.setFunctionInactive(hash)
        

    async def onMessage(self, payload):
        msg = payload
        logger.debug(">>> WS: " + msg)
        hash = None
        try:
            hash = json.loads(msg)
        except:
            logger.error("Websocket JSON couldn't be decoded")
            return

        try:
            if ("awaitId" in hash and len(self.msg_listeners) > 0):
                removeElement = None
                for listener in self.msg_listeners:
                    if (listener['awaitId'] == hash["awaitId"]):
                        listener['func'](msg)
                        removeElement = listener
                if (removeElement):
                    self.msg_listeners.remove(removeElement)
            else:
                ret = ''
                if (hash['msgtype'] == "function"):
                    fhem.setFunctionActive(hash)
                    # load module
                    nmInstance = None
                    if (hash['function'] != "Undefine"):
                        if (not (hash["NAME"] in loadedModuleInstances)):
                            nm = 0

                            try:
                                module_object = import_module(
                                    "lib." + hash["PYTHONTYPE"] + "." + hash["PYTHONTYPE"])
                                target_class = getattr(module_object, hash["PYTHONTYPE"])
                                loadedModuleInstances[hash["NAME"]] = target_class()
                                if (hash["function"] != "Define"):
                                    func = getattr(loadedModuleInstances[hash["NAME"]], "Define", "nofunction")
                                    await asyncio.wait_for(func(hash, hash['defargs'], hash['defargsh']), 1)
                            except asyncio.TimeoutError:
                                await self.sendBackError(hash, "Function execution >1s, cancelled: " + hash["NAME"] + " - Define")
                                return 0
                            except Exception as e:
                                await self.sendBackError(hash, "Failed to load module " + hash["PYTHONTYPE"] + ": " + traceback.format_exc())
                                return 0
                        nmInstance = loadedModuleInstances[hash["NAME"]]

                    if (nmInstance != None):
                        try:
                            func = getattr(nmInstance, hash["function"], "nofunction")
                            if (func != "nofunction"):
                                ret = await asyncio.wait_for(func(hash, hash['args'], hash['argsh']), 1)
                                if (ret == None):
                                    ret = ""
                        except asyncio.TimeoutError:
                            await self.sendBackError(hash, "Function execution >1s, cancelled: " + hash["NAME"] + " - " + hash["function"])
                            return 0
                        except Exception as e:
                            await self.sendBackError(hash, "Failed to execute function " + hash["function"] + ": " + traceback.format_exc())
                            return 0
                    
                    if (hash['function'] == "Undefine"):
                        if hash["NAME"] in loadedModuleInstances:
                            del loadedModuleInstances[hash["NAME"]]
                    await self.sendBackReturn(hash, ret)

        except Exception as err:
            logger.error("Failed to handle message: " + str(err))

def run():
    logger.info("Starting pythonbinding...")
    asyncio.get_event_loop().run_until_complete(
        websockets.serve(pybinding, '0.0.0.0', 15733, ping_timeout=None, ping_interval=None))
    asyncio.get_event_loop().run_forever()
