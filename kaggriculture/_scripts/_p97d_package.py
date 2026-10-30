# -*- coding: utf-8 -*-
"""P97d: build submit-ready packages H3/H4 (NO auto-submit)."""
from __future__ import annotations

import hashlib
import tarfile
from pathlib import Path

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
METAV4 = PROJ / "_push_metav4_v13" / "main.py"
base = METAV4.read_text(encoding="utf-8", errors="ignore")

OVERLAY_H3 = r'''
# === ORIGINAL P97b terminal cash-greedy overlay (day27+) ===
_P97_CASH = ("STRAWBERRY", "MELON", "MILK", "WOOL", "EGG", "TOMATO", "CARROT")
_P97_PARENT = agent
del agent

def agent(observation, configuration=None):
    action = _P97_PARENT(observation, configuration)
    try:
        step = int(observation.get("step", 0))
        if step < 648 or not isinstance(action, dict):
            return action
        market = [list(o) for o in (action.get("market") or [])]
        already = {o[1] for o in market if len(o) >= 2 and o[0] == "SELL"}
        shed = dict(((observation.get("private") or {}).get("shed") or {}))
        prices = (observation.get("market") or {}).get("prices") or {}
        added = False
        for item in _P97_CASH:
            if item in already:
                continue
            stock = int(shed.get(item, 0) or 0)
            if stock <= 0 or int(prices.get(item, 0) or 0) < 1:
                continue
            if len(market) >= 10:
                break
            market.append(["SELL", item, min(stock, 60)])
            added = True
        if added:
            action = dict(action, market=market)
    except Exception:
        pass
    return action

agent.telemetry = getattr(_P97_PARENT, "telemetry", {})
agent = globals().pop("agent")
'''

OVERLAY_H4 = r'''
# === ORIGINAL P97b terminal combo overlay (cap+lead+greedy) ===
_P97_CASH = ("STRAWBERRY", "MELON", "MILK", "WOOL", "EGG", "TOMATO", "CARROT")
_P97_PARENT = agent
del agent

def agent(observation, configuration=None):
    action = _P97_PARENT(observation, configuration)
    try:
        step = int(observation.get("step", 0))
        if step < 624 or not isinstance(action, dict):
            return action
        market = [list(o) for o in (action.get("market") or [])]
        changed = False
        for o in market:
            if len(o) >= 3 and o[0] == "SELL" and o[1] in _P97_CASH and int(o[2] or 0) >= 120:
                o[2] = 80
                changed = True
        already = {o[1] for o in market if len(o) >= 2 and o[0] == "SELL"}
        shed = dict(((observation.get("private") or {}).get("shed") or {}))
        prices = (observation.get("market") or {}).get("prices") or {}
        for item in _P97_CASH:
            if item in already:
                continue
            stock = int(shed.get(item, 0) or 0)
            if stock <= 0:
                continue
            if step >= 648:
                if int(prices.get(item, 0) or 0) < 1:
                    continue
                qty = min(stock, 60)
            elif step >= 576 and int(prices.get(item, 0) or 0) >= 2:
                qty = min(stock, 40)
            else:
                continue
            if len(market) >= 10:
                break
            market.append(["SELL", item, qty])
            changed = True
        if changed:
            action = dict(action, market=market)
    except Exception:
        pass
    return action

agent.telemetry = getattr(_P97_PARENT, "telemetry", {})
agent = globals().pop("agent")
'''

for name, ov in (("h3_term_greedy", OVERLAY_H3), ("h4_term_combo", OVERLAY_H4)):
    out = PROJ / f"_push_{name}"
    out.mkdir(parents=True, exist_ok=True)
    code = base + ov
    (out / "main.py").write_text(code, encoding="utf-8")
    sha = hashlib.sha256(code.encode()).hexdigest()
    tar = out / "submission.tar.gz"
    with tarfile.open(tar, "w:gz") as tf:
        tf.add(out / "main.py", arcname="main.py")
    print(name, "bytes", len(code), "sha", sha, "tar", tar.stat().st_size)

# smoke load H3
import importlib.util
import io
from contextlib import redirect_stdout

ns = {"__name__": "pkg_h3", "__file__": str(PROJ / "_push_h3_term_greedy" / "main.py"), "__builtins__": __builtins__}
with redirect_stdout(io.StringIO()):
    exec(compile((PROJ / "_push_h3_term_greedy" / "main.py").read_text(encoding="utf-8"), "main.py", "exec"), ns)
print("H3 load OK", ns.get("agent"))
