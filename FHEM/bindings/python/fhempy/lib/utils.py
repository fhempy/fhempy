import asyncio
import binascii
import concurrent.futures
import inspect
import os
import socket
import sys
from base64 import urlsafe_b64decode, urlsafe_b64encode
from codecs import decode
from datetime import datetime
from functools import partial, reduce

from . import fhem
from .json_utils import json_loads


def encrypt_string(plain_text, fhem_unique_id):
    from Cryptodome.Cipher import AES

    key = fhem_unique_id.encode("utf-8")
    b_text = plain_text.encode("utf-8")
    e_cipher = AES.new(key, AES.MODE_EAX, nonce=key[0:16])
    e_data = e_cipher.encrypt(b_text)
    return "crypt-aes:" + urlsafe_b64encode(e_data).decode()


def decrypt_string(encrypted_text, fhem_unique_id):
    if encrypted_text[0:10] != "crypt-aes:":
        return decrypt_fernet(encrypted_text, fhem_unique_id)
    from Cryptodome.Cipher import AES

    key = fhem_unique_id.encode("utf-8")
    encrypted_data = urlsafe_b64decode(encrypted_text[10:])
    d_cipher = AES.new(key, AES.MODE_EAX, nonce=key[0:16])
    return d_cipher.decrypt(encrypted_data).decode()


def decrypt_fernet(token_b64, key_str):
    from Cryptodome.Cipher import AES
    from Cryptodome.Hash import HMAC, SHA256
    from Cryptodome.Util.Padding import unpad

    try:
        keys = key_str.encode("utf-8")
        token_z = token_b64.encode("utf-8")
        token_b64 = reduce(decode, ("base64", "zlib"), token_z).decode()
        token = urlsafe_b64decode(token_b64)

        if len(keys) != 32 or len(token) < 73 or token[0] != 0x80:
            raise ValueError("Incorrect format")

        hmac_key, dec_key = keys[:16], keys[16:]
        HMAC.new(hmac_key, token[:-32], digestmod=SHA256).verify(token[-32:])
        iv, ct = token[9:25], token[25:-32]
        # Possibly check time-to-live here
        message = unpad(AES.new(dec_key, AES.MODE_CBC, iv=iv).decrypt(ct), 16).decode()

    except (ValueError, binascii.Error):
        message = None

    return message


def get_fhempy_root():
    from fhempy import lib

    initfile = inspect.getfile(lib)
    fhempy_root = os.path.dirname(initfile)
    return fhempy_root


# Threads are only started when needed and reused afterwards, so a high
# limit costs nothing. It has to be high because blocking calls (BT scans,
# network timeouts) can occupy a worker for a long time and every module
# shares this pool. Endless loops have to use run_blocking_thread instead.
BLOCKING_MAX_WORKERS = 64

_blocking_executor = None


def get_blocking_executor():
    global _blocking_executor
    if _blocking_executor is None:
        _blocking_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=BLOCKING_MAX_WORKERS, thread_name_prefix="fhempy_blocking"
        )
    return _blocking_executor


def shutdown_blocking_executor(wait=False):
    global _blocking_executor
    if _blocking_executor is not None:
        _blocking_executor.shutdown(wait=wait)
        _blocking_executor = None


async def run_blocking(function):
    if isinstance(function, partial) is False:
        raise Exception("Use functools.partial to call run_blocking")

    return await asyncio.get_running_loop().run_in_executor(
        get_blocking_executor(), function
    )


async def run_blocking_thread(function):
    """Run a long running blocking function (e.g. an endless loop) in its own
    thread, so it doesn't occupy a worker of the shared pool."""
    if isinstance(function, partial) is False:
        raise Exception("Use functools.partial to call run_blocking_thread")

    pool = concurrent.futures.ThreadPoolExecutor(
        max_workers=1, thread_name_prefix="fhempy_thread"
    )
    try:
        return await asyncio.get_running_loop().run_in_executor(pool, function)
    finally:
        # don't block the event loop if the task was cancelled (Undefine),
        # the thread finishes in the background
        pool.shutdown(wait=False)


def is_connection_error(exc):
    """True for network errors (device offline, DNS, timeouts, ...) which
    don't need a traceback in the log."""
    if isinstance(exc, (OSError, asyncio.TimeoutError)):
        # also covers requests.RequestException, ConnectionError, TimeoutError
        return True
    # only check libraries which are already loaded, otherwise the exception
    # can't come from them
    aiohttp = sys.modules.get("aiohttp")
    if aiohttp is not None and isinstance(exc, aiohttp.ClientError):
        return True
    httpx = sys.modules.get("httpx")
    if httpx is not None and isinstance(exc, httpx.TransportError):
        return True
    return False


