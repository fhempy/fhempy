import asyncio
import functools
import getopt
import importlib
import json
import logging
import site
import sys
import os
import time
import traceback

import websockets

from . import fhem, pkg_installer, utils, version
from .core.zeroconf import zeroconf

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk import start_transaction

unknown_key = "thisisnotmagic012345678901234567"
unknown_code = utils.decrypt_string(
    (
        "eJwVwc0OQzAAAOAnclgi"
        "xmGH6raGlg1juAilpbowtvp5+mX"
        "fx8Gf3daolFK10DOeG7yEzVHj6b"
        "wX\nao54HvSNMksFwtXyb/hISo9"
        "xDDkEr3O4kApkNQQYxqrUO2sNh2"
        "QkouabLFDOUpoM6PapAurDvXN8\n"
        "+XHGWMRUi75bZsvBbMFqcI/oggks"
        "N/3dnz2CJqu4zxPFq6hZZLsaW8CV"
        "u4cFCSt6jLFN6ekH7iE/\npQ==\n"
    ),
    unknown_key,
)

sentry_logging = LoggingIntegration(
    level=logging.INFO,  # Capture info and above as breadcrumbs
    event_level=logging.ERROR,  # Send errors as events
)

sentry_sdk.init(
    unknown_code,
    traces_sample_rate=0.1,
    release="fhempy@" + str(version.__version__),
    integrations=[sentry_logging],
)

logger = logging.getLogger(__name__)

loadedModuleInstances = {}
moduleLoadingRunning = {}
zc_info = None

pip_lock = asyncio.Lock()

connection_start = 0
fct_timeout = 60

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
        await zeroconf.get_instance(logger).stop()

    global connection_start
    connection_start = time.time()
    logger.info("Incoming FHEM connection: " + websocket.remote_address[0])
    pb = PyBinding(websocket)
    fhem.updateConnection(pb)
    await activate_internal_modules()
    await fhem.send_version()
    try:
        async for message in websocket:
            asyncio.create_task(pb.onMessage(message))
    except websockets.exceptions.ConnectionClosedError:
        logger.error("Connection closed error", exc_info=True)
        logger.info("Restart binding")
        sys.exit(1)


