"""python -m qrlib.report [--root results/qrlib] : the paper's tables and figures from finished runs.

Reads every finished seed under --root (results/qrlib/seed_<s>/<dataset>/) and, when they exist, the ablation
roots next to it (_offline, _onestep, _wideq), and writes <root>/paper/:
  tables/  main, ablation, init, llm_cost, detector  (.md and .tex; mean +- std over seeds)
  figures/ fig1_pipeline ... fig8_headline           (.png and .pdf)
  captions.md
Time plots use the first seed and the LLM builder (else the first builder found). Shaded GPS sections are
drawn C.PLOT_HIGHLIGHT_WIDEN (50 %) wider than the sections, centred, so short sections stay visible.
Colours: builders in the reference palette's first three slots (blue LLM, orange random, aqua GWO, which
pass the colour-vision checks for all pairs); references in neutral inks with their own dash patterns;
GPS sections in paper 1's section colours.
"""
import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

from . import config as C, data as D  # noqa: E402

INK = {"primary": "#0b0b0b", "secondary": "#52514e", "muted": "#8a8984", "grid": "#e8e7e3"}
SERIES = {"llm": "#2a78d6", "random": "#eb6834", "gwo": "#1baf7a", "de": "#e87ba4",
          "no_filter": "#e34948", "true": "#008300", "static": "#eda100"}
REF = {"theta0": dict(color=INK["secondary"], ls=(0, (4, 2))), "paper1": dict(color=INK["primary"], ls=(0, (1, 1.4)))}
SECTION = {"5 m": "#e6ab02", "15 m": "#e7298a", "outage": "#7570b3"}         # paper 1's section colours
SECTION_LABEL = {"5 m": "5 m GPS noise", "15 m": "15 m GPS noise", "outage": "GPS outage"}
BUILDER = {"llm": "LLM", "random": "Random search", "gwo": "GWO", "de": "DE"}
DS = {"eth_outages_s0": "ETH", "inavwhu/playground00_outages_s0": "iNav-WHU playground",
      "inavwhu/street00_outages_s0": "iNav-WHU street"}
METRICS = [("rmse_heavy_15m", "15 m section"), ("rmse_outside", "Normal GPS"), ("rmse_recovery_30s", "30 s after outage"),
           ("rmse_outage", "Outage"), ("nis_over_dof", "NIS / dof")]
P1 = "Paper 1 GWO (ground truth, offline)"


def slug(ds):
    return ds.replace("/", "__")


def style():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8,
        "legend.fontsize": 7, "xtick.labelsize": 7, "ytick.labelsize": 7, "axes.edgecolor": INK["muted"],
        "axes.labelcolor": INK["secondary"], "xtick.color": INK["secondary"], "ytick.color": INK["secondary"],
        "axes.titlecolor": INK["primary"], "text.color": INK["primary"], "axes.grid": True,
        "grid.color": INK["grid"], "grid.linewidth": 0.5, "axes.spines.top": False, "axes.spines.right": False,
        "axes.axisbelow": True, "lines.linewidth": 1.1, "figure.facecolor": "white", "axes.facecolor": "white",
        "savefig.dpi": 300, "legend.frameon": False, "figure.constrained_layout.use": True})


def save(fig, out, name):
    for ax in fig.axes:                                # log axes: label the decades only
        for axis, sc in ((ax.xaxis, ax.get_xscale()), (ax.yaxis, ax.get_yscale())):
            if sc == "log":
                axis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    for ext in ("png", "pdf"):
        fig.savefig(out / f"{name}.{ext}")
    plt.close(fig)


def top_legend(fig, axes, ncol=4):
    """One legend for the figure, above the panels (collected from every axis, first label wins)."""
    seen = {}
    for ax in np.ravel(axes):
        for h, lab in zip(*ax.get_legend_handles_labels()):
            seen.setdefault(lab, h)
    fig.legend(seen.values(), seen.keys(), loc="outside upper center", ncol=ncol)


