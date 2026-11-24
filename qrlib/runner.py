"""Running the filter: one Stream per drive, checkpoints of a reference run, scoring candidates on windows
with the GPS-only score, and the piecewise online run that follows the library."""
import numpy as np
import torch


from . import aekf, config as C
from . import data as D

DT = aekf.DTYPE


class Drive:
    """A whole drive on one Stream, split at t_split (train: steps < i_split, test: steps >= i_split)."""

    def __init__(self, data, t_split, device="cuda"):
        self.data = data
        self.S = aekf.Stream(data, device=device)
        self.t = data["t_imu"]
        self.i_split = int(np.searchsorted(self.t, t_split))
        self.theta0 = np.asarray(data["theta0"], dtype=float)
        self.has_vel = {3, 4} <= set(self.S.channels.tolist())
        self.free = np.array([True] * 6 + [self.has_vel])        # log_r_vel is unused without GPS velocity
        span = np.array([C.Q_SPAN] * 4 + [C.R_SPAN] * 3)
        self.lo, self.hi = self.theta0 - span, self.theta0 + span
        self.decide = max(1, int(round(C.DECIDE_S / float(np.median(np.diff(self.t))))))
        jumps = D.fix_jumps(data)                                     # per fix, from GPS only
        zi = self.S.zi
        self.z_jump = torch.as_tensor(np.where(zi >= 0, jumps[np.maximum(zi, 0)], 0.0), dtype=DT,
                                      device=self.S.device)

    def step(self, t):
        return int(np.clip(np.searchsorted(self.t, t), 0, self.S.n - 1))

    def clip(self, theta):
        th = np.clip(np.asarray(theta, dtype=float), self.lo, self.hi)
        th[..., ~self.free] = self.theta0[~self.free]
        return th


def _state(out, b=None):
    sel = (lambda v: v) if b is None else (lambda v: v[b:b + 1])
    return {"x": sel(out["x"]).detach(), "P": sel(out["P"]).detach(), "t_last": sel(out["t_last"]).detach(),
            "p_fix": sel(out["p_fix"]).detach()}


def initial_state(drive):
    S = drive.S
    x, P = S.x0.unsqueeze(0).clone(), S.P0.unsqueeze(0).clone()
    return {"x": x, "P": P, "t_last": S.t[[0]].clone(), "p_fix": x[:, 0:2].clone()}


@torch.no_grad()
def checkpoints(drive, theta, steps, start=None, s_start=0, keep_pos=False):
    """Run theta from s_start (state start, default the drive's initial state) and keep the state at each step
    of steps (sorted, >= s_start). Returns {step: state}, and with keep_pos also the positions (n x 3) from
    s_start to the last step."""
    st = initial_state(drive) if start is None else start
    lq, lr = aekf.base_logs(theta, 1, drive.S.device)
    out_states, s, pos = {}, s_start, []
    for target in sorted(set(int(v) for v in steps)):
        if target > s:
            o = aekf.rollout(drive.S, [s], st["x"], st["P"], target - s, lq, lr, gate=C.GATE,
                             t_last0=st["t_last"], p_fix0=st["p_fix"])
            if keep_pos:
                pos.append(o["pos"][1:] if pos else o["pos"])
            st, s = _state(o), target
        out_states[target] = st
    if keep_pos:
        return out_states, torch.cat(pos)[:, 0].cpu().numpy()
    return out_states


