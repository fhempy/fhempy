import asyncio
import base64
import binascii
import ipaddress
import json
import logging
import time

import pytest
import pytest_asyncio
from tests.utils import mock_fhem

from fhempy.lib import fhem_pythonbinding
from fhempy.lib.pkg_installer import check_and_install_dependencies
from fhempy.lib.wireguard import helper, keys, network, remote, wireguard

logger = logging.getLogger(__name__)

NAME = "vpn"
NET = {
    "local_ip": "192.168.1.20",
    "home_network": "192.168.1.0/24",
    "gateway": "192.168.1.1",
    "vpn_network": "10.99.7.0/24",
}


def readings():
    return mock_fhem.readings.get(NAME, {})


async def wait_for(condition, timeout=10):
    for _ in range(int(timeout * 50)):
        if condition():
            return
        await asyncio.sleep(0.02)
    raise AssertionError(f"condition not reached, readings: {readings()}")


def test_x25519_rfc7748():
    scalar = binascii.unhexlify(
        "a546e36bf0527c9d3b16154b82465edd62144c0ac1fc5a18506a2244ba449ac4"
    )
    point = binascii.unhexlify(
        "e6db6867583030db3594c1a424b15f7c726624ec26b3353b10a903a6d0ab1c4c"
    )
    assert keys.x25519(scalar, point).hex() == (
        "c3da55379de9c6908e94ea4df28d084f32eccf03491c71f754b4075577a28552"
    )
    alice = base64.b64encode(
        binascii.unhexlify(
            "77076d0a7318a57d3c16c17251b26645df4c2f87ebc0992ab177fba51db92c2a"
        )
    ).decode()
    assert base64.b64decode(keys.public_key(alice)).hex() == (
        "8520f0098930a754748b7ddcb43ef75a0dbf3a0d26381af4eba4a98eaa9b4e6a"
    )
    private = keys.private_key()
    assert helper.check_key(private) == private
    assert helper.check_key(keys.public_key(private))
    assert len(base64.b64decode(keys.preshared_key())) == 32


def valid_config():
    return {
        "private_key": keys.private_key(),
        "port": 51820,
        "address": "10.99.7.1/24",
        "peers": [
            {
                "public_key": keys.public_key(keys.private_key()),
                "preshared_key": keys.preshared_key(),
                "ip": "10.99.7.2",
            }
        ],
    }


def test_helper_check_config_and_render():
    config = helper.check_config(valid_config())
    assert config["network"] == "10.99.7.0/24"
    text = helper.render(config, "eth0")
    assert "ListenPort = 51820" in text
    assert "AllowedIPs = 10.99.7.2/32" in text
    assert "-s 10.99.7.0/24 -o eth0 -j MASQUERADE" in text
    assert helper.interface_section(text).count("PostDown") == 4
    assert "[Peer]" not in helper.interface_section(text)


@pytest.mark.parametrize(
    "change",
    [
        {"port": "51820"},
        {"port": 0},
        {"port": True},
        {"address": "8.8.8.1/24"},
        {"address": "10.99.7.0/24"},
        {"address": "10.0.0.1/8"},
        {"private_key": "abc\nPostUp = rm -rf /"},
        {"private_key": base64.b64encode(b"x" * 31).decode()},
    ],
)
def test_helper_rejects(change):
    data = valid_config()
    data.update(change)
    with pytest.raises(helper.Invalid):
        helper.check_config(data)


@pytest.mark.parametrize(
    "peer",
    [
        {"ip": "10.99.8.2"},
        {"ip": "10.99.7.1"},
        {"ip": "10.99.7.255"},
        {"ip": "10.99.7.2/32\nPostUp = id"},
        {"public_key": "x"},
        {"preshared_key": None},
    ],
)
def test_helper_rejects_peer(peer):
    data = valid_config()
    data["peers"][0].update(peer)
    with pytest.raises(helper.Invalid):
        helper.check_config(data)


def test_helper_rejects_duplicates():
    data = valid_config()
    data["peers"].append(dict(data["peers"][0], ip="10.99.7.3"))
    with pytest.raises(helper.Invalid):
        helper.check_config(data)
    data["peers"][1] = dict(
        data["peers"][0], public_key=keys.public_key(keys.private_key())
    )
    with pytest.raises(helper.Invalid):
        helper.check_config(data)