def highlight(ax, sections, kinds=("5 m", "15 m", "outage"), t0=0.0, labels=None):
    """Shade the GPS sections, C.PLOT_HIGHLIGHT_WIDEN wider than they are (centred)."""
    for s in sections:
        k = "outage" if s["kind"] == "outage" else f"{s['sigma_h_m']:.0f} m"
        if k not in kinds:
            continue
        a, b = s["t_start_s"] - t0, s["t_end_s"] - t0
        pad = 0.5 * C.PLOT_HIGHLIGHT_WIDEN * (b - a)
        lab = SECTION_LABEL[k] if labels is None or k not in labels else None
        if labels is not None:
            labels.add(k)
        ax.axvspan(a - pad, b + pad, color=SECTION[k], alpha=0.16, lw=0, zorder=0, label=lab)


def truth_err(data, t, pos):
    tt, pt = data["t_true"], data["p_true"]
    m = (t >= tt[0]) & (t <= tt[-1])
    p = np.column_stack([np.interp(t, tt, pt[:, i]) for i in range(2)])
    e = np.hypot(*(pos[:, :2] - p).T)
    return np.where(m, e, np.nan)


def mean_std(v):
    v = np.asarray(v, dtype=float)
    v = v[np.isfinite(v)]
    if not len(v):
        return "–"
    sd = v.std(ddof=1) if len(v) > 1 else 0.0
    return f"{v.mean():.2f}" if sd < 0.005 else f"{v.mean():.2f} ± {sd:.2f}"     # deterministic: no +- 0.00


# ------------------------------------------------------------------ loading
def load(root):
    rows, init = [], []
    for f in sorted(root.glob("seed_*/*/metrics.csv")):
        seed = int(f.parent.parent.name.split("_")[1])
        rows.append(pd.read_csv(f).assign(seed=seed, run=str(f.parent)))
        g = f.parent / "init.csv"
        if g.exists():
            init.append(pd.read_csv(g).assign(seed=seed))
    met = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
    ini = pd.concat(init, ignore_index=True) if init else pd.DataFrame()
    return met, ini


def builders_in(met):
    found = {m.split("(")[-1].rstrip(")") for m in met.method if m.startswith("Library (")}
    return [b for b in ("llm", "random", "gwo", "de") if b in found]


def ablation_roots(root):
    smoke = root.name.endswith("_smoke")
    base = root.name[:-len("_smoke")] if smoke else root.name
    return {k: root.parent / (base + suffix + ("_smoke" if smoke else ""))
            for k, suffix in (("offline", "_offline"), ("onestep", "_onestep"), ("wideq", "_wideq"))}


# ------------------------------------------------------------------ tables
def write_table(df, out, name, title):
    md = f"## {title}\n\n" + df.to_markdown(index=False) + "\n"
    (out / f"{name}.md").write_text(md, encoding="utf-8")
    cols = "l" * 2 + "r" * (df.shape[1] - 2)
    tex = df.to_latex(index=False, column_format=cols, escape=True).replace("±", r"$\pm$")
    (out / f"{name}.tex").write_text(tex.replace("\\toprule", "\\toprule").replace("–", "--"), encoding="utf-8")
    return md


def table_main(met, builders):
    order = ["Raw GPS", "Baseline THETA0", P1] + [m for b in builders for m in
                                                    (f"Static ({b})", f"Library + online update ({b})")]
    out = []
    for ds in met.dataset.unique():
        d = met[met.dataset == ds]
        for m in order:
            r = d[d.method == m]
            if r.empty:
                continue
            out.append({"Drive": DS.get(ds, ds), "Method": m.replace("Library + online update", "Library"),
                        **{lab: mean_std(r[c]) if c in r else "–" for c, lab in METRICS}})
    return pd.DataFrame(out)


