# -*- coding: utf-8 -*-
"""Medal R11: early premium dump on day-29 morning (append-only).

Mirror losses open at d27-29. Goal: sell a slice of premium BEFORE the
shared d29 flood, without reordering the queue or touching staples.
"""
from pathlib import Path
import ast

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
src = ROOT / "_push_medal" / "main.py"
dst_dir = ROOT / "_push_medal_r11"
dst_dir.mkdir(parents=True, exist_ok=True)
dst = dst_dir / "main.py"

text = src.read_text(encoding="utf-8")
if "MEDAL_R11_EARLYPREM" not in text:
    overlay = r'''

# ---------------------------------------------------------------------------
# MEDAL_R11_EARLYPREM: day-29 morning premium slice (append-only)
# ---------------------------------------------------------------------------
_R11_PARENT = agent
_R11_WINDOW = range(700, 712)  # day 29 hours 4-15
_R11_RULES = (
    # item, min_price, min_stock, slice
    ("MILK", 40, 16, 8),
    ("WOOL", 80, 12, 6),
    ("STRAWBERRY", 80, 16, 8),
    ("EGG", 40, 16, 8),
)


def _r11_early(obs, action):
    step = int(obs.get("step") or 0)
    if step not in _R11_WINDOW:
        return action
    private = obs.get("private") or {}
    shed = private.get("shed") or {}
    prices = ((obs.get("market") or {}).get("prices") or {})
    market = list(action.get("market") or [])
    already = {}
    for o in market:
        if isinstance(o, (list, tuple)) and len(o) >= 3 and o[0] == "SELL":
            already[o[1]] = already.get(o[1], 0) + int(o[2] or 0)
    changed = False
    for item, min_price, min_stock, slice_qty in _R11_RULES:
        if len(market) >= 10:
            break
        price = int(prices.get(item) or 1)
        stock = int(shed.get(item) or 0)
        avail = stock - already.get(item, 0)
        if price < min_price or avail < min_stock:
            continue
        qty = min(slice_qty, avail)
        if qty <= 0:
            continue
        merged = False
        for o in market:
            if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL" and o[1] == item:
                o[2] = int(o[2] or 0) + qty
                merged = True
                changed = True
                break
        if not merged:
            market.append(["SELL", item, qty])
            changed = True
    if not changed:
        return action
    result = dict(action)
    result["market"] = market[:10]
    return result


def agent(observation, configuration=None):
    action = _R11_PARENT(observation, configuration)
    try:
        return _r11_early(observation, action)
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
  "id": "ziyiming/kaggriculture-medal-r11",
  "title": "Kaggriculture Medal R11",
  "code_file": "main.py",
  "enable_gpu": false,
  "kernel_type": "script"
}
""",
    encoding="utf-8",
)
print("meta ok")