def test_parse_dump():
    now = int(time.time())
    dump = (
        "PRIV\tPUB\t51820\toff\n"
        f"KEY1\tPSK\t203.0.113.5:40000\t10.99.7.2/32\t{now}\t1500000\t250000\t25\n"
        "KEY2\tPSK\t(none)\t10.99.7.3/32\t0\t0\t0\t25\n"
    )
    peers = wireguard.parse_dump(dump)
    assert peers["KEY1"] == {
        "endpoint": "203.0.113.5:40000",
        "handshake": now,
        "rx": 1500000,
        "tx": 250000,
    }
    assert peers["KEY2"]["endpoint"] == ""
    assert wireguard.endpoint_ip("[2001:db8::1]:51820") == ipaddress.ip_address(
        "2001:db8::1"
    )


def test_network_helpers(tmp_path):
    used = [
        ipaddress.IPv4Interface("192.168.1.20/24"),
        ipaddress.IPv4Interface("10.99.7.5/16"),
    ]
    assert str(network.choose_vpn_network(used)) == "10.123.7.0/24"
    assert str(network.home_network("192.168.1.20", used)) == "192.168.1.0/24"
    route = tmp_path / "route"
    route.write_text(
        "Iface\tDestination\tGateway \tFlags\tRefCnt\tUse\tMetric\tMask\n"
        "eth0\t00000000\t0101A8C0\t0003\t0\t0\t0\t00000000\n"
    )
    assert network.default_gateway(str(route)) == "192.168.1.1"
    assert network.public_address_problem("100.70.1.2")
    assert network.public_address_problem("192.168.0.2")
    assert network.public_address_problem("203.0.113.9") is None


class FakeHelper:
    """sudo fhempy-wireguard"""

    def __init__(self):
        self.version = str(helper.HELPER_VERSION)
        self.applied = []
        self.running = False
        self.dump = ""
        self.calls = []

    async def run(self, args, stdin=None, limit=120):
        args = [str(a) for a in args]
        self.calls.append(args)
        if helper.INSTALL_PATH not in args:
            return 127, "program not found"
        cmd = args[args.index(helper.INSTALL_PATH) + 1]
        if cmd == "version":
            return 0, self.version + "\n"
        if cmd == "apply":
            config = helper.check_config(json.loads(stdin))
            self.applied.append(config)
            self.running = True
            return 0, ""
        if cmd == "status":
            if not self.running:
                return 3, "not running"
            pub = keys.public_key(self.applied[-1]["private_key"])
            return 0, f"PRIV\t{pub}\t51820\toff\n" + self.dump
        if cmd == "stop":
            self.running = False
            return 0, ""
        return 1, "unknown"


class FakeRouter:
    def __init__(self, logger):
        self.available = True
        self.external = "203.0.113.9"
        self.forwarded = []
        self.removed = []

    async def find(self, session):
        return self.available

    async def external_ip(self):
        return self.external

    async def forward(self, port, ip, description):
        self.forwarded.append((port, ip))
        return self.available

    async def remove(self, port):
        self.removed.append(port)


async def fake_send(hash, cmd):
    return ""


@pytest_asyncio.fixture
async def module(mocker, tmp_path, monkeypatch):
    # segno for the QR code
    await check_and_install_dependencies("wireguard")
    mock_fhem.mock_module(mocker)
    mock_fhem.readings.pop(NAME, None)
    mock_fhem.attributes.pop(NAME, None)
    monkeypatch.chdir(tmp_path)
    fake = FakeHelper()
    installed = tmp_path / "fhempy-wireguard"
    installed.write_text("")
    mocker.patch.object(helper, "INSTALL_PATH", str(installed))
    mocker.patch.object(wireguard, "run_command", fake.run)
    mocker.patch.object(wireguard, "is_root", lambda: False)
    mocker.patch.object(wireguard, "tool", lambda name: "/usr/bin/" + name)
    mocker.patch.object(wireguard, "free_port", lambda: 51820)
    mocker.patch.object(wireguard, "SETUP_INTERVAL", 0.02)
    mocker.patch.object(network, "detect", lambda: dict(NET))
    mocker.patch.object(network, "Router", FakeRouter)
    mocker.patch.object(wireguard, "resolve", lambda host: {"203.0.113.9"})

    async def public_ip(session):
        return "203.0.113.9"

    mocker.patch.object(network, "public_ip", public_ip)
    mocker.patch("fhempy.lib.fhem.sendCommandHash", fake_send)
    mocker.patch.dict(fhem_pythonbinding.loadedModuleInstances, {}, clear=True)
    mod = wireguard.wireguard(logger)
    mod.fake = fake
    await mod.Define({"NAME": NAME, "FHEMPYTYPE": "wireguard"}, [], {})
    await wait_for(lambda: readings().get("port_forwarding") == "router (UPnP)")
    yield mod
    await mod.Undefine(mod.hash)


