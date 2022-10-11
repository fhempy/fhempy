import asyncio
import time

import aiohttp

from .. import fhem, generic


class websitetests(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)

        attr_config = {
            "interval": {
                "default": 600,
                "format": "int",
                "help": "Change interval, default is 600s.",
            },
            "max_duration": {
                "default": 800,
                "format": "int",
                "help": (
                    "Error will be reported if duration_ms "
                    "higher than max_duration in ms."
                ),
            },
            "headers": {
                "default": {},
                "format": "json",
                "options": "textField-long",
                "help": (
                    "Example:<br>"
                    '{<br>"'
                    '"Content-type": "application/json",<br>'
                    '"Accept": "application/json, text/plain, */*",<br>'
                    '"Accept-Language": "en",<br>'
                    '"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 15054.63.0) '
                    '"AppleWebKit/537.36 (KHTML, like Gecko) "'
                    'Chrome/106.0.0.0 Safari/537.36"<br>'
                    "}"
                ),
            },
            "response_contains": {
                "default": "",
                "options": "textField-long",
                "help": "Response must contain this text.",
            },
        }
        self.set_attr_config(attr_config)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(argsh) > 0:
            k = list(argsh)[0]
            url = k + "=" + argsh[k]
            args.append(url)
        if len(args) != 4:
            return "Usage: define webtest fhempy websitetests URL"

        self.update_url = args[3]

        self.create_async_task(self.update_loop())

    async def update_loop(self):
        while True:
            # aiohttp get
            start_time = time.time()
            end_time = 0
            status = 0
            response_contains = -1
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        self.update_url, headers=self._attr_headers
                    ) as resp:
                        status = resp.status
                        end_time = time.time()
                        await fhem.readingsSingleUpdate(
                            self.hash, "response_status", resp.status, 1
                        )
                        if resp.status == 200:
                            text = await resp.text()
                            if len(text) > 5000:
                                text = text[0:5000] + "..."
                            await fhem.readingsSingleUpdate(
                                self.hash, "response", text, 1
                            )
                            response_contains = text.find(self._attr_response_contains)
                            await fhem.readingsSingleUpdate(
                                self.hash, "response_contains", response_contains, 1
                            )

                        else:
                            await fhem.readingsSingleUpdate(
                                self.hash,
                                "state",
                                f"failed: HTTP error {resp.status}",
                                1,
                            )
                            self.logger.error(
                                f"Failed to fetch {self.update_url}, "
                                f"failed with status {resp.status}"
                            )
            except Exception:
                status = 0
                end_time = time.time()
                self.logger.exception("Failed to update")

            duration = (end_time - start_time) * 1000
            await fhem.readingsSingleUpdate(self.hash, "duration_ms", duration, 1)
            if status == 200:
                if duration < self._attr_max_duration:
                    await fhem.readingsSingleUpdate(self.hash, "state", "ok", 1)
                else:
                    await fhem.readingsSingleUpdate(
                        self.hash,
                        "state",
                        "duration too long: " + str(int(duration)),
                        1,
                    )
                if response_contains == -1:
                    await fhem.readingsSingleUpdate(
                        self.hash, "state", "incorrect response", 1
                    )

            await asyncio.sleep(self._attr_interval)
