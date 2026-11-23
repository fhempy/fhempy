"""Grundfos ALPHA circulation pumps: estimated flow from the electrical
power and the selected setting, and the heat delivered to the house.

The values are approximations from the data sheets (maximum head, maximum
flow, power range). A pump on a given setting runs on a known curve, the
power it takes rises with the flow, so the power tells the flow. Expect
about +-25 %, attr flow_factor calibrates it (e.g. with a heat meter).
"""

import math

# model: (max head m, max flow m³/h, min power W, max power W)
MODELS = {
    "ALPHA1 25-40": (4.0, 2.5, 4.0, 22.0),
    "ALPHA1 25-60": (6.0, 3.0, 4.0, 40.0),
    "ALPHA1 25-65": (6.5, 3.2, 4.0, 45.0),
    "ALPHA1 32-60": (6.0, 3.0, 4.0, 40.0),
    "ALPHA1 L 15-40": (4.0, 2.4, 4.0, 25.0),
    "ALPHA1 L 15-60": (6.0, 2.9, 4.0, 45.0),
    "ALPHA1 L 25-40": (4.0, 2.4, 4.0, 25.0),
    "ALPHA1 L 25-60": (6.0, 2.9, 4.0, 45.0),
    "ALPHA1 L 32-40": (4.0, 2.4, 4.0, 25.0),
    "ALPHA1 L 32-60": (6.0, 2.9, 4.0, 45.0),
    "ALPHA2 15-40": (4.0, 2.6, 3.0, 18.0),
    "ALPHA2 15-60": (6.0, 3.0, 3.0, 34.0),
    "ALPHA2 25-40": (4.0, 2.6, 3.0, 18.0),
    "ALPHA2 25-50": (5.0, 2.8, 3.0, 26.0),
    "ALPHA2 25-60": (6.0, 3.0, 3.0, 34.0),
    "ALPHA2 25-80": (8.0, 3.6, 3.0, 50.0),
    "ALPHA2 32-40": (4.0, 2.6, 3.0, 18.0),
    "ALPHA2 32-60": (6.0, 3.0, 3.0, 34.0),
    "ALPHA2 32-80": (8.0, 3.6, 3.0, 50.0),
    "ALPHA2 L 15-40": (4.0, 2.4, 5.0, 22.0),
    "ALPHA2 L 15-60": (6.0, 2.9, 5.0, 45.0),
    "ALPHA2 L 25-40": (4.0, 2.4, 5.0, 22.0),
    "ALPHA2 L 25-60": (6.0, 2.9, 5.0, 45.0),
    "ALPHA2 L 32-40": (4.0, 2.4, 5.0, 22.0),
    "ALPHA2 L 32-60": (6.0, 2.9, 5.0, 45.0),
    "ALPHA3 15-40": (4.0, 2.6, 3.0, 18.0),
    "ALPHA3 15-60": (6.0, 3.0, 3.0, 34.0),
    "ALPHA3 25-40": (4.0, 2.6, 3.0, 18.0),
    "ALPHA3 25-60": (6.0, 3.0, 3.0, 34.0),
    "ALPHA3 25-80": (8.0, 3.6, 3.0, 50.0),
    "ALPHA3 32-40": (4.0, 2.6, 3.0, 18.0),
    "ALPHA3 32-60": (6.0, 3.0, 3.0, 34.0),
    "ALPHA3 32-80": (8.0, 3.6, 3.0, 50.0),
}

# setting: (kind, fraction of the max head or speed)
SETTINGS = {
    "AUTOADAPT": ("pp", 0.55),
    "PP1": ("pp", 0.4),
    "PP2": ("pp", 0.55),
    "PP3": ("pp", 0.75),
    "CP1": ("cp", 0.4),
    "CP2": ("cp", 0.55),
    "CP3": ("cp", 0.75),
    "I": ("speed", 0.6),
    "II": ("speed", 0.8),
    "III": ("speed", 1.0),
}
# the ALPHA1 L and ALPHA2 L have no AUTOadapt
NO_AUTOADAPT = ("ALPHA1 L", "ALPHA2 L")

# water at 30-60 °C: 0.985 kg/l * 4.18 kJ/(kg K) / 3600 s/h
WATT_PER_LH_K = 1.144
# hydraulic power W per (m³/h * m): rho * g / 3600
HYD_W = 1000 * 9.81 / 3600


def model_names():
    return list(MODELS)


def settings_of(model):
    names = list(SETTINGS)
    if model and model.startswith(NO_AUTOADAPT):
        names.remove("AUTOADAPT")
    return names


def normalize_setting(text):
    """'PP2', 'pp 2', 'Stufe 3' (speed III), 'auto', '2' -> setting name"""
    if text is None:
        return None
    s = str(text).strip().upper().replace(" ", "").replace("-", "")
    s = s.replace("STUFE", "").replace("SPEED", "").replace("KONSTANTKURVE", "")
    roman = {"1": "I", "2": "II", "3": "III"}
    if s in roman:
        return roman[s]
    if s.startswith("AUTO"):
        return "AUTOADAPT"
    if s in ("PP", "CP"):
        return s + "2"
    return s if s in SETTINGS else None


def _max_head(head, flow, q):
    return head * max(0.0, 1 - (q / flow) ** 2)


def head_at(model, setting, q):
    """head in m on this setting at flow q m³/h"""
    head, flow, _, _ = MODELS[model]
    kind, fraction = SETTINGS[setting]
    if kind == "speed":
        return _max_head(fraction**2 * head, fraction * flow, q)
    if kind == "cp":
        h = fraction * head
    else:
        h = fraction * head * (0.5 + 0.5 * q / flow)
    return min(h, _max_head(head, flow, q))


def _reference(model):
    head, flow, _, _ = MODELS[model]
    # best point of the max curve takes the max power
    q = flow / math.sqrt(3)
    return q * _max_head(head, flow, q)


def power_at(model, setting, q):
    """electrical power W at flow q m³/h"""
    _, _, p_min, p_max = MODELS[model]
    hyd = q * head_at(model, setting, q)
    return p_min + (p_max - p_min) * min(hyd / _reference(model), 1.0)


def _flow_limit(model, setting):
    """largest flow with power still rising (behind it the curve falls)"""
    _, flow, _, _ = MODELS[model]
    best_q, best_p = 0.0, 0.0
    for i in range(1, 201):
        q = flow * i / 200
        p = power_at(model, setting, q)
        if p > best_p + 1e-9:
            best_q, best_p = q, p
    return best_q


def estimate_flow(model, setting, power):
    """flow in l/h from the electrical power, None if unknown"""
    setting = normalize_setting(setting)
    if model not in MODELS or setting is None or power is None:
        return None
    _, _, p_min, _ = MODELS[model]
    if power <= p_min:
        return 0.0
    low, high = 0.0, _flow_limit(model, setting)
    if power >= power_at(model, setting, high):
        return round(high * 1000, 0)
    for _ in range(40):
        mid = (low + high) / 2
        if power_at(model, setting, mid) < power:
            low = mid
        else:
            high = mid
    return round((low + high) / 2 * 1000, 0)


def heat_watts(flow_lh, flow_temp, return_temp):
    """heat delivered to the house in W"""
    if flow_lh is None or flow_temp is None or return_temp is None:
        return None
    return max(0.0, flow_lh * WATT_PER_LH_K * (flow_temp - return_temp))
