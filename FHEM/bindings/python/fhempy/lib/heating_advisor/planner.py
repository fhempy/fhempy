"""Does a setback pay off? Compares "keep heating" with "set back and heat
up again as late as possible" with the learned model of each room.

Comfort is the felt (operative) temperature: air AND walls must be warm
again when you are back, cold walls feel unpleasant even with warm air.
The energy to warm up the walls again is counted, also after the return
(tail), because the walls are still colder then."""

import math

from . import model as m

# absences (hours) for which the saving is computed
DURATIONS = (2, 4, 6, 8, 12, 16, 24, 36, 48, 72, 96, 120, 168, 240, 336)
TAIL_HOURS = 24
# the air may be heated above the normal setpoint while heating up, so cold
# walls are compensated sooner (as long as the asymmetry limit is kept)
BOOSTS = (0.0, 1.5)
# felt temperature may be this much lower than with constant heating
COMFORT_TOLERANCE = 0.3
STEPS_PER_HOUR = int(3600 / m.DT)
HEATING_TYPES = ("heatpump", "gas", "oil", "electric", "district")
DESIGN_FLOW = {"floor": 35.0, "radiator": 55.0}


def efficiency(heating_type, ta, load, emitter="radiator"):
    """heat per final energy (COP of heat pumps). load: power / max power,
    a heat pump needs a higher flow temperature at high power"""
    if heating_type == "heatpump":
        design = DESIGN_FLOW.get(emitter, 55.0)
        flow = 20 + (design - 20) * max(min(load, 1.0), 0.05) ** (1 / 1.3)
        hot = flow + 5 + 273.15
        cold = ta - 5 + 273.15
        cop = 0.5 * hot / max(hot - cold, 5.0)
        return min(max(cop, 1.2), 7.0)
    if heating_type == "gas":
        return 0.92
    if heating_type == "oil":
        return 0.88
    return 1.0


class Room:
    """what the planner needs of a room"""

    def __init__(self, name, params, heat_to_mass, k, x0, normal, emitter):
        self.name = name
        self.model = m.Discrete(params, heat_to_mass)
        self.params = params
        self.k = k
        self.x0 = x0
        self.normal = normal
        self.emitter = emitter

    @property
    def p_max(self):
        return self.params["p_heat"]


def simulate(room, inputs, setpoints, heating_type):
    """states and final energy (W steps) for air setpoints per step
    (None = heating off)"""
    x = room.x0
    states = []
    final = 0.0
    heat = 0.0
    for row, target in zip(inputs, setpoints):
        qa, qm = room.model.gains(row["sun"], row.get("present"))
        if target is None:
            x = room.model.step(x, row["ta"], qa, qm, row.get("window"))
            power = 0.0
        else:
            power, x = room.model.power_for(
                x, row["ta"], qa, qm, row.get("window"), target, room.p_max
            )
        if power > 0:
            heat += power
            final += power / efficiency(
                heating_type, row["ta"], power / room.p_max, room.emitter
            )
        states.append(x)
    return states, heat, final


def comfortable(room, state, reference, basis, max_asymmetry):
    ti, tm = state
    if basis == "air":
        return ti >= reference[0] - COMFORT_TOLERANCE
    top = m.operative_temp(ti, tm, room.k)
    asym = ti - m.surface_temp(ti, tm, room.k)
    ref_top = m.operative_temp(reference[0], reference[1], room.k)
    return top >= ref_top - COMFORT_TOLERANCE and asym <= max(
        max_asymmetry, reference[0] - m.surface_temp(*reference, room.k) + 0.2
    )


def plan(
    room,
    inputs,
    absence_steps,
    setback,
    heating_type,
    basis="operative",
    max_asymmetry=3.0,
    boosts=BOOSTS,
):
    """best plan for one setback temperature (None = off). Returns dict:
    keep/setback final energy (W steps), reheat step (latest start of
    heating up), boost and feasible (comfort reached at the return)"""
    total = len(inputs)
    keep_points = [room.normal] * total
    keep_states, keep_heat, keep_final = simulate(
        room, inputs, keep_points, heating_type
    )
    reference = keep_states[absence_steps - 1]
    best = None
    for boost in boosts:

        def setpoints(reheat, boost=boost):
            points = [setback] * reheat
            points += [room.normal + boost] * (absence_steps - reheat)
            points += [room.normal] * (total - absence_steps)
            return points

        def run(reheat):
            return simulate(room, inputs, setpoints(reheat), heating_type)

        def ready(states):
            return comfortable(
                room, states[absence_steps - 1], reference, basis, max_asymmetry
            )

        # latest reheat start which is still comfortable at the return
        low, high = 0, absence_steps
        result_low = None
        if not ready(run(low)[0]):
            continue
        while high - low > 1:
            mid = (low + high) // 2
            if ready(run(mid)[0]):
                low = mid
            else:
                high = mid
        if low == 0:
            continue
        # a boost only for the last part, then back to normal: here the
        # whole reheat phase is boosted, the thermostat limits the power
        states, heat, final = run(low)
        result_low = {
            "reheat": low,
            "boost": boost,
            "final": final,
            "heat": heat,
            "states": states,
        }
        if best is None or result_low["final"] < best["final"]:
            best = result_low
    return {
        "keep_final": keep_final,
        "keep_heat": keep_heat,
        "keep_states": keep_states,
        "setback": setback,
        "best": best,
    }


