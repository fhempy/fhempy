"""Release party on the first start of a new major version.

The fhempy log gets a small banner once. FHEM gets a short countdown in the
reading "release_party" of the BindingsIo device.

The last celebrated major version is stored in .fhempy/celebrated_major, so
the party runs once per major version. FHEMPY_CELEBRATE=1 forces it,
FHEMPY_CELEBRATE=0 turns it off.
"""

import logging
import os
import pathlib

from . import fhem
from .version import __version__

logger = logging.getLogger(__name__)

MARKER_FILE = pathlib.Path(".fhempy/celebrated_major")
RELEASES_URL = "https://github.com/fhempy/fhempy/releases"

# figlet font "small"
_FHEMPY_ART = [
    "  __ _                        ",
    " / _| |_  ___ _ __  _ __ _  _ ",
    "|  _| ' \\/ -_) '  \\| '_ \\ || |",
    "|_| |_||_\\___|_|_|_| .__/\\_, |",
    "                   |_|   |__/ ",
]

_DIGIT_ART = {
    "0": ["  __  ", " /  \\ ", "| () |", " \\__/ "],
    "1": [" _ ", "/ |", "| |", "|_|"],
    "2": [" ___ ", "|_  )", " / / ", "/___|"],
    "3": [" ____", "|__ /", " |_ \\", "|___/"],
    "4": [" _ _  ", "| | | ", "|_  _|", "  |_| "],
    "5": [" ___ ", "| __|", "|__ \\", "|___/"],
    "6": ["  __ ", " / / ", "/ _ \\", "\\___/"],
    "7": [" ____ ", "|__  |", "  / / ", " /_/  "],
    "8": [" ___ ", "( _ )", "/ _ \\", "\\___/"],
    "9": [" ___ ", "/ _ \\", "\\_, /", " /_/ "],
    ".": ["   ", "   ", " _ ", "(_)"],
}


def banner_lines(version=__version__):
    """ASCII art of 'fhempy <version>', digits and dots only."""
    ver_art = [""] * 4
    for char in version:
        glyph = _DIGIT_ART.get(char)
        if glyph is None:
            # e.g. a dev suffix, the art shows the numeric part only
            break
        ver_art = [line + part for line, part in zip(ver_art, glyph)]
    # the version has no descender line
    ver_art.append("")
    return [(fhempy + "  " + ver).rstrip() for fhempy, ver in zip(_FHEMPY_ART, ver_art)]


def _major(version):
    try:
        return int(str(version).strip().split(".")[0])
    except ValueError:
        return 0


def should_celebrate(version=__version__):
    force = os.environ.get("FHEMPY_CELEBRATE")
    if force == "0":
        return False
    if force == "1":
        return True
    major = _major(version)
    if major < 1:
        return False
    try:
        celebrated = _major(MARKER_FILE.read_text())
    except OSError:
        celebrated = 0
    return major > celebrated


def mark_celebrated(version=__version__):
    try:
        MARKER_FILE.parent.mkdir(parents=True, exist_ok=True)
        MARKER_FILE.write_text(f"{_major(version)}\n")
    except OSError:
        logger.debug("Failed to store celebrated version", exc_info=True)


class ReleaseParty:
    def __init__(self, version=__version__):
        self.version = version
        self.pending = should_celebrate(version)
        self.task = None

    def show_in_log(self):
        """Small banner in the fhempy log, only on this one start."""
        if not self.pending:
            return
        try:
            for line in banner_lines(self.version):
                logger.info(line)
            logger.info(
                f"Welcome to fhempy {self.version}, thank you for using fhempy!"
                f" Release notes: {RELEASES_URL}"
            )
        except Exception:
            # a party must never break the start
            logger.debug("Release party in the log failed", exc_info=True)
        # the banner appears once, even if FHEM never connects
        mark_celebrated(self.version)

    async def show_in_fhem(self):
        """Countdown in the BindingsIo reading release_party."""
        if not self.pending:
            return
        self.pending = False
        try:
            ret = await fhem.sendCommandName("fhempy", fhem_party_command(self.version))
        except Exception:
            logger.debug("Release party in FHEM failed", exc_info=True)
            return
        if ret:
            logger.debug(f"Release party in FHEM returned: {ret}")


def fhem_party_command(version=__version__):
    """Perl code for BindingsIo, which evaluates it with $hash = BindingsIo."""
    p = fhem.perlString
    frames = ["3", "2", "1", "liftoff", f"fhempy {version} - thank you!"]
    frame_list = ",".join(p(frame) for frame in frames)
    return (
        "{"
        "if (ref($hash) eq 'HASH' && defined($hash->{NAME})) {"
        "my $n = $hash->{NAME};"
        f"my @frames = ({frame_list});"
        "my $start = gettimeofday();"
        "for my $i (0..$#frames) {"
        "my $frame = $frames[$i];"
        "InternalTimer($start + 0.7 * $i, sub {"
        "readingsSingleUpdate($defs{$n}, 'release_party', $frame, 1)"
        " if (defined($defs{$n}));"
        "}, undef);"
        "}"
        # the reading would stay in the statefile forever otherwise
        "InternalTimer($start + 600, sub {"
        "CommandDeleteReading(undef, $n . ' release_party') if (defined($defs{$n}));"
        "}, undef);"
        "}"
        "undef;"
        "}"
    )
