"""Install the FHEM modules (.pm files) of the running fhempy version in FHEM.

The module installer of FHEMWEB (www/fhempy) is installed the same way.

The files are taken from the GitHub tag of the running version and sent through
the websocket, therefore it also works when fhempy runs on another host.
FHEM writes them, updates its controls file for FHEM update and reloads the
loaded modules, so neither FHEM update nor a FHEM restart is needed.
"""
import base64
import logging

from packaging.version import InvalidVersion, Version

from . import fhem
from .version import __version__

logger = logging.getLogger(__name__)

RAW_URL = "https://raw.githubusercontent.com/fhempy/fhempy/v{version}/{path}"
CONTROLS_FILE = "controls_pythonbinding.txt"
VERSION_KEY = "fhempy_modules_version"
# commands with this name are handled by BindingsIo outside of device functions
COMMAND_NAME = "fhempy_modules"

STORED_VERSION_CMD = (
    "my ($err, $ver) = getKeyValue('" + VERSION_KEY + "');; defined($ver) ? $ver : ''"
)


MISSING_FILES_CMD = (
    "my $mp = $main::attr{global}{modpath};; my @missing;; "
    "if (open(my $fh, '<', $mp.'/FHEM/" + CONTROLS_FILE + "')) { "
    "while (my $line = <$fh>) { my @p = split(' ', $line);; "
    "next if (@p != 4 || $p[0] ne 'UPD');; "
    # unreadable files (mode 000 written by fhempy 2.10.2 - 2.11.0) count as missing
    "my @st = CORE::stat($mp.'/'.$p[3]);; "
    "push @missing, $p[3] if (!@st || !($st[2] & 0400));; } "
    "close($fh);; } join(' ', @missing)"
)


def valid_path(path):
    """Only files of the FHEM directory and the module installer of FHEMWEB."""
    return (
        path.startswith(("FHEM/", "www/fhempy/"))
        and ".." not in path.split("/")
        and "\\" not in path
        and "'" not in path
    )


def controls_files(controls):
    """Files listed in the controls file, limited to the FHEM directory and the
    module installer of FHEMWEB (www/fhempy)."""
    files = []
    for line in controls.splitlines():
        parts = line.split()
        if len(parts) != 4 or parts[0] != "UPD":
            continue
        path = parts[3]
        if not valid_path(path):
            logger.warning("Ignore unexpected file in controls file: %s", path)
            continue
        files.append(path)
    return files


def needs_install(installed, running):
    """Only install newer modules, a newer fhempy might run on another host."""
    if not installed:
        return True
    try:
        return Version(running) > Version(installed)
    except InvalidVersion:
        return installed != running


async def download(version, only=None):
    """Files of the controls file at the tag of version, only=paths limits it to
    these files (without the controls file)."""
    # Keep aiohttp's import out of the binding's startup path.
    import aiohttp

    files = {}
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:

        async def get(path):
            async with session.get(RAW_URL.format(version=version, path=path)) as resp:
                resp.raise_for_status()
                return await resp.read()

        controls = await get(CONTROLS_FILE)
        for path in controls_files(controls.decode("utf-8")):
            if only is None or path in only:
                files[path] = await get(path)
        if only is None:
            # write the controls file last, FHEM update relies on it
            files["FHEM/" + CONTROLS_FILE] = controls
    return files