def table_ablation(met, roots, b):
    out = []
    variants = [("Full: library + online update", None, f"Library + online update ({b})"),
                ("Without online update", None, f"Library ({b})"),
                ("Without plausibility filter", None, f"Library, no plausibility filter ({b})"),
                ("True condition instead of detector (upper bound)", None, f"Library, true condition ({b})"),
                ("Offline build instead of initialization mode", "offline", f"Library + online update ({b})"),
                ("One-step score (no simulated dropouts)", "onestep", f"Library + online update ({b})"),
                ("Q over THETA0 +- 3 decades", "wideq", f"Library + online update ({b})")]
    other = {k: load(r)[0] for k, r in roots.items() if r.exists()}
    for ds in met.dataset.unique():
        for name, src, m in variants:
            d = met if src is None else other.get(src)
            if d is None or d.empty:
                continue
            r = d[(d.dataset == ds) & (d.method == m)]
            if r.empty:
                continue
            out.append({"Drive": DS.get(ds, ds), "Variant": name,
                        **{lab: mean_std(r[c]) for c, lab in METRICS[:4]}, "Seeds": r.seed.nunique()})
    return pd.DataFrame(out)


def table_init(ini, builders):
    if ini.empty:
        return pd.DataFrame()
    cols = [("train_rmse_all", "Whole period"), ("train_rmse_moderate_5m", "5 m section"),
            ("train_rmse_moderate_5m_first10s", "First 10 s of it"), ("train_rmse_outside", "Normal GPS")]
    out = []
    for ds in ini.dataset.unique():
        for m in ["THETA0"] + [f"Initialization mode ({b})" for b in builders]:
            r = ini[(ini.dataset == ds) & (ini.method == m)]
            if not r.empty:
                out.append({"Drive": DS.get(ds, ds), "Method": m, **{lab: mean_std(r[c]) for c, lab in cols}})
    return pd.DataFrame(out)


def llm_rounds(entry):
    return entry.get("llm_log") or []


def table_llm(root):
    out = []
    for run in sorted(root.glob("seed_*/*")):
        f, g = run / "library_llm.json", run / "online_llm.json"
        if not f.exists():
            continue
        lib = json.loads(f.read_text())
        logs = [e for v in lib["library"].values() for e in llm_rounds(v)] + llm_rounds(lib["static"])
        if g.exists():
            on = json.loads(g.read_text())
            logs += [e for v in on["library"].values() if "online_at_s" in v for e in llm_rounds(v)]
        if not logs:
            continue
        K = C.BUILD_K
        ds = pd.read_csv(run / "metrics.csv").dataset.iloc[0]
        out.append({"dataset": ds, "calls": len(logs), "tokens_in": np.mean([e["tokens_in"] for e in logs]),
                    "tokens_out": np.mean([e["tokens_out"] for e in logs]),
                    "parsed": sum(e["n_parsed"] for e in logs) / (K * len(logs)),
                    "seconds": np.mean([e.get("seconds", np.nan) for e in logs]),
                    "total_min": np.nansum([e.get("seconds", np.nan) for e in logs]) / 60})
    if not out:
        return pd.DataFrame()
    d = pd.DataFrame(out)
    return pd.DataFrame([{"Drive": DS.get(ds, ds), "LLM calls per run": mean_std(g.calls),
                          "Prompt tokens per call": mean_std(g.tokens_in), "Reply tokens per call": mean_std(g.tokens_out),
                          "Settings parsed": f"{100 * g.parsed.mean():.0f} %", "Seconds per call": mean_std(g.seconds),
                          "LLM minutes per run": mean_std(g.total_min)} for ds, g in d.groupby("dataset")])


def onset_delay(t_dec, det, true_label, t_start):
    i0 = np.searchsorted(t_dec, t_start)
    hit = np.flatnonzero(np.asarray(det[i0:]) == true_label)
    return float(t_dec[i0 + hit[0]] - t_start) if len(hit) else np.nan


