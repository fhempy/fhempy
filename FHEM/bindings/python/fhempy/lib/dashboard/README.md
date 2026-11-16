# Tablet dashboard

A modern dashboard for the tablets at home: on the wall in the living room, next to the couch or at the front door. It
has its own look (dark and light, not the FHEM style), works without any configuration in FHEM and is set up in about a
minute on the tablet itself.

- rooms and tiles are built automatically from the FHEM rooms and devices: lights, dimmers, switches, plugs, blinds,
  thermostats, locks, windows and doors, motion and climate sensors, LightScene scenes
- the header shows weather, who is at home (tap it: who arrived when, who is away since when), open windows (by name
  when only a few are open) and empty batteries
- *Home* starts with status chips for light (how many are on), climate (rooms heating or the range of temperatures), blinds and security (open windows and doors, unlocked locks); a tap opens an overview of the rooms this tablet shows, e.g. every lamp that is on by room with *Off* and *All lights off*, every room's temperature with target and humidity, all blinds with *Up*/*Down* and *All up*/*All down*
- a tap on a room card on *Home* opens the room at a glance: a temperature ring (drag it to set the target, or + and −), *Light* with one button for all lamps of the room, *Blinds* with one slider for all blinds and up/down, *Switches*, the scenes and the other devices; the arrow unfolds every lamp, blind or switch with its own slider. *Open the whole room* goes to the room tab
- *Home* shows what is still open or on (with *All off*), energy (solar, usage, storage) and a card per room
- temperatures are shown big, coloured from cold (blue) to warm (orange), with the curve of the day and a rising/falling
  arrow, in the tiles and on the room cards (curves need a timeline device)
- *Home* warns when a room is heated while its window is open, room cards suggest airing at high humidity
- tap the icon of a tile to switch, tap the rest of the tile (or hold it) for the details; swiping sideways over a dimmer or blind tile dims or moves it. The details have: dimming by dragging, target temperature, blinds, history of the day with temperature and humidity curves (if a timeline device exists)
- *History* shows the [timeline](../timeline/README.md) of every day, if a timeline device exists; *Home* shows what happened last in the whole home (today, after a quiet day also yesterday)
- scenes and unlocking need a second tap (*Tap again*), so nothing starts by accident
- when a device doesn't react or FHEM refuses the command, the tablet says so with *Try again*
- timers: the details of a light, switch or fan offer *Switch off in* 15 min, 30 min, 1 h or 2 h (*Switch on for* when it is off), the tile shows the time left. FHEM runs the timer (a temporary `at`), so it works with the tablet off too; switching off by hand ends it
- colour lights: the details have colours and a colour strip, white lights a strip from warm to cold; the tile shows the colour as a small dot. Found by the set commands (`rgb`/`hex` colour pickers, `ct`/`color_temp` in mired or kelvin), e.g. HUEDevice, zigbee2mqtt, Shelly
- push messages of the [push](../push/README.md) module are shown on the tablets as well
- doorbell: the tablets show the camera live (WebRTC), you can talk to the visitor and open the door by sliding
- every tablet keeps its own place, room, layout (order of rooms and tiles by dragging, hidden tiles; the room cards of *Home* have their own order and can be hidden there only) and theme

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