def setback_candidates(normal, setback, min_temp):
    """setback temperatures which are tried; setback None = automatic"""
    if setback is not None:
        return [max(setback, min_temp)]
    values = {max(min_temp, round(normal - 2)), max(min_temp, round(normal - 4))}
    values.add(min_temp)
    return sorted(v for v in values if v < normal)


def best_plan(
    room,
    inputs,
    absence_steps,
    setback,
    min_temp,
    heating_type,
    basis="operative",
    max_asymmetry=3.0,
):
    """plan with the setback temperature which saves most"""
    best = None
    for candidate in setback_candidates(room.normal, setback, min_temp):
        result = plan(
            room,
            inputs,
            absence_steps,
            candidate,
            heating_type,
            basis,
            max_asymmetry,
        )
        result["saving"] = (
            result["keep_final"] - result["best"]["final"]
            if result["best"] is not None
            else 0.0
        )
        if best is None or result["saving"] > best["saving"]:
            best = result
    return best


def kwh(watt_steps, scale):
    return watt_steps * m.DT / 3600 / 1000 * scale


def constant_inputs(ta, steps):
    return [{"ta": ta, "sun": (0.0, 0.0, 0.0), "present": 0.0, "window": 0.0}] * steps


def steady_state(room, ta):
    """state of a room heated to its setpoint for a long time at ta"""
    qa, qm = room.model.gains((0.0, 0.0, 0.0), 0.0)
    return (room.normal, room.model.steady_mass(room.normal, ta, qm))


def savings_by_duration(
    rooms,
    inputs_for,
    setback,
    min_temp,
    heating_type,
    scale,
    basis="operative",
    max_asymmetry=3.0,
    durations=DURATIONS,
):
    """for each absence duration: saving of the whole house.
    inputs_for(steps) gives the weather for that many steps.
    Returns list of dicts duration_h, keep_kwh, saving_kwh, saving_pct,
    per room details"""
    results = []
    for hours in durations:
        absence = hours * STEPS_PER_HOUR
        steps = absence + TAIL_HOURS * STEPS_PER_HOUR
        inputs = inputs_for(steps)
        keep = saving = 0.0
        per_room = {}
        for room in rooms:
            result = best_plan(
                room,
                inputs,
                absence,
                setback,
                min_temp,
                heating_type,
                basis,
                max_asymmetry,
            )
            keep += result["keep_final"]
            saving += max(result["saving"], 0.0)
            per_room[room.name] = result
        results.append(
            {
                "hours": hours,
                "keep_kwh": kwh(keep, scale),
                "saving_kwh": kwh(saving, scale),
                "saving_pct": 100 * saving / keep if keep > 0 else 0.0,
                "rooms": per_room,
            }
        )
    return results


def worth_from(results, threshold_pct, threshold_kwh, room=None):
    """smallest duration (hours) from which a setback saves enough,
    None if never (up to the longest duration)"""
    for result in results:
        if room is None:
            pct, saved = result["saving_pct"], result["saving_kwh"]
        else:
            r = result["rooms"].get(room)
            if r is None or r["keep_final"] <= 0:
                continue
            pct = 100 * max(r["saving"], 0.0) / r["keep_final"]
            saved = None
        if pct >= threshold_pct and (saved is None or saved >= threshold_kwh):
            return result["hours"]
    return None


def reheat_hours(
    room, ta, setback, heating_type, basis="operative", max_asymmetry=3.0, max_hours=72
):
    """how long heating up from a long setback takes until the room is
    comfortable again (air only and air + walls)"""
    model = room.model
    qa, qm = model.gains((0.0, 0.0, 0.0), 0.0)
    # cooled down state: air at the setback temperature, mass in equilibrium
    x = (setback, model.steady_mass(setback, ta, qm))
    reference = steady_state(room, ta)
    air_hours = None
    for step in range(max_hours * STEPS_PER_HOUR):
        power, x = model.power_for(x, ta, qa, qm, 0.0, room.normal, room.p_max)
        if air_hours is None and x[0] >= room.normal - COMFORT_TOLERANCE:
            air_hours = (step + 1) / STEPS_PER_HOUR
        if comfortable(room, x, reference, basis, max_asymmetry):
            return air_hours, (step + 1) / STEPS_PER_HOUR
    return air_hours, None


def forecast_off(room, inputs):
    """states with heating off from the current state"""
    states, _, _ = simulate(room, inputs, [None] * len(inputs), "electric")
    return states


def hours_text(hours):
    if hours is None:
        return "never"
    if hours < 48:
        return f"{hours:g} h"
    days = hours / 24
    return f"{days:.1f} days".replace(".0 days", " days")


def first_below(states, limit):
    for i, (ti, _) in enumerate(states):
        if ti < limit:
            return i
    return None


def clamp(value, low, high):
    return min(max(value, low), high)


def isfinite(value):
    return value is not None and math.isfinite(value)
