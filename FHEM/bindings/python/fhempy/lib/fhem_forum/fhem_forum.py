import asyncio

import aiohttp
from bs4 import BeautifulSoup

from .. import fhem, generic


class fhem_forum(generic.FhemModule):

    URL_UNREADREPLIES = "https://forum.fhem.de/index.php?action=unreadreplies"
    URL_UNREAD = "https://forum.fhem.de/index.php?action=unread"

    def __init__(self, logger):
        super().__init__(logger)

        attr_config = {
            "interval": {
                "default": 15,
                "format": "int",
                "help": "Change interval in minutes, default is 15.",
            },
            "max_topics": {
                "default": 10,
                "format": "int",
                "help": "Maximum number of topics to show in readings.",
            },
            "keywords_unread_replies": {
                "default": "",
                "help": "Only topics with this keywords will be listed.",
            },
            "keywords_unread": {
                "default": "",
                "help": "Only topics with this keywords will be listed.",
            },
        }
        self.set_attr_config(attr_config)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) != 4:
            return "Usage: define fhem.forum fhempy fhem_forum FHEM_COOKIE"

        self.cookie = args[3]

        self.create_async_task(self.update_loop())

    async def update_loop(self):
        while True:
            # aiohttp get
            await self.get_fhem_data(fhem_forum.URL_UNREADREPLIES)
            await self.get_fhem_data(fhem_forum.URL_UNREAD)
            await asyncio.sleep(self._attr_interval * 60)

    async def get_fhem_data(self, url):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers={"cookie": "FHEM-Forum588=" + self.cookie},
                ) as resp:
                    if resp.status == 200:
                        await self.handle_response(await resp.text(), url)
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
            self.logger.exception("Failed to update")

    def contains_keyword(self, topic, keywords):
        if keywords == "":
            return True

        for kw in keywords.split(","):
            if topic.find(kw) > -1:
                return True
        return False

    async def handle_response(self, response, url):
        # bs4
        reading = "unread_replies"
        keywords = self._attr_keywords_unread_replies
        if url == fhem_forum.URL_UNREAD:
            reading = "unread"
            keywords = self._attr_keywords_unread

        soup = BeautifulSoup(response, "html.parser")
        tbody = soup.find("tbody")
        entries = tbody.findAll("tr")
        i = 1
        stateset = False
        await fhem.readingsBeginUpdate(self.hash)
        for entry in entries:
            subject = entry.find("td", {"class": "subject windowbg2"})
            if not self.contains_keyword(subject.find("span").text, keywords):
                continue

            link_to_new = subject.findAll("a")[1]
            link_to_new.next_element.replace_with(subject.find("span").text)
            link_to_new.attrs["target"] = "_blank"

            last_post = " ".join(
                entry.find("td", {"class": "lastpost windowbg2"}).text.split()
            )

            await fhem.readingsBulkUpdateIfChanged(
                self.hash,
                f"topic_{reading}_{i:02d}",
                f"<html>{link_to_new}<br>{last_post}</html>",
            )

            if i == 1 and url == fhem_forum.URL_UNREADREPLIES:
                stateset = True
                await fhem.readingsBulkUpdateIfChanged(
                    self.hash,
                    "state",
                    f"<html>{link_to_new}<br>{last_post}</html>",
                )

            i += 1
            if i > self._attr_max_topics:
                break

        if stateset is False:
            await fhem.readingsBulkUpdateIfChanged(
                self.hash,
                "state",
                f"-",
            )

        while i <= self._attr_max_topics:
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, f"topic_{reading}_{i:02d}", "-"
            )
            i += 1

        await fhem.readingsEndUpdate(self.hash, 1)
