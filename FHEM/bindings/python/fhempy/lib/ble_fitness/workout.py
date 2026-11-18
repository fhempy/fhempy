"""Summary of a workout: duration, averages, maxima, energy, heart rate zones
and heart rate variability."""

import math

# share of the maximum heart rate where zone 1..5 start
ZONE_LIMITS = (0.5, 0.6, 0.7, 0.8, 0.9)
# a gap without values longer than this doesn't count as workout time
MAX_GAP = 10
# RMSSD over the RR intervals of this many seconds
HRV_WINDOW = 60
# RR intervals outside are artefacts (strap moved, missed beat)
RR_MIN = 300
RR_MAX = 2000


def heart_rate_zone(heart_rate, max_heart_rate):
    """0 (below 50 % of the maximum) to 5 (above 90 %)."""
    if not heart_rate or not max_heart_rate:
        return 0
    share = heart_rate / max_heart_rate
    return sum(1 for limit in ZONE_LIMITS if share >= limit)


def calories_per_minute(heart_rate, weight, age, sex):
    """Energy expenditure from the heart rate (Keytel et al. 2005), kcal/min."""
    if sex == "female":
        kj = -20.4022 + 0.4472 * heart_rate - 0.1263 * weight + 0.074 * age
    else:
        kj = -55.0969 + 0.6309 * heart_rate + 0.1988 * weight + 0.2017 * age
    return max(0.0, kj / 4.184)


def rmssd(rr_intervals):
    """Root mean square of successive differences of the RR intervals (ms)."""
    rr = [value for value in rr_intervals if RR_MIN <= value <= RR_MAX]
    if len(rr) < 3:
        return None
    diffs = [(b - a) ** 2 for a, b in zip(rr, rr[1:])]
    return round(math.sqrt(sum(diffs) / len(diffs)), 1)


class _Average:
    """Time weighted average and maximum."""

    def __init__(self):
        self.weighted = 0.0
        self.seconds = 0.0
        self.maximum = None

    def add(self, value, seconds):
        if value is None:
            return
        self.weighted += value * seconds
        self.seconds += seconds
        if self.maximum is None or value > self.maximum:
            self.maximum = value

    @property
    def average(self):
        if not self.seconds:
            return None
        return self.weighted / self.seconds


class Workout:
    def __init__(self, start):
        self.start = start
        self._last = start
        self.active_seconds = 0.0
        self.heart_rate = _Average()
        self.power = _Average()
        self.cadence = _Average()
        self.speed = _Average()
        self.energy_kj = 0.0
        self.heart_rate_kcal = 0.0
        self.zone_seconds = [0.0] * 6
        self.device_calories = None
        self.distance_start = None
        self.distance = None
        self._rr = []

    def add(self, now, values, profile):
        """values: heart_rate, power, cadence, speed, distance, calories, rr.
        profile: max_heart_rate, weight, age, sex (None if unknown)."""
        seconds = now - self._last
        self._last = now
        if not 0 < seconds <= MAX_GAP:
            seconds = 0
        self.active_seconds += seconds

        heart_rate = values.get("heart_rate")
        power = values.get("power")
        self.heart_rate.add(heart_rate, seconds)
        self.power.add(power, seconds)
        self.cadence.add(values.get("cadence"), seconds)
        self.speed.add(values.get("speed"), seconds)
        if power is not None and power > 0:
            self.energy_kj += power * seconds / 1000
        if heart_rate:
            zone = heart_rate_zone(heart_rate, profile.get("max_heart_rate"))
            self.zone_seconds[zone] += seconds
            if profile.get("weight") and profile.get("age"):
                self.heart_rate_kcal += (
                    calories_per_minute(
                        heart_rate,
                        profile["weight"],
                        profile["age"],
                        profile.get("sex"),
                    )
                    * seconds
                    / 60
                )
        if values.get("distance") is not None:
            if self.distance_start is None or values["distance"] < self.distance_start:
                self.distance_start = values["distance"]
            self.distance = values["distance"] - self.distance_start
        if values.get("calories") is not None:
            self.device_calories = values["calories"]
        for value in values.get("rr", []):
            self._rr.append((now, value))
        self._rr = [(t, v) for t, v in self._rr if now - t <= HRV_WINDOW]

    @property
    def hrv(self):
        return rmssd([value for _, value in self._rr])

    @property
    def calories(self):
        """kcal: from the power (a human converts about 24 % of the energy
        into mechanical work, 1 kJ at the pedals is about 1 kcal), from the
        device, otherwise from the heart rate."""
        if self.energy_kj:
            return round(self.energy_kj / (0.24 * 4.184))
        if self.device_calories is not None:
            return self.device_calories
        if self.heart_rate_kcal:
            return round(self.heart_rate_kcal)
        return None

    def summary(self):
        """Readings of the workout, values that weren't measured are left out."""
        result = {"workout_duration": round(self.active_seconds / 60, 1)}

        def put(name, value, digits=0):
            if value is not None:
                result[name] = round(value, digits) if digits else round(value)

        put("workout_heart_rate_avg", self.heart_rate.average)
        put("workout_heart_rate_max", self.heart_rate.maximum)
        put("workout_power_avg", self.power.average)
        put("workout_power_max", self.power.maximum)
        put("workout_cadence_avg", self.cadence.average)
        put("workout_speed_avg", self.speed.average, 1)
        if self.energy_kj:
            put("workout_energy", self.energy_kj)
        put("workout_calories", self.calories)
        if self.distance is not None:
            result["workout_distance"] = round(self.distance / 1000, 2)
        if self.heart_rate.seconds:
            for zone in range(1, 6):
                result[f"workout_zone{zone}"] = round(self.zone_seconds[zone] / 60, 1)
        return result