def install_command(version, files):
    """Perl code which writes the changed files and reloads the loaded modules.

    It runs in BindingsIo_processCommand, $hash is the BindingsIo device.
    Only perl code is used, it works with every BindingsIo version.
    """
    entries = ",".join(
        "['" + path + "','" + base64.b64encode(content).decode("ascii") + "']"
        for path, content in files.items()
    )
    return (
        "do { require MIME::Base64;; require File::Basename;; require File::Path;; "
        "my $version = " + fhem.perlString(version) + ";; "
        "my $modpath = $main::attr{global}{modpath};; "
        "my (@changed, @errors);; "
        "foreach my $entry (" + entries + ") { "
        "  my ($path, $data) = @$entry;; "
        "  last if (@errors);; "
        "  my $content = MIME::Base64::decode_base64($data);; "
        "  my $file = $modpath.'/'.$path;; "
        # CORE::stat, other FHEM modules might import File::stat into main
        "  my @stat = CORE::stat($file);; "
        # an unreadable file (mode 000) gets the mode of a new file
        "  my $mode = @stat && ($stat[2] & 0400) ? $stat[2] & 07777 : undef;; "
        "  my $old;; "
        "  if (open(my $in, '<:raw', $file)) { local $/;; $old = <$in>;; close($in);; } "
        "  next if (defined($mode) && defined($old) && $old eq $content);; "
        "  File::Path::make_path(File::Basename::dirname($file));; "
        "  my $tmp = $file.'.fhempy_new';; "
        "  my $out;; "
        "  if (!open($out, '>:raw', $tmp)) { push @errors, \"$path: $!\";; next;; } "
        "  my $written = print {$out} $content;; "
        "  if (!close($out) || !$written) { push @errors, \"$path: $!\";; unlink($tmp);; next;; } "
        # a new file gets the mode of FHEM's own files (e.g. 0744 or 0644)
        "  my @ref = CORE::stat($modpath.'/'.($path =~ m{^www/} "
        "    ? 'www/pgm2/fhemweb.js' : 'FHEM/98_update.pm'));; "
        "  chmod(defined($mode) ? $mode : ($path =~ m{/bin/} ? 0755 "
        "    : (@ref && ($ref[2] & 0400) ? $ref[2] & 0777 : 0644)), $tmp);; "
        "  if (!rename($tmp, $file)) { push @errors, \"$path: $!\";; unlink($tmp);; next;; } "
        "  push @changed, $path;; "
        "} "
        "my @reload = map { m{^FHEM/(\\d\\d_(\\w+))\\.pm$} && $main::modules{$2} "
        "  && $main::modules{$2}{LOADED} ? ($1) : () } @changed;; "
        "if (@errors) { "
        "  Log3 $hash, 1, \"BindingsIo ($hash->{NAME}): failed to install FHEM modules of \""
        "    .\"fhempy $version: \".join(', ', @errors);; "
        "  readingsSingleUpdate($hash, 'update_status', 'failed: FHEM modules of fhempy '"
        "    .$version.' not installed: '.join(', ', @errors), 1);; "
        "} else { "
        "  setKeyValue('" + VERSION_KEY + "', $version);; "
        "  if (@changed) { "
        "    Log3 $hash, 3, \"BindingsIo ($hash->{NAME}): installed FHEM modules of fhempy \""
        "      .\"$version: \".join(', ', @changed);; "
        "    readingsSingleUpdate($hash, 'update_status', 'finished, fhempy '.$version"
        "      .' running, FHEM modules updated', 1);; "
        "  } "
        "} "
        # reload after this command finished, BindingsIo itself might be reloaded
        "InternalTimer(gettimeofday() + 1, sub { foreach my $module (@reload) { "
        "  my $ret = CommandReload(undef, $module);; "
        "  Log3 undef, 1, \"fhempy: reload of $module failed: $ret\" if ($ret);; "
        "} }, undef) if (@reload);; "
        "join(',', @changed).(@errors ? ' errors: '.join(', ', @errors) : '');; "
        "}"
    )


async def install():
    """Install the FHEM modules of the running version if FHEM has older ones."""
    try:
        installed = await fhem.sendCommandName(COMMAND_NAME, STORED_VERSION_CMD)
        if not needs_install(installed, __version__):
            await restore_missing(installed)
            return
        logger.info("Install FHEM modules of fhempy %s", __version__)
        try:
            files = await download(__version__)
        except Exception as error:
            # e.g. development versions without a tag
            logger.warning(
                "Couldn't download FHEM modules of fhempy %s: %s", __version__, error
            )
            return
        ret = await fhem.sendCommandName(
            COMMAND_NAME, install_command(__version__, files)
        )
        logger.info("FHEM modules installed: %s", ret or "no changes")
    except Exception:
        logger.exception("Failed to install FHEM modules")


async def restore_missing(version):
    """Files of the controls file which are missing in FHEM (e.g. deleted by
    mistake) are installed again from the tag of the installed version."""
    result = await fhem.sendCommandName(COMMAND_NAME, MISSING_FILES_CMD)
    missing = [path for path in str(result or "").split() if valid_path(path)]
    if not missing:
        return
    logger.warning("FHEM files of fhempy are missing: %s", ", ".join(missing))
    try:
        files = await download(version, only=set(missing))
    except Exception as error:
        logger.warning("Couldn't download the missing FHEM files: %s", error)
        return
    ret = await fhem.sendCommandName(COMMAND_NAME, install_command(version, files))
    logger.info("Missing FHEM files installed again: %s", ret or "none")
