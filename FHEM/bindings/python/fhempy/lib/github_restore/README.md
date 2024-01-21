
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
