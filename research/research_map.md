# Research map: tuning Q/R for GNSS/INS Kalman filters (Nov 2026)

Built from web searches and from our own experiments in this repo. Papers were found through search
summaries and abstracts, not read in full; several are 2025-26 preprints. Check every citation before use.

## 1. The space, cell by cell

| # | Family | What it does | Representative work | How crowded |
|---|---|---|---|---|
| A1 | Offline metaheuristic tuning | GA / PSO / hybrids find one static Q/R | hybrid PSO-GA for INS/GNSS Q [1]; PSO for GPS KF covariance [2]; PSO-tuned UKF Q/R [3]; GA noted in [4] | active, almost always one static setting |
| A2 | Offline Bayesian optimisation | GP / Student-t surrogate on NEES/NIS cost | "Weak in the NEES?" [5], journal version [6]; mean NIS is not enough, match the chi-square distribution [7] | small, mature |
| A3 | Offline gradient tuning | backprop through a differentiable filter | "How to train your differentiable filter" [8] | mature in robotics |
| B | Classical online adaptive | covariance matching, Sage-Husa, variational Bayes, IMM/MMAE, robust Huber | decoupled VB-AKF for MEMS INS/GNSS [9]; RBF-aided robust adaptive [10] | very mature; the baselines reviewers expect |
| C | Context-aware navigation | detect environment (open sky / urban / canyon / tunnel), then change rules or robust parameters | review [11]; Huber parameter per context [12]; scenario-aware dual-adaptive CKF [13]; kNN context classifier [14] | active; adaptations are rules or heuristics, not optimised parameter sets |
| D | Learned online Q/R | a network predicts Q and/or R every step | transformer + denoising AE for R [15]; linear-attention transformer [16]; multitask Q/R [17]; AI-IMU CNN [18]; sigma-Q/R nets [19]; RL for Q [20], RL parameter policies [21] | **crowded**: "transformer predicts R" is incremental |
| E | Learned gain | network replaces the Kalman gain | KalmanNet [22], Split-KalmanNet [23], Recursive KalmanNet [24]; survey [25] | **crowded** |
| F | Outage bridging | network predicts position increments while GNSS is lost | LSTM [26, 27], GRU [28], CNN-LSTM-attention [29], spiking transformer [30] | **crowded** |
| G | Offline search -> online learner | offline optimum trains an online adapter | GA -> neural Q adaptation (electro-pneumatic, not navigation) [31]; meta-learned KF parameters [32] | **sparse**, nothing found for GNSS/INS |
| H | LLMs | LLM designs or tunes | LLM + genetic programming discovers KF variants [33]; LLM-assisted evolution of update structure with Q/R [34]; LLM as optimiser (OPRO) [35]; LLM hyperparameter tuning [36]; budget-matched study: LLM gain came from its warm start [37] | **sparse**: no LLM Q/R tuner for navigation found |
| I | Evaluation practice | how learned tuners are tested | OOD on noise level / trajectory length / dynamics is common; leakage-free time splits not described; one same-dataset table with Sage-Husa and VB-AKF [38] | **sparse** |

Datasets: ETH (ours, 10 Hz consumer IMU, mild GPS); UrbanNav Hong Kong/Tokyo [39]: real urban canyons and a tunnel,
raw GNSS, NovAtel SPAN reference.

## 2. What our own experiments already show (ETH, contiguous 50/50 split)

- Raw GPS (3.41 m) beats every filter on nominal data; the room for Q/R tuning on ETH is small.
- Perfect per-window R choice would gain 9 % on the training half (3.94 -> 3.57 m): the per-condition optimum exists.
- Per-condition optima differ a lot: best R_xy +0.86 decades in noisy windows, -0.32 elsewhere.
- Every free-form learned tuner (transformer, LLM backbone, learned correction) improved on validation and lost
  on the test half. Only a lookup over pre-evaluated candidates held up (3.53 m vs 3.58 m baseline, not significant).
- A NIS-weighted search objective was satisfied by an unphysical state (+-10 rad/s gyro bias) that also faked the
  outage result. During an outage Q/R cannot change the drift at all (no updates); only the entry state and recovery.

