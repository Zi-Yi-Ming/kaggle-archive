# -*- coding: utf-8 -*-
"""P115: rebuild H3+ package using proven p97d overlay pattern (start=624)."""
from __future__ import annotations

import hashlib
import importlib.util
import io
import tarfile
from contextlib import redirect_stdout
from pathlib import Path

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
METAV4 = PROJ / "_push_metav4_v13" / "main.py"
base = METAV4.read_text(encoding="utf-8", errors="ignore")

# Same as working H3 overlay but START=624 instead of 648
OVERLAY_H3PLUS = r'''
# === P109b H3+ terminal cash-greedy overlay (start 624) ===
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


def main():
    out = PROJ / "_push_h3plus_term624"
    out.mkdir(parents=True, exist_ok=True)
    code = base + OVERLAY_H3PLUS
    main_py = out / "main.py"
    main_py.write_text(code, encoding="utf-8")
    sha = hashlib.sha256(code.encode()).hexdigest()
    tar = out / "submission.tar.gz"
    with tarfile.open(tar, "w:gz") as tf:
        tf.add(main_py, arcname="main.py")
    print("H3+ bytes", len(code), "sha", sha[:16], "tar", tar.stat().st_size, flush=True)

    # smoke load exactly like p97d
    ns = {"__name__": "pkg_h3plus", "__file__": str(main_py), "__builtins__": __builtins__}
    with redirect_stdout(io.StringIO()):
        exec(compile(code, "main.py", "exec"), ns)
    agent = ns.get("agent")
    print("load OK", agent, flush=True)
    # call once with a dummy obs
    obs = {"step": 650, "private": {"shed": {"MELON": 30, "WHEAT": 5}}, "market": {"prices": {"MELON": 200}}}
    act = agent(obs, None)
    print("act", act, flush=True)
    assert isinstance(act, dict)
    print("SMOKE PASS", flush=True)


if __name__ == "__main__":
    main()
