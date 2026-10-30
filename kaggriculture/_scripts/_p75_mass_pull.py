# -*- coding: utf-8 -*-
"""P75 aggressive mass pull of public kaggriculture notebooks."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

KAGGLE = r"C:\Users\Lenovo\AppData\Roaming\Python\Python313\Scripts\kaggle.exe"
ROOT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_p75_mass")
ROOT.mkdir(parents=True, exist_ok=True)

SLUGS = [
    "seyitkaangunes/kaggriculture-2820-score",
    "jaxa623/2802-two-identical-agents-90-points-apart",
    "jaxa623/2780-beyond-48-0-128-128-worlds-with-95-cis",
    "nathanjacob/kaggriculture-pipe-8-clean-opening",
    "nathanjacob/kaggriculture-pipe-7-wheat-microstructure",
    "degnonguidi/kaggriculture-cloning-agent",
    "sunil123kumar/kaggriculture-v8",
    "ahmedberatozer/kaggriculture-v47-reactive-market-coordination",
    "ahmedberatozer/kaggriculture-v49-funded-sale-timing-and-worker",
    "ahmedberatozer/kaggriculture-v48-clear-the-queue",
    "ahmedberatozer/kaggriculture-v45-first-turn-wheat-round-trip",
    "aurax7/kaggriculture-shop-router-reactive-v7",
    "yeshawang/kaggriculture-agent-evolution-public-notebook",
    "xuanzhang001/kaggriculture-auto-top1",
    "taylorclark637/sovereign-swarm-kinematics-the",
    "lynnsakurai/farming-score-v2-a-better-approach",
    "ayodejiibrahimlateef/kaggriculture-cloning-v45-open-78-experiment",
    "web3cainiao/kaggriculture-v21-tactical-memory",
    "thomastschinkel/kaggriculture-public-state-router-74-5-win-rate",
    "romantamrazov/kaggriculture-hamburger",
    "indarkarhana/shape-the-shop-work-the-pasture-top-10",
    "tetsutani/kaggriculture-market-smart-farming",
    "prvsiyan/kaggriculture-frontier-the-moon-counts-melons",
    "yhay81/shop-router-0909",
    "kaitofukami/40-40-early-floor-39-46-top-10-v48-fast-routes",
    "kaitofukami/25-27-strict-future-v27-midgame-meta-reset",
    "boatlee/v16-rc5-high-score-8c-4s-premium-market-lead",
    "xuanzhang001/kaggriculture-pipe7-public-top1",
    "nathanjacob/kaggriculture-pipe-5-terminal-boost",
    "guruprasaathas111/kaggriculture-master-engine-v3",
]


def main() -> None:
    env = dict(**__import__("os").environ)
    env["KAGGLE_CONFIG_DIR"] = r"C:\Users\Lenovo\.kaggle"
    ok, fail = [], []
    for slug in SLUGS:
        name = slug.replace("/", "__")
        dest = ROOT / name
        dest.mkdir(parents=True, exist_ok=True)
        nbs = list(dest.glob("*.ipynb"))
        if nbs:
            print(f"SKIP {slug}")
            ok.append(slug)
            continue
        print(f"PULL {slug}", flush=True)
        r = subprocess.run(
            [KAGGLE, "kernels", "pull", "-p", str(dest), slug],
            capture_output=True,
            text=True,
            env=env,
            encoding="utf-8",
            errors="replace",
        )
        if r.returncode == 0 and list(dest.glob("*.ipynb")):
            ok.append(slug)
        else:
            fail.append((slug, (r.stderr or r.stdout or "")[:120]))
            print(f"  FAIL {fail[-1][1]}")
    print(f"\nOK={len(ok)} FAIL={len(fail)}")
    for s, e in fail:
        print(" ", s, e)


if __name__ == "__main__":
    main()