@pytest.mark.asyncio
async def test_starts_without_clients(module, tmp_path):
    await wait_for(lambda: readings().get("state", "").startswith("running, add"))
    assert module.fake.applied[0]["address"] == "10.99.7.1/24"
    assert module.fake.applied[0]["port"] == 51820
    assert module.router.forwarded == [(51820, "192.168.1.20")]
    assert readings()["endpoint"] == "203.0.113.9:51820"
    assert readings()["problem"] == "none"
    state_file = tmp_path / ".fhempy" / "wireguard" / "vpn.json"
    assert state_file.stat().st_mode & 0o077 == 0
    page = module.detail_html()
    assert "Add a device" in page and "Set up site" in page
    assert 'wgSend(this,&quot;vpn&quot;,"add_site")' in page
    assert "name='port' type='number'" in page


@pytest.mark.asyncio
async def test_add_and_monitor_client(module):
    page = await module.set_add_client(module.hash, {"name": "Phone"})
    assert page.startswith("<html>") and "data:image/png;base64" in page
    peers = module.fake.applied[-1]["peers"]
    assert [p["ip"] for p in peers] == ["10.99.7.2"]
    conf = await module.get_client_config(module.hash, {"name": "Phone"})
    assert "Address = 10.99.7.2/32" in conf
    assert "Endpoint = 203.0.113.9:51820" in conf
    assert "AllowedIPs = 10.99.7.0/24, 192.168.1.0/24" in conf
    assert "DNS" not in conf
    assert f"PublicKey = {keys.public_key(module.config['private_key'])}" in conf
    assert readings()["Phone_state"] == "disconnected"

    client = module.config["clients"]["Phone"]
    module.fake.dump = (
        f"{client['public_key']}\tPSK\t198.51.100.7:4500\t10.99.7.2/32\t"
        f"{int(time.time())}\t2500000\t900000\t25\n"
    )
    await module.update_status()
    assert readings()["state"] == "1 of 1 connected"
    assert readings()["Phone_state"] == "connected"
    assert str(readings()["Phone_from"]) == "198.51.100.7"
    assert readings()["Phone_received_mb"] == 2.5
    assert readings()["connected"] == "Phone"
    assert "VPN works from outside" in module.detail_html()

    assert "exists already" in await module.set_add_client(
        module.hash, {"name": "Phone"}
    )
    assert "Name:" in await module.set_add_client(module.hash, {"name": "a b"})
    await module.set_add_client(module.hash, {"name": "Laptop"})
    assert module.config["clients"]["Laptop"]["ip"] == "10.99.7.3"

    await module.set_remove_client(module.hash, {"name": "Phone"})
    assert "Phone_state" not in readings()
    assert [p["ip"] for p in module.fake.applied[-1]["peers"]] == ["10.99.7.3"]
    assert readings()["clients"] == 1


@pytest.mark.asyncio
async def test_all_traffic(module):
    module._attr_client_traffic = "all"
    await module.set_add_client(module.hash, {"name": "Phone"})
    conf = module.client_config("Phone")
    assert "AllowedIPs = 0.0.0.0/0, ::/0" in conf
    assert "DNS = 192.168.1.1" in conf


@pytest.mark.asyncio
async def test_no_upnp_and_cgnat(module):
    module.router.available = False
    await module.check_network()
    assert readings()["port_forwarding"] == "needed: UDP port 51820 to 192.168.1.20"
    assert "Port forwarding in the router needed" in module.detail_html()
    module.router.available = True
    module.router.external = "100.64.3.4"
    await module.check_network()
    assert "no public IPv4" in readings()["problem"]


@pytest.mark.asyncio
async def test_ddns_hostname(module, mocker):
    class Ddns:
        hash = {"NAME": "ddns", "FHEMPYTYPE": "ddnssde"}
        hostnames = {"other.ddnss.de": {"ip": "1.2.3.4"}, "home.ddnss.de": {}}
        _attr_hostname = "home_ddnss_de"

    fhem_pythonbinding.loadedModuleInstances["ddns"] = Ddns()
    assert module.endpoint_host() == "home.ddnss.de"
    mocker.patch.object(wireguard, "resolve", lambda host: {"198.51.100.1"})
    await module.update_problem()
    assert "not to your public address" in readings()["problem"]
    module._attr_endpoint = "vpn.example.org"
    assert module.endpoint_host() == "vpn.example.org"


