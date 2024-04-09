import asyncio
from datetime import datetime

import RPi.GPIO as GPIO
from luma.core.interface.serial import noop, spi
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.led_matrix.device import max7219
from PIL import ImageFont

from .. import fhem, generic, utils


class piclock(generic.FhemModule):

    pm_font = ImageFont.truetype(utils.get_fhempy_root() + "/piclock/clockfont.ttf", 8)
    icons = {
        "rain": [0x1C, 0x7E, 0xFF, 0xFF, 0x7E, 0x8, 0x52, 0x84],
        "nt_rain": [0x1C, 0x7E, 0xFF, 0xFF, 0x7E, 0x8, 0x52, 0x84],
        "chancerain": [0x1C, 0x7E, 0xFF, 0xFF, 0x7E, 0x8, 0x52, 0x84],
        "nt_chancerain": [0x1C, 0x7E, 0xFF, 0xFF, 0x7E, 0x8, 0x52, 0x84],
        "clear": [0x81, 0x5A, 0x3C, 0x7E, 0x7E, 0x3C, 0x5A, 0x81],
        "nt_clear": [0x30, 0x18, 0xC, 0xE, 0xE, 0xC, 0x18, 0x30],
        "snow": [0x42, 0x24, 0x99, 0x7E, 0x99, 0x24, 0x42, 0x00],
        "sleet": [0x1C, 0x7E, 0xFF, 0xFF, 0x7E, 0x89, 0x20, 0x85],
        "wind": [0x0, 0x6, 0x1, 0xFE, 0x0, 0xFE, 0x1, 0x6],
        "fog": [0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA],
        "cloudy": [0x1C, 0x7E, 0xFF, 0xFF, 0x7E, 0x0, 0x0, 0x0],
        "nt_cloudy": [0x1C, 0x7E, 0xFF, 0xFF, 0x7E, 0x0, 0x0, 0x0],
        "mostlycloudy": [0x1C, 0x7E, 0xFF, 0xFF, 0x7E, 0x0, 0x0, 0x0],
        "nt_mostlycloudy": [0x1C, 0x7E, 0xFF, 0xFF, 0x7E, 0x0, 0x0, 0x0],
        "partlycloudy": [0x0, 0x1C, 0x62, 0x81, 0x81, 0x7E, 0x0, 0x0],
        "nt_partlycloudy": [0x0, 0x1C, 0x62, 0x81, 0x81, 0x7E, 0x0, 0x0],
        "tstorm": [0x1C, 0x62, 0x81, 0x81, 0x7E, 0x18, 0xC, 0x10],
        "notused_nt_partlycloudy": [0xFF, 0xF3, 0x9D, 0x7E, 0x7E, 0x81, 0xFF, 0xFF],
    }

    def __init__(self, logger):
        super().__init__(logger)

        self.temp_dev = None
        self.temp_reading = None
        self.weather_dev = None
        self.weather_reading = None
        self.buttons = []
        self._notification_inactive = asyncio.Event()

        # create seven segment device
        serial = spi(port=0, device=0, gpio=noop())
        self.matrix_device = max7219(
            serial, cascaded=4, block_orientation=-90, rotate=0
        )

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)

        attr_config = {
            "display_time_duration": {
                "default": 20,
                "format": "int",
                "help": "Duration of time display in seconds (default 20s).",
            },
            "display_weather_duration": {
                "default": 5,
                "format": "int",
                "help": "Duration of time display in seconds (default 5s).",
            },
        }
        await self.set_attr_config(attr_config)

        set_config = {
            "notification": {
                "args": ["text"],
                "help": "Display a notification on piclock.",
            },
            "brightness": {
                "args": ["contrast"],
                "params": {"contrast": {"format": "int"}},
                "options": "slider,0,1,255,0",
            },
        }
        await self.set_set_config(set_config)

        if len(args) > 6 or len(args) < 3:
            return (
                "Usage: define piclock fhempy piclock "
                "DEVICE:TEMP_READING DEVICE:WEATHER_READING GPIOID_LIST_OF_BUTTONS"
            )

        if len(args) >= 4:
            self.temp_dev, self.temp_reading = args[3].split(":")
        if len(args) >= 5:
            self.weather_dev, self.weather_reading = args[4].split(":")
        if len(args) == 6:
            self.buttons = args[5].split(",")

        # init buttons
        GPIO.setmode(GPIO.BCM)
        for input in self.buttons:  # [4, 17, 27, 22, 18]
            GPIO.setup(input, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(
                input, GPIO.RISING, callback=self.button_pressed, bouncetime=300
            )

        await fhem.readingsSingleUpdate(self.hash, "state", "active", 1)
        self.change_contrast(
            int(await fhem.ReadingsVal(self.hash["NAME"], "brightness", "100"))
        )

        self.create_async_task(self.run_piclock())

    async def set_notification(self, hash, params):
        self.create_async_task(self.show_notification(params["text"]))

    async def set_brightness(self, hash, params):
        await fhem.readingsSingleUpdateIfChanged(
            self.hash, "brightness", params["contrast"], 1
        )
        self.change_contrast(params["contrast"])

    async def run_piclock(self):
        await self.display_text("PiClock loading...")
        await asyncio.sleep(5)
        await self.run_piclock_mainloop()

    async def run_piclock_mainloop(self):
        while True:
            try:
                # show time
                self._current_time_task = self.create_async_task(
                    self.show_current_time_loop()
                )

                # show weather
                if self.temp_dev is not None:
                    await asyncio.sleep(self._attr_display_time_duration)
                    self._current_time_task.cancel()

                    self._current_weather_task = self.create_async_task(
                        self.show_current_weather()
                    )
                    await asyncio.sleep(self._attr_display_weather_duration)
                    self._current_weather_task.cancel()
                else:
                    # no weather data, show only time
                    return

            except asyncio.CancelledError:
                await self._notification_inactive.wait()
            except Exception:
                self.logger.exception("Failed run_piclock_mainloop")

    async def show_notification(self, notification):
        self._notification_inactive.clear()
        if self._current_time_task.done() is False:
            self._current_time_task.cancel()
        if self._current_weather_task.done() is False:
            self._current_weather_task.cancel()
        await self.display_text(notification)
        self._notification_inactive.set()

    async def show_current_time_loop(self):
        try:
            while True:
                now = datetime.now()
                await self.display_text(now.strftime("%H %M"))
                next_change = 60 - datetime.now().second
                await asyncio.sleep(next_change)
        except asyncio.CancelledError:
            raise
        except Exception:
            self.logger.exception("Failed on show_current_time_loop")

    async def show_current_weather(self):
        weather = None

        if self.temp_dev is not None:
            temp = await fhem.ReadingsVal(
                self.temp_dev, self.temp_reading, "No temperature data available"
            )
        if self.weather_dev is not None:
            weather = await fhem.ReadingsVal(self.weather_dev, self.weather_reading, "")
            if weather == "":
                weather = None

        if self.temp_dev is not None:
            await self.display_text(temp + "°", weather)

    async def display_text(self, msg, iconid=None):
        await fhem.readingsSingleUpdate(self.hash, "display", msg, 1)

        w = self.text_size(msg) + self.icon_size(iconid)
        x = self.matrix_device.width
        startx = 0

        virtual = viewport(
            self.matrix_device, width=w + x, height=self.matrix_device.height
        )
        with canvas(virtual) as draw:
            if w < x:
                startx = (x - w) / 2 + 1
            if iconid is not None:
                startx += self.display_icon(draw, startx, iconid)

            draw.text((startx, 0), msg, fill="white", font=piclock.pm_font)

        # sroll text
        if w > x:
            await asyncio.sleep(1.5)
            for offset in range(w - x):
                virtual.set_position((offset, 0))
                await asyncio.sleep(0.04)
            await asyncio.sleep(1.8)

    def change_contrast(self, contrast):
        # change contrast
        self.matrix_device.contrast(contrast)

    def text_size(self, msg):
        w = 0
        with canvas(self.matrix_device) as draw:
            w = draw.textlength(msg, font=piclock.pm_font)
        return int(w)

    def icon_size(self, iconid):
        if iconid is None:
            return 0

        if iconid in piclock.icons:
            return 9
        else:
            return 0

    def display_icon(self, draw, startx, iconid):
        iconid_small = iconid.replace(" ", "").lower()
        if iconid_small in piclock.icons:
            x, y = (0, startx)
            for byte in piclock.icons[iconid_small]:
                for j in range(7, -1, -1):
                    if byte & 0x01 > 0:
                        draw.point((y + j, x), fill="white")
                    byte >>= 1
                x += 1
            return 9
        else:
            self.logger.error("icon not found: " + iconid_small)
            return 0

    def button_pressed(self, channel):
        self.create_async_task(self.async_button_pressed(channel))

    async def async_button_pressed(self, button):
        if button > 0:
            text = await fhem.AttrVal(
                self.hash["NAME"], "button_" + str(button) + "_display"
            )
            cmd = await fhem.AttrVal(
                self.hash["NAME"], "button_" + str(button) + "_cmd"
            )

            await self.show_notification(text)
            await fhem.sendCommandName(self.hash["NAME"], cmd)