def table_detector(root):
    out = []
    for run in sorted(root.glob("seed_0/*")):
        tr, it = run / "traces.npz", run / "init_traces.npz"
        if not tr.exists():
            continue
        ds = pd.read_csv(run / "metrics.csv").dataset.iloc[0]
        _, sections = D.load(ds)
        z = np.load(tr)
        agree = np.mean(z["labels_detected"] == z["labels_true"])
        row = {"Drive": DS.get(ds, ds), "Agreement, test part": f"{100 * agree:.1f} %"}
        if it.exists():
            zi = np.load(it)
            orc = np.array(D.oracle(sections, zi["t_dec"]))
            row["Agreement, initialization"] = f"{100 * np.mean(zi['labels_detected'] == orc):.1f} %"
            s5 = sections[0]
            row["Onset delay, 5 m (s)"] = f"{onset_delay(zi['t_dec'], zi['labels_detected'], D.noise_label(s5['sigma_h_m']), s5['t_start_s']):.0f}"
        s15 = sections[1]
        row["Onset delay, 15 m (s)"] = f"{onset_delay(z['t_dec'], z['labels_detected'], D.noise_label(s15['sigma_h_m']), s15['t_start_s']):.0f}"
        row["Without trigger, 15 m (s)"] = f"{onset_delay(z['t_dec'], z['labels_no_filter'], D.noise_label(s15['sigma_h_m']), s15['t_start_s']):.0f}"
        out.append(row)
    return pd.DataFrame(out)


# ------------------------------------------------------------------ figures
def fig_pipeline(out):
    fig, ax = plt.subplots(figsize=(7.0, 2.7))
    ax.set_axis_off()
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 4.2)

    def box(x, y, w, h, text, fc="white", ec=INK["muted"]):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=0.8))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=7, color=INK["primary"])

    def arrow(a, b, text=None, rad=0.0, dx=0.0, dy=0.12):
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=8, color=INK["secondary"], lw=0.8,
                                     connectionstyle=f"arc3,rad={rad}"))
        if text:
            ax.text((a[0] + b[0]) / 2 + dx, (a[1] + b[1]) / 2 + dy, text, ha="center", fontsize=6,
                    color=INK["secondary"])

    box(0.1, 2.5, 1.5, 0.9, "GPS fixes")
    box(2.1, 2.45, 2.4, 1.0, "Condition detector\nnoise level (15 s window)\n+ jump trigger (4 of 7)")
    box(5.0, 2.45, 2.0, 1.0, "Q/R library\none setting per\nGPS condition", fc="#eef4fc", ec=SERIES["llm"])
    box(7.6, 2.45, 2.2, 1.0, "16-state EKF\nQ/R in force\n+ jump gate")
    box(7.6, 0.35, 2.2, 0.9, "IMU\n(accel, gyro)")
    box(2.1, 0.2, 4.9, 1.2, "Builder: LLM (or random search, GWO) proposes Q/R settings,\n"
                            "scored on GPS only: prediction error against new fixes,\n"
                            "with simulated dropouts. From the drive start (initialization\n"
                            "mode) and when a new condition appears (online update).")
    arrow((1.6, 2.95), (2.1, 2.95))
    arrow((4.5, 2.95), (5.0, 2.95), "condition")
    arrow((7.0, 2.95), (7.6, 2.95), "Q, R")
    arrow((0.85, 3.4), (8.7, 3.45), "fixes", rad=-0.18, dy=0.55)
    arrow((8.7, 1.25), (8.7, 2.45))
    arrow((0.85, 2.5), (2.1, 0.8), "scoring", rad=0.25, dx=-0.35, dy=-0.15)
    arrow((6.0, 1.4), (6.0, 2.45), "new / re-tuned entry", dx=0.95, dy=0.0)
    arrow((9.8, 2.95), (10.9, 2.95))
    ax.text(10.9, 3.1, "position", ha="right", fontsize=7, color=INK["secondary"])
    save(fig, out, "fig1_pipeline")


def detector_series(run, ds):
    _, sections = D.load(ds)
    z, zi = np.load(run / "traces.npz"), np.load(run / "init_traces.npz")
    t = np.concatenate([zi["t_dec"], z["t_dec"]])
    sig = np.concatenate([zi["sigma_h"], z["sigma_h"]])
    det = np.concatenate([zi["labels_detected"], z["labels_detected"]])
    tru = np.array(D.oracle(sections, t))
    return t, sig, det, tru, sections


LEVELS = ["nominal", "recovery", "moderate", "heavy", "extreme", "outage"]


