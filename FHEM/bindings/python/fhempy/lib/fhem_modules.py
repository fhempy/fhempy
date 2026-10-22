"""Install the FHEM modules (.pm files) of the running fhempy version in FHEM.

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


def controls_files(controls):
    """Files listed in the controls file, limited to the FHEM directory."""
    files = []
    for line in controls.splitlines():
        parts = line.split()
        if len(parts) != 4 or parts[0] != "UPD":
            continue
        path = parts[3]
        if (
            not path.startswith("FHEM/")
            or ".." in path.split("/")
            or "\\" in path
            or "'" in path
        ):
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


async def download(version):
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
            files[path] = await get(path)
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
        "  my $old;; "
        "  if (open(my $in, '<:raw', $file)) { local $/;; $old = <$in>;; close($in);; } "
        "  next if (defined($old) && $old eq $content);; "
        "  my @stat = stat($file);; "
        "  File::Path::make_path(File::Basename::dirname($file));; "
        "  my $tmp = $file.'.fhempy_new';; "
        "  my $out;; "
        "  if (!open($out, '>:raw', $tmp)) { push @errors, \"$path: $!\";; next;; } "
        "  my $written = print {$out} $content;; "
        "  if (!close($out) || !$written) { push @errors, \"$path: $!\";; unlink($tmp);; next;; } "
        "  chmod(@stat ? $stat[2] & 07777 : ($path =~ m{/bin/} ? 0755 : 0644), $tmp);; "
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
