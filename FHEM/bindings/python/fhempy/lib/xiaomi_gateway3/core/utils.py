import asyncio
import json
import logging
import random
import re
import string
import traceback
import functools
from typing import List, Optional

import requests

from fhempy.lib import utils
from .ezsp import EzspUtils
from .mini_miio import AsyncMiIO
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


async def check_mgl03(
    host: str, token: str, telnet_cmd: Optional[str]
) -> Optional[str]:
    # 1. try connect with telnet (custom firmware)?
    sh = TelnetShell()
    try:
        if await sh.connect(host):
            # 1.1. check token with telnet
            return None if await sh.get_token() == token else "wrong_token"

        if not telnet_cmd:
            return "cant_connect"

        # 2. try connect with miio
        miio = AsyncMiIO(host, token)
        info = await miio.info()

        # if info is None - devise doesn't answer on pings
        if info is None:
            return "cant_connect"

        # if empty info - device works but not answer on commands
        if not info:
            return "wrong_token"

        # 3. check if right model
        if info["model"] != "lumi.gateway.mgl03":
            return "wrong_model"

        raw = json.loads(telnet_cmd)
        # fw 1.4.6_0043+ won't answer on cmd without cloud, don't check answer
        await miio.send(raw["method"], raw.get("params"))

        # waiting for telnet to start
        await asyncio.sleep(1)

        if not await sh.connect(host):
            return "wrong_telnet"

        return None

    finally:
        await sh.close()


async def get_lan_key(host: str, token: str):
    device = AsyncMiIO(host, token)
    resp = await device.send("get_lumi_dpf_aes_key")
    if resp is None:
        return "Can't connect to gateway"
    if len(resp[0]) == 16:
        return resp[0]
    key = "".join(
        random.choice(string.ascii_lowercase + string.digits) for _ in range(16)
    )
    resp = await device.send("set_lumi_dpf_aes_key", [key])
    if resp[0] == "ok":
        return key
    return "Can't update gateway key"


async def get_room_mapping(cloud: MiCloud, host: str, token: str):
    try:
        device = AsyncMiIO(host, token)
        local_rooms = await device.send("get_room_mapping")
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


NCP_URL = "https://master.dl.sourceforge.net/project/mgl03/zigbee/%s?viasf=1"


def flash_zigbee_firmware(
    host: str, ports: list, fw_url: str, fw_ver: str, fw_port=0, force=False
):
    """
    param host: gateway host
    param ports: one or multiple ports with different speeds, first port
        should be 115200
    param fw_url: url to firmware file
    param fw_ver: firmware version, checks before and after flash
    param fw_port: optional, port with firmware speed if it is not 115200
    param second_port: optional, second port if current firmware may have
        different speed
    param force: skip check firmware version before flash
    return: True if NCP firmware version equal to fw_ver
    """

    # we can flash NCP only in boot mode on speed 115200
    # but NCP can work on another speed, so we need to try both of them
    # work with 115200 on port 8115, and with 38400 on port 8038
    _LOGGER.debug(f"Try to update Zigbee NCP to version {fw_ver}")

    if isinstance(ports, int):
        ports = [ports]

    utils = EzspUtils()

    try:
        # try to find right speed from the list
        for port in ports:
            utils.connect(host, port)
            state = utils.state()
            if state:
                break
            utils.close()
        else:
            raise RuntimeError

        if state == "normal":
            if fw_ver in utils.version and not force:
                _LOGGER.info("No need to flash")
                return True
            _LOGGER.info(f"NCP state: {state}, version: {utils.version}")
            utils.launch_boot()
            state = utils.state()

        _LOGGER.info(f"NCP state: {state}, version: {utils.version}")

        # should be in boot
        if state != "boot":
            return False

        r = requests.get(fw_url)
        assert r.status_code == 200, r.status_code

        assert utils.flash_and_close(r.content)

        utils.connect(host, ports[0])
        utils.reboot_and_close()

        utils.connect(host, fw_port or ports[0])
        state = utils.state()
        _LOGGER.info(f"NCP state: {state}, version: {utils.version}")
        return fw_ver in utils.version

    except:
        _LOGGER.error(f"NCP flash error: {traceback.format_exc(1)}")
        return False

    finally:
        utils.close()


async def update_zigbee_firmware(host: str, custom: bool):
    """Update zigbee firmware for both ZHA and zigbee2mqtt modes"""

    sh = TelnetShell()
    try:
        if not await sh.connect(host) or not await sh.run_zigbee_flash():
            return False
    except:
        pass
    finally:
        await sh.close()

    await asyncio.sleep(0.5)

    args = (
        [
            host,
            [8115, 8038],
            NCP_URL % "mgl03_ncp_6_7_10_b38400_sw.gbl",
            "v6.7.10",
            8038,
        ]
        if custom
        else [
            host,
            [8115, 8038],
            NCP_URL % "ncp-uart-sw_mgl03_6_6_2_stock.gbl",
            "v6.6.2",
            8115,
        ]
    )

    for _ in range(3):
        if await utils.run_blocking(functools.partial(flash_zigbee_firmware, *args)):
            return True
    return False
