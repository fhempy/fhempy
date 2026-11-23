"""The control logic without FHEM: mixer, pump, room setpoints, learning.
All functions get plain values so they are easy to test."""

FROST_PIPE = 5.0
# % mixer per K flow deviation
MIXER_KP = 3.0
# % per K and minute
MIXER_KI = 0.6
MIXER_INTEGRAL = 40.0
# K flow temperature per K the coldest room is too cold
ROOM_GAIN = 2.0
ROOM_BOOST_MAX = 8.0
ROOM_BOOST_MIN = -3.0
BIAS_LIMIT = 4.0


def clamp(value, low, high):
    return max(low, min(high, value))


def round_half(value):
    return round(value * 2) / 2


def effective_outdoor(current, forecast, hours):
    """the house reacts slowly: heat now for the next hours, mean of the
    current temperature and the forecast up to `hours` ahead"""
    ahead = [t for h, t in forecast if 1 <= h <= hours]
    if current is None and not ahead:
        return None
    if current is None:
        return sum(ahead) / len(ahead)
    if not ahead:
        return current
    return (current + sum(ahead) / len(ahead)) / 2


def room_deficits(rooms):
    """K each room is too cold, rooms with an open window are left out"""
    return [
        room["target"] - room["actual"]
        for room in rooms
        if room.get("actual") is not None
        and room.get("target") is not None
        and not room.get("window")
    ]


def room_boost(rooms):
    deficits = room_deficits(rooms)
    if not deficits:
        return 0.0
    return clamp(ROOM_GAIN * max(deficits), ROOM_BOOST_MIN, ROOM_BOOST_MAX)


def max_valve(rooms):
    valves = [r["valve"] for r in rooms if r.get("valve") is not None]
    return max(valves) if valves else None


def pump_decision(pump_on, rooms, outdoor, settings, pipe_temps):
    """(wanted state, reason). Keeps the current state in between (hysteresis)."""
    pipes = [t for t in pipe_temps if t is not None]
    if pipes and min(pipes) < FROST_PIPE:
        return True, "frost"
    deficits = room_deficits(rooms)
    coldest = max(deficits) if deficits else None
    valve = max_valve(rooms)
    limit = settings.get("heating_limit", 16.0)
    if outdoor is not None and outdoor >= limit:
        if coldest is None or coldest <= 1.0:
            return False, "summer"
    if coldest is not None and coldest > 0.0:
        return True, "heating"
    if valve is not None and valve > 15:
        return True, "heating"
    if coldest is None:
        return pump_on, "heating" if pump_on else "idle"
    if coldest <= -0.3 and (valve is None or valve < 5):
        return False, "warm"
    return pump_on, "heating" if pump_on else "warm"


class Mixer:
    """PI controller with a feedforward from the mixing ratio:
    flow = x * supply + (1 - x) * return"""

    def __init__(self):
        self.integral = 0.0

    def reset(self):
        self.integral = 0.0

    def position(self, target, flow, supply, ret, seconds):
        if target is None:
            return None
        if supply is not None and supply <= target:
            # the heat source is colder than needed: all it has
            self.integral = 0.0
            return 100.0
        if supply is not None and ret is not None and supply - ret > 2:
            feed = clamp((target - ret) / (supply - ret) * 100, 0, 100)
        else:
            feed = 50.0
        if flow is None:
            return round(feed, 1)
        error = target - flow
        out = feed + MIXER_KP * error + self.integral
        saturated = (out >= 100 and error > 0) or (out <= 0 and error < 0)
        if not saturated:
            step = MIXER_KI * error * min(max(seconds, 0), 300) / 60
            self.integral = clamp(self.integral + step, -MIXER_INTEGRAL, MIXER_INTEGRAL)
        return round(clamp(feed + MIXER_KP * error + self.integral, 0, 100), 1)


def thermostat_bias(old_bias, thermostat_temp, room_temp):
    """how much warmer the thermostat at the radiator measures than the
    room thermometer, smoothed"""
    if thermostat_temp is None or room_temp is None:
        return old_bias or 0.0
    bias = clamp(thermostat_temp - room_temp, -BIAS_LIMIT, BIAS_LIMIT)
    if old_bias is None:
        return bias
    return old_bias + 0.3 * (bias - old_bias)


def thermostat_setpoint(target, bias):
    return clamp(round_half(target + (bias or 0.0)), 5.0, 30.0)


def learn_error(rooms):
    """what the learning step sees: >0 rooms too cold, <0 flow too hot"""
    deficits = room_deficits(rooms)
    if not deficits:
        return None
    error = (max(deficits) + sum(deficits) / len(deficits)) / 2
    valve = max_valve(rooms)
    if error < 0.2 and valve is not None and valve < 35:
        # warm enough with mostly closed valves: a lower flow is enough
        error = min(error, -0.3 * (35 - valve) / 35)
    return error