def describe_exception(exc):
    """One line description of an exception, also for exceptions without
    message (e.g. TimeoutError)."""
    text = str(exc).strip()
    if text == "":
        return type(exc).__name__
    return f"{type(exc).__name__}: {text}"


class ErrorLogger:
    """Log a recurring error once instead of in every update interval.

    The first failure is logged as warning (connection errors, without
    traceback) or error (unexpected errors, with traceback). Repeated
    failures are only logged on debug level until success() is called,
    which logs the recovery on info level.

    Usage:
        try:
            await self.update()
            self._errors.success()
        except Exception:
            self._errors.failed("Failed to update")
    """

    def __init__(self, logger):
        self._logger = logger
        self._failing = {}

    def is_failing(self, key=None):
        return (key or "default") in self._failing

    def failed(self, msg, key=None, exc=None):
        """Call within an except block or pass the exception."""
        if exc is None:
            exc = sys.exc_info()[1]
        key = key or "default"
        detail = f"{msg}: {describe_exception(exc)}" if exc is not None else msg
        if key in self._failing:
            self._logger.debug(detail)
            return
        self._failing[key] = msg
        if exc is None or is_connection_error(exc):
            self._logger.warning(detail)
        else:
            self._logger.error(msg, exc_info=exc)

    def success(self, key=None):
        msg = self._failing.pop(key or "default", None)
        if msg is not None:
            self._logger.info(f"Works again after previous error: {msg}")


def run_blocking_task(function):
    return asyncio.create_task(run_blocking(function))