def fig_detector(root, out):
    runs = [r for r in sorted(root.glob("seed_0/*")) if (r / "init_traces.npz").exists()]
    if not runs:
        return
    fig, axes = plt.subplots(2 * len(runs), 1, figsize=(7.0, 2.3 * len(runs)), sharex=False,
                             gridspec_kw={"height_ratios": [1.4, 1] * len(runs)})
    for k, run in enumerate(runs):
        ds = pd.read_csv(run / "metrics.csv").dataset.iloc[0]
        t, sig, det, tru, sections = detector_series(run, ds)
        a1, a2 = axes[2 * k], axes[2 * k + 1]
        a2.sharex(a1)
        a1.tick_params(labelbottom=False)
        highlight(a1, sections)
        a1.plot(t, np.where(np.isfinite(sig), np.maximum(sig, 1e-2), np.nan), color=INK["primary"], lw=0.7,
                label="estimated GPS noise $\\sigma_h$")
        for name, edge in C.NOISE_BINS[:-1]:
            a1.axhline(edge, color=INK["muted"], lw=0.6, ls=(0, (2, 2)))
            a1.text(t[-1], edge, f" {name} < {edge:g} m", fontsize=6, color=INK["secondary"], va="bottom", ha="right")
        a1.set_yscale("log")
        a1.set_ylabel("$\\sigma_h$ (m)")
        a1.set_title(DS.get(ds, ds), loc="left")
        y = lambda labs: np.array([LEVELS.index(v) for v in labs])
        highlight(a2, sections, labels=set(SECTION))
        a2.step(t, y(tru), where="post", color=INK["secondary"], ls=(0, (3, 2)), lw=1.0, label="true condition")
        a2.step(t, y(det), where="post", color=SERIES["llm"], lw=1.0, label="detected condition (GPS only)")
        a2.set_yticks(range(len(LEVELS)), LEVELS)
        a2.set_xlabel("time (s)")
    top_legend(fig, axes, ncol=3)
    save(fig, out, "fig2_detector")


def time_runs(root, b):
    for run in sorted(root.glob("seed_0/*")):
        if (run / "traces.npz").exists():
            yield run, pd.read_csv(run / "metrics.csv").dataset.iloc[0]


def fig_onset(root, out, b):
    runs = list(time_runs(root, b))
    if not runs:
        return
    fig, axes = plt.subplots(1, len(runs), figsize=(7.0, 2.4), squeeze=False)
    for ax, (run, ds) in zip(axes[0], runs):
        data, sections = D.load(ds)
        z = np.load(run / "traces.npz")
        t0 = sections[1]["t_start_s"]
        rel = z["t"] - t0
        win = (rel >= -20) & (rel <= 60)
        highlight(ax, sections, kinds=("15 m",), t0=t0)
        ax.axvline(0, color=SECTION["15 m"], lw=1.2, label="15 m noise starts")
        for key, lab, kw in (("Baseline THETA0", "THETA0", REF["theta0"]),
                             (f"Library, no plausibility filter ({b})", "library, no plausibility filter",
                              dict(color=INK["primary"], ls=(0, (5, 1.5, 1, 1.5)), lw=0.9)),
                             (f"Library, true condition ({b})", "library, true condition",
                              dict(color=INK["muted"], ls=(0, (1, 1.2)), lw=1.3)),
                             (f"Library ({b})", f"library, detected condition ({BUILDER[b]})", dict(color=SERIES[b]))):
            if key in z:
                ax.plot(rel[win], truth_err(data, z["t"], z[key])[win], label=lab, **kw)
        ax.set_title(DS.get(ds, ds), loc="left")
        ax.set_xlabel("time since the 15 m section starts (s)")
        ax.set_xlim(-20, 60)
    axes[0][0].set_ylabel("horizontal error (m)")
    top_legend(fig, axes, ncol=3)
    save(fig, out, "fig3_onset")


