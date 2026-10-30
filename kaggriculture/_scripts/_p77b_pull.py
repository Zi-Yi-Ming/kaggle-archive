# -*- coding: utf-8 -*-
"""P77b: pull high-value new public notebooks."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

KAGGLE = r"C:\Users\Lenovo\AppData\Roaming\Python\Python313\Scripts\kaggle.exe"
ROOT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_p77")
ROOT.mkdir(parents=True, exist_ok=True)

SLUGS = [
    "hesoponyo/pure-rl-agent-bc-ppo-self-play",
    "municef1/lb-2448-single-file-kaggriculture-agent",
    "dmitriigluzdov/kaggriculture-7-turn-rescue-historical-lb-2800",
    "dmitriigluzdov/kaggriculture-herd-safe-sale-window-lb-2700",
    "alperen5252525/kaggriculture-metacounter-r1-scored-agent",
    "salemali7/kaggriculture-2900",
    "lime0001/score2710-t23-kaggriculture-smart-harvest",
    "nusrati/2715-6",
    "avioon/kaggriculture-apex-v7-god-emperor",
    "llccqq624/kaggriculture-top-5-meta-ensemble",
    "nathanjacob/how-many-twins-strategy-clustering-kaggriculture",
    "nathanjacob/beyond-v43-what-the-top-clusters-do-on-turn-1",
    "guruprasaathas111/kaggriculture-fully-dynamic-autonomous-agent",
    "rohitt94/kaggriculture-route-replay-agent",
    "denizeryilmaz/v111-8c4s-economic-core-premium-lead",
    "andrewsokolovsky/kaggriculture-breaking-the-tie",
    "lynnsakurai/farming-score-v3-replay-revised",
    "lynnsakurai/farming-score-v5-timing-optimized",
    "evgendvorkin/kaggriculture",
    "reyhanksatria/kaggriculture-dynamic-route-agent",
    "yhay81/shop-router-0913",
    "yhay81/fieldbook-commit-for-three-days",
    "crystalbaby/kaggriculture-v38-public-submission",
    "hosen42/kaggriculture-v11-hc1-full-panel-validation",
    "arsgorynich/kaggriculture-v40-challenger",
    "indarkarhana/rank-top10-read-the-market-choose-the-farm",
    "cjlcjlcjl/kaggriculture-what-the-top-farms-do-a-live-meta",
    "thomastschinkel/kaggriculture-93-8-win-rate-public-state-router",
    "kaitofukami/103-128-fresh-public-v43-sparse-shop-hybrid",
    "salemali7/harvest-kaggriculture",
]


def main() -> None:
    env = dict(os.environ)
    env["KAGGLE_CONFIG_DIR"] = r"C:\Users\Lenovo\.kaggle"
    ok = fail = 0
    for slug in SLUGS:
        dest = ROOT / slug.replace("/", "__")
        dest.mkdir(parents=True, exist_ok=True)
        if list(dest.glob("*.ipynb")):
            print("SKIP", slug)
            ok += 1
            continue
        print("PULL", slug, flush=True)
        r = subprocess.run(
            [KAGGLE, "kernels", "pull", "-p", str(dest), slug],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        if r.returncode == 0 and list(dest.glob("*.ipynb")):
            ok += 1
        else:
            fail += 1
            print("  FAIL", (r.stderr or r.stdout or "")[:100])
    print(f"OK={ok} FAIL={fail}")


if __name__ == "__main__":
    main()
