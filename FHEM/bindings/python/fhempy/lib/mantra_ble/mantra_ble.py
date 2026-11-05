import asyncio
import time

from .. import fhem, generic
from .mantra import CODECS
from .models import BleAdvConfig, BleAdvEncCmd

USAGE = (
    "Usage: define <name> fhempy mantra_ble <HEX_ID> [only-fan|only-light]"
    " (e.g. 1F42)"
)
# only-fan/only-light: the device is only the fan or only the light of the
# ceiling fan, e.g. to have two devices in Matter or Google apps
ONLY_FAN = "only-fan"
ONLY_LIGHT = "only-light"
MODES = (ONLY_FAN, ONLY_LIGHT)
LIGHT_STATES = ("on", "off")
FAN_STATES = ("on", "off")
FAN_PRESETS = ("summer", "winter", "breeze", "sleep")
MIN_FAN_SPEED = 0
MAX_FAN_SPEED = 31
# fan_mode like Matter fans, in % of the max speed
FAN_MODES = ("off", "low", "medium", "high")
FAN_MODE_PERCENT = {"off": 0, "low": 33, "medium": 66, "high": 100}
MIN_BRIGHTNESS = 0
MAX_BRIGHTNESS = 100
MIN_CT = 2700
MAX_CT = 6500
CHOOSE_PREFIX = "choose "


# Input validator functions (executed by fhempy before handlers run)
def _hex_id(value):
    try:
        val = int(value, 16)
        if not 0 <= val <= 0xFFFF:
            raise ValueError
        return val
    except (ValueError, TypeError):
        raise ValueError("expected a 4-digit hexadecimal ID (e.g. 1F42)") from None


def _light_state(value):
    val = str(value).lower()
    if val not in LIGHT_STATES:
        raise ValueError(CHOOSE_PREFIX + " or ".join(LIGHT_STATES))
    return val


def _fan_state(value):
    val = str(value).lower()
    if val not in FAN_STATES:
        raise ValueError(CHOOSE_PREFIX + " or ".join(FAN_STATES))
    return val


def _fan_speed(value):
    try:
        number = int(value)
    except (ValueError, TypeError, OverflowError):
        raise ValueError("expected a whole number") from None
    if not MIN_FAN_SPEED <= number <= MAX_FAN_SPEED:
        raise ValueError(f"expected {MIN_FAN_SPEED} to {MAX_FAN_SPEED}")
    return number


def _fan_pct(value):
    try:
        number = int(value)
    except (ValueError, TypeError, OverflowError):
        raise ValueError("expected a whole number") from None
    if not 0 <= number <= 100:
        raise ValueError("expected 0 to 100")
    return number


def _fan_mode(value):
    val = str(value).lower()
    if val not in FAN_MODES:
        raise ValueError(CHOOSE_PREFIX + " or ".join(FAN_MODES))
    return val


def speed_to_pct(speed):
    return round(speed * 100 / MAX_FAN_SPEED)


def pct_to_speed(pct):
    if pct <= 0:
        return 0
    return max(1, round(pct * MAX_FAN_SPEED / 100))


def pct_to_mode(pct):
    if pct <= 0:
        return "off"
    if pct <= FAN_MODE_PERCENT["low"]:
        return "low"
    if pct <= FAN_MODE_PERCENT["medium"]:
        return "medium"
    return "high"


def _fan_preset(value):
    val = str(value).lower()
    if val not in FAN_PRESETS:
        raise ValueError(CHOOSE_PREFIX + " or ".join(FAN_PRESETS))
    return val


def _brightness(value):
    try:
        number = int(value)
    except (ValueError, TypeError, OverflowError):
        raise ValueError("expected a whole number") from None
    if not MIN_BRIGHTNESS <= number <= MAX_BRIGHTNESS:
        raise ValueError(f"expected {MIN_BRIGHTNESS} to {MAX_BRIGHTNESS}")
    return number


def _color_temp(value):
    try:
        number = int(value)
    except (ValueError, TypeError, OverflowError):
        raise ValueError("expected a whole number") from None
    if not MIN_CT <= number <= MAX_CT:
        raise ValueError(f"expected {MIN_CT} to {MAX_CT}")
    return number