def fig_test_error(root, out, b):
    runs = list(time_runs(root, b))
    if not runs:
        return
    fig, axes = plt.subplots(len(runs), 1, figsize=(7.0, 1.9 * len(runs)), squeeze=False)
    for ax, (run, ds) in zip(axes[:, 0], runs):
        data, sections = D.load(ds)
        z = np.load(run / "traces.npz")
        highlight(ax, sections, kinds=("15 m", "outage"))
        for key, lab, kw in (("Baseline THETA0", "THETA0", REF["theta0"]), (P1, "paper 1 GWO (truth-tuned)", REF["paper1"]),
                             (f"Library + online update ({b})", f"library + online update ({BUILDER[b]})",
                              dict(color=SERIES[b]))):
            if key in z:
                ax.plot(z["t"], np.maximum(truth_err(data, z["t"], z[key]), 1e-2), label=lab, lw=0.8, **kw)
        ax.set_yscale("log")
        ax.set_ylabel("error (m)")
        ax.set_title(DS.get(ds, ds), loc="left")
    axes[-1, 0].set_xlabel("time (s)")
    top_legend(fig, axes, ncol=5)
    save(fig, out, "fig4_test_error")


def fig_score(out):
    pts, coast = C.OUT / "score_points.csv", C.OUT / "coast_points.csv"
    if not pts.exists() or not coast.exists():
        return
    p, q = pd.read_csv(pts), pd.read_csv(coast)
    p = p[p.score_type == "with dropouts"]
    dss = [d for d in C.DATASETS if d in set(p.dataset)]
    fig, axes = plt.subplots(2, len(dss), figsize=(7.0, 4.6), squeeze=False)
    from scipy.stats import spearmanr
    note = dict(transform=None, fontsize=6.5, color=INK["secondary"], ha="right", va="bottom")
    for j, ds in enumerate(dss):
        ax = axes[0, j]
        txt = []
        for sec, col, lab in (("5 m noise", SECTION["5 m"], "5 m GPS noise section"),
                              ("15 m noise", SECTION["15 m"], "15 m GPS noise section")):
            r = p[(p.dataset == ds) & (p.section == sec)]
            if r.empty:
                continue
            txt.append(f"{sec.split()[0]} m: $\\rho$ = {spearmanr(r.score, r.truth_rmse)[0]:.2f}")
            ax.scatter(r.score, r.truth_rmse, s=14, color=col, edgecolors="white", linewidths=0.5, label=lab)
        ax.text(0.97, 0.04, "\n".join(txt), **{**note, "transform": ax.transAxes})
        ax.set_xscale("log")
        ax.set_title(DS.get(ds, ds), loc="left")
        ax.set_xlabel("GPS-only score (m)")
        ax2 = axes[1, j]
        r = q[q.dataset == ds]
        r = r[np.isfinite(r.truth_drift) & np.isfinite(r.score_dropout)]
        rho_d = spearmanr(r.score_dropout, r.truth_drift)[0]
        rho_o = spearmanr(r.score_onestep, r.truth_drift)[0]
        ax2.scatter(r.score_dropout, r.truth_drift, s=12, color=SERIES["llm"], edgecolors="white", linewidths=0.5,
                    label="random Q/R setting (normal-GPS windows)")
        t0 = r[r.is_theta0]
        ax2.scatter(t0.score_dropout, t0.truth_drift, s=60, marker="*", color=INK["primary"], label="THETA0", zorder=3)
        ax2.text(0.97, 0.04, f"$\\rho$ = {rho_d:.2f}\n(one-step score: {rho_o:.2f})",
                 **{**note, "transform": ax2.transAxes})
        ax2.set_xscale("log")
        ax2.set_yscale("log")
        ax2.set_xlabel("score with dropouts (m)")
    axes[0, 0].set_ylabel("true error in section (m)")
    axes[1, 0].set_ylabel("true drift, 30 s no GPS (m)")
    top_legend(fig, axes, ncol=4)
    save(fig, out, "fig5_score_check")


