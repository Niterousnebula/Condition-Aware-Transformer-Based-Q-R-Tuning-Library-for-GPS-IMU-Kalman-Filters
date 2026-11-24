# Condition-Aware Transformer-Based Q/R Tuning Library for GPS-IMU Kalman Filters

A GPS-IMU Extended Kalman Filter is only as good as its noise covariances, and the right covariances depend
on the GPS: what suits clean fixes fails under heavy noise and the other way round. One offline-tuned setting
has to compromise across every condition a vehicle drives through, and tuning it needs ground truth.

This repository is the code for a filter that tunes itself while it drives. It keeps a **library of Q/R
settings, one per GPS condition** (normal, moderate noise, heavy noise, recovery after an outage), recognises
the current condition from the GPS fixes alone, and switches between entries online. A **pretrained
transformer language model** proposes the settings, and each proposal is judged by a **GPS-only score**, so
neither building nor switching ever sees ground truth. The library is built causally from the start of the
drive (initialization mode) and extended whenever an unseen condition appears (online update). Random search
and the Grey Wolf Optimizer, the strongest optimizer in our earlier study [1], are the matched-budget
baselines without language.

## Relation to the preprint

This work builds on our preprint *Joint Tuning of Q and R in a GPS-IMU EKF* [1], which tuned Q and R jointly
and offline for the same 16-state filter, on the same three drives, with GA, PSO, DE and GWO against
ground truth, and found GWO the strongest of the four. That setting leaves three questions open, which this
paper answers:

| Preprint [1] | This paper |
|---|---|
| One Q/R for the whole drive | One Q/R per GPS condition, switched online |
| Tuned against ground truth | Tuned on GPS alone (self-supervised score) |
| Offline, on the complete recording | Causal: built while driving, from the drive start |
| Metaheuristic optimizers | A transformer language model as the optimizer, against random search and GWO |

Reused from [1]: the EKF (`ekf/`: filterpy reference and batched GPU filter, the per-drive starting values
`THETA0`, data loading), the three drives with their degraded GPS sections (`processed_data/`), GWO, and
[1]'s ground-truth-tuned GWO settings, which serve as a reference row in every table.

## Contributions

1. **A condition-aware Q/R library** for a GPS-IMU EKF, with a GPS-only condition detector and a
   plausibility filter that keeps the switch from corrupting the filter state at the onset of noise.
2. **A self-supervised score** for Q/R settings: prediction error against incoming GPS fixes, with simulated
   GPS dropouts so that it also measures coasting on the IMU. Validated against ground truth.
3. **Causal construction**: an initialization mode that builds the library from the drive start and an online
   update for unseen conditions. No offline phase and no ground truth.
4. **A transformer language model as the Q/R optimizer**, compared at equal evaluation budget with random
   search and the preprint's GWO, with three seeds, ablations of every component, and the preprint's
   ground-truth-tuned settings as a reference.

## Method

```
GPS fixes -> condition detector (+ jump trigger) -> Q/R library -> EKF (Q/R in force, jump gate) -> position
                 LLM / random / GWO builder  <->  GPS-only score (with simulated dropouts)
```

**Filter and parameters.** The 16-state EKF of [1] (position, velocity, attitude quaternion, accelerometer
and gyroscope biases), with a Joseph-form GPS update and a displacement plausibility gate (a fix is used only
if it lies within 6 m/s x dt + 25 m of the last accepted fix). A Q/R setting is seven log10 values:
accelerometer and gyroscope white-noise PSDs, their bias random walks, and the GPS horizontal, vertical and
velocity variances. R, which models the GPS, is searched over THETA0 +- 3 decades; Q, which models the IMU and
does not change with the GPS, over +- 1 decade (see the coasting check below). The batched filter
(`qrlib/aekf.py`) runs many settings at once and matches the filterpy reference to 1.4e-14 m.

**GPS condition detector** (`qrlib/data.py`). Every second, from the fixes received so far: *outage* (no fix
for max(2 s, 5 intervals)), *recovery* (the first 30 s after an outage), otherwise a noise level sigma_h,
a robust (MAD) estimate of the fixes' white noise over the last 15 s, binned as *nominal* (< 2.5 m),
*moderate* (< 8 m), *heavy* (< 25 m) or *extreme*, with 20 % hysteresis at the bin edges. A cleaner condition
must hold for 2 s before the library switches back.

