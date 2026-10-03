import asyncio
import base64
import pathlib
import shutil
from datetime import datetime

import aiohttp

from .. import fhem, generic
from ..core import pending_restore


class github_restore(generic.FhemModule):
    """Restore FHEM backup from github repository"""

    headers = {
        "Authorization": "",
        "Accept": "application/vnd.github+json",
    }

    def __init__(self, logger):
        super().__init__(logger)
        self.gh_token_ready = asyncio.Event()

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)

        attr_config = {
            "github_token": {"default": "", "help": "Personal github token"},
        }
        await self.set_attr_config(attr_config)

        set_config = {
            "restore_now": {},
        }
        await self.set_set_config(set_config)

        if len(args) != 5:
            return (
                "Usage: define my_restore fhempy github_restore "
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

    async def set_restore_now(self, hash, params):
        self.create_async_task(self.restore_backup())

    async def set_attr_github_token(self, hash):
        if self._attr_github_token == "":
            await fhem.readingsSingleUpdate(
                hash, "state", "Please set github_token attribute", 1
            )
            return

        self.gh_token_ready.set()
        github_restore.headers["Authorization"] = f"token {self._attr_github_token}"

    async def restore_backup(self):
        await self.gh_token_ready.wait()
        self.gh_token_ready.clear()

        await fhem.readingsSingleUpdate(self.hash, "state", "Restoring backup", 1)

        # get latest commit from self.directory
        url = f"https://api.github.com/repos/{self.gh_user}/{self.gh_repo}/commits?path={self.directory}"
        commits = await self.github_get(url)
        if not commits:
            await fhem.readingsSingleUpdate(
                self.hash, "state", "Failed to get commits", 1
            )
            return

        commit = commits[0]
        commit_sha = commit["sha"]
        commit_date = commit["commit"]["author"]["date"]
        commit_date = datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%SZ")
        commit_date = commit_date.strftime("%Y-%m-%d %H:%M:%S")

        # get tree recursively
        url = f"https://api.github.com/repos/{self.gh_user}/{self.gh_repo}/git/trees/{commit_sha}?recursive=1"
        tree = await self.github_get(url)
        if not tree:
            await fhem.readingsSingleUpdate(self.hash, "state", "Failed to get tree", 1)
            return

        # get all files in directory
        backup_files = []
        for entry in tree["tree"]:
            if entry["path"].startswith(self.directory):
                backup_files.append(entry)

        # drop zigbee2mqtt data of an earlier restore which wasn't applied yet
        shutil.rmtree(pending_restore.Z2M_PENDING_DIR, ignore_errors=True)

        # retrieve all backup files
        z2m_pending = False
        for backup_file in backup_files:
            if backup_file["type"] == "blob":
                restored_path = await self.restore_backup_file(backup_file)
                if restored_path is not None and restored_path.is_relative_to(
                    pending_restore.Z2M_PENDING_DIR
                ):
                    z2m_pending = True

        state = (
            "Backup restored<br>YOU MUST RESTART FHEM NOW, DO NOT SAVE BEFORE RESTARTING"
        )
        if z2m_pending:
            state += (
                "<br>zigbee2mqtt data will be applied "
                + "after the zigbee2mqtt installation, before it starts"
            )
        await fhem.readingsSingleUpdate(self.hash, "state", state, 1)

    async def restore_backup_file(self, backup_file):
        # get blob
        url = f"https://api.github.com/repos/{self.gh_user}/{self.gh_repo}/git/blobs/{backup_file['sha']}"
        blob = await self.github_get(url)
        if not blob:
            await fhem.readingsSingleUpdate(self.hash, "state", "Failed to get blob", 1)
            return None

        # decode blob
        content = base64.b64decode(blob["content"])

        # remove self.directory from path, zigbee2mqtt data is stored as
        # pending restore which zigbee2mqtt applies after its installation
        path = pending_restore.restore_path(
            pathlib.Path(backup_file["path"]).relative_to(self.directory)
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

        # update reading
        await fhem.readingsSingleUpdate(
            self.hash, "state", f"Restored {backup_file['path']}", 1
        )
        return path

    async def github_get(self, url):
        ret = None
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.get(url, headers=github_restore.headers) as resp:
                if resp.status < 400:
                    ret = await resp.json()
                else:
                    self.logger.error(
                        f"Failed to get {url} with HTTP error {resp.status}"
                    )
        return ret

    async def update_static_readings(self):
        await fhem.readingsSingleUpdateIfChanged(
            self.hash,
            "repository",
            f"<html><a href='{self.url}' target='_blank'>"
            + "Open repository (new tab/window)</a></html>",
            1,
        )
