
# github_backup
Backup files from the working directory to a private GitHub repository, daily at `backup_time` (default 03:38) or with `set backup_now`. On local installation it's your /opt/fhem directory, on remote peers it's the users home directory. Only files which changed since the last backup are uploaded.

By default (attribute `backup_files`) the following files are backed up, missing files are skipped:
 - fhem.cfg, configDB.db, configDB.conf, log/fhem.save, www/gplot/SVG*.gplot
 - FHEM/FhemUtils/uniqueID: FHEM's uniqueID and the passwords FHEM modules store with it (setKeyValue). Without it, stored passwords can't be read after a restore.
 - zigbee2mqtt: .fhempy/zigbee2mqtt/data/*.yaml, *.json and database.db
 - ESPHome: esphome_config/*.yaml
 - Matter: .fhempy/matter_server/data (keys of your Matter network)
 - Matter bridge: .fhempy/matter_bridge/*/pairing.json and data (pairings with Apple Home, Google Home, Alexa...)

The backup contains secrets (passwords, zigbee network key, Matter keys, ESPHome secrets.yaml), **always use a private repository**.

# Readings
 - state: `ok` if all files were backed up, `failed` otherwise
 - last_backup: time of the last backup
 - last_successful_backup: time of the last backup without errors
 - files_uploaded / files_unchanged / files_failed: number of files of the last backup
 - error, failed_files: only shown when the last backup failed, removed after the next successful backup
 - next_backup: time of the next scheduled backup


# Usage
1. Login to github and create a personal account token here: https://github.com/settings/tokens
2. Set all repo permissions for the token
3. Create a private github repository (e.g. fhempy_backup)
4. Create the backup device in FHEM:
```
define my_backup fhempy github_backup https://github.com/USER/fhempy_backup BACKUP_DIRECTORY
```

USER = Your github username.

BACKUP_DIRECTORY = Name of the directory where the files are backed up.


5. Set token
```
attr my_backup attr github_token gh.............
```
