
# Zigbee2MQTT
This module installs and runs Zigbee2MQTT.

## Usage

Check if NodeJS is installed on your system
```
node --version
```
If it is not installed yet, follow the next steps:
```
curl -fsSL https://deb.nodesource.com/setup_current.x | sudo -E bash -
sudo apt install nodejs
```

When NodeJS was successfully installed you can go on in FHEM:

```
define z2m fhempy zigbee2mqtt
```

Wait a few minutes for the installation to finish. There are some readings which show you the status. It can take up to 10 minutes or sometimes even more.

The reading "installation" is going to be set to "successful" when finished.

### Start
```
set z2m start
```

### Stop
```
set z2m stop
```

### Update
```
set z2m update
```
The update stops Zigbee2MQTT, pulls the new version, always reinstalls the
dependencies (`pnpm install --frozen-lockfile`), builds it (`pnpm run build`)
and starts it again. The reading "update" shows the current step, the fhempy
log shows the pnpm output if a step fails.

If `node_modules` doesn't fit the installed version (e.g. after an
interrupted update), the dependencies are installed again on the next start.

## Logging

Zigbee2MQTT writes its own log files to:

FHEM-ROOT-DIRECTORY/.fhempy/zigbee2mqtt/data/log/

The console output of Zigbee2MQTT goes to `FHEM-ROOT-DIRECTORY/.fhempy/log/<NAME>.log` (rotated at 5 MB), not to the fhempy log. If Zigbee2MQTT crashes, the last lines are written to the fhempy log.
