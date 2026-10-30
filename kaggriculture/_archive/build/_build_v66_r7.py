# -*- coding: utf-8 -*-
from pathlib import Path
import shutil
import ast

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
src_dir = ROOT / "_external" / "git" / "v66"
dst_dir = ROOT / "_push_v66_r7"

# force clean
if dst_dir.exists():
    shutil.rmtree(dst_dir, ignore_errors=True)
# wait / rename leftover
if dst_dir.exists():
    alt = ROOT / "_push_v66_r7_old"
    if alt.exists():
        shutil.rmtree(alt, ignore_errors=True)
    try:
        dst_dir.rename(alt)
    except Exception as e:
        print("rename leftover failed", e)

shutil.copytree(
    src_dir,
    dst_dir,
    ignore=shutil.ignore_patterns(".git", "*.tar.gz", "__pycache__", "build_submission.py"),
)

main_p = dst_dir / "main.py"
text = main_p.read_text(encoding="utf-8")
if "V66_R7_FERT" not in text:
    overlay = r'''

# ---------------------------------------------------------------------------
# V66_R7_FERT: market-only fertilizer sell boost (no unit-action stealing)
# ---------------------------------------------------------------------------
_R7_PARENT = agent
_R7_MIN_STOCK = 6
_R7_MIN_PRICE = 2


def _r7_fert(obs, action):
    step = int(obs.get("step") or 0)
    if step >= 716 or step < 96:
        return action
    private = obs.get("private") or {}
    shed = private.get("shed") or {}
    stock = int(shed.get("FERTILIZER") or 0)
    if stock < _R7_MIN_STOCK:
        return action
    prices = ((obs.get("market") or {}).get("prices") or {})
    price = int(prices.get("FERTILIZER") or 1)
    if price < _R7_MIN_PRICE:
        return action
    market = [list(o) for o in (action.get("market") or [])]
    already = sum(
        int(o[2] or 0) for o in market if o and o[0] == "SELL" and len(o) > 2 and o[1] == "FERTILIZER"
    )
    excess = stock - already
    if excess < 4 or len(market) >= 10:
        return action
    merged = False
    for o in market:
        if o and o[0] == "SELL" and len(o) > 2 and o[1] == "FERTILIZER":
            o[2] = int(o[2] or 0) + excess
            merged = True
            break
    if not merged:
        market.append(["SELL", "FERTILIZER", excess])
    result = dict(action)
    result["market"] = market[:10]
    return result


def agent(observation, configuration=None):
    action = _R7_PARENT(observation, configuration)
    try:
        return _r7_fert(observation, action)
    except Exception:
        return action
'''
    text = text + overlay
    main_p.write_text(text, encoding="utf-8")

ast.parse(main_p.read_text(encoding="utf-8"))
print("OK", dst_dir, "files", len(list(dst_dir.iterdir())), "main", main_p.stat().st_size)