Then it asks which rooms this tablet shows: every room is a big tile with an icon and its number of devices, tap to
select or deselect, *All*/*None* for everything at once. This can be changed later in the settings.

![Setting up a tablet: tap the rooms this tablet shows](screenshot-setup-rooms.png)

That's it. Add the page to the home screen (Android: menu, *Add to home screen*; iPad: share, *Add to Home Screen*) to
get it in full screen without browser bar. Every further tablet is added the same way, the code is valid for 10
minutes and once.

Everything else is changed on the tablet with the gear button. *This tablet*: name, place and room, theme, order and
visibility of rooms, and *Edit tiles* to hide tiles or drag them to another place; these settings belong to this
tablet only. *Whole home* (all tablets): arranging rooms and the devices *All off* leaves on.

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

## Camera page

With cameras the tablets get a tab *Cameras*: all cameras as still pictures, refreshed every two seconds while the page
is shown. A tap opens the live picture full screen, swipe or the arrows go to the next camera. A tablet only for
cameras sets *Start page: Cameras* in its settings; it then starts with the cameras, comes back to them and has no
screensaver. Tablets restricted to some rooms see no camera page.

## All off

*All off* switches off lights, switches and plugs, never thermostats. Plugs of heating, heat pumps, fridges, routers
and the like stay on: they are found by their name (e.g. *Heizstab*, *Kühlschrank*, *Router*). Anything else is one tap
away: *Leave on* next to the device in *Now open and on* on *Home*, the switch in the details of a device or the list
in the settings. This is stored in attribute `keep_on` and applies to all tablets.

*All off* switches a few devices at a time with a short pause, so radio systems (433 MHz, HomeMatic duty cycle, Zigbee)
don't lose commands. A few seconds later the tablet names the devices that are still on, with *Try again*.

## PIN for the settings

On a family tablet somebody may rearrange everything by accident. With `attr <dashboard> settings_pin 1234` the
settings, arranging rooms, editing tiles and *Leave on* ask for the PIN first, then stay open for 10 minutes on that
tablet. FHEM checks the PIN, the tablets never get it. After 5 wrong PINs a tablet waits 5 minutes. A new tablet is
set up without the PIN.

## Calendar and waste collection

FHEM `Calendar` devices are read every 5 minutes. *Home* shows the entries of today and tomorrow. Pickups of waste get a
chip on *Home* and a line in the screensaver on the day before and on the day itself (*Tomorrow: Yellow bin*). Pickups
are found by what an entry says (bin, Tonne, Müll, Altpapier, Gelber Sack, recycling …), and every entry of a calendar
that mostly holds pickups counts as one, also a bare *Gelb* or *Papier*. Devices with the readings `next_text` and
`next_days` (e.g. ABFALL) work the same way.

## Weather

A tap on the weather in the header shows the next 24 hours as a curve with the chance of rain, the next days with
rain and low/high, and sunrise and sunset. The screensaver shows the next hours under the weather. Hours come from
`openmeteo_weather`, days also from the FHEM `Weather` module.

## Good night and leaving home

*Good night* and *Leave home* on *Home* first show what is still open or on: windows and doors, unlocked locks (lock
them with one tap), lights and switches, and at night the open blinds. One tap switches off the lights and switches
(not those left on with *All off*) and, at night, closes the blinds. *Undo* brings back how it was before, for 10
minutes. When windows are open and rain, storm or frost comes in the next hours, the list says so (from the hourly
forecast of `openmeteo_weather`).

## Connection and updates

When the connection to fhempy is lost, the tablet says so at the top and greys out the values, so nobody trusts an old
state. After an fhempy update that changes the dashboard, a tablet still running the old version shows *New version*
with *Reload*. A wall tablet in the screensaver reloads by itself.

## Maintenance and fresh air

A *Maintenance* chip on *Home* appears only when something needs to be done: a device that is not reachable (HomeMatic
`Activity dead`, `availability offline` of zigbee2mqtt/MQTT, or a state like *unreachable*), a temperature or humidity
sensor without new values for two days, or a low battery. A tap lists them by room.

A room card says *Air out* when the humidity is 65 % or more, or the CO₂ (`co2`, `CO2`, `carbonDioxide`) is 1400 ppm or
more, as long as no window of the room is open already.

## Own notices

A notice like *Mail is here* shows at the top of *Home* while a device is on, open or triggered, and chimes once on
every tablet. Switch it on in the details of a device (*Notice on Home*) and type the text. The tick resets the device
when it can be switched off (e.g. a dummy set by a mailbox sensor), otherwise it hides the notice until the device
reports again.

Attribute `notices` holds them, separated by `;`: `device[:reading][=value] text`, e.g.
`Mailbox Mail is here; Basement:water=wet Water in the basement`. Without `=value` a notice shows while the reading is
on, open, 1, true, motion or detected. The devices need no room.

## Blinds

The details of a blind show a window whose blind moves like the real one: drag it down to close, up to open. Next to it
*Up*, *50 %*, *Down* and *Stop* (when the device knows `stop`). Tiles and the room popup show a small window with the
current position, the room popup also has one slider for all blinds of the room.

## Thermostats

The details of a thermostat show a ring: drag the knob to the wanted temperature, or use − and +. The range and steps
come from the set command (e.g. `desired-temp:slider,4.5,0.5,30.5`). The flame and *Heating* appear only when the
thermostat really heats: its valve is open (`actuator`, `ValvePosition`, `valve`, `pi_heating_demand` …) or it says so
(`hvac_action`, `running_state`). Without these readings the tablets guess from the target and the room temperature.

## Washing machine, dryer and dishwasher

Plugs which report their power are watched. A long program (at least 20 minutes, with a peak of 300 W or more for
heating or spinning) followed by 10 minutes without power is a finished program. After the first one the tablets ask
once what is plugged in: *Washing machine*, *Dryer*, *Dishwasher* or *None of these*. The name of the plug is only used
to put the likely answer first. The answer is stored in attribute `appliances` (e.g. `Plug_basement:washer`), which
can also be set by hand.

While a program runs, *Home* shows it with the time it runs and, after the first programs, about how long it takes. When
it is done, all tablets chime and *Home* says *Laundry done* until somebody taps *Done*, the next program starts or 12
hours pass.

## Smoke, water and the alarm system

Smoke and water detectors are found by their readings (`smoke`, `smoke_detect`, `fire`, `water_leak`, `leak`,
`flood`, `moistureDetected` …). When one goes off, every tablet shows a full screen alarm with a siren sound, also
tablets restricted to other rooms. *Sound off* and *Hide* only act on that tablet, a new alarm shows again.

`attr <dashboard> alarm_system <device>` adds the alarm system to *Security*: arm when away, arm at home and disarm,
with the set commands the device has (`armAway`/`armed`/`arm`/`on`, `armHome`/`home`/`night`, `disarm`/`disarmed`/
`off`). A state with *alarm* or *triggered* is an intrusion alarm on all tablets. With `attr <dashboard> alarm_pin 2580`
disarming asks for the PIN, FHEM checks it. Without a PIN, disarming needs a second tap. The alarm system gets no
tile, so *All off* and *Leave home* never disarm it.

## Arranging rooms

Devices in the wrong room or in no room at all? Tap the gear button and *Arrange rooms*. The tablet lists the devices
without a room (with a suggestion from the device name, e.g. `wz_Lamp` goes to *Wohnzimmer*) and every room with its
devices. Drag a device to another room (on tablets: hold it briefly, then drag) or tap it to choose a room or create a new
one, × takes it out of a room (without any room left it is listed under *Without room* again). Devices without a room
also offer the three rooms chosen last on this tablet. Only devices shown on the tablets are listed. *+ Device* in a room searches all devices while typing and moves the chosen ones into the room. Tap the pencil
to rename a room. Devices without any new value for more than a month are marked and listed under *Not used
for long*, where they can be deleted with two taps (gone for good with `save`). This changes the
FHEM attribute `room`, so FHEMWEB and the other modules see the same rooms, and applies to all tablets. Other rooms of
a device stay. Only tablets without restrictions (all rooms, not read only) can arrange rooms.

## Restricted tablets

A tablet in the kids' room or at the guest bed may only see some rooms, only show, or not see the timeline (what
happened at home and the history of devices; temperature curves stay):

```
set tablets tablet_rooms Kids Kids_room,Bathroom
set tablets tablet_readonly Guests 1
set tablets tablet_timeline Guests 0
```

A tablet for some rooms only sees the timeline entries of these rooms.

`set tablets remove_tablet <name>` disconnects a tablet (lost or sold), it has to be paired again then.

## Which devices are shown

All devices with a room and a known type. The type is detected like for [matter_bridge](../matter_bridge/README.md)
(genericDeviceType, set commands and readings). Use attribute `devices` to limit it, e.g. `room=Livingroom,Kitchen`,
and `hidden_devices` to leave devices out, e.g. `Alarm_system,TYPE=CUL_HM`. Rooms like *hidden*, *Unsorted*, *fhempy* or
*Timeline* are left out.

## DOIF inputs

A DOIF with attribute `setList` (and `readingList`) gets a tile with its values, a tap opens the inputs: sliders
(`slider,min,step,max`), choices (`auto,on,off`), time (`time`), text (`textField`) and buttons (`noArg`). Example:

```
attr di_Watering readingList Duration Mode Start
attr di_Watering setList Duration:slider,5,5,60 Mode:auto,on,off Start:time
```

Tablets can only set these inputs, values are checked against the setList (range, options, time format), DOIF commands
like disable or cmd_1 are not offered.

## Fans

Fans (set commands `fan_pct`/`fan_mode`, `genericDeviceType fan` or `matterType fan`) get a fan tile: tap switches
off/on (medium), swiping sideways sets the speed, the details have off/low/medium/high. A ceiling fan with light (e.g.
mantra_ble) stays a light tile, its fan is controlled in the details of the light.

## Music players

fhempy googlecast and dlna_dmr devices, FHEM modules like BOSEST or SONOSPLAYER and every device with
`genericDeviceType speaker` (or set commands play, pause and next) get a music tile: cover, title and play/pause on the
tile, a tap opens previous/next, volume and the presets. The commands are taken from the set list of the device
(e.g. `nextTrack` or `next`), nothing has to be configured.

* BOSEST shows its 6 presets (`channel_01` to `channel_06`, empty ones are left out). BOSEST doesn't report logos of the
  presets, so the dashboard remembers the cover it sees after a preset was chosen. Until a preset played once, its
  initials are shown.
* Covers are loaded through fhempy, so the tablets need no access to the players and https works too.

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
| settings_pin | PIN of 4 to 8 digits for the settings, arranging rooms and editing tiles on the tablets, open for 10 minutes after the PIN. Empty: no PIN |
| keep_on | Devices *All off* leaves on, `none`: all are switched off, empty: found by their name |

## Set commands

| Command | Meaning |
|---------|---------|
| refresh | Read rooms and devices again (happens automatically after define, rename, delete and attribute changes) |
| test_ring | Ring on all tablets |
| remove_tablet | Disconnect a tablet |
| rename_tablet | Rename a tablet |
| tablet_rooms | Rooms a tablet may see, empty: all |
| tablet_readonly | 1: the tablet may only show |
| tablet_timeline | 0: the tablet doesn't show the timeline, 1: it does (default) |

## Security

The dashboard runs on its own port in the home network. Only paired tablets get data: every tablet has its own random
key (stored as hash in FHEM), pairing codes are valid for 10 minutes and once, and too many wrong codes block pairing
for a minute. Tablets can't run FHEM commands, only switch the devices shown on them.