**Plausibility filter.** A setting that trusts clean GPS would fuse the first fixes of a noise onset before
any window-based detector can react, and the state errors they cause outlast the switch. Each fix's *jump*,
its distance from the straight line through the two fixes before it (GPS only, known on arrival), drives two
rules:
- *Jump gate*: under nominal or moderate GPS, a fix that jumps more than the condition's bin edge is not
  fused. Heavy and extreme conditions are not gated; their settings already weight GPS lightly.
- *Jump trigger*: when at least 4 of the last 7 fixes jump beyond a noisier bin's edge, the library switches
  to that bin at once (up to heavy; extreme is left to the 15 s window).

**Library lookup.** The entry for the detected condition is used. A noise condition without an entry takes the
nearest cleaner entry with its R raised to at least THETA0's, so an unseen, noisier condition never trusts
GPS more than a cleaner one or the default; otherwise the nearest noisier entry.

**GPS-only score** (`qrlib/runner.py`). A candidate is run on the condition's 30 s windows, starting from the
running filter's state, and scored by the RMS of |GPS fix - predicted position| over the windows' fixes. For
white GPS noise, E|z - p_pred|^2 = E|p - p_pred|^2 + sigma^2, so the score ranks candidates as their true
prediction error would. One-step predictions say little about Q, which mainly governs how the filter coasts
without GPS, so in every window the fixes from 5 to 10 s into each 15 s are hidden and the first fix after
each gap measures the coasting error.

**Builders** (`qrlib/propose.py`, `qrlib/build.py`). Each proposes 8 settings per round, seeded with THETA0
and the library's existing entries:
- *LLM*: Qwen3.5-9B (Q4_K_M, llama.cpp server, hidden reasoning off, temperature 0.8) in an OPRO-style
  prompt: the filter, each parameter's meaning, units and bounds, the detected condition and its sigma_h, the
  entries for other conditions and the scored history; it reasons briefly and replies in JSON (an unusable
  reply is filled near the best setting and counted).
- *Random search*: uniform over the bounds.
- *GWO*: the preprint's Grey Wolf Optimizer (alpha, beta, delta leaders; a from 2 to 0 over the rounds),
  with a pack of 8 started from the scored seeds plus uniform random wolves.

**Initialization mode** (drive start to the end of the training part). The filter starts on THETA0 and follows
the library as it grows. Each time a condition completes a new 30 s window (up to its first 6), its entry is
re-tuned on its windows so far (2 rounds of 8), from the running filter's own states, and used from then on.

**Operation mode.** The library switches with the detected condition. A noise condition without an entry, or a
recovery, that lasts 20 s gets one: 3 rounds of 8 on those 20 s. Outages have no fixes to score and get no
entry.

## Experimental protocol

**Data.** The three drives of [1], each with three degraded GPS sections at 25, 50 and 75 % of the path: about
5 m of added white noise, about 15 m, and a complete outage. ETH Zurich (10 Hz IMU, 5 Hz GPS with velocity)
and iNav-WHU playground00 and street00 (200 Hz ADIS IMU, 1 Hz GPS, position only).

**Split.** Each drive is one continuous run, split midway between the 5 m and the 15 m section. The first part
(normal GPS and the 5 m section) is the initialization period; the second part (normal GPS, the 15 m section
and the outage), which the library has never seen, is the test.

**Methods on the test part.** Raw GPS; THETA0; the preprint's ground-truth-tuned GWO setting [1] (a
reference: tuned offline on the whole drive with truth); and for each builder: a static setting (one setting
tuned on the whole initialization period, the usual approach) and the library with online update.

**Ablations.** Within every run: without the online update, without the plausibility filter, and with the true
condition in place of the detector (its upper bound). As separate runs (LLM, seed 0): the library built
offline after the initialization period, the one-step score without dropouts, and Q searched over +- 3
decades.

