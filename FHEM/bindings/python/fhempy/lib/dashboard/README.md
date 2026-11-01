# Tablet dashboard

A modern dashboard for the tablets at home: on the wall in the living room, next to the couch or at the front door. It
has its own look (dark and light, not the FHEM style), works without any configuration in FHEM and is set up in about a
minute on the tablet itself.

- rooms and tiles are built automatically from the FHEM rooms and devices: lights, dimmers, switches, plugs, blinds,
  thermostats, locks, windows and doors, motion and climate sensors, LightScene scenes
- the header shows weather, who is at home, open windows (by name when only a few are open) and empty batteries
- *Home* shows what is still open or on (with *All off*), energy (solar, usage, storage) and a card per room
- tap switches, long press opens the details: dimming by dragging, target temperature, blinds, history of the day
- *History* shows the [timeline](../timeline/README.md) of every day, if a timeline device exists
- push messages of the [push](../push/README.md) module are shown on the tablets as well
- doorbell: the tablets show the camera live (WebRTC), you can talk to the visitor and open the door by sliding
- every tablet keeps its own place, room, layout (order of rooms and tiles, hidden tiles) and theme

![Dashboard on a wall tablet: open windows by name in the header, what is still on, energy and the rooms](screenshot.png)

![A room: scenes, lights, blind, thermostat with + and −, window and what just happened](screenshot-room.png)

## Set up

```
define tablets fhempy dashboard
```

Or use the *Tablet dashboard* tile in *Install modules* of the fhempy device. Then open the device `tablets` in FHEM: it
shows a QR code. Scan it with the camera of the tablet (or open the address shown below the code and type in the
6-digit code). The tablet asks where it is:

| Place | Behaviour |
|-------|-----------|
| On the wall | Starts with the whole home, screensaver with clock after 5 minutes, wakes up on motion in its room, warnings big at the top |
| At the couch | Starts in its own room, lights, scenes and blinds first, no screensaver |
| At the door | A ring takes over the screen with camera, talking and door opener, *Before you leave* shows what is still open |

![Setting up a tablet: choose wall, couch or door and its room](screenshot-setup.png)

That's it. Add the page to the home screen (Android: menu, *Add to home screen*; iPad: share, *Add to Home Screen*) to
get it in full screen without browser bar. Every further tablet is added the same way, the code is valid for 10
minutes and once.

Everything else is changed on the tablet with the gear button: name, place, room, theme, order and visibility of
rooms, and *Edit tiles* to hide or move tiles. These settings belong to this tablet only.

| Light theme at the couch | On a phone |
|---|---|
| ![Light theme on a couch tablet](screenshot-light.png) | ![The dashboard on a phone](screenshot-phone.png) |

## Doorbell and cameras

Doorbells are found automatically (devices with *doorbell*/*klingel* in the name and ring devices). Set attribute
`doorbell` to choose them yourself, e.g. `Doorbell` or `Bell:action` for a reading. `set tablets test_ring` tries it
out.

For the live picture the tablets need a camera stream:

- **You already use go2rtc** (e.g. of Frigate or Home Assistant): `attr tablets go2rtc http://192.168.1.5:1984`
- **Otherwise** give the RTSP address of the camera: `attr tablets cameras Door=rtsp://user:password@192.168.1.20/stream1`.
  fhempy downloads [go2rtc](https://github.com/AlexxIT/go2rtc) and starts it with this camera.

`attr tablets door_camera Door` chooses the camera when there are several. With
`attr tablets door_opener Door_opener on` the tablet at the door shows *Slide to open* when somebody rings.

The picture also works over plain http. **Talking** needs the microphone, which browsers only allow on https pages:
open the device in FHEM and follow *Talk at the door (microphone)*: install the certificate of the dashboard once on the
tablet, then tap *Switch to https* in the settings of the dashboard (port 8096). Or use the address of
[remote_access](../remote_access/README.md).

![Somebody rings: live picture, talking and slide to open](screenshot-doorbell.png)

## Restricted tablets

A tablet in the kids' room or at the guest bed may only see some rooms or only show:

```
set tablets tablet_rooms Kids Kids_room,Bathroom
set tablets tablet_readonly Guests on
```

`set tablets remove_tablet <name>` disconnects a tablet (lost or sold), it has to be paired again then.

## Which devices are shown

All devices with a room and a known type. The type is detected like for [matter_bridge](../matter_bridge/README.md)
(genericDeviceType, set commands and readings). Use attribute `devices` to limit it, e.g. `room=Livingroom,Kitchen`,
and `hidden_devices` to leave devices out, e.g. `Alarm_system,TYPE=CUL_HM`. Rooms like *hidden*, *Unsorted*, *fhempy* or
*Timeline* are left out.

## Attributes

| Attribute | Meaning |
|-----------|---------|
| port | Port of the dashboard, default 8095 |
| https_port | https port with an own certificate, default 8096, 0 switches it off |
| devices | Only these devices (devspec) |
| hidden_devices | Never these devices (devspec) |
| doorbell | Doorbell devices, optionally with reading (`Bell:action`) |
| cameras | Cameras as `name=rtsp://...`, separated by spaces |
| go2rtc | Address of an existing go2rtc |
| door_camera | Camera shown when somebody rings |
| door_opener | Command of the door opener without `set` |

## Set commands

| Command | Meaning |
|---------|---------|
| refresh | Read rooms and devices again (happens automatically after define, rename, delete and attribute changes) |
| test_ring | Ring on all tablets |
| remove_tablet | Disconnect a tablet |
| rename_tablet | Rename a tablet |
| tablet_rooms | Rooms a tablet may see, empty: all |
| tablet_readonly | on: the tablet may only show |

## Security

The dashboard runs on its own port in the home network. Only paired tablets get data: every tablet has its own random
key (stored as hash in FHEM), pairing codes are valid for 10 minutes and once, and too many wrong codes block pairing
for a minute. Tablets can't run FHEM commands, only switch the devices shown on them.
