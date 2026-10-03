"""Restored zigbee2mqtt data waiting to be applied.

github_restore must not write zigbee2mqtt data directly to
.fhempy/zigbee2mqtt: after the FHEM restart zigbee2mqtt gets installed
(git clone into an empty directory, default configuration.yaml), which
would fail or overwrite the restored files. Instead the files are stored in
a pending directory and the zigbee2mqtt module applies them after the
installation, right before zigbee2mqtt starts.
"""

import pathlib
import shutil

Z2M_DIR = pathlib.Path(".fhempy/zigbee2mqtt")
Z2M_PENDING_DIR = pathlib.Path(".fhempy/zigbee2mqtt_restore")


def restore_path(path):
    """Path (relative to FHEM's directory) a restored file is written to"""
    path = pathlib.Path(path)
    try:
        return Z2M_PENDING_DIR / path.relative_to(Z2M_DIR)
    except ValueError:
        return path


def apply_z2m_restore(z2m_directory, pending_directory=None):
    """Copy pending restored files to zigbee2mqtt and remove them afterwards.

    Returns the list of applied files (relative paths), empty if no restore
    is pending. If copying fails, the pending files are kept and applied on
    the next start.
    """
    z2m_directory = pathlib.Path(z2m_directory)
    if pending_directory is None:
        pending_directory = z2m_directory.parent / Z2M_PENDING_DIR.name
    pending_directory = pathlib.Path(pending_directory)
    if not pending_directory.is_dir():
        return []

    applied = sorted(
        str(f.relative_to(pending_directory))
        for f in pending_directory.rglob("*")
        if f.is_file()
    )
    shutil.copytree(pending_directory, z2m_directory, dirs_exist_ok=True)
    # mark the restore as consumed, it must not be applied again
    shutil.rmtree(pending_directory)
    return applied
