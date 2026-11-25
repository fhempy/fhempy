"""Grey-box thermal model of a room (2R2C), pure Python without numpy.

Two temperatures: the air with furniture surfaces (Ti, capacity Ci) and the
thermal mass of walls, ceilings and floors (Tm, capacity Cm):

    Ci dTi/dt = (Tm - Ti)/Rim + (Ta - Ti)(1/Ria + Hv w) + Qair
    Cm dTm/dt = (Ti - Tm)/Rim + (Ta - Tm)/Rma + Qmass

Qair/Qmass are sun, internal gains and heating. Without a heat meter the
absolute size of a room can't be seen in temperatures, so Ci is fixed to a
nominal value and all other values are relative to it; energies are scaled
by the house factor (see advisor) when a meter or the heating power is known.

The parameters are fitted by maximum a posteriori: a Kalman filter computes
the likelihood of the measured air temperature (Tm is never measured),
priors keep the values near typical houses while there is little data.
"""

import math
import random

DT = 900.0
CI = 1.0e6
# share of the sun which heats the air directly, the rest heats the floor
# and walls it shines on
SUN_TO_AIR = 0.4
# heating power going directly into the mass: radiators heat the air
# (some radiation), floor heating the floor
HEAT_TO_MASS = {"radiator": 0.15, "floor": 0.7}
# default share of the way from air to mass where the surfaces are
SURFACE_K = 0.35
# measurement noise of the air temperature (K) and process noise per step
MEAS_SD = 0.12
PROC_SD = (0.06, 0.01)
# process noise while the heating is unknown: the filter follows the
# measurements, these steps don't count for the likelihood
UNKNOWN_SD = 0.6
WINDOW_LEVELS = 4

# name: (prior median, prior sd of log, lower, upper)
PRIORS = {
    "cm_ratio": (12.0, 1.0, 1.0, 200.0),
    "r_ia": (1 / 15.0, 1.0, 1 / 1000.0, 2.0),
    "r_im": (1 / 150.0, 1.0, 1 / 5000.0, 0.5),
    "r_ma": (1 / 25.0, 1.0, 1 / 1000.0, 2.0),
    "h_win": (25.0, 1.0, 0.5, 1000.0),
    "g_e": (0.5, 1.5, 0.005, 50.0),
    "g_s": (1.0, 1.5, 0.005, 50.0),
    "g_w": (0.5, 1.5, 0.005, 50.0),
    "p0": (80.0, 1.2, 1.0, 5000.0),
    "p_pres": (60.0, 1.5, 1.0, 5000.0),
    "p_heat": (1500.0, 1.0, 50.0, 50000.0),
}
NAMES = tuple(PRIORS)


def default_params():
    return {name: prior[0] for name, prior in PRIORS.items()}


# --- 2x2 linear algebra ---


def _expm2(a, t):
    """exp(A t) of a 2x2 matrix with real eigenvalues (RC networks)"""
    (a11, a12), (a21, a22) = a
    tr = a11 + a22
    det = a11 * a22 - a12 * a21
    disc = tr * tr / 4 - det
    root = math.sqrt(max(disc, 0.0))
    l1, l2 = tr / 2 + root, tr / 2 - root
    if abs(l1 - l2) < 1e-15:
        e = math.exp(l1 * t)
        return [
            [e * (1 + (a11 - l1) * t), e * a12 * t],
            [e * a21 * t, e * (1 + (a22 - l1) * t)],
        ]
    e1, e2 = math.exp(l1 * t), math.exp(l2 * t)
    c = 1 / (l1 - l2)
    return [
        [c * (e1 * (a11 - l2) - e2 * (a11 - l1)), c * (e1 - e2) * a12],
        [c * (e1 - e2) * a21, c * (e1 * (a22 - l2) - e2 * (a22 - l1))],
    ]


def _solve2(a, b):
    """A^-1 b for a 2x2 matrix and a 2 vector"""
    (a11, a12), (a21, a22) = a
    det = a11 * a22 - a12 * a21
    return (
        (a22 * b[0] - a12 * b[1]) / det,
        (-a21 * b[0] + a11 * b[1]) / det,
    )


