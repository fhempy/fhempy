
# github_backup
Backup files from the working directory. On local installation it's your /opt/fhem directory, on remote peers it's the users home directory. Keep in mind that you need to specify the files which you would like to backup.
By default the following files are backed up:
 - configDB.conf
 - configDB.db
 - fhem.cfg


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
