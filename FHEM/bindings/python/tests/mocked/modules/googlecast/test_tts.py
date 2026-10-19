import aiohttp
import pytest
from aiohttp import web

from fhempy.lib.googlecast import tts


def test_split_text_short():
    assert tts.split_text("  Hallo   Welt ") == ["Hallo Welt"]
    assert tts.split_text("") == []


def test_split_text_long_keeps_sentences_together():
    sentence = "Das ist ein Satz mit ein paar Wörtern."
    text = " ".join([sentence] * 20)
    chunks = tts.split_text(text)
    assert len(chunks) > 1
    assert all(len(c) <= tts.MAX_CHUNK_LEN for c in chunks)
    assert all(c.endswith(".") for c in chunks)
    assert " ".join(chunks) == text


def test_split_text_without_punctuation():
    text = " ".join(["Wort"] * 100)
    chunks = tts.split_text(text)
    assert all(len(c) <= tts.MAX_CHUNK_LEN for c in chunks)
    assert " ".join(chunks) == text


def test_split_text_very_long_word():
    chunks = tts.split_text("x" * 450)
    assert [len(c) for c in chunks] == [200, 200, 50]


def test_shorten():
    assert tts.shorten("kurz") == "kurz"
    short = tts.shorten("Heute wird es sonnig, " * 10)
    assert len(short) <= tts.DISPLAY_LEN
    assert short.endswith("…")
    assert short.startswith("Heute wird es sonnig")


def test_tts_url_quotes_text():
    url = tts.tts_url("Grüße & mehr", "de", 1, 3)
    assert url.startswith("https://translate.google.com/translate_tts?")
    assert "q=Gr%C3%BC%C3%9Fe%20%26%20mehr" in url
    assert "tl=de" in url and "idx=1" in url and "total=3" in url


def test_strip_id3():
    frames = b"\xff\xfb\x90\x00" + b"a" * 50
    id3v2 = b"ID3\x04\x00\x00\x00\x00\x00\x05" + b"12345"
    id3v1 = b"TAG" + b"\x00" * 125
    assert tts.strip_id3(id3v2 + frames + id3v1) == frames
    assert tts.strip_id3(frames) == frames


@pytest.mark.asyncio
async def test_server_serves_files_ranges_and_icon():
    server = tts.TTSServer()
    await server.start(0)
    try:
        assert server.running and server.port > 0
        base = f"http://127.0.0.1:{server.port}"
        path = server.add(b"0123456789")
        async with aiohttp.ClientSession() as session:
            async with session.get(base + path) as res:
                assert res.status == 200
                assert res.content_type == "audio/mpeg"
                assert await res.read() == b"0123456789"
            async with session.get(base + path, headers={"Range": "bytes=2-5"}) as res:
                assert res.status == 206
                assert await res.read() == b"2345"
            async with session.get(base + "/tts/unknown.mp3") as res:
                assert res.status == 404
            async with session.get(base + "/tts/") as res:
                assert res.status in (403, 404)
            async with session.get(base + tts.ICON_PATH) as res:
                assert res.status == 200
                assert (await res.read())[:8] == b"\x89PNG\r\n\x1a\n"
    finally:
        await server.stop()
        server.remove_files()
    assert not server.running
    assert not server.directory.exists()


def test_server_keeps_only_recent_files():
    server = tts.TTSServer()
    try:
        paths = [server.add(bytes([i])) for i in range(tts.MAX_STORED_FILES + 2)]
        stored = sorted(p.name for p in server.directory.iterdir())
        assert len(stored) == tts.MAX_STORED_FILES
        assert paths[0].split("/")[-1] not in stored
        assert paths[-1].split("/")[-1] in stored
    finally:
        server.remove_files()


@pytest.mark.asyncio
async def test_fetch_tts_joins_parts(monkeypatch):
    requests = []

    async def handler(request):
        requests.append(dict(request.query))
        return web.Response(
            body=b"ID3\x04\x00\x00\x00\x00\x00\x01X" + request.query["idx"].encode(),
            content_type="audio/mpeg",
        )

    app = web.Application()
    app.router.add_get("/translate_tts", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = runner.addresses[0][1]

    orig_url = tts.tts_url

    def local_url(text, lang, idx=0, total=1, scheme="https"):
        return orig_url(text, lang, idx, total, "http").replace(
            "translate.google.com", f"127.0.0.1:{port}"
        )

    monkeypatch.setattr(tts, "tts_url", local_url)
    try:
        async with aiohttp.ClientSession() as session:
            mp3 = await tts.fetch_tts(session, "Satz eins. " * 40, "de")
    finally:
        await runner.cleanup()
    assert len(requests) > 1
    assert mp3 == "".join(str(i) for i in range(len(requests))).encode()
    assert all(r["tl"] == "de" for r in requests)
