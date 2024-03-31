import asyncio
import datetime
import json

import aiohttp

from .. import fhem, generic


class energie_gv_at(generic.FhemModule):

    URL_PEAK_HOURS = "https://awareness.cloud.apg.at/api/v1/PeakHourStatus"
    URL_ELECTRICITY_NOW = (
        "https://energie.gv.at/api/gd/store/renewable_electricity_now_bars.json"
    )
    URL_RENEWABLE_NOW = (
        "https://energie.gv.at/api/gd/store/renewable_electricity_now_total.json"
    )

    def __init__(self, logger):
        super().__init__(logger)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) != 3:
            return "Usage: define energy_austria fhempy energie_gv_at"

        await self.set_icon("measure_photovoltaic_inst")

        self.create_async_task(self.update_loop())

    async def retrieve_data(self, url):
        # aiohttp get
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-AT,en;q=0.9,de-AT;q=0.8,de;q=0.7,en-GB;q=0.6,en-US;q=0.5",
            "sec-ch-ua": '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Chrome OS"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        }
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        r_json = json.loads(await resp.text())
                        return r_json
                    else:
                        await fhem.readingsSingleUpdate(
                            self.hash,
                            "state",
                            f"failed: HTTP error {resp.status}",
                            1,
                        )
                        self.logger.error(
                            f"Failed to fetch, failed with status {resp.status} {url}"
                        )
        except Exception as ex:
            self.logger.exception("Failed to update")
            await fhem.readingsSingleUpdate(
                self.hash,
                "state",
                f"failed: {ex}",
                1,
            )
        return None

    async def update_loop(self):
        while True:
            try:
                peak_hours = await self.retrieve_data(energie_gv_at.URL_PEAK_HOURS)
                await self.handle_peak_hours(peak_hours)
                elec_now = await self.retrieve_data(energie_gv_at.URL_ELECTRICITY_NOW)
                await self.handle_electricity_now(elec_now)
                renewable_now = await self.retrieve_data(
                    energie_gv_at.URL_RENEWABLE_NOW
                )
                await self.handle_renewable_now(renewable_now)
                delta = datetime.timedelta(hours=1)
                now = datetime.datetime.now()
                next_hour = (now + delta).replace(microsecond=0, second=0, minute=0)
                wait_seconds = (next_hour - now).seconds
            except Exception as ex:
                self.logger.exception("Failed to update")
                await fhem.readingsSingleUpdate(
                    self.hash,
                    "state",
                    f"failed: {ex}",
                    1,
                )
                wait_seconds = 60
            await asyncio.sleep(wait_seconds + 10)

    async def handle_renewable_now(self, res):
        await fhem.readingsSingleUpdate(
            self.hash,
            f"current_hour_ratio_renewable",
            round(res["renewablePercentage"], 1),
            1,
        )
        await fhem.readingsSingleUpdate(
            self.hash,
            f"current_hour_ratio_conventional",
            round(res["conventionalPercentage"], 1),
            1,
        )

    async def handle_electricity_now(self, res):
        all_labels = [
            "Biomasse",
            "Erdgas",
            "Nettoimporte",
            "Sonne",
            "Sonstige",
            "Wasser",
            "Wind",
        ]
        for entry in res:
            await fhem.readingsSingleUpdate(
                self.hash,
                f"current_hour_electricity_{entry['label']}",
                round(entry["percentage"], 1),
                1,
            )
            all_labels.remove(entry["label"])
        for entry in all_labels:
            await fhem.readingsSingleUpdate(
                self.hash,
                f"current_hour_electricity_{entry}",
                0,
                1,
            )

    async def handle_peak_hours(self, res):
        # current_hour_category
        default_status = res["DefaultStatus"]
        curr_status = default_status
        status_infos = res["StatusInfos"]
        for entry in status_infos:
            utc = entry["utc"]
            entry_time = datetime.datetime.strptime(utc, "%Y-%m-%dT%H:%M:%S%z")
            entry_time_diff = (
                entry_time - datetime.datetime.now(datetime.timezone.utc)
            ).total_seconds()

            if 0 < entry_time_diff < 3599:
                curr_status = entry["s"]

        await fhem.readingsSingleUpdate(
            self.hash, "current_hour_category", curr_status, 1
        )

        state = "ok" if curr_status == "1" else "save energy"
        await fhem.readingsSingleUpdate(self.hash, "state", state, 1)