@pytest.mark.asyncio
async def test_public_ip_changed(module):
    await module.set_add_client(module.hash, {"name": "Phone"})
    module.config["clients"]["Phone"]["endpoint"] = "203.0.113.1"
    await module.update_problem()
    assert "public address changed" in readings()["problem"]


@pytest.mark.asyncio
async def test_stop_and_start(module):
    await module.set_stop(module.hash, {})
    assert not module.fake.running
    assert module.router.removed == [51820]
    assert module.config["stopped"]
    await module.update_status()
    assert readings()["state"] == "stopped"
    await module.set_start(module.hash, {})
    assert module.fake.running
    await wait_for(lambda: readings().get("state", "").startswith("running"))


@pytest.mark.asyncio
async def test_keeps_keys_after_redefine(module):
    await module.set_add_client(module.hash, {"name": "Phone"})
    key = module.config["private_key"]
    await module.Undefine(module.hash)
    mod = wireguard.wireguard(logger)
    await mod.Define({"NAME": NAME, "FHEMPYTYPE": "wireguard"}, [], {})
    await wait_for(lambda: mod.config.get("clients"))
    assert mod.config["private_key"] == key
    assert "Phone" in mod.config["clients"]
    await mod.Undefine(mod.hash)


@pytest.mark.asyncio
async def test_setup_needed(mocker, tmp_path, monkeypatch):
    await check_and_install_dependencies("wireguard")
    mock_fhem.mock_module(mocker)
    mock_fhem.readings.pop(NAME, None)
    monkeypatch.chdir(tmp_path)
    fake = FakeHelper()
    missing = tmp_path / "fhempy-wireguard"
    mocker.patch.object(helper, "INSTALL_PATH", str(missing))
    mocker.patch.object(wireguard, "run_command", fake.run)
    mocker.patch.object(wireguard, "is_root", lambda: False)
    mocker.patch.object(wireguard, "tool", lambda name: "/usr/bin/" + name)
    mocker.patch.object(wireguard, "free_port", lambda: 51820)
    mocker.patch.object(wireguard, "SETUP_INTERVAL", 0.02)
    mocker.patch.object(network, "detect", lambda: dict(NET))
    mocker.patch.object(network, "Router", FakeRouter)

    async def public_ip(session):
        return "203.0.113.9"

    mocker.patch.object(network, "public_ip", public_ip)
    mocker.patch("fhempy.lib.fhem.sendCommandHash", fake_send)
    mod = wireguard.wireguard(logger)
    await mod.Define({"NAME": NAME, "FHEMPYTYPE": "wireguard"}, [], {})
    await wait_for(lambda: readings().get("setup_problem") == "helper not installed")
    assert readings()["state"].startswith("setup needed")
    assert "helper.py install" in mod.detail_html()
    page = await mod.set_add_client(mod.hash, {"name": "Phone"})
    assert "data:image/png" in page
    # the user ran the command: fhempy continues by itself
    missing.write_text("")
    await wait_for(lambda: fake.running)
    assert [p["ip"] for p in fake.applied[-1]["peers"]] == ["10.99.7.2"]
    await wait_for(lambda: "setup_problem" not in readings())
    await mod.Undefine(mod.hash)


@pytest.mark.asyncio
async def test_site_to_site(module):
    await module.set_add_client(module.hash, {"name": "Phone"})
    page = await module.set_add_client(
        module.hash, {"name": "Holiday", "network": "192.168.2.7/24"}
    )
    assert "wg-quick@wgfhempy" in page and "data:image/png" not in page
    peers = {p["ip"]: p for p in module.fake.applied[-1]["peers"]}
    assert peers["10.99.7.3"]["networks"] == ["192.168.2.0/24"]
    site = module.client_config("Holiday")
    assert "AllowedIPs = 10.99.7.0/24, 192.168.1.0/24\n" in site
    assert "-s 10.99.7.0/24 -o $(ip -4 route" in site
    assert "-s 192.168.1.0/24" in site and "TCPMSS" in site
    phone = module.client_config("Phone")
    assert "AllowedIPs = 10.99.7.0/24, 192.168.1.0/24, 192.168.2.0/24" in phone
    for bad in ("192.168.1.0/24", "10.99.7.0/25", "8.8.8.0/24", "nonsense"):
        error = await module.set_add_client(
            module.hash, {"name": "Other", "network": bad}
        )
        assert "network" in error.lower() or "overlaps" in error
    assert "overlaps" in await module.set_add_client(
        module.hash, {"name": "Other", "network": "192.168.2.128/25"}
    )


