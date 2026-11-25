"""One dataset end to end: build the libraries on the training part, run every method on the test part,
score against ground truth (only here), write results/qrlib/<dataset>/."""
import json
import time

import numpy as np
import pandas as pd
import torch

from . import build, config as C, data as D, runner


def _slug(ds):
    return ds.replace("/", "__")


def _jsonable(v):
    if isinstance(v, dict):
        return {k: _jsonable(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_jsonable(x) for x in v]
    if isinstance(v, np.ndarray):
        return v.tolist()
    if isinstance(v, (np.floating, np.integer)):
        return v.item()
    return v


def self_update_run(drive, start, labels, stats, library0, proposer_name, nominal_sig, n_dec, log,
                    rounds=C.UPDATE_ROUNDS, K=C.UPDATE_K):
    """The library follows the detected condition; a noise condition it has no entry for (or recovery), once
    it has lasted UPDATE_S, gets one: a search on those last UPDATE_S seconds from this run's own state at
    their start, scored on GPS only (R only with C.UPDATE_R_ONLY). With C.UPDATE_REPROCESS the window is then
    filtered again with the new entry from that same state, so the entry is used from the state it was scored
    from; the positions already output for the window are kept (causal). Outages get no entry (no fixes)."""
    library = {k: dict(v) for k, v in library0.items()}
    need = lambda lab: int(round((C.UPDATE_RECOVERY_S if lab == "recovery" else C.UPDATE_S) / C.DECIDE_S))
    s_of = lambda k: drive.i_split + k * drive.decide
    # triggers depend only on the labels and on which entries exist, so they are known in advance
    triggers, have, run_lab, run_n = [], set(library), None, 0
    for k, lab in enumerate(labels):
        run_n = run_n + 1 if lab == run_lab else 1
        run_lab = lab
        n_need = need(lab)
        if lab not in have and lab != "outage" and run_n == n_need:
            triggers.append((k - n_need + 1, k, lab))
            have.add(lab)
    pos, qr, nis, used_all, events = [], [], [], [], []
    state, k_from = start, 0
    bounds = sorted({b for kw, kt, _ in triggers for b in (kw, kt)} | {n_dec})
    pending = {kt: (kw, lab) for kw, kt, lab in triggers}
    saved = {}
    for k_to in bounds:
        if k_to > k_from:
            tab, used = runner.tables_for(drive, labels, library, n_dec)
            s_to = min(s_of(k_to), drive.S.n - 1)
            out = runner.run_test(drive, state, tab[None, k_from:k_to], s_from=s_of(k_from), s_to=s_to,
                                  jumps=runner.jumps_for(labels)[None, k_from:k_to])
            pos.append(out["pos"][1:] if pos else out["pos"])
            qr.append(out["qr"][0])
            nis += out["nis_log"]
            used_all += used[k_from:k_to]
            state = runner._state(out)
            k_from = k_to
        saved[k_to] = state
        if k_to in pending:
            kw, lab = pending[k_to]
            win_s = [(drive.t[s_of(kw)], drive.t[s_of(k_to)])]
            sig = float(np.nanmedian(stats["sigma_h"][kw:k_to + 1]))
            info = build.prompt_info(drive, lab, sig, nominal_sig, win_s, library)
            in_force = np.asarray(runner.lookup(library, lab, drive.theta0)[0], dtype=float)
            if C.UPDATE_R_ONLY:                         # Q stays at the setting in force
                free_r = drive.free & np.array([False] * 4 + [True] * 3)
                info.update(free=free_r, theta0=in_force,
                            clip=lambda th, f=free_r, b=in_force: drive.clip(np.where(f, th, b)))
            seeds = [in_force, drive.theta0] + [v["theta"] for v in library.values()]
            log(f"  online {proposer_name}: new condition '{lab}' at t = {win_s[0][1]:.0f} s")
            entry = build.search(drive, win_s, {s_of(kw): saved[kw]}, proposer_name, rounds, K, seeds, info, log)
            entry["online_at_s"] = win_s[0][1]
            library[lab] = entry
            events.append({"label": lab, "t_s": win_s[0][1], "score": entry["score"],
                           "theta": entry["theta"].tolist()})
            if C.UPDATE_REPROCESS:                      # re-filter the window with the new entry (outputs stay)
                tab, _ = runner.tables_for(drive, labels, library, n_dec)
                out = runner.run_test(drive, saved[kw], tab[None, kw:k_to], s_from=s_of(kw),
                                      s_to=min(s_of(k_to), drive.S.n - 1), keep=False,
                                      jumps=runner.jumps_for(labels)[None, kw:k_to])
                state = runner._state(out)
                saved[k_to] = state
    return {"pos": torch.cat(pos).cpu().numpy()[:, 0], "qr": torch.cat(qr).cpu().numpy(), "nis": nis,
            "used": used_all, "events": events, "library": library}


def nis_over_dof(drive, nis_log):
    """Mean NIS / dof of the used updates, per batch element."""
    if not nis_log:
        return None
    N = torch.stack([n for _, n, _ in nis_log])
    U = torch.stack([u for _, _, u in nis_log]).to(N.dtype)
    return ((N * U).sum(0) / U.sum(0).clamp(min=1) / drive.S.m).cpu().numpy()


def metrics(drive, sections, pos, nis=None, raw=False):
    """Horizontal RMSE on the test part, overall and per part, against the ground truth."""
    d = drive.data
    t_split = drive.t[drive.i_split]
    tt, pt = d["t_true"], d["p_true"]
    if raw:
        tg = d["t_gps"]
        m = (tg >= t_split) & (tg >= tt[0]) & (tg <= tt[-1])
        te, pe = tg[m], d["p_gps"][m]
        err = pe - np.column_stack([np.interp(te, tt, pt[:, i]) for i in range(3)])
        terr = te
    else:
        t = drive.t[drive.i_split:drive.i_split + len(pos)]
        m = (tt >= t[0]) & (tt <= t[-1])
        terr = tt[m]
        est = np.column_stack([np.interp(terr, t, pos[:, i]) for i in range(3)])
        err = est - pt[m]
    eh = np.hypot(err[:, 0], err[:, 1])
    heavy, outage = sections[1], sections[2]
    parts = {"all": np.ones(len(terr), bool),
             "heavy_15m": (terr >= heavy["t_start_s"]) & (terr < heavy["t_end_s"]),
             "outage": (terr >= outage["t_start_s"]) & (terr < outage["t_end_s"]),
             "recovery_30s": (terr >= outage["t_end_s"]) & (terr < outage["t_end_s"] + C.RECOVERY_S)}
    parts["outside"] = ~(parts["heavy_15m"] | parts["outage"] | parts["recovery_30s"])
    out = {f"rmse_{k}": float(np.sqrt(np.mean(eh[v] ** 2))) if v.any() else np.nan for k, v in parts.items()}
    if nis is not None:
        out["nis_over_dof"] = float(nis)
    return out, terr, eh


def train_metrics(drive, sections, pos):
    """Horizontal RMSE over the training part (the initialization period): overall, in its 5 m section,
    in the first 10 s of that section and outside it."""
    d = drive.data
    t = drive.t[:len(pos)]
    tt, pt = d["t_true"], d["p_true"]
    m = (tt >= t[0]) & (tt <= t[-1])
    terr = tt[m]
    est = np.column_stack([np.interp(terr, t, pos[:, i]) for i in range(2)])
    eh = np.hypot(*(est - pt[m][:, :2]).T)
    s5 = sections[C.SPLIT_AFTER_SECTION]
    in5 = (terr >= s5["t_start_s"]) & (terr < s5["t_end_s"])
    parts = {"all": np.ones(len(terr), bool), "moderate_5m": in5,
             "moderate_5m_first10s": in5 & (terr < s5["t_start_s"] + 10.0), "outside": ~in5}
    return {f"train_rmse_{k}": float(np.sqrt(np.mean(eh[v] ** 2))) if v.any() else np.nan for k, v in parts.items()}


def paper1_theta(dataset):
    """Paper 1's ground-truth-tuned offline GWO setting for this drive (D:\\EKF best_values.csv), or None."""
    if not C.PAPER1_BEST.exists():
        return None
    df = pd.read_csv(C.PAPER1_BEST)
    r = df[(df.dataset == dataset) & (df.optimizer == "GWO")]
    return None if r.empty else r.iloc[0][list(C.PARAM_NAMES)].to_numpy(dtype=float)


def _every(drive, hz=C.TRACE_HZ):
    return max(1, int(round(1.0 / (hz * float(np.median(np.diff(drive.t)))))))


def run(dataset, builders=("llm", "gwo"), smoke=False, device="cuda", log=print, out_dir=None):
    t0 = time.time()
    out_dir = (C.OUT / _slug(dataset)) if out_dir is None else out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    data, sections = D.load(dataset)
    _, _, t_split = D.split(data, sections)
    drive = runner.Drive(data, t_split, device=device)
    rounds, K, maxw = (1, 2, 2) if smoke else (C.BUILD_ROUNDS, C.BUILD_K, C.MAX_WINDOWS)
    irounds = 1 if smoke else C.INIT_ROUNDS
    urounds, uK = (1, 2) if smoke else (C.UPDATE_ROUNDS, C.UPDATE_K)
    log(f"=== {dataset}: split at {t_split:.0f} s (step {drive.i_split} of {drive.S.n}), decision every "
        f"{drive.decide} IMU steps; library: {'initialization mode' if C.INIT_MODE else 'offline build'}")

    # decisions every drive.decide IMU steps from the drive start (training part), then over the test part
    n_tr = (drive.i_split + drive.decide - 1) // drive.decide
    n_dec = (drive.S.n - 1 - drive.i_split + drive.decide - 1) // drive.decide
    t_dec_tr = drive.t[drive.decide * np.arange(n_tr)]
    t_dec_te = drive.t[drive.i_split + drive.decide * np.arange(n_dec)]
    lab_all, st_all = D.detect(data, np.concatenate([t_dec_tr, t_dec_te]))
    hold = int(round(C.HOLD_S / C.DECIDE_S))
    act_all = runner.active_labels(lab_all, hold)
    lab_tr = lab_all[:n_tr]
    act_tr, act_det = act_all[:n_tr], act_all[n_tr:]
    st_tr = {k: v[:n_tr] for k, v in st_all.items()}
    st_te = {k: v[n_tr:] for k, v in st_all.items()}
    act_orc = D.oracle(sections, t_dec_te)
    jn = C.JUMP_N                                      # ablation: the detector without the jump trigger
    C.JUMP_N = 0
    act_nf = runner.active_labels(D.detect(data, np.concatenate([t_dec_tr, t_dec_te]))[0], hold)[n_tr:]
    C.JUMP_N = jn
    sig_nom = st_tr["sigma_h"][np.array(lab_tr) == "nominal"]
    nominal_sig = float(np.nanmedian(sig_nom)) if np.isfinite(sig_nom).any() else float("nan")

    # reference THETA0 run over the training part: its states (static entry, offline build) and positions
    starts = {drive.step(a) for a, _ in build.tiles(drive.t[0], drive.t[drive.i_split - 1])} | {drive.i_split}
    if not C.INIT_MODE:
        for label in C.SEVERITY:
            starts |= {drive.step(a) for a, _ in build.condition_windows(t_dec_tr, lab_tr, drive.t[0], t_split,
                                                                         label, maxw)}
    tr0 = time.time()
    states, pos_ref = runner.checkpoints(drive, drive.theta0, sorted(starts), keep_pos=True)
    log(f"  reference run over the training part: {time.time() - tr0:.0f} s")
    start0 = states[drive.i_split]
    init_rows = [{"method": "THETA0", **train_metrics(drive, sections, pos_ref)}]

    libs = {}
    for b in builders:
        if C.INIT_MODE:
            lib, st_b, pos_b, ev = build.init_mode(drive, t_dec_tr, act_tr, st_tr, b, log, rounds=irounds, K=K,
                                                   max_windows=maxw)
            init_rows.append({"method": f"Initialization mode ({b})", **train_metrics(drive, sections, pos_b),
                              "tunings": len(ev)})
        else:
            lib = build.build_library(drive, t_dec_tr, lab_tr, st_tr, b, states, nominal_sig, log, rounds=rounds,
                                      K=K, max_windows=maxw)
            st_b, ev = start0, []
        static = build.build_static(drive, st_tr, b, states, nominal_sig, log, rounds=rounds, K=K,
                                    max_windows=maxw)
        libs[b] = {"library": lib, "static": static, "init_events": ev}
        (out_dir / f"library_{b}.json").write_text(json.dumps(_jsonable(libs[b]), indent=1))
        libs[b]["start"] = st_b
        if C.INIT_MODE:
            libs[b]["pos_init"] = pos_b
        log(f"  {b} library: " + ", ".join(f"{k} {v['score']:.3f} (THETA0 {v['seed_score']:.3f})"
                                           for k, v in lib.items()) + f"; static {static['score']:.3f}")
    # fixed methods, one batched rollout; library methods continue from their own state at the split
    off = np.full(n_dec, np.inf)                       # baseline and static: the plain gate only
    names, tabs, jmps = ["Baseline THETA0"], [np.repeat(drive.theta0[None], n_dec, 0)], [off]
    sts = [start0]
    p1 = paper1_theta(dataset)
    if p1 is not None:                                 # truth-tuned on the whole drive, offline: a reference
        names.append("Paper 1 GWO (ground truth, offline)")
        tabs.append(np.repeat(p1[None], n_dec, 0))
        jmps.append(off)
        sts.append(start0)
    for b in builders:
        lib, static = libs[b]["library"], libs[b]["static"]
        names.append(f"Static ({b})")
        tabs.append(np.repeat(np.asarray(static["theta"])[None], n_dec, 0))
        jmps.append(off)
        sts.append(start0)
        names.append(f"Library ({b})")
        tabs.append(runner.tables_for(drive, act_det, lib, n_dec)[0])
        jmps.append(runner.jumps_for(act_det))
        sts.append(libs[b]["start"])
        names.append(f"Library, true condition ({b})")
        tabs.append(runner.tables_for(drive, act_orc, lib, n_dec)[0])
        jmps.append(runner.jumps_for(act_orc))
        sts.append(libs[b]["start"])
        names.append(f"Library, no plausibility filter ({b})")
        tabs.append(runner.tables_for(drive, act_nf, lib, n_dec)[0])
        jmps.append(off)
        sts.append(libs[b]["start"])
    r0 = time.time()
    out = runner.run_test(drive, runner.cat_states(sts), np.stack(tabs), jumps=np.stack(jmps))
    log(f"  test part, {len(names)} fixed methods: {time.time() - r0:.0f} s")
    pos_all = out["pos"].cpu().numpy()
    rows, traces = [], {}
    m, _, _ = metrics(drive, sections, None, raw=True)
    rows.append({"method": "Raw GPS", **m})
    nis = nis_over_dof(drive, out["nis_log"])
    for i, name in enumerate(names):
        m, _, _ = metrics(drive, sections, pos_all[:, i], None if nis is None else nis[i])
        m["switches"] = int((np.abs(np.diff(tabs[i], axis=0)).max(1) > 0).sum())
        rows.append({"method": name, **m})
        traces[name] = pos_all[:, i]
    del out
    torch.cuda.empty_cache()

    # self-updating library
    events = {}
    for b in builders:
        r0 = time.time()
        su = self_update_run(drive, libs[b]["start"], act_det, st_te, libs[b]["library"], b, nominal_sig, n_dec,
                             log, rounds=urounds, K=uK)
        name = f"Library + online update ({b})"
        nis = nis_over_dof(drive, su["nis"])
        m, _, _ = metrics(drive, sections, su["pos"], None if nis is None else nis[0])
        rows.append({"method": name, **m, "online_entries": len(su["events"])})
        traces[name] = su["pos"]
        events[b] = su["events"]
        (out_dir / f"online_{b}.json").write_text(json.dumps(_jsonable(
            {"events": su["events"], "library": {k: v for k, v in su["library"].items()}}), indent=1))
        log(f"  {name}: {time.time() - r0:.0f} s, {len(su['events'])} new entries")

    df = pd.DataFrame(rows)
    df.insert(0, "dataset", dataset)
    df.to_csv(out_dir / "metrics.csv", index=False)
    df_init = pd.DataFrame(init_rows)
    df_init.insert(0, "dataset", dataset)
    df_init.to_csv(out_dir / "init.csv", index=False)
    ev = _every(drive)                                 # traces for the figures at ~TRACE_HZ
    np.savez_compressed(out_dir / "traces.npz", t=drive.t[drive.i_split:][::ev],
                        **{k: v[::ev] for k, v in traces.items()}, t_dec=t_dec_te,
                        labels_detected=np.array(act_det), labels_true=np.array(act_orc),
                        labels_no_filter=np.array(act_nf), sigma_h=st_te["sigma_h"])
    np.savez_compressed(out_dir / "init_traces.npz", t=drive.t[:drive.i_split + 1][::ev],
                        THETA0=pos_ref[::ev], **{b: libs[b]["pos_init"][::ev] for b in builders if "pos_init" in libs[b]},
                        t_dec=t_dec_tr, labels_detected=np.array(act_tr), sigma_h=st_tr["sigma_h"])
    (out_dir / "results.md").write_text(
        f"# {dataset}\n\n## Test part\n\nHorizontal RMSE in m.\n\n"
        + df.drop(columns="dataset").to_markdown(index=False, floatfmt=".3g")
        + "\n\n## Training part (initialization period)\n\n"
        + df_init.drop(columns="dataset").to_markdown(index=False, floatfmt=".3g") + "\n", encoding="utf-8")
    log(df_init.drop(columns="dataset").to_string(index=False, float_format=lambda v: f"{v:.3g}"))
    log(df.drop(columns="dataset").to_string(index=False, float_format=lambda v: f"{v:.3g}"))
    log(f"  done in {(time.time() - t0) / 60:.1f} min")
    return df, df_init
