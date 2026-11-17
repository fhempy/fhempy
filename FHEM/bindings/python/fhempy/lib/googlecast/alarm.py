"""Alarm sound for googlecast.

The sound is generated here (no download, no extra dependency): a siren
like an alarm system, the pitch sweeps up and down continuously. One sweep
is calculated once and repeated for the requested duration, so even long
alarms are created quickly on small machines. The sweep ends after a whole
number of oscillations, so the repeated sweeps join without a click.
"""

import array
import functools
import math
import struct
import sys

SAMPLE_RATE = 22050
LOW_FREQ = 700
HIGH_FREQ = 1700
# one sweep up and down; (LOW_FREQ + HIGH_FREQ) / 2 * SWEEP_LEN must be a
# whole number, then every sweep starts and ends at phase 0
SWEEP_LEN = 0.5
# odd harmonics make the tone sharp like a siren horn instead of a pure beep
HARMONICS = ((1, 1.0), (3, 0.3), (5, 0.12))
VOLUME = 0.75
DEFAULT_DURATION = 30
MAX_DURATION = 600
IMAGE_PATH = "/static/alarm.png"


def _phase(t):
    """Phase in oscillations at time t within one sweep (frequency up, then down)."""
    half = SWEEP_LEN / 2
    slope = (HIGH_FREQ - LOW_FREQ) / half
    if t <= half:
        return LOW_FREQ * t + slope * t * t / 2
    s = t - half
    return LOW_FREQ * half + slope * half * half / 2 + HIGH_FREQ * s - slope * s * s / 2


@functools.lru_cache(maxsize=1)
def _cycle():
    """PCM samples (16 bit signed, mono) of one siren sweep."""
    norm = sum(amp for _, amp in HARMONICS)
    samples = array.array("h")
    for i in range(round(SWEEP_LEN * SAMPLE_RATE)):
        phase = 2 * math.pi * _phase(i / SAMPLE_RATE)
        value = sum(amp * math.sin(n * phase) for n, amp in HARMONICS) / norm
        samples.append(int(32767 * VOLUME * value))
    if sys.byteorder != "little":
        samples.byteswap()
    return samples.tobytes()


def cycle_length():
    """Length of one siren sweep in seconds."""
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