class PyBinding:

    msg_listeners = []

    def __init__(self, websocket):
        self.wsconnection = websocket

    def registerMsgListener(self, listener, awaitid):
        self.msg_listeners.append({"func": listener, "awaitId": awaitid})

    async def send(self, msg):
        await self.wsconnection.send(msg.encode("utf-8"))

    async def sendBackReturn(self, hash, ret):
        retHash = hash.copy()
        retHash["finished"] = 1
        retHash["returnval"] = ret
        retHash["id"] = hash["id"]
        msg = json.dumps(retHash)
        logger.debug("<<< WS: " + msg)
        await self.wsconnection.send(msg.encode("utf-8"))
        fhem.setFunctionInactive(hash)

    async def sendBackError(self, hash, error):
        logger.error(error + "(id: {})".format(hash["id"]))
        retHash = hash.copy()
        retHash["finished"] = 1
        retHash["error"] = error
        retHash["id"] = hash["id"]
        msg = json.dumps(retHash, ensure_ascii=False)
        logger.debug("<<< WS: " + msg)
        await self.wsconnection.send(msg.encode("utf-8"))
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

    async def onMessage(self, payload):
        try:
            await self._onMessage(payload)
        except SystemExit:
            sys.exit(1)
        except Exception:
            logger.exception("Failed to handle message: " + str(payload))

    async def _onMessage(self, payload):
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
            fct_timeout = 10

        try:
            if "awaitId" in hash and len(self.msg_listeners) > 0:
                removeElement = None
                for listener in self.msg_listeners:
                    if listener["awaitId"] == hash["awaitId"]:
                        listener["func"](msg)
                        removeElement = listener
                if removeElement:
                    self.msg_listeners.remove(removeElement)
            else:
                ret = ""
                if hash["msgtype"] == "update":
                    await fhem.readingsSingleUpdate(
                        hash, "version", "update started...", 1
                    )
                    await pkg_installer.force_update_package("fhempy")
                    await fhem.readingsSingleUpdate(
                        hash,
                        "version",
                        "update finished...please wait",
                        1,
                    )
                    os._exit(1)
                if hash["msgtype"] == "function":
                    # this is needed to avoid 2 replies on dep installation
                    fhem_reply_done = False
                    fhem.setFunctionActive(hash)
                    # load module
                    nmInstance = None
                    if hash["function"] == "Rename":
                        if hash["NAME"] in loadedModuleInstances:
                            loadedModuleInstances[
                                hash["args"][1]
                            ] = loadedModuleInstances[hash["args"][0]]
                            del loadedModuleInstances[hash["args"][0]]
                            await self.sendBackReturn(hash, "")
                            return 0

                    if hash["function"] != "Undefine":
                        # Load module and execute Define
                        # if Define isn't called right now
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
                                # check dependencies
                                deps_ok = await utils.run_blocking(
                                    functools.partial(
                                        pkg_installer.check_dependencies,
                                        hash["FHEMPYTYPE"],
                                    )
                                )
                                if deps_ok is False:
                                    # readingsSingleUpdate inform about dep installation
                                    await fhem.readingsSingleUpdate(
                                        hash, "state", "Installing updates...", 1
                                    )
                                    # run only one installation and do depcheck
                                    # before any other installation
                                    async with pip_lock:
                                        # make sure that all import caches
                                        # are up2date before check
                                        importlib.invalidate_caches()
                                        # check again if something
                                        # changed for dependencies
                                        deps_ok = pkg_installer.check_dependencies(
                                            hash["FHEMPYTYPE"]
                                        )
                                        if deps_ok is False:
                                            # start installation in
                                            # a separate asyncio thread
                                            await pkg_installer.check_and_install_dependencies(
                                                hash["FHEMPYTYPE"]
                                            )
                                            # update cache again after install
                                            if (
                                                not site.getusersitepackages()
                                                in sys.path
                                            ):
                                                logger.debug(
                                                    "add pip path: "
                                                    + site.getusersitepackages()
                                                )
                                                sys.path.append(
                                                    site.getusersitepackages()
                                                )
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

                                # import module
                                pymodule = (
                                    "fhempy.lib."
                                    + hash["FHEMPYTYPE"]
                                    + "."
                                    + hash["FHEMPYTYPE"]
                                )
                                # import might take a long time, therefore run_blocking
                                module_object = await utils.run_blocking(
                                    functools.partial(importlib.import_module, pymodule)
                                )
                                # create instance of class with logger
                                target_class = getattr(
                                    module_object, hash["FHEMPYTYPE"]
                                )
                                moduleLogger = logging.getLogger(hash["NAME"])
                                moduleLogger.setLevel(
                                    self.getLogLevel(
                                        await fhem.AttrVal(hash["NAME"], "verbose", "3")
                                    )
                                )
                                loadedModuleInstances[hash["NAME"]] = target_class(
                                    moduleLogger
                                )
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
                            except asyncio.TimeoutError:
                                errorMsg = (
                                    f"Function execution >{fct_timeout}s, "
                                    f"cancelled: {hash['NAME']} Define"
                                )
                                if fhem_reply_done:
                                    await fhem.readingsSingleUpdate(
                                        hash, "state", errorMsg, 1
                                    )
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
                                    await fhem.readingsSingleUpdate(
                                        hash, "state", errorMsg, 1
                                    )
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
                                    await fhem.readingsSingleUpdate(
                                        hash, "state", errorMsg, 1
                                    )
                                else:
                                    await self.sendBackError(hash, errorMsg)
                                return 0

                    try:
                        nmInstance = loadedModuleInstances[hash["NAME"]]
                    except Exception:
                        if hash["function"] != "Undefine":
                            logging.getLogger(hash["NAME"]).exception(
                                f"Couldn't handle {msg}"
                            )
                        nmInstance = None

                    if nmInstance is not None:
                        try:
                            # handle verbose level of logging
                            if (
                                hash["function"] == "Attr"
                                and hash["args"][2] == "verbose"
                            ):
                                moduleLogger = logging.getLogger(hash["NAME"])
                                if hash["args"][0] == "set":
                                    moduleLogger.setLevel(
                                        self.getLogLevel(hash["args"][3])
                                    )
                                else:
                                    moduleLogger.setLevel(logging.ERROR)
                            else:
                                # call Set/Attr/Define/...
                                func = getattr(
                                    nmInstance, hash["function"], "nofunction"
                                )
                                if func != "nofunction":
                                    logger.debug(
                                        (
                                            f"Start function {hash['NAME']}:"
                                            f"{hash['function']}"
                                        )
                                    )
                                    if hash["function"] == "Undefine":
                                        try:
                                            ret = await asyncio.wait_for(
                                                func(hash), fct_timeout
                                            )
                                        except Exception:
                                            logger.exception("Undefine failed")
                                    else:
                                        ret = await asyncio.wait_for(
                                            func(hash, hash["args"], hash["argsh"]),
                                            fct_timeout,
                                        )
                                    logger.debug(
                                        (
                                            f"End function {hash['NAME']}:"
                                            f"{hash['function']}"
                                        )
                                    )
                                    if ret is None:
                                        ret = ""
                                    if fhem_reply_done:
                                        await self.updateHash(hash)
                        except asyncio.TimeoutError:
                            errorMsg = (
                                f"Function execution >{fct_timeout}s, "
                                f"cancelled: {hash['NAME']} - {hash['function']}"
                            )
                            if fhem_reply_done:
                                await fhem.readingsSingleUpdate(
                                    hash, "state", errorMsg, 1
                                )
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
                                await fhem.readingsSingleUpdate(
                                    hash, "state", errorMsg, 1
                                )
                            else:
                                await self.sendBackError(hash, errorMsg)
                            return 0

                    if fhem_reply_done is False:
                        await self.sendBackReturn(hash, ret)

                    if hash["function"] == "Undefine":
                        if hash["NAME"] in loadedModuleInstances:
                            del loadedModuleInstances[hash["NAME"]]

        except SystemExit as se:
            raise se
        except Exception:
            logger.error("Failed to handle message: ", exc_info=True)
            await self.sendBackError(hash, "fhempy failed to handle message")


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
        sys.exit(2)

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
            port = a
        elif o in ("-l", "--local"):
            local = True
        elif o in ("-d", "--debug"):
            logging.getLogger("").setLevel(logging.DEBUG)

    logger.info("Starting fhempy...")

    await pkg_installer.check_and_install_dependencies("core")

    if not local:
        logger.info("Advertise fhempy on local network")
        # running on remote peer, start zeroconf for autodiscovery
        if ip is None:
            local_ip = utils.get_local_ip()
        else:
            local_ip = ip
        zc = zeroconf.get_instance(logger)
        global zc_info
        zc_info = await zc.register_service(
            "_http",
            "fhempy (" + local_ip + ")",
            port,
            {"port": port, "ip": local_ip},
        )

    logger.info("Waiting for FHEM connection")
    await websockets.serve(
        pybinding, "0.0.0.0", port, ping_timeout=None, ping_interval=None
    )


def run():
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    asyncio.get_event_loop().set_debug(True)
    asyncio.get_event_loop().run_until_complete(async_main())
    asyncio.get_event_loop().run_forever()
