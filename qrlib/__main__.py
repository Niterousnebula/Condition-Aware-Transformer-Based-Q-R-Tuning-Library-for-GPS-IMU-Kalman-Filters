"""python -m qrlib [--seeds 0 1 2] [--datasets ...] [--builders llm random gwo] [--smoke] [--offline] [--onestep]

Each drive starts in initialization mode (the library is built from the drive start to the split, causally),
then runs every method on its test part (normal GPS, the 15 m section, the outage). One folder per seed:
results/qrlib/seed_<s>/<dataset>/. A finished (seed, dataset) is skipped unless --force, so an interrupted
run resumes. Ablations go to their own folders: --offline (library built offline after the training part)
-> results/qrlib_offline/, --onestep (score without simulated dropouts) -> results/qrlib_onestep/, --wide-q
(Q over THETA0 +- 3 decades, not +- 1) -> results/qrlib_wideq/; --smoke
(tiny budgets) adds _smoke. python -m qrlib.report then writes the paper's tables and figures.
"""
import argparse
import time

import pandas as pd

from . import config as C


def out_root(smoke=False, offline=False, onestep=False, wide_q=False):
    name = ("qrlib" + ("_offline" if offline else "") + ("_onestep" if onestep else "") + ("_wideq" if wide_q else "")
            + ("_smoke" if smoke else ""))
    return C.ROOT / "results" / name


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seeds", nargs="+", type=int, default=list(C.SEEDS))
    ap.add_argument("--datasets", nargs="+", default=list(C.DATASETS))
    ap.add_argument("--builders", nargs="+", default=["llm", "random", "gwo"], help="llm, random, gwo (and de)")
    ap.add_argument("--smoke", action="store_true", help="tiny budgets")
    ap.add_argument("--offline", action="store_true",
                    help="ablation: build the library offline after the training part (no initialization mode)")
    ap.add_argument("--onestep", action="store_true", help="ablation: score without simulated GPS dropouts")
    ap.add_argument("--wide-q", action="store_true", help="ablation: Q searched over THETA0 +- 3 decades (not +- 1)")
    ap.add_argument("--force", action="store_true", help="rerun (seed, dataset) pairs that are already done")
    ap.add_argument("--llm-url", default=C.LLM_URL, help="llama-server chat endpoint (default Qwen3.5-9B on 8070)")
    ap.add_argument("--llm-model", default=C.LLM_MODEL, help="the server's --alias")
    ap.add_argument("--device", default="cpu", help="for the filter (the CPU is 3-5x faster than the GPU at these batch sizes); the LLM always runs on the GPU")
    a = ap.parse_args()
    for b in a.builders:
        if b not in ("llm", "random", "gwo", "de"):
            ap.error(f"unknown builder {b}")
    C.LLM_URL, C.LLM_MODEL = a.llm_url, a.llm_model
    C.INIT_MODE = not a.offline
    C.SCORE_DROPOUT = not a.onestep
    if a.wide_q:
        C.Q_SPAN = 3.0
    if "llm" in a.builders and C.LLM_BACKEND == "server":
        from . import llm
        llm.check_server()
    root = out_root(a.smoke, a.offline, a.onestep, a.wide_q)
    root.mkdir(parents=True, exist_ok=True)
    logf = open(root / "run.log", "a", encoding="utf-8")
    logf.write(f"--- seeds {a.seeds}, builders {a.builders}; llm: {C.LLM_BACKEND} {C.LLM_MODEL} at {C.LLM_URL}, "
               f"thinking {C.LLM_THINKING}; library: {'initialization mode' if C.INIT_MODE else 'offline build'}; "
               f"score dropouts {C.SCORE_DROPOUT}; Q span {C.Q_SPAN}" + "\n")

    def log(msg):
        print(msg, flush=True)
        logf.write(msg + "\n")
        logf.flush()

    from . import evaluate
    t0 = time.time()
    for seed in a.seeds:
        C.SEED = seed
        for ds in a.datasets:
            out_dir = root / f"seed_{seed}" / evaluate._slug(ds)
            if (out_dir / "metrics.csv").exists() and not a.force:
                log(f"=== seed {seed}, {ds}: done already (--force to rerun)")
                continue
            log(f"=== seed {seed}")
            evaluate.run(ds, a.builders, smoke=a.smoke, device=a.device, log=log, out_dir=out_dir)
    # every finished (seed, dataset) in this root, one table each
    for name, fname in (("metrics.csv", "summary.csv"), ("init.csv", "init_summary.csv")):
        parts = []
        for f in sorted(root.glob(f"seed_*/*/{name}")):
            d = pd.read_csv(f)
            d.insert(0, "seed", int(f.parent.parent.name.split("_")[1]))
            parts.append(d)
        if parts:
            pd.concat(parts, ignore_index=True).to_csv(root / fname, index=False)
    log(f"all done in {(time.time() - t0) / 60:.1f} min, results in {root}")


if __name__ == "__main__":
    main()
