# MCP server: control FHEM with AI

Talk to your FHEM in plain language with an AI app like Claude, LM Studio or Cursor:

- *"Which lights are on?"*
- *"Switch off the kitchen light."*
- *"Switch off all lights when I leave the house."* The AI creates a DOIF for you, and you
  approve it in FHEMWEB with one click.

The module is an [MCP](https://modelcontextprotocol.io) server. MCP is the standard way AI apps
use tools. The AI only gets what this module gives it: your devices and their readings, never
your passwords, and automations it creates do nothing until you approve them.

## 1. Create the device

```
define AI fhempy mcp_server
```

That's all on the FHEM side. Open the device in FHEMWEB. At the top you see your **secret
address**, e.g. `http://192.168.1.10:8099/mcp/AbCdEf...`. It works like a password: everybody
with this address can control your FHEM devices, so don't share it.

## 2. Connect your AI app

Copy the secret address from the FHEMWEB page and add it to your app. The FHEMWEB page shows
the exact text for your installation, ready to copy.

**Claude Desktop** (Windows, Mac): Claude Desktop needs [Node.js](https://nodejs.org) on your
computer for addresses in your home network, install it first. Then open *Settings &rarr;
Developer &rarr; Edit Config*, put this into the file `claude_desktop_config.json` (with your
address), save it and restart Claude Desktop:

```json
{
  "mcpServers": {
    "fhem": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://192.168.1.10:8099/mcp/AbCdEf...", "--allow-http"]
    }
  }
}
```

Note: *Settings &rarr; Connectors &rarr; Add custom connector* does not work for FHEM, these
connectors are called from the internet and can't reach your home network.

**Claude Code**: run in a terminal

```
claude mcp add --transport http fhem http://192.168.1.10:8099/mcp/AbCdEf...
```

**LM Studio, Cursor, VS Code, n8n, Open WebUI and other apps**: add an MCP server of type
*Streamable HTTP* (sometimes just called *HTTP* or *URL*) with your secret address. For apps
which want the token as header: use the address without the last part
(`http://192.168.1.10:8099/mcp`) and the header `Authorization: Bearer AbCdEf...`.

With a local AI model (e.g. in LM Studio) nothing leaves your home. With Claude or other cloud
AIs, everything the AI reads (device names, readings) is sent to the AI provider.

## 3. Ask the AI

Just ask, e.g. *"Which devices are in the living room?"* or *"Switch off all lights when
nobody is at home."* The AI looks up your devices first, then switches them or creates an
automation.

### Approve automations

Automations (DOIF, notify, at, watchdog) created or changed by the AI are created
**disabled** (`attr disable 1`) in the room **AI**. On the page of your mcp_server device you
see them under *Waiting for your approval*, with what they do and their definition. Check it,
then click **Approve** to activate it or **Reject** to delete it. The same works with

```
set AI approve ai_lights_off
set AI reject ai_lights_off
set AI approve all
```

The AI can only change and delete automations it created itself. Your own automations are
safe. When the AI changes one of its automations or one of its attributes (e.g. `do always`), it
is disabled again and has to be approved again. The approval list shows the attributes too.

Some attributes can only be set by you, as they would skip the approval or run Perl code even
while the automation is disabled: `disable`, `disabledForIntervals`, `disabledAfterTrigger`,
`userattr`, `userReadings`, `stateFormat`, `devStateIcon`, `devStateStyle`, `uiTable`,
`uiState`.

## What the AI can see and do

| Tool | What it does | Attribute |
|------|--------------|-----------|
| list_rooms, list_devices | Rooms and devices with alias, type, room, state | `devices`, `hidden_devices` |
| get_device | Readings, a few attributes (alias, room, group, comment, genericDeviceType, webCmd, eventMap, setList, disable; all attributes for automations) and the `set` commands of a device | |
| list_automations | All DOIF, notify, at and watchdog with their definition | |
| set_device | `set <device> <command>`, e.g. `on`, `pct 50` | `allow_set` |
| create_automation, change_automation, delete_automation | Automations, see above | `allow_automations`, `require_approval` |
| set_automation_attribute | Set or delete attributes of its own automations, e.g. `do always` or `wait 300` for a DOIF | `allow_automations`, `require_approval` |
| fhem_command | Any FHEM command, off by default | `allow_fhem_command` |

### Your passwords stay secret

- Hidden readings (starting with a dot, e.g. `.password`) are never sent.
- Readings and attributes with names like password, token, secret, apikey, pin, auth are
  replaced by `***`. Passwords in addresses (`https://user:password@...`) and texts like
  `password=...` are replaced too.
- Of all attributes only the harmless ones listed above are sent (for automations all
  attributes, names like password are masked there too).
- Device definitions (DEF) are only sent for automations, never for other devices, as some
  modules have passwords in their definition.
- FHEM itself (FHEMWEB, telnet, logs, fhempy) is never visible.
- `setKeyValue` (where most FHEM modules store their passwords) can't be read by the AI.
  Only `allow_fhem_command 1` would allow that, so leave it off.

### Hide devices

```
attr AI hidden_devices Alarm_system,TYPE=Calendar
```

hides these devices completely. Or the other way round, show only some rooms:

```
attr AI devices room=Livingroom,Kitchen
```

(automations are always visible).

## Attributes

| Attribute | Default | Description |
|-----------|---------|-------------|
| port | 8099 | Network port. Change it if another program uses 8099 (state shows an error then). |
| devices | (all) | Only these devices are visible for the AI (devspec, e.g. `room=Kitchen`) |
| hidden_devices | | These devices are never visible for the AI (devspec) |
| allow_set | 1 | 0: the AI can only read, not switch |
| allow_automations | 1 | 0: the AI can't create automations |
| require_approval | 1 | 0: automations of the AI are active immediately, without your approval |
| automation_room | AI | Room of the automations created by the AI |
| allow_fhem_command | 0 | 1: the AI may run any FHEM command, including deleting devices and reading passwords |

## Set commands

| Command | Description |
|---------|-------------|
| approve &lt;automation&gt; | Activate an automation of the AI (`all` for all) |
| reject &lt;automation&gt; | Delete an automation of the AI (`all` for all) |
| new_token | New secret address, the old one stops working. Enter the new one in your apps. |

## Readings

| Reading | Description |
|---------|-------------|
| state | `ready`, `waiting for approval: ...` or an error |
| url | Address of the server without the secret part |
| waiting_for_approval | Automations waiting for your approval |
| last_action | What the AI did last, e.g. `set Lamp_kitchen off` |
| last_client | The AI app which connected last |

Every action of the AI is also written to the fhempy log.

## Troubleshooting

- **The AI app can't connect**: open the secret address in your browser on the same computer.
  It must show *This address works*. If not, check the IP address and whether a firewall
  blocks port 8099.
- **Wrong or missing token**: the address was copied incompletely or `set new_token` was used.
  Copy it again from FHEMWEB.
- **state shows "port 8099 is used by another program"**: `attr AI port 8100` (any free port).
- **The AI doesn't find your lights**: give your devices an `alias` and a room, or set
  `genericDeviceType` to `light`. The AI also finds devices by words like lamp, light, Licht,
  Lampe in the name.
