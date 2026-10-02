import json
import time

import pytest
from fhempy.lib import fhem, fhem_pythonbinding


@pytest.mark.asyncio
async def test_reply_without_waiting_listener_is_ignored():
    pb = fhempy_instance()
    reply = {"awaitId": 12345678, "error": 0, "result": ""}

    # must not be handled as function call (which needs "id" and "msgtype")
    await pb.handle_message(json.dumps(reply), reply)

    assert pb._msg_listeners == {}


@pytest.mark.asyncio
async def test_reply_is_passed_to_waiting_listener():
    pb = fhempy_instance()
    received = []
    pb.register_msg_listener(received.append, 12345678)
    msg = json.dumps({"awaitId": 12345678, "error": 0, "result": "ok"})

    await pb.handle_message(msg, json.loads(msg))

    assert received == [json.loads(msg)]
    assert pb._msg_listeners == {}


def test_msg_handling_completed_removes_stale_messages():
    pb = fhempy_instance()
    now = time.time()
    pb.msg_received_time = {
        1: {"time": now, "payload": "done"},
        2: {"time": now - 120, "payload": "stale"},
        3: {"time": now, "payload": "running"},
    }

    pb.msg_handling_completed({"id": 1})

    assert list(pb.msg_received_time) == [3]


@pytest.mark.asyncio
async def test_send_back_error_without_received_timestamp(monkeypatch):
    monkeypatch.setattr(fhem, "function_active", ["dev"])
    pb = fhempy_instance()
    sent = []

    async def send(msg):
        sent.append(msg)

    pb.wsconnection.send = send
    await pb.sendBackError({"id": 4711, "NAME": "dev"}, "failed")

    assert len(sent) == 1


class FakeWebsocket:
    async def send(self, msg):
        pass


def fhempy_instance():
    return fhem_pythonbinding.fhempy(FakeWebsocket())
