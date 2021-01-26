from .base import BaseDevice


class HTSensor(BaseDevice):
    def __init__(self, logger, gateway):
        super().__init__(logger, gateway)


class MotionSensor(BaseDevice):
    def __init__(self, logger, gateway):
        super().__init__(logger, gateway)


class ContactSensor(BaseDevice):
    def __init__(self, logger, gateway):
        super().__init__(logger, gateway)