class Discrete:
    """the model for one time step, one variant per window level"""

    def __init__(self, params, heat_to_mass=HEAT_TO_MASS["radiator"], dt=DT):
        self.params = params
        self.heat_to_mass = heat_to_mass
        self.dt = dt
        p = params
        cm = CI * p["cm_ratio"]
        self.variants = []
        for level in range(WINDOW_LEVELS + 1):
            w = level / WINDOW_LEVELS
            g_air = 1 / p["r_ia"] + p["h_win"] * w
            a = [
                [-(1 / p["r_im"] + g_air) / CI, 1 / (p["r_im"] * CI)],
                [1 / (p["r_im"] * cm), -(1 / p["r_im"] + 1 / p["r_ma"]) / cm],
            ]
            ad = _expm2(a, dt)
            ad_minus_i = [[ad[0][0] - 1, ad[0][1]], [ad[1][0], ad[1][1] - 1]]

            def column(b, ad_minus_i=ad_minus_i, a=a):
                # A^-1 (Ad - I) b
                v = (
                    ad_minus_i[0][0] * b[0] + ad_minus_i[0][1] * b[1],
                    ad_minus_i[1][0] * b[0] + ad_minus_i[1][1] * b[1],
                )
                return _solve2(a, v)

            b_ta = column((g_air / CI, 1 / (p["r_ma"] * cm)))
            b_qa = column((1 / CI, 0.0))
            b_qm = column((0.0, 1 / cm))
            self.variants.append((ad, b_ta, b_qa, b_qm))

    def variant(self, window):
        level = int(round(min(max(window or 0.0, 0.0), 1.0) * WINDOW_LEVELS))
        return self.variants[level]

    def gains(self, sun, present):
        """(Qair, Qmass) without heating in W, sun = (east, south, west)"""
        p = self.params
        q_sun = p["g_e"] * sun[0] + p["g_s"] * sun[1] + p["g_w"] * sun[2]
        q_int = p["p0"] + p["p_pres"] * (present or 0.0)
        return q_sun * SUN_TO_AIR + q_int, q_sun * (1 - SUN_TO_AIR)

    def heat(self, power):
        return power * (1 - self.heat_to_mass), power * self.heat_to_mass

    def step(self, x, ta, qa, qm, window=0.0):
        ad, b_ta, b_qa, b_qm = self.variant(window)
        return (
            ad[0][0] * x[0]
            + ad[0][1] * x[1]
            + b_ta[0] * ta
            + b_qa[0] * qa
            + b_qm[0] * qm,
            ad[1][0] * x[0]
            + ad[1][1] * x[1]
            + b_ta[1] * ta
            + b_qa[1] * qa
            + b_qm[1] * qm,
        )

    def power_for(self, x, ta, qa, qm, window, target, p_max):
        """heating power which brings the air to target at the end of the
        step (what a thermostat does), limited to 0..p_max"""
        free = self.step(x, ta, qa, qm, window)
        if free[0] >= target:
            return 0.0, free
        ad, b_ta, b_qa, b_qm = self.variant(window)
        per_watt = b_qa[0] * (1 - self.heat_to_mass) + b_qm[0] * self.heat_to_mass
        power = min(max((target - free[0]) / per_watt, 0.0), p_max)
        hq_a, hq_m = self.heat(power)
        return power, (
            free[0] + b_qa[0] * hq_a + b_qm[0] * hq_m,
            free[1] + b_qa[1] * hq_a + b_qm[1] * hq_m,
        )

    def steady_mass(self, ti, ta, qm=0.0):
        """mass temperature in equilibrium with the air at ti"""
        p = self.params
        g_im, g_ma = 1 / p["r_im"], 1 / p["r_ma"]
        return (g_im * ti + g_ma * ta + qm) / (g_im + g_ma)


def surface_temp(ti, tm, k=SURFACE_K):
    """mean temperature of the room surfaces (walls, floor, windows)"""
    return ti - (ti - tm) * k


def operative_temp(ti, tm, k=SURFACE_K):
    """felt temperature: mean of air and surfaces (radiation)"""
    return (ti + surface_temp(ti, tm, k)) / 2


# --- Kalman filter ---


