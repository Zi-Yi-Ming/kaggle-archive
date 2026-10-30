# -*- coding: utf-8 -*-
"""Deeper peek at executable scan candidates: uniqueness vs shop-router."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_20260919")
FOCUS = [
    "thomastschinkel",
    "goodpjw2008",
    "ahmedberatozer__kaggriculture-v50",
    "guruprasaathas111__game-theoretic",
    "guruprasaathas111__kaggriculture-master-engine-v3",
    "sunil123kumar",
]


def nb_text(p: Path) -> str:
    nb = json.loads(p.read_text(encoding="utf-8"))
    parts = []
    for cell in nb.get("cells", []):
        src = cell.get("source", [])
        parts.append("".join(src) if isinstance(src, list) else str(src))
    return "\n".join(parts)


def main() -> None:
    alperen = Path(r"D:\桌面\Kaggle\kaggriculture\_push_alperen\main.py")
    alp = alperen.read_text(encoding="utf-8", errors="ignore")
    # tokenize alperen identifiers
    alp_ids = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]{3,}", alp))

    lines = []
    for d in sorted(ROOT.iterdir()):
        if not d.is_dir():
            continue
        if not any(d.name.startswith(f) or f in d.name for f in FOCUS):
            continue
        nbs = list(d.glob("*.ipynb"))
        if not nbs:
            continue
        text = nb_text(nbs[0])
        ids = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]{3,}", text))
        inter = len(ids & alp_ids)
        only = len(ids - alp_ids)
        # unique-ish constants / crops / claims in markdown
        md_scores = re.findall(r"\b(2[7-9]\d{2}(?:\.\d+)?|3\d{3}(?:\.\d+)?)\b", text[:20000])
        crops = sorted({c for c in ["WHEAT","MELON","STRAWBERRY","CARROT","TOMATO","WOOL","MILK","EGG","YARN"] if c in text})
        # look for novel keywords
        novel_kw = [k for k in ["PPO","transformer","beam","MCTS","genetic","overfit","holdout","Bradley","meta-router","ensemble","clone"] if k.lower() in text.lower()]
        # first markdown-ish claim block
        m = re.search(r"(?is)(best.?score|public.?score|leaderboard|2945|win.?rate).{0,200}", text)
        snippet = re.sub(r"\s+", " ", m.group(0))[:180] if m else ""
        lines.append(
            f"## {d.name}\n"
            f"- size={nbs[0].stat().st_size} ids={len(ids)} inter_alperen={inter} only_here={only} jaccard≈{inter/max(1,len(ids|alp_ids)):.2f}\n"
            f"- crops={','.join(crops)} novel_kw={novel_kw}\n"
            f"- md_scores_sample={md_scores[:8]}\n"
            f"- snippet={snippet}\n"
        )
    out = ROOT / "deep_peek.txt"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out.read_text(encoding="utf-8"))
    print("WROTE", out)


if __name__ == "__main__":
    main()