**Metrics.** Horizontal RMSE in the 15 m section, on normal GPS, in the 30 s after the outage, and during the
outage (reported separately: no Q/R setting stops IMU drift without fixes); NIS/dof; the error during the
initialization period against THETA0; detector agreement and onset delay; LLM calls, tokens and time.
Three seeds per builder (each seed re-runs every search, LLM sampling included); mean +- std.

## Validation of the design

Ground truth is used here only to check design choices, never to build or switch.

**The GPS-only score ranks R like the truth** (`python -m qrlib.score_check`). A grid of R settings on each
noise section, from the THETA0 state at the section start; Spearman correlation between score and true RMSE,
and the true RMSE of the score's pick against the best setting and THETA0:

| Drive | Section | Spearman (one-step / with dropouts) | True RMSE (m): pick with dropouts / best / THETA0 |
|---|---|---:|---|
| ETH | 5 m | 0.99 / 0.82 | 3.10 / 3.10 / 3.12 |
| ETH | 15 m | 0.88 / 0.73 | 3.37 / 3.21 / 4.60 |
| iNav playground | 5 m | 0.95 / 0.95 | 1.84 / 1.76 / 2.81 |
| iNav playground | 15 m | 1.00 / 1.00 | 6.19 / 6.19 / 11.79 |
| iNav street | 5 m | 0.98 / 0.98 | 1.84 / 1.79 / 2.81 |
| iNav street | 15 m | 1.00 / 1.00 | 6.45 / 6.45 / 10.95 |

On ETH the best settings trust the GPS velocity more; on iNav-WHU, without GPS velocity, they raise the
horizontal GPS variance by about three decades, which is why R spans +- 3 decades.

**Coasting and the Q range.** On normal-GPS windows, 47 random settings and THETA0, each also run for 30 s
without GPS. Narrowing Q to +- 1 decade bounds how badly any setting can coast, and the dropout score ranks
that drift on two of the three drives:

| Drive | Worst 30 s drift, Q +- 3 / +- 1 | Spearman(score, drift), one-step / with dropouts |
|---|---:|---:|
| ETH | 788 / 583 m | -0.11 / +0.30 |
| iNav playground | 37 / 12 m | +0.59 / +0.76 |
| iNav street | 35 / 16 m | -0.69 / -0.52 |

**Detector.** It agrees with the true condition 97-99 % of the time and recognises a noise section 1-2 s after
it starts on ETH (5 Hz GPS) and 4-7 s on iNav-WHU (1 Hz), against 10-14 s for the 15 s window alone.

**Switching.** With the one-step score check's settings in the library (THETA0 for normal GPS, its 5 m and 15 m
picks), horizontal RMSE in the 15 m section:

| Drive | THETA0 | Library, no plausibility filter | Library, detected condition | Library, true condition | 15 m setting from the section start |
|---|---:|---:|---:|---:|---:|
| ETH | 4.58 | 3.63 | 3.49 | 3.54 | 3.49 |
| iNav playground | 11.78 | 32.56 | 6.21 | 6.19 | 6.19 |
| iNav street | 10.93 | 7.59 | 6.44 | 6.44 | 6.45 |

With the plausibility filter, switching on the detected condition matches switching on the true condition and
applying the 15 m setting exactly from the section start.

## Reproducing

```powershell
# 1. the LLM, in its own terminal (an 8 GB GPU is enough)
cd D:\llama-b9754-bin-win-cuda-13.3-x64; .\llama-server.exe -m "D:\Modelfile\Qwen_Qwen3.5-9B-Q4_K_M.gguf" --alias qwen35-9b -c 4096 --port 8070
# 2. in another terminal, from this folder
pip install -r requirements.txt
python main.py                 # everything: score check, 3 seeds, ablations, tables and figures (~9 h)
python main.py --plan          # what is done, what is left, rough time; runs nothing
python main.py --plots-only    # rebuild the tables and figures
python main.py --smoke         # a few-minute pipeline check (ETH, random search and GWO, no LLM)
python reset.py                # delete the results (lists them, then asks; --smoke, --all, --yes)
```

`main.py` runs each step in its own process and resumes after an interruption (a finished seed and drive is
skipped); a failed step is logged and the remaining steps still run; an LLM call that fails is retried and
then counted as an empty reply. Log: `results/qrlib/main.log`; sessions: `results/qrlib/main_manifest.json`.
The steps, also usable on their own:

