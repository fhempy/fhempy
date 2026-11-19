# VPN server (WireGuard)

Your own VPN into the home network: from anywhere, your phone or laptop is connected to home as if it were in your
WiFi. You reach FHEM, the router, the NAS, cameras... No network know-how needed:

- **Everything is created automatically**: keys, a VPN network which doesn't collide with your home network, the
  configuration for each device.
- **New device = QR code**: `set vpn add_client Phone` shows a QR code, scan it with the WireGuard app, done.
  Computers get a file to download.
- **Port forwarding by itself**: fhempy asks the router via UPnP to forward the VPN port. If the router doesn't allow
  it, the device page tells you exactly what to set up.
- **Internet address**: the public IP address is found automatically, or the name of a [ddnssde](../ddnssde/)
  device. fhempy warns if your connection can't be reached from the internet (carrier grade NAT / DS-Lite) or if the
  DynDNS name points somewhere else.
- **Monitoring**: which device is connected, since when, from where, how much traffic.

## Set up

```
define vpn fhempy wireguard
```

Or use the *VPN server (WireGuard)* tile in *Install modules* of the fhempy device.

### One-time setup (root)

A VPN server needs root rights (network interface, IP forwarding, iptables rules for forwarding, NAT and MSS
clamping). fhempy runs as user `fhem`, which normally can't do this. The device page asks once for a user of this
computer which may use sudo (e.g. `pi`, the user you log in with):

```
set vpn setup user=pi password=secret
```

fhempy logs in to this computer via SSH with it and does the rest. The password is only used for this login, it's
neither stored nor logged. SSH must be enabled (Raspberry Pi: it usually is, `sudo raspi-config` > Interface
Options > SSH). If fhempy itself may already use sudo without password, nothing is asked.

Without SSH, log in yourself and run the command shown on the device page once:

```
sudo python3 /opt/fhem/.fhempy/.../fhempy/lib/wireguard/helper.py install fhem
```

It installs `wireguard-tools` (and `iptables` if missing) with apt, copies a small helper to
`/usr/local/sbin/fhempy-wireguard` and allows `fhem` to run only this helper with sudo
(`/etc/sudoers.d/fhempy-wireguard`). The helper writes the WireGuard configuration itself from checked values
(keys, port, addresses), fhempy gets no general root rights. fhempy continues by itself after the command.

The VPN runs as system service `wg-quick@wgfhempy` (interface `wgfhempy`): it keeps running when FHEM or fhempy
restart and starts again after a reboot.

To remove everything again: `sudo /usr/local/sbin/fhempy-wireguard uninstall`.

### Router

The router must forward **UDP port 51820** (see reading `port`) to this computer:

- With UPnP fhempy does it by itself. FRITZ!Box: *Internet > Permit Access > Port Sharing*, edit this device and
  enable *Permit independent port sharing for this device*.
- Otherwise set it up by hand, the device page shows the values. Then `attr vpn port_forwarding manual`.

Most home connections get a new public IP address from time to time. Then devices set up before can't connect
anymore. Use a free DynDNS name (e.g. the [ddnssde](../ddnssde/) module or MyFRITZ!) and set it with
`attr vpn endpoint myhome.ddnss.de` **before** you add the devices.

If the reading `problem` says your connection has no public IPv4 address (carrier grade NAT / DS-Lite, common with
cable and fibre providers), a VPN server at home can't be reached over IPv4. Ask your provider for a public IPv4
address, or use the [remote_access](../remote_access/README.md) module which needs no port forwarding.

## Add a device

```
set vpn add_client Phone
```

1. Install the **WireGuard** app (Android, iPhone, Windows, macOS, Linux)
2. Tap **+** and **Scan from QR code**
3. Switch the tunnel on

The QR codes of all devices are on the device page (click *QR code and configuration*). Keep them private, they are
the key to your home network. A lost phone: `set vpn remove_client Phone`.

## Connect another site (site to site)

A Raspberry Pi (or another Linux computer with Debian / Raspberry Pi OS) at another place, e.g. a holiday home or
your parents' house, connects both home networks. fhempy sets it up by itself, you only need its address and a user
with sudo rights:

```
set vpn add_site Holiday host=192.168.2.10 user=pi password=secret
```