## 3. Gaps, ranked

| Gap | Why it is open | Our evidence | Effort | Risk |
|---|---|---|---|---|
| **G1. Optimised context library.** Offline optimiser builds one Q/R/gate set per GNSS condition; the filter switches online from innovation statistics | A1/A2 give one static set; C switches rules, not optimised sets; G has no navigation work | per-condition optima differ; lookup was the only thing that generalised | medium | gain on ETH may be small: needs UrbanNav |
| **G2. LLM as the library builder,** at matched EKF-evaluation budget vs metaheuristic / BO | H has no Q/R tuner; [37] says the LLM's edge may just be its warm start, so that is the control to run | none yet | medium | needs a capable LLM (1.7B local is likely too weak for OPRO-style search) |
| **G3. Honest evaluation protocol.** Time-split, optimised static baseline, classical adaptive + IMM, raw GPS, block-bootstrap CIs, NEES/NIS distribution | I shows no leakage protocol and few same-dataset comparisons | our learned tuners flip from "better" to "worse" under it | low (mostly built) | alone it reads as a comparative study |
| **G4. Objective gaming.** NIS-led objectives accept unphysical states; bound the search, score on RMSE, test consistency separately | [7] covers the mean-NIS weakness, not unphysical states | the HISA gyro-bias finding | low | a section, not a paper |

Not worth the headline: transformer/LLM predicting R (D), KalmanNet variants (E), outage bridging networks (F),
RL tuning (exists in [20, 21]).

## 4. Recommended paper (G1 core, G2 as the LLM contribution, G3 as the protocol, G4 as a finding)

Working title: *Offline-optimised context libraries for adaptive GNSS/INS filtering: metaheuristic vs LLM-built
parameter sets with innovation-driven switching.*

Claim to test: switching among per-condition optimised Q/R sets beats (a) one optimised static set, (b) Sage-Husa
and VB adaptive R, and (c) IMM over the same library, under a leakage-free split; and an LLM proposer builds that
library with fewer EKF evaluations than a metaheuristic (or does not, beyond its warm start).

Experiments, in order (each one gates the next):
1. **Go/no-go (minutes, CPU):** oracle switching (true condition known) between per-condition best R vs one static R,
   on ETH's test-half noise scenario. If the oracle does not win, stop here.
2. Library: conditions = nominal, noise levels, outlier rate, partial dropout, post-outage recovery; bounded search
   (physical bias limits, RMSE-led score) with DE/CMA-ES and BO.
3. Online switching: innovation-statistics rule with hysteresis, kNN (existing lookup code), small classifier.
4. Baselines: static optimum, Sage-Husa, VB-AKF, IMM over the library, oracle, raw GPS.
5. Second dataset: UrbanNav (needs a loader and a GNSS position solution from its raw data; check what it ships).
6. LLM proposer at matched budget, with a warm-start-only control.

Reusable from this repo: batched GPU EKF, scenario injection (label_test), displacement gate, lookup/kNN selector,
evaluation tables, block-bootstrap comparisons (hisa_effect).

Possible SCIE venues (check current indexing and scope): IEEE Sensors Journal, Sensors, Remote Sensing,
IEEE Access, Measurement, GPS Solutions.

## Sources

