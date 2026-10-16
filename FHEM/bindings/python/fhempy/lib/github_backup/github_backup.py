import asyncio
import base64
import functools
import hashlib
import io
import json
import pathlib
from datetime import datetime, timedelta

import aiohttp

from .. import fhem, generic, utils

# multiple of 3, so the base64 chunks can be joined
B64_CHUNK = 3 * 2**16


def read_file_for_github(filename):
    """Content as base64 bytes and git blob sha, run in a thread.

    base64 holds the GIL, encode in chunks so the event loop keeps running.
    """
    with open(filename, "rb") as fh:
        f_content = fh.read()
    header = f"blob {len(f_content)}\0"
    # git identifies blobs by sha1, not used for security
    sha = hashlib.sha1(  # NOSONAR
        header.encode("utf-8") + f_content, usedforsecurity=False
    ).hexdigest()
    content_view = memoryview(f_content)
    b64 = b"".join(
        base64.b64encode(content_view[i : i + B64_CHUNK])
        for i in range(0, len(f_content), B64_CHUNK)
    )
    return b64, sha


DEFAULT_BACKUP_FILES = ",".join(
    [
        "fhem.cfg",
        "configDB.db",
        "configDB.conf",
        "log/fhem.save",
        # FHEM's uniqueID, also holds passwords stored by FHEM modules
        # (setKeyValue), they can't be decrypted without it after a restore
        "FHEM/FhemUtils/uniqueID",
        "www/gplot/SVG*.gplot",
        ".fhempy/zigbee2mqtt/data/*.yaml",
        ".fhempy/zigbee2mqtt/data/*.json",
        ".fhempy/zigbee2mqtt/data/database.db",
        "esphome_config/*.yaml",
        # Matter fabric (keys of all paired devices)
        ".fhempy/matter_server/data/**/*",
    ]
)

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

HTTP_ERRORS = {
    401: "github_token is invalid or expired",
    403: "github_token has no write permission for the repository",
    404: "repository not found or github_token has no access to it",
}


class GithubError(Exception):
    def __init__(self, status, url):
        self.status = status
        reason = HTTP_ERRORS.get(status, "GitHub request failed")
        super().__init__(f"{reason} (HTTP {status})")
        self.url = url


def json_body(data, content):
    """JSON body with base64 content, without serializing the big string."""
    prefix = json.dumps(data)[:-1]
    if data:
        prefix += ", "
    return prefix.encode("utf-8") + b'"content": "' + content + b'"}'


