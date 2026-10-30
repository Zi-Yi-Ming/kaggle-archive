# -*- coding: utf-8 -*-
"""Medal R12: mid-game milk price floor (quantity reduce, no reorder).

Hypothesis from live d15-21 analysis:
- Wins sell MILK at 116-178
- Losses sell MILK at 10-66
R12 shrinks MILK SELL qty when quoted price < floor, leaving stock for
a later high window or the d29 dump. Does not reorder the market queue.
"""
from pathlib import Path
import ast

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
src = ROOT / "_push_medal" / "main.py"
dst_dir = ROOT / "_push_medal_r12"
dst_dir.mkdir(parents=True, exist_ok=True)
dst = dst_dir / "main.py"

text = src.read_text(encoding="utf-8")
if "MEDAL_R12_MILKFLOOR" not in text:
    overlay = r'''

# ---------------------------------------------------------------------------
# MEDAL_R12_MILKFLOOR: hold milk when price is low (d12-27)
# ---------------------------------------------------------------------------
_R12_PARENT = agent
_R12_FLOOR = 55          # skip/reduce milk sells below this price
_R12_START, _R12_END = 288, 672  # day 12 .. day 28 start
_R12_MIN_KEEP = 0        # sell down to this when price >= floor


def _r12_milk_floor(obs, action):
    step = int(obs.get("step") or 0)
    if step < _R12_START or step >= _R12_END:
        return action
    prices = ((obs.get("market") or {}).get("prices") or {})
    price = int(prices.get("MILK") or 1)
    if price >= _R12_FLOOR:
        return action
    market = action.get("market") or []
    changed = False
    new_market = []
    for o in market:
        if (
            isinstance(o, list)
            and len(o) >= 3
            and o[0] == "SELL"
            and o[1] == "MILK"
        ):
            # drop the milk sell entirely at low price
            changed = True
            continue
        new_market.append(o)
    if not changed:
        return action
    result = dict(action)
    result["market"] = new_market[:10]
    return result


def agent(observation, configuration=None):
    action = _R12_PARENT(observation, configuration)
    try:
        return _r12_milk_floor(observation, action)
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
  "id": "ziyiming/kaggriculture-medal-r12",
  "title": "Kaggriculture Medal R12",
  "code_file": "main.py",
  "enable_gpu": false,
  "kernel_type": "script"
}
""",
    encoding="utf-8",
)
print("meta ok")
