"""Proposers for the library search: the LLM (OPRO-style: it sees the scored history and proposes new
settings), and matched-budget baselines without language: uniform random search and the Grey Wolf Optimizer
(paper 1's best metaheuristic; differential evolution is kept as an option). All propose K settings per
round; the caller scores them with the GPS-only score."""
import json
import re
import time

import numpy as np

from . import config as C
from . import llm

SYSTEM = ("You are an expert in Kalman filter tuning for GPS/IMU navigation. You propose noise settings for an "
          "extended Kalman filter, see how they score, and propose better ones. First reason briefly (at most four "
          "sentences) about what the GPS condition and the scores imply, then give the JSON.")


def _fmt(theta, free):
    return "[" + ", ".join(f"{v:.2f}" for v in np.asarray(theta)[free]) + "]"


def _jitter_unique(cands, tried, info, rng, tol=0.05):
    out = []
    for c in cands:
        c = info["clip"](c)
        for _ in range(5):
            if all(np.abs((c - t)[info["free"]]).max() > tol for t in tried + out):
                break
            c = info["clip"](c + rng.normal(0, 0.15, len(c)) * info["free"])
        out.append(c)
    return out


class RandomProposer:
    name = "random"

    def propose(self, history, K, info, rng):
        lo, hi = info["lo"], info["hi"]
        c = [info["clip"](rng.uniform(lo, hi)) for _ in range(K)]
        return np.array(c), {}


class DEProposer:
    """DE/rand/1/bin, F = 0.7, CR = 0.9, population K, greedy selection (the D:\\EKF benchmark's settings)."""
    name = "de"

    def __init__(self):
        self.pop, self.trials = None, None

    def propose(self, history, K, info, rng):
        if self.pop is None:
            best = sorted(history, key=lambda h: h["score"])[:K]
            self.pop = [(h["theta"], h["score"]) for h in best]
            while len(self.pop) < K:
                th = info["clip"](rng.uniform(info["lo"], info["hi"]))
                self.pop.append((th, np.inf))              # unevaluated: any trial replaces it
        elif self.trials is not None:
            scored = history[-len(self.trials):]
            for i, h in enumerate(scored):
                if h["score"] <= self.pop[i][1]:
                    self.pop[i] = (h["theta"], h["score"])
        free = info["free"]
        trials = []
        for i in range(K):
            others = [j for j in range(K) if j != i]
            a, b, c = rng.choice(others, 3, replace=len(others) < 3)      # K < 4 only in smoke runs
            mutant = self.pop[a][0] + 0.7 * (self.pop[b][0] - self.pop[c][0])
            cross = (rng.random(len(mutant)) < 0.9) | (np.arange(len(mutant)) == rng.choice(np.flatnonzero(free)))
            trials.append(info["clip"](np.where(cross & free, mutant, self.pop[i][0])))
        self.trials = trials
        return np.array(trials), {}


class GWOProposer:
    """Grey Wolf Optimizer as in paper 1 (D:\\EKF\\GWO.py, the best of GA / PSO / DE / GWO there): alpha, beta
    and delta are the three best wolves of the current pack, every wolf moves to the mean of its three
    encircling steps L - A |C L - w| (A = 2 a r1 - a, C = 2 r2), and a falls linearly from 2 to 0 over the
    search's rounds. The pack (K wolves, matched budget; paper 1 used 100) starts from the best settings
    scored so far (the seeds, THETA0 included) filled with uniform random wolves; only scored wolves lead."""
    name = "gwo"

    def __init__(self):
        self.pack, self.costs, self.gen = None, None, 0

    def propose(self, history, K, info, rng):
        if self.pack is None:
            best = sorted(history, key=lambda h: h["score"])[:K]
            self.pack = [np.asarray(h["theta"], dtype=float) for h in best]
            self.costs = [h["score"] for h in best]
            while len(self.pack) < K:
                self.pack.append(info["clip"](rng.uniform(info["lo"], info["hi"])))
                self.costs.append(np.inf)                  # not scored yet: moves, but cannot lead
        else:
            scored = history[-K:]                          # the pack moved last round; these are its scores
            self.pack = [np.asarray(h["theta"], dtype=float) for h in scored]
            self.costs = [h["score"] for h in scored]
        self.gen += 1
        a = max(0.0, 2.0 * (1.0 - self.gen / (info.get("rounds", C.BUILD_ROUNDS) + 1)))
        wolves, costs = np.array(self.pack), np.array(self.costs)
        order = [i for i in np.argsort(costs) if np.isfinite(costs[i])] or [0]
        leaders = wolves[(order * 3)[:3]]                 # fewer than three scored: the best leads twice
        new = []
        for w in wolves:
            steps = []
            for lead in leaders:
                A = 2.0 * a * rng.random(w.size) - a
                Cc = 2.0 * rng.random(w.size)
                steps.append(lead - A * np.abs(Cc * lead - w))
            new.append(info["clip"](np.mean(steps, axis=0)))
        return np.array(new), {}


