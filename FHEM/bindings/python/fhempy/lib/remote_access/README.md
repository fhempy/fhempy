# Remote access: FHEM on your phone from anywhere

Open FHEMWEB on your phone while you're away, in the normal browser of the phone:

- a fixed address like `https://fhem.tail1234.ts.net`, with a valid https certificate
- no VPN app on the phone, no port forwarding in the router, no dynamic DNS
- protected by a password, your normal FHEMWEB in the home network stays as it is

The module uses [Tailscale Funnel](https://tailscale.com/kb/1223/funnel). Tailscale is free
for private use, fhempy downloads and runs it by itself.

## Set up

```
define remote fhempy remote_access
```

Or use the *Remote access* tile in *Install modules* of the fhempy device. Then open the device
in FHEMWEB, it shows you the next step:

1. **Log in to Tailscale**: click the button and log in with your Google, Microsoft, Apple or
   GitHub account. A free Tailscale account is created on the first login.
2. **Allow access from the internet**: Tailscale asks once if this device may use Funnel.
   Click *Enable*.
3. **Done**: FHEMWEB shows your address, a QR code, the user name and the password. Scan the QR
   code with your phone, log in and save the page on the home screen.

The page continues by itself after each step, the reading `state` shows where you are.

## Password

The module creates its own FHEMWEB instance (`WEBremote`, only reachable from this computer)
with an `allowed` device (`allowed_WEBremote`), so only the Tailscale address needs the
password. It looks like your FHEMWEB `WEB` (room icons, style, hidden rooms... are copied on
every start). The password is created randomly, the user name is `fhem`. The phone remembers the
login for 30 days (attribute `basicAuthExpiry` of the allowed device).

Before the address is switched on, the module checks that FHEMWEB refuses requests without
password. If it doesn't, the remote access stays off.

- `set remote password <your password>`: your own password, at least 10 characters
- `set remote new_password`: new random password
- `attr remote username <name>`: other user name

## ESPHome, Zigbee2MQTT and other web pages

Web pages of your home network which FHEM shows with a weblink (e.g. the ESPHome dashboard
or the Zigbee2MQTT frontend, `http://192.168.x.x:port`) work from anywhere too. Two of them
get an own https address of the remote access, `https://fhem.<tailnet>.ts.net:8443` and
`:10000` (Tailscale Funnel only allows these ports), ESPHome and Zigbee2MQTT first. They need
the same password, the phone is logged in already. The remote FHEMWEB shows these addresses
in the weblinks, the reading `web_pages` lists them.

## Commands and attributes

- `set remote restart`: start again (checks FHEMWEB and the password, copies the look of
  FHEMWEB, restarts Tailscale)
- `set remote logout`: log out of Tailscale, e.g. to use another account
- `attr remote hostname <name>`: first part of the address, default `fhem`

Readings: `state`, `url` (your address), `web_pages`, `tailscale_version`.

## How it works

fhempy downloads the official Tailscale binaries to `.fhempy/tailscale` (updated on every
start of fhempy) and runs its own `tailscaled` in userspace mode: it needs no root rights and
doesn't change the network of your computer. A Tailscale you installed yourself is not
touched. Tailscale Funnel forwards `https://<hostname>.<tailnet>.ts.net` to the FHEMWEB
instance of the module. The log of Tailscale is in `.fhempy/log/tailscale.log`.

Tailscale keeps running while fhempy restarts, e.g. for an update: FHEMWEB stays reachable from
your phone. Only the ESPHome/Zigbee2MQTT pages on `:8443` and `:10000` are gone until fhempy
is back. Tailscale only restarts when fhempy downloaded a new Tailscale version. On a
fhempy peer running as its own systemd service, systemd stops Tailscale together with fhempy.

If fhempy runs on another computer than FHEM (fhempy peer), the FHEMWEB instance listens in the
home network (with password) and Tailscale forwards to it.

**Not included**: the Apple Home, Google Home or Alexa apps. For them use the
[Matter bridge](../matter_bridge/README.md) with a home hub (HomePod, Apple TV, Nest...).

## Remove

`delete remote` stops the remote access. The FHEMWEB instance `WEBremote` and the allowed
device `allowed_WEBremote` stay, delete them as well if you don't need them any more. The
device of the computer can be removed in the
[Tailscale admin console](https://login.tailscale.com/admin/machines).
