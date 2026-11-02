# Automations (visual DOIF editor)

Create and change DOIF rules as sentences instead of brackets, and keep the overview when you have many of them.
Existing DOIFs open as they are: everything the editor understands is shown as building blocks, the rest stays as
code block in between, unchanged parts are written back exactly as they were.

- every case of a DOIF is a card: **WHEN** conditions, **THEN** commands, steps with a waiting time in between
- the lightning icon of a condition says whether it starts the rule (trigger) or is only checked (`[?...]`)
- devices, readings, commands and values are chosen from lists, with the current values
- *Advanced* asks the DOIF attributes as plain questions (`do always`, `repeatsame`, `cmdpause`, `waitsame`, ...)
- *What would happen now?* shows which case would be executed now and why (not), with hints to typical pitfalls
- *What would have happened?* replays the last days of the timeline through the rule (needs the timeline module)
- *Code* shows definition and attributes as in FHEM, also for editing, and back to the visual view
- every save is checked with a temporary DOIF first and kept as version, older versions can be restored
- German or English, like `attr global language`

## Set up

```
define automations fhempy doif_editor
```

Or use the *Automations* tile in *Install modules* of the fhempy device. The device is put into the room *Automations*.

## Computed values

A value is calculated like a receipt from top to bottom, e.g. a cooking time, the duration of a light or of the
irrigation:

| Row | Example |
|---|---|
| Start with | 20 min |
| × factor depending on | weather: sunny 100 %, cloudy 80 % |
| + depending on | temperature: below 15 °C −5 min, from 28 °C +10 min |
| only if | any condition |
| Limits, rounding | at least 5, at most 40 |

Sources are readings of devices, the history of a reading (sum, minimum, maximum, average, number of changes or time
since the last change of the last hours, from the timeline), the time of day, weekday, month, inputs and other
values. fhempy computes the values and writes them as readings of this device, e.g. `Duration` and for minutes and
hours also `Duration_s` in seconds. Rules use them like any reading:

```
attr di_irrigation wait 0,[automations:Duration_s]
```

Inputs are readings which you set yourself, e.g. `set automations input Guests 4`.

## Overview of all automations

The tab *Relations* reads all DOIF, notify, at and watchdog devices:

- map: what starts each rule and what it switches, for the whole house, a room, a device or a rule
- health check: devices switched differently by several rules (with *wins* button which adds
  `[?winner:cmd_nr] != N` to the other rule), rules that trigger each other, missing devices, rules not executed for
  90 days, identical rules, values nobody uses
- *Why is it so?*: which rule switched a device last and what triggered it
- day plan: what happens today (DOIF timers, waiting times, at)
- changes: who changed which rule when, also changes made directly in FHEM

Every device page gets a box *Who controls this?* and DOIF pages a button *Edit visually* (attribute
`device_pages`, default 1).

## Commands

| Command | |
|---|---|
| `set automations input <name> <value>` | value of an input |
| `set automations enable/disable <rule>` | switch a rule on or off |
| `set automations run <rule> <case>` | execute a case now |
| `set automations restore <rule> <version>` | restore a version |
| `set automations recompute` | compute all values again |

The other set and get commands are used by the page and take base64 encoded JSON.
