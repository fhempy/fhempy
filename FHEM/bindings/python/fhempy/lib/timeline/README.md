# Timeline

See what happened at home, e.g. during your holidays. fhempy records the events of all FHEM devices and shows them
on the device page as a story per day, newest first:

- doors and windows, locks, motion, lights, thermostats and who came home or left
- *on* and *off* become one entry with a duration ("Light sofa on, 3 h 12 min")
- repeats are bundled ("Hallway motion, 14× until 09:15")
- devices switched together, e.g. by a scene, become one entry ("3 lights on")
- days without anything to tell are merged into one line
- while nobody is at home (RESIDENTS absent or gone), opened doors and motion are highlighted, smoke and water alarms
  always
- absences of a day or more are offered as buttons, e.g. *Away Aug 12 – Aug 26*

![Timeline with a few days of holidays: the opened terrace door while nobody was at home is highlighted](screenshot.png)

## Set up

```
define timeline fhempy timeline
```

Or use the *Timeline* tile in *Install modules* of the fhempy device. Then open the device `timeline`: that's it,
the timeline fills up as soon as something happens at home. The device is put into the room *Timeline*: a click on *Timeline* in the menu shows the timeline on the whole page. On wide screens the curves of each day are shown next to the story.

The FHEM modules of fhempy have to be up to date (`update all`, restart FHEM), otherwise the state says
*FHEM update needed*.

## Without technical noise

Every reading lands in one of three layers, nothing has to be configured:

| Layer | What | Shown as |
|---|---|---|
| Story | contact, motion, presence, lock, alarm, the state of lights and switches, desired temperature... | one line per change |
| Curves | numbers like temperature, humidity, power, energy | small curves per day (min/max per hour) |
| Technical | signal strength (RSSI, linkquality), last seen, voltages, versions, uptime, other text readings | hidden, "+ 1,411 technical events and measurements" |

fhempy decides by the name of the reading, its value (few fixed values or numbers), how often it changes and the
device: notify, at, DOIF, FileLog, gateways and dummies without room are never part of the story. A reading which
changes more than 60 times per hour is hidden automatically (not for doors, motion and presence, these are bundled).
The most frequent technical events (RSSI, linkquality, last seen...) are only counted by FHEM and never sent to
fhempy.

If something is wrong:

- **Hide from story** next to an entry takes this reading out of the story, it is still recorded and listed in the hidden events of the day (attribute `hidden`). It asks whether every value of the reading or only this value is hidden, e.g. only `status: booting` of a router
- **Always show** in the list of hidden events of a day shows a reading in the story (attribute `always_show`)
- **Stop recording** in the list of hidden events of a day adds a reading (or only this value) to `skip_events`, FHEM doesn't send its events anymore and nothing is stored. *Delete recorded events* (`set <timeline> prune`) then deletes what was already stored
- **Only on change** next to a curve or a hidden event adds the reading to `event-on-change-reading` of the device, so FHEM only creates events when the value changes
- Click a device name for the history of the device (story and curves of the last 7 or 31 days) with an *Open device* button, Ctrl+click opens the device directly
- Curves which stayed the same all day are folded away, *Show unchanged curves* shows them
- Curves are grouped by device; hovering a curve (or touching it on a phone) shows the value and the hour
- Click a curve to open it big: one day, 7 or 31 days with ‹ › (or the arrow keys) to step back and forth, latest, min, max and average value, min–max band and the exact value under the mouse or finger
- Thermostats: measured and target temperature in one curve (target dashed), "set desired-temp 20" echoes of FHEM and the same target again don't show up in the story, which says "Heizung set to 20 °C"
- Readings that only send changes keep their value until the next event, so their curves don't break up
- The history of a device shows readable names with units, its curves with axes and the values which didn't change
- Doors, lights, motion, outlets and buttons: the history shows the state now ("Closed since 18:14"), how often and how long ("Open 24× in 7 days · 1 h 22 min in total") and one bar per day with the times it was open/on
- A device which reports *on* again while it is still on doesn't start a new entry; *still on for …* shows how long it has been on so far
- `set timeline auto <device>:<reading>` lets fhempy decide again

## Storage

Everything is stored in `.fhempy/timeline/<device name>.db` (SQLite) in the FHEM directory, no database server or
DbLog needed. The story and the daily curves are kept for 2 years (`keep_days`), hidden events for 14 days
(`keep_details_days`). Writes are collected for 60 seconds to protect the SD card; opening the timeline,
a device history or stopping fhempy writes them right away.

## Attributes

| Attribute | Default | |
|---|---|---|
| hidden | | readings which are never shown, e.g. `Hallway:motion Sensor1:*` |
| always_show | | readings which are always shown, e.g. `Washer:program` |
| skip_events | | regexp of events (`device:reading: value`) FHEM doesn't send at all |
| keep_days | 730 | days the story and curves are kept |
| keep_details_days | 14 | days hidden events are kept |

## Readings

- `state`: recording, starting or what is wrong
- `story_events_today`, `hidden_events_today`
- `last_story`: text of the last story event, e.g. for a notify
- `database_size`

`get timeline entries [YYYY-MM-DD] [YYYY-MM-DD]` returns the timeline as JSON, `get timeline details YYYY-MM-DD`
the hidden events of a day.