@torch.no_grad()
def score_candidates(drive, thetas, windows, states, jump_max=None):
    """GPS-only score of each candidate: RMS of |GPS fix - predicted position| (horizontal) over every fix in
    every window, the filter switching to the candidate at the window start from the stored state.

    windows: list of (s_start, s_end) steps; states: {s_start: state}. jump_max: the jump gate's limit for the
    condition being tuned (None or inf: no jump gate). Returns scores (K,) and failed (K,).
    E|z - p_pred|^2 = E|p_true - p_pred|^2 + sigma_gps^2 for white GPS noise, so within one window the score
    ranks candidates as their prediction error against the truth would, without the truth.
    Simulated dropouts (C.SCORE_DROPOUT): the fixes of SCORE_DROP_S seconds from SCORE_DROP_AT s into every
    SCORE_DROP_EVERY s of the window are hidden, so the score also holds the prediction after the filter
    coasted on the IMU (the first fix after each gap). That is what Q decides; one-step predictions alone
    rewarded settings that follow smooth GPS with drifting bias estimates.
    """
    S = drive.S
    thetas = np.atleast_2d(thetas)
    K, M = len(thetas), len(windows)
    s0 = np.array([w[0] for w in windows] * K)
    n_steps = min(max(w[1] - w[0] for w in windows), S.n - 1 - int(s0.max()))
    cat = lambda key: torch.cat([states[w[0]][key] for w in windows] * K, dim=0)
    th = np.repeat(thetas, M, axis=0)
    lq, lr = aekf.base_logs(th, K * M, S.device)
    out = aekf.rollout(S, s0, cat("x"), cat("P"), n_steps, lq, lr, gate=C.GATE, t_last0=cat("t_last"),
                       p_fix0=cat("p_fix"), keep_innov=True, z_drop=drop_mask(drive, s0, n_steps),
                       **_jump_args(drive, jump_max, K * M))
    t_end = torch.as_tensor([S.t[min(w[1], S.n - 1)].item() for w in windows] * K, dtype=DT, device=S.device)
    if out["innov_log"]:
        T = torch.stack([e[0] for e in out["innov_log"]])
        Y = torch.stack([e[1] for e in out["innov_log"]])
        H = torch.stack([e[2] for e in out["innov_log"]]) & (T < t_end.view(1, -1))
        sq = torch.where(H, Y * Y, torch.zeros_like(Y)).sum(0).view(K, M).sum(1)
        n = H.sum(0).view(K, M).sum(1).to(DT)
        score = torch.sqrt(sq / n.clamp(min=1)).cpu().numpy()
    else:
        score = np.full(K, np.nan)
    failed = out["failed"].view(K, M).any(1).cpu().numpy() | ~np.isfinite(score)
    score = np.where(failed, np.inf, score)
    return score, failed


def drop_mask(drive, s0, n_steps):
    """The score's simulated GPS dropouts (B x n_steps, True = hide the fixes of that step), None when off."""
    if not C.SCORE_DROPOUT:
        return None
    S = drive.S
    s0 = torch.as_tensor(np.asarray(s0), device=S.device).long().view(-1, 1)
    idx = torch.clamp(s0 + torch.arange(n_steps, device=S.device).view(1, -1), max=S.n - 2)
    phase = torch.remainder(S.t[idx + 1] - S.t[s0], C.SCORE_DROP_EVERY)   # step i's fixes arrive by t[s0+i+1]
    return (phase >= C.SCORE_DROP_AT) & (phase < C.SCORE_DROP_AT + C.SCORE_DROP_S)


def _jump_args(drive, jump_max, B):
    if not C.JUMP_GATE or jump_max is None or not np.isfinite(jump_max):
        return {}
    return {"z_jump": drive.z_jump, "jump_max": torch.full((B,), float(jump_max), dtype=DT, device=drive.S.device)}


class PiecewisePolicy:
    """Q/R in force at each decision, from a per-decision theta table (n_dec x B x 7), and the jump gate's
    limit from jump_table (n_dec x B)."""
    needs_ctx = False

    def __init__(self, table, base, jump_table=None):
        self.table, self.base, self.k = table, base, 0
        self.jump_table, self.jump_max = jump_table, None

    def __call__(self):
        k = min(self.k, len(self.table) - 1)
        th = self.table[k]
        self.k += 1
        if self.jump_table is not None:
            self.jump_max = self.jump_table[k]
        d = th - self.base
        return d[:, :4], d[:, 4:7]


