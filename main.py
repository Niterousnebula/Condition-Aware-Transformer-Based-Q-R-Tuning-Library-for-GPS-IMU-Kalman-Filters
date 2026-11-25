"""Paper 2 (Condition-Aware Transformer-Based Q/R Tuning Library for GPS-IMU Kalman Filters), everything in
one command: the main run, the ablations, then the tables and figures.

    python main.py                 # the full run, resumable (starts and stops the LLM server itself)
    python main.py --plan          # what is done, what is left and a rough time estimate; runs nothing
    python main.py --plots-only    # rebuild the tables and figures from finished runs
    python main.py --smoke         # tiny budgets, ETH and the home drive, GWO only (no LLM): checks the pipeline
    python main.py --force         # run finished steps again (deletes nothing; reruns overwrite)

The LLM is a llama-server on this machine (LLAMA_SERVER below). main.py starts it when a step needs the LLM
and nothing answers on its port, logs it to results/qrlib/llama_server.log and stops it when the run ends.
A server that was already running is used as it is and left running.

Steps, each in its own process (so an ablation's settings cannot leak into the next step):
    1. main run        3 seeds x 4 drives (ETH, iNav-WHU playground00 and street00, the home drive) x LLM and
                       GWO; every run also has the baseline THETA0 (python -m qrlib) -> results/qrlib/seed_<s>/
    2. ablations       LLM only, seed 0: offline build, one-step score, Q over +- 3 decades
                       -> results/qrlib_offline/, qrlib_onestep/, qrlib_wideq/
    3. report          tables and figures (python -m qrlib.report) -> results/qrlib/paper/

Resumable: a finished (seed, drive) is skipped, so after an interruption run
the same command again. A failed step is logged and the next steps still run (the report is built from
whatever finished); the exit code is 1 if any step failed. Everything printed goes to
results/qrlib/main.log, every session is appended to results/qrlib/main_manifest.json, and
results/qrlib/.main.lock marks a run in progress (reset.py refuses to delete while it exists).
"""
import argparse
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HOME = "home/20260927_115918_outages_s0"      # make_home_data.py, from collected data/
DRIVES = ("eth_outages_s0", "inavwhu/playground00_outages_s0", "inavwhu/street00_outages_s0", HOME)
SEEDS = (0, 1, 2)
BUILDERS = ("llm", "gwo")       # the benchmark: baseline THETA0 (always run) against the GWO and LLM builders
ABLATIONS = (("offline build (no initialization mode)", "--offline", "qrlib_offline"),
             ("one-step score (no simulated dropouts)", "--onestep", "qrlib_onestep"),
             ("Q over THETA0 +- 3 decades", "--wide-q", "qrlib_wideq"))
SMOKE_DRIVES, SMOKE_BUILDERS, SMOKE_SEEDS = ("eth_outages_s0", HOME), ("gwo",), (0, 1)
# rough minutes per (seed, drive) at full budget with BUILDERS, and with the LLM alone (home: scaled from smoke)
MINUTES = {"eth_outages_s0": (9, 6), "inavwhu/playground00_outages_s0": (40, 25),
           "inavwhu/street00_outages_s0": (40, 25), HOME: (15, 10)}
LLAMA_SERVER = [r"D:\llama-b9754-bin-win-cuda-13.3-x64\llama-server.exe",
                "-m", r"D:\Modelfile\Qwen_Qwen3.5-9B-Q4_K_M.gguf", "--alias", "qwen35-9b", "-c", "4096",
                "--port", "8070"]
SERVER_LOAD_S = 300              # how long to wait for the model to load


def results_root(name="qrlib", smoke=False):
    return ROOT / "results" / (name + ("_smoke" if smoke else ""))


def slug(ds):
    return ds.replace("/", "__")


def done(root, seed, ds):
    return (root / f"seed_{seed}" / slug(ds) / "metrics.csv").exists()


def steps(smoke):
    """(name, python arguments, done?, minutes left) in order."""
    py = []
    if smoke:
        drives, builders, seeds, ab_seeds, ab_builders = SMOKE_DRIVES, SMOKE_BUILDERS, SMOKE_SEEDS, (0,), SMOKE_BUILDERS
        extra = ["--smoke"]
    else:
        drives, builders, seeds, ab_seeds, ab_builders = DRIVES, BUILDERS, SEEDS, (0,), ("llm",)
        extra = []
    root = results_root(smoke=smoke)
    left = [(s, d) for s in seeds for d in drives if not done(root, s, d)]
    py.append((f"main run: seeds {list(seeds)} x {len(drives)} drives x {', '.join(builders)}",
               ["-m", "qrlib", "--seeds", *map(str, seeds), "--builders", *builders, "--datasets", *drives, *extra],
               not left, sum(MINUTES[d][0] for _, d in left)))
    for name, flag, base in ABLATIONS:
        r = results_root(base, smoke)
        left = [(s, d) for s in ab_seeds for d in drives if not done(r, s, d)]
        py.append((f"ablation: {name}", ["-m", "qrlib", flag, "--seeds", *map(str, ab_seeds), "--builders",
                                         *ab_builders, "--datasets", *drives, *extra],
                   not left, sum(MINUTES[d][1] for _, d in left)))
    py.append(("tables and figures", ["-m", "qrlib.report", "--root", str(root)], False, 1))
    return py


