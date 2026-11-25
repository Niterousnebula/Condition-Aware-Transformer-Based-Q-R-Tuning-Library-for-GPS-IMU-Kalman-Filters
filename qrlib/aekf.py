"""The batched 16-state GPS-IMU EKF used by the Q/R library (PyTorch, float64, CPU or GPU).

The filter math is the one in ekf/filter.py (reference, filterpy) and ekf/gpu.py (batched): the same
strapdown prediction, the same Jacobians built from the same constant matrices (ekf.gpu._basis), Joseph-form
GPS update and quaternion normalisation after every prediction and update. On top of that:

* Q_c and R can change at every decision and differ per batch element (the library's settings);
* every batch element can start at its own IMU step from its own state (scoring windows, chained runs);
* the displacement plausibility gate (a fix is used only if it lies within GATE_VMAX * dt + GATE_MARGIN of
  the last accepted fix) and the jump gate (z_jump / jump_max, qrlib.data.fix_jumps);
* simulated GPS dropouts for the score (z_drop) and the innovation log the score is computed from.

check_against_reference() runs it next to ekf.filter.run_ekf with constant Q/R.
"""
import numpy as np
import torch

from ekf.filter import G_NAV, MAX_POSITION, N_STATES, init_state, measurement_channels
from ekf.gpu import _basis

from . import config as C

DTYPE = torch.float64


def q_r_from_log(log_q, log_r, channels):
    """log10 noise -> Q_c (B x 12) and the R variances of the used channels (B x m).

    log_q = [acc, gyro, bias-acc RW, bias-gyro RW]; log_r = [xy, z, vel], as ekf.tuning.theta_to_QR.
    """
    q = 10.0 ** log_q
    Q_c = q.repeat_interleave(3, dim=1)
    r = 10.0 ** log_r
    R6 = torch.stack([r[:, 0], r[:, 0], r[:, 1], r[:, 2], r[:, 2], r[:, 2]], dim=1)
    return Q_c, R6[:, channels]


class Stream:
    """One data segment on the GPU: IMU inputs, the GPS fixes after each prediction, truth at IMU times."""

    def __init__(self, data, device="cuda", x0=None):
        dev = self.device = torch.device(device)
        T = lambda a: torch.as_tensor(np.asarray(a, dtype=float), dtype=DTYPE, device=dev)
        t_imu, t_gps = data["t_imu"], data["t_gps"]
        self.data = data
        self.gate_vmax = data.get("max_speed_ms") or C.GATE_VMAX     # a car drive sets its own top speed
        self.n = n = len(t_imu)
        self.channels = measurement_channels(data)
        self.m = m = len(self.channels)
        self.ch = torch.as_tensor(self.channels, device=dev)
        z_all = np.hstack([data["p_gps"], data["v_gps"]])[:, self.channels]

        # run_ekf's schedule: the first fix sets x0; fixes with t <= t_imu[k] follow prediction k
        j, n_gps = 1, len(t_gps)
        while j < n_gps and t_gps[j] <= t_imu[0]:
            j += 1
        slots = [[] for _ in range(n - 1)]
        for k in range(1, n):
            while j < n_gps and t_gps[j] <= t_imu[k]:
                slots[k - 1].append(j)
                j += 1
        self.U = U = max(1, max(len(s) for s in slots))
        z = np.zeros((n - 1, U, m))
        zt = np.zeros((n - 1, U))
        zm = np.zeros((n - 1, U), dtype=bool)
        zi = np.full((n - 1, U), -1, dtype=np.int64)            # index of the fix in data["t_gps"]
        for s, idx in enumerate(slots):
            for u, jj in enumerate(idx):
                z[s, u], zt[s, u], zm[s, u], zi[s, u] = z_all[jj], t_gps[jj], True, jj
        self.z, self.zt, self.zm = T(z), T(zt), torch.as_tensor(zm, device=dev)
        self.zi = zi
        self.n_fix = self.zm.sum(dim=1).to(DTYPE)

        self.t = T(t_imu)
        self.a, self.w, self.dt = T(data["accel"][:-1]), T(data["gyro"][:-1]), T(np.diff(t_imu))

        # truth at IMU times (linear interpolation), valid inside the truth's time span
        t_true, p_true = data["t_true"], data["p_true"]
        p = np.column_stack([np.interp(t_imu, t_true, p_true[:, i]) for i in range(3)])
        self.p_true = T(p)
        self.true_ok = torch.as_tensor((t_imu >= t_true[0]) & (t_imu <= t_true[-1]), device=dev)

        x_init, P0 = init_state(data)
        self.x0, self.P0 = T(x_init if x0 is None else x0), T(P0)
        self.theta0 = np.asarray(data["theta0"], dtype=float)
        self.g_nav = T(G_NAV)
        self.I3 = torch.eye(3, dtype=DTYPE, device=dev)
        self.I4 = torch.eye(4, dtype=DTYPE, device=dev)
        self.I16 = torch.eye(N_STATES, dtype=DTYPE, device=dev)
        self.c_omega, self.c_xi, self.c_left, self.c_dra, self.c_rot = (T(c) for c in _basis())


