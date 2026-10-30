# -*- coding: utf-8 -*-
"""Medal R13: surgical late-step sell reordering (Beiciccc C16 style).

Only steps 649, 717, 718. Reorder existing SELL orders among themselves:
premium first, WHEAT last. Non-sells stay in original slots.
No qty change, no mid-game reorder.
"""
from pathlib import Path
import ast

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
src = ROOT / "_push_medal" / "main.py"
dst_dir = ROOT / "_push_medal_r13"
dst_dir.mkdir(parents=True, exist_ok=True)
dst = dst_dir / "main.py"

text = src.read_text(encoding="utf-8")
if "MEDAL_R13_SWAP649" not in text:
    overlay = r'''

# ---------------------------------------------------------------------------
# MEDAL_R13_SWAP649: late-step sell order swap (same multiset)
# ---------------------------------------------------------------------------
_R13_PARENT = agent
_R13_STEPS = {649, 717, 718}
_R13_RANK = {
    "MELON": 0, "WOOL": 1, "MILK": 2, "STRAWBERRY": 3,
    "EGG": 4, "TOMATO": 5, "CARROT": 6, "FERTILIZER": 7,
    "WHEAT": 9,
}


def _r13_swap(obs, action):
    step = int(obs.get("step") or 0)
    if step not in _R13_STEPS:
        return action
    market = list(action.get("market") or [])
    # extract sells, keep non-sells in place by rebuilding
    sells = []
    for i, o in enumerate(market):
        if isinstance(o, (list, tuple)) and len(o) >= 2 and o[0] == "SELL":
            sells.append((i, list(o)))
    if len(sells) < 2:
        return action
    # sort sells by premium rank (stable)
    sells_sorted = sorted(sells, key=lambda t: _R13_RANK.get(t[1][1], 5))
    # write back into the same sell slots in order
    sell_slot_idx = [i for i, _ in sells]
    new_market = list(market)
    for slot, (_, order) in zip(sell_slot_idx, sells_sorted):
        new_market[slot] = order
    result = dict(action)
    result["market"] = new_market[:10]
    return result


def agent(observation, configuration=None):
    action = _R13_PARENT(observation, configuration)
    try:
        return _r13_swap(observation, action)
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
  "id": "ziyiming/kaggriculture-medal-r13",
  "title": "Kaggriculture Medal R13",
  "code_file": "main.py",
  "enable_gpu": false,
  "kernel_type": "script"
}
""",
    encoding="utf-8",
)
print("meta ok")
