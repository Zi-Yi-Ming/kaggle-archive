# -*- coding: utf-8 -*-
"""Lineage markers for local agents."""
from pathlib import Path
import hashlib
import re

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
CANDS = {
    "R2": ROOT / "_push_medal" / "main.py",
    "Moon": ROOT / "_external" / "public_nb" / "prvsiyan_moon" / "main.py",
    "prvsiyan": ROOT / "_external" / "top5_notebooks" / "prvsiyan" / "prvsiyan_main.py",
    "tetsu_msf_router": ROOT / "_external" / "public_nb" / "tetsu_msf" / "router.py",
    "tetsu": ROOT / "_external" / "top5_notebooks" / "tetsu2131" / "tetsu2131_main.py",
    "tetsu_shape": ROOT / "_external" / "public_nb" / "tetsu_shape" / "main.py",
    "boatlee": ROOT / "_external" / "public_nb" / "boatlee_v20" / "main.py",
    "rayk": ROOT / "_external" / "public_nb" / "rayk_rank" / "main.py",
    "kaito58": ROOT / "_external" / "public_nb" / "kaito_v58" / "main.py",
    "kaito48": ROOT / "_external" / "public_nb" / "kaito_v48" / "main.py",
    "flex": ROOT / "_external" / "top5_notebooks" / "flexonafft" / "flexonafft_main.py",
    "salem": ROOT / "_external" / "top5_notebooks" / "salemali7" / "salemali7_main.py",
}

MARKERS = [
    "yhay81", "aurax7", "SHOP_PLANS", "Shop Router", "prvsiyan",
    "advance_sales", "projected_shed", "_INLINE_TAPES", "kaitofukami",
    "minimax", "closed-loop", "def agent",
]


def main():
    print(f"{'name':16s} {'sha12':12s} {'len':>7s}  markers")
    texts = {}
    for k, p in CANDS.items():
        if not p.exists():
            print(f"{k:16s} MISSING")
            continue
        b = p.read_bytes()
        t = b.decode("utf-8", "replace")
        texts[k] = t
        sha = hashlib.sha256(b).hexdigest()[:12]
        marks = []
        for m in MARKERS:
            c = t.count(m)
            if c:
                marks.append(f"{m}:{c}")
        print(f"{k:16s} {sha:12s} {len(b):7d}  {' '.join(marks)}")

    # pairwise jaccard on unique identifier-like tokens (cheap)
    def toks(t):
        return set(re.findall(r"[A-Za-z_][A-Za-z0-9_]{4,}", t))

    print("\n=== token Jaccard (top pairs) ===")
    names = list(texts)
    pairs = []
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            ta, tb = toks(texts[a]), toks(texts[b])
            j = len(ta & tb) / len(ta | tb) if ta | tb else 0
            pairs.append((j, a, b))
    for j, a, b in sorted(pairs, reverse=True)[:15]:
        print(f"  {j:.3f}  {a} ↔ {b}")

    print("\n=== lineage verdicts ===")
    print("R2 ↔ Moon: SAME_FAMILY (yhay81+aurax7+SHOP_PLANS, exact-tie 6/6)")
    print("R2 ↔ tetsu_msf_router: SAME_FAMILY (explicit yhay81 header)")
    print("R2 ↔ tetsu: UNKNOWN/different tapes (tetsu2131 adaptive, no yhay81 header)")
    print("R2 ↔ tetsu_shape: candidate INDEPENDENT (different notebook/author)")
    print("R2 ↔ boatlee: INDEPENDENT multi-route")
    print("R2 ↔ rayk: INDEPENDENT public-replay reconstruction")
    print("R2 ↔ kaito58: INDEPENDENT minimax closed-loop")


if __name__ == "__main__":
    main()
