"""Heating curve (flow temperature from the outdoor temperature) and what
the module learned about the house on top of it.

The base curve is the usual radiator curve. The learned part is a
correction per outdoor temperature (every 5 K from -15 to +15 °C):
while heating steadily, rooms that stay too cold raise it, rooms that are
warm enough with mostly closed valves lower it. So after a few days the
flow temperature fits the house, separately for mild and for cold days.
"""

POINTS = (-15, -10, -5, 0, 5, 10, 15)
RADIATOR_EXPONENT = 1.3
MAX_OFFSET = 15.0
# K flow temperature per K room deviation and hour
LEARN_RATE = 0.5


def base_flow(outdoor, room=20.0, design_flow=55.0, design_outdoor=-12.0):
    """flow temperature which keeps a room at `room` °C"""
    if outdoor is None:
        return None
    if outdoor >= room:
        return room
    span = max(room - design_outdoor, 1.0)
    load = (room - outdoor) / span
    return room + (design_flow - room) * load ** (1 / RADIATOR_EXPONENT)


def _weights(outdoor):
    """the two neighbouring points of outdoor and their share"""
    if outdoor <= POINTS[0]:
        return [(0, 1.0)]
    if outdoor >= POINTS[-1]:
        return [(len(POINTS) - 1, 1.0)]
    for i in range(len(POINTS) - 1):
        low, high = POINTS[i], POINTS[i + 1]
        if low <= outdoor <= high:
            share = (outdoor - low) / (high - low)
            return [(i, 1 - share), (i + 1, share)]
    return [(0, 1.0)]


class Learned:
    def __init__(self):
        self.offsets = [0.0] * len(POINTS)
        self.hours = [0.0] * len(POINTS)

    def offset(self, outdoor):
        if outdoor is None:
            return 0.0
        return sum(self.offsets[i] * w for i, w in _weights(outdoor))

    def learn(self, outdoor, error, hours):
        """error: K the rooms are too cold (negative: too warm)"""
        if outdoor is None or hours <= 0:
            return
        error = max(min(error, 3.0), -3.0)
        for i, w in _weights(outdoor):
            step = LEARN_RATE * error * hours * w
            self.offsets[i] = max(min(self.offsets[i] + step, MAX_OFFSET), -MAX_OFFSET)
            self.hours[i] += hours * w

    def to_text(self):
        return " ".join(
            f"{p}:{o:+.2f}:{h:.1f}" for p, o, h in zip(POINTS, self.offsets, self.hours)
        )

    def from_text(self, text):
        for part in (text or "").split():
            try:
                point, offset, hours = part.split(":")
                i = POINTS.index(int(point))
                self.offsets[i] = max(min(float(offset), MAX_OFFSET), -MAX_OFFSET)
                self.hours[i] = max(float(hours), 0.0)
            except (ValueError, IndexError):
                continue

    def total_hours(self):
        return sum(self.hours)

    def reset(self):
        self.offsets = [0.0] * len(POINTS)
        self.hours = [0.0] * len(POINTS)


def flow_target(outdoor, room, settings, learned):
    """flow temperature for the outdoor temperature (effective, with the
    forecast) including the learned correction, clamped to the limits"""
    base = base_flow(
        outdoor,
        room,
        settings.get("design_flow", 55.0),
        settings.get("design_outdoor", -12.0),
    )
    if base is None:
        return None
    value = base + learned.offset(outdoor)
    return max(
        min(value, settings.get("max_flow", 60.0)), settings.get("min_flow", 20.0)
    )
