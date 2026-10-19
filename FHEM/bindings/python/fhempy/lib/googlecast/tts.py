"""Text to speech helpers for googlecast.

Google's translate_tts endpoint only accepts about 200 characters per
request. Long texts are split at sentence boundaries, every part is
downloaded and the MP3 parts are joined to one file. A small HTTP server
serves that file and the fhempy icon to the cast device, so the whole
announcement plays as one media item and the display stays the same.
"""

import collections
import re
import secrets
import shutil
import socket
import tempfile
from pathlib import Path
from urllib.parse import quote

MAX_CHUNK_LEN = 200
MAX_STORED_FILES = 5
DISPLAY_LEN = 80
STATIC_DIR = Path(__file__).parent / "static"
ICON_PATH = "/static/fhempy_icon.png"


def split_text(text, max_len=MAX_CHUNK_LEN):
    """Split text into parts of at most max_len characters.

    Splits after sentence ends first, then after commas/semicolons/colons,
    then at spaces and only as a last resort inside a word.
    """
    text = " ".join(text.split())
    chunks = []
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        _add_part(chunks, sentence, max_len, [r"(?<=[,;:])\s+", r"\s+"])
    return chunks


def _add_part(chunks, part, max_len, separators):
    if not part:
        return
    if len(part) > max_len:
        if separators:
            for sub in re.split(separators[0], part):
                _add_part(chunks, sub, max_len, separators[1:])
        else:
            for i in range(0, len(part), max_len):
                chunks.append(part[i : i + max_len])
        return
    if chunks and len(chunks[-1]) + 1 + len(part) <= max_len:
        chunks[-1] += " " + part
    else:
        chunks.append(part)


def tts_url(text, lang, idx=0, total=1, scheme="https"):
    return (
        f"{scheme}://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob"
        f"&tl={quote(lang)}&q={quote(text)}"
        f"&total={total}&idx={idx}&textlen={len(text)}"
    )


def shorten(text, max_len=DISPLAY_LEN):
    text = " ".join(text.split())
    if len(text) <= max_len:
        return text
    cut = text[: max_len - 1]
    if " " in cut:
        cut = cut[: cut.rindex(" ")]
    return cut.rstrip(" ,;:.") + "…"


def strip_id3(data):
    """Remove ID3v2 header and ID3v1 trailer so MP3 parts can be joined."""
    if len(data) > 10 and data[:3] == b"ID3":
        size = 0
        for byte in data[6:10]:
            size = (size << 7) | (byte & 0x7F)
        footer = 10 if data[5] & 0x10 else 0
        data = data[10 + size + footer :]
    if len(data) >= 128 and data[-128:-125] == b"TAG":
        data = data[:-128]
    return data


async def fetch_tts(session, text, lang):
    """Download the speech for text and return one MP3 file as bytes."""
    chunks = split_text(text)
    parts = []
    for idx, chunk in enumerate(chunks):
        url = tts_url(chunk, lang, idx, len(chunks))
        async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as res:
            res.raise_for_status()
            parts.append(strip_id3(await res.read()))
    return b"".join(parts)


def local_ip_for(host):
    """Return the own IP address which is used to reach host."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect((host, 8009))
        return sock.getsockname()[0]
    finally:
        sock.close()


class TTSServer:
    """Serves generated MP3 files and the fhempy icon to cast devices."""

    def __init__(self):
        self.runner = None
        self.port = None
        self.requested_port = None
        self.files = collections.deque()
        self.directory = Path(tempfile.mkdtemp(prefix="fhempy_tts_"))

    @property
    def running(self):
        return self.runner is not None

    async def start(self, port=0):
        from aiohttp import web

        await self.stop()
        app = web.Application()
        # static routes handle Range requests and never list the directory
        app.router.add_static("/tts", self.directory)
        app.router.add_static("/static", STATIC_DIR)
        runner = web.AppRunner(app, access_log=None)
        await runner.setup()
        # IPv4 only: with port 0 an IPv6 socket would get a different port,
        # and the URL for the cast device uses the IPv4 address anyway
        site = web.TCPSite(runner, host="0.0.0.0", port=port)
        try:
            await site.start()
        except OSError:
            await runner.cleanup()
            raise
        self.runner = runner
        self.requested_port = port
        self.port = runner.addresses[0][1]

    async def stop(self):
        runner, self.runner = self.runner, None
        if runner is not None:
            await runner.cleanup()

    def add(self, mp3):
        """Store mp3 and return its path on the server. Blocking file I/O."""
        name = secrets.token_urlsafe(16) + ".mp3"
        (self.directory / name).write_bytes(mp3)
        self.files.append(name)
        while len(self.files) > MAX_STORED_FILES:
            (self.directory / self.files.popleft()).unlink(missing_ok=True)
        return "/tts/" + name

    def remove_files(self):
        """Delete all stored files. Blocking file I/O."""
        self.files.clear()
        shutil.rmtree(self.directory, ignore_errors=True)
