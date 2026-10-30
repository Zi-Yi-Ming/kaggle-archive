# -*- coding: utf-8 -*-
"""Static gate pre-screen for scanned notebooks."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_20260919")
KNOWN_MARKERS = [
    "shop_router",
    "SHOP_PLANS",
    "shop-router",
    "yhay81",
    "aurax7",
    "prvsiyan",
    "alperen_meta",
    "MetaCounter",
    "cleo_v11",
    "v11E",
    "tetsu2131",
    "route_label",
    "kaito",
    "finn",
    "fallow",
]
CLAIM_RE = re.compile(r"(2\d{3}(?:\.\d+)?|3\d{3}(?:\.\d+)?)")
AGENT_RE = re.compile(r"def\s+agent\s*\(")
FUNC_RE = re.compile(r"def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")


def nb_text(p: Path) -> str:
    try:
        nb = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        return f"__READ_FAIL__ {e}"
    parts = []
    for cell in nb.get("cells", []):
        src = cell.get("source", [])
        if isinstance(src, list):
            parts.append("".join(src))
        else:
            parts.append(str(src))
    return "\n".join(parts)


def main() -> None:
    rows = []
    for d in sorted(ROOT.iterdir()):
        if not d.is_dir():
            continue
        nbs = list(d.glob("*.ipynb"))
        if not nbs:
            rows.append((d.name, "NO_NB", 0, "", "", ""))
            continue
        text = nb_text(nbs[0])
        if text.startswith("__READ_FAIL__"):
            rows.append((d.name, text[:40], 0, "", "", ""))
            continue
        has_agent = bool(AGENT_RE.search(text))
        funcs = FUNC_RE.findall(text)
        agent_like = [
            f
            for f in funcs
            if re.search(r"agent|policy|step|act|main|farm|route|plan", f, re.I)
        ][:8]
        marks = [m for m in KNOWN_MARKERS if m.lower() in text.lower()]
        head = text[:15000]
        claims = sorted(set(CLAIM_RE.findall(head)), key=lambda x: -float(x))[:6]
        rows.append(
            (
                d.name[:48],
                "Y" if has_agent else "N",
                len(funcs),
                ",".join(agent_like)[:70],
                ",".join(marks)[:55],
                ",".join(claims)[:40],
            )
        )

    out = ROOT / "prescreen_summary.txt"
    lines = [
        f"{'notebook':48s} {'agent':5s} {'#fn':4s} {'agent-like':70s} {'markers':55s} claims",
        "-" * 200,
    ]
    for r in rows:
        lines.append(
            f"{r[0]:48s} {r[1]:5s} {r[2]:<4d} {r[3]:70s} {r[4]:55s} {r[5]}"
        )
    text = "\n".join(lines) + "\n"
    out.write_text(text, encoding="utf-8")
    print(text)
    print("WROTE", out)


if __name__ == "__main__":
    main()
