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


# the event loop keeps only weak references to tasks
_background_tasks = set()


def create_background_task(coro):
    """Start a task nobody awaits, keep a reference until it's done."""
    task = asyncio.create_task(coro)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    return task


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
    if attr_name in attr_list:
        config = attr_list[attr_name]
        if cmd == "set":
            attr_val = args[3]
        else:
            attr_val = config.get("default", "")
        try:
            value = (
                "" if cmd != "set" and "default" not in config
                else convert2format(attr_val, config)
            )
        except (ValueError, TypeError, OverflowError) as exc:
            return _format_error(attr_name, attr_val, config, exc)
        setattr(obj, "_attr_" + attr_name, value)

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
        config = attr_list[attr]
        try:
            value = convert2format(curr_val, config)
        except (ValueError, TypeError, OverflowError) as exc:
            # An invalid stored value must not prevent a module from loading.
            # A missing/invalid default is a module configuration error.
            value = convert2format(config["default"], config)
            obj.logger.error(
                "%s Using default %r.",
                _format_error(attr, curr_val, config, exc), value,
            )
        setattr(obj, "_attr_" + attr, value)

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
    """Convert a value; a synchronous callable may also validate it.

    Callable formats return the converted value or raise ValueError with a
    user-facing explanation. Keep them free of I/O and side effects.
    """
    target_format = "none"
    if "format" in list_def:
        target_format = list_def["format"]

    if callable(target_format):
        return target_format(value)
    elif target_format == "int":
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


def _format_error(name, value, config, exc):
    target_format = config.get("format")
    reason = str(exc) if callable(target_format) else f"expected {target_format}"
    return f"Invalid value for {name}: {value!r} ({reason})."


# See helloworld for examples of command configuration and validation.
async def handle_set(set_list_conf, obj, hash, args, argsh):
    return await _handle_command("set", set_list_conf, obj, hash, args, argsh)


async def handle_get(get_list_conf, obj, hash, args, argsh):
    return await _handle_command("get", get_list_conf, obj, hash, args, argsh)


def _command_options(command_config):
    options = []
    for command, config in command_config.items():
        if "options" in config:
            suffix = ":" + config["options"]
        elif "args" in config or "argsh" in config:
            suffix = ""
        else:
            suffix = ":noArg"
        options.append(command + suffix)
    return "Unknown argument ?, choose one of " + " ".join(options)


def _command_params(cmd_def, args, argsh):
    # Each invocation owns its parameters; do not store values in the config.
    unknown = argsh.keys() - cmd_def.get("argsh", [])
    if unknown:
        return "Unknown named argument: " + ", ".join(sorted(unknown))
    params = dict(zip(cmd_def.get("args", []), args[2:]))
    duplicates = params.keys() & argsh.keys()
    if duplicates:
        return "Argument provided twice: " + ", ".join(sorted(duplicates))
    params.update(argsh)
    return _convert_command_params(cmd_def.get("params", {}), params)


def _convert_command_params(configs, params):
    missing = object()
    for name, config in configs.items():
        value = params.get(name, config.get("value", config.get("default", missing)))
        if value is missing:
            if config.get("optional", False):
                continue
            return f"Required argument {name} missing."
        try:
            params[name] = convert2format(value, config)
        except (ValueError, TypeError, OverflowError) as exc:
            return _format_error(name, value, config, exc)
    return params


async def _handle_command(command_type, command_config, obj, hash, args, argsh):
    if len(args) < 2 or (not argsh and args[1] == "?"):
        return _command_options(command_config)

    cmd = args[1]
    if cmd not in command_config:
        return "Command not available for this device."
    cmd_def = command_config[cmd]
    positional = cmd_def.get("args", [])
    if len(args) > 2 and (
        args[2] == "?" or ("args" in cmd_def and len(args) - 2 > len(positional))
    ):
        return f"Usage: {command_type} {hash['NAME']} {cmd} " + " ".join(positional)
    if len(args) - 2 > len(positional):
        return f"Too many parameters provided: {args[2 + len(positional)]}"

    params = _command_params(cmd_def, args, argsh)
    if isinstance(params, str):
        return params
    if "function_param" in cmd_def:
        params["function_param"] = cmd_def["function_param"]
    function = cmd_def.get("function", command_type + "_" + cmd)
    if "function" in cmd_def:
        params["cmd"] = cmd
    ret = getattr(obj, function)(hash, params)
    if inspect.isawaitable(ret):
        ret = await ret
    return ret