fhempy logs in via SSH, finds the home network of that site, installs `wireguard-tools` and `iptables`, writes
`/etc/wireguard/wgfhempy.conf` and starts it as system service (also after a reboot). Progress is in the reading
`Holiday_setup`. The password isn't stored. `host` must be reachable from here, e.g. while the Pi is still in your
home network or through the VPN of a phone. Another home network than the detected one: add `network=...`.

Every site needs its own network: if both use `192.168.178.0/24`, change one of them in its router.

### Internet through home for single devices (e.g. a TV)

Only the traffic to the home network goes through the VPN, the internet of the other site stays direct. For single
devices of the site the internet can go through your home instead, e.g. so that a TV in the holiday home streams with
your home connection:

```
set vpn add_site Holiday host=192.168.2.10 user=pi password=secret via_home=192.168.2.50
```

`via_home`: addresses of the devices, comma separated. Running `add_site` again for an existing site changes its
settings, the keys stay. The device page then shows what to set on the TV (network settings, manual / static):
its fixed address, gateway / router = the Pi of the site, DNS = your router at home. The Pi of the site routes only
these devices through the VPN (policy routing, `Table = off`), its own traffic and all other devices stay direct. If
the VPN is down, the TV uses the internet of the site directly. Streaming uses the upload of your home connection
(HD needs about 5-8 Mbit/s).

By hand instead: `set vpn add_client Holiday network=192.168.2.0/24`, the device page shows the configuration file
for the Pi of the other site:

1. `sudo apt install wireguard-tools iptables`
2. Save the file as `/etc/wireguard/wgfhempy.conf` (or `get vpn client_config Holiday`)
3. `sudo systemctl enable --now wg-quick@wgfhempy`

FHEM and fhempy on this computer then reach all devices of the other site directly (e.g. a shelly in the holiday
home), and the devices of the other site reach your home network. Phones and laptops get the networks of all sites
in their QR code. Both Pis use NAT, the routers need no extra routes. Devices at home (not this computer) reach the
other site only with a static route in your router (network of the other site via the IP address of this
computer).

## Commands

| Command | |
|---|---|
| `set <name> add_client <device>` | Add a device, shows its QR code |
| `set <name> add_site <site> host=<ip> user=<user> password=<pw> [via_home=<ips>]` | Set up (or change) the Pi of another site via SSH (site to site), optionally internet through home for some devices |
| `set <name> add_client <site> network=<network>` | Add another site by hand |
| `set <name> setup user=<user> password=<pw>` | One-time setup of this computer via SSH |
| `set <name> remove_client <device>` | Remove a device, it can't connect anymore |
| `set <name> start` | Start the VPN server (again) |
| `set <name> stop` | Stop the VPN server, also after a reboot. Run it before you delete the FHEM device |
| `get <name> client_config <device>` | WireGuard configuration of a device as text |

## Attributes

| Attribute | Default | |
|---|---|---|
| `client_traffic` | `home` | `home`: only traffic to the home network goes through the VPN (fast). `all`: everything, also internet (safe in public WiFi). Devices need a new QR code afterwards |
| `endpoint` | empty | Internet address for the devices, e.g. a DynDNS name. Empty: name of a ddnssde device, else the public IP |
| `port` | empty | UDP port, empty: 51820 or the next free one |
| `port_forwarding` | `upnp` | `upnp`: fhempy asks the router, `manual`: you set it up in the router |
| `interval` | `30` | Seconds between the updates of the connected devices |

## Readings

- `state`: e.g. `2 of 3 connected`, `running, no device connected`, `setup needed: ...`
- `clients`, `clients_connected`, `connected`: number and names of the connected devices
- `<device>_state` (`connected`/`disconnected`), `<device>_last_seen`, `<device>_from` (internet address of the
  device), `<device>_received_mb`, `<device>_sent_mb`
- `public_ip`, `endpoint`, `port`, `port_forwarding`, `home_network`, `vpn_network`
- `problem`: what prevents connections from the internet, `none` if all is fine
- `setup`, `<site>_setup`: progress of the setup via SSH

WireGuard has no events for connects, fhempy reads the state of the interface every `interval` seconds (a local
command, no network traffic). A device counts as connected if it sent a handshake within the last 3 minutes, the
devices get `PersistentKeepalive = 25` for this.

## Files

- `.fhempy/wireguard/<name>.json`: keys and devices (only readable for the fhempy user). Delete and define the
  device again with the same name and all devices keep working.
- `/etc/wireguard/wgfhempy.conf`: written by the helper