class Filter:
    """live state estimation, also used to compute the likelihood"""

    def __init__(self, model, x=None, p=None):
        self.model = model
        self.x = x
        self.p = p or [[1.0, 0.0], [0.0, 4.0]]

    def predict(self, row):
        """row: dict with ta, sun, present, heat (W or None), window"""
        m = self.model
        qa, qm = m.gains(row["sun"], row.get("present"))
        heat = row.get("heat")
        if heat is not None:
            ha, hm = m.heat(heat)
            qa, qm = qa + ha, qm + hm
        ad = m.variant(row.get("window"))[0]
        self.x = m.step(self.x, row["ta"], qa, qm, row.get("window"))
        p = self.p
        # Ad P Ad^T + Q
        t00 = ad[0][0] * p[0][0] + ad[0][1] * p[1][0]
        t01 = ad[0][0] * p[0][1] + ad[0][1] * p[1][1]
        t10 = ad[1][0] * p[0][0] + ad[1][1] * p[1][0]
        t11 = ad[1][0] * p[0][1] + ad[1][1] * p[1][1]
        sd0 = PROC_SD[0] if heat is not None else UNKNOWN_SD
        self.p = [
            [
                t00 * ad[0][0] + t01 * ad[0][1] + sd0 * sd0,
                t00 * ad[1][0] + t01 * ad[1][1],
            ],
            [
                t10 * ad[0][0] + t11 * ad[0][1],
                t10 * ad[1][0] + t11 * ad[1][1] + PROC_SD[1] * PROC_SD[1],
            ],
        ]

    def update(self, y):
        """measurement of the air temperature, returns (innovation, variance)"""
        p = self.p
        s = p[0][0] + MEAS_SD * MEAS_SD
        e = y - self.x[0]
        k0, k1 = p[0][0] / s, p[1][0] / s
        self.x = (self.x[0] + k0 * e, self.x[1] + k1 * e)
        self.p = [
            [p[0][0] - k0 * p[0][0], p[0][1] - k0 * p[0][1]],
            [p[1][0] - k1 * p[0][0], p[1][1] - k1 * p[0][1]],
        ]
        return e, s

    def start(self, row):
        y = row["y"]
        self.x = (y, self.model.steady_mass(y, row["ta"]))


def heat_of(row, p_heat):
    h = row.get("h")
    return None if h is None else h * p_heat


def run_filter(params, rows, heat_to_mass, collect=None):
    """negative log likelihood of rows (list of dicts with y, ta, sun,
    present, h 0..1 or None, window or None = unknown/excluded)"""
    model = Discrete(params, heat_to_mass)
    filt = Filter(model)
    nll = 0.0
    count = 0
    for row in rows:
        y = row.get("y")
        if filt.x is None:
            if y is None:
                continue
            filt.start(row)
            continue
        known = row.get("h") is not None and row.get("window") is not None
        filt.predict(
            {
                "ta": row["ta"],
                "sun": row["sun"],
                "present": row.get("present"),
                "heat": heat_of(row, params["p_heat"]) if known else None,
                "window": row.get("window") or 0.0,
            }
        )
        if y is None:
            continue
        e, s = filt.update(y)
        if known:
            nll += 0.5 * (math.log(s) + e * e / s)
            count += 1
        if collect is not None:
            collect.append((row, filt.x, e, s))
    return nll, count, filt


def _to_theta(params):
    return [math.log(params[name]) for name in NAMES]


def _from_theta(theta):
    params = {}
    for name, value in zip(NAMES, theta):
        _, _, low, high = PRIORS[name]
        params[name] = min(max(math.exp(value), low), high)
    return params


def _objective(theta, rows, heat_to_mass, fixed):
    params = _from_theta(theta)
    params.update(fixed)
    nll, count, _ = run_filter(params, rows, heat_to_mass)
    penalty = 0.0
    for name, value in zip(NAMES, theta):
        if name in fixed:
            continue
        median, sd, _, _ = PRIORS[name]
        z = (value - math.log(median)) / sd
        penalty += 0.5 * z * z
    return nll + penalty


def nelder_mead(f, x0, step=0.5, max_evals=600, tol=1e-4, rng=None):
    """minimum of f, plain Nelder-Mead"""
    n = len(x0)
    simplex = [list(x0)]
    for i in range(n):
        x = list(x0)
        x[i] += step
        simplex.append(x)
    values = [f(x) for x in simplex]
    evals = n + 1
    while evals < max_evals:
        order = sorted(range(n + 1), key=lambda i: values[i])
        simplex = [simplex[i] for i in order]
        values = [values[i] for i in order]
        if abs(values[-1] - values[0]) < tol * (abs(values[0]) + 1e-9):
            break
        centroid = [sum(x[i] for x in simplex[:-1]) / n for i in range(n)]
        worst = simplex[-1]
        reflected = [c + (c - w) for c, w in zip(centroid, worst)]
        fr = f(reflected)
        evals += 1
        if fr < values[0]:
            expanded = [c + 2 * (c - w) for c, w in zip(centroid, worst)]
            fe = f(expanded)
            evals += 1
            if fe < fr:
                simplex[-1], values[-1] = expanded, fe
            else:
                simplex[-1], values[-1] = reflected, fr
        elif fr < values[-2]:
            simplex[-1], values[-1] = reflected, fr
        else:
            contracted = [c + 0.5 * (w - c) for c, w in zip(centroid, worst)]
            fc = f(contracted)
            evals += 1
            if fc < values[-1]:
                simplex[-1], values[-1] = contracted, fc
            else:
                best = simplex[0]
                for i in range(1, n + 1):
                    simplex[i] = [b + 0.5 * (x - b) for b, x in zip(best, simplex[i])]
                    values[i] = f(simplex[i])
                evals += n
    best = min(range(n + 1), key=lambda i: values[i])
    return simplex[best], values[best]


