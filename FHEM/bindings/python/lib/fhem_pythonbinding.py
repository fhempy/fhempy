
import asyncio
import websockets
import json
import traceback
import logging
import concurrent.futures
import functools
import site
import sys
import importlib
from . import fhem
from . import pkg_installer

logging.basicConfig(format='%(asctime)s - %(levelname)-8s - %(name)s: %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

loadedModuleInstances = {}
moduleLoadingRunning = {}
wsconnection = None

pip_lock = asyncio.Lock()

async def pybinding(websocket, path):
        logger.info("FHEM connection started: " + websocket.remote_address[0])
        pb = PyBinding(websocket)
        fhem.updateConnection(pb)
        try:
            async for message in websocket:
                asyncio.create_task(pb.onMessage(message))
        except websockets.exceptions.ConnectionClosedError:
            logger.error("Connection closed error", exc_info=True)
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
                    # this is needed to avoid 2 replies on dep installation
                    fhem_reply_done = False
                    fhem.setFunctionActive(hash)
                    # load module
                    nmInstance = None
                    if (hash['function'] != "Undefine"):
                        # Load module and execute Define if Define isn't called right now
                        if (not (hash["NAME"] in loadedModuleInstances)):
                            if hash["NAME"] in moduleLoadingRunning:
                                await self.sendBackReturn(hash, "")
                                return 0

                            moduleLoadingRunning[hash["NAME"]] = True
                            nm = 0

                            # loading a module might take some time, therefore sendBackReturn now
                            await self.sendBackReturn(hash, "")
                            fhem_reply_done = True

                            try:
                                # check dependencies
                                deps_ok = pkg_installer.check_dependencies(hash["PYTHONTYPE"])
                                if deps_ok == False:
                                    # readingsSingleUpdate inform about dep installation
                                    await fhem.readingsSingleUpdate(hash, "state", "Installing updates...", 1)
                                    # run only one installation and do depcheck before any other installation
                                    async with pip_lock:
                                        # make sure that all import caches are up2date before check
                                        importlib.invalidate_caches()
                                        # check again if something changed for dependencies
                                        deps_ok = pkg_installer.check_dependencies(hash["PYTHONTYPE"])
                                        if deps_ok == False:
                                            # start installation in a separate asyncio thread
                                            with concurrent.futures.ThreadPoolExecutor() as pool:
                                                result = await asyncio.get_event_loop().run_in_executor(
                                                        pool, functools.partial(
                                                            pkg_installer.check_and_install_dependencies,
                                                            hash["PYTHONTYPE"]))
                                            # update cache again after install
                                            if not site.getusersitepackages() in sys.path:
                                                logger.debug("add pip path: " + site.getusersitepackages())
                                                sys.path.append(site.getusersitepackages())
                                            importlib.invalidate_caches()
                                    # when installation finished, inform user
                                    await fhem.readingsSingleUpdate(hash, "state", "Installation finished. Define now...", 1)
                                    # wait 5s so that user can read the msg about installation
                                    await asyncio.sleep(5)
                                    # continue define

                                # import module
                                pymodule = "lib." + hash["PYTHONTYPE"] + "." + hash["PYTHONTYPE"]
                                module_object = importlib.import_module(pymodule)
                                # create instance of class with logger
                                target_class = getattr(module_object, hash["PYTHONTYPE"])
                                moduleLogger = logging.getLogger(hash["NAME"])
                                loadedModuleInstances[hash["NAME"]] = target_class(moduleLogger)
                                del moduleLoadingRunning[hash["NAME"]]
                                if (hash["function"] != "Define"):
                                    func = getattr(loadedModuleInstances[hash["NAME"]], "Define", "nofunction")
                                    await asyncio.wait_for(func(hash, hash['defargs'], hash['defargsh']), 1)
                            except asyncio.TimeoutError:
                                errorMsg = "Function execution >1s, cancelled: " + hash["NAME"] + " - Define"
                                if fhem_reply_done:
                                    await fhem.readingsSingleUpdate(hash, "state", errorMsg, 1)
                                else:
                                    await self.sendBackError(hash, errorMsg)
                                return 0
                            except Exception as e:
                                errorMsg = "Failed to load module " + hash["PYTHONTYPE"] + ": " + traceback.format_exc()
                                if fhem_reply_done:
                                    await fhem.readingsSingleUpdate(hash, "state", errorMsg, 1)
                                else:
                                    await self.sendBackError(hash, errorMsg)
                                return 0
                        
                        nmInstance = loadedModuleInstances[hash["NAME"]]

                    if (nmInstance != None):
                        try:
                            # handle verbose level of logging
                            if hash["function"] == "Attr":
                                if hash["args"][2] == "verbose":
                                    moduleLogger = logging.getLogger(hash["NAME"])
                                    if hash["args"][0] == "set":
                                        verbose_level = hash["args"][3]
                                        if verbose_level == "5":
                                            moduleLogger.setLevel(logging.DEBUG)
                                        elif verbose_level == "4":
                                            moduleLogger.setLevel(logging.INFO)
                                        elif verbose_level <= "3":
                                            moduleLogger.setLevel(logging.ERROR)
                                    else:
                                        moduleLogger.setLevel(logging.ERROR)
                            else:
                                # call Set/Attr/Define/...
                                func = getattr(nmInstance, hash["function"], "nofunction")
                                if (func != "nofunction"):
                                    ret = await asyncio.wait_for(func(hash, hash['args'], hash['argsh']), 1)
                                    if (ret == None):
                                        ret = ""
                        except asyncio.TimeoutError:
                            errorMsg = "Function execution >1s, cancelled: " + hash["NAME"] + " - " + hash["function"]
                            if fhem_reply_done:
                                await fhem.readingsSingleUpdate(hash, "state", errorMsg, 1)
                            else:
                                await self.sendBackError(hash, errorMsg)
                            return 0
                        except Exception as e:
                            errorMsg = "Failed to execute function " + hash["function"] + ": " + traceback.format_exc()
                            if fhem_reply_done:
                                await fhem.readingsSingleUpdate(hash, "state", errorMsg, 1)
                            else:
                                await self.sendBackError(hash, errorMsg)
                            return 0
                    
                    if (hash['function'] == "Undefine"):
                        if hash["NAME"] in loadedModuleInstances:
                            del loadedModuleInstances[hash["NAME"]]
                    
                    if fhem_reply_done is False:
                        await self.sendBackReturn(hash, ret)

        except Exception as err:
            logger.error("Failed to handle message: ", exc_info=True)

def run():
    logger.info("Starting pythonbinding...")
    asyncio.get_event_loop().run_until_complete(
        websockets.serve(pybinding, '0.0.0.0', 15733, ping_timeout=None, ping_interval=None))
    asyncio.get_event_loop().run_forever()