1. [Hybrid PSO-GA process noise tuning, INS/GNSS](https://journals.modares.ac.ir/article_28006.html)
2. [PSO tuning of GPS Kalman filter covariance (2008)](https://link.springer.com/chapter/10.1007/978-3-540-87442-3_29)
3. [PSO-tuned UKF for inertial-GPS fusion](https://arxiv.org/abs/2601.01578v1)
4. [Kalman filter tuning for direct and indirect INS/GNSS (Sensors 2024)](https://www.mdpi.com/1424-8220/24/22/7331)
5. [Weak in the NEES?](https://arxiv.org/pdf/1807.08855)
6. [Kalman filter tuning with Bayesian optimization](https://arxiv.org/pdf/1912.08601)
7. [KF auto-tuning by enforcing chi-squared distributions](https://arxiv.org/pdf/2306.07225)
8. [How to train your differentiable filter](https://arxiv.org/pdf/2012.14313)
9. [Decoupled VB adaptive KF for MEMS INS/GNSS](https://pmc.ncbi.nlm.nih.gov/articles/PMC13766212)
10. [RBF-aided robust adaptive GNSS/INS in urban areas](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12694146/)
11. [Review of environmental context detection for navigation](https://doi.org/10.3390/s20164532)
12. [Adaptive robust-statistics GNSS navigation with context detection](https://www.researchgate.net/publication/368495547_Adaptive_Robust-Statistics_GNSS_Navigation_Based_on_Environmental_Context_Detection)
13. [Dual-adaptive cubature KF for degraded urban GNSS](https://doi.org/10.3390/electronics15102064)
14. [Context-aware GNSS with a kNN classifier](https://doi.org/10.3390/engproc2026126010)
15. [Transformer + denoising autoencoder for R, tightly coupled](https://www.researchgate.net/publication/359655505_Towards_Predicting_the_Measurement_Noise_Covariance_with_a_Transformer_and_Residual_Denoising_Autoencoder_for_GNSSINS_Tightly-Coupled_Integrated_Navigation)
16. [Linear-attention transformer for R](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5739728)
17. [Multitask learning of noise covariance for GNSS/INS](https://www.researchgate.net/publication/345095356_Predicting_the_Noise_Covariance_With_a_Multitask_Learning_Model_for_Kalman_Filter-Based_GNSSINS_Integrated_Navigation)
18. [AI-IMU dead reckoning](https://arxiv.org/pdf/1904.06064)
19. [Learned Q and R networks in a UKF](https://arxiv.org/pdf/2603.11649)
20. [RL-based adaptive KF for GNSS/INS](https://mdpi.com/2072-4292/12/11/1704)
21. [RL adaptive parameter policies for Bayesian filters](https://arxiv.org/html/2603.19910v1)
22. [KalmanNet](https://arxiv.org/pdf/2107.10043)
23. [Split-KalmanNet](https://arxiv.org/pdf/2210.09636)
24. [Recursive KalmanNet](https://arxiv.org/abs/2506.11639)
25. [AI-aided Kalman filters (survey)](https://arxiv.org/pdf/2410.12289v3.pdf)
26. [LSTM + factor graph during GNSS interruptions](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11398165/)
27. [LSTM pseudo-GNSS increments (Remote Sensing 2020)](https://mdpi-res.com/d_attachment/remotesensing/remotesensing-12-00256/article_deploy/remotesensing-12-00256.pdf)
28. [GRU outage bridging (Remote Sensing 2022)](https://mdpi-res.com/d_attachment/remotesensing/remotesensing-14-00752/article_deploy/remotesensing-14-00752.pdf)
29. [CNN-LSTM-attention with factor graphs](https://ieeexplore.ieee.org/abstract/document/10937982)
30. [Spiking-transformer fusion for GPS outages](https://arxiv.org/pdf/2601.08244)
31. [Genetic-neural adaptation of KF process noise](https://doi.org/10.3390/app16178706)
32. [Meta-learned online dynamics adaptation with KF](https://arxiv.org/abs/2504.16923)
33. [LLM + genetic programming for interpretable KF variants](https://arxiv.org/pdf/2508.11703)
34. [The Kalman Evolve](https://arxiv.org/html/2605.26830v1)
35. [Large language models as optimizers (OPRO)](https://arxiv.org/abs/2309.03409v3)
36. [LLMs for hyperparameter optimization](https://arxiv.org/html/2312.04528v2)
37. [When is an LLM worth it for HPO? Budget-matched study](https://arxiv.org/pdf/2606.21641)
38. [WRAP: Wasserstein-robust adaptive plug-in](https://arxiv.org/pdf/2608.09807)
39. [UrbanNav dataset](https://www.polyu.edu.hk/aae/ipn-lab/us/en/resources/urbannav-dataset/)