ROUTE = "default via 192.168.2.1 dev wlan0 proto dhcp src 192.168.2.10 metric 600\n"
ADDRESSES = (
    "1: lo    inet 127.0.0.1/8 scope host lo\\       valid_lft forever\n"
    "3: wlan0    inet 192.168.2.10/24 brd 192.168.2.255 scope global wlan0\n"
)


def test_parse_site():
    assert remote.parse_site(ROUTE, ADDRESSES) == {
        "network": "192.168.2.0/24",
        "ip": "192.168.2.10",
        "dev": "wlan0",
    }
    assert remote.parse_site("", ADDRESSES) == {}
    # a strange interface name never goes into the configuration
    route = ROUTE.replace("wlan0", "wl;rm")
    assert "dev" not in remote.parse_site(route, ADDRESSES.replace("wlan0", "wl;rm"))


class Result:
    def __init__(self, stdout="", exit_status=0):
        self.stdout = stdout
        self.exit_status = exit_status


class FakeConn:
    """asyncssh connection to the Pi of another site"""

    def __init__(self, sudo_output="started\n", sudo_status=0):
        self.commands = []
        self.uploads = {}
        self.sudo_output = sudo_output
        self.sudo_status = sudo_status

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def run(self, cmd, input=None, check=False, **kwargs):
        self.commands.append((cmd, input))
        if cmd.endswith("mktemp"):
            return Result("/tmp/tmp.abc\n")
        if cmd.startswith("umask 077; cat > "):
            self.uploads[cmd.rsplit(" ", 1)[1]] = input
            return Result()
        if cmd.startswith("ip -4 -o route"):
            return Result(ROUTE)
        if cmd.startswith("ip -4 -o addr"):
            return Result(ADDRESSES)
        if cmd.startswith("sudo -S -p ''"):
            return Result(self.sudo_output, self.sudo_status)
        if cmd.startswith("command -v"):
            # WireGuard isn't installed yet
            return Result("/usr/sbin/iptables\n", 1)
        return Result()

    async def create_process(self, cmd, input=None, **kwargs):
        return FakeProcess(await self.run(cmd, input))


class FakeProcess:
    def __init__(self, result):
        self.result = result
        self.stdout = self.lines()

    async def lines(self):
        for line in str(self.result.stdout or "").splitlines(keepends=True):
            yield line

    async def wait(self):
        return self.result


@pytest.mark.asyncio
async def test_add_site_via_ssh(module, mocker):
    await check_and_install_dependencies("core/peer_installer")
    conn = FakeConn()

    async def connect(host, user, password, port=22, log=None):
        assert (host, user, password) == ("192.168.2.10", "pi", "secret")
        return conn

    mocker.patch.object(remote, "connect", connect)
    mocker.patch.object(module, "install_requirements", mocker.AsyncMock())
    ret = await module.set_add_site(
        module.hash,
        {"name": "Holiday", "host": "192.168.2.10", "user": "pi", "password": "secret"},
    )
    assert "Holiday_setup" in ret
    await wait_for(lambda: readings().get("Holiday_setup", "").startswith("done"))
    assert module.config["clients"]["Holiday"]["networks"] == ["192.168.2.0/24"]
    uploaded = conn.uploads["/tmp/tmp.abc"].decode()
    assert uploaded == module.client_config("Holiday")
    sudo = [c for c in conn.commands if c[0].startswith("sudo")]
    assert all(stdin == "secret\n" for _, stdin in sudo)
    sudo_cmds = " ".join(cmd for cmd, _ in sudo)
    assert "wireguard-tools" in sudo_cmds and "restart wg-quick@wgfhempy" in sudo_cmds
    assert "exec </dev/null" in sudo[0][0]
    assert "secret" not in str(module.config)
    # live log: commands and output, never the password
    log = readings()["setup_log"]
    assert log.startswith("# Setup of site Holiday")
    assert "$ ip -4 -o route show default" in log
    assert "$ sudo env DEBIAN_FRONTEND=noninteractive apt-get -y -q install" in log
    assert "$ sudo systemctl restart wg-quick@wgfhempy" in log
    assert "default via 192.168.2.1" in log
    assert log.endswith("# done, network 192.168.2.0/24")
    assert "secret" not in log and "PrivateKey" not in log
    page = module.detail_html()
    assert "informId='vpn-setup_log'" in page and "$ sudo wg show wgfhempy" in page
    # popup with the log, opens by itself when lines arrive
    assert "class='wgLogBack'" in page and "wgLogOpen" in page
    assert "Show setup log" in page
    peers = module.fake.applied[-1]["peers"]
    assert peers[0]["networks"] == ["192.168.2.0/24"]


