import asyncio
import binascii
import concurrent.futures
import importlib
import inspect
import logging
import os
import secrets
import socket
import sys
import threading
import time
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


# pycryptodomex is only imported when a module needs it. The first import
# takes up to 2 seconds on a Raspberry Pi, the event loop would wait meanwhile.
CRYPTO_MODULES = (
    "Cryptodome.Cipher.AES",
    "Cryptodome.Hash.HMAC",
    "Cryptodome.Hash.SHA256",
    "Cryptodome.Util.Padding",
)


async def load_crypto():
    """Imports pycryptodomex in a worker thread"""
    for name in CRYPTO_MODULES:
        await import_module(name)


async def async_encrypt_string(plain_text, fhem_unique_id):
    """encrypt_string without blocking the event loop on the first call"""
    await load_crypto()
    return encrypt_string(plain_text, fhem_unique_id)


async def async_decrypt_string(encrypted_text, fhem_unique_id):
    """decrypt_string without blocking the event loop on the first call"""
    await load_crypto()
    return decrypt_string(encrypted_text, fhem_unique_id)


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


async def import_module(name):
    """Import a module in a worker thread.

    The first import of a large package (e.g. aiohttp) takes seconds on a
    Raspberry Pi, the event loop and FHEM would wait meanwhile."""
    module = sys.modules.get(name)
    # a module which is still imported by another thread is already in
    # sys.modules but only partially initialized, import_module waits for it
    spec = getattr(module, "__spec__", None)
    if module is not None and not getattr(spec, "_initializing", False):
        return module
    return await asyncio.to_thread(importlib.import_module, name)


def _http_get(url, headers, timeout):
    import urllib.request

    request = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


async def http_get(url, headers=None, timeout=15):
    """Body of an https GET request, raises urllib.error.URLError on errors.

    For fhempy's own requests (update check, FHEM modules). aiohttp isn't
    needed for this, it costs ~16 MB RAM if no device module uses it."""
    if not url.startswith("https://"):
        raise ValueError("only https URLs are supported")
    return await asyncio.to_thread(_http_get, url, headers, timeout)


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


def format_duration(seconds):
    """Short human readable duration: 45s, 12m, 3h12m, 2d3h."""
    seconds = int(max(seconds, 0))
    if seconds < 60:
        return f"{seconds}s"
    minutes, seconds = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m"
    hours, minutes = divmod(minutes, 60)
    if hours < 24:
        return f"{hours}h{minutes:02d}m" if minutes else f"{hours}h"
    days, hours = divmod(hours, 24)
    return f"{days}d{hours}h" if hours else f"{days}d"


class _Failure:
    __slots__ = ("msg", "since", "attempts", "next_reminder", "error_types")

    def __init__(self, msg, now):
        self.msg = msg
        self.since = now
        self.attempts = 0
        self.next_reminder = now + ErrorLogger.REMINDERS[0]
        self.error_types = set()


