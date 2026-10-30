# -*- coding: utf-8 -*-
import json
import re
from pathlib import Path

base = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_p94_violent")
for name in [
    "kaggriculture-top-2-master-engine-v4",
    "25-27-strict-future-v27-midgame-meta-reset",
    "84-84-base-public-holdout-v14-clone-preemption",
    "kaggriculture-rank-your-agent",
    "cropsense-the-adaptive-farm-ai",
    "farmpilot-ai",
    "a-wonderful-life",
]:
    nbs = list((base / name).rglob("*.ipynb"))
    if not nbs:
        print(name, "NO NB")
        continue
    nb = json.loads(nbs[0].read_text(encoding="utf-8", errors="ignore"))
    print("====", name, "cells", len(nb.get("cells", [])))
    for i, c in enumerate(nb.get("cells", [])[:8]):
        s = c.get("source", "")
        if isinstance(s, list):
            s = "".join(s)
        keys = [k for k in ("SOURCE", "BLOB", "B85", "B64", "PAYLOAD", "FILES", "def agent", "%%writefile", "submission") if k in s]
        print(f"  {i} {c.get('cell_type')} len={len(s)} keys={keys} head={s[:120]!r}")
