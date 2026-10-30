# -*- coding: utf-8 -*-
"""Build Medal R4: Medal R2 + multi-turn endgame liquidation overlay.

Rationale:
- Original only liquidates at LAST_STEP=718.
- Reports suggest the final turn may not fully execute, and late harvests
  after 718 can strand inventory (unsold shed has $0 value).
- R4 dumps remaining sellable stock over the last ~2 days in price-aware batches.

Local gate: must beat Medal R2 on paired seeds or we do not submit.
"""
from pathlib import Path
import shutil
import ast

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
src = ROOT / "_push_medal" / "main.py"
dst_dir = ROOT / "_push_medal_r4"
dst_dir.mkdir(parents=True, exist_ok=True)
dst = dst_dir / "main.py"

text = src.read_text(encoding="utf-8")

# Avoid double-append if re-run
if "MEDAL_R4_ENDGAME" not in text:
    overlay = r'''

# ---------------------------------------------------------------------------
# MEDAL_R4_ENDGAME: multi-turn endgame liquidation overlay
# ---------------------------------------------------------------------------
_R4_DUMP_START = 696          # day 29 hour 0 — hard dump window
_R4_SOFT_START = 672          # day 28 hour 0 — soft premium dump
_R4_PREMIUM = ("MELON", "STRAWBERRY", "MILK", "WOOL", "EGG", "TOMATO")
_R4_SELLABLE = (
    "WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
    "EGG", "MILK", "WOOL", "FERTILIZER",
)

_R4_PARENT = agent


def _r4_shed_view(obs):
    private = obs.get("private") or {}
    shed = private.get("shed") or {}
    prices = ((obs.get("market") or {}).get("prices") or {})
    return {k: int(v or 0) for k, v in shed.items()}, {k: int(prices.get(k, 1) or 1) for k in _R4_SELLABLE}


def _r4_endgame(obs, action):
    step = int(obs.get("step") or 0)
    if step < _R4_SOFT_START:
        return action
    shed, prices = _r4_shed_view(obs)
    orders = list(action.get("market") or [])
    already = {o[1] for o in orders if o and o[0] == "SELL" and len(o) > 1}

    def remaining(item):
        scheduled = sum(int(o[2] or 0) for o in orders if o and o[:2] == ["SELL", item] and len(o) >= 3)
        return max(0, shed.get(item, 0) - scheduled)

    # Hard dump last day+: everything left, premium first by $ value
    if step >= _R4_DUMP_START:
        items = sorted(
            [i for i in _R4_SELLABLE if remaining(i) > 0 and i not in already],
            key=lambda i: -(prices.get(i, 1) * remaining(i)),
        )
        for item in items:
            if len(orders) >= 10:
                break
            qty = remaining(item)
            if qty > 0:
                orders.append(["SELL", item, qty])
        action = dict(action)
        action["market"] = orders[:10]
        return action

    # Soft dump day 28: only premium goods sitting in shed, metered
    for item in _R4_PREMIUM:
        if len(orders) >= 10:
            break
        if item in already:
            continue
        qty = remaining(item)
        if qty <= 0:
            continue
        price = prices.get(item, 1)
        # At floor, dump harder (won't get better); mid price dump half; high dump quarter
        if price <= 2:
            sell = qty
        elif price >= 40:
            sell = max(1, qty // 4)
        else:
            sell = max(1, qty // 2)
        orders.append(["SELL", item, sell])
    action = dict(action)
    action["market"] = orders[:10]
    return action


def agent(observation, configuration=None):
    action = _R4_PARENT(observation, configuration)
    try:
        return _r4_endgame(observation, action)
    except Exception:
        return action
'''
    # insert overlay after final kaggle_agent=agent line if present, else append
    if "kaggle_agent=agent" in text:
        text = text.replace("kaggle_agent=agent", "kaggle_agent=agent\n" + overlay + "\nkaggle_agent=agent\n", 1)
    else:
        text = text + overlay

dst.write_text(text, encoding="utf-8")
ast.parse(dst.read_text(encoding="utf-8"))
print("wrote", dst, "bytes", dst.stat().st_size)

meta = '''{
  "competition_sources": ["kaggriculture"],
  "language": "python",
  "enable_internet": false,
  "is_private": true,
  "id": "ziyiming/kaggriculture-medal-r4",
  "title": "Kaggriculture Medal R4 Endgame",
  "code_file": "main.py",
  "enable_gpu": false,
  "kernel_type": "script"
}
'''
(dst_dir / "kernel-metadata.json").write_text(meta, encoding="utf-8")
print("meta ok")
