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
    monkeypatch.setattr(memory, "freeze_objects", lambda: None)
    task = asyncio.create_task(memory.trim_periodically())
    await asyncio.sleep(0.1)
    task.cancel()
    if memory._get_malloc_trim() is None:
        assert calls == []
    else:
        assert len(calls) >= 2


def test_freeze_objects(monkeypatch):
    import gc

    monkeypatch.setattr(memory, "_last_unfreeze", None)
    try:
        memory.freeze_objects()
        frozen = gc.get_freeze_count()
        assert frozen > 0
        # once per UNFREEZE_INTERVAL everything is checked again
        monkeypatch.setattr(memory, "UNFREEZE_INTERVAL", 0)
        unfreeze = []
        real_unfreeze = gc.unfreeze
        monkeypatch.setattr(gc, "unfreeze", lambda: unfreeze.append(real_unfreeze()))
        memory.freeze_objects()
        assert len(unfreeze) == 1
        assert gc.get_freeze_count() > 0
    finally:
        gc.unfreeze()


@pytest.mark.asyncio
async def test_freeze_without_malloc_trim(monkeypatch):
    calls = []
    monkeypatch.setattr(memory, "_loaded", True)
    monkeypatch.setattr(memory, "_malloc_trim", None)
    monkeypatch.setattr(memory, "FIRST_TRIM_DELAY", 0)
    monkeypatch.setattr(memory, "TRIM_INTERVAL", 0.01)
    monkeypatch.setattr(memory, "freeze_objects", lambda: calls.append(1))
    task = asyncio.create_task(memory.trim_periodically())
    await asyncio.sleep(0.1)
    task.cancel()
    assert len(calls) >= 2