def fig_library(root, out, builders):
    rows = []
    for f in sorted(root.glob("seed_*/*/online_*.json")):
        b = f.stem.split("_", 1)[1]
        ds = pd.read_csv(f.parent / "metrics.csv").dataset.iloc[0]
        th0 = np.asarray(json.loads((f.parent / f"library_{b}.json").read_text())["library"]["nominal"]["history"][0]["theta"])
        for lab, e in json.loads(f.read_text())["library"].items():
            th = np.asarray(e["theta"])
            rows.append({"dataset": ds, "builder": b, "condition": lab, "dr_xy": th[4] - th0[4], "dr_vel": th[6] - th0[6]})
    if not rows:
        return
    d = pd.DataFrame(rows)
    conds = [c for c in ("nominal", "moderate", "heavy", "recovery") if c in set(d.condition)]
    dss = [x for x in C.DATASETS if x in set(d.dataset)]
    fig, axes = plt.subplots(1, len(dss), figsize=(7.0, 2.3), squeeze=False, sharey=True)
    for ax, ds in zip(axes[0], dss):
        ax.axhline(0, color=INK["secondary"], ls=(0, (4, 2)), lw=0.8, label="THETA0")
        for k, b in enumerate([x for x in builders if x in set(d.builder)]):
            r = d[(d.dataset == ds) & (d.builder == b)]
            x = np.array([conds.index(c) for c in r.condition]) + (k - 1) * 0.18
            ax.scatter(x, r.dr_xy, s=16, color=SERIES[b], edgecolors="white", linewidths=0.5, label=BUILDER[b])
        ax.set_xticks(range(len(conds)), conds)
        ax.set_title(DS.get(ds, ds), loc="left")
    axes[0][0].set_ylabel("log$_{10}$ R$_{xy}$ above THETA0 (decades)")
    top_legend(fig, axes, ncol=4)
    save(fig, out, "fig6_library")


def fig_init(root, out, builders):
    runs = [r for r in sorted(root.glob("seed_0/*")) if (r / "init_traces.npz").exists()]
    if not runs:
        return
    fig, axes = plt.subplots(len(runs), 1, figsize=(7.0, 1.9 * len(runs)), squeeze=False)
    for ax, run in zip(axes[:, 0], runs):
        ds = pd.read_csv(run / "metrics.csv").dataset.iloc[0]
        data, sections = D.load(ds)
        z = np.load(run / "init_traces.npz")
        highlight(ax, sections, kinds=("5 m",))
        ax.plot(z["t"], np.maximum(truth_err(data, z["t"], z["THETA0"]), 1e-2), lw=0.8, label="THETA0", **REF["theta0"])
        for b in builders:
            if b in z:
                ax.plot(z["t"], np.maximum(truth_err(data, z["t"], z[b]), 1e-2), lw=0.8, color=SERIES[b],
                        label=f"initialization mode ({BUILDER[b]})")
                lib = json.loads((run / f"library_{b}.json").read_text())
                for ev in lib.get("init_events", []):
                    ax.plot([ev["t_s"]], [1.0], marker="|", ms=7, color=SERIES[b], transform=ax.get_xaxis_transform())
        ax.set_yscale("log")
        ax.set_ylabel("error (m)")
        ax.set_title(f"{DS.get(ds, ds)} (ticks: re-tunings)", loc="left")
    axes[-1, 0].set_xlabel("time from drive start (s)")
    top_legend(fig, axes, ncol=4)
    save(fig, out, "fig7_initialization")


def fig_headline(met, out, builders):
    methods = [("Baseline THETA0", "THETA0", INK["secondary"]), (P1, "Paper 1 GWO (truth)", INK["primary"])] + [
        (f"Library + online update ({b})", f"Library, {BUILDER[b]}", SERIES[b]) for b in builders]
    dss = [x for x in C.DATASETS if x in set(met.dataset)]
    mets = METRICS[:3]
    fig, axes = plt.subplots(len(mets), len(dss), figsize=(7.0, 1.05 + 0.32 * len(methods) * len(mets)),
                             squeeze=False, sharey=True)
    names = [n for _, n, _ in methods]
    for i, (col, lab) in enumerate(mets):
        for j, ds in enumerate(dss):
            ax = axes[i, j]
            d = met[met.dataset == ds]
            for y, (m, name, c) in enumerate(methods):
                r = d[d.method == m][col].dropna()
                if r.empty:
                    continue
                ax.barh(y, r.mean(), height=0.72, color=c, edgecolor="white", linewidth=1.5,
                        xerr=r.std(ddof=1) if len(r) > 1 else None,
                        error_kw=dict(lw=0.8, capsize=2, ecolor=INK["primary"]))
            ax.set_yticks(range(len(names)), names)
            ax.grid(axis="y", visible=False)
            ax.set_xlabel(f"{lab} RMSE (m)")
            if i == 0:
                ax.set_title(DS.get(ds, ds), loc="left")
    axes[0, 0].invert_yaxis()                          # shared y: THETA0 on top everywhere
    save(fig, out, "fig8_headline")