```bash
python -m qrlib.score_check                          # score vs ground truth (R grid, coasting)
python -m qrlib --seeds 0 1 2                        # main run -> results/qrlib/seed_<s>/<drive>/
python -m qrlib --seeds 0 --builders llm --offline   # ablation -> results/qrlib_offline/
python -m qrlib --seeds 0 --builders llm --onestep   # ablation -> results/qrlib_onestep/
python -m qrlib --seeds 0 --builders llm --wide-q    # ablation -> results/qrlib_wideq/
python -m qrlib.report                               # tables and figures -> results/qrlib/paper/
```

**Outputs** (`results/qrlib/paper/`): tables (main, ablations, initialization period, LLM cost, detector) as
Markdown and LaTeX, mean +- std over seeds; figures as PNG and PDF, with `captions.md`:

| Figure | Shows |
|---|---|
| fig1_pipeline | The system |
| fig2_detector | Estimated GPS noise and detected condition against the true sections |
| fig3_onset | Error at the onset of the 15 m section, with and without the plausibility filter |
| fig4_test_error | Error over the test part: THETA0, the preprint's GWO setting, the library |
| fig5_score_check | GPS-only score against true error (R grid) and against coasting drift |
| fig6_library | The library's horizontal GPS variance per condition, per builder and seed |
| fig7_initialization | Error during the initialization period against THETA0, with the re-tunings |
| fig8_headline | RMSE per drive and method, mean and std over seeds |

GPS sections are shaded 50 % wider than they are (centred) so that they remain visible at the scale of a
whole drive. Builders keep one colour throughout (LLM blue, random search orange, GWO aqua; colour-vision
checked); references are drawn in neutral inks with their own dash patterns.

## Repository layout

| Path | Holds |
|---|---|
| `main.py` | The whole experiment in one resumable command |
| `reset.py` | Deletes generated results |
| `qrlib/config.py` | Every setting, with the reason for its value |
| `qrlib/aekf.py` | The batched EKF: per-decision Q/R, per-element start, displacement and jump gates, simulated dropouts |
| `qrlib/data.py` | Drives, split, condition detector, jump trigger and gate limits |
| `qrlib/runner.py` | Checkpoints, the GPS-only score, the switching policy, library lookup |
| `qrlib/propose.py` | Builders: LLM, random search, GWO (and DE) |
| `qrlib/llm.py` | The llama-server client |
| `qrlib/build.py` | Initialization mode, offline build (ablation), static entry, the search loop |
| `qrlib/evaluate.py` | One drive end to end: every method, metrics, traces |
| `qrlib/score_check.py` | The score against ground truth |
| `qrlib/report.py` | Tables and figures |
| `ekf/` | The preprint's EKF, unchanged |
| `processed_data/` | The three drives with their degraded GPS sections |
| `research/research_map.md` | Literature map and research gaps |

## Results

After `python main.py`: `results/qrlib/paper/tables/all.md` and `results/qrlib/paper/figures/`.

## Limitations

- **Normal GPS cannot reveal every outage behaviour.** On iNav-WHU street the settings that track best on
  normal GPS drift most once GPS is lost (Spearman -0.52 between the dropout score and 30 s drift). A
  GPS-only score sees coasting only over its short simulated gaps.
- **Q/R cannot stop drift during an outage.** Without fixes the position follows the IMU; on ETH (10 Hz
  IMU) the error grows to kilometres over the 82 s outage for every setting. Outage RMSE is reported apart
  from the headline metrics.
- **Degradation is synthetic.** The noise sections add white noise to real GPS; multipath and slowly varying
  errors in real urban GPS are not modelled.
- **Scope.** Three drives, one language model (Qwen3.5-9B, quantised), and one bin structure for conditions.

## References

[1] A. Verma, R. Anthwal, A. Deka, S. Shokeen (supervisor: V. Agarwal), *Joint Tuning of Q and R in a
GPS-IMU EKF*, preprint, Netaji Subhas University of Technology. Code:
https://github.com/Niterousnebula/Joint-Tuning-of-QR-Matricies-in-GPS-IMU-EKF. <!-- add the preprint link -->