class ErrorLogger:
    """Log a device/service which keeps failing without flooding the log.

    Works like FHEM's DevIo: one line when it fails, one line when it works
    again, and in between only rare summaries.

    - The first failure is logged as warning (connection errors, without
      traceback) or error (unexpected errors, with traceback).
    - Repeated failures are logged on debug level. A different kind of error
      (other exception type) is logged once as warning.
    - While it keeps failing, a summary is logged after 1h, 6h, 24h and then
      once a day: "Still failing since 3h12m (140 attempts): ...".
    - success() logs the recovery with duration and number of attempts.

    With hash, the reading lastError gets the error text (only when the text
    changes, it stays after recovery; its timestamp tells when it happened).
    With state, the state reading is set to that value once on the first
    failure and set back to the previous value after recovery (unless the
    module changed state in the meantime).

    next_delay() returns a retry delay with exponential backoff.

    Usage:
        self._errors = utils.ErrorLogger(logger, hash, state="disconnected")
        while True:
            try:
                await self.update()
                self._errors.success()
            except Exception:
                self._errors.failed("Failed to update")
            await asyncio.sleep(self._errors.next_delay())
    """

    # summaries after 1h, 6h, 24h, then every 24h
    REMINDERS = (3600, 6 * 3600, 24 * 3600)

    def __init__(self, logger, hash=None, state=None):
        self._logger = logger
        self._hash = hash
        self._state = state
        self._failing = {}
        self._last_error = None
        self._state_before = None
        self._state_set = False
        self._readings_task = None

    def is_failing(self, key=None):
        return (key or "default") in self._failing

    def attempts(self, key=None):
        """Number of failed attempts since the last success."""
        failure = self._failing.get(key or "default")
        return failure.attempts if failure else 0

    def failing_since(self, key=None):
        """time.time() of the first failure, None if it works."""
        failure = self._failing.get(key or "default")
        return failure.since if failure else None

    def next_delay(self, key=None, minimum=5, maximum=600):
        """Retry delay: minimum while it works, doubled with every failed
        attempt up to maximum, with +-10% jitter so many devices don't
        retry at exactly the same moment."""
        attempts = self.attempts(key)
        if attempts <= 1:
            delay = minimum
        else:
            delay = min(minimum * 2 ** min(attempts - 1, 30), maximum)
        return delay * _jitter.uniform(0.9, 1.1)

    def failed(self, msg, key=None, exc=None, traceback=True, expected=None):
        """Call within an except block or pass the exception.
        traceback=False: known errors are logged as error without traceback.
        expected=True: log like a connection error (warning, no traceback),
        e.g. for library specific "device offline" exceptions."""
        if exc is None:
            exc = sys.exc_info()[1]
        key = key or "default"
        detail = f"{msg}: {describe_exception(exc)}" if exc is not None else msg
        now = time.time()
        failure = self._failing.get(key)
        error_type = type(exc).__name__ if exc is not None else None
        if failure is None:
            failure = self._failing[key] = _Failure(msg, now)
            failure.attempts = 1
            failure.error_types.add(error_type)
            if expected is None:
                expected = exc is None or is_connection_error(exc)
            if expected:
                self._logger.warning(detail)
            elif not traceback:
                self._logger.error(detail)
            else:
                self._logger.error(msg, exc_info=exc)
        else:
            failure.attempts += 1
            if error_type not in failure.error_types:
                failure.error_types.add(error_type)
                self._logger.warning(detail)
            elif now >= failure.next_reminder:
                self._logger.warning(
                    f"Still failing since {format_duration(now - failure.since)} "
                    f"({failure.attempts} attempts): {detail}"
                )
            else:
                self._logger.debug(detail)
            if now >= failure.next_reminder:
                failure.next_reminder = self._next_reminder(failure, now)
        self._update_readings(detail)

    def success(self, key=None):
        failure = self._failing.pop(key or "default", None)
        if failure is None:
            return
        failed_for = format_duration(time.time() - failure.since)
        self._logger.info(
            f"Works again after {failed_for} and {failure.attempts} failed "
            f"attempt{'s' if failure.attempts != 1 else ''}: {failure.msg}"
        )
        if not self._failing:
            self._update_readings(None)

    def _next_reminder(self, failure, now):
        for offset in ErrorLogger.REMINDERS:
            if failure.since + offset > now:
                return failure.since + offset
        days = int((now - failure.since) // 86400) + 1
        return failure.since + days * 86400

    def _update_readings(self, error):
        if self._hash is None:
            return
        set_error = error is not None and error != self._last_error
        set_state = self._state is not None and (error is not None) != self._state_set
        if not set_error and not set_state:
            return
        if set_error:
            self._last_error = error
        if set_state:
            self._state_set = error is not None
        previous = self._readings_task

        async def update():
            if previous is not None and not previous.done():
                # keep the order of the updates
                await asyncio.wait([previous])
            try:
                await self._write_readings(error, set_error, set_state)
            except Exception:
                self._logger.debug("Failed to update error readings", exc_info=True)

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return
        self._readings_task = create_background_task(update())

    async def _write_readings(self, error, set_error, set_state):
        if set_error:
            await fhem.readingsSingleUpdateIfChanged(self._hash, "lastError", error, 1)
        if not set_state:
            return
        name = self._hash["NAME"]
        if error is not None:
            current = await fhem.ReadingsVal(name, "state", "")
            if current != self._state:
                self._state_before = current
            await fhem.readingsSingleUpdateIfChanged(
                self._hash, "state", self._state, 1
            )
        else:
            current = await fhem.ReadingsVal(name, "state", "")
            # the module may have set a new state already
            if current == self._state and self._state_before is not None:
                await fhem.readingsSingleUpdateIfChanged(
                    self._hash, "state", self._state_before, 1
                )
            self._state_before = None


_jitter = secrets.SystemRandom()


class RepeatedLogFilter(logging.Filter):
    """Safety net against log floods, e.g. from libraries which log every
    failed reconnect attempt.

    The same message (same logger, level and message template) is let through
    once, repetitions are suppressed for a while (10 minutes, doubled while
    it keeps repeating, up to 6 hours). The next line that passes says how
    many lines were suppressed. Debug messages and loggers on debug level
    (verbose 5) are never suppressed.
    """

    WINDOW = 600
    MAX_WINDOW = 6 * 3600
    MAX_KEYS = 2000

    def __init__(self):
        super().__init__()
        self._lock = threading.Lock()
        self._seen = {}

    def filter(self, record):
        if record.levelno < logging.INFO:
            return True
        if logging.getLogger(record.name).isEnabledFor(logging.DEBUG):
            return True
        key = (record.name, record.levelno, str(record.msg))
        now = record.created
        with self._lock:
            entry = self._seen.get(key)
            if entry is None or now - entry[0] >= entry[1] * 2:
                # new message or quiet for a long time: start again
                if len(self._seen) >= self.MAX_KEYS:
                    self._purge(now)
                self._seen[key] = [now, self.WINDOW, 0]
                return True
            last, window, suppressed = entry
            if now - last < window:
                entry[2] += 1
                return False
            entry[0] = now
            entry[1] = min(window * 2, self.MAX_WINDOW) if suppressed else window
            entry[2] = 0
        if suppressed:
            record.msg = (
                f"{record.msg} (repeated {suppressed}x in the last "
                f"{format_duration(now - last)}, suppressed)"
            )
        return True

    def _purge(self, now):
        for key, entry in list(self._seen.items()):
            if now - entry[0] >= entry[1] * 2:
                del self._seen[key]
        if len(self._seen) >= self.MAX_KEYS:
            self._seen.clear()


_repeated_log_filter = RepeatedLogFilter()


def install_repeated_log_filter():
    """Add RepeatedLogFilter to all handlers of the root logger."""
    for handler in logging.getLogger().handlers:
        if _repeated_log_filter not in handler.filters:
            handler.addFilter(_repeated_log_filter)


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
                ""
                if cmd != "set" and "default" not in config
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
        ret = fct_call(hash)
        # plain functions are fine for hooks without anything to await
        if inspect.isawaitable(ret):
            ret = await ret
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
                _format_error(attr, curr_val, config, exc),
                value,
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
