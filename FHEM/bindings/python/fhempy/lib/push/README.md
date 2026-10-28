# Push notifications on your phone

Get notifications from FHEM on your phone and tablet, like with Pushbullet, but:

- no app to install and no account to create
- works on Android (Chrome, Firefox, Edge, Samsung Internet) and iPhone/iPad (iOS 16.4 or newer)
- on Android with picture and up to two buttons which run FHEM commands, e.g. *Open the door*

## Set up

```
define push fhempy push
```

Or use the *Push notifications* tile in *Install modules* of the fhempy device.

Then open the device `push` in FHEMWEB **on the phone** and tap **Enable notifications**. That's it, the phone gets
a first message right away. Do the same on every phone or tablet which should get notifications.

Browsers offer notifications only on **https** pages. The device page shows you what to do if FHEMWEB isn't opened
with https yet:

- **From anywhere (recommended):** the module [remote_access](../remote_access/README.md) gives FHEM an https address
  via Tailscale (free). Open the device `push` with this address on the phone. Use this address at home too.
- **Only in the home network:** tap *Create local https address*. fhempy creates an own FHEMWEB `WEBpush` with https
  on port 8443 and a certificate for it. Each phone installs this certificate once, the device page shows the steps
  for Android and iPhone. Your FHEMWEB `WEB` stays as it is.

The messages are delivered by the push service of the browser (Google, Apple, Mozilla), encrypted so that only your
phone can read them. The phone needs internet, FHEM needs no open port.

**iPhone/iPad:** notifications only work in the home screen app. Open the device page in Safari, tap *Share* →
*Add to Home Screen*, open *FHEM* on the home screen and tap *Enable notifications* there. Pictures and buttons are not
shown on iOS, the text arrives.

## Send messages

```
set push message Washing machine is done
set push message title=Door Somebody is at the door
set push message to=Pixel Battery of the smoke detector is low
set push message image=https://.../snapshot.jpg action="Open door:set door open" Somebody rings
```

| Option | Meaning |
|--------|---------|
| `title=` | Title of the notification, default *FHEM* |
| `to=` | Only to these phones, comma separated names (see reading `devices`), default all |
| `image=` | Picture below the text, e.g. a camera snapshot (Android) |
| `url=` | Page which opens on a tap on the notification, default FHEM |
| `action=` / `action2=` | Button `"Label:FHEM command"`, a tap runs the command without opening FHEM (Android) |

Options with spaces need quotes: `title="Front door"`. `set push msg ...` works too.

In notify or DOIF:

```
define n_washer notify washer:power:.0 set push message Washing machine is done
```

or with the Perl function, e.g. in a DOIF or `{ }`:

```
{fhempy_push("Washing machine is done")}
{fhempy_push("Somebody rings", "Door")}
{fhempy_push("Only for Dom", "Info", "Pixel")}
```

### Replacing Pushbullet

`set pushbullet message text | title` becomes `set push message text | title`, the part after `|` is the title like
with Pushbullet. Or rename the device to the name of your old Pushbullet device after deleting it, then the existing
notifys stay as they are.

## Buttons

The FHEM command of a button never leaves FHEM: the notification only contains a random code which works once and for
24 hours. If the phone can't reach FHEM directly (e.g. the password of the remote access is needed), FHEM opens and
runs the command there. The reading `last_action` shows the last command run by a button.

## Messages of the last 7 days

The device page shows every message of the last 7 days, newest first and grouped by day: title, text, picture,
which button was used and whether all phones got it. The search field finds old messages, a tap on a notification
opens the list with this message highlighted (unless the message has its own `url`). New messages appear without
reloading the page. *Clear list* or `set push clear_history` deletes the list. The commands of the buttons are not
stored in the list.

## Readings

| Reading | Meaning |
|---------|---------|
| `state` | Number of phones which get notifications |
| `devices` | Names of these phones |
| `message` | Last message sent |
| `delivered` | How many phones accepted the last message, e.g. `2 of 2` |
| `history` | Number of messages in the list of the last 7 days |
| `last_error` | Last problem while sending |
| `local_https` | Local https address, if created |

## Set commands

- `message ...`: see above
- `test`: sends a test message to all phones
- `clear_history`: deletes the list of messages on the device page
- `remove_device <name>`: this phone gets no notifications anymore (or tap *Turn off on this device* on the phone)
- `local_https [hostname]`: creates the local https address (the button on the device page does this for you)

Phones which deleted the browser data or turned notifications off are removed by themselves at the next message.
