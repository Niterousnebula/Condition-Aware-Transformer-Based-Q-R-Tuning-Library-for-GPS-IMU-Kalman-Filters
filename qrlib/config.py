"""Every setting of the Q/R library pipeline."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "results" / "qrlib"
PAPER1_BEST = Path(r"D:\EKF\results\outages\summary\best_values.csv")   # paper 1's truth-tuned settings
TRACE_HZ = 10.0                  # traces saved for the figures
SEEDS = (0, 1, 2)                # python -m qrlib --seeds; each seed reruns every builder (LLM sampling too)
PLOT_HIGHLIGHT_WIDEN = 0.5       # figures: the shaded noise / outage sections are drawn 50 % wider (centred)

# The three drives of D:\EKF with their degraded GPS sections (~5 m, ~15 m, full outage at 25/50/75 %)
DATASETS = ("eth_outages_s0", "inavwhu/playground00_outages_s0", "inavwhu/street00_outages_s0")

# Train = start .. midway between the end of the 5 m section and the start of the 15 m section; test = rest
SPLIT_AFTER_SECTION = 0          # index of the last section inside the training part

# Search space (log10) around THETA0. R (the GPS, which is what changes between conditions): +- 3 decades; the
# D:\EKF benchmark's +- 2 caps iNav-WHU's log_r_xy at 1.78, while on its 15 m sections the truth's best is
# ~2.8-3.0. Q (the IMU, which does not change with the GPS): +- 1 decade. Paper 1 searched Q over +- 3 against
# ground truth; a GPS-only score sees Q's effect (coasting) only in part, and at +- 3 its picks could drift
# 35-37 m in 30 s without GPS on iNav-WHU (12-16 m at +- 1; coast_check in score_check.py). --wide-q: +- 3.
Q_SPAN, R_SPAN = 1.0, 3.0
PARAM_NAMES = ("log_q_acc", "log_q_gyro", "log_q_ba", "log_q_bg", "log_r_xy", "log_r_z", "log_r_vel")
PARAM_MEANING = ("accelerometer white noise PSD, (m/s^2)^2/Hz per axis", "gyroscope white noise PSD, (rad/s)^2/Hz per axis",
                 "accelerometer bias random walk PSD, (m/s^2)^2/s per axis",
                 "gyroscope bias random walk PSD, (rad/s)^2/s per axis",
                 "GPS horizontal position noise variance, m^2 per axis (east, north)",
                 "GPS vertical position noise variance, m^2", "GPS velocity noise variance, (m/s)^2 per axis")
GATE = "fix"                     # displacement plausibility gate (the only gate used):
GATE_VMAX = 6.0                  # a fix within GATE_VMAX * dt + GATE_MARGIN of the last accepted one is plausible;
GATE_MARGIN = 25.0               # m/s and m (ETH's ground truth tops out near 5 m/s; its raw fixes are off by <= 25 m)

# GPS condition detector (GPS fixes only, causal)
DECIDE_S = 1.0                   # a decision every second
COND_WINDOW_S = 15.0             # fixes of the last 15 s
COND_MIN_FIXES = 6
OUTAGE_GAP_S = 2.0               # no fix for max(2 s, 5 nominal intervals) -> outage
OUTAGE_GAP_INTERVALS = 5
RECOVERY_S = 30.0                # the first 30 s after an outage
NOISE_BINS = (("nominal", 2.5), ("moderate", 8.0), ("heavy", 25.0), ("extreme", float("inf")))  # sigma_h upper edges, m
HYSTERESIS = 1.2                 # the window keeps its bin until sigma_h leaves it by 20 % (iNav's 15 m noise sits
                                 # at ~20 m, near the 25 m edge, and flickered into extreme)
HOLD_S = 2.0                    # a cleaner noise condition must hold this long before the library switches back
# Plausibility trigger: at least JUMP_Y of the last JUMP_N fixes jump off the line through the two fixes before
# them by more than a noisier bin's edge (in sigma_h units) -> switch to that bin at once. JUMP_N = 0: off
JUMP_N, JUMP_Y = 7, 4
# Jump gate: under a noise condition in JUMP_GATE_LABELS, a fix whose jump exceeds that condition's bin edge is
# not fused (it is implausible there); once JUMP_Y of JUMP_N jump, the trigger moves to the noisier bin. It
# protects settings that trust GPS at the onset of noise; under heavy noise it only threw fixes away (ETH 15 m
# section after the onset 3.4 -> 4.0 m, street 7.6 -> 10.2 m), so heavy and extreme are not gated.
# Used by the library methods and their search; the baseline and static settings keep the plain gate.
JUMP_GATE = True
JUMP_GATE_LABELS = ("nominal", "moderate")
SEVERITY = ("nominal", "moderate", "heavy", "extreme")

# GPS-only score with simulated dropouts: in every scoring window the fixes from 5 to 10 s into each 15 s are
# hidden, so the score also measures the prediction after coasting on the IMU (what Q decides)
SCORE_DROPOUT = True
SCORE_DROP_EVERY, SCORE_DROP_AT, SCORE_DROP_S = 15.0, 5.0, 5.0

# Score windows and budgets
WINDOW_S = 30.0                  # each candidate is scored on windows of 30 s
MAX_WINDOWS = 6                  # per condition (offline)
MIN_WINDOW_S = 15.0              # a shorter run of one condition is not used
BUILD_ROUNDS, BUILD_K = 8, 8     # offline build and the static entry: 8 rounds of 8 proposals (+ seeds)
# Initialization mode (default): the library is built during the drive, from its start to the split, causally.
# Each time a condition completes a new WINDOW_S window (its first MAX_WINDOWS), its entry is re-tuned with
# INIT_ROUNDS rounds of BUILD_K on its windows so far, and used from then on. INIT_MODE = False: offline build.
INIT_MODE = True
INIT_ROUNDS = 2
UPDATE_S = 20.0                  # online: an unseen condition must last 20 s, then it is tuned on those 20 s
UPDATE_ROUNDS, UPDATE_K = 3, 8
SEED = 0

# LLM proposer. "server": a llama-server running on this machine (OpenAI-compatible); main.py starts and stops
# it (main.LLAMA_SERVER); for python -m qrlib on its own, start it first with
#   llama-server.exe -m D:\Modelfile\Qwen_Qwen3.5-9B-Q4_K_M.gguf --alias qwen35-9b -c 4096 --port 8070
# Qwen3.5-9B Q4 fits the 8 GB GPU (~13 s per round). gemma4-v2 Q8 (12.7 GB) does not fit, runs partly on the CPU
# and takes ~3 min per round (--llm-url http://127.0.0.1:8080/v1/chat/completions --llm-model gemma-q8, server
# started without -ngl). "local": a Hugging Face model loaded in-process (LLM_PATH, e.g. Qwen2.5-3B: too weak).
LLM_BACKEND = "server"
LLM_URL = "http://127.0.0.1:8070/v1/chat/completions"
LLM_MODEL = "qwen35-9b"
LLM_TIMEOUT_S = 1800              # per call; no speed limit, a busy GPU only makes the run slower
LLM_RETRIES = 2                  # then the call counts as an empty reply instead of stopping the run
LLM_THINKING = False             # hidden "thinking" off (Qwen3.5 thinks for 3,000+ tokens); the reply still reasons
LLM_PATH = Path(r"D:\safetensors\Qwen2.5-3B-Instruct")
LLM_TEMPERATURE = 0.8
LLM_TOP_P = 0.95
LLM_MAX_NEW_TOKENS = 900         # a few sentences of reasoning + K settings; generation stops after the JSON
LLM_HISTORY = 12                 # best settings shown back to the model
