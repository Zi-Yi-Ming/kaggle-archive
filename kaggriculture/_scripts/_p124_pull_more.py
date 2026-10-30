# -*- coding: utf-8 -*-
"""P124: pull ALL gold episodes + scan new public kernels for stealable edges."""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
OUT = PROJ / "_external" / "p101_replays" / "gold"
OUT.mkdir(parents=True, exist_ok=True)
SCAN = PROJ / "_external" / "scan_p124"
SCAN.mkdir(parents=True, exist_ok=True)

GOLD_SUB = 56450063


def pull_gold(api):
    eps = [e.to_dict() for e in api.competition_list_episodes(submission_id=GOLD_SUB)]
    eps = [e for e in eps if (e.get("state") or "").upper() == "COMPLETED"]
    eps.sort(key=lambda e: e.get("createTime") or "", reverse=True)
    print(f"gold completed episodes: {len(eps)}", flush=True)
    n = 0
    for e in eps:
        eid = e.get("id")
        path = OUT / f"episode-{eid}-replay.json"
        if path.exists() and path.stat().st_size > 1000:
            continue
        try:
            api.competition_episode_replay(eid, path=str(OUT), quiet=True)
            n += 1
            print("  dl", eid, flush=True)
        except Exception as ex:
            print("  fail", eid, ex, flush=True)
        time.sleep(0.3)
        if n >= 25:
            break
    print("new gold downloads", n, flush=True)


def pull_kernels():
    slugs = [
        ("haideptry/the-2965-master-hybrid-engine", "hy2965"),
        ("haideptry/the-2950-peak-farm", "peak2950"),
        ("evgendvorkin/kaggriculture", "evgen"),
        ("dmitriigluzdov/kaggriculture-more-wheat-smarter-sales", "dmitrii_wheat"),
        ("xuanzhang001/kaggriculture-auto-top1", "autotop1"),
        ("leoprovorov/a-song-of-ice-and-fire-fixed-flexible", "icefire"),
    ]
    for slug, name in slugs:
        dest = SCAN / name
        dest.mkdir(parents=True, exist_ok=True)
        if list(dest.glob("*.ipynb")):
            print("skip", name, flush=True)
            continue
        r = subprocess.run(
            ["kaggle", "kernels", "pull", slug, "-p", str(dest), "-m"],
            capture_output=True, text=True, timeout=90,
        )
        print("pull", name, "ok" if r.returncode == 0 else (r.stderr or r.stdout)[-150:], flush=True)
        time.sleep(0.5)


def main():
    api = KaggleApi()
    api.authenticate()
    pull_gold(api)
    pull_kernels()
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
