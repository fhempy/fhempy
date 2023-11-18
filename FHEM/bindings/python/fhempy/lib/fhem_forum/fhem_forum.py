import asyncio
import functools

import aiohttp
from bs4 import BeautifulSoup

from .. import fhem, generic, utils


class fhem_forum(generic.FhemModule):

    URL_UNREADREPLIES = "https://forum.fhem.de/index.php?action=unreadreplies"
    URL_UNREAD = "https://forum.fhem.de/index.php?action=unread"
    URL_PM = "https://forum.fhem.de/index.php?action=pm"

    def __init__(self, logger):
        super().__init__(logger)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)

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
                "function": "set_attr_keywords",
            },
            "keywords_unread": {
                "default": "",
                "help": "Only topics with this keywords will be listed.",
                "function": "set_attr_keywords",
            },
        }
        await self.set_attr_config(attr_config)

        if len(args) != 4:
            return "Usage: define fhem.forum fhempy fhem_forum FHEM_COOKIE"

        self.cookie = args[3]
        self.first_run = True

        self.create_async_task(self.update_loop())

    async def set_attr_keywords(self, hash):
        self.create_async_task(self.update_once())

    async def update_once(self):
        stateset_ur = await self.get_fhem_data(fhem_forum.URL_UNREADREPLIES)
        stateset_u = await self.get_fhem_data(fhem_forum.URL_UNREAD)
        stateset_pm = await self.get_fhem_data(fhem_forum.URL_PM)
        if stateset_ur is False and stateset_u is False and stateset_pm is False:
            await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "-", 1)

    async def update_loop(self):
        while True:
            # aiohttp get
            await self.update_once()
            await asyncio.sleep(self._attr_interval * 60)

    async def get_fhem_data(self, url):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers={"cookie": "FHEM-Forum588=" + self.cookie},
                ) as resp:
                    if resp.status == 200:
                        return await self.handle_response(await resp.text(), url)
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

    def get_soup_entries(self, response):
        soup = BeautifulSoup(response, "html.parser")
        topics = soup.find("div", {"id": "topic_container"})
        if topics is None:
            return []
        entries = topics.findAll("div", {"class": "windowbg"})
        return entries

    def get_soup_private_messages(self, response):
        soup = BeautifulSoup(response, "html.parser")
        topics = soup.select(".windowbg.unread_pm")
        if topics is None:
            return []
        entries = soup.select(".windowbg.unread_pm")
        return entries

    async def handle_private_messages(self, response):
        stateset = False
        entries = await utils.run_blocking(
            functools.partial(self.get_soup_private_messages, response)
        )
        if len(entries) == 0:
            ret = await fhem.readingsBulkUpdateIfChanged(
                self.hash, f"private_message", "-"
            )
            return stateset

        try:
            for entry in entries:
                title = entry.select(".pm_subject")[0].next.next.text
                user_from = entry.select(".pm_from_to")[0].text.strip()
                date_sent = entry.select(".pm_time")[0].text
                link_to_msg = entry.select(".pm_subject")[0].next.next["href"]
                link_to_msg = "https://forum.fhem.de/index.php?action=pm" + link_to_msg

                ret = await fhem.readingsBulkUpdateIfChanged(
                    self.hash,
                    f"private_message",
                    f'<html><a href="{link_to_msg}" target="_blank">'
                    + f"{title}</a>"
                    + f"<br>{date_sent} von {user_from}</html>",
                )

                if ret:
                    stateset = True
                    ret = await fhem.readingsBulkUpdateIfChanged(
                        self.hash,
                        f"state",
                        f'<html><a href="{link_to_msg}" target="_blank">'
                        + f"{title}</a>"
                        + f"<br>{date_sent} von {user_from}</html>",
                    )
                break

        except Exception:
            self.logger.exception("Failed to handle private messages")
        return stateset

    async def handle_response(self, response, url):
        # bs4
        stateset = False
        await fhem.readingsBeginUpdate(self.hash)
        try:
            reading = "topic_unread_replies"
            keywords = self._attr_keywords_unread_replies
            if url == fhem_forum.URL_UNREAD:
                reading = "topic_unread"
                keywords = self._attr_keywords_unread
            elif url == fhem_forum.URL_PM:
                await self.handle_private_messages(response)

            if url != fhem_forum.URL_PM:
                entries = await utils.run_blocking(
                    functools.partial(self.get_soup_entries, response)
                )

                i = 1
                for entry in entries:
                    subject = entry.find("div", {"class": "recent_title"})
                    if subject is None:
                        continue

                    if not self.contains_keyword(subject.find("span").text, keywords):
                        continue

                    link_to_new = subject.findAll("a")[0]["href"]
                    title_to_new = subject.find("span").find("a").text

                    last_post = entry.find("div", {"class": "lastpost"}).findAll("a")
                    last_post_date = last_post[0]
                    last_post_name = last_post[1]
                    last_post_date["target"] = "_blank"
                    last_post_name["target"] = "_blank"
                    last_post_str = f"{last_post_date} von {last_post_name}"

                    ret = await fhem.readingsBulkUpdateIfChanged(
                        self.hash,
                        f"{reading}_{i:02d}",
                        f'<html><a href="{link_to_new}" target="_blank">'
                        + f"{title_to_new}</a>"
                        + f"<br>{last_post_str}</html>",
                    )

                    if i == 1 and (ret is not None or self.first_run is True):
                        self.first_run = False
                        await fhem.readingsBulkUpdateIfChanged(
                            self.hash,
                            "state",
                            f'<html><a href="{link_to_new}" target="_blank">'
                            + f"{title_to_new}</a>"
                            + f"<br>{last_post_str}</html>",
                        )

                    stateset = True

                    i += 1
                    if i > self._attr_max_topics:
                        break

                while i <= self._attr_max_topics:
                    await fhem.readingsBulkUpdateIfChanged(
                        self.hash, f"{reading}_{i:02d}", "-"
                    )
                    i += 1

        except Exception as ex:
            self.logger.exception(f"Failed to handle data from {url}")
            await fhem.readingsBulkUpdate(self.hash, "state", {ex}, 1)

        await fhem.readingsEndUpdate(self.hash, 1)

        return stateset