CAPTIONS = """# Figure captions

Shaded bands mark the injected GPS sections (5 m noise, 15 m noise, outage) and are drawn 50 % wider than the
sections, centred, so the short sections stay visible at the scale of a whole drive.

- **fig1_pipeline**: the system. The condition detector works on GPS fixes only; the library holds one Q/R
  setting per GPS condition; the builder (an LLM, or random search / GWO at the same budget) proposes
  settings scored on GPS only, from the drive start (initialization mode) and when a new condition appears.
- **fig2_detector**: estimated GPS noise and the detected condition against the true sections, whole drive.
- **fig3_onset**: horizontal error at the start of the 15 m section (solid line: where the noise starts):
  THETA0, the library without the plausibility filter, with the true condition, and as deployed (detected
  condition).
- **fig4_test_error**: horizontal error over the test part: THETA0, paper 1's truth-tuned GWO setting and the
  library with online update.
- **fig5_score_check**: top, the GPS-only score against the true error over R settings on the noise sections;
  bottom, on normal-GPS windows, the score against the true drift over 30 s without GPS (Q settings included).
- **fig6_library**: the library's horizontal GPS noise setting per condition, in decades above THETA0, per
  builder and seed (R rises with the GPS noise).
- **fig7_initialization**: horizontal error from the drive start to the split, THETA0 against the
  initialization mode; ticks mark re-tunings.
- **fig8_headline**: RMSE in the 15 m section, on normal GPS and in the 30 s after the outage, mean and
  standard deviation over seeds.
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=str(C.OUT), help="a results root with seed_<s>/ folders")
    a = ap.parse_args()
    root = Path(a.root)
    out = root / "paper"
    (out / "tables").mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(parents=True, exist_ok=True)
    style()
    met, ini = load(root)
    if met.empty:
        raise SystemExit(f"no finished runs under {root}")
    builders = builders_in(met)
    b = "llm" if "llm" in builders else builders[0]
    md = ["# Q/R library: paper tables",
          f"Root: {root}; seeds {', '.join(str(int(x)) for x in sorted(met.seed.unique()))}; main builder {b}.", ""]
    for name, title, df in (("main", "Test part, horizontal RMSE (m), mean ± std over seeds", table_main(met, builders)),
                            ("ablation", f"Ablations ({BUILDER[b]} builder), test part RMSE (m)",
                             table_ablation(met, ablation_roots(root), b)),
                            ("init", "Initialization period (drive start to split), RMSE (m)", table_init(ini, builders)),
                            ("llm_cost", "LLM cost", table_llm(root)),
                            ("detector", "Condition detector (seed 0)", table_detector(root))):
        if not df.empty:
            md.append(write_table(df, out / "tables", name, title))
    (out / "tables" / "all.md").write_text("\n".join(md), encoding="utf-8")
    fo = out / "figures"
    fig_pipeline(fo)
    fig_detector(root, fo)
    fig_onset(root, fo, b)
    fig_test_error(root, fo, b)
    fig_score(fo)
    fig_library(root, fo, builders)
    fig_init(root, fo, builders)
    fig_headline(met, fo, builders)
    (out / "captions.md").write_text(CAPTIONS, encoding="utf-8")
    print(f"tables and figures in {out}")


if __name__ == "__main__":
    main()
