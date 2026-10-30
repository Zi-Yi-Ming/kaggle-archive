# -*- coding: utf-8 -*-
"""Medal R9: premium-first market queue only (no extra dump).

Silas lesson: first units in the market queue get the best price.
Only reorders existing orders — no quantity changes, no endgame race.
"""
from pathlib import Path
import ast

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
src = ROOT / "_push_medal" / "main.py"
dst_dir = ROOT / "_push_medal_r9"
dst_dir.mkdir(parents=True, exist_ok=True)
dst = dst_dir / "main.py"

text = src.read_text(encoding="utf-8")
if "MEDAL_R9_SLOT" not in text:
    overlay = r'''

# ---------------------------------------------------------------------------
# MEDAL_R9_SLOT: premium-first sell ordering only
# ---------------------------------------------------------------------------
_R9_PARENT = agent
_R9_PREMIUM = {"MELON", "WOOL", "MILK", "STRAWBERRY", "EGG"}


def _r9_reorder(orders):
    prem, other, rest = [], [], []
    for o in orders:
        if isinstance(o, (list, tuple)) and len(o) >= 2 and o[0] == "SELL":
            if o[1] in _R9_PREMIUM:
                prem.append(list(o))
            else:
                other.append(list(o))
        else:
            rest.append(list(o) if isinstance(o, (list, tuple)) else o)
    return prem + other + rest


def agent(observation, configuration=None):
    action = _R9_PARENT(observation, configuration)
    try:
        if isinstance(action, dict) and action.get("market"):
            action = dict(action)
            action["market"] = _r9_reorder(action["market"])[:10]
        return action
    except Exception:
        return action
'''
    if "kaggle_agent=agent" in text:
        text = text.replace("kaggle_agent=agent", "kaggle_agent=agent\n" + overlay + "\nkaggle_agent=agent\n", 1)
    else:
        text = text + overlay

dst.write_text(text, encoding="utf-8")
ast.parse(dst.read_text(encoding="utf-8"))
print("wrote", dst, dst.stat().st_size)
(dst_dir / "kernel-metadata.json").write_text(
    """{
  "competition_sources": ["kaggriculture"],
  "language": "python",
  "enable_internet": false,
  "is_private": true,
  "id": "ziyiming/kaggriculture-medal-r9",
  "title": "Kaggriculture Medal R9",
  "code_file": "main.py",
  "enable_gpu": false,
  "kernel_type": "script"
}
""",
    encoding="utf-8",
)
