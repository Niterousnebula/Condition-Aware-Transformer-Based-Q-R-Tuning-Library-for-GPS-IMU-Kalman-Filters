"""Remove paper 2's generated results so the next `python main.py` starts from scratch.

    python reset.py                    # paper 2: every results/qrlib*/ folder (main run, ablations, smoke runs,
                                       # score check, tables, figures); lists them, then asks
    python reset.py --smoke            # only the smoke runs (results/qrlib*_smoke/)
    python reset.py --all              # everything under results/ and every
                                       # __pycache__
    python reset.py --yes              # remove without asking

Keeps all code, the README, processed_data/ and the raw data. Refuses while a main.py run holds a
.main.lock in what it would remove.
"""
import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"


def targets(smoke=False, everything=False):
    if everything:
        found = [RESULTS] + sorted(p for p in ROOT.rglob("__pycache__") if p.is_dir())
    else:
        found = sorted(p for p in RESULTS.glob("qrlib*") if p.is_dir() and (not smoke or p.name.endswith("_smoke")))
    return [t for t in found if t.exists()]


def size_mb(p):
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file()) / 1e6


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--smoke", action="store_true", help="only the smoke runs")
    p.add_argument("--all", action="store_true", help="everything under results/ and every __pycache__")
    p.add_argument("--yes", "-y", action="store_true", help="remove without asking")
    a = p.parse_args()
    found = targets(a.smoke, a.all)
    for t in found:                                    # never anything outside this project folder
        assert t.resolve().is_relative_to(ROOT) and t.resolve() != ROOT, t
    locks = [lock for t in found for lock in t.glob("**/.main.lock")]
    if locks:
        raise SystemExit(f"{locks[0].relative_to(ROOT)} exists: a main.py run is in progress "
                         "(delete the lock if none is).")
    if not found:
        print("Nothing to remove.")
        return
    print("Will remove:")
    for t in found:
        print(f"  {t.relative_to(ROOT)}  ({size_mb(t):.1f} MB)")
    if not a.yes and input("Remove these? [y/N] ").strip().lower() != "y":
        print("Nothing removed.")
        return
    for t in found:
        shutil.rmtree(t)
    print(f"Removed {len(found)} folders. Run `python main.py` to regenerate the results.")


if __name__ == "__main__":
    main()
