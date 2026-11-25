"""Building library entries: windows of one GPS condition, and the proposer-driven search scored on GPS only."""
import time
import zlib

import numpy as np
import torch

from . import config as C
from . import data as D, propose, runner


def condition_windows(t_dec, labels, t_lo, t_hi, label, max_windows):
    """Non-overlapping WINDOW_S windows (s) inside runs of label within [t_lo, t_hi); a run shorter than
    WINDOW_S but at least MIN_WINDOW_S gives one window of its own length. Evenly thinned to max_windows."""
    runs, start = [], None
    for td, lab in zip(list(t_dec) + [np.inf], list(labels) + [None]):
        inside = lab == label and t_lo <= td < t_hi
        if inside and start is None:
            start = td
        elif not inside and start is not None:
            runs.append((start, min(td, t_hi)))
            start = None
    wins = []
    for a, b in runs:
        if b - a >= C.WINDOW_S:
            n = int((b - a) // C.WINDOW_S)
            wins += [(a + i * C.WINDOW_S, a + (i + 1) * C.WINDOW_S) for i in range(n)]
        elif b - a >= C.MIN_WINDOW_S:
            wins.append((a, b))
    if len(wins) > max_windows:
        idx = np.unique(np.round(np.linspace(0, len(wins) - 1, max_windows)).astype(int))
        wins = [wins[i] for i in idx]
    return wins


def tiles(t_lo, t_hi):
    n = int((t_hi - t_lo) // C.WINDOW_S)
    return [(t_lo + i * C.WINDOW_S, t_lo + (i + 1) * C.WINDOW_S) for i in range(n)]


def prompt_info(drive, label, sigma_h, sigma_nominal, windows_s, library=None):
    d = drive.data
    return {"label": label, "sigma_h": float(sigma_h), "sigma_nominal": float(sigma_nominal),
            "imu_hz": 1.0 / float(np.median(np.diff(d["t_imu"]))),
            "gps_hz": 1.0 / float(np.median(np.diff(d["t_gps"]))), "has_vel": drive.has_vel,
            "theta0": drive.theta0, "lo": drive.lo, "hi": drive.hi, "free": drive.free, "clip": drive.clip,
            "n_windows": len(windows_s), "window_s": float(np.mean([b - a for a, b in windows_s])),
            "library": library or {}}


def search(drive, windows_s, states, proposer_name, rounds, K, seeds, info, log, seed=None):
    """Seeds, then rounds x K proposals, each scored on all windows. Returns the entry with its history.
    The random stream depends on the run's seed (C.SEED), the condition and the window set, so every tuning
    of every seed draws differently (the LLM's sampling seed comes from it too)."""
    seed = C.SEED if seed is None else seed
    rng = np.random.default_rng([int(seed), zlib.crc32(info["label"].encode()),
                                 int(round(1000 * windows_s[-1][1])) & 0x7FFFFFFF, len(windows_s)])
    prop = propose.make(proposer_name)
    info = {**info, "rounds": rounds}                       # GWO's a falls from 2 to 0 over these rounds
    windows = [(drive.step(a), drive.step(b)) for a, b in windows_s]
    history, llm_log, t0 = [], [], time.time()

    def add(thetas, rnd, source):
        sc, failed = runner.score_candidates(drive, thetas, windows, states, jump_max=D.jump_limit(info["label"]))
        for th, s in zip(thetas, sc):
            history.append({"theta": np.asarray(th, dtype=float), "score": float(s), "round": rnd,
                            "source": source})

    add(np.array([info["clip"](s) for s in seeds]), 0, "seed")   # info["clip"]: an R-only search fixes Q
    for r in range(1, rounds + 1):
        cands, plog = prop.propose(history, K, info, rng)
        if plog:
            llm_log.append({"round": r, **plog})
        add(cands, r, proposer_name)
        best = min(history, key=lambda h: h["score"])
        extra = f"  (LLM parsed {plog['n_parsed']}/{K})" if plog else ""
        log(f"    {info['label']:9s} {proposer_name:6s} round {r}: best {best['score']:.3f}{extra}")
    best = min(history, key=lambda h: h["score"])
    asked = K * len(llm_log)
    parsed = sum(e["n_parsed"] for e in llm_log)
    return {"theta": best["theta"], "score": best["score"], "sigma_h": info["sigma_h"],
            "best_source": best["source"], "best_round": best["round"],
            "llm_parsed_share": (parsed / asked) if asked else None,
            "n_windows": len(windows_s), "windows_s": windows_s, "n_evals": len(history),
            "seconds": time.time() - t0, "seed_score": history[0]["score"],
            "history": [{**h, "theta": h["theta"].tolist()} for h in history], "llm_log": llm_log}


def build_library(drive, t_dec, labels, stats, proposer_name, states, nominal_sig, log, rounds=C.BUILD_ROUNDS,
                  K=C.BUILD_K, max_windows=C.MAX_WINDOWS):
    """Offline library from the training part (INIT_MODE = False): one entry per noise condition seen there
    (nominal first, so later conditions see it), from the THETA0 reference states."""
    t_lo, t_hi = drive.t[0], drive.t[drive.i_split - 1]
    sig = stats["sigma_h"]
    lab_arr = np.array(labels)
    in_train = (t_dec < t_hi)
    library = {}
    for label in C.SEVERITY:
        wins = condition_windows(t_dec, labels, t_lo, t_hi, label, max_windows)
        if not wins:
            continue
        m = in_train & (lab_arr == label)
        info = prompt_info(drive, label, np.nanmedian(sig[m]), nominal_sig, wins,
                           {k: v for k, v in library.items()})
        seeds = [drive.theta0] + [v["theta"] for v in library.values()]
        log(f"  {proposer_name}: {label}, {len(wins)} window(s)")
        library[label] = search(drive, wins, states, proposer_name, rounds, K, seeds, info, log)
    return library


def build_static(drive, stats, proposer_name, states, nominal_sig, log, rounds=C.BUILD_ROUNDS, K=C.BUILD_K,
                 max_windows=C.MAX_WINDOWS):
    """'static': one setting for the whole training part (the usual offline tuning), on up to 4 x max_windows
    tiles from the THETA0 reference states."""
    t_lo, t_hi = drive.t[0], drive.t[drive.i_split - 1]
    wins = tiles(t_lo, t_hi)
    if len(wins) > 4 * max_windows:
        idx = np.unique(np.round(np.linspace(0, len(wins) - 1, 4 * max_windows)).astype(int))
        wins = [wins[i] for i in idx]
    info = prompt_info(drive, "all (one setting for the whole drive)", np.nanmedian(stats["sigma_h"]),
                       nominal_sig, wins)
    log(f"  {proposer_name}: static, {len(wins)} window(s)")
    return search(drive, wins, states, proposer_name, rounds, K, [drive.theta0], info, log)


def init_mode(drive, t_dec, labels, stats, proposer_name, log, rounds=C.INIT_ROUNDS, K=C.BUILD_K,
              max_windows=C.MAX_WINDOWS):
    """Initialization mode, from the drive start to the split, causal throughout. The filter starts on THETA0
    and follows the library as it grows (switching and jump gate as in operation). Each time a condition
    completes a new WINDOW_S window (its first max_windows), its entry is re-tuned on its windows so far, from
    the running filter's own states at their starts, seeded with THETA0 and the current entries, and used from
    then on. t_dec: decisions every drive.decide steps from step 0; labels: the active condition at each.
    Returns the library, the state at the split, the positions from step 0 to the split, and the tunings."""
    n = len(t_dec)
    s_of = lambda k: min(k * drive.decide, drive.i_split)
    lab_arr, sig = np.array(labels), stats["sigma_h"]
    t_hi = drive.t[drive.i_split - 1]
    wins = {}                                          # label -> [(k_start, k_end)], first max_windows in time
    for label in list(C.SEVERITY) + ["recovery"]:
        w = condition_windows(t_dec, labels, t_dec[0], t_hi, label, 10 ** 9)[:max_windows]
        if w:
            wins[label] = [(int(np.searchsorted(t_dec, a)), min(int(np.searchsorted(t_dec, b)), n)) for a, b in w]
    tunings = sorted((kb, C.SEVERITY.index(lab) if lab in C.SEVERITY else 9, lab, j)
                     for lab, ws in wins.items() for j, (_, kb) in enumerate(ws))
    bounds = sorted({ka for ws in wins.values() for ka, _ in ws} | {kb for kb, *_ in tunings} | {n})
    library, saved, pos, events = {}, {}, [], []
    state, k_from = runner.initial_state(drive), 0
    saved[0] = state
    jumps = runner.jumps_for(labels)
    t0 = time.time()
    for k_to in bounds:
        if k_to > k_from:
            tab, _ = runner.tables_for(drive, labels, library, n)
            out = runner.run_test(drive, state, tab[None, k_from:k_to], s_from=s_of(k_from), s_to=s_of(k_to),
                                  keep=False, jumps=jumps[None, k_from:k_to])
            pos.append(out["pos"][1:] if pos else out["pos"])
            state = runner._state(out)
            k_from = k_to
        saved[k_to] = state
        for _, _, label, j in [e for e in tunings if e[0] == k_to]:
            ws = wins[label][:j + 1]
            win_s = [(drive.t[s_of(a)], drive.t[s_of(b)]) for a, b in ws]
            seen = lab_arr[:k_to]
            s_lab = sig[:k_to][seen == label]
            s_nom = sig[:k_to][seen == "nominal"]
            sigma = float(np.nanmedian(s_lab)) if np.isfinite(s_lab).any() else np.nan
            nominal_sig = float(np.nanmedian(s_nom)) if np.isfinite(s_nom).any() else sigma
            info = prompt_info(drive, label, sigma, nominal_sig, win_s,
                               {k: v for k, v in library.items() if k != label})
            seeds = [drive.theta0] + [v["theta"] for v in library.values()]
            log(f"  {proposer_name} init: '{label}' window {j + 1} done at t = {win_s[-1][1]:.0f} s, "
                f"tuning on {len(ws)} window(s)")
            entry = search(drive, win_s, {s_of(a): saved[a] for a, _ in ws}, proposer_name, rounds, K, seeds,
                           info, log)
            entry.update(tuned_at_s=float(win_s[-1][1]), n_tunings=j + 1)
            library[label] = entry
            events.append({"label": label, "t_s": float(win_s[-1][1]), "n_windows": len(ws),
                           "score": entry["score"], "seed_score": entry["seed_score"],
                           "theta": np.asarray(entry["theta"]).tolist()})
    log(f"  {proposer_name} initialization mode: {len(events)} tunings, {time.time() - t0:.0f} s")
    return library, state, torch.cat(pos)[:, 0].cpu().numpy(), events
