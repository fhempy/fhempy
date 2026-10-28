# System update

Keeps the operating system of the computer fhempy runs on up to date (Raspberry Pi OS, Debian, Ubuntu), carefully so
that an update doesn't break FHEM:

- **Security updates are installed automatically** every night, all other updates are listed and installed with one
  click (`set update`).
- **Critical packages are held back**: kernel, firmware, bootloader, python3, nodejs and fhem are only installed with
  `set update_all`.
- **Checks before**: enough free space, no interrupted installation, no under-voltage of the Raspberry Pi.
- **Backup before**: a [github_backup](../github_backup/) device of this fhempy makes a backup first, the list of all
  installed packages (with versions) is saved.
- **Safe apt**: no package is ever removed, your changed config files are kept, the Debian release is never changed
  (no Bookworm → Trixie). apt runs as its own system service, a restart of FHEM or fhempy during the update doesn't
  interrupt it.
- **Checks after**: FHEM answers, all fhempy connections are back, no system service failed. If something is wrong you
  get a push notification on your phone (module [push](../push/README.md)).
- **Reboot only when needed** (e.g. new kernel) and only at the time you allow (`attr reboot_time`). After the reboot
  the same checks run again.

Nothing can prevent every broken update, but with these rules they're rare and you know about it right away.

## Set up

```
define system_update fhempy system_update
```

Or use the *System update* tile in *Install modules* of the fhempy device.

fhempy runs as user `fhem`, installing updates needs root rights. The device page shows a command, run it **once** on
the computer (e.g. via ssh as user `pi`):

```
sudo python3 /opt/fhem/.fhempy/.../fhempy/lib/system_update/helper.py install fhem
```

It copies a small helper to `/usr/local/sbin/fhempy-system-update` and allows `fhem` to run only this helper with
sudo (`/etc/sudoers.d/fhempy-system-update`):

```
fhem ALL=(root) NOPASSWD: /usr/local/sbin/fhempy-system-update
```

The helper only knows a few fixed commands (update package lists, install updates of given packages, repair,
reboot) and checks the package names. fhempy gets no general apt or root rights. To remove it again:
`sudo /usr/local/sbin/fhempy-system-update uninstall`.

Then `set system_update check` shows the available updates.

## Commands

| Command | |
|---|---|
| `set <name> check` | Check for updates now, nothing is installed |
| `set <name> update` | Install all updates now, except the critical `hold_packages` |
| `set <name> update_all` | Install all updates now, also kernel, firmware, python3... |
| `set <name> repair` | Finish an interrupted installation (`dpkg --configure -a`) |
| `set <name> reboot` | Reboot now |

## Attributes

| Attribute | Default | |
|---|---|---|
| `auto_update` | `security` | Installed automatically at `update_time`: `security`, `all` (except hold_packages) or `off` |
| `update_time` | `03:15` | Daily check and automatic update |
| `reboot_time` | empty | Reboot at this time if an update needs it, e.g. `04:30`. Empty: never automatically, you get a notification |
| `hold_packages` | kernel, firmware, python3, nodejs, fhem | Critical packages (comma separated, `*` allowed), only installed with `update_all` |
| `backup` | `required` | github_backup before each update: `required` (no update if it fails), `optional` or `off` |
| `min_free_mb` | `500` | Minimum free space on `/` |
| `notify` | `problems` | Push notifications: `problems` (failed update, problems afterwards, reboot needed), `all` or `off` |
| `notify_device` | all push devices | push device(s) for the notifications |

## Readings

- `state`: e.g. `up to date`, `5 updates (2 security)`, `updating 3 packages`, `problem after update: ...`
- `updates`, `updates_available`, `updates_security`, `updates_held`: what's available
- `last_update`, `packages_updated`, `packages_kept_back`: the last update. apt keeps an update back if a held package
  depends on it, it is installed together with the held package by `update_all`.
- `health`: result of the check after the last update or reboot, `ok` or the problems
- `reboot_required`, `backup`, `last_error`, `setup_problem`

## Files

- `.fhempy/system_update/packages-*.txt`: installed packages and versions before each update, to see what changed or
  to install an older version by hand (`sudo apt install package=version`)
- `.fhempy/system_update/update-*.txt`: apt output of each update
- `/var/log/fhempy-system-update/`: status and output of the running update
