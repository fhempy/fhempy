"""Parsers for the standard Bluetooth fitness profiles.

- Heart Rate Measurement (0x2A37): chest straps, arm bands, watches
- Cycling Power Measurement (0x2A63): power meters, smart trainers
- Cycling Speed and Cadence Measurement (0x2A5B): speed/cadence sensors
- Indoor Bike Data (0x2AD2) of the Fitness Machine Service: smart trainers
- Treadmill Data (0x2ACD) and Rower Data (0x2AD1) of the Fitness Machine Service

All functions take the raw notification and return a dict with the values that
are present, unknown or truncated data raises ValueError.
"""

import struct


def uuid16(short):
    return f"0000{short:04x}-0000-1000-8000-00805f9b34fb"


HEART_RATE_SERVICE = uuid16(0x180D)
CYCLING_POWER_SERVICE = uuid16(0x1818)
CYCLING_SPEED_CADENCE_SERVICE = uuid16(0x1816)
FITNESS_MACHINE_SERVICE = uuid16(0x1826)

HEART_RATE_MEASUREMENT = uuid16(0x2A37)
CYCLING_POWER_MEASUREMENT = uuid16(0x2A63)
CSC_MEASUREMENT = uuid16(0x2A5B)
INDOOR_BIKE_DATA = uuid16(0x2AD2)
TREADMILL_DATA = uuid16(0x2ACD)
ROWER_DATA = uuid16(0x2AD1)
FITNESS_MACHINE_CONTROL_POINT = uuid16(0x2AD9)
BATTERY_LEVEL = uuid16(0x2A19)

FITNESS_MACHINE_DATA = (INDOOR_BIKE_DATA, TREADMILL_DATA, ROWER_DATA)
CYCLING_SENSOR_DATA = (CYCLING_POWER_MEASUREMENT, CSC_MEASUREMENT)


class _Reader:
    def __init__(self, data):
        self.data = bytes(data)
        self.pos = 0

    def take(self, fmt):
        size = struct.calcsize(fmt)
        if self.pos + size > len(self.data):
            raise ValueError("notification too short")
        value = struct.unpack_from(fmt, self.data, self.pos)
        self.pos += size
        return value if len(value) > 1 else value[0]

    def uint24(self):
        low, high = self.take("<HB")
        return low | high << 16


def heart_rate(data):
    """Heart Rate Measurement: heart_rate (bpm), sensor_contact (True/False,
    missing if the sensor can't tell), energy (kJ), rr (list of ms)."""
    reader = _Reader(data)
    flags = reader.take("<B")
    result = {"heart_rate": reader.take("<H" if flags & 0x01 else "<B")}
    if flags & 0x04:
        result["sensor_contact"] = bool(flags & 0x02)
    if flags & 0x08:
        result["energy"] = reader.take("<H")
    if flags & 0x10:
        rr = []
        while reader.pos + 2 <= len(reader.data):
            rr.append(round(reader.take("<H") * 1000 / 1024))
        result["rr"] = rr
    return result


# (flag bit, struct format or "uint24", names (None: skipped), scale)
# names with more than one value for formats with several fields
_CYCLING_POWER_FIELDS = (
    (0x0001, "<B", ("balance",), 0.5),
    (0x0004, "<H", (None,), 1),  # accumulated torque
    (0x0010, "<IH", ("wheel_revolutions", "wheel_time"), 1),
    (0x0020, "<HH", ("crank_revolutions", "crank_time"), 1),
    (0x0040, "<hh", (None, None), 1),  # extreme force magnitudes
    (0x0080, "<hh", (None, None), 1),  # extreme torque magnitudes
    (0x0100, "<3B", (None, None, None), 1),  # extreme angles
    (0x0200, "<H", (None,), 1),  # top dead spot angle
    (0x0400, "<H", (None,), 1),  # bottom dead spot angle
    (0x0800, "<H", ("accumulated_energy",), 1),
)

_CSC_FIELDS = (
    (0x01, "<IH", ("wheel_revolutions", "wheel_time"), 1),
    (0x02, "<HH", ("crank_revolutions", "crank_time"), 1),
)

# Fitness Machine Service: bit 0 ("more data") is inverted, the first field
# is present if it is NOT set. Energy: total kcal, per hour, per minute.
_ENERGY = ("<HHB", ("calories", None, None), 1)

_INDOOR_BIKE_FIELDS = (
    (0x0001, "<H", ("speed",), 0.01),
    (0x0002, "<H", (None,), 1),  # average speed
    (0x0004, "<H", ("cadence",), 0.5),
    (0x0008, "<H", (None,), 1),  # average cadence
    (0x0010, "uint24", ("distance",), 1),
    (0x0020, "<h", ("resistance",), 1),
    (0x0040, "<h", ("power",), 1),
    (0x0080, "<h", (None,), 1),  # average power
    (0x0100, *_ENERGY),
    (0x0200, "<B", ("heart_rate",), 1),
    (0x0400, "<B", (None,), 1),  # metabolic equivalent
    (0x0800, "<H", ("elapsed",), 1),
)

_TREADMILL_FIELDS = (
    (0x0001, "<H", ("speed",), 0.01),
    (0x0002, "<H", (None,), 1),  # average speed
    (0x0004, "uint24", ("distance",), 1),
    (0x0008, "<hh", ("incline", None), 0.1),  # incline, ramp angle
    (0x0010, "<HH", (None, None), 1),  # elevation gain
    (0x0020, "<B", (None,), 1),  # instantaneous pace
    (0x0040, "<B", (None,), 1),  # average pace
    (0x0080, *_ENERGY),
    (0x0100, "<B", ("heart_rate",), 1),
    (0x0200, "<B", (None,), 1),  # metabolic equivalent
    (0x0400, "<H", ("elapsed",), 1),
)