class github_backup(generic.FhemModule):

    headers = {
        "Authorization": "",
        "Accept": "application/vnd.github+json",
    }

    def __init__(self, logger):
        super().__init__(logger)
        self.gh_token_ready = asyncio.Event()
        self.backup_lock = asyncio.Lock()

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)

        attr_config = {
            "backup_time": {
                "default": "03:38",
                "format": "time",
                "help": "Daily backup at a specific time. Format HH:MM, default 03:38.",
            },
            "github_token": {"default": "", "help": "Personal github token"},
            "backup_files": {
                "default": DEFAULT_BACKUP_FILES,
                "help": (
                    "Comma separated list of files to backup, wildcards "
                    + "(*, ** for subdirectories) are allowed.<br>"
                    + "Default:<br>"
                    + DEFAULT_BACKUP_FILES.replace(",", ", ")
                ),
            },
        }
        await self.set_attr_config(attr_config)

        set_config = {
            "backup_now": {},
        }
        await self.set_set_config(set_config)

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
        """JSON response, None if the file doesn't exist (yet)"""
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.get(url, headers=github_backup.headers) as resp:
                if resp.status == 404:
                    return None
                if resp.status >= 400:
                    raise GithubError(resp.status, url)
                return await resp.json()

    async def github_put(self, url, json_data, content):
        # encode in a thread and send the body from a BytesIO, aiohttp writes
        # it in chunks then; a plain bytes body is TLS encrypted in one go,
        # which blocked the event loop (and FHEM) for big files
        body = await utils.run_blocking(
            functools.partial(json_body, json_data, content)
        )
        headers = dict(github_backup.headers)
        headers["Content-Type"] = "application/json"
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.put(url, data=io.BytesIO(body), headers=headers) as resp:
                if resp.status >= 400:
                    raise GithubError(resp.status, url)
        return True

    async def b64encode_file(self, filename):
        return await utils.run_blocking(
            functools.partial(read_file_for_github, filename)
        )

    def contents_url(self, filename):
        return (
            f"https://api.github.com/repos/{self.gh_user}/"
            + f"{self.gh_repo}/contents/{self.directory}/{filename}"
        )

    async def get_sha_from_file(self, filename):
        resp = await self.github_get(self.contents_url(filename))
        if resp is not None and "sha" in resp:
            return resp["sha"]
        return None

    async def upload_file(self, filename):
        """Returns "uploaded" or "unchanged", raises on errors"""
        # get current sha
        f_sha = await self.get_sha_from_file(filename)

        content, sha = await self.b64encode_file(filename)

        if f_sha == sha:
            # no update required
            return "unchanged"

        # upload file
        data_msg = {
            "message": f"{self.directory} - {filename} backup",
        }
        if f_sha:
            data_msg["sha"] = f_sha

        await self.github_put(self.contents_url(filename), data_msg, content)
        return "uploaded"

    async def backup_loop(self):
        await self.gh_token_ready.wait()
        # readings of older versions, one per failed file which never vanished
        # (file names contain . or /, unlike last_backup)
        await fhem.CommandDeleteReading(
            self.hash, f"{self.hash['NAME']} .*[./].*_backup"
        )
        while True:
            await self.do_backup()
            now = datetime.today()
            seconds_till_time = (self._attr_backup_time - now).seconds
            await fhem.readingsSingleUpdate(
                self.hash,
                "next_backup",
                (now + timedelta(seconds=seconds_till_time)).strftime(TIME_FORMAT),
                1,
            )
            await asyncio.sleep(seconds_till_time)

    def files_to_backup(self):
        files = []
        for pattern in self._attr_backup_files.split(","):
            pattern = pattern.strip()
            if pattern == "":
                continue
            for filepath in sorted(pathlib.Path(".").glob(pattern)):
                if filepath.is_file() and filepath not in files:
                    files.append(filepath)
        return files

    async def do_backup(self):
        if self._attr_github_token == "":
            return
        if self.backup_lock.locked():
            # backup_now while a backup is running
            return

        async with self.backup_lock:
            result = await self.run_backup()
        await self.update_backup_readings(result)

    async def run_backup(self):
        result = {"uploaded": [], "unchanged": [], "failed": [], "error": None}
        files = await utils.run_blocking(functools.partial(self.files_to_backup))
        if not files:
            result["error"] = "No file found, check attribute backup_files"
            return result

        for filepath in files:
            try:
                result[await self.upload_file(filepath)].append(str(filepath))
            except Exception as exc:
                result["failed"].append(str(filepath))
                if result["error"] is None:
                    result["error"] = f"{filepath}: {exc}"
                if isinstance(exc, GithubError):
                    self.logger.error(f"Failed to upload {filepath}: {exc}")
                else:
                    self.logger.exception(f"Failed to upload {filepath}")
        return result

    async def update_backup_readings(self, result):
        now = datetime.now().strftime(TIME_FORMAT)
        success = result["error"] is None
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdate(self.hash, "state", "ok" if success else "failed")
        await fhem.readingsBulkUpdate(self.hash, "last_backup", now)
        if success:
            await fhem.readingsBulkUpdate(self.hash, "last_successful_backup", now)
        else:
            await fhem.readingsBulkUpdate(self.hash, "error", result["error"])
            await fhem.readingsBulkUpdate(
                self.hash, "failed_files", ",".join(result["failed"]) or "-"
            )
        for key in ["uploaded", "unchanged", "failed"]:
            await fhem.readingsBulkUpdate(self.hash, f"files_{key}", len(result[key]))
        await fhem.readingsEndUpdate(self.hash, 1)
        if success:
            # the error of an earlier backup is history now
            await fhem.CommandDeleteReading(
                self.hash, f"{self.hash['NAME']} (error|failed_files)"
            )

    async def update_static_readings(self):
        await fhem.readingsSingleUpdateIfChanged(
            self.hash,
            "repository",
            f"<html><a href='{self.url}' target='_blank'>"
            + "Open repository (new tab/window)</a></html>",
            1,
        )
