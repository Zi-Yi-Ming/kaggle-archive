# -*- coding: utf-8 -*-
"""Build tetsu R6: fertilizer collect-boost + proactive fert sales overlay."""
from pathlib import Path
import ast

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
src = ROOT / "_external" / "top5_notebooks" / "tetsu2131" / "tetsu2131_main.py"
dst_dir = ROOT / "_push_tetsu_r6"
dst_dir.mkdir(parents=True, exist_ok=True)
dst = dst_dir / "main.py"

text = src.read_text(encoding="utf-8")
if "TETSU_R6_FERT" not in text:
    overlay = r'''

# ---------------------------------------------------------------------------
# TETSU_R6_FERT: collect-boost + proactive fertilizer sales
# ---------------------------------------------------------------------------
_R6_PARENT = agent
_R6_KEEP_FERT = 0          # sell down to this buffer
_R6_SELL_IF_PRICE = 2
_R6_MIN_BATCH = 4
# Never override these unit commands (survival / cash-critical)
_R6_KEEP_CMDS = {
    ("FEED",), ("CARE",), ("HARVEST",), ("DIG",),
    ("PICKUP", "WHEAT"), ("DROP",),
}


def _r6_is_keep(cmd):
    if not cmd:
        return True
    t = tuple(cmd)
    if t in _R6_KEEP_CMDS:
        return True
    if t[0] in ("BUY_LAND", "BUY_ANIMAL", "BUY_PRODUCT", "BUY_SEED"):
        return True
    # keep planned FEED/CARE/HARVEST/PICKUP WHEAT
    if t[0] in ("FEED", "CARE", "HARVEST", "DIG"):
        return True
    if t[0] == "PICKUP" and len(t) > 1 and t[1] == "WHEAT":
        return True
    return False


def _r6_overlay(obs, action):
    step = int(obs.get("step") or 0)
    if step >= 716:
        return action
    seat = int(obs.get("player") or 0)
    farms = obs.get("farms") or []
    if seat >= len(farms):
        return action
    farm = farms[seat] or {}
    private = obs.get("private") or {}
    shed = {k: int(v or 0) for k, v in (private.get("shed") or {}).items()}
    inventories = list(private.get("inventories") or [])
    positions = [farm.get("farmer") or [4, 4], *(farm.get("hands") or [])]
    tiles = farm.get("tiles") or []

    def tile_at(pos):
        try:
            x, y = int(pos[0]), int(pos[1])
            return tiles[y][x]
        except Exception:
            return None

    result = dict(action)
    cmds = [result.get("farmer") or ["PASS"], *list(result.get("hands") or [])]
    # Pad / trim to positions
    while len(cmds) < len(positions):
        cmds.append(["PASS"])
    cmds = cmds[: len(positions)]

    for actor, pos in enumerate(positions):
        if actor >= len(cmds):
            break
        if _r6_is_keep(cmds[actor]):
            continue
        tile = tile_at(pos)
        if isinstance(tile, dict) and tile.get("fertilizer_available"):
            # only steal the action if worker is not doing something more valuable
            # (already filtered keep-cmds). PASS / MOVE / plant-ish get replaced.
            cmds[actor] = ["COLLECT_FERTILIZER"]

    result["farmer"] = cmds[0]
    result["hands"] = cmds[1:]

    # Proactive fertilizer sale
    prices = ((obs.get("market") or {}).get("prices") or {})
    price = int(prices.get("FERTILIZER") or 1)
    stock = shed.get("FERTILIZER", 0)
    # include carried fert that will drop EOD? conservative: shed only
    market = [list(o) for o in (result.get("market") or [])]
    already = sum(
        int(o[2] or 0) for o in market if o and o[0] == "SELL" and len(o) > 2 and o[1] == "FERTILIZER"
    )
    excess = max(0, stock - already - _R6_KEEP_FERT)
    if excess >= _R6_MIN_BATCH and price >= _R6_SELL_IF_PRICE and len(market) < 10:
        # merge into existing FERT sell if present
        merged = False
        for o in market:
            if o and o[0] == "SELL" and len(o) > 2 and o[1] == "FERTILIZER":
                o[2] = int(o[2] or 0) + excess
                merged = True
                break
        if not merged:
            market.append(["SELL", "FERTILIZER", excess])
    result["market"] = market[:10]
    return result


def agent(observation, configuration=None):
    action = _R6_PARENT(observation)
    try:
        return _r6_overlay(observation, action)
    except Exception:
        return action
'''
    text = text + "\n" + overlay + "\n"

dst.write_text(text, encoding="utf-8")
ast.parse(dst.read_text(encoding="utf-8"))
print("wrote", dst, dst.stat().st_size)

(dst_dir / "kernel-metadata.json").write_text(
    """{
  "competition_sources": ["kaggriculture"],
  "language": "python",
  "enable_internet": false,
  "is_private": true,
  "id": "ziyiming/kaggriculture-tetsu-r6-fert",
  "title": "Kaggriculture tetsu R6 fert",
  "code_file": "main.py",
  "enable_gpu": false,
  "kernel_type": "script"
}
""",
    encoding="utf-8",
)
print("meta ok")
