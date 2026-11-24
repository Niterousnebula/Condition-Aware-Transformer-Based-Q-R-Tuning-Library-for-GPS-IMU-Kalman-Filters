"""Does the GPS-only score rank settings like the ground truth does? (python -m qrlib.score_check)

1. R grid. On each degraded GPS section of each drive (training 5 m section and test 15 m section), a grid of R settings
(log_r_xy over THETA0 +- 3 decades, and log_r_vel where the drive has GPS velocity) is run from the THETA0
reference state at the section start. Each setting gets its GPS-only score (runner.score_candidates) and its
true horizontal RMSE over the section; the Spearman correlation and the regret of the score's pick are written
to results/qrlib/score_check.csv, for the one-step score and the score with simulated dropouts.
2. Coasting. On the training part's normal-GPS windows, THETA0 and 47 uniform random settings (as the random
builder draws them, Q included) get both scores and two truth errors: tracking (RMSE over the window, all GPS)
and drift (RMSE over 30 s with no GPS right after it). Written to coast_check.csv (summary) and
coast_points.csv (every setting, for the figure).
Ground truth is used here only to check the score, never to build.
"""
import numpy as np
import pandas as pd
import torch
from scipy.stats import spearmanr

from . import aekf, build, config as C, data as D, runner


POINTS = []


def check(dataset, device="cpu"):
    d, sections = D.load(dataset)
    _, _, t_split = D.split(d, sections)
    dr = runner.Drive(d, t_split, device=device)
    rows = []
    for s in sections:
        if s["kind"] != "noise":
            continue
        a, b = dr.step(s["t_start_s"]), dr.step(s["t_end_s"])
        st = runner.checkpoints(dr, dr.theta0, [a])[a]
        grid = []
        for dxy in np.arange(-1.0, 3.01, 0.5):
            for rv in ([-1.0, 0.0, 0.5, 1.0] if dr.has_vel else [dr.theta0[6]]):
                th = dr.theta0.copy()
                th[4], th[6] = dr.theta0[4] + dxy, rv
                grid.append(dr.clip(th))
        grid = np.unique(np.array(grid), axis=0)
        K = len(grid)
        score, _ = runner.score_candidates(dr, grid, [(a, b)], {a: st})
        lq, lr = aekf.base_logs(grid, K, dr.S.device)
        rep = lambda v: v.expand(K, *v.shape[1:]).clone()
        with torch.no_grad():
            o = aekf.rollout(dr.S, [a] * K, rep(st["x"]), rep(st["P"]), b - a, lq, lr, gate=C.GATE,
                             t_last0=rep(st["t_last"]), p_fix0=rep(st["p_fix"]))
        pos = o["pos"].cpu().numpy()
        pt = dr.S.p_true[a:b + 1].cpu().numpy()
        rmse = np.sqrt(((pos[:, :, :2] - pt[:, None, :2]) ** 2).sum(-1).mean(0))
        for th, sc_, rm in zip(grid, score, rmse):
            POINTS.append({"dataset": dataset, "section": f"{s['sigma_h_m']:.0f} m noise",
                           "score_type": "with dropouts" if C.SCORE_DROPOUT else "one-step",
                           "log_r_xy": float(th[4]), "log_r_vel": float(th[6]), "score": float(sc_),
                           "truth_rmse": float(rm)})
        i_s, i_t = int(np.argmin(score)), int(np.argmin(rmse))
        i_0 = int(np.argmin(np.abs(grid - dr.theta0).sum(1)))
        rows.append({"dataset": dataset, "section": f"{s['sigma_h_m']:.0f} m noise",
                     "part": "train" if s["t_end_s"] <= t_split else "test", "n_settings": K,
                     "spearman": float(spearmanr(score, rmse)[0]),
                     "truth_rmse_score_pick": float(rmse[i_s]), "truth_rmse_best": float(rmse[i_t]),
                     "truth_rmse_theta0": float(rmse[i_0]),
                     "score_pick_r_xy": float(grid[i_s][4]), "best_r_xy": float(grid[i_t][4]),
                     "score_pick_r_vel": float(grid[i_s][6]), "best_r_vel": float(grid[i_t][6])})
    return rows


