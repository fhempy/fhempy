import base64
import json
import struct

import pytest
from Cryptodome.Cipher import AES

from fhempy.lib.gree_climate import discovery as gree
from fhempy.lib.goodwe import discovery as goodwe
from fhempy.lib.miio import discovery as miio
from fhempy.lib.tuya import discovery as tuya


def tuya_package(payload):
    return tuya.PREFIX + bytes(16) + payload + bytes(4) + bytes.fromhex("0000aa55")


def pkcs7(data):
    pad = 16 - len(data) % 16
    return data + bytes([pad]) * pad


def test_tuya_plain_and_encrypted():
    info = {"ip": "192.168.1.30", "gwId": "bf123", "version": "3.3"}
    plain = json.dumps(info).encode()
    assert tuya.parse(tuya_package(plain)) == info
    encrypted = AES.new(tuya.UDP_KEY, AES.MODE_ECB).encrypt(pkcs7(plain))
    assert tuya.parse(tuya_package(encrypted)) == info
    assert tuya.parse(b"garbage") is None
    assert tuya.parse(tuya_package(b'{"foo": 1}')) is None


def gree_answer(info, gcm):
    data = json.dumps(info).encode()
    if gcm:
        cipher = AES.new(gree.GCM_KEY, AES.MODE_GCM, nonce=gree.GCM_NONCE)
        cipher.update(gree.GCM_AAD)
        pack, tag = cipher.encrypt_and_digest(data)
        answer = {"t": "pack", "pack": base64.b64encode(pack).decode()}
        answer["tag"] = base64.b64encode(tag).decode()
    else:
        pack = AES.new(gree.ECB_KEY, AES.MODE_ECB).encrypt(pkcs7(data))
        answer = {"t": "pack", "pack": base64.b64encode(pack).decode()}
    return json.dumps(answer).encode()


@pytest.mark.parametrize("gcm", [False, True])
def test_gree(gcm):
    answer = gree_answer({"t": "dev", "mac": "f4911e", "name": "Office"}, gcm)
    assert gree.parse(answer) == ("f4911e", "Office")
    assert gree.parse(b'{"t": "scan"}') is None
    assert gree.parse(b"not json") is None


def test_miio():
    answer = bytes.fromhex("21310020") + bytes(4) + struct.pack(">I", 1234)
    answer += bytes(20)
    assert miio.parse(answer) == 1234
    # our own hello isn't an answer
    assert miio.parse(miio.HELLO) is None
    assert miio.title_from_hostname("roborock-vacuum-s5_miio123") == (
        "roborock vacuum s5"
    )


def test_goodwe():
    assert goodwe.parse(b"192.168.1.40,289C6E000000,Solar-WiFi", "1.2.3.4") == (
        "192.168.1.40",
        "289C6E000000",
        "Solar-WiFi",
    )
    assert goodwe.parse(b"nothing", "1.2.3.4") is None


class FakeContext:
    def __init__(self, answers):
        self.answers = answers
        self.results = []

    async def udp_broadcast(self, port, payload, wait=3, listen_port=None):
        return self.answers

    async def hostname(self, ip):
        return "roborock-vacuum-s5_miio1234"

    def found(self, **values):
        self.results.append(values)


@pytest.mark.asyncio
async def test_miio_search_once_per_device():
    answer = bytes.fromhex("21310020") + bytes(4) + struct.pack(">I", 7) + bytes(20)
    ctx = FakeContext([(answer, "192.168.1.50"), (answer, "192.168.1.50")])
    await miio.search(ctx)
    assert ctx.results == [
        {
            "id": "7",
            "ip": "192.168.1.50",
            "title": "Xiaomi roborock vacuum s5 (192.168.1.50)",
            "model": "roborock vacuum s5",
        }
    ]
