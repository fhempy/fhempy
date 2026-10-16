"""Restored zigbee2mqtt and Matter data waiting to be applied.

github_restore must not write zigbee2mqtt data directly to
.fhempy/zigbee2mqtt: after the FHEM restart zigbee2mqtt gets installed
(git clone into an empty directory, default configuration.yaml), which
would fail or overwrite the restored files. Instead the files are stored in
a pending directory and the zigbee2mqtt module applies them after the
installation, right before zigbee2mqtt starts.

The same applies to the Matter server storage: a running Matter server
writes its storage and would overwrite restored files, so the matter module
replaces the storage with the restored one right before the server starts.
The pairings of a Matter bridge are applied the same way, per bridge.
"""

import pathlib
import shutil

Z2M_DIR = pathlib.Path(".fhempy/zigbee2mqtt")
Z2M_PENDING_DIR = pathlib.Path(".fhempy/zigbee2mqtt_restore")
MATTER_DATA_DIR = pathlib.Path(".fhempy/matter_server/data")
MATTER_PENDING_DIR = pathlib.Path(".fhempy/matter_server_restore")
BRIDGE_DIR = pathlib.Path(".fhempy/matter_bridge")
BRIDGE_PENDING_DIR = pathlib.Path(".fhempy/matter_bridge_restore")

# directory -> pending directory restored files of it are staged in
PENDING_DIRS = {
    Z2M_DIR: Z2M_PENDING_DIR,
    MATTER_DATA_DIR: MATTER_PENDING_DIR,
    BRIDGE_DIR: BRIDGE_PENDING_DIR,
}


def restore_path(path):
    """Path (relative to FHEM's directory) a restored file is written to"""
    path = pathlib.Path(path)
    for directory, pending_directory in PENDING_DIRS.items():
        try:
            return pending_directory / path.relative_to(directory)
        except ValueError:
            continue
    return path


def pending_dirs(restored_paths):
    """Pending directories which got restored files (None entries ignored)"""
    return {
        pending_dir
        for path in restored_paths
        if path is not None
        for pending_dir in PENDING_DIRS.values()
        if path.is_relative_to(pending_dir)
    }


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


def apply_matter_restore(storage_directory, pending_directory=None):
    """Replace the Matter server storage with a pending restored one.

    The storage is replaced completely, mixing the keys of two fabrics breaks
    it. The previous storage is kept in data.before_restore. Returns the list
    of applied files (relative paths), empty if no restore is pending.
    """
    storage_directory = pathlib.Path(storage_directory)
    if pending_directory is None:
        pending_directory = storage_directory.parent.parent / MATTER_PENDING_DIR.name
    pending_directory = pathlib.Path(pending_directory)
    if not pending_directory.is_dir():
        return []

    return _replace_directory(storage_directory, pending_directory)


def apply_bridge_restore(bridge_directory, pending_directory=None):
    """Replace the pairings of a Matter bridge with pending restored ones.

    Returns the list of applied files (relative paths), empty if no restore
    is pending for this bridge.
    """
    bridge_directory = pathlib.Path(bridge_directory)
    if pending_directory is None:
        pending_directory = (
            bridge_directory.parent.parent
            / BRIDGE_PENDING_DIR.name
            / bridge_directory.name
        )
    pending_directory = pathlib.Path(pending_directory)
    if not pending_directory.is_dir():
        return []
    applied = _replace_directory(bridge_directory, pending_directory)
    try:
        # removed when the last bridge got its files
        pending_directory.parent.rmdir()
    except OSError:
        pass
    return applied


def _replace_directory(directory, pending_directory):
    """Replace directory completely by pending_directory (mixing the keys of
    two fabrics breaks them). The previous directory is kept with the suffix
    .before_restore."""
    applied = sorted(
        str(f.relative_to(pending_directory))
        for f in pending_directory.rglob("*")
        if f.is_file()
    )
    if directory.exists():
        previous = directory.with_name(directory.name + ".before_restore")
        shutil.rmtree(previous, ignore_errors=True)
        directory.rename(previous)
    shutil.copytree(pending_directory, directory)
    # mark the restore as consumed, it must not be applied again
    shutil.rmtree(pending_directory)
    return applied