# ---------------------------------------------------------------------------
# One step, functional
# ---------------------------------------------------------------------------
def _normalize(S, x, P):
    q = x[:, 6:10]
    norm = torch.linalg.vector_norm(q, dim=1, keepdim=True)
    q_bar = q / norm
    x = torch.cat([x[:, :6], q_bar, x[:, 10:]], dim=1)
    J = (S.I4 - q_bar.unsqueeze(2) * q_bar.unsqueeze(1)) / norm.unsqueeze(2)
    Tm = S.I16.expand(x.shape[0], -1, -1).clone()
    Tm[:, 6:10, 6:10] = J
    P = Tm @ P @ Tm.transpose(1, 2)
    return x, 0.5 * (P + P.transpose(1, 2))


def predict(S, x, P, a_m, w_m, dt, Q_c):
    """ekf.filter.GpsImuEKF.predict_x + P = F P F' + Q + normalize, for B elements with their own dt."""
    B = x.shape[0]
    dt = dt.view(B, 1)
    dt3 = dt.view(B, 1, 1)
    p, v, q, b_a, b_g = x[:, 0:3], x[:, 3:6], x[:, 6:10], x[:, 10:13], x[:, 13:16]
    a = a_m - b_a
    w = w_m - b_g
    R_nb = ((q.unsqueeze(2) * q.unsqueeze(1)).reshape(B, 16) @ S.c_rot).view(B, 3, 3)
    acc_nav = (R_nb @ a.unsqueeze(2)).squeeze(2) + S.g_nav
    n = torch.linalg.vector_norm(w, dim=1, keepdim=True)
    n_safe = torch.where(n > 0, n, torch.ones_like(n))
    n3 = n_safe.view(B, 1, 1)
    Om = (w @ S.c_omega).view(B, 4, 4)
    angle = n.view(B, 1, 1) * dt3
    half = 0.5 * angle
    Phi_q = torch.where(angle < 1e-9, S.I4 + 0.5 * Om * dt3,
                        torch.cos(half) * S.I4 + (torch.sin(half) / n3) * Om)
    dRa_dq = ((q.unsqueeze(2) * a.unsqueeze(1)).reshape(B, 12) @ S.c_dra).view(B, 3, 4)
    Xi = (q @ S.c_xi).view(B, 4, 3)
    small = (n * dt) < 1e-6
    h = 0.5 * n_safe * dt
    s = torch.sin(h) / n_safe
    ds_dn = (0.5 * dt * torch.cos(h) * n_safe - torch.sin(h)) / (n_safe * n_safe)
    u = w / n_safe
    top = torch.where(small, -0.25 * dt * dt * w, -0.5 * dt * torch.sin(h) * u)
    low = torch.where(small.view(B, 1, 1), 0.5 * dt3 * S.I3,
                      s.view(B, 1, 1) * S.I3 + ds_dn.view(B, 1, 1) * (w.unsqueeze(2) * u.unsqueeze(1)))
    d_dq = torch.cat([top.unsqueeze(1), low], dim=1)
    dq_dw = (q @ S.c_left).view(B, 4, 4) @ d_dq

    F = S.I16.expand(B, -1, -1).clone()
    F[:, 0:3, 3:6] = S.I3 * dt3
    F[:, 0:3, 6:10] = 0.5 * dt3 * dt3 * dRa_dq
    F[:, 0:3, 10:13] = -0.5 * dt3 * dt3 * R_nb
    F[:, 3:6, 6:10] = dRa_dq * dt3
    F[:, 3:6, 10:13] = -R_nb * dt3
    F[:, 6:10, 6:10] = Phi_q
    F[:, 6:10, 13:16] = -dq_dw
    G = torch.zeros(B, N_STATES, 12, dtype=DTYPE, device=x.device)
    G[:, 3:6, 0:3] = -R_nb
    G[:, 6:10, 3:6] = -0.5 * Xi
    G[:, 10:13, 6:9] = S.I3
    G[:, 13:16, 9:12] = S.I3
    Q = ((G * Q_c.unsqueeze(1)) @ G.transpose(1, 2)) * dt3

    x_new = torch.cat([p + v * dt + 0.5 * acc_nav * dt * dt, v + acc_nav * dt,
                       (Phi_q @ q.unsqueeze(2)).squeeze(2), b_a, b_g], dim=1)
    P_new = F @ P @ F.transpose(1, 2) + Q
    return _normalize(S, x_new, P_new)