def active_labels(labels, hold_decisions):
    """The condition the library follows: a noisier condition, outage and recovery switch at once; a cleaner
    noise condition only after it held hold_decisions decisions."""
    sev = {s: i for i, s in enumerate(C.SEVERITY)}
    out, cur, cand, n = [], labels[0], labels[0], 0
    for lab in labels:
        if lab in ("outage", "recovery"):
            cur, cand, n = lab, lab, 0
        elif lab != cur:
            n = n + 1 if lab == cand else 1
            cand = lab
            noisier = cur in sev and sev[lab] > sev[cur]
            if noisier or n >= hold_decisions or cur in ("outage", "recovery"):
                cur, n = lab, 0
        else:
            n = 0
        out.append(cur)
    return out


def lookup(library, label, theta0):
    """The library's entry for label. A noise condition without one takes the nearest cleaner entry with its R
    raised to at least THETA0's (an unseen noisier condition never trusts GPS more than a cleaner one or the
    default), else the nearest noisier entry. Anything else takes nominal, else THETA0."""
    if label in library:
        return library[label]["theta"], label
    if label in C.SEVERITY:
        i = C.SEVERITY.index(label)
        for j in range(i - 1, -1, -1):
            if C.SEVERITY[j] in library:
                th = np.array(library[C.SEVERITY[j]]["theta"], dtype=float)
                th[4:7] = np.maximum(th[4:7], theta0[4:7])
                return th, C.SEVERITY[j] + " (R >= THETA0)"
        for j in range(i + 1, len(C.SEVERITY)):
            if C.SEVERITY[j] in library:
                return library[C.SEVERITY[j]]["theta"], C.SEVERITY[j]
    if "nominal" in library:
        return library["nominal"]["theta"], "nominal"
    return theta0, "theta0"


def tables_for(drive, active, library, n_dec):
    """The setting in force at each decision (n_dec x 7) and the entry used, following the active condition;
    THETA0 while the library is empty."""
    if not library:
        return np.repeat(drive.theta0[None], n_dec, 0), ["theta0"] * n_dec
    th, used = [], []
    for k in range(n_dec):
        t, lab = lookup(library, active[k], drive.theta0)
        th.append(t)
        used.append(lab)
    return np.array(th), used


def jumps_for(active):
    """The jump gate's limit at each decision, from the condition the library follows."""
    return np.array([D.jump_limit(lab) for lab in active])


def cat_states(states):
    """One batched state from a list of single states."""
    return {k: torch.cat([s[k] for s in states], dim=0) for k in states[0]}


@torch.no_grad()
def run_test(drive, start, tables, s_from=None, s_to=None, keep=True, jumps=None):
    """One rollout over [s_from, s_to) for B filters, each following its own per-decision theta table
    (B x n_dec x 7) and, with jumps (B x n_dec, inf = off), its jump gate limit. Returns positions (n+1, B, 3),
    the Q/R in force, the end state and the NIS log."""
    S = drive.S
    s_from = drive.i_split if s_from is None else s_from
    s_to = S.n - 1 if s_to is None else s_to
    tables = np.asarray(tables)
    B = tables.shape[0]
    base = np.repeat(drive.theta0[None], B, 0)
    tb = torch.as_tensor(np.transpose(tables, (1, 0, 2)), dtype=DT, device=S.device)
    jt = None
    if C.JUMP_GATE and jumps is not None:
        jt = torch.as_tensor(np.transpose(np.asarray(jumps, dtype=float)), dtype=DT, device=S.device)
    pol = PiecewisePolicy(tb, torch.as_tensor(base, dtype=DT, device=S.device), jt)
    lq, lr = aekf.base_logs(base, B, S.device)
    rep = lambda v: v.expand(B, *v.shape[1:]).clone() if v.shape[0] == 1 else v
    out = aekf.rollout(S, [s_from] * B, rep(start["x"]), rep(start["P"]), s_to - s_from, lq, lr, policy=pol,
                       gate=C.GATE, decide_every=drive.decide, t_last0=rep(start["t_last"]),
                       p_fix0=rep(start["p_fix"]), keep_nis=keep, z_jump=drive.z_jump if jt is not None else None)
    return out
