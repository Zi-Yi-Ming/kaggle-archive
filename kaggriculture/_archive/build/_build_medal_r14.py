# -*- coding: utf-8 -*-
"""Medal R14: reorder sells on the real endgame dump window (709-717).

R13 only touched 649/717/718 but tape mega-dump starts at 712.
C16-style: same multiset, premium sells first, WHEAT last, non-sells stay.
"""
from pathlib import Path
import ast

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
src = ROOT / "_push_medal" / "main.py"
dst_dir = ROOT / "_push_medal_r14"
dst_dir.mkdir(parents=True, exist_ok=True)
dst = dst_dir / "main.py"

text = src.read_text(encoding="utf-8")
if "MEDAL_R14_DUMPWIN" not in text:
    overlay = r'''

# ---------------------------------------------------------------------------
# MEDAL_R14_DUMPWIN: premium-first sell order on steps 709-717
# ---------------------------------------------------------------------------
_R14_PARENT = agent
_R14_STEPS = set(range(709, 718))
_R14_RANK = {
    "STRAWBERRY": 0,
    "MELON": 1,
    "MILK": 2,
    "WOOL": 3,
    "EGG": 4,
    "TOMATO": 5,
    "CARROT": 6,
    "FERTILIZER": 7,
    "WHEAT": 9,
}


def _r14_swap(obs, action):
    step = int(obs.get("step") or 0)
    if step not in _R14_STEPS:
        return action
    market = list(action.get("market") or [])
    sells = []
    for i, o in enumerate(market):
        if isinstance(o, (list, tuple)) and len(o) >= 2 and o[0] == "SELL":
            sells.append((i, list(o)))
    if len(sells) < 2:
        return action
    sells_sorted = sorted(sells, key=lambda t: _R14_RANK.get(t[1][1], 5))
    slots = [i for i, _ in sells]
    new_market = list(market)
    for slot, (_, order) in zip(slots, sells_sorted):
        new_market[slot] = order
    result = dict(action)
    result["market"] = new_market[:10]
    return result


def agent(observation, configuration=None):
    action = _R14_PARENT(observation, configuration)
    try:
        return _r14_swap(observation, action)
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
  "id": "ziyiming/kaggriculture-medal-r14",
  "title": "Kaggriculture Medal R14",
  "code_file": "main.py",
  "enable_gpu": false,
  "kernel_type": "script"
}
""",
    encoding="utf-8",
)
print("meta ok")
