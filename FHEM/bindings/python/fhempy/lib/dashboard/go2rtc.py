"""Camera streams for the tablets with go2rtc (https://github.com/AlexxIT/go2rtc).

go2rtc turns almost every camera (RTSP, ONVIF, Doorbird, Reolink, ESPHome...)
into WebRTC, the tablets show the picture without delay and can talk back to
cameras with a speaker. An existing go2rtc (e.g. of Frigate or Home Assistant)
is used if one is configured, otherwise fhempy downloads go2rtc and runs it
with the cameras of attribute cameras."""

import asyncio
import functools
import json
import os
import platform
import re
import stat
import subprocess

from .. import utils
from ..core import child_process

VERSION = "1.9.9"
DOWNLOAD_URL = "https://github.com/AlexxIT/go2rtc/releases/download/v{}/go2rtc_linux_{}"
ARCHITECTURES = {
    "aarch64": "arm64",
    "arm64": "arm64",
    "armv6l": "armv6",
    "armv7l": "arm",
    "armv8l": "arm",
    "x86_64": "amd64",
    "amd64": "amd64",
    "i386": "i386",
    "i686": "i386",
}
# own ports, a go2rtc of Frigate or Home Assistant uses 1984/8555
API_PORT = 11984
WEBRTC_PORT = 18555
STREAM_NAME = re.compile(r"^[A-Za-z0-9_.\-]{1,64}$")


def base_directory():
    return os.path.join(os.getcwd(), ".fhempy", "go2rtc")


def binary():
    return os.path.join(base_directory(), f"go2rtc-{VERSION}")


def config_path():
    return os.path.join(base_directory(), "go2rtc.yaml")


def parse_cameras(text):
    """'Haustuer=rtsp://... Garten=onvif://...' -> {name: source}"""
    cameras = {}
    for part in re.split(r"\s+", str(text or "").strip()):
        name, sep, source = part.partition("=")
        if sep and STREAM_NAME.match(name) and source:
            cameras[name] = source
    return cameras


def config_text(cameras):
    """go2rtc.yaml, YAML is a superset of JSON"""
    return json.dumps(
        {
            "api": {"listen": f"127.0.0.1:{API_PORT}", "origin": "*"},
            "rtsp": {"listen": ""},
            "webrtc": {"listen": f":{WEBRTC_PORT}"},
            "streams": cameras,
        },
        indent=2,
    )


def architecture():
    machine = platform.machine().lower()
    if machine not in ARCHITECTURES:
        raise RuntimeError(f"go2rtc is not available for {machine}")
    return ARCHITECTURES[machine]


def _write_binary(data):
    os.makedirs(base_directory(), exist_ok=True)
    path = binary()
    tmp = path + ".tmp"
    with open(tmp, "wb") as file:
        file.write(data)
    os.chmod(tmp, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP)
    os.replace(tmp, path)
    # old versions
    for name in os.listdir(base_directory()):
        if name.startswith("go2rtc-") and name != os.path.basename(path):
            os.remove(os.path.join(base_directory(), name))


def _write_config(cameras):
    os.makedirs(base_directory(), exist_ok=True)
    with open(config_path(), "w", encoding="utf-8") as file:
        file.write(config_text(cameras))


async def install(logger):
    import aiohttp

    if await utils.run_blocking(functools.partial(os.path.isfile, binary())):
        return
    url = DOWNLOAD_URL.format(VERSION, architecture())
    logger.info(f"Downloading go2rtc {VERSION}")
    timeout = aiohttp.ClientTimeout(total=600, sock_read=60)
    async with (
        aiohttp.ClientSession(timeout=timeout) as session,
        session.get(url) as resp,
    ):
        resp.raise_for_status()
        data = await resp.read()
    await utils.run_blocking(functools.partial(_write_binary, data))


class Go2rtc:
    """the go2rtc of fhempy or an existing one (url)"""

    def __init__(self, logger):
        self.logger = logger
        self.proc = None
        self.url = ""

    async def start(self, url, cameras):
        await self.stop()
        if url:
            self.url = url.rstrip("/")
            return
        if not cameras:
            self.url = ""
            return
        await install(self.logger)
        await utils.run_blocking(functools.partial(_write_config, cameras))
        path = child_process.log_path("go2rtc")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.proc = child_process.start(
            [binary(), "-config", config_path()],
            cwd=base_directory(),
            stdin=subprocess.DEVNULL,
            output_log=child_process.OutputLog(path, self.logger),
        )
        self.url = f"http://127.0.0.1:{API_PORT}"  # NOSONAR local only

    async def stop(self):
        proc, self.proc = self.proc, None
        if proc is not None:
            await child_process.stop(proc)

    async def request(self, method, path, **kwargs):
        import aiohttp

        if not self.url:
            raise RuntimeError("no camera configured")
        timeout = aiohttp.ClientTimeout(total=15)
        async with (
            aiohttp.ClientSession(timeout=timeout) as session,
            session.request(method, self.url + path, **kwargs) as resp,
        ):
            body = await resp.read()
            return resp.status, resp.headers.get("Content-Type", ""), body

    async def streams(self):
        try:
            status, _, body = await self.request("GET", "/api/streams")
        except (RuntimeError, OSError, asyncio.TimeoutError):
            return []
        if status != 200:
            return []
        try:
            return sorted(json.loads(body))
        except (ValueError, TypeError):
            return []

    async def webrtc(self, stream, offer):
        """SDP offer of the tablet -> SDP answer of go2rtc"""
        status, _, body = await self.request(
            "POST",
            f"/api/webrtc?src={stream}",
            data=offer.encode(),
            headers={"Content-Type": "application/sdp"},
        )
        if status not in (200, 201):
            raise RuntimeError(f"go2rtc answered {status}")
        return body.decode()

    async def snapshot(self, stream):
        status, content_type, body = await self.request(
            "GET", f"/api/frame.jpeg?src={stream}"
        )
        if status != 200:
            raise RuntimeError(f"go2rtc answered {status}")
        return content_type or "image/jpeg", body
