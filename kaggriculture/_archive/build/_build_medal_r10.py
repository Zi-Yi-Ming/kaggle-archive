# -*- coding: utf-8 -*-
"""Medal R10: append-only late liquidation (no reorder, no mid-game change).

R8/R9 failed because they reordered the queue and broke buy-funding.
R10 only APPENDs missing SELL orders at the end on steps 717-718.
Original order positions (which fund buys) stay intact.
"""
from pathlib import Path
import ast

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
src = ROOT / "_push_medal" / "main.py"
dst_dir = ROOT / "_push_medal_r10"
dst_dir.mkdir(parents=True, exist_ok=True)
dst = dst_dir / "main.py"

text = src.read_text(encoding="utf-8")
if "MEDAL_R10_APPEND" not in text:
    overlay = r'''

# ---------------------------------------------------------------------------
# MEDAL_R10_APPEND: append-only late sells (preserve original queue order)
# ---------------------------------------------------------------------------
_R10_PARENT = agent
_R10_SELLABLE = (
    "MELON", "WOOL", "MILK", "STRAWBERRY", "EGG",
    "TOMATO", "FERTILIZER", "CARROT", "WHEAT",
)


def _r10_append_late(obs, action):
    step = int(obs.get("step") or 0)
    if step not in (716, 717, 718):
        return action
    private = obs.get("private") or {}
    shed = private.get("shed") or {}
    market = list(action.get("market") or [])
    already = {}
    for o in market:
        if isinstance(o, (list, tuple)) and len(o) >= 3 and o[0] == "SELL":
            already[o[1]] = already.get(o[1], 0) + int(o[2] or 0)
    changed = False
    for item in _R10_SELLABLE:
        if len(market) >= 10:
            break
        stock = int(shed.get(item) or 0)
        excess = stock - already.get(item, 0)
        if excess <= 0:
            continue
        # merge only into an existing SELL of same item (keeps its slot)
        merged = False
        for o in market:
            if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL" and o[1] == item:
                o[2] = int(o[2] or 0) + excess
                merged = True
                changed = True
                break
        if not merged:
            market.append(["SELL", item, excess])
            changed = True
    if not changed:
        return action
    result = dict(action)
    result["market"] = market[:10]
    return result


def agent(observation, configuration=None):
    action = _R10_PARENT(observation, configuration)
    try:
        return _r10_append_late(observation, action)
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
  "id": "ziyiming/kaggriculture-medal-r10",
  "title": "Kaggriculture Medal R10",
  "code_file": "main.py",
  "enable_gpu": false,
  "kernel_type": "script"
}
""",
    encoding="utf-8",
)
print("meta ok")