@pytest.mark.asyncio
async def test_add_site_fails(module, mocker):
    await check_and_install_dependencies("core/peer_installer")
    conn = FakeConn("Sorry, try again.\nsudo: 1 incorrect password attempt\n", 1)

    async def connect(host, user, password, port=22, log=None):
        return conn

    mocker.patch.object(remote, "connect", connect)
    mocker.patch.object(module, "install_requirements", mocker.AsyncMock())
    await module.set_add_site(
        module.hash,
        {"name": "Holiday", "host": "h", "user": "pi", "password": "wrong"},
    )
    await wait_for(lambda: readings().get("Holiday_setup", "").startswith("failed"))
    assert "no sudo rights" in readings()["Holiday_setup"]
    assert "Holiday" not in module.config["clients"]
    # the site uses the home network of this side
    conn = FakeConn()
    conn_net = "192.168.1.0/24"
    await module.set_add_site(
        module.hash,
        {
            "name": "Holiday",
            "host": "h",
            "user": "pi",
            "password": "x",
            "network": conn_net,
            "mode": "networks",
        },
    )
    await wait_for(lambda: "overlaps" in readings().get("Holiday_setup", ""))
    assert "Usage" in await module.set_add_site(module.hash, {"name": "Other"})


@pytest.mark.asyncio
async def test_setup_via_ssh(mocker, tmp_path, monkeypatch):
    await check_and_install_dependencies("core/peer_installer")
    mock_fhem.mock_module(mocker)
    mock_fhem.readings.pop(NAME, None)
    monkeypatch.chdir(tmp_path)
    fake = FakeHelper()
    missing = tmp_path / "fhempy-wireguard"
    mocker.patch.object(helper, "INSTALL_PATH", str(missing))
    mocker.patch.object(wireguard, "run_command", fake.run)
    mocker.patch.object(wireguard, "is_root", lambda: False)
    mocker.patch.object(wireguard, "tool", lambda name: "/usr/bin/" + name)
    mocker.patch.object(wireguard, "free_port", lambda: 51820)
    mocker.patch.object(wireguard, "SETUP_INTERVAL", 0.02)
    mocker.patch.object(network, "detect", lambda: dict(NET))
    mocker.patch.object(network, "Router", FakeRouter)
    mocker.patch("fhempy.lib.fhem.sendCommandHash", fake_send)
    conn = FakeConn("Installed\n")

    async def connect(host, user, password, port=22, log=None):
        assert host == "127.0.0.1"
        missing.write_text("")
        return conn

    mocker.patch.object(remote, "connect", connect)
    mod = wireguard.wireguard(logger)
    mocker.patch.object(mod, "install_requirements", mocker.AsyncMock())
    await mod.Define({"NAME": NAME, "FHEMPYTYPE": "wireguard"}, [], {})
    await wait_for(lambda: readings().get("setup_problem") == "helper not installed")
    assert "type='password'" in mod.detail_html()
    assert "Usage" in await mod.set_setup(mod.hash, {"user": "pi"})
    await mod.set_setup(mod.hash, {"user": "pi", "password": "secret"})
    await wait_for(lambda: fake.running)
    sudo_cmd, sudo_input = next(c for c in conn.commands if c[0].startswith("sudo"))
    assert sudo_input == "secret\n"
    assert "/tmp/tmp.abc install" in sudo_cmd
    assert conn.uploads["/tmp/tmp.abc"] == open(helper.__file__, "rb").read()
    assert readings()["setup"] == "done"
    log = readings()["setup_log"]
    assert "$ sudo python3 -I /tmp/tmp.abc install" in log and "Installed" in log
    assert "secret" not in log
    await mod.Undefine(mod.hash)