class LLMProposer:
    name = "llm"

    def __init__(self):
        self.calls = 0

    def prompt(self, history, K, info):
        free = info["free"]
        names = [n for n, f in zip(C.PARAM_NAMES, free) if f]
        lines = [f"- {n}: {m}, default {d:.2f}, allowed [{lo:.2f}, {hi:.2f}]"
                 for n, m, d, lo, hi, f in zip(C.PARAM_NAMES, C.PARAM_MEANING, info["theta0"], info["lo"],
                                               info["hi"], free) if f]
        vel = "with" if info["has_vel"] else "without"
        best = sorted(history, key=lambda h: h["score"])[:C.LLM_HISTORY]
        tried = "\n".join(json.dumps({"setting": json.loads(_fmt(h["theta"], free)),
                                      "score": (round(float(h["score"]), 3) if np.isfinite(h["score"])
                                                else "diverged")}) for h in best)
        lib = ""
        if info.get("library"):
            lib = "Settings already chosen for other GPS conditions of this drive:\n" + "\n".join(
                f"- {lab} (GPS noise ~{e['sigma_h']:.1f} m): {_fmt(e['theta'], free)}, score {e['score']:.3f}"
                for lab, e in info["library"].items()) + "\n\n"
        return (
            f"Filter: 16-state GPS/IMU EKF, {info['imu_hz']:.0f} Hz IMU, {info['gps_hz']:.1f} Hz GPS {vel} "
            f"velocity. Parameters are log10 of variances or PSDs, not of standard deviations: log_r_xy = "
            f"log10(sigma_axis^2), with sigma_axis = sigma_h / sqrt(2) for white GPS noise (e.g. log_r_xy = 1.0 "
            f"means sigma_axis = 3.2 m, 2.0 means 10 m). In this order {names}:\n" + "\n".join(lines) + "\n\n"
            f"GPS condition to tune for: {info['label']}. Estimated horizontal GPS white noise sigma_h = "
            f"{info['sigma_h']:.2f} m (2-axis standard deviation; this receiver's normal level: "
            f"{info['sigma_nominal']:.2f} m). The estimate sees only the fix-to-fix (white) part of the GPS "
            f"error, not slowly varying errors.\n\n" + lib +
            f"Score: RMS in metres of the filter's prediction error against each new GPS fix, over "
            f"{info['n_windows']} window(s) of {info['window_s']:.0f} s in this condition. Lower is better.\n\n"
            f"Tried so far (best first):\n{tried}\n\n"
            f"Propose {K} new settings, each different from those tried, that you expect to score lower than the "
            f"best. Mix small refinements of the best with a few bolder moves. After your sentence, give JSON: "
            f'{{"settings": [[{", ".join(names)}], ...]}} with {len(names)} numbers per setting.')

    def propose(self, history, K, info, rng):
        free = info["free"]
        nf = int(free.sum())
        user = self.prompt(history, K, info)
        num = r"-?\d+(?:\.\d+)?"
        pat = re.compile(r"\[\s*" + r"\s*,\s*".join([num] * nf) + r"\s*\]")
        t0 = time.time()
        text, n_in, n_out = llm.chat(SYSTEM, user, seed=int(rng.integers(1 << 31)),
                                     done=lambda s: len(pat.findall(s)) >= K)
        seconds = time.time() - t0
        self.calls += 1
        parsed = []
        for m in pat.finditer(text):
            v = np.array([float(x) for x in re.findall(num, m.group(0))])
            th = info["theta0"].copy()
            th[free] = v
            parsed.append(th)
        parsed = parsed[:K]
        n_parsed = len(parsed)
        best = min(history, key=lambda h: h["score"])["theta"]
        while len(parsed) < K:                                 # unusable reply: fill near the best
            parsed.append(best + rng.normal(0, 0.3, len(best)) * free)
        tried = [h["theta"] for h in history]
        c = _jitter_unique(parsed, tried, info, rng)
        return np.array(c), {"prompt": user, "reply": text, "n_parsed": n_parsed, "n_filled": K - n_parsed,
                             "tokens_in": n_in, "tokens_out": n_out, "seconds": seconds}


def make(name):
    return {"llm": LLMProposer, "random": RandomProposer, "gwo": GWOProposer, "de": DEProposer}[name]()