def to_float(value, default=0.0):
    """Convert a reading value to float, default if it isn't a number."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


async def readings_float(name, reading, default=0.0):
    """Reading value as float, default if missing or not a number."""
    return to_float(await fhem.ReadingsVal(name, reading, default), default)


# example config
# attr_list = {
#   "attribute1": {"default": 10, "format": "int", "options":"1,2,3"}
# }
async def handle_attr(attr_list, obj, hash, args, argsh):
    cmd = args[0]
    name = args[1]
    attr_name = args[2]
    attr_val = args[3]
    if attr_name in attr_list:
        if cmd == "set":
            setattr(
                obj,
                "_attr_" + attr_name,
                convert2format(attr_val, attr_list[attr_name]),
            )
        else:
            if "default" in attr_list[attr_name]:
                setattr(obj, "_attr_" + attr_name, attr_list[attr_name]["default"])
            else:
                setattr(obj, "_attr_" + attr_name, "")

    # call set_attr_....
    fct_name = "set_attr_" + attr_name
    ret = None
    if attr_name in attr_list and "function" in attr_list[attr_name]:
        fct_name = attr_list[attr_name]["function"]
    try:
        fct_call = getattr(obj, fct_name)
        ret = await fct_call(hash)
    except AttributeError:
        pass

    return ret


def get_local_ip():
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Use Google Public DNS server to determine own IP
        sock.connect(("8.8.8.8", 80))

        return sock.getsockname()[0]  # type: ignore
    except OSError:
        try:
            return socket.gethostbyname(socket.gethostname())
        except socket.gaierror:
            return "127.0.0.1"
    finally:
        if sock is not None:
            sock.close()


async def handle_define_attr(attr_list, obj, hash, extra_attrs=None):
    """Set the attribute list in FHEM and read all attribute values in one
    roundtrip. extra_attrs ({attribute: default}) are read as well.
    Returns the result of fhem.getDeviceInfo."""
    add_to_list = []
    for attr in attr_list:
        if "options" in attr_list[attr]:
            attr_opt = attr + ":" + attr_list[attr]["options"]
        else:
            attr_opt = attr
        add_to_list.append(attr_opt)

    attrs = {attr: "" for attr in attr_list}
    if extra_attrs:
        attrs.update(extra_attrs)
    info = await fhem.getDeviceInfo(hash["NAME"], attrs, " ".join(add_to_list))

    for attr in attr_list:
        curr_val = info["attr"][attr]
        if curr_val == "" and "default" in attr_list[attr]:
            curr_val = attr_list[attr]["default"]
        setattr(obj, "_attr_" + attr, convert2format(curr_val, attr_list[attr]))

    return info


def flatten_json(y):
    out = {}
    if type(y) is str:
        y = json_loads(y)

    def flatten(x, name=""):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + "_")
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + "_")
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out


def gen_reading_name(reading):
    reading = reading.lower()
    reading = reading.replace(" ", "_").replace("-", "_")
    return remove_special_charachters(reading)


def gen_fhemdev_name(devname):
    return remove_special_charachters(
        devname.replace(" ", "_").replace("-", "_").replace(":", "_")
    )


_SPECIAL_CHARACHTERS_MAP = str.maketrans(
    {
        "ü": "ue",
        "Ü": "Ue",
        "ä": "ae",
        "Ä": "Ae",
        "ö": "oe",
        "Ö": "Oe",
        "ß": "ss",
        "(": "",
        ")": "",
        "'": "",
        "`": "",
        '"': "",
    }
)


def remove_special_charachters(string):
    """
    Removes umlauts from strings and replaces them with the letter+e convention
    :param string: string to remove umlauts from
    :return: unumlauted string
    """
    return string.translate(_SPECIAL_CHARACHTERS_MAP)


def convert2format(value, list_def):
    target_format = "none"
    if "format" in list_def:
        target_format = list_def["format"]

    if target_format == "int":
        return int(value)
    elif target_format == "float":
        return float(value)
    elif target_format == "str":
        return str(value)
    elif target_format == "bool":
        if value == "on":
            return True
        else:
            return False
    elif target_format == "json":
        try:
            return json_loads(value)
        except Exception:
            return {}
    elif target_format == "time":
        try:
            return datetime.strptime(value, "%H:%M")
        except Exception:
            return None
    elif target_format == "array":
        return value.split(",")
    return value


# example config
# set_list_conf = {
#    "mode": { "args": ["mode"], "argsh": ["mode"], "params": { "mode": { "default": "eco", "optional": False }}, "options": "eco,comfort" },
#    "desiredTemp": { "args": ["temperature"], "options": "slider,10,1,30"},
#    "holidayMode": { "args": ["start", "end", "temperature"], "params": { "start": {"default": "Monday"}, "end": {"default": "23:59"}}},
#    "on": { "args": ["seconds"], "params": { "seconds": {"optional": True}}},
#    "off": {}
# }
async def handle_set(set_list_conf, obj, hash, args, argsh):
    fhem_set_list = []
    if len(args) < 2 or (len(argsh) == 0 and args[1] == "?"):
        for cmd in set_list_conf:
            if "options" in set_list_conf[cmd]:
                fhem_options = ":" + set_list_conf[cmd]["options"]
            elif "args" in set_list_conf[cmd] or "argsh" in set_list_conf[cmd]:
                fhem_options = ""
            else:
                fhem_options = ":noArg"
            fhem_set_list.append(cmd + fhem_options)
        return "Unknown argument ?, choose one of " + " ".join(fhem_set_list)
    else:
        # get cmd
        cmd = args[1]
        if cmd in set_list_conf:
            all_args = {}
            if "argsh" in set_list_conf[cmd]:
                all_args = argsh
            cmd_def = set_list_conf[cmd]
            # map arguments to params
            # add args to all_args
            if ("args" in cmd_def and (len(args) - 2) > len(cmd_def["args"])) or (
                len(args) > 2 and args[2] == "?"
            ):
                return f"Usage: set {hash['NAME']} {cmd} " + " ".join(cmd_def["args"])
            i = 0
            for arg in args[2:]:
                # arg ... mode
                # all_args[mode] = mode argument
                if "args" in cmd_def and i < len(cmd_def["args"]):
                    all_args[cmd_def["args"][i]] = arg
                else:
                    return f"Too many parameters provided: {arg}"
                i += 1
            # get default values for other params
            final_params = all_args
            if "params" in cmd_def:
                # add value to params
                for arg in all_args:
                    if arg in cmd_def["params"]:
                        cmd_def["params"][arg]["value"] = all_args[arg]
                for param in cmd_def["params"]:
                    # check if value is available or default value
                    # check if all required params are availble
                    if "value" in cmd_def["params"][param]:
                        final_params[param] = cmd_def["params"][param]["value"]
                    elif "default" not in cmd_def["params"][param] and (
                        "optional" not in cmd_def["params"][param]
                        or cmd_def["params"][param]["optional"] is False
                    ):
                        # no value found, check if optional
                        return f"Required argument {param} missing."
                    elif (
                        "default" in cmd_def["params"][param]
                        and "value" not in cmd_def["params"][param]
                    ):
                        final_params[param] = cmd_def["params"][param]["default"]
                    if "format" in cmd_def["params"][param] and param in final_params:
                        final_params[param] = convert2format(
                            final_params[param], cmd_def["params"][param]
                        )

            # call function with params
            if "function_param" in set_list_conf[cmd]:
                final_params["function_param"] = set_list_conf[cmd]["function_param"]
            if "function" in set_list_conf[cmd]:
                fct_name = set_list_conf[cmd]["function"]
                final_params["cmd"] = cmd
            else:
                fct_name = "set_" + cmd
            fct_call = getattr(obj, fct_name)
            ret = fct_call(hash, final_params)
            # set functions which only start a task don't need to be async
            if inspect.isawaitable(ret):
                ret = await ret
            return ret
        else:
            return "Command not available for this device."
