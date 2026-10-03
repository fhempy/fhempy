
# github_restore
Restore files from your github backup.


# Usage
Use the github token from your github_backup attribute or take it from here: https://github.com/settings/tokens

```
define gh_restore fhempy github_restore https://github.com/USER/fhempy_backup BACKUP_DIRECTORY
```

USER = Your github username.

BACKUP_DIRECTORY = Name of the directory where the files are backed up.


Set token
```
attr my_backup attr github_token gh.............
```

Start restore.

Now you can restart FHEM, do not press save before you restart!

## zigbee2mqtt
Restored zigbee2mqtt data (`.fhempy/zigbee2mqtt/...`) is not written to the zigbee2mqtt directory directly, otherwise it would be overwritten by the zigbee2mqtt installation after the FHEM restart. It is stored in `.fhempy/zigbee2mqtt_restore` and the zigbee2mqtt module applies it after the installation, right before zigbee2mqtt starts. Afterwards the directory is removed, the reading `restore` of the zigbee2mqtt device lists the applied files.
