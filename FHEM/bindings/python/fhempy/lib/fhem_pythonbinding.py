import asyncio
import functools
import getopt
import http
import importlib
import json
import logging
import os
import signal
import site
import sys
import time
import traceback

import websockets

from . import fhem, pkg_installer, utils, version
from .core.zeroconf import zeroconf

logger = logging.getLogger(__name__)

loadedModuleInstances = {}
moduleLoadingRunning = {}
zc_info = None

pip_lock = asyncio.Lock()

connection_start = 0
fct_timeout = 100

stop_event = asyncio.Event()
exit_code = 0

# internal modules
active_internal_modules = []
conf = {"internal_modules": ["discover_fhempy"]}


def getFhemPyDeviceByName(name):
    if name in loadedModuleInstances:
        return loadedModuleInstances[name]
    return None


async def activate_internal_modules():
    for im in conf["internal_modules"]:
        await pkg_installer.check_and_install_dependencies("core/" + im)
        module_object = importlib.import_module("fhempy.lib.core." + im + "." + im)
        # create instance of class with logger
        module_class = getattr(module_object, im)
        instance = module_class()
        await instance.activate()
        active_internal_modules.append(instance)


async def pybinding(websocket, path):
    global zc_info
    if zc_info is not None:
        # FHEM discovered us, stop zeroconf
        await zeroconf.get_instance(logger).unregister_service(zc_info)
        zc_info = None
        # do not stop zeroconf, as it is needed to discover other fhempy
        # instances on the network in discover_fhempy
        # await zeroconf.get_instance(logger).stop()

    global connection_start
    connection_start = time.time()
    logger.info("Incoming FHEM connection: " + websocket.remote_address[0])
    pb = fhempy(websocket)
    # handle SIGTERM to shutdown gracefuly
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(pb.shutdown()))
    loop.add_signal_handler(signal.SIGINT, lambda: asyncio.create_task(pb.shutdown()))
    fhem.updateConnection(pb)
    await activate_internal_modules()
    await fhem.send_version()
    asyncio.create_task(fhem.send_latest_release())
    try:
        async for message in websocket:
            asyncio.create_task(pb.onMessage(message))
            await asyncio.sleep(0)
    except asyncio.CancelledError:
        pass
    except websockets.exceptions.ConnectionClosedError:
        if not stop_event.is_set():
            logger.error("Connection closed error", exc_info=True)
            logger.info("Restart fhempy")
            global exit_code
            exit_code = 1
            stop_event.set()


