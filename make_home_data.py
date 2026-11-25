"""Turn the home-collected drives in "collected data/" into processed datasets the EKF and qrlib can run on.

    python make_home_data.py              # every drive in collected data/
    python make_home_data.py --seed 0 1   # degraded-section variants for more seeds

A drive is the set of files <stamp>_imu.csv, <stamp>_raw.txt and <stamp>_truth.csv written by the ESP32 logger
(MPU-6500 at 100 Hz, a multi-GNSS NMEA module at 0.5 Hz) plus a 1 Hz reference track with UTC timestamps.
It writes, in the format of the D:\\EKF data pipeline (time rebased to the first IMU sample, IMU in SI units in the
sensor frame as logged, GPS and truth in ENU around the first kept fix):

    processed_data/home/<stamp>/                imu.csv, gps.csv, gt.csv, meta.json (raw GPS)
    processed_data/home/<stamp>_outages_s<seed>/ gps.csv, meta.json: raw GPS with a ~5 m section, a ~15 m section
                                                and an outage at 25/50/75 % of the path, like the other drives

Choices (also written to meta.json):
- GPS comes from the NMEA in raw.txt (GGA position and altitude, RMC speed for the stop detection); the logger's
  gps.csv has speed and course one fix late. Position only: ve/vn/vu are NaN (as for iNav-WHU), so the noise
  added to a degraded section cannot be bypassed through clean velocity.
- Time: the ESP32 clock drifts against UTC (~170 ppm), so UTC is mapped onto the device clock with a straight
  line fitted to the GGA arrival times, shifted to their earliest arrival (the remaining latency is < 0.25 s).
  The truth's UTC times go through the same line.
- Start: the filter needs a static start (attitude from the first second, IMU noise from the first 10 s), and the
  car was already moving when the logger started, so the drive starts at its first stop (>= MIN_STOP_FIXES fixes
  with RMC speed below STOP_SPEED).
- Truth altitude uses another datum than the module's (about 50 m apart), so it is shifted by the median
  difference to the GPS altitude. Horizontal metrics are unaffected.
- Sections: the other drives degrade 76.2 m of travel, which takes ~60 s there. At car speed 76.2 m is ~5 s
  (2-3 fixes at 0.5 Hz), too short for the condition detector, so here each section lasts SECTION_S seconds,
  centred where the path reaches 25/50/75 % of its length.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "collected data"
OUT = ROOT / "processed_data" / "home"

STOP_SPEED = 0.2          # m/s: a fix this slow counts as stopped
MIN_STOP_FIXES = 3        # consecutive stopped fixes for the static start
MAX_SPEED_MS = 30.0       # plausibility rule's top speed (the drive's RMC speed peaks at 23.7 m/s; default 6 m/s
                          # is for the walking-speed drives and rejected 245 of 341 fixes here)
SECTION_S = 60.0         # duration of each degraded section (the iNav-WHU drives' sections last 52-65 s)
SECTIONS = ({"kind": "noise", "sigma_h_m": 5.0, "at": 0.25},
            {"kind": "noise", "sigma_h_m": 15.0, "at": 0.50},
            {"kind": "outage", "at": 0.75})

_A, _E2 = 6378137.0, 0.00669437999014         # WGS84


def latlon_to_enu(lat, lon, alt, lat0, lon0, alt0):
    """Tangent-plane ENU around (lat0, lon0, alt0), m (same as D:\\EKF data_pipeline.geo)."""
    k = np.pi / 180.0
    s = np.sin(lat0 * k) ** 2
    meridional = _A * (1 - _E2) / (1 - _E2 * s) ** 1.5
    prime_vertical = _A / np.sqrt(1 - _E2 * s)
    return ((np.asarray(lon, float) - lon0) * k * prime_vertical * np.cos(lat0 * k),
            (np.asarray(lat, float) - lat0) * k * meridional, np.asarray(alt, float) - alt0)


def _sod(hhmmss):
    """UTC seconds of day from an NMEA hhmmss.sss field."""
    return int(hhmmss[:2]) * 3600 + int(hhmmss[2:4]) * 60 + float(hhmmss[4:])


def _deg(value, hemi, width):
    v = float(value[:width]) + float(value[width:]) / 60.0
    return -v if hemi in "SW" else v


def read_nmea(path):
    """GGA fixes joined with the RMC of the same epoch: t_dev (arrival, s), utc, lat, lon, alt, sats, hdop, speed."""
    gga, rmc = {}, {}
    for line in open(path, encoding="utf-8", errors="replace"):
        if not line.startswith("G,"):
            continue
        _, t_us, sentence = line.rstrip("\n").split(",", 2)
        f = sentence.split("*")[0].split(",")
        try:
            if f[0].endswith("GGA") and f[6] not in ("", "0") and f[2]:
                gga[f[1]] = {"t_dev": int(t_us) / 1e6, "utc": _sod(f[1]), "lat": _deg(f[2], f[3], 2),
                             "lon": _deg(f[4], f[5], 3), "alt": float(f[9]), "fix": int(f[6]),
                             "sats": int(f[7]), "hdop": float(f[8])}
            elif f[0].endswith("RMC") and f[2] == "A":
                rmc[f[1]] = {"speed_mps": float(f[7]) * 0.514444, "course_deg": float(f[8]) if f[8] else np.nan}
        except (ValueError, IndexError):
            continue                                   # a sentence cut by the logger
    rows = [{**g, **rmc.get(k, {"speed_mps": np.nan, "course_deg": np.nan})} for k, g in gga.items()]
    return pd.DataFrame(rows).sort_values("utc").reset_index(drop=True)


def clock_map(gps):
    """(a, b, info): device time = a * utc + b, a line through the GGA arrival times shifted to their earliest."""
    a, b = np.polyfit(gps["utc"], gps["t_dev"], 1)
    resid = gps["t_dev"] - (a * gps["utc"] + b)
    b += resid.min()
    lat = resid - resid.min()
    return a, b, {"drift_ppm": float((a - 1) * 1e6), "arrival_latency_spread_s": [float(lat.median()), float(lat.max())]}


def static_start(gps):
    """Device time of the first fix of the first run of MIN_STOP_FIXES stopped fixes."""
    stopped = (gps["speed_mps"] < STOP_SPEED).to_numpy()
    for i in range(len(stopped) - MIN_STOP_FIXES + 1):
        if stopped[i:i + MIN_STOP_FIXES].all():
            return float(gps["t"].iloc[i]), int(i)
    raise ValueError("no stop in the drive: the EKF needs a static start")


def process(stamp):
    imu = pd.read_csv(RAW / f"{stamp}_imu.csv", skipinitialspace=True)
    imu.columns = [c.strip() for c in imu.columns]
    gps = read_nmea(RAW / f"{stamp}_raw.txt")
    truth = pd.read_csv(RAW / f"{stamp}_truth.csv")
    a, b, clock = clock_map(gps)
    gps["t"] = a * gps["utc"] + b
    ts = pd.to_datetime(truth["time"], utc=True)
    truth["t"] = a * (ts.dt.hour * 3600 + ts.dt.minute * 60 + ts.dt.second + ts.dt.microsecond / 1e6) + b

    t_imu = imu["t_us"].to_numpy() / 1e6
    t_start, i_start = static_start(gps)
    t_end = float(t_imu[-1])
    t0 = float(t_imu[t_imu <= t_start][-1])        # the last IMU sample at or before the first stopped fix
    keep = t_imu >= t0
    imu_out = pd.DataFrame({"t": t_imu[keep] - t0,
                            "ax": imu["ax_mps2"].to_numpy()[keep], "ay": imu["ay_mps2"].to_numpy()[keep],
                            "az": imu["az_mps2"].to_numpy()[keep],
                            **{f"w{c}": np.radians(imu[f"g{c}_dps"].to_numpy()[keep]) for c in "xyz"},
                            "temp_C": imu["temp_C"].to_numpy()[keep]})

    g = gps[(gps["t"] >= t0) & (gps["t"] <= t_end)].reset_index(drop=True)
    lat0, lon0, alt0 = g["lat"].iloc[0], g["lon"].iloc[0], g["alt"].iloc[0]
    e, n, u = latlon_to_enu(g["lat"], g["lon"], g["alt"], lat0, lon0, alt0)
    gps_out = pd.DataFrame({"t": g["t"] - t0, "e": e, "n": n, "u": u, "ve": np.nan, "vn": np.nan, "vu": np.nan,
                            "speed_mps": g["speed_mps"], "course_deg": g["course_deg"], "sats": g["sats"],
                            "hdop": g["hdop"]})

    tr = truth[(truth["t"] >= t0) & (truth["t"] <= t_end)].reset_index(drop=True)
    te, tn, tu = latlon_to_enu(tr["lat"], tr["long"], tr["altitude"], lat0, lon0, alt0)
    alt_shift = float(np.median(np.interp(gps_out["t"], tr["t"] - t0, tu) - gps_out["u"]))
    gt_out = pd.DataFrame({"t": tr["t"] - t0, "e": te, "n": tn, "u": tu - alt_shift,
                           "ve": np.nan, "vn": np.nan, "vu": np.nan})

    err = np.hypot(gps_out["e"] - np.interp(gps_out["t"], gt_out["t"], gt_out["e"]),
                   gps_out["n"] - np.interp(gps_out["t"], gt_out["t"], gt_out["n"]))
    lags = np.arange(-1.0, 1.01, 0.1)
    lag_rms = [float(np.sqrt(np.mean((gps_out["e"] - np.interp(gps_out["t"] + L, gt_out["t"], gt_out["e"])) ** 2
                                     + (gps_out["n"] - np.interp(gps_out["t"] + L, gt_out["t"], gt_out["n"])) ** 2)))
               for L in lags]
    path_m = float(np.sum(np.hypot(np.diff(gt_out["e"]), np.diff(gt_out["n"]))))
    dt = np.diff(imu_out["t"].to_numpy())
    start_f = float(np.linalg.norm(imu_out.loc[imu_out["t"] < 1.0, ["ax", "ay", "az"]].mean()))
    ds_id = f"home/{stamp}"
    meta = {
        "id": ds_id,
        "label": f"Home drive {stamp} (car; MPU-6500 IMU 100 Hz, NMEA GNSS 0.5 Hz, 1 Hz reference track)",
        "source_files": [f"{stamp}_imu.csv", f"{stamp}_raw.txt", f"{stamp}_truth.csv"],
        "time_base": "ESP32 device clock (t_us); UTC mapped onto it",
        "clock": {"device_per_utc": float(a), **clock},
        "imu_frame": "sensor frame as logged (mounted tilted: static specific force ~(-5.3, -0.8, -8.7) m/s^2)",
        "imu_note": "MPU-6500, accel +-4 g, gyro +-500 dps, DLPF 41 Hz; no magnetometer. Gyro bias ~(-5, 3, 0) "
                    "deg/s and |specific force| ~10.2 m/s^2 are left in the data (the EKF estimates the biases)",
        "gnss": "NMEA GGA (single point), 0.5 Hz, no velocity channel used (ve/vn/vu NaN); speed_mps/course_deg "
                "from RMC, sats and hdop kept for reference only",
        "truth_note": "1 Hz reference track with whole-second UTC stamps (a consumer GNSS log, not RTK): "
                      "metrics against it include its own error",
        "truth_alt_shift_m": alt_shift,
        "gps_origin_lat_lon_alt": [float(lat0), float(lon0), float(alt0)],
        "gps_origin_method": "first fix of the kept part",
        "start": {"rule": f"first run of {MIN_STOP_FIXES} fixes slower than {STOP_SPEED} m/s",
                  "t_dev_s": t0, "fix_index": i_start, "dropped_s": float(t0 - t_imu[0])},
        "t0_source_s": t0,
        "imu_samples": len(imu_out),
        "imu_dropped_invalid": 0,
        "imu_dropped_outside_kept_segment": int((~keep).sum()),
        "imu_duration_s": float(imu_out["t"].iloc[-1]),
        "imu_rate_hz": float(1.0 / np.median(dt)),
        "imu_max_gap_s": float(dt.max()),
        "units": {"time": "s", "accel": "m/s^2", "gyro": "rad/s", "position": "m (ENU)", "velocity": "m/s (ENU)"},
        "frames": "IMU in the sensor/body frame as logged; GPS and GT in ENU",
        "gps_samples": len(gps_out), "gps_dropped": int(len(gps) - len(gps_out)),
        "gps_start_s": float(gps_out["t"].iloc[0]), "gps_end_s": float(gps_out["t"].iloc[-1]),
        "gt_samples": len(gt_out), "gt_dropped": int(len(truth) - len(gt_out)),
        "gt_start_s": float(gt_out["t"].iloc[0]), "gt_end_s": float(gt_out["t"].iloc[-1]),
        "gt_path_m": path_m,
        "raw_gps_vs_truth_h_m": {"rmse": float(np.sqrt(np.mean(err ** 2))), "median": float(np.median(err)),
                                 "max": float(err.max())},
        "truth_lag_check": {"best_lag_s": float(lags[int(np.argmin(lag_rms))]), "rmse_at_best_m": min(lag_rms),
                            "rmse_at_0_m": lag_rms[10], "applied_lag_s": 0.0},
        "start_specific_force_ms2": start_f,
        "max_speed_ms": MAX_SPEED_MS,
        "ekf_ready": {"ready": bool(len(gps_out) >= 10 and len(gt_out) >= 10 and 8.0 <= start_f <= 11.5),
                      "reasons": [], "gps_channels": ["e", "n", "u"]},
    }
    out = OUT / stamp
    out.mkdir(parents=True, exist_ok=True)
    imu_out.to_csv(out / "imu.csv", index=False)
    gps_out.to_csv(out / "gps.csv", index=False)
    gt_out.to_csv(out / "gt.csv", index=False)
    (out / "meta.json").write_text(json.dumps(meta, indent=2))
    print(f"{ds_id}: {meta['imu_duration_s']:.0f} s, {len(gps_out)} fixes, {len(gt_out)} truth rows, path "
          f"{path_m:.0f} m, start dropped {meta['start']['dropped_s']:.1f} s, raw GPS vs truth "
          f"{meta['raw_gps_vs_truth_h_m']['rmse']:.2f} m RMS (best truth lag {meta['truth_lag_check']['best_lag_s']:+.1f} s)")
    return ds_id, gps_out, gt_out, meta


def make_sections(stamp, gps, gt, meta, seed=0):
    """Raw GPS with SECTIONS degraded, each SECTION_S long and centred at its share of the path."""
    t, p = gt["t"].to_numpy(), gt[["e", "n"]].to_numpy()
    s = np.r_[0.0, np.cumsum(np.hypot(*np.diff(p, axis=0).T))]
    gps = gps.copy()
    rng = np.random.default_rng(seed)
    keep = np.ones(len(gps), bool)

    def h_rmse(df):
        if not len(df):
            return float("nan")
        return float(np.sqrt(np.mean((df["e"] - np.interp(df["t"], t, gt["e"])) ** 2
                                     + (df["n"] - np.interp(df["t"], t, gt["n"])) ** 2)))

    out_sections = []
    for sec in SECTIONS:
        tc = float(np.interp(sec["at"] * s[-1], s, t))
        t0, t1 = tc - SECTION_S / 2, tc + SECTION_S / 2
        inside = ((gps["t"] >= t0) & (gps["t"] <= t1)).to_numpy()
        raw = h_rmse(gps[inside])
        if sec["kind"] == "noise":
            axis = sec["sigma_h_m"] / np.sqrt(2)
            gps.loc[inside, ["e", "n", "u"]] += rng.normal(0.0, 1.0, (inside.sum(), 3)) * [axis, axis, 1.5 * axis]
            degraded = h_rmse(gps[inside])
        else:
            keep &= ~inside
            degraded = float("nan")
        s0, s1 = np.interp([t0, t1], t, s)
        out_sections.append({**sec, "t_start_s": t0, "t_end_s": t1, "duration_s": SECTION_S, "start_m": float(s0),
                             "length_m": float(s1 - s0), "n_fixes": int(inside.sum()), "raw_gps_rmse_h_m": raw,
                             "degraded_gps_rmse_h_m": degraded})
    gps = gps[keep]
    new_id = f"home/{stamp}_outages_s{seed}"
    out = ROOT / "processed_data" / new_id
    out.mkdir(parents=True, exist_ok=True)
    gps.to_csv(out / "gps.csv", index=False)
    m = {**meta, "id": new_id,
         "label": f"{meta['label']}, raw GPS with {len(SECTIONS)} degraded sections of {SECTION_S:g} s",
         "derived_from": meta["id"], "gps_samples": int(len(gps)),
         "gps_sections": {"seed": seed, "duration_s": SECTION_S,
                          "note": "sections by duration, not 76.2 m of travel (see make_home_data.py)",
                          "sections": out_sections, "raw_gps_rmse_h_clean_m": meta["raw_gps_vs_truth_h_m"]["rmse"],
                          "raw_gps_rmse_h_m": h_rmse(gps)}}
    (out / "meta.json").write_text(json.dumps(m, indent=2))
    print(f"{new_id}: " + "; ".join(
        f"{x['kind']}{' %g m' % x['sigma_h_m'] if x['kind'] == 'noise' else ''} t {x['t_start_s']:.0f}-"
        f"{x['t_end_s']:.0f} s ({x['n_fixes']} fixes, {x['length_m']:.0f} m, GPS {x['raw_gps_rmse_h_m']:.2f} -> "
        f"{x['degraded_gps_rmse_h_m']:.2f} m)" for x in out_sections))
    return new_id


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seed", type=int, nargs="+", default=[0], help="seeds of the degraded-section variants")
    args = ap.parse_args()
    stamps = sorted(p.name[:-len("_imu.csv")] for p in RAW.glob("*_imu.csv"))
    if not stamps:
        raise SystemExit(f"no <stamp>_imu.csv in {RAW}")
    for stamp in stamps:
        _, gps, gt, meta = process(stamp)
        for seed in args.seed:
            make_sections(stamp, gps, gt, meta, seed)


if __name__ == "__main__":
    main()
