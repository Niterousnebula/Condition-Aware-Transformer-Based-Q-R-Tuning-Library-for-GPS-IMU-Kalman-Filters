"""Datasets, the train/test split and the GPS condition detector (GPS fixes only, causal)."""
import json

import numpy as np

import ekf

from . import config as C


def load(dataset):
    """data dict (ekf.load_data) plus its degraded sections [{kind, sigma_h_m, t_start_s, t_end_s}, ...]."""
    data = ekf.load_data(dataset)
    meta = json.loads((ekf.data.PROCESSED_DIR / dataset / "meta.json").read_text())
    sections = [dict(s) for s in meta["gps_sections"]["sections"]]
    return data, sections


_ARRAYS = {"imu": ("t_imu", "accel", "gyro"), "gps": ("t_gps", "p_gps", "v_gps"),
           "gt": ("t_true", "p_true", "motion")}


def segment(data, t0, t1, name):
    """Copy of data restricted to t0 <= t < t1 (IMU, GPS and ground truth alike)."""
    keys = {k for ks in _ARRAYS.values() for k in ks}
    out = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in data.items() if k not in keys}
    for group, ks in _ARRAYS.items():
        t = data[ks[0]]
        keep = (t >= t0) & (t < t1)
        for k in ks:
            out[k] = data[k][keep].copy()
    out["segment"] = name
    out["t_range"] = (float(t0), float(t1))
    return out


def split(data, sections):
    """(train, test, t_split): train holds normal GPS and the 5 m section, test the rest."""
    a, b = sections[C.SPLIT_AFTER_SECTION], sections[C.SPLIT_AFTER_SECTION + 1]
    t_split = 0.5 * (a["t_end_s"] + b["t_start_s"])
    t = data["t_imu"]
    return (segment(data, t[0], t_split, "train"), segment(data, t_split, t[-1] + 1.0, "test"),
            float(t_split))


def nominal_dt(data):
    return float(np.median(np.diff(data["t_gps"])))


def _residuals(t, z):
    """Each fix's distance from the line through its two neighbours, scaled to unit noise (per axis)."""
    t0, t1, t2 = t[:-2], t[1:-1], t[2:]
    span = t2 - t0
    a = (t2 - t1) / span                # weight of the previous fix
    b = (t1 - t0) / span                # weight of the next fix
    r = (z[1:-1] - (a[:, None] * z[:-2] + b[:, None] * z[2:])) / np.sqrt(1 + a * a + b * b)[:, None]
    return r, t2, span                  # a residual is known once its next fix has arrived (t2)


RAYLEIGH_MEDIAN = float(np.sqrt(np.log(4.0) / 2.0))     # median of |2-D white noise| / sigma_h (0.83)


def _jumps(t, z):
    """Each fix's distance from the straight line through the two fixes before it, scaled so that its mean
    square is sigma_h^2 for white GPS noise. Known as soon as the fix arrives (causal)."""
    t0, t1, t2 = t[:-2], t[1:-1], t[2:]
    c = (t2 - t1) / np.maximum(t1 - t0, 1e-9)
    e = z[2:] - ((1 + c)[:, None] * z[1:-1] - c[:, None] * z[:-2])
    return np.linalg.norm(e, axis=1) / np.sqrt(1 + (1 + c) ** 2 + c ** 2), t2, t2 - t0


def fix_jumps(data):
    """Every fix's jump in sigma_h units (_jumps / RAYLEIGH_MEDIAN: half the jumps of white noise sigma_h exceed
    sigma_h), 0 where it is undefined (the first two fixes, and after a gap of more than 3 nominal intervals)."""
    t, z = data["t_gps"], data["p_gps"][:, 0:2]
    jmp, _, span = _jumps(t, z)
    out = np.zeros(len(t))
    out[2:] = np.where(span <= 3.0 * nominal_dt(data), jmp / RAYLEIGH_MEDIAN, 0.0)
    return out


def jump_limit(label):
    """Largest plausible jump (sigma_h units) under a gated noise condition (C.JUMP_GATE_LABELS): its bin's
    upper edge; inf (no jump gate) otherwise."""
    return dict(C.NOISE_BINS)[label] if label in C.JUMP_GATE_LABELS else float("inf")


def noise_label(sigma_h):
    for name, edge in C.NOISE_BINS:
        if sigma_h < edge:
            return name
    return C.NOISE_BINS[-1][0]


def _hysteresis(sigma_h, current):
    """noise_label, but the current bin is kept while sigma_h is within C.HYSTERESIS of its edges."""
    new = noise_label(sigma_h)
    if new != current and current in C.SEVERITY:
        i = C.SEVERITY.index(current)
        lo, hi = (C.NOISE_BINS[i - 1][1] if i else 0.0), C.NOISE_BINS[i][1]
        if lo / C.HYSTERESIS <= sigma_h <= hi * C.HYSTERESIS:
            return current
    return new