class fhempy:
    def __init__(self, websocket):
        self.wsconnection = websocket
        self.shutdown_started = 0
        self._event_listener = []
        self._msg_listeners = []
        self.msg_received_time = {}

    def register_msg_listener(self, listener, awaitid):
        self._msg_listeners.append({"func": listener, "awaitId": awaitid})

    async def send(self, msg):
        if stop_event.is_set():
            return

        await self.wsconnection.send(msg.encode("utf-8"))

    async def sendBackReturn(self, hash, ret):
        retHash = hash.copy()
        retHash["finished"] = 1
        retHash["returnval"] = ret
        retHash["id"] = hash["id"]
        msg = json.dumps(retHash)
        logger.debug("<<< WS: " + msg)
        await self.wsconnection.send(msg.encode("utf-8"))
        self.msg_handling_completed(hash)
        fhem.setFunctionInactive(hash)

    async def sendBackError(self, hash, error):
        logger.error(error + f" with hash: {hash}")
        retHash = hash.copy()
        retHash["finished"] = 1
        retHash["error"] = error
        if "id" in hash:
            retHash["id"] = hash["id"]
        msg = json.dumps(retHash, ensure_ascii=False)
        logger.debug("<<< WS: " + msg)
        await self.wsconnection.send(msg.encode("utf-8"))
        self.msg_handling_completed(hash)
        fhem.setFunctionInactive(hash)

    async def updateHash(self, hash):
        retHash = hash.copy()
        retHash["msgtype"] = "update_hash"
        del retHash["id"]
        msg = json.dumps(retHash, ensure_ascii=False)
        logger.debug("<<< WS: " + msg)
        await self.wsconnection.send(msg.encode("utf-8"))

    def getLogLevel(self, verbose_level):
        if verbose_level == "5":
            return logging.DEBUG
        elif verbose_level == "4":
            return logging.INFO
        elif verbose_level == "3":
            return logging.WARNING
        else:
            return logging.ERROR

    def msg_handling_completed(self, hash):
        if "id" in hash:
            if hash["id"] in self.msg_received_time:
                time_received = self.msg_received_time[hash["id"]]["time"]
                payload = self.msg_received_time[hash["id"]]["payload"]
                time_finished = time.time()
                time_duration = (time_finished - time_received) * 1000
                if time_duration > 5000:
                    logger.warning(f"fhempy took {time_duration:.0f}ms for {payload}")
                del self.msg_received_time[hash["id"]]

                # cleanup old messages
                for id in self.msg_received_time:
                    time_received = self.msg_received_time[id]["time"]
                    time_duration = (time_finished - time_received) * 1000
                    if time_duration > 60000:
                        logger.error(
                            f"fhempy didn't send response for {time_duration}ms"
                        )
                        del self.msg_received_time[id]

    async def onMessage(self, payload):
        try:
            await self._onMessage(payload)
        except Exception:
            logger.exception(f"Failed to handle message: {payload}")

    async def _onMessage(self, payload):
        if type(payload) is bytes:
            try:
                payload = payload.decode("utf-8")
            except Exception:
                # currently there is no need to handle
                # none utf-8 messages
                # images in readings might cause too many error msgs
                # therefore we just skip it at the moment
                logger.debug(f"Skipped non-utf8 payload: {payload}")
                return
        msg = payload
        logger.debug(">>> WS: " + msg)
        hash = None
        try:
            hash = json.loads(msg)
            # keep this for one year (written on 11.10.2021)
            if "PYTHONTYPE" in hash:
                hash["FHEMPYTYPE"] = hash["PYTHONTYPE"]
        except Exception:
            logger.error("Websocket JSON couldn't be decoded")
            return

        global fct_timeout, connection_start
        if time.time() - connection_start > 120:
            fct_timeout = 30

        try:
            await self.handle_message(msg, hash)
        except Exception:
            logger.error("Failed to handle message: ", exc_info=True)
            await self.sendBackError(hash, "fhempy failed to handle message")

    async def handle_message(self, msg, hash):
        if "awaitId" in hash and len(self._msg_listeners) > 0:
            removeElement = None
            for listener in self._msg_listeners:
                if listener["awaitId"] == hash["awaitId"]:
                    listener["func"](msg)
                    removeElement = listener
            if removeElement:
                self._msg_listeners.remove(removeElement)
        else:
            if hash["msgtype"] == "update":
                await self.update_and_exit(hash)
            elif hash["msgtype"] == "restart":
                await self.restart(hash)
            elif hash["msgtype"] == "function":
                if "id" in hash:
                    time_received = time.time()
                    self.msg_received_time[hash["id"]] = {
                        "time": time_received,
                        "payload": msg,
                    }
                await self.handle_function(hash, msg)
            elif hash["msgtype"] == "event":
                await self.handle_event(hash, msg)

    def register_event_listener(self, event_device, event_name, callback):
        self._event_listener.append(
            {
                "event_device": event_device,
                "event_name": event_name,
                "callback": callback,
            }
        )

    def unregister_event_listener(self, event_device, event_name, callback):
        self._event_listener.remove(
            {
                "event_device": event_device,
                "event_name": event_name,
                "callback": callback,
            }
        )

    async def handle_event(self, hash, msg):
        event = f"{hash['args'][0]}"
        event_device = hash["NAME"]
        event_arr = event.split(": ")
        if len(event_arr) > 1:
            event_name = event_arr[0]
            event_value = event_arr[1]
        else:
            event_name = "state"
            event_value = event_arr[0]

        for listener in self._event_listener:
            if (
                event_device == listener["event_device"]
                or listener["event_device"] is None
            ) and (
                event_name == listener["event_name"] or listener["event_name"] is None
            ):
                await listener["callback"](event_device, event_name, event_value)

    async def handle_function(self, hash, msg):
        ret = ""
        # this is needed to avoid 2 replies on dep installation
        fhem_reply_done = False
        fhem.setFunctionActive(hash)
        # load module
        nmInstance = None
        if hash["function"] == "Rename":
            new_name = hash["args"][0]
            old_name = hash["args"][1]
            if old_name in loadedModuleInstances:
                await self.rename_device(hash, old_name, new_name)
                return 0

        if hash["function"] != "Undefine":
            # Load module and execute Define
            # if Define isn't called right now

            if hash["function"] == "Define" and hash["NAME"] in loadedModuleInstances:
                # this code is called on defmod
                # if module is loaded and Define is called, do Undefine first
                # call undefine
                hash["function"] = "Undefine"
                await self.execute_function(
                    hash, fhem_reply_done, loadedModuleInstances[hash["NAME"]]
                )
                # delete module from loadedModuleInstances
                del loadedModuleInstances[hash["NAME"]]
                hash["function"] = "Define"

            if not (hash["NAME"] in loadedModuleInstances):
                if hash["NAME"] in moduleLoadingRunning:
                    await self.sendBackReturn(hash, "")
                    return 0

                moduleLoadingRunning[hash["NAME"]] = True

                # loading a module might take some time,
                # therefore sendBackReturn now
                await self.sendBackReturn(hash, "")
                fhem_reply_done = True

                try:
                    await self.check_and_install_dependencies(hash)

                    module_object = await self.import_module(hash)

                    await self.define_module(hash, module_object)
                except asyncio.TimeoutError:
                    errorMsg = (
                        f"Function execution >{fct_timeout}s, "
                        f"cancelled: {hash['NAME']} Define"
                    )
                    if fhem_reply_done:
                        await fhem.readingsSingleUpdate(hash, "state", errorMsg, 1)
                    else:
                        await self.sendBackError(hash, errorMsg)
                    return 0
                except ModuleNotFoundError:
                    errorMsg = (
                        f"Module failed to load: {hash['FHEMPYTYPE']}\n"
                        f"Maybe you need to update fhempy "
                        f"on this or remote peer."
                    )
                    errorMsg += "\n\nStacktrace:\n" + traceback.format_exc()
                    if fhem_reply_done:
                        await fhem.readingsSingleUpdate(hash, "state", errorMsg, 1)
                    else:
                        await self.sendBackError(hash, errorMsg)
                    return 0
                except Exception:
                    errorMsg = (
                        "Failed to load module "
                        + hash["FHEMPYTYPE"]
                        + ": "
                        + traceback.format_exc()
                    )
                    if fhem_reply_done:
                        await fhem.readingsSingleUpdate(hash, "state", errorMsg, 1)
                    else:
                        await self.sendBackError(hash, errorMsg)
                    return 0

        try:
            nmInstance = loadedModuleInstances[hash["NAME"]]
        except Exception:
            if hash["function"] != "Undefine":
                logging.getLogger(hash["NAME"]).exception(f"Couldn't handle {msg}")
            nmInstance = None

        if nmInstance is not None:
            try:
                ret = await self.execute_function(hash, fhem_reply_done, nmInstance)
            except asyncio.TimeoutError:
                errorMsg = (
                    f"Function execution >{fct_timeout}s, "
                    f"cancelled: {hash['NAME']} - {hash['function']}"
                )
                if fhem_reply_done:
                    await fhem.readingsSingleUpdate(hash, "state", errorMsg, 1)
                else:
                    await self.sendBackError(hash, errorMsg)
                return 0
            except Exception:
                errorMsg = (
                    "Failed to execute function "
                    + hash["function"]
                    + ": "
                    + traceback.format_exc()
                )
                if fhem_reply_done:
                    await fhem.readingsSingleUpdate(hash, "state", errorMsg, 1)
                else:
                    await self.sendBackError(hash, errorMsg)
                return 0

        if fhem_reply_done is False:
            await self.sendBackReturn(hash, ret)

        if hash["function"] == "Undefine":
            if hash["NAME"] in loadedModuleInstances:
                del loadedModuleInstances[hash["NAME"]]

    async def define_module(self, hash, module_object):
        # create instance of class with logger
        target_class = getattr(module_object, hash["FHEMPYTYPE"])
        moduleLogger = logging.getLogger(hash["NAME"])
        moduleLogger.setLevel(
            self.getLogLevel(await fhem.AttrVal(hash["NAME"], "verbose", "3"))
        )
        loadedModuleInstances[hash["NAME"]] = target_class(moduleLogger)
        del moduleLoadingRunning[hash["NAME"]]
        if hash["function"] != "Define":
            func = getattr(
                loadedModuleInstances[hash["NAME"]],
                "Define",
                "nofunction",
            )
            await asyncio.wait_for(
                func(hash, hash["defargs"], hash["defargsh"]),
                fct_timeout,
            )

    async def execute_function(self, hash, fhem_reply_done, nmInstance):
        ret = ""
        # handle verbose level of logging
        if hash["function"] == "Attr" and hash["args"][2] == "verbose":
            moduleLogger = logging.getLogger(hash["NAME"])
            if hash["args"][0] == "set":
                moduleLogger.setLevel(self.getLogLevel(hash["args"][3]))
            else:
                moduleLogger.setLevel(logging.ERROR)
        else:
            # call Set/Attr/Define/...
            func = getattr(nmInstance, hash["function"], "nofunction")
            if func != "nofunction":
                logger.debug((f"Start function {hash['NAME']}:" f"{hash['function']}"))
                if hash["function"] == "Undefine":
                    try:
                        ret = await asyncio.wait_for(func(hash), fct_timeout)
                    except Exception:
                        logger.exception(f"Undefine failed for {hash['NAME']}")
                else:
                    ret = await asyncio.wait_for(
                        func(hash, hash["args"], hash["argsh"]),
                        fct_timeout,
                    )
                logger.debug((f"End function {hash['NAME']}:" f"{hash['function']}"))
                if ret is None:
                    ret = ""
                if fhem_reply_done:
                    await self.updateHash(hash)
        return ret

    async def rename_device(self, hash, old_name, new_name):
        loadedModuleInstances[new_name] = loadedModuleInstances[old_name]
        del loadedModuleInstances[old_name]
        await self.sendBackReturn(hash, "")
        loadedModuleInstances[new_name].hash["NAME"] = new_name

    async def update_and_exit(self, hash):
        await fhem.readingsSingleUpdate(hash, "version", "update started...", 1)
        logger.info("Start update...")
        await pkg_installer.force_update_package("fhempy")
        await self.restart(hash)

    async def restart(self, hash):
        await fhem.readingsSingleUpdate(
            hash,
            "version",
            "restart...please wait",
            1,
        )
        global exit_code
        exit_code = 1
        logger.info("Restart initiated...")
        await self.undefine_all()
        stop_event.set()

    async def shutdown(self, *args):
        global exit_code
        exit_code = 0
        if self.shutdown_started == 0:
            self.shutdown_started = 1
            logger.info("Shutdown initiated...")
            await self.undefine_all()
            stop_event.set()
        else:
            logger.info("Shutdown is already running, keep calm.")
            asyncio.get_event_loop().remove_signal_handler(signal.SIGTERM)
            asyncio.get_event_loop().remove_signal_handler(signal.SIGINT)

    async def undefine_all(self):
        tasks = []
        for name in loadedModuleInstances:
            dev_instance = loadedModuleInstances[name]
            func = getattr(dev_instance, "Undefine", "nofunction")
            if func != "nofunction":
                try:
                    task = asyncio.create_task(
                        asyncio.wait_for(func(dev_instance.hash), 60)
                    )
                    tasks.append(task)
                except Exception:
                    global exit_code
                    exit_code = 2
                    logger.exception("Undefine failed")

        if len(tasks) == 0:
            return

        try:
            await asyncio.wait(tasks, timeout=60)
            for task in tasks:
                if task.cancelled():
                    continue
                if not task.done():
                    logger.error(f"Task {task} couldn't be cancelled.")
                    continue
                if task.exception() is not None:
                    logger.error(
                        f"Failed to cancel task {task}, exception: {task.exception()}"
                    )
            logger.info("All modules successfully undefined!")
        except Exception:
            logger.exception("Undefined failed")

    async def import_module(self, hash):
        # import module
        pymodule = "fhempy.lib." + hash["FHEMPYTYPE"] + "." + hash["FHEMPYTYPE"]

        # import might take a long time, therefore run_blocking
        module_object = await utils.run_blocking(
            functools.partial(importlib.import_module, pymodule)
        )

        return module_object

    async def check_and_install_dependencies(self, hash):
        # check dependencies
        deps_ok = await utils.run_blocking(
            functools.partial(
                pkg_installer.check_dependencies,
                hash["FHEMPYTYPE"],
            )
        )
        if deps_ok is False:
            # readingsSingleUpdate inform about dep installation
            await fhem.readingsSingleUpdate(hash, "state", "Installing updates...", 1)
            # run only one installation and do depcheck
            # before any other installation
            async with pip_lock:
                # make sure that all import caches
                # are up2date before check
                importlib.invalidate_caches()
                # check again if something
                # changed for dependencies
                deps_ok = pkg_installer.check_dependencies(hash["FHEMPYTYPE"])
                if deps_ok is False:
                    # start installation in
                    # a separate asyncio thread
                    await pkg_installer.check_and_install_dependencies(
                        hash["FHEMPYTYPE"]
                    )
                    # update cache again after install
                    if not site.getusersitepackages() in sys.path:
                        logger.debug("add pip path: " + site.getusersitepackages())
                        sys.path.append(site.getusersitepackages())
                    importlib.invalidate_caches()
                    # when installation finished, inform user
            await fhem.readingsSingleUpdate(
                hash,
                "state",
                "Installation finished. Please wait...",
                1,
            )
            # wait 3s so that user can read
            # the msg about installation
            await asyncio.sleep(3)
            # continue define


