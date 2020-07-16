
import asyncio
from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory
import json
import traceback
import logging

import lib.googlecast.googlecast

from importlib import import_module
from . import fhem

logging.basicConfig(format='%(asctime)s - %(levelname)-8s - %(message)s', level=logging.DEBUG)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

loadedModuleInstances = {}

class FhemPyProtocol(WebSocketServerProtocol):

    msg_listeners = []

    def sendBackReturn(self, hash, ret):
        retHash = hash.copy()
        del retHash['ws']
        retHash['finished'] = 1
        retHash['returnval'] = ret
        logger.debug("<<< WS: " + json.dumps(retHash))
        hash['ws'].sendMessage(json.dumps(retHash).encode("utf-8"))

    def sendBackError(self, hash, error):
        retHash = hash.copy()
        del retHash['ws']
        retHash['finished'] = 1
        retHash['error'] = error
        logger.debug("<<< WS: " + json.dumps(retHash))
        hash['ws'].sendMessage(json.dumps(retHash).encode("utf-8"))

    async def onMessage(self, payload, isBinary):
        msg = payload.decode("utf-8")
        logger.debug(">>> WS: " + msg)
        hash = json.loads(msg)
        hash['ws'] = self
        fhem.updateConnection(self)

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
                
                # load module
                nmInstance = None
                if (hash['function'] != "Undefine"):
                    if (not (hash["NAME"] in loadedModuleInstances)):
                        nm = 0
                    
                        try:
                            # TODO move import to startup to prevent timeout at the beginning
                            module_object = import_module(
                                "lib." + hash["PYTHONTYPE"] + "." + hash["PYTHONTYPE"])
                            target_class = getattr(module_object, hash["PYTHONTYPE"])
                            loadedModuleInstances[hash["NAME"]] = target_class()
                            if (hash["function"] != "Define"):
                                func = getattr(loadedModuleInstances[hash["NAME"]], "Define", "nofunction")
                                # TODO use asyncio.wait_for to use a timeout for functions
                                await func(hash, hash['defargs'], hash['defargsh'])
                        except Exception as e:
                            self.sendBackError(hash, "Failed to load module " + hash["PYTHONTYPE"] + ": " + traceback.format_exc())
                            return 0
                    nmInstance = loadedModuleInstances[hash["NAME"]]

                if (nmInstance != None):
                    try:
                        func = getattr(nmInstance, hash["function"], "nofunction")
                        if (func != "nofunction"):
                            ret = await func(hash, hash['args'], hash['argsh'])
                            if (ret == None):
                                ret = ""
                    except Exception as e:
                        self.sendBackError(hash, "Failed to execute function " + hash["function"] + ": " + traceback.format_exc())
                        return 0
                
                if (hash['function'] == "Undefine"):
                    if hash["NAME"] in loadedModuleInstances:
                        del loadedModuleInstances[hash["NAME"]]
                self.sendBackReturn(hash, ret)

            elif (hash['msgtype'] == "ping"):
                self.sendBackReturn(hash, 0)

def run():
    logger.info("Starting pythonbinding...")
    factory = WebSocketServerFactory("ws://127.0.0.1:15733")
    factory.protocol = FhemPyProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, '0.0.0.0', 15733)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()