class Tee:
    """Copy everything printed into the run log."""

    def __init__(self, path):
        self.f = open(path, "a", encoding="utf-8")

    def __call__(self, line):
        sys.stdout.write(line)
        sys.stdout.flush()
        self.f.write(line)
        self.f.flush()


def run_step(args, log):
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"}
    p = subprocess.Popen([sys.executable, *args], cwd=ROOT, env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
    for line in p.stdout:
        log(line)
    return p.wait()


def start_server(llm, log_path):
    """Start LLAMA_SERVER unless one already answers; returns the process to stop later (None if not ours)."""
    try:
        llm.check_server()
        return None
    except RuntimeError:
        pass
    print(f"starting llama-server (log: {log_path})", flush=True)
    p = subprocess.Popen(LLAMA_SERVER, stdout=open(log_path, "a", encoding="utf-8"), stderr=subprocess.STDOUT)
    for _ in range(SERVER_LOAD_S):
        if p.poll() is not None:
            raise SystemExit(f"llama-server exited with code {p.returncode}; see {log_path}")
        try:
            llm.check_server()
            print("llama-server ready", flush=True)
            return p
        except RuntimeError:
            time.sleep(1)
    p.kill()
    raise SystemExit(f"llama-server not ready after {SERVER_LOAD_S} s; see {log_path}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", action="store_true", help="print what is done and left, run nothing")
    ap.add_argument("--plots-only", action="store_true", help="only rebuild the tables and figures")
    ap.add_argument("--smoke", action="store_true", help="tiny budgets, ETH and the home drive, no LLM")
    ap.add_argument("--force", action="store_true", help="run finished steps again")
    a = ap.parse_args()

    plan = steps(a.smoke)
    if a.plots_only:
        plan = [s for s in plan if s[0] == "tables and figures"]
    if a.plan:
        total = 0
        for name, args, finished, minutes in plan:
            state = "done" if finished and not a.force else f"~{minutes} min"
            total += 0 if finished and not a.force else minutes
            print(f"  {'[x]' if finished else '[ ]'} {name:62s} {state}")
        print(f"rough time left: {total / 60:.1f} h (estimates from smoke runs; the iNav-WHU drives dominate)")
        return

    root = results_root(smoke=a.smoke)
    root.mkdir(parents=True, exist_ok=True)
    lock = root / ".main.lock"
    if lock.exists():
        raise SystemExit(f"{lock} exists: a main.py run is in progress (delete the lock if none is).")
    needs_llm = not a.plots_only and not a.smoke and any(
        "llm" in args and (not finished or a.force) for _, args, finished, _ in plan)
    server = None
    if needs_llm:
        sys.path.insert(0, str(ROOT))
        from qrlib import llm
        server = start_server(llm, root / "llama_server.log")   # fail now, not hours in
    lock.write_text(str(os.getpid()))
    log = Tee(root / "main.log")
    session = {"started": datetime.now().isoformat(timespec="seconds"), "argv": sys.argv[1:],
               "python": sys.version.split()[0], "platform": platform.platform(), "steps": []}
    t0, failed = time.time(), []
    try:
        log(f"\n######## main.py {' '.join(sys.argv[1:])}  {session['started']}\n")
        for name, args, finished, _ in plan:
            if finished and not a.force:
                log(f"\n=== {name}: done already\n")
                session["steps"].append({"step": name, "status": "skipped (done)"})
                continue
            if a.force and args[1] == "qrlib":
                args = [*args, "--force"]
            log(f"\n=== {name}\n    python {' '.join(args)}\n")
            s0 = time.time()
            code = run_step(args, log)
            status = "ok" if code == 0 else f"failed (exit {code})"
            if code != 0:
                failed.append(name)
            log(f"=== {name}: {status} in {(time.time() - s0) / 60:.1f} min\n")
            session["steps"].append({"step": name, "status": status, "minutes": round((time.time() - s0) / 60, 1)})
    finally:
        if server is not None:                          # free the GPU (shared machine)
            server.terminate()
            server.wait(timeout=30)
        lock.unlink(missing_ok=True)
        session["finished"] = datetime.now().isoformat(timespec="seconds")
        man = root / "main_manifest.json"
        hist = json.loads(man.read_text()) if man.exists() else []
        man.write_text(json.dumps(hist + [session], indent=1), encoding="utf-8")
    log(f"\nall steps in {(time.time() - t0) / 60:.1f} min" + (f"; FAILED: {', '.join(failed)}" if failed else "")
        + f"; tables and figures in {root / 'paper'}\n")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
