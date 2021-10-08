import asyncio
import time

from fhempy.lib import fhem

from .base import BaseDevice


class HTSensor(BaseDevice):
    def __init__(self, logger, gateway):
        super().__init__(logger, gateway)


class WaterLeakSensor(BaseDevice):
    def __init__(self, logger, gateway):
        super().__init__(logger, gateway)


class MotionSensor(BaseDevice):
    def __init__(self, logger, gateway):
        super().__init__(logger, gateway)
        self.reset_task = None
        self._attr_reset_motion = 120

    def update(self, data):
        asyncio.run_coroutine_threadsafe(self.async_update(data), self.loop).result()

    async def async_update(self, data):
        self.last_update = time.time()
        if data is None:
            return

        await fhem.readingsBeginUpdate(self.hash)
        # device is online
        await fhem.readingsBulkUpdateIfChanged(self.hash, "state", "online")
        # update data
        for reading in data:
            if reading == "motion":
                await fhem.readingsBulkUpdate(self.hash, reading, str(data[reading]))
            elif reading == "added_device":
                pass
            else:
                await fhem.readingsBulkUpdateIfChanged(
                    self.hash, reading.replace(" ", "_"), str(data[reading])
                )
        await fhem.readingsEndUpdate(self.hash, 1)

        if "motion" in data and "voltage" in data:
            return

        if self.reset_task:
            self.reset_task.cancel()

        self.reset_task = self.create_async_task(self._set_no_motion())

    async def _set_no_motion(self):
        try:
            await asyncio.sleep(self._attr_reset_motion)
            await fhem.readingsSingleUpdate(self.hash, "motion", "0", 1)
        except asyncio.CancelledError:
            pass


class ContactSensor(BaseDevice):
    def __init__(self, logger, gateway):
        super().__init__(logger, gateway)