def update(S, x, P, z, R, has_fix, t_now, t_last, gate, p_fix=None, extra_ok=None):
    """Joseph-form GPS update (filterpy's), applied where has_fix and, with gate="fix", the fix lies within
    GATE_VMAX * (t_now - t_last) + GATE_MARGIN of the last accepted fix p_fix (horizontal). extra_ok (B,): a
    further plausibility test (the jump gate; False = reject). Returns x, P, t_last, p_fix and a dict with this
    update's innovation, NIS and masks."""
    ch = S.ch
    B = x.shape[0]
    PHT = P.index_select(2, ch)
    Sm = PHT.index_select(1, ch) + torch.diag_embed(R)
    SI, info = torch.linalg.inv_ex(Sm)
    K = PHT @ SI
    y = z - x.index_select(1, ch)
    x_new = x + (K @ y.unsqueeze(2)).squeeze(2)
    KH = torch.zeros(B, N_STATES, N_STATES, dtype=DTYPE, device=x.device)
    KH[:, :, ch] = K
    I_KH = S.I16 - KH
    P_new = I_KH @ P @ I_KH.transpose(1, 2) + (K * R.unsqueeze(1)) @ K.transpose(1, 2)
    x_new, P_new = _normalize(S, x_new, P_new)
    nis = ((y.unsqueeze(1) @ SI) @ y.unsqueeze(2)).view(-1)

    use = has_fix & (info == 0)
    rejected = torch.zeros_like(has_fix)
    if gate == "fix":
        d = torch.linalg.vector_norm(z[:, 0:2] - p_fix, dim=1)
        plausible = d <= S.gate_vmax * (t_now - t_last) + C.GATE_MARGIN
        rejected = has_fix & ~plausible
        use = use & plausible
    if extra_ok is not None:
        rejected = rejected | (has_fix & ~extra_ok)
        use = use & extra_ok
    x = torch.where(use.view(B, 1), x_new, x)
    P = torch.where(use.view(B, 1, 1), P_new, P)
    t_last = torch.where(use, t_now, t_last)
    if p_fix is not None:
        p_fix = torch.where(use.view(B, 1), z[:, 0:2], p_fix)
    return x, P, t_last, p_fix, {"y": y, "nis": nis, "used": use, "rejected": rejected}