@pytest.mark.asyncio
async def test_site_via_home(module, mocker):
    await check_and_install_dependencies("core/peer_installer")
    conn = FakeConn()

    async def connect(host, user, password, port=22, log=None):
        return conn

    mocker.patch.object(remote, "connect", connect)
    mocker.patch.object(module, "install_requirements", mocker.AsyncMock())
    login = {"host": "192.168.2.10", "user": "pi", "password": "secret"}
    for bad, error in (
        ("192.168.3.5", "not in the network"),
        ("192.168.2.10", "Pi of the site itself"),
        ("tv", "Invalid address"),
    ):
        await module.set_add_site(
            module.hash, dict(login, name="Holiday", via_home=bad)
        )
        await wait_for(lambda: error in readings().get("Holiday_setup", ""))
        assert "Holiday" not in module.config["clients"]
    await module.set_add_site(module.hash, dict(login, name="Holiday"))
    await wait_for(lambda: readings().get("Holiday_setup", "").startswith("done"))
    key = module.config["clients"]["Holiday"]["public_key"]
    assert "Table = off" not in module.client_config("Holiday")
    # again with via_home: same keys, new configuration on the Pi
    readings()["Holiday_setup"] = ""
    await module.set_add_site(
        module.hash, dict(login, name="Holiday", via_home="192.168.2.50")
    )
    await wait_for(lambda: "internet through home" in readings()["Holiday_setup"])
    client = module.config["clients"]["Holiday"]
    assert client["public_key"] == key
    assert client["via_home"] == ["192.168.2.50"]
    conf = module.client_config("Holiday")
    assert conf == list(conn.uploads.values())[-1].decode()
    assert "Table = off" in conf and "AllowedIPs = 0.0.0.0/0" in conf
    assert "PostUp = ip route add 192.168.1.0/24 dev %i" in conf
    assert "PostUp = ip route add default dev %i table 51820" in conf
    assert "ip rule add from 192.168.2.50 table 51820 priority 5181" in conf
    assert "PostDown = ip rule del from 192.168.2.50 table 51820" in conf
    page = module.client_html("Holiday")
    assert "gateway / router <b>192.168.2.10</b>" in page
    assert "DNS <b>192.168.1.1</b>" in page
    # the server routes the whole network of the site
    peers = {p["ip"]: p for p in module.fake.applied[-1]["peers"]}
    assert peers[client["ip"]]["networks"] == ["192.168.2.0/24"]
    # every device with the Pi as gateway, by the network interface
    readings()["Holiday_setup"] = ""
    await module.set_add_site(module.hash, dict(login, name="Holiday", via_home="all"))
    await wait_for(lambda: "Pi as gateway" in readings()["Holiday_setup"])
    assert client["via_home"] == "all" and client["site_dev"] == "wlan0"
    conf = module.client_config("Holiday")
    assert "ip rule add from" not in conf
    assert (
        "PostUp = ip rule add iif wlan0 lookup main suppress_prefixlength 0 "
        "priority 5180" in conf
    )
    assert "PostUp = ip rule add iif wlan0 table 51820 priority 5181" in conf
    assert "PostDown = ip rule del iif wlan0 table 51820 priority 5181" in conf
    assert "every device which" in module.client_html("Holiday")
    assert "checkbox" in module.forms_html()
    await module.set_add_client(module.hash, {"name": "Phone"})
    assert "is a device" in await module.set_add_site(
        module.hash, dict(login, name="Phone")
    )


