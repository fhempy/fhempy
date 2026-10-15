"""Release party on the first start of a new major version.

The fhempy log gets a countdown, a rocket launch and a banner. FHEM gets
the banner in its log, a short countdown in the reading "release_party" of
the BindingsIo device and a dialog in every open FHEMWEB page.

The last celebrated major version is stored in .fhempy/celebrated_major, so
the party runs once per major version. FHEMPY_CELEBRATE=1 forces it,
FHEMPY_CELEBRATE=0 turns it off.
"""

import asyncio
import logging
import os
import pathlib

from . import fhem
from .version import __version__

logger = logging.getLogger(__name__)

MARKER_FILE = pathlib.Path(".fhempy/celebrated_major")
RELEASES_URL = "https://github.com/fhempy/fhempy/releases"

# figlet font "slant"
_FHEMPY_ART = [
    "    ______                               ",
    "   / __/ /_  ___  ____ ___  ____  __  __ ",
    "  / /_/ __ \\/ _ \\/ __ `__ \\/ __ \\/ / / / ",
    " / __/ / / /  __/ / / / / / /_/ / /_/ /  ",
    "/_/ /_/ /_/\\___/_/ /_/ /_/ .___/\\__, /   ",
    "                        /_/    /____/    ",
]

_DIGIT_ART = {
    "0": ["   ____ ", "  / __ \\", " / / / /", "/ /_/ / ", "\\____/  "],
    "1": ["   ___", "  <  /", "  / / ", " / /  ", "/_/   "],
    "2": ["   ___ ", "  |__ \\", "  __/ /", " / __/ ", "/____/ "],
    "3": ["   _____", "  |__  /", "   /_ < ", " ___/ / ", "/____/  "],
    "4": ["   __ __", "  / // /", " / // /_", "/__  __/", "  /_/   "],
    "5": ["    ______", "   / ____/", "  /___ \\  ", " ____/ /  ", "/_____/   "],
    "6": ["   _____", "  / ___/", " / __ \\ ", "/ /_/ / ", "\\____/  "],
    "7": [" _____", "/__  /", "  / / ", " / /  ", "/_/   "],
    "8": ["   ____ ", "  ( __ )", " / __  |", "/ /_/ / ", "\\____/  "],
    "9": ["   ____ ", "  / __ \\", " / /_/ /", " \\__, / ", "/____/  "],
    ".": ["   ", "   ", "   ", " _ ", "(_)"],
}

_ROCKET = [
    "                 /\\",
    "                /  \\",
    "               | fp |",
    "               |    |",
    "              /| /\\ |\\",
    "             /_|/  \\|_\\",
    "                (  )",
    "               ( )( )",
    "              (  )(  )",
    "               '    '",
]

_STAR_LINE = "*  .  *  .  *  .  *  .  *  .  *  .  *  .  *  .  *  .  *"


def banner_lines(version=__version__):
    """ASCII art of 'fhempy <version>', digits and dots only."""
    ver_art = [""] * 5
    for char in version:
        glyph = _DIGIT_ART.get(char)
        if glyph is None:
            # e.g. a dev suffix, the art shows the numeric part only
            break
        ver_art = [line + part for line, part in zip(ver_art, glyph)]
    # the version has no descender line, align it to the baseline of fhempy
    ver_art.append("")
    return [
        (fhempy + "   " + ver).rstrip() for fhempy, ver in zip(_FHEMPY_ART, ver_art)
    ]


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

    async def show_in_log(self, delay=0.15):
        """Countdown, rocket launch and banner in the fhempy log, ~4s."""
        if not self.pending:
            return
        try:
            logger.info(_STAR_LINE)
            for count in ("3", "2", "1"):
                logger.info(f"   fhempy {self.version} launch in {count}...")
                await asyncio.sleep(delay * 4)
            logger.info("   IGNITION!")
            # the log scrolls upwards, so the rocket takes off
            for line in _ROCKET:
                logger.info(line)
                await asyncio.sleep(delay)
            for smoke in ("              ( ) ( ) ( )", "               .  .  .", ""):
                logger.info(smoke)
                await asyncio.sleep(delay)
            for line in banner_lines(self.version):
                logger.info(line)
                await asyncio.sleep(delay / 2)
            logger.info("")
            logger.info(
                f"   Welcome to fhempy {self.version}! Thank you to everyone who"
                " used, tested and improved fhempy on the way here."
            )
            logger.info(f"   Release notes: {RELEASES_URL}")
            logger.info(_STAR_LINE)
        except asyncio.CancelledError:
            raise
        except Exception:
            # a party must never break the start
            logger.debug("Release party in the log failed", exc_info=True)

    async def show_in_fhem(self):
        """Banner, reading countdown and FHEMWEB dialog, once per version."""
        if not self.pending:
            return
        try:
            ret = await fhem.sendCommandName("fhempy", fhem_party_command(self.version))
        except Exception:
            logger.debug("Release party in FHEM failed", exc_info=True)
            return
        if ret:
            # e.g. an old FHEM, log it and celebrate anyway
            logger.debug(f"Release party in FHEM returned: {ret}")
        self.pending = False
        mark_celebrated(self.version)