def detect(data, t_dec):
    """GPS condition at each decision time, from the fixes received up to then.

    Returns labels (list of str) and stats (dict of arrays: sigma_h, fix_rate, gap). Labels: outage (no fix
    for max(OUTAGE_GAP_S, 5 nominal intervals)), recovery (the first RECOVERY_S after an outage), else the
    noise bin of sigma_h, a robust (MAD) estimate of the fixes' white noise from each fix's distance to the
    line through its neighbours. With too few fixes in the window the last noise label is kept.
    Plausibility trigger (fast, for the onset of noise): when at least JUMP_Y of the last JUMP_N fixes jump off
    the straight line through the two fixes before them by more than a noisier bin's edge, the label is that
    bin at once (stats sigma_fast). It only ever makes the label noisier, and only acts while the window says
    a gated condition (C.JUMP_GATE_LABELS: it is there to leave those fast; heavy vs extreme is the window's
    call). Going back waits for the window.
    """
    t, z = data["t_gps"], data["p_gps"][:, 0:2]
    dt_nom = nominal_dt(data)
    gap_max = max(C.OUTAGE_GAP_S, C.OUTAGE_GAP_INTERVALS * dt_nom)
    r, t_known, span = _residuals(t, z)
    ok = span <= 3.0 * dt_nom                           # no residual across a gap
    r, t_known = r[ok], t_known[ok]
    jmp, t_jmp, span_j = _jumps(t, z)
    okj = span_j <= 3.0 * dt_nom
    jmp, t_jmp = jmp[okj] / RAYLEIGH_MEDIAN, t_jmp[okj]     # in sigma_h units: half the jumps exceed sigma_h
    labels, sig, fast_sig, rate, gaps = [], [], [], [], []
    noise, last_outage_end, in_outage = "nominal", -np.inf, False
    t_begin = t_dec[0]                                   # the first decision counts as a fix (no false outage)
    for td in t_dec:
        j = np.searchsorted(t, td, side="right")         # fixes up to td
        gap = td - max(t[j - 1] if j > 0 else -np.inf, t_begin)
        lo, hi = np.searchsorted(t_known, td - C.COND_WINDOW_S, side="right"), np.searchsorted(t_known, td, side="right")
        n_win = np.searchsorted(t, td, side="right") - np.searchsorted(t, td - C.COND_WINDOW_S, side="right")
        s_h = np.nan
        if hi - lo >= C.COND_MIN_FIXES:
            w = r[lo:hi]
            mad = 1.4826 * np.median(np.abs(w - np.median(w, axis=0)), axis=0)
            s_h = float(np.sqrt((mad ** 2).sum()))
            noise = _hysteresis(s_h, noise)
        now = noise
        hj = np.searchsorted(t_jmp, td, side="right")
        s_f = np.nan
        if (C.JUMP_N and noise in C.JUMP_GATE_LABELS and hj >= C.JUMP_N
                and t_jmp[hj - C.JUMP_N] >= td - 3.0 * C.JUMP_N * dt_nom):
            s_f = float(np.sort(jmp[hj - C.JUMP_N:hj])[-C.JUMP_Y])   # JUMP_Y of the last JUMP_N exceed it
            fast = C.SEVERITY[min(C.SEVERITY.index(noise_label(s_f)), len(C.JUMP_GATE_LABELS))]  # at most heavy
            if C.SEVERITY.index(fast) > C.SEVERITY.index(now):
                now = fast
        if gap > gap_max:
            lab, in_outage = "outage", True
        else:
            if in_outage:
                last_outage_end, in_outage = td, False
            lab = "recovery" if td - last_outage_end < C.RECOVERY_S else now
        labels.append(lab)
        sig.append(s_h)
        fast_sig.append(s_f)
        rate.append(n_win / C.COND_WINDOW_S)
        gaps.append(gap)
    return labels, {"sigma_h": np.array(sig), "sigma_fast": np.array(fast_sig), "fix_rate": np.array(rate),
                    "gap": np.array(gaps)}


def oracle(sections, t_dec):
    """The true condition at each decision time, from the section table (upper bound for the detector)."""
    labels = []
    for td in t_dec:
        lab = "nominal"
        for s in sections:
            if s["t_start_s"] <= td < s["t_end_s"]:
                lab = "outage" if s["kind"] == "outage" else noise_label(s["sigma_h_m"])
            elif s["kind"] == "outage" and s["t_end_s"] <= td < s["t_end_s"] + C.RECOVERY_S:
                lab = "recovery"
        labels.append(lab)
    return labels


def decision_times(seg):
    t = seg["t_imu"]
    return np.arange(t[0], t[-1], C.DECIDE_S)