@pytest.mark.asyncio
async def test_add_site_port_and_home_network(module, mocker):
    await check_and_install_dependencies("core/peer_installer")
    conn = FakeConn()
    ports = []

    async def connect(host, user, password, port=22, log=None):
        ports.append(port)
        return conn

    async def site_info(conn, log=None):
        # the Pi is still in the home network of the VPN server
        return {"network": "192.168.1.0/24", "ip": "192.168.1.77"}

    mocker.patch.object(remote, "connect", connect)
    mocker.patch.object(remote, "site_info", site_info)
    mocker.patch.object(module, "install_requirements", mocker.AsyncMock())
    login = {"host": "192.168.1.77", "user": "pi", "password": "secret"}
    await module.set_add_site(module.hash, dict(login, name="Holiday", port="99999"))
    await wait_for(lambda: "invalid SSH port" in readings().get("Holiday_setup", ""))
    # the network is detected: the same as home gives only a warning, the
    # Pi itself is connected
    await module.set_add_site(module.hash, dict(login, name="Holiday", port="2222"))
    await wait_for(lambda: readings().get("Holiday_setup", "").startswith("done"))
    assert ports == [2222]
    assert "warning: same network as at home" in readings()["Holiday_setup"]
    client = module.config["clients"]["Holiday"]
    assert client["internet_only"] and client["networks"] == []
    conf = module.client_config("Holiday")
    assert f"AllowedIPs = {module.vpn_network}\n" in conf
    assert "MASQUERADE" not in conf and "ip rule" not in conf
    page = module.client_html("Holiday")
    assert "Only the Pi is connected so far" in page
    assert "wgFillSite.apply(null,[&quot;Holiday&quot;, &quot;10.99.7.2&quot;])" in page
    # address of a device at the site entered by hand: its /24 network
    readings()["Holiday_setup"] = ""
    await module.set_add_site(
        module.hash, dict(login, name="Holiday", network="192.168.2.34")
    )
    await wait_for(lambda: readings().get("Holiday_setup", "").startswith("done"))
    assert ports == [2222, 22]
    assert "warning" not in readings()["Holiday_setup"]
    assert module.config["clients"]["Holiday"]["networks"] == ["192.168.2.0/24"]
    assert "Only the Pi is connected" not in module.client_html("Holiday")
    form = module.forms_html()
    assert "Where is the Pi right now?" in form and "name='network'" in form


def test_known_hosts_name():
    assert remote.known_hosts_name("1.2.3.4", 22) == "1.2.3.4"
    assert remote.known_hosts_name("1.2.3.4", 2222) == "[1.2.3.4]:2222"


@pytest.mark.asyncio
async def test_site_internet_only(module, mocker):
    """both sites use the same network: only the internet of the via_home
    devices goes through home, the networks aren't connected"""
    await check_and_install_dependencies("core/peer_installer")
    conn = FakeConn()

    async def connect(host, user, password, port=22, log=None):
        return conn

    async def site_info(conn, log=None):
        # same network as the home network of the VPN server
        return {"network": "192.168.1.0/24", "ip": "192.168.1.77"}

    mocker.patch.object(remote, "connect", connect)
    mocker.patch.object(remote, "site_info", site_info)
    mocker.patch.object(module, "install_requirements", mocker.AsyncMock())
    login = {"host": "192.168.1.77", "user": "pi", "password": "secret"}
    assert "mode:" in await module.set_add_site(
        module.hash, dict(login, name="Holiday", mode="x")
    )
    # automatic: the detected network is the home network, via_home is set
    await module.set_add_site(
        module.hash, dict(login, name="Holiday", via_home="192.168.1.50")
    )
    await wait_for(lambda: readings().get("Holiday_setup", "").startswith("done"))
    assert "internet only" in readings()["Holiday_setup"]
    client = module.config["clients"]["Holiday"]
    assert client["networks"] == [] and client["internet_only"]
    assert client["site_network"] == "192.168.1.0/24"
    conf = module.client_config("Holiday")
    assert conf == list(conn.uploads.values())[-1].decode()
    assert "Table = off" in conf and "AllowedIPs = 0.0.0.0/0" in conf
    assert "PostUp = iptables -t nat -A POSTROUTING -o %i -j MASQUERADE" in conf
    assert "--ctstate RELATED,ESTABLISHED" in conf
    # no route into the own network through the VPN
    assert "ip route add 192.168.1.0/24" not in conf
    assert f"PostUp = ip route add {module.vpn_network} dev %i" in conf
    assert "ip rule add from 192.168.1.50 table 51820 priority 5181" in conf
    # the server routes only the VPN address of the Pi
    peers = {p["ip"]: p for p in module.fake.applied[-1]["peers"]}
    assert peers[client["ip"]]["networks"] == []
    page = module.client_html("Holiday")
    assert "internet only" in page and "DNS <b>1.1.1.1</b>" in page
    # phones don't get the network of the site
    await module.set_add_client(module.hash, {"name": "Phone"})
    assert module.client_config("Phone").count("192.168.1.0/24") == 1
    # explicitly networks: overlap is an error
    readings()["Holiday_setup"] = ""
    await module.set_add_site(
        module.hash,
        dict(
            login,
            name="Holiday",
            via_home="192.168.1.50",
            mode="networks",
            network="192.168.1.0/24",
        ),
    )
    await wait_for(lambda: "overlaps" in readings().get("Holiday_setup", ""))