def rollout(S, s0, x, P, n_steps, log_q, log_r, policy=None, gate=False, decide_every=1, keep_nis=False,
            z_drop=None, t_last0=None, p_fix0=None, keep_innov=False, z_jump=None, jump_max=None):
    """Run B filters from their own start steps s0 (B,) for n_steps IMU predictions.

    log_q (B x 4), log_r (B x 3): the base noise in log10. With a policy (callable () -> (dlog_q, dlog_r)),
    the noise in force is base + delta, decided every decide_every steps; a policy with a jump_max attribute
    also sets the jump gate's limit then. z_drop (B x n_steps) hides the fixes of a step (the score's
    simulated dropouts). t_last0 / p_fix0 continue the gate's memory (time and position of the last accepted
    fix) from an earlier rollout, so a run can be split into pieces without the gate noticing. keep_innov
    logs, for every fix, the horizontal innovation |z - H x_pred| before the update, used or not. z_jump
    ((n-1) x U, one value per fix slot) and jump_max (B,): a fix is also rejected when z_jump > jump_max.

    Returns a dict with pos (n_steps+1, B, 3), failed (B), nis_sum, n_upd, n_rej (B), the final x, P, t_last,
    p_fix, the Q/R in force (with a policy) and optionally every update's NIS and innovation.
    """
    dev = S.device
    B = x.shape[0]
    s0 = torch.as_tensor(s0, device=dev).long().view(B)
    t_last = S.t[s0].clone() if t_last0 is None else t_last0.clone()
    p_fix = x[:, 0:2].detach().clone() if p_fix0 is None else p_fix0.clone()
    innov_log, nis_log, qr_log = [], [], []
    failed = torch.zeros(B, dtype=torch.bool, device=dev)
    nis_sum = torch.zeros(B, dtype=DTYPE, device=dev)
    n_upd = torch.zeros(B, dtype=DTYPE, device=dev)
    n_rej = torch.zeros(B, dtype=DTYPE, device=dev)
    pos = [x[:, 0:3]]
    lq, lr = log_q, log_r
    Q_c, R = q_r_from_log(lq, lr, S.ch)
    for i in range(n_steps):
        if policy is not None and i % decide_every == 0:
            dq, dr = policy()
            lq, lr = log_q + dq, log_r + dr
            Q_c, R = q_r_from_log(lq, lr, S.ch)
            if getattr(policy, "jump_max", None) is not None:
                jump_max = policy.jump_max
        if policy is not None:
            qr_log.append(torch.cat([lq, lr], dim=1).detach())
        s = s0 + i
        x, P = predict(S, x, P, S.a[s], S.w[s], S.dt[s], Q_c)
        for u in range(S.U):
            has = S.zm[s, u]
            if z_drop is not None:
                has = has & ~z_drop[:, i]
            if not bool(has.any()):
                continue
            t_now = S.zt[s, u]
            ok = None if z_jump is None or jump_max is None else z_jump[s, u] <= jump_max
            x, P, t_last, p_fix, up = update(S, x, P, S.z[s, u], R, has & ~failed, t_now, t_last, gate, p_fix,
                                             extra_ok=ok)
            used = up["used"]
            nis_sum = nis_sum + torch.where(used, up["nis"], torch.zeros_like(nis_sum))
            n_upd = n_upd + used.to(DTYPE)
            n_rej = n_rej + up["rejected"].to(DTYPE)
            if keep_nis:
                nis_log.append((S.zt[s, u].detach(), up["nis"].detach(), used))
            if keep_innov:
                innov_log.append((S.zt[s, u].detach(),
                                  torch.linalg.vector_norm(up["y"][:, 0:2], dim=1).detach(), has & ~failed))
        bad = ~torch.isfinite(x).all(dim=1) | (x[:, 0:3].abs().amax(dim=1) > MAX_POSITION)
        failed = failed | bad
        pos.append(x[:, 0:3])
    out = {"pos": torch.stack(pos), "failed": failed, "nis_sum": nis_sum, "n_upd": n_upd, "n_rej": n_rej,
           "x": x, "P": P, "t_last": t_last, "p_fix": p_fix}
    if keep_innov:
        out["innov_log"] = innov_log
    if keep_nis:
        out["nis_log"] = nis_log
    if qr_log:
        out["qr"] = torch.stack(qr_log, dim=1)                 # B x n_steps x 7 (log10 Q4, R3)
    return out


def base_logs(theta, B, device):
    """log_q (B x 4), log_r (B x 3) tensors from a 7-vector theta (ekf.tuning layout), or B x 7 thetas."""
    th = torch.as_tensor(np.asarray(theta, dtype=float), dtype=DTYPE, device=device)
    th = th.expand(B, -1) if th.dim() == 1 else th
    return th[:, :4].contiguous(), th[:, 4:7].contiguous()


def check_against_reference(data, theta, n_steps=3000, device="cpu"):
    """Largest position difference (m) between this filter and ekf.filter.run_ekf over n_steps, gate off;
    returns (difference, mean NIS of the reference, mean NIS of this filter)."""
    from ekf.filter import OPTIONS, run_ekf
    from ekf.tuning import theta_to_QR
    seg = {k: v for k, v in data.items()}
    t_end = data["t_imu"][n_steps]
    old = dict(OPTIONS)
    OPTIONS.update(plausibility=False, gate=False)
    try:
        Q_c, R = theta_to_QR(theta)
        x_log, _, mean_nis, ok, _ = run_ekf(seg, Q_c, R, t_end=t_end)
    finally:
        OPTIONS.update(old)
    S = Stream(seg, device)
    lq, lr = base_logs(theta, 1, S.device)
    with torch.no_grad():
        out = rollout(S, [0], S.x0.unsqueeze(0).clone(), S.P0.unsqueeze(0).clone(), len(x_log) - 1, lq, lr)
    pos = out["pos"][:, 0].cpu().numpy()
    diff = np.abs(pos - x_log[:, 0:3]).max()
    return float(diff), float(mean_nis), float((out["nis_sum"] / out["n_upd"]).item())
