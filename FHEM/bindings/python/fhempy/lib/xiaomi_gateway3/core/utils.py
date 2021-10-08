import json
import logging
import random
import re
import string
import time
import functools
from typing import List, Optional

from fhempy.lib import utils

import requests

from .mini_miio import SyncmiIO
from .shell import TelnetShell
from .xiaomi_cloud import MiCloud

DOMAIN = "xiaomi_gateway3"

_LOGGER = logging.getLogger(__name__)


# new miio adds colors to logs
RE_JSON1 = re.compile(b"msg:(.+) length:([0-9]+) bytes")
RE_JSON2 = re.compile(b"{.+}")


def extract_jsons(raw) -> List[bytes]:
    """There can be multiple concatenated json on one line. And sometimes the
    length does not match the message."""
    m = RE_JSON1.search(raw)
    if m:
        length = int(m[2])
        raw = m[1][:length]
    else:
        m = RE_JSON2.search(raw)
        raw = m[0]
    return raw.replace(b"}{", b"}\n{").split(b"\n")


def migrate_options(data):
    data = dict(data)
    options = {k: data.pop(k) for k in ("ble", "zha") if k in data}
    return {"data": data, "options": options}


def check_mgl03(host: str, token: str, telnet_cmd: Optional[str]) -> Optional[str]:
    try:
        # 1. try connect with telnet (custom firmware)?
        shell = TelnetShell(host)
        # 1.1. check token with telnet
        return None if shell.get_token() == token else "wrong_token"
    except:
        if not telnet_cmd:
            return "cant_connect"

    # 2. try connect with miio
    miio = SyncmiIO(host, token)
    info = miio.info()
    # fw 1.4.6_0012 without cloud will respond with a blank string reply
    if info is None:
        # if device_id not None - device works but not answer on commands
        return "wrong_token" if miio.device_id else "cant_connect"

    # 3. check if right model
    if info and info["model"] != "lumi.gateway.mgl03":
        return "wrong_model"

    raw = json.loads(telnet_cmd)
    # fw 1.4.6_0043+ won't answer on cmd without cloud, so don't check answer
    miio.send(raw["method"], raw.get("params"))

    # waiting for telnet to start
    time.sleep(1)

    try:
        # 4. check if telnet command helps
        TelnetShell(host)
    except:
        return "wrong_telnet"


def get_lan_key(host: str, token: str):
    device = SyncmiIO(host, token)
    resp = device.send("get_lumi_dpf_aes_key")
    if resp is None:
        return "Can't connect to gateway"
    if len(resp[0]) == 16:
        return resp[0]
    key = "".join(
        random.choice(string.ascii_lowercase + string.digits) for _ in range(16)
    )
    resp = device.send("set_lumi_dpf_aes_key", [key])
    if resp[0] == "ok":
        return key
    return "Can't update gateway key"


async def get_room_mapping(cloud: MiCloud, host: str, token: str):
    try:
        device = SyncmiIO(host, token)
        local_rooms = device.send("get_room_mapping")
        cloud_rooms = await cloud.get_rooms()
        result = ""
        for local_id, cloud_id in local_rooms:
            cloud_name = next(
                (p["name"] for p in cloud_rooms if p["id"] == cloud_id), "-"
            )
            result += f"\n- {local_id}: {cloud_name}"
        return result

    except:
        return "Can't get from cloud"


async def get_bindkey(cloud: MiCloud, did: str):
    bindkey = await cloud.get_bindkey(did)
    if bindkey is None:
        return "Can't get from cloud"
    if bindkey.endswith("FFFFFFFF"):
        return "Not needed"
    return bindkey


def reverse_mac(s: str):
    return f"{s[10:]}{s[8:10]}{s[6:8]}{s[4:6]}{s[2:4]}{s[:2]}"


EZSP_URLS = {
    7: "https://master.dl.sourceforge.net/project/mgl03/zigbee/"
    "ncp-uart-sw_mgl03_6_6_2_stock.gbl?viasf=1",
    8: "https://master.dl.sourceforge.net/project/mgl03/zigbee/"
    "ncp-uart-sw_mgl03_6_7_8_z2m.gbl?viasf=1",
}


def _update_zigbee_firmware(host: str, ezsp_version: int):
    shell = TelnetShell(host)

    # stop all utilities without checking if they are running
    shell.stop_lumi_zigbee()
    shell.stop_zigbee_tcp()
    # flash on another port because running ZHA or z2m can breake process
    shell.run_zigbee_tcp(port=8889)
    time.sleep(0.5)

    _LOGGER.debug(f"Try update EZSP to version {ezsp_version}")

    from .elelabs_ezsp_utility import ElelabsUtilities

    config = type(
        "", (), {"port": (host, 8889), "baudrate": 115200, "dlevel": _LOGGER.level}
    )
    utils = ElelabsUtilities(config, _LOGGER)

    # check current ezsp version
    resp = utils.probe()
    _LOGGER.debug(f"EZSP before flash: {resp}")
    if resp[0] == 0 and resp[1] == ezsp_version:
        return True

    url = EZSP_URLS[ezsp_version]
    r = requests.get(url)

    resp = utils.flash(r.content)
    _LOGGER.debug(f"EZSP after flash: {resp}")
    return resp[0] == 0 and resp[1] == ezsp_version


async def update_zigbee_firmware(host: str, ezsp_version: int):
    return await utils.run_blocking(
        functools.partial(_update_zigbee_firmware, host, ezsp_version)
    )
