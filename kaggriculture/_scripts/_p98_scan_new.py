"""P98: pull new public kernels of interest and prep dual-gate."""
from pathlib import Path
import subprocess
import sys

OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_p98_new")
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = [
    # (kernel slug, short name)
    ("ahmedberatozer/kaggriculture-v56-smarter-seeds-and-fertilizer", "v56"),
    ("busyaprime/v54-fork-wins-72-5-head-to-head-against-v54", "v54fork"),
    ("busyaprime/92-vs-the-best-public-farm-a-seed-leak-in-v54", "v54leak"),
    ("nathanjacob/kaggriculture-pipe19-sale-advance-overflow", "pipe19"),
    ("nathanjacob/kaggriculture-pipe18-six-layers", "pipe18"),
    ("shiiin9/your-market-list-is-an-order-book", "orderbook"),
    ("ahmedberatozer/kaggriculture-v55-one-turn-market-race-edge", "v55"),
]


def pull(slug: str, name: str) -> Path | None:
    dest = OUT / name
    dest.mkdir(parents=True, exist_ok=True)
    cmd = ["kaggle", "kernels", "pull", slug, "-p", str(dest), "-m"]
    print("PULL", slug, "->", dest)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        print("FAIL", slug, r.stderr[-300:] if r.stderr else r.stdout[-300:])
        return None
    files = list(dest.glob("*"))
    print("OK", name, [f.name for f in files][:8])
    return dest


def main():
    for slug, name in TARGETS:
        try:
            pull(slug, name)
        except Exception as e:
            print("ERR", name, e)
    print("DONE pulls")


if __name__ == "__main__":
    main()
