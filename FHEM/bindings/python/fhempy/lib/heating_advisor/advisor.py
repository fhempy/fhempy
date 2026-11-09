"""Learning per room: grid rows + weather -> model rows -> fitted model.
Pure functions (blocking, CPU only), no FHEM access."""

import math
import statistics

from . import model, weather

SLOT = int(model.DT)
# heating is off below this setpoint (frost protection / "off")
OFF_SETPOINT = 8.0
# setpoint reached: heating idles / setpoint far away: full power
ABOVE_SETPOINT = 0.4
BELOW_SETPOINT = 0.7
# no heating needed at this daily mean outdoor temperature
SUMMER_TEMP = 16.0
# airing without contact: drop per slot
AIRING_DROP = 0.4
AIRING_SLOTS = 4
HOLDOUT_DAYS = 7
MIN_DAYS = 3
GOOD_DAYS = 14


def slot_of(ts):
    return int(ts // SLOT * SLOT)


def heating_of(row, daily_ta):
    """share of heating power 0..1, None if unknown"""
    if row.get("valve") is not None:
        return row["valve"]
    setp, y = row.get("setp"), row.get("y")
    if setp is not None and y is not None:
        if setp <= OFF_SETPOINT:
            return 0.0
        if y > setp + ABOVE_SETPOINT:
            return 0.0
        if y < setp - BELOW_SETPOINT:
            return 1.0
        return None
    if daily_ta is not None and daily_ta > SUMMER_TEMP:
        return 0.0
    return None


def model_rows(grid, wx, lat, lon, has_contacts, ta_bias=0.0):
    """rows for model.run_filter from grid rows of one room (sorted, any
    gaps) and a weather.Weather. Gaps become steps without measurement."""
    if not grid:
        return []
    by_ts = {row["ts"]: row for row in grid}
    start, end = grid[0]["ts"], grid[-1]["ts"]
    # daily mean outdoor temperature for the summer rule
    rows = []
    airing_left = 0
    last_y = None
    ta_hist = []
    for ts in range(start, end + SLOT, SLOT):
        g = by_ts.get(ts, {})
        w = wx.at(ts + SLOT / 2)
        ta = g.get("ta")
        if ta is None and w is not None:
            ta = w[0] + ta_bias
        if ta is None:
            ta = ta_hist[-1] if ta_hist else 5.0
        ta_hist.append(ta)
        if len(ta_hist) > 96:
            ta_hist.pop(0)
        if w is not None:
            sun = weather.sun_at(ts + SLOT / 2, lat, lon, w[1], w[2])
        else:
            direct, diffuse = weather.clear_sky(ts + SLOT / 2, lat, lon)
            sun = weather.facade_sun(
                direct * 0.4, diffuse, *weather.sun_position(ts + SLOT / 2, lat, lon)
            )
        y = g.get("y")
        window = g.get("window")
        if window is None and not has_contacts:
            window = 0.0
        if g.get("detected"):
            airing_left = AIRING_SLOTS
        elif (
            not has_contacts
            and y is not None
            and last_y is not None
            and y - last_y < -AIRING_DROP
        ):
            airing_left = AIRING_SLOTS
        if airing_left > 0:
            airing_left -= 1
            window = None
        if y is not None:
            last_y = y
        daily = sum(ta_hist) / len(ta_hist) if len(ta_hist) >= 48 else None
        rows.append(
            {
                "ts": ts,
                "y": y,
                "ta": ta,
                "sun": sun,
                "present": g.get("present") if g.get("present") is not None else 0.5,
                "h": heating_of(g, daily) if g else None,
                "window": window if g else None,
                "surface": g.get("surface"),
                "setp": g.get("setp"),
            }
        )
    return rows


def usable(rows):
    return sum(
        1
        for row in rows
        if row.get("y") is not None
        and row.get("h") is not None
        and row.get("window") is not None
    )


def off_steps(rows):
    return sum(
        1
        for row in rows
        if row.get("y") is not None
        and (row.get("h") is not None and row["h"] <= 0)
        and (row.get("window") is not None and row["window"] <= 0)
    )


def fit_room(rows, heat_to_mass, old=None, max_evals=900):
    """fits the model of a room. old: previous result (dict with params,
    rmse) which is kept if the new fit forecasts worse.
    Returns dict params, rmse, days, usable, off_hours, surface_k, accepted"""
    days = len(rows) / (86400 / SLOT)
    n_usable = usable(rows)
    holdout = int(HOLDOUT_DAYS * 86400 / SLOT)
    if days >= MIN_DAYS + HOLDOUT_DAYS:
        train = rows[: len(rows) - holdout]
        test_start = len(rows) - holdout
    else:
        train, test_start = rows, max(len(rows) - int(86400 / SLOT), 0)
    fixed = {}
    if sum(1 for row in train if (row.get("h") or 0) > 0.3) < 8:
        # no heating seen: its power can't be learned
        fixed["p_heat"] = (
            (old or {}).get("params", {}).get("p_heat", model.PRIORS["p_heat"][0])
        )
    if not any(row.get("present") not in (None, 0.5) for row in train):
        fixed["p_pres"] = model.PRIORS["p_pres"][0]
    if not any((row.get("window") or 0) > 0 for row in train):
        fixed["h_win"] = (
            (old or {}).get("params", {}).get("h_win", model.PRIORS["h_win"][0])
        )
    start = (old or {}).get("params")
    params, _ = model.fit(
        train, heat_to_mass, start=start, fixed=fixed, max_evals=max_evals
    )
    rmse = model.forecast_rmse(params, rows, heat_to_mass, test_start)
    accepted = True
    if old and old.get("params"):
        old_rmse = model.forecast_rmse(old["params"], rows, heat_to_mass, test_start)
        if old_rmse is not None and (rmse is None or rmse > old_rmse * 1.05):
            params, rmse, accepted = old["params"], old_rmse, False
    collected = []
    model.run_filter(params, rows, heat_to_mass, collect=collected)
    by_id = {id(row): row for row in rows}
    surface = [by_id[id(r)].get("surface") for r, _, _, _ in collected]
    k = model.fit_surface_k(collected, surface)
    return {
        "params": params,
        "rmse": rmse,
        "days": round(days, 1),
        "usable": n_usable,
        "off_hours": round(off_steps(rows) * SLOT / 3600, 1),
        "surface_k": k,
        "accepted": accepted,
    }


def state_of(result):
    """learning, ready or good"""
    if not result or result.get("days", 0) < MIN_DAYS:
        return "learning"
    if result.get("off_hours", 0) < 8:
        return "learning"
    rmse = result.get("rmse")
    if rmse is None or rmse > 1.0:
        return "learning"
    if rmse <= 0.5 and result.get("days", 0) >= GOOD_DAYS:
        return "good"
    return "ready"


def heat_loss_w_per_k(params):
    """heat loss of the room per K in steady state (nominal units)"""
    return 1 / params["r_ia"] + 1 / (params["r_im"] + params["r_ma"])


def storage_j_per_k(params):
    return model.CI * (1 + params["cm_ratio"])


def time_constants_h(params):
    """(air, mass) time constants in hours (eigenvalues of the model)"""
    p = params
    cm = model.CI * p["cm_ratio"]
    a11 = -(1 / p["r_im"] + 1 / p["r_ia"]) / model.CI
    a12 = 1 / (p["r_im"] * model.CI)
    a21 = 1 / (p["r_im"] * cm)
    a22 = -(1 / p["r_im"] + 1 / p["r_ma"]) / cm
    tr = a11 + a22
    det = a11 * a22 - a12 * a21
    root = math.sqrt(max(tr * tr / 4 - det, 0.0))
    l1, l2 = tr / 2 + root, tr / 2 - root
    return -1 / l2 / 3600, -1 / l1 / 3600


def normal_setpoint(grid, default=21.0):
    """the usual comfort setpoint: upper quartile of setpoints >= 17 °C"""
    values = [row["setp"] for row in grid if row.get("setp") and row["setp"] >= 17]
    if not values:
        return default
    values.sort()
    return values[int(len(values) * 0.75) - 1 if len(values) > 3 else -1]


def ta_bias(grid, wx):
    """mean difference of the outdoor sensor and Open-Meteo"""
    diffs = []
    for row in grid:
        if row.get("ta") is None:
            continue
        w = wx.at(row["ts"] + SLOT / 2)
        if w is not None:
            diffs.append(row["ta"] - w[0])
    if len(diffs) < 96:
        return 0.0
    return max(min(statistics.median(diffs), 5.0), -5.0)
