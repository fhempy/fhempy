import asyncio

import pytest
from fhempy.lib.xiaomi_gateway3.core import utils


class HangingMiIO:
    def __init__(self, *_):
        pass

    async def send(self, *_):
        await asyncio.Event().wait()


class FailingMiIO(HangingMiIO):
    async def send(self, *_):
        await asyncio.sleep(0)
        raise OSError("unreachable")


@pytest.mark.asyncio
async def test_get_room_mapping_propagates_cancel(monkeypatch):
    monkeypatch.setattr(utils, "AsyncMiIO", HangingMiIO)
    task = asyncio.create_task(utils.get_room_mapping(None, "host", "token"))
    await asyncio.sleep(0.05)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


@pytest.mark.asyncio
async def test_get_room_mapping_returns_error_text(monkeypatch):
    monkeypatch.setattr(utils, "AsyncMiIO", FailingMiIO)
    assert await utils.get_room_mapping(None, "host", "token") == (
        "Can't get from cloud"
    )
