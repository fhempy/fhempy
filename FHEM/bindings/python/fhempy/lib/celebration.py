"""Banner in the fhempy log on the first start of a new major version.

The last celebrated major version is stored in .fhempy/celebrated_major.
FHEMPY_CELEBRATE=1 forces the banner, FHEMPY_CELEBRATE=0 turns it off.
"""

import logging
import os
import pathlib

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
        logger.debug(f"Failed to write {MARKER_FILE}", exc_info=True)


class ReleaseBanner:
    def __init__(self, version=__version__):
        self.version = version
        self.log_pending = should_celebrate(version)

    def show_in_log(self):
        """Small banner in the fhempy log, only on this one start."""
        if not self.log_pending:
            return
        self.log_pending = False
        try:
            for line in banner_lines(self.version):
                logger.info(line)
            logger.info(
                f"Welcome to fhempy {self.version}, thank you for using fhempy!"
                f" Release notes: {RELEASES_URL}"
            )
        except Exception:
            # the banner must never break the start
            logger.debug("Release banner in the log failed", exc_info=True)
        # the banner appears once, even if FHEM never connects
        mark_celebrated(self.version)