_ROWER_FIELDS = (
    (0x0001, "<BH", ("stroke_rate", "strokes"), 1),
    (0x0002, "<B", (None,), 1),  # average stroke rate
    (0x0004, "uint24", ("distance",), 1),
    (0x0008, "<H", (None,), 1),  # instantaneous pace
    (0x0010, "<H", (None,), 1),  # average pace
    (0x0020, "<h", ("power",), 1),
    (0x0040, "<h", (None,), 1),  # average power
    (0x0080, "<h", ("resistance",), 1),
    (0x0100, *_ENERGY),
    (0x0200, "<B", ("heart_rate",), 1),
    (0x0400, "<B", (None,), 1),  # metabolic equivalent
    (0x0800, "<H", ("elapsed",), 1),
)


def _fields(reader, flags, fields, inverted_first=False):
    result = {}
    for bit, fmt, names, scale in fields:
        present = bool(flags & bit)
        if inverted_first and bit == 0x0001:
            present = not present
        if not present:
            continue
        values = (reader.uint24(),) if fmt == "uint24" else reader.take(fmt)
        if not isinstance(values, tuple):
            values = (values,)
        for name, value in zip(names, values):
            if name is not None:
                result[name] = round(value * scale, 2) if scale != 1 else value
    # 0xFFFF: not available
    if result.get("calories") == 0xFFFF:
        del result["calories"]
    return result


def cycling_power(data):
    """Cycling Power Measurement: power (W), balance (%), crank_revolutions,
    crank_time (1/1024 s), wheel_revolutions, wheel_time (1/2048 s),
    accumulated_energy (kJ)."""
    reader = _Reader(data)
    flags = reader.take("<H")
    power = reader.take("<h")
    return {"power": power, **_fields(reader, flags, _CYCLING_POWER_FIELDS)}


def speed_cadence(data):
    """CSC Measurement: wheel_revolutions, wheel_time, crank_revolutions,
    crank_time (both times in 1/1024 s)."""
    reader = _Reader(data)
    return _fields(reader, reader.take("<B"), _CSC_FIELDS)


def indoor_bike(data):
    """Indoor Bike Data: speed (km/h), cadence (rpm), distance (m),
    resistance, power (W), calories (kcal), heart_rate, elapsed (s)."""
    reader = _Reader(data)
    return _fields(reader, reader.take("<H"), _INDOOR_BIKE_FIELDS, True)


def treadmill(data):
    """Treadmill Data: speed (km/h), distance (m), incline (%), calories,
    heart_rate, elapsed (s)."""
    reader = _Reader(data)
    return _fields(reader, reader.take("<H"), _TREADMILL_FIELDS, True)


def rower(data):
    """Rower Data: stroke_rate (strokes/min), strokes, distance (m),
    power (W), calories, heart_rate, elapsed (s)."""
    reader = _Reader(data)
    result = _fields(reader, reader.take("<H"), _ROWER_FIELDS, True)
    if "stroke_rate" in result:
        # resolution 0.5, the stroke count isn't scaled
        result["stroke_rate"] = result["stroke_rate"] / 2
    return result


PARSERS = {
    HEART_RATE_MEASUREMENT: heart_rate,
    CYCLING_POWER_MEASUREMENT: cycling_power,
    CSC_MEASUREMENT: speed_cadence,
    INDOOR_BIKE_DATA: indoor_bike,
    TREADMILL_DATA: treadmill,
    ROWER_DATA: rower,
}


class RevolutionRate:
    """Revolutions per minute from the cumulative revolutions and the time of
    the last event, as sent by power meters and speed/cadence sensors. Both
    counters wrap around."""

    # no new revolution for this long: standing still
    STOPPED_AFTER = 3

    def __init__(self, revolution_bits, time_unit):
        self._revolution_wrap = 1 << revolution_bits
        self._time_unit = time_unit
        self._last = None
        self._last_change = None
        self.rpm = None

    def update(self, revolutions, event_time, now):
        """Returns the current rpm, 0 when nothing turns any more."""
        if self._last is None:
            self._last = (revolutions, event_time)
            self._last_change = now
            return self.rpm
        last_revolutions, last_time = self._last
        delta_revolutions = (revolutions - last_revolutions) % self._revolution_wrap
        delta_time = (event_time - last_time) % 0x10000
        if delta_revolutions and delta_time:
            self.rpm = delta_revolutions * 60 * self._time_unit / delta_time
            self._last = (revolutions, event_time)
            self._last_change = now
        elif now - self._last_change >= self.STOPPED_AFTER:
            self.rpm = 0
        return self.rpm


def control_target_power(watts):
    return struct.pack("<Bh", 0x05, int(watts))


def control_simulation(grade, wind_speed=0.0, crr=0.004, cw=0.51):
    """Indoor bike simulation: grade in %, wind in m/s, rolling resistance
    coefficient and wind resistance coefficient (kg/m)."""
    return struct.pack(
        "<BhhBB",
        0x11,
        int(round(wind_speed * 1000)),
        int(round(grade * 100)),
        int(round(crr * 10000)),
        int(round(cw * 100)),
    )


CONTROL_REQUEST = bytes([0x00])
CONTROL_RESET = bytes([0x01])
CONTROL_RESPONSE = 0x80
CONTROL_RESULTS = {
    0x01: "ok",
    0x02: "not supported",
    0x03: "invalid parameter",
    0x04: "failed",
    0x05: "control not permitted",
}


def control_response(data):
    """(request op code, result text) of a control point indication, None if
    it isn't a response."""
    data = bytes(data)
    if len(data) < 3 or data[0] != CONTROL_RESPONSE:
        return None
    return data[1], CONTROL_RESULTS.get(data[2], f"error {data[2]}")
