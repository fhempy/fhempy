import asyncio

import pytest
from fhempy.lib.core import memory


def test_trim_doesnt_fail():
    # glibc: memory given back or nothing to give back, other libc: False
    assert memory.trim() in (True, False)


def test_trim_without_malloc_trim(monkeypatch):
    monkeypatch.setattr(memory, "_loaded", True)
    monkeypatch.setattr(memory, "_malloc_trim", None)
    assert memory.trim() is False


@pytest.mark.asyncio
async def test_trim_periodically(monkeypatch):
    calls = []
    monkeypatch.setattr(memory, "FIRST_TRIM_DELAY", 0)
    monkeypatch.setattr(memory, "TRIM_INTERVAL", 0.01)
    monkeypatch.setattr(memory, "trim", lambda: calls.append(1))
    monkeypatch.setattr(memory, "freeze_objects", lambda check_all=False: None)
    task = asyncio.create_task(memory.trim_periodically())
    await asyncio.sleep(0.1)
    task.cancel()
    if memory._get_malloc_trim() is None:
        assert calls == []
    else:
        assert len(calls) >= 2


def test_freeze_objects(monkeypatch):
    import gc

    try:
        memory.freeze_objects()
        assert gc.get_freeze_count() > 0
        assert not memory.collecting
        # only a full check unfreezes the frozen objects
        unfreeze = []
        real_unfreeze = gc.unfreeze
        monkeypatch.setattr(gc, "unfreeze", lambda: unfreeze.append(real_unfreeze()))
        memory.freeze_objects()
        assert unfreeze == []
        memory.freeze_objects(check_all=True)
        assert len(unfreeze) == 1
        assert gc.get_freeze_count() > 0
    finally:
        gc.unfreeze()


def test_collection_started_since(monkeypatch):
    import time

    before = time.monotonic()
    try:
        memory.freeze_objects()
    finally:
        import gc

        gc.unfreeze()
    assert memory.collection_started_since(before)
    assert not memory.collection_started_since(time.monotonic() + 1)


@pytest.mark.asyncio
async def test_no_full_check_without_removed_device(monkeypatch):
    calls = []
    monkeypatch.setattr(memory, "FIRST_TRIM_DELAY", 0)
    monkeypatch.setattr(memory, "TRIM_INTERVAL", 0.01)
    monkeypatch.setattr(memory, "trim", lambda: None)
    monkeypatch.setattr(
        memory, "freeze_objects", lambda check_all=False: calls.append(check_all)
    )
    task = asyncio.create_task(memory.trim_periodically())
    await asyncio.sleep(0.1)
    task.cancel()
    assert len(calls) >= 2
    assert not any(calls)


@pytest.mark.asyncio
async def test_full_check_after_removed_devices(monkeypatch):
    import gc

    calls = []
    monkeypatch.setattr(memory, "FIRST_TRIM_DELAY", 0)
    monkeypatch.setattr(memory, "TRIM_INTERVAL", 3600)
    monkeypatch.setattr(memory, "REMOVAL_SETTLE", 0.05)
    monkeypatch.setattr(memory, "trim", lambda: None)
    monkeypatch.setattr(gc, "get_freeze_count", lambda: 1)
    monkeypatch.setattr(
        memory, "freeze_objects", lambda check_all=False: calls.append(check_all)
    )
    task = asyncio.create_task(memory.trim_periodically())
    await asyncio.sleep(0.02)
    assert calls == [False]
    # several devices removed one after another: one full check after them
    for _ in range(3):
        memory.device_removed()
        await asyncio.sleep(0.02)
    assert calls == [False]
    await asyncio.sleep(0.1)
    task.cancel()
    assert calls == [False, True]


@pytest.mark.asyncio
async def test_freeze_without_malloc_trim(monkeypatch):
    calls = []
    monkeypatch.setattr(memory, "_loaded", True)
    monkeypatch.setattr(memory, "_malloc_trim", None)
    monkeypatch.setattr(memory, "FIRST_TRIM_DELAY", 0)
    monkeypatch.setattr(memory, "TRIM_INTERVAL", 0.01)
    monkeypatch.setattr(
        memory, "freeze_objects", lambda check_all=False: calls.append(1)
    )
    task = asyncio.create_task(memory.trim_periodically())
    await asyncio.sleep(0.1)
    task.cancel()
    assert len(calls) >= 2