def usage():
    print("Usage: fhempy [-h|--help] [-v|--version] [-i|--ip] [-p|--port] [-l|--local]")
    print("  --local   Use only if you run fhempy on your FHEM machine")
    print(
        "  --ip      "
        "Specify the IP address for FHEM connection setup (default: local ip)"
    )
    print("  --port    Specify the port fhempy runs on (default: 15733)")
    print("  --version Print version and exit")
    print("  --help    This help text")


async def health_check(path, request_headers):
    if path == "/healthcheck":
        return http.HTTPStatus.OK, [], b"OK\n"


async def async_main():
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "dhvli:p:",
            ["help", "version", "ip=", "port=", "local", "debug"],
        )
    except getopt.GetoptError as err:
        logger.error(err)
        usage()
        return

    ip, port, local = handle_cmdline_options(opts)

    logger.info(f"Starting fhempy {version.__version__}...")

    await pkg_installer.check_and_install_dependencies("core")

    if not local:
        await advertise_fhempy(ip, port)

    logger.info("Waiting for FHEM connection")
    async with websockets.serve(
        pybinding,
        "0.0.0.0",
        port,
        ping_timeout=None,
        ping_interval=None,
        process_request=health_check,
        max_size=None,
        write_limit=2**20,
    ):
        await stop_event.wait()