def _dialog_html(version):
    # becomes a single quoted JavaScript string inside FW_okDialog('...'),
    # so no single quotes, backslashes or newlines here
    return (
        "<style>"
        "@keyframes fpyRocket{0%{transform:translateY(80px) rotate(-45deg);opacity:0}"
        "20%{opacity:1}100%{transform:translateY(-120px) rotate(-45deg);opacity:0}}"
        "@keyframes fpyPop{0%{transform:scale(0.2);opacity:0}"
        "70%{transform:scale(1.15);opacity:1}100%{transform:scale(1);opacity:1}}"
        "@keyframes fpyHue{from{filter:hue-rotate(0deg)}to{filter:hue-rotate(360deg)}}"
        "@keyframes fpyConfetti{0%{transform:translateY(-30px);opacity:0}"
        "30%{opacity:1}100%{transform:translateY(60px) rotate(360deg);opacity:0}}"
        "</style>"
        '<div style="text-align:center;min-width:300px;height:220px;'
        'position:relative;overflow:hidden">'
        '<div style="font-size:56px;height:70px;'
        'animation:fpyRocket 1.8s ease-in 1 both">&#x1F680;</div>'
        '<div style="position:absolute;top:10px;left:0;right:0;font-size:22px;'
        'animation:fpyConfetti 2.5s ease-out 1.6s 2 both">'
        "&#x1F389; &#x2728; &#x1F38A; &#x2728; &#x1F389;</div>"
        '<div style="font-size:42px;font-weight:bold;color:#e65100;'
        "animation:fpyPop 0.8s ease-out 1.5s both,"
        'fpyHue 4s linear 2.3s infinite">'
        f"fhempy {version}</div>"
        '<div style="margin-top:12px;animation:fpyPop 0.6s ease-out 2.1s both">'
        "Thank you for using fhempy!</div>"
        '<div style="margin-top:12px;animation:fpyPop 0.6s ease-out 2.5s both">'
        f'<a href="{RELEASES_URL}" target="_blank">Release notes</a></div>'
        "</div>"
    )


def fhem_party_command(version=__version__):
    """Perl code for BindingsIo, which evaluates it with $hash = BindingsIo."""
    p = fhem.perlString
    frames = [
        "3",
        "2",
        "1",
        "ignition",
        "liftoff",
        f"fhempy {version} - thank you!",
    ]
    log_lines = "".join(
        f"Log3 $io, 3, {p(line)};" for line in ["", *banner_lines(version), ""]
    )
    welcome = f"Welcome to fhempy {version}, thank you for using fhempy!"
    frame_list = ",".join(p(frame) for frame in frames)
    js = "FW_okDialog('" + _dialog_html(version) + "')"
    return (
        "{"
        "my $io = (ref($hash) eq 'HASH' && defined($hash->{NAME})) ? $hash : undef;"
        "my $n = defined($io) ? $io->{NAME} : 'fhempy';"
        f"{log_lines}"
        f"Log3 $io, 3, {p(welcome)};"
        "if (defined($io)) {"
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
        "if (defined(&FW_directNotify)) {"
        "my %seen;"
        "foreach my $fw (values %defs) {"
        "next if (!$fw->{TYPE} || $fw->{TYPE} ne 'FHEMWEB' || !$fw->{SNAME});"
        "next if ($seen{$fw->{SNAME}}++);"
        f"FW_directNotify('#FHEMWEB:' . $fw->{{SNAME}}, {p(js)}, '');"
        "}"
        "}"
        "undef;"
        "}"
    )
