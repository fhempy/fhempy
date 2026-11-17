"""Alarm sound for googlecast.

The sound is generated here (no download, no extra dependency): a classic
alarm clock pattern of four short beeps followed by a short pause. One
cycle is calculated once and repeated for the requested duration, so even
long alarms are created quickly on small machines.
"""

import array
import functools
import math
import struct
import sys

SAMPLE_RATE = 16000
BEEP_FREQ = 2000
BEEP_LEN = 0.09
BEEP_GAP = 0.06
BEEPS = 4
PAUSE_LEN = 0.45
FADE_LEN = 0.005
VOLUME = 0.7
DEFAULT_DURATION = 30
MAX_DURATION = 600
IMAGE_PATH = "/static/alarm.png"


@functools.lru_cache(maxsize=1)
def _cycle():
    """PCM samples (16 bit signed, mono) of one beep cycle."""
    beep = int(BEEP_LEN * SAMPLE_RATE)
    fade = int(FADE_LEN * SAMPLE_RATE)
    gap = int(BEEP_GAP * SAMPLE_RATE)
    samples = array.array("h")
    for idx in range(BEEPS):
        for i in range(beep):
            # soft start/end avoids clicks on the speaker
            env = min(1.0, i / fade, (beep - i) / fade)
            t = i / SAMPLE_RATE
            # a bit of the 2nd harmonic sounds more like a real alarm clock
            value = 0.8 * math.sin(2 * math.pi * BEEP_FREQ * t) + 0.2 * math.sin(
                4 * math.pi * BEEP_FREQ * t
            )
            samples.append(int(32767 * VOLUME * env * value))
        pause = gap if idx < BEEPS - 1 else int(PAUSE_LEN * SAMPLE_RATE)
        samples.extend([0] * pause)
    if sys.byteorder != "little":
        samples.byteswap()
    return samples.tobytes()


def cycle_length():
    """Length of one beep cycle in seconds."""
    return len(_cycle()) / 2 / SAMPLE_RATE


def make_wav(duration=DEFAULT_DURATION):
    """Return a WAV file (bytes) with the alarm sound of about duration seconds."""
    duration = max(1, min(MAX_DURATION, duration))
    cycle = _cycle()
    pcm = cycle * max(1, round(duration / cycle_length()))
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        36 + len(pcm),
        b"WAVE",
        b"fmt ",
        16,
        1,  # PCM
        1,  # mono
        SAMPLE_RATE,
        SAMPLE_RATE * 2,
        2,
        16,
        b"data",
        len(pcm),
    )
    return header + pcm