def handle_cmdline_options(opts):
    ip = None
    port = 15733
    local = False

    for o, a in opts:
        if o in ("-v", "--version"):
            print("fhempy " + str(version.__version__))
            sys.exit()
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-i", "--ip"):
            ip = a
        elif o in ("-p", "--port"):
            port = int(a)
        elif o in ("-l", "--local"):
            local = True
        elif o in ("-d", "--debug"):
            logging.getLogger("").setLevel(logging.DEBUG)
            asyncio.get_event_loop().set_debug(True)
    return ip, port, local


async def advertise_fhempy(ip, port):
    # running on remote peer, start zeroconf for autodiscovery
    if ip is None:
        local_ip = utils.get_local_ip()
    else:
        local_ip = ip
    logger.info(f"Advertise fhempy on local network with {local_ip}:{port}")
    zc = zeroconf.get_instance(logger)
    global zc_info
    zc_info = await zc.register_service(
        "_http",
        "fhempy (" + local_ip + ")",
        port,
        {"port": port, "ip": local_ip},
    )


# from Home Assistant runner.py
def _cancel_all_tasks_with_timeout(
    loop: asyncio.AbstractEventLoop, timeout: int
) -> None:
    """Adapted _cancel_all_tasks from python 3.9 with a timeout."""
    to_cancel = asyncio.all_tasks(loop)
    if not to_cancel:
        return

    for task in to_cancel:
        task.cancel()

    loop.run_until_complete(asyncio.wait(to_cancel, timeout=timeout))

    for task in to_cancel:
        if task.cancelled():
            continue
        if not task.done():
            logger.warning(
                "Task could not be canceled and was still running after shutdown: %s",
                task,
            )
            continue
        if task.exception() is not None:
            loop.call_exception_handler(
                {
                    "message": "unhandled exception during shutdown",
                    "exception": task.exception(),
                    "task": task,
                }
            )


def run():
    global exit_code
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(async_main())
    finally:
        try:
            pass
            # the code below currently doesn't work
            # loop.run_until_complete doesn't end, therefore deactivated
            # _cancel_all_tasks_with_timeout(loop, 10)
            # loop.run_until_complete(loop.shutdown_asyncgens())
            # loop.run_until_complete(loop.shutdown_default_executor())
        finally:
            asyncio.set_event_loop(None)
            loop.close()

    logging.getLogger(__name__).info(f"Exit {exit_code}")

    # sys.exit doesn't work well, therefore os._exit is used
    os._exit(exit_code)
