import asyncio
import base64
import hashlib
import pathlib
from datetime import datetime

import aiohttp

from .. import fhem, generic


class github_backup(generic.FhemModule):

    headers = {
        "Authorization": "",
        "Accept": "application/vnd.github+json",
    }

    def __init__(self, logger):
        super().__init__(logger)

        self.gh_token_ready = asyncio.Event()

        attr_config = {
            "backup_time": {
                "default": "03:38",
                "format": "time",
                "help": "Daily backup at a specific time. Format HH:MM, default 03:38.",
            },
            "github_token": {"default": "", "help": "Personal github token"},
            "backup_files": {
                "default": (
                    "fhem.cfg,configDB.db,configDB.conf,log/fhem.save,"
                    + ".fhempy/zigbee2mqtt/data/configuration.yaml,"
                    + "esphome_config/*.yaml"
                ),
                "help": (
                    "Comma separated list of files to backup.<br>"
                    + "Default:<br>"
                    + "fhem.cfg,configDB.db,configDB.conf,log/fhem.save,"
                    + ".fhempy/zigbee2mqtt/data/configuration.yaml,"
                    + "esphome_config/*.yaml"
                ),
            },
        }
        self.set_attr_config(attr_config)

        set_config = {
            "backup_now": {},
        }
        self.set_set_config(set_config)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) != 5:
            return (
                "Usage: define my_backup fhempy github_backup"
                + " https://github.com/xxx/fhem_backup master_fhem_rpi"
            )

        self.url = args[3]
        self.gh_user = self.url.split("/")[-2]
        self.gh_repo = self.url.split("/")[-1]
        self.directory = args[4]

        icon = await fhem.AttrVal(self.hash["NAME"], "icon", "")
        if icon == "":
            await fhem.CommandAttr(self.hash, f"{self.hash['NAME']} icon system_backup")
            await fhem.CommandAttr(
                self.hash,
                f"{self.hash['NAME']} devStateIcon "
                + "failed:message_attention ok:message_ok",
            )

        # do this to check if gh token is set
        await self.set_attr_github_token(hash)

        self.create_async_task(self.update_static_readings())
        self.create_async_task(self.backup_loop())

    async def set_backup_now(self, hash, params):
        self.create_async_task(self.do_backup())

    async def set_attr_github_token(self, hash):
        if self._attr_github_token == "":
            await fhem.readingsSingleUpdate(
                hash, "state", "Please set github_token attribute", 1
            )
            return

        self.gh_token_ready.set()
        github_backup.headers["Authorization"] = f"token {self._attr_github_token}"

    async def github_get(self, url):
        ret = None
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.get(url, headers=github_backup.headers) as resp:
                if resp.status < 400:
                    ret = await resp.json()
                else:
                    self.logger.error(
                        f"Failed to get {url} with HTTP error {resp.status}"
                    )
        return ret

    async def github_put(self, url, json_data):
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.put(
                url, json=json_data, headers=github_backup.headers
            ) as resp:
                if resp.status < 400:
                    return True
                else:
                    self.logger.error(
                        f"Failed to put {url} with HTTP error {resp.status}"
                    )
        return False

    async def b64encode_file(self, filename):
        fh = open(filename, "rb")
        f_content = fh.read()
        fh.close()
        header = f"blob {len(f_content)}\0"
        gh_sha_content = header.encode("utf-8") + f_content
        sha = hashlib.sha1(gh_sha_content).hexdigest()
        b64_bytes = base64.b64encode(f_content)
        return b64_bytes.decode("ascii"), sha

    async def get_sha_from_file(self, filename):
        resp = await self.github_get(
            f"https://api.github.com/repos/{self.gh_user}/"
            + f"{self.gh_repo}/contents/{self.directory}/{filename}"
        )
        if resp is not None and "sha" in resp:
            return resp["sha"]
        return None

    async def upload_file(self, filename):
        try:
            # get current sha
            f_sha = await self.get_sha_from_file(filename)

            content, sha = await self.b64encode_file(filename)

            if f_sha == sha:
                # no update required
                return True

            # upload file
            data_msg = {
                "message": f"{self.directory} - {filename} backup",
                "content": content,
            }
            if f_sha:
                data_msg["sha"] = f_sha

            await self.github_put(
                f"https://api.github.com/repos/{self.gh_user}/"
                + f"{self.gh_repo}/contents/{self.directory}/{filename}",
                data_msg,
            )
            return True
        except Exception:
            await fhem.readingsSingleUpdateIfChanged(
                self.hash, f"{filename}_backup", "failed", 1
            )
            self.logger.exception(f"Failed to upload file {filename}")
        return False

    async def backup_loop(self):
        await self.gh_token_ready.wait()
        while True:
            await self.do_backup()
            now = datetime.today()
            seconds_till_time = (self._attr_backup_time - now).seconds
            await asyncio.sleep(seconds_till_time)

    async def do_backup(self):
        if self._attr_github_token == "":
            return

        state_val = "ok"
        for file in self._attr_backup_files.split(","):
            filepaths = pathlib.Path(".").glob(file)
            for filepath in filepaths:
                if not filepath.is_file():
                    continue

                if not await self.upload_file(filepath):
                    state_val = "failed"

        await fhem.readingsSingleUpdate(self.hash, "state", state_val, 1)

    async def update_static_readings(self):
        await fhem.readingsSingleUpdateIfChanged(
            self.hash,
            "repository",
            f"<html><a href='{self.url}' target='_blank'>"
            + "Open repository (new tab/window)</a></html>",
            1,
        )