def fit(rows, heat_to_mass, start=None, fixed=None, max_evals=900):
    """MAP estimate of the parameters. fixed: parameters which can't be
    learned from the data (e.g. p_heat without heating phases)"""
    fixed = dict(fixed or {})
    params = dict(default_params())
    params.update(start or {})
    names = [name for name in NAMES if name not in fixed]
    theta_all = _to_theta(params)
    index = [NAMES.index(name) for name in names]

    def f(sub):
        theta = list(theta_all)
        for i, value in zip(index, sub):
            theta[i] = value
        return _objective(theta, rows, heat_to_mass, fixed)

    x0 = [theta_all[i] for i in index]
    best, value = nelder_mead(f, x0, max_evals=max_evals)
    # second run from the result, Nelder-Mead often stops early in 10 dims
    best, value = nelder_mead(f, best, step=0.2, max_evals=max_evals // 2)
    theta = list(theta_all)
    for i, v in zip(index, best):
        theta[i] = v
    result = _from_theta(theta)
    result.update(fixed)
    return result, value


def fit_surface_k(collected, surface):
    """share k of Ts = Ti - (Ti - Tm) k from measured surface temperatures:
    least squares over the filtered states. collected from run_filter,
    surface: list of measured surface temperatures (None if missing)"""
    num = den = 0.0
    for (row, x, _, _), ts in zip(collected, surface):
        if ts is None:
            continue
        d = x[0] - x[1]
        num += (x[0] - ts) * d
        den += d * d
    if den < 1.0:
        return None
    return min(max(num / den, 0.05), 0.95)


def forecast_rmse(params, rows, heat_to_mass, start, horizon=48, every=24):
    """open loop forecast error (K) of the air temperature over horizon
    steps, starting every `every` steps from the filtered state at row
    index >= start. Only forecasts where the heating is known count."""
    model = Discrete(params, heat_to_mass)
    collected = []
    run_filter(params, rows, heat_to_mass, collect=collected)
    by_index = {id(row): i for i, row in enumerate(rows)}
    states = {by_index[id(row)]: x for row, x, _, _ in collected}
    errors = []
    for begin in range(start, len(rows) - horizon, every):
        x = states.get(begin)
        if x is None:
            continue
        ok = True
        for row in rows[begin + 1 : begin + 1 + horizon]:
            if row.get("h") is None or row.get("window") is None:
                ok = False
                break
            qa, qm = model.gains(row["sun"], row.get("present"))
            ha, hm = model.heat(heat_of(row, params["p_heat"]))
            x = model.step(x, row["ta"], qa + ha, qm + hm, row["window"])
            if row.get("y") is not None:
                errors.append(x[0] - row["y"])
        if not ok:
            continue
    if not errors:
        return None
    return math.sqrt(sum(e * e for e in errors) / len(errors))


# --- synthetic houses (tests, demo) ---


def simulate_house(params, inputs, heat_to_mass, x0, setpoints, seed=1, k=SURFACE_K):
    """measured rows of a simulated room. inputs: list of dicts (ta, sun,
    present, window), setpoints: air setpoint per step (None = heating off).
    Returns rows with y (rounded like a sensor), h (valve 0..1) and the
    true states."""
    rng = random.Random(seed)
    model = Discrete(params, heat_to_mass)
    x = x0
    rows = []
    for row, target in zip(inputs, setpoints):
        qa, qm = model.gains(row["sun"], row.get("present"))
        if target is None:
            power = 0.0
            x = model.step(x, row["ta"], qa, qm, row.get("window"))
        else:
            power, x = model.power_for(
                x, row["ta"], qa, qm, row.get("window"), target, params["p_heat"]
            )
        x = (x[0] + rng.gauss(0, 0.02), x[1])
        rows.append(
            dict(
                row,
                y=round(x[0] + rng.gauss(0, 0.05), 1),
                h=power / params["p_heat"],
                true=x,
                surface=surface_temp(x[0], x[1], k),
            )
        )
    return rows
