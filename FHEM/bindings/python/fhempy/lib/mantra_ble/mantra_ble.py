import asyncio
import time

from .. import fhem, generic
from .mantra import CODECS
from .models import BleAdvConfig, BleAdvEncCmd

USAGE = "Usage: define <name> fhempy mantra_ble <HEX_ID> (e.g. 1F42)"
LIGHT_STATES = ("on", "off")
FAN_STATES = ("on", "off")
FAN_PRESETS = ("summer", "winter", "breeze", "sleep")
MIN_FAN_SPEED = 0
MAX_FAN_SPEED = 31
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

    @staticmethod
    def validate_define(args, argsh):
        """Check arguments without I/O, before a running device is undefined."""
        # Expected: ['DeviceName', 'fhempy', 'mantra_ble', '1F42'] -> len(args) == 4
        if len(args) != 4 or argsh:
            return USAGE
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
        device_name = hash["NAME"]

        set_config = {
            "on": {
                "help": "<b>on</b><br>Switch light on.",
            },
            "off": {
                "help": "<b>off</b><br>Switch light off.",
            },
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
            "fan_preset": {
                "args": ["preset"],
                "params": {"preset": {"format": _fan_preset}},
                "options": ",".join(FAN_PRESETS),
                "help": "<b>fan_preset [preset]</b><br>Select " + ", ".join(FAN_PRESETS) + ".",
            },
        }
        await self.set_set_config(set_config)

        get_config = {
            "help": {
                "help": "<b>help</b><br>List the Define usage, commands and attributes.",
            },
        }
        await self.set_get_config(get_config)

        # Apply UI defaults if not yet configured by the user
        current_webcmd = await fhem.AttrVal(device_name, "webCmd", "")
        if not current_webcmd:
            await fhem.CommandAttr(self.hash, f"{device_name} webCmd fan:fan_speed")

        current_widgetoverride = await fhem.AttrVal(device_name, "widgetOverride", "")
        if not current_widgetoverride:
            await fhem.CommandAttr(
                self.hash,
                f"{device_name} widgetOverride fan:iconSwitch,on,vent_ventilation,off,vent_ventilation_level_3@orange"
            )

        # Initialize readings atomically
        await fhem.readingsBeginUpdate(hash)
        await fhem.readingsBulkUpdateIfChanged(hash, "state", "off")
        await fhem.readingsBulkUpdateIfChanged(hash, "light", "off")
        await fhem.readingsBulkUpdateIfChanged(hash, "fan", "off")
        await fhem.readingsBulkUpdateIfChanged(hash, "brightness", 100)
        await fhem.readingsBulkUpdateIfChanged(hash, "ct", 4000)
        await fhem.readingsEndUpdate(hash, 1)

    # -------------------------------------------------------------------------
    # SET HANDLERS
    # -------------------------------------------------------------------------

    async def set_on(self, hash, params):
        await self.set_light(hash, {"state": "on"})

    async def set_off(self, hash, params):
        await self.set_light(hash, {"state": "off"})

    async def set_light(self, hash, params):
        state = params["state"]
        if state == "on":
            enc_cmd = BleAdvEncCmd(0x01, 0x05, 0, 0, 0, 0, 0)
            await self._transmit_ble(enc_cmd, duration=0.9)
        else:
            enc_cmd = BleAdvEncCmd(0x01, 0x06, 0, 0, 0, 0, 0)
            await self._transmit_ble(enc_cmd, duration=0.35)

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
            await self._transmit_ble(enc_cmd, duration=0.9)
        else:
            enc_cmd = BleAdvEncCmd(0x01, 0x08, 0, 0, 0, 0, 0)
            await self._transmit_ble(enc_cmd, duration=0.35)

        await fhem.readingsBeginUpdate(hash)
        await fhem.readingsBulkUpdateIfChanged(hash, "fan", state)
        await fhem.readingsEndUpdate(hash, 1)

    async def set_fan_speed(self, hash, params):
        speed = params["speed"]
        if speed == 0:
            await self.set_fan(hash, {"state": "off"})
        else:
            enc_cmd = BleAdvEncCmd(0x03, 0x01, speed, 0, 0, 0, 0)
            await self._transmit_ble(enc_cmd, duration=0.9)
            await fhem.readingsBeginUpdate(hash)
            await fhem.readingsBulkUpdateIfChanged(hash, "fan", "on")
            await fhem.readingsBulkUpdateIfChanged(hash, "fan_speed", speed)
            await fhem.readingsEndUpdate(hash, 1)

    async def set_fan_preset(self, hash, params):
        preset = params["preset"]
        preset_map = {
            "summer": 0x12,
            "winter": 0x14,
            "breeze": 0x0D,
            "sleep": 0x0E,
        }
        enc_cmd = BleAdvEncCmd(0x01, preset_map[preset], 0, 0, 0, 0, 0)
        await self._transmit_ble(enc_cmd, duration=0.9)
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
        duration = 0.35 if current_state == "on" else 0.9
        await self._transmit_ble(enc_cmd, duration=duration)

    async def _transmit_ble(self, enc_cmd, duration=0.35):
        """Builds the BLE payload and executes hcitool asynchronously."""
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
