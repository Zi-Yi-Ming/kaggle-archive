# -*- coding: utf-8 -*-
"""Build Medal R8: multi-turn endgame dump + premium-first queue on R2.

Mirror-meta insight: at 2300+ almost everyone is shop-router. Losses are
1.5k-3k. Opponents like kurushun dump harder on day 29.
R8 dumps remaining shed from step 704 every turn and reorders premium sells first.
"""
from pathlib import Path
import ast

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
src = ROOT / "_push_medal" / "main.py"
dst_dir = ROOT / "_push_medal_r8"
dst_dir.mkdir(parents=True, exist_ok=True)
dst = dst_dir / "main.py"

text = src.read_text(encoding="utf-8")
if "MEDAL_R8_DUMP" not in text:
    overlay = r'''

# ---------------------------------------------------------------------------
# MEDAL_R8_DUMP: endgame multi-turn dump + premium-first sell ordering
# ---------------------------------------------------------------------------
_R8_PARENT = agent
_R8_DUMP_FROM = 704  # day 29 hour 8
_R8_SELLABLE = (
    "MELON", "WOOL", "MILK", "STRAWBERRY", "EGG",
    "TOMATO", "FERTILIZER", "CARROT", "WHEAT",
)
_R8_PREMIUM = {"MELON", "WOOL", "MILK", "STRAWBERRY", "EGG"}


def _r8_is_sell(o):
    return isinstance(o, (list, tuple)) and len(o) >= 2 and o[0] == "SELL"


def _r8_reorder(orders):
    prem, other, rest = [], [], []
    for o in orders:
        if _r8_is_sell(o) and len(o) > 1 and o[1] in _R8_PREMIUM:
            prem.append(o)
        elif _r8_is_sell(o):
            other.append(o)
        else:
            rest.append(o)
    return prem + other + rest


def _r8_endgame(obs, action):
    step = int(obs.get("step") or 0)
    if step < _R8_DUMP_FROM:
        return action
    private = obs.get("private") or {}
    shed = private.get("shed") or {}
    market = [list(o) for o in (action.get("market") or [])]
    already = {}
    for o in market:
        if _r8_is_sell(o) and len(o) > 2:
            already[o[1]] = already.get(o[1], 0) + int(o[2] or 0)
    for item in _R8_SELLABLE:
        if len(market) >= 10:
            break
        stock = int(shed.get(item) or 0)
        excess = stock - already.get(item, 0)
        if excess <= 0:
            continue
        merged = False
        for o in market:
            if _r8_is_sell(o) and len(o) > 2 and o[1] == item:
                o[2] = int(o[2] or 0) + excess
                merged = True
                break
        if not merged:
            market.append(["SELL", item, excess])
    action = dict(action)
    action["market"] = _r8_reorder(market)[:10]
    return action


def agent(observation, configuration=None):
    action = _R8_PARENT(observation, configuration)
    try:
        action = _r8_endgame(observation, action)
        if isinstance(action, dict) and action.get("market"):
            action = dict(action)
            action["market"] = _r8_reorder(action["market"])[:10]
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
  "id": "ziyiming/kaggriculture-medal-r8",
  "title": "Kaggriculture Medal R8",
  "code_file": "main.py",
  "enable_gpu": false,
  "kernel_type": "script"
}
""",
    encoding="utf-8",
)
print("meta ok")