@torch.no_grad()
def coast_check(dataset, n_random=47, outage_s=30.0, n_windows=4, device="cpu", seed=0):
    d, sections = D.load(dataset)
    _, _, t_split = D.split(d, sections)
    dr = runner.Drive(d, t_split, device=device)
    n_tr = (dr.i_split + dr.decide - 1) // dr.decide
    t_dec = dr.t[dr.decide * np.arange(n_tr)]
    act = runner.active_labels(D.detect(d, t_dec)[0], int(round(C.HOLD_S / C.DECIDE_S)))
    t_last = dr.t[dr.i_split - 1] - outage_s                    # room for the drift run inside the training part
    wins = build.condition_windows(t_dec, act, dr.t[0], t_last, "nominal", n_windows)
    steps = [(dr.step(a), dr.step(b)) for a, b in wins]
    states = runner.checkpoints(dr, dr.theta0, [a for a, _ in steps])
    rng = np.random.default_rng(seed)
    thetas = np.array([dr.theta0] + [dr.clip(rng.uniform(dr.lo, dr.hi)) for _ in range(n_random)])
    K, M = len(thetas), len(steps)
    jm = D.jump_limit("nominal")
    keep = C.SCORE_DROPOUT
    scores = {}
    for drop in (False, True):
        C.SCORE_DROPOUT = drop
        scores[drop] = runner.score_candidates(dr, thetas, steps, states, jump_max=jm)[0]
    C.SCORE_DROPOUT = keep
    # truth: the window with all GPS, then outage_s with none
    n_out = int(round(outage_s / float(np.median(np.diff(dr.t)))))
    lens = np.array([b - a for a, b in steps] * K)
    total = int(lens.max()) + n_out
    s0 = np.array([a for a, _ in steps] * K)
    i = np.arange(total)[None, :]
    z_drop = torch.as_tensor(i >= lens[:, None], device=dr.S.device)
    cat = lambda key: torch.cat([states[a][key] for a, _ in steps] * K, dim=0)
    lq, lr = aekf.base_logs(np.repeat(thetas, M, axis=0), K * M, dr.S.device)
    o = aekf.rollout(dr.S, s0, cat("x"), cat("P"), total, lq, lr, gate=C.GATE, t_last0=cat("t_last"),
                     p_fix0=cat("p_fix"), z_drop=z_drop, **runner._jump_args(dr, jm, K * M))
    pos = o["pos"].cpu().numpy()[1:, :, :2]                     # after step i
    idx = np.minimum(s0[None, :] + np.arange(1, total + 1)[:, None], dr.S.n - 1)
    err2 = ((pos - dr.S.p_true.cpu().numpy()[idx][..., :2]) ** 2).sum(-1)    # total x B
    rel = np.arange(total)[:, None]
    win = rel < lens[None, :]
    out = (rel >= lens[None, :]) & (rel < lens[None, :] + n_out)
    track = np.sqrt((np.where(win, err2, 0).sum(0) / win.sum(0)).reshape(K, M).mean(1))
    drift = np.sqrt((np.where(out, err2, 0).sum(0) / out.sum(0)).reshape(K, M).mean(1))
    bad = o["failed"].cpu().numpy().reshape(K, M).any(1) | ~np.isfinite(track) | ~np.isfinite(drift)
    track, drift = np.where(bad, np.inf, track), np.where(bad, np.inf, drift)
    sp = lambda a, b: float(spearmanr(a, b, nan_policy="omit")[0])
    i1, i2 = int(np.argmin(scores[False])), int(np.argmin(scores[True]))
    row = {"dataset": dataset, "n_settings": K, "n_windows": M,
           "spearman_onestep_track": sp(scores[False], track), "spearman_dropout_track": sp(scores[True], track),
           "spearman_onestep_drift": sp(scores[False], drift), "spearman_dropout_drift": sp(scores[True], drift),
           "drift_onestep_pick": float(drift[i1]), "drift_dropout_pick": float(drift[i2]),
           "drift_theta0": float(drift[0]), "drift_best": float(np.min(drift)),
           "track_onestep_pick": float(track[i1]), "track_dropout_pick": float(track[i2]),
           "track_theta0": float(track[0]), "track_best": float(np.min(track))}
    pts = pd.DataFrame(thetas, columns=list(C.PARAM_NAMES))
    pts.insert(0, "dataset", dataset)
    pts["is_theta0"] = np.arange(K) == 0
    pts["score_onestep"], pts["score_dropout"], pts["truth_track"], pts["truth_drift"] = (
        scores[False], scores[True], track, drift)
    return row, pts


def main():
    C.OUT.mkdir(parents=True, exist_ok=True)
    keep, rows = C.SCORE_DROPOUT, []
    for ds in C.DATASETS:
        for drop in (False, True):
            C.SCORE_DROPOUT = drop
            rows += [{**r, "score": "with dropouts" if drop else "one-step"} for r in check(ds)]
    C.SCORE_DROPOUT = keep
    df = pd.DataFrame(rows)
    df.to_csv(C.OUT / "score_check.csv", index=False)
    pd.DataFrame(POINTS).to_csv(C.OUT / "score_points.csv", index=False)
    print(df.to_string(index=False, float_format=lambda v: f"{v:.2f}"))
    res = [coast_check(ds) for ds in C.DATASETS]
    dc = pd.DataFrame([r for r, _ in res])
    dc.to_csv(C.OUT / "coast_check.csv", index=False)
    pd.concat([p for _, p in res], ignore_index=True).to_csv(C.OUT / "coast_points.csv", index=False)
    print(dc.T.to_string(float_format=lambda v: f"{v:.3f}"))


if __name__ == "__main__":
    main()