class mantra_ble(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.lamp_id = None
        self.codec = CODECS[0]
        self.conf = BleAdvConfig()
        self._tx_lock = asyncio.Lock()
        self.mode = None

    @staticmethod
    def validate_define(args, argsh):
        """Check arguments without I/O, before a running device is undefined."""
        # Expected: ['DeviceName', 'fhempy', 'mantra_ble', '1F42'] plus an
        # optional only-fan/only-light
        if len(args) not in (4, 5) or argsh:
            return USAGE
        if len(args) == 5 and args[4].lower() not in MODES:
            return f"{USAGE}\nError: choose " + " or ".join(MODES)
        try:
            _hex_id(args[3])
        except ValueError as err:
            return f"{USAGE}\nError: {err}"
        return None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        error = self.validate_define(args, argsh)
        if error:
            return error
        await super().Define(hash, args, argsh)

        self.lamp_id = _hex_id(args[3])
        self.conf.id = self.lamp_id
        self.mode = args[4].lower() if len(args) == 5 else None
        device_name = hash["NAME"]
        has_light = self.mode != ONLY_FAN
        has_fan = self.mode != ONLY_LIGHT
        switches = "fan" if self.mode == ONLY_FAN else "light"

        set_config = {
            "on": {
                "help": f"<b>on</b><br>Switch {switches} on.",
            },
            "off": {
                "help": f"<b>off</b><br>Switch {switches} off.",
            },
        }
        light_config = {
            "light": {
                "args": ["state"],
                "params": {"state": {"format": _light_state}},
                "options": ",".join(LIGHT_STATES),
                "help": "<b>light [on|off]</b><br>Switch light on or off.",
            },
            "brightness": {
                "args": ["brightness"],
                "params": {"brightness": {"format": _brightness}},
                "options": f"slider,{MIN_BRIGHTNESS},1,{MAX_BRIGHTNESS}",
                "help": f"<b>brightness [0-{MAX_BRIGHTNESS}]</b><br>Set light brightness percentage (0 turns off).",
            },
            "ct": {
                "args": ["ct"],
                "params": {"ct": {"format": _color_temp}},
                "options": f"colorpicker,CT,{MIN_CT},100,{MAX_CT}",
                "help": f"<b>ct [{MIN_CT}-{MAX_CT}]</b><br>Set color temperature in Kelvin ({MIN_CT}K warm to {MAX_CT}K cold).",
            },
        }
        fan_config = {
            "fan": {
                "args": ["state"],
                "params": {"state": {"format": _fan_state}},
                "options": ",".join(FAN_STATES),
                "help": "<b>fan [on|off]</b><br>Switch fan on or off.",
            },
            "fan_speed": {
                "args": ["speed"],
                "params": {"speed": {"format": _fan_speed}},
                "options": f"slider,{MIN_FAN_SPEED},1,{MAX_FAN_SPEED}",
                "help": f"<b>fan_speed [0-{MAX_FAN_SPEED}]</b><br>Set fan speed.",
            },
            "fan_pct": {
                "args": ["pct"],
                "params": {"pct": {"format": _fan_pct}},
                "options": "slider,0,1,100",
                "help": "<b>fan_pct [0-100]</b><br>Set fan speed in percent (0 turns the fan off).",
            },
            "fan_mode": {
                "args": ["mode"],
                "params": {"mode": {"format": _fan_mode}},
                "options": ",".join(FAN_MODES),
                "help": "<b>fan_mode [" + "|".join(FAN_MODES) + "]</b><br>Set fan speed in steps.",
            },
            "fan_preset": {
                "args": ["preset"],
                "params": {"preset": {"format": _fan_preset}},
                "options": ",".join(FAN_PRESETS),
                "help": "<b>fan_preset [preset]</b><br>Select " + ", ".join(FAN_PRESETS) + ".",
            },
        }
        if has_light:
            set_config.update(light_config)
        if has_fan:
            set_config.update(fan_config)
        await self.set_set_config(set_config)

        get_config = {
            "help": {
                "help": "<b>help</b><br>List the Define usage, commands and attributes.",
            },
        }
        await self.set_get_config(get_config)

        # UI defaults, set once: the user may change or delete them later
        if has_fan:
            defaults = {
                "webCmd": "fan:fan_speed",
                "widgetOverride": "fan:iconSwitch,on,vent_ventilation,off,"
                "vent_ventilation_level_3@orange",
            }
        else:
            defaults = {"webCmd": "light:brightness"}
        await fhem.setDefaultAttrs(self.hash, defaults)

        # Initialize readings atomically
        await fhem.readingsBeginUpdate(hash)
        await fhem.readingsBulkUpdateIfChanged(hash, "state", "off")
        if has_light:
            await fhem.readingsBulkUpdateIfChanged(hash, "light", "off")
            # Keep the last brightness/color temperature across restarts
            if await fhem.ReadingsVal(device_name, "brightness", "") == "":
                await fhem.readingsBulkUpdateIfChanged(hash, "brightness", 100)
            if await fhem.ReadingsVal(device_name, "ct", "") == "":
                await fhem.readingsBulkUpdateIfChanged(hash, "ct", 4000)
        if has_fan:
            await fhem.readingsBulkUpdateIfChanged(hash, "fan", "off")
            await fhem.readingsBulkUpdateIfChanged(hash, "fan_pct", 0)
            await fhem.readingsBulkUpdateIfChanged(hash, "fan_mode", "off")
        await fhem.readingsEndUpdate(hash, 1)

    # -------------------------------------------------------------------------
    # SET HANDLERS
    # -------------------------------------------------------------------------

    async def set_on(self, hash, params):
        if self.mode == ONLY_FAN:
            await self.set_fan(hash, {"state": "on"})
        else:
            await self.set_light(hash, {"state": "on"})

    async def set_off(self, hash, params):
        if self.mode == ONLY_FAN:
            await self.set_fan(hash, {"state": "off"})
        else:
            await self.set_light(hash, {"state": "off"})

    async def set_light(self, hash, params):
        state = params["state"]
        if state == "on":
            enc_cmd = BleAdvEncCmd(0x01, 0x05, 0, 0, 0, 0, 0)
            await self._transmit_ble(enc_cmd, duration=1.5)
        else:
            enc_cmd = BleAdvEncCmd(0x01, 0x06, 0, 0, 0, 0, 0)
            await self._transmit_ble(enc_cmd, duration=1.0)

        await fhem.readingsBeginUpdate(hash)
        await fhem.readingsBulkUpdateIfChanged(hash, "light", state)
        await fhem.readingsBulkUpdateIfChanged(hash, "state", state)
        await fhem.readingsEndUpdate(hash, 1)

    async def set_brightness(self, hash, params):
        brightness = params["brightness"]
        if brightness == 0:
            await self.set_off(hash, {})
            return

        device_name = hash["NAME"]
        ct = int(await fhem.ReadingsVal(device_name, "ct", 4000))
        await self._transmit_light_ct(brightness, ct)

        await fhem.readingsBeginUpdate(hash)
        await fhem.readingsBulkUpdateIfChanged(hash, "brightness", brightness)
        await fhem.readingsBulkUpdateIfChanged(hash, "light", "on")
        await fhem.readingsBulkUpdateIfChanged(hash, "state", "on")
        await fhem.readingsEndUpdate(hash, 1)

    async def set_ct(self, hash, params):
        ct = params["ct"]
        device_name = hash["NAME"]
        brightness = int(await fhem.ReadingsVal(device_name, "brightness", 100))
        if brightness == 0:
            brightness = 100

        await self._transmit_light_ct(brightness, ct)

        await fhem.readingsBeginUpdate(hash)
        await fhem.readingsBulkUpdateIfChanged(hash, "ct", ct)
        await fhem.readingsBulkUpdateIfChanged(hash, "brightness", brightness)
        await fhem.readingsBulkUpdateIfChanged(hash, "light", "on")
        await fhem.readingsBulkUpdateIfChanged(hash, "state", "on")
        await fhem.readingsEndUpdate(hash, 1)

    async def set_fan(self, hash, params):
        state = params["state"]
        if state == "on":
            enc_cmd = BleAdvEncCmd(0x01, 0x07, 0, 0, 0, 0, 0)
            await self._transmit_ble(enc_cmd, duration=1.5)
        else:
            enc_cmd = BleAdvEncCmd(0x01, 0x08, 0, 0, 0, 0, 0)
            await self._transmit_ble(enc_cmd, duration=1.0)

        pct = 0
        if state == "on":
            # the fan continues with its last speed
            pct = await self._last_fan_pct(hash)
        await self._update_fan_readings(hash, state, pct)

    async def _update_fan_readings(self, hash, state, pct, speed=None):
        await fhem.readingsBeginUpdate(hash)
        await fhem.readingsBulkUpdateIfChanged(hash, "fan", state)
        if speed is not None:
            await fhem.readingsBulkUpdateIfChanged(hash, "fan_speed", speed)
        await fhem.readingsBulkUpdateIfChanged(hash, "fan_pct", pct)
        await fhem.readingsBulkUpdateIfChanged(hash, "fan_mode", pct_to_mode(pct))
        if self.mode == ONLY_FAN:
            await fhem.readingsBulkUpdateIfChanged(hash, "state", state)
        await fhem.readingsEndUpdate(hash, 1)

    async def _last_fan_pct(self, hash):
        value = await fhem.ReadingsVal(hash["NAME"], "fan_speed", "")
        try:
            speed = int(value)
        except (ValueError, TypeError):
            speed = 0
        if speed <= 0:
            # speed unknown, show the fan as running
            return FAN_MODE_PERCENT["medium"]
        return speed_to_pct(min(speed, MAX_FAN_SPEED))

    async def set_fan_speed(self, hash, params):
        await self._apply_fan_speed(hash, params["speed"])

    async def _apply_fan_speed(self, hash, speed, pct=None):
        if speed == 0:
            await self.set_fan(hash, {"state": "off"})
            return
        enc_cmd = BleAdvEncCmd(0x03, 0x01, speed, 0, 0, 0, 0)
        await self._transmit_ble(enc_cmd, duration=1.5)
        # the requested percent, not the rounded speed: apps show what was set
        pct = speed_to_pct(speed) if pct is None else pct
        await self._update_fan_readings(hash, "on", pct, speed)

    async def set_fan_pct(self, hash, params):
        pct = params["pct"]
        await self._apply_fan_speed(hash, pct_to_speed(pct), pct)

    async def set_fan_mode(self, hash, params):
        pct = FAN_MODE_PERCENT[params["mode"]]
        await self._apply_fan_speed(hash, pct_to_speed(pct), pct)

    async def set_fan_preset(self, hash, params):
        preset = params["preset"]
        preset_map = {
            "summer": 0x12,
            "winter": 0x14,
            "breeze": 0x0D,
            "sleep": 0x0E,
        }
        enc_cmd = BleAdvEncCmd(0x01, preset_map[preset], 0, 0, 0, 0, 0)
        await self._transmit_ble(enc_cmd, duration=1.5)
        await fhem.readingsSingleUpdate(hash, "fan_preset", preset, 1)

    # -------------------------------------------------------------------------
    # GET HANDLERS
    # -------------------------------------------------------------------------

    def get_help(self, hash, params):
        return "\n".join([
            USAGE,
            "Set commands: " + ", ".join(self._conf_set),
            "Get commands: " + ", ".join(self._conf_get),
        ])

    # -------------------------------------------------------------------------
    # CORE BLUETOOTH TRANSMISSION (ASYNC)
    # -------------------------------------------------------------------------

    async def _transmit_light_ct(self, brightness, ct):
        """Calculates multi-channel brightness/CCT values and transmits command 0x02."""
        br = max(0.01, min(1.0, brightness / 100.0))
        ct_rev = max(0.0, min(1.0, (ct - MIN_CT) / (MAX_CT - MIN_CT)))
        warm = br * (1.0 - ct_rev)
        cold = br * ct_rev

        param = int(round(warm * 255))
        arg0 = int(round(cold * 255))
        arg1 = int(round(br * 7))
        arg2 = int(round(ct_rev * 6))
        arg3 = int(round(br * 255))
        arg4 = int(round(ct_rev * 255))

        enc_cmd = BleAdvEncCmd(0x02, param, arg0, arg1, arg2, arg3, arg4)
        current_state = await fhem.ReadingsVal(self.hash["NAME"], "state", "off")
        duration = 1.0 if current_state == "on" else 1.5
        await self._transmit_ble(enc_cmd, duration=duration)

    async def _transmit_ble(self, enc_cmd, duration=1.0):
        """Builds the BLE payload and executes hcitool asynchronously.

        Serialized by a lock, otherwise overlapping sends (e.g. slider moves)
        would mix up the advertising data of two commands on hci0.
        """
        async with self._tx_lock:
            await self._transmit_ble_locked(enc_cmd, duration)

    async def _transmit_ble_locked(self, enc_cmd, duration):
        self.conf.tx_count = int(time.time() * 10) % 65535

        adv_list = self.codec.encode_advs(enc_cmd, self.conf)
        ble_payload = adv_list[0].raw
        manuf_len = len(ble_payload) + 1

        adv_payload = bytearray([0x02, 0x01, 0x02, manuf_len, 0xFF]) + ble_payload
        adv_cmd_params = bytearray([len(adv_payload)]) + adv_payload
        adv_cmd_params += bytearray([0x00] * (32 - len(adv_cmd_params)))

        hex_adv_data = " ".join([f"{b:02X}" for b in adv_cmd_params])
        hcitool_set_adv = f"sudo hcitool -i hci0 cmd 0x08 0x0008 {hex_adv_data}"
        hcitool_set_params = "sudo hcitool -i hci0 cmd 0x08 0x0006 20 00 20 00 03 00 00 00 00 00 00 00 00 07 00"

        try:
            await self._run_os_cmd(hcitool_set_params)
            await self._run_os_cmd(hcitool_set_adv)
            await self._run_os_cmd("sudo hcitool -i hci0 cmd 0x08 0x000a 01")
            await asyncio.sleep(duration)
            await self._run_os_cmd("sudo hcitool -i hci0 cmd 0x08 0x000a 00")
        except Exception as e:
            self.logger.error(f"Failed to transmit BLE command: {e}")

    async def _run_os_cmd(self, cmd):
        """Helper to run a shell command asynchronously and log errors."""
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            self.logger.error(
                f"Command failed (exit code {proc.returncode}): {cmd} | "
                f"Error: {stderr.decode().strip()}"
            )
