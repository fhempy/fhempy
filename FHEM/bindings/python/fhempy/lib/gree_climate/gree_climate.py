import asyncio

from greeclimate.device import (
    Device,
    FanSpeed,
    HorizontalSwing,
    Mode,
    TemperatureUnits,
    VerticalSwing,
)
from greeclimate.discovery import Discovery

from .. import fhem, generic


class gree_climate(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)

        self.device = None

        attr_config = {
            "interval": {
                "default": 60,
                "format": "int",
                "help": "Change interval, default is 60.",
            }
        }
        self.set_attr_config(attr_config)

        set_config = {
            "mode": {
                "args": ["mode"],
                "argsh": ["mode"],
                "params": {"mode": {"default": "Auto"}},
                "options": "Auto,Cool,Dry,Fan,Heat",
            },
            "desiredTemp": {
                "args": ["temperature"],
                "params": {"temperature": {"format": "int"}},
                "options": "slider,8,1,30",
            },
            "fan_speed": {
                "args": ["speed"],
                "options": "Auto,Low,MediumLow,Medium,MediumHigh,High",
            },
            "swing_horizontal": {
                "args": ["mode"],
                "options": (
                    "Default,FullSwing,Left,LeftCenter,Center,RightCenter,Right"
                ),
            },
            "swing_vertical": {
                "args": ["mode"],
                "options": (
                    "Default,FullSwing,FixedUpper,FixedUpperMiddle,FixedMiddle,"
                    "FixedLowerMiddle,FixedLower,SwingUpper,SwingUpperMiddle,"
                    "SwingMiddle,SwingLowerMiddle,SwingLower"
                ),
            },
            "fresh_air": {"args": ["onoff"], "options": "on,off"},
            "xfan": {"args": ["onoff"], "options": "on,off"},
            "anion": {"args": ["onoff"], "options": "on,off"},
            "sleep": {"args": ["onoff"], "options": "on,off"},
            "light": {"args": ["onoff"], "options": "on,off"},
            "quiet": {"args": ["onoff"], "options": "on,off"},
            "turbo": {"args": ["onoff"], "options": "on,off"},
            "steady_heat": {"args": ["onoff"], "options": "on,off"},
            "power_save": {"args": ["onoff"], "options": "on,off"},
            "on": {},
            "off": {},
        }
        self.set_set_config(set_config)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) != 4:
            return "Usage: define gree_scan fhempy gree_climate scan/name"
        await fhem.readingsSingleUpdate(self.hash, "state", "offline", 1)

        self.discovery = Discovery()

        self.name = args[3]
        if self.name == "scan":
            self.create_async_task(self.scan_devices())
            self.set_set_config({})
        else:
            self.create_async_task(self.update_loop())

    async def scan_devices(self, name=None):
        device_infos = await self.discovery.scan(wait_for=5)
        for device_info in device_infos:
            try:
                device = Device(device_info)
                await device.bind()
            except Exception:
                self.logger.exception("Failed to connect to device")
                continue

            if name is None:
                await fhem.CommandDefine(
                    self.hash,
                    (
                        f"gree_{device.device_info.name} "
                        f"fhempy gree_climate {device.device_info.name}"
                    ),
                )
            else:
                if device.device_info.name == name:
                    return device
        return None

    async def connect_device(self):
        self.device = await self.scan_devices(self.name)

    async def update_once(self):
        try:
            await self.device.update_state()
            await self.update_readings()
        except Exception:
            self.logger.exception("Failed to update readings")
            await self.connect_device()

    async def update_loop(self):
        while True:
            if self.device is None:
                await self.connect_device()
                if self.device is None:
                    self.logger.error("Couldn't find device, retry in 60s")
                    # try to connect to device every 60s
                    await asyncio.sleep(60)
                continue
            await self.update_once()
            await asyncio.sleep(self._attr_interval)

    async def update_readings(self):
        await fhem.readingsBeginUpdate(self.hash)
        try:
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "desiredTemp", self.device.target_temperature
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "temperature", self.device.current_temperature
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "mode", Mode(self.device.mode).name
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash,
                "temperature_units",
                TemperatureUnits(self.device.temperature_units).name,
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "fan_speed", FanSpeed(self.device.fan_speed).name
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "fresh_air", "on" if self.device.fresh_air else "off"
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "xfan", "on" if self.device.xfan else "off"
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "anion", "on" if self.device.anion else "off"
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "sleep", "on" if self.device.sleep else "off"
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "light", "on" if self.device.light else "off"
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash,
                "horizontal_swing",
                HorizontalSwing(self.device.horizontal_swing).name,
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash,
                "vertical_swing",
                VerticalSwing(self.device.vertical_swing).name,
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "quiet", "on" if self.device.quiet else "off"
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "turbo", "on" if self.device.turbo else "off"
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "steady_heat", "on" if self.device.steady_heat else "off"
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "power_save", "on" if self.device.power_save else "off"
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "state", "on" if self.device.power else "off"
            )
            # device info
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "ip", self.device.device_info.ip
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "port", self.device.device_info.port
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "brand", self.device.device_info.brand
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "model", self.device.device_info.model
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "name", self.device.device_info.name
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "version", self.device.device_info.version
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "mac", self.device.device_info.mac
            )
        except Exception:
            self.logger.exception("Failed to update_readings")
        await fhem.readingsEndUpdate(self.hash, 1)

    async def set_on(self, hash, params):
        self.device.power = True
        self.create_async_task(self.send_command())

    async def set_off(self, hash, params):
        self.device.power = False
        self.create_async_task(self.send_command())

    async def set_mode(self, hash, params):
        self.device.power = Mode[params["mode"]]
        self.create_async_task(self.send_command())

    async def set_desiredTemp(self, hash, params):
        self.device.target_temperature = params["temperature"]
        self.create_async_task(self.send_command())

    async def set_fan_speed(self, hash, params):
        self.device.fan_speed = FanSpeed[params["speed"]]
        self.create_async_task(self.send_command())

    async def set_swing_horizontal(self, hash, params):
        self.device.horizontal_swing = HorizontalSwing[params["mode"]]
        self.create_async_task(self.send_command())

    async def set_swing_vertical(self, hash, params):
        self.device.vertical_swing = VerticalSwing[params["mode"]]
        self.create_async_task(self.send_command())

    async def set_fresh_air(self, hash, params):
        self.device.fresh_air = True if params["onoff"] == "on" else False
        self.create_async_task(self.send_command())

    async def set_xfan(self, hash, params):
        self.device.xfan = True if params["onoff"] == "on" else False
        self.create_async_task(self.send_command())

    async def set_anion(self, hash, params):
        self.device.anion = True if params["onoff"] == "on" else False
        self.create_async_task(self.send_command())

    async def set_sleep(self, hash, params):
        self.device.sleep = True if params["onoff"] == "on" else False
        self.create_async_task(self.send_command())

    async def set_light(self, hash, params):
        self.device.light = True if params["onoff"] == "on" else False
        self.create_async_task(self.send_command())

    async def set_quiet(self, hash, params):
        self.device.quiet = True if params["onoff"] == "on" else False
        self.create_async_task(self.send_command())

    async def set_turbo(self, hash, params):
        self.device.turbo = True if params["onoff"] == "on" else False
        self.create_async_task(self.send_command())

    async def set_steady_heat(self, hash, params):
        self.device.steady_heat = True if params["onoff"] == "on" else False
        self.create_async_task(self.send_command())

    async def set_power_save(self, hash, params):
        self.device.power_save = True if params["onoff"] == "on" else False
        self.create_async_task(self.send_command())

    async def send_command(self):
        await self.device.push_state_update()
        await self.update_once()
