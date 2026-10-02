import enum


class PairingState(enum.Enum):
    SUCCESS = 0
    WRONG_PIN = 1
    TIMEOUT = 2
    FAILED = 3
