# -*- coding: utf-8 -*-
"""Build Medal R5: Medal R2 + premium-first market queue reordering.

Mechanism (slotter_silas lesson): market orders resolve in list order; the first
unit of a sale gets the best price. Reordering costs nothing.

Also keep a late hard-dump only at step >= 716 (not day-28 soft dump, which R4
showed was noise/negative).
"""
from pathlib import Path
import ast

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
src = ROOT / "_push_medal" / "main.py"
dst_dir = ROOT / "_push_medal_r5"
dst_dir.mkdir(parents=True, exist_ok=True)
dst = dst_dir / "main.py"

text = src.read_text(encoding="utf-8")
if "MEDAL_R5_SLOT" not in text:
    overlay = r'''

# ---------------------------------------------------------------------------
# MEDAL_R5_SLOT: premium-first sell ordering + late hard dump
# ---------------------------------------------------------------------------
_R5_PREMIUM_RANK = {
    "MELON": 0, "WOOL": 1, "MILK": 2, "STRAWBERRY": 3,
    "TOMATO": 4, "EGG": 5, "FERTILIZER": 6, "CARROT": 7, "WHEAT": 8,
}
_R5_SELLABLE = (
    "WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
    "EGG", "MILK", "WOOL", "FERTILIZER",
)
_R5_DUMP_FROM = 716
_R5_PARENT = agent


def _r5_is_sell(o):
    return isinstance(o, (list, tuple)) and len(o) >= 2 and o[0] == "SELL"


def _r5_reorder(orders):
    """Stable partition: premium sells, other sells, non-sells. Preserve relative order."""
    premium, other_sell, rest = [], [], []
    for o in orders:
        if _r5_is_sell(o):
            item = o[1] if len(o) > 1 else ""
            if item in _R5_PREMIUM_RANK and _R5_PREMIUM_RANK[item] <= 3:
                premium.append(o)
            else:
                other_sell.append(o)
        else:
            rest.append(o)
    return premium + other_sell + rest


def _r5_hard_dump(obs, action):
    step = int(obs.get("step") or 0)
    if step < _R5_DUMP_FROM:
        return action
    private = obs.get("private") or {}
    shed = private.get("shed") or {}
    prices = ((obs.get("market") or {}).get("prices") or {})
    orders = list(action.get("market") or [])
    already = {o[1] for o in orders if _r5_is_sell(o) and len(o) > 1}
    for item in _R5_SELLABLE:
        if len(orders) >= 10:
            break
        if item in already:
            continue
        qty = int(shed.get(item) or 0)
        if qty <= 0:
            continue
        scheduled = sum(int(o[2] or 0) for o in orders if _r5_is_sell(o) and len(o) > 2 and o[1] == item)
        qty = max(0, qty - scheduled)
        if qty <= 0:
            continue
        orders.append(["SELL", item, qty])
    orders = _r5_reorder(orders)
    action = dict(action)
    action["market"] = orders[:10]
    return action


def agent(observation, configuration=None):
    action = _R5_PARENT(observation, configuration)
    try:
        action = _r5_hard_dump(observation, action)
        if isinstance(action, dict) and action.get("market"):
            action = dict(action)
            action["market"] = _r5_reorder(action["market"])[:10]
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
    '''{
  "competition_sources": ["kaggriculture"],
  "language": "python",
  "enable_internet": false,
  "is_private": true,
  "id": "ziyiming/kaggriculture-medal-r5",
  "title": "Kaggriculture Medal R5",
  "code_file": "main.py",
  "enable_gpu": false,
  "kernel_type": "script"
}
''',
    encoding="utf-8",
)
print("meta ok")
