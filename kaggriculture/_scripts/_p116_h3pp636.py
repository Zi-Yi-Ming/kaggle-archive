# -*- coding: utf-8 -*-
"""P116: dual-gate H3++ (start=636, best of p114) and package with p97d overlay."""
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import tarfile
from contextlib import redirect_stdout
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "p79", r"D:\桌面\Kaggle\kaggriculture\_scripts\_p79_mass_gate_vs_thomas.py"
)
p79 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p79)

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
METAV4 = PROJ / "_push_metav4_v13" / "main.py"
SHOPV7 = PROJ / "_external/p70_extracted/kaggriculture_shop_router_reactive_v7__0.py"
THOMAS = PROJ / "_push_thomas_2945" / "main.py"
OUTJSON = PROJ / "_research" / "p116_h3pp636.json"
PUSH = PROJ / "_push_h3pp_term636"

OVERLAY = r'''
# === P116 H3++ terminal overlay (start 636) ===
_P97_CASH = ("STRAWBERRY", "MELON", "MILK", "WOOL", "EGG", "TOMATO", "CARROT")
_P97_PARENT = agent
del agent

def agent(observation, configuration=None):
    action = _P97_PARENT(observation, configuration)
    try:
        step = int(observation.get("step", 0))
        if step < 636 or not isinstance(action, dict):
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


def load_mv(tag: str):
    code = METAV4.read_text(encoding="utf-8", errors="ignore")
    ns = {"__name__": tag, "__file__": str(METAV4), "__builtins__": __builtins__}
    exec(compile(code, str(METAV4), "exec"), ns)
    fn = ns.get("agent")
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)

    def agent(obs, configuration=None):
        return fn(obs) if n <= 1 else fn(obs, configuration)

    return agent


def call(fn, obs, configuration=None):
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)
    return fn(obs, configuration) if n > 1 else fn(obs, obs and configuration)


def make_636(tag):
    parent = load_mv(tag)

    def agent(obs, configuration=None):
        action = call(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            if step < 636 or not isinstance(action, dict):
                return action
            m = [list(o) for o in (action.get("market") or [])]
            already = {o[1] for o in m if len(o) >= 2 and o[0] == "SELL"}
            shed = dict(((obs.get("private") or {}).get("shed") or {}))
            prices = (obs.get("market") or {}).get("prices") or {}
            for item in ("STRAWBERRY", "MELON", "MILK", "WOOL", "EGG", "TOMATO", "CARROT"):
                if item in already:
                    continue
                stock = int(shed.get(item, 0) or 0)
                if stock <= 0 or int(prices.get(item, 0) or 0) < 1:
                    continue
                if len(m) >= 10:
                    break
                m.append(["SELL", item, min(stock, 60)])
                already.add(item)
            return dict(action, market=m) if m else action
        except Exception:
            return action

    return agent


def series(make_cand, opp_path, seeds, label):
    wins = 0
    margins = []
    rows = []
    for seed in seeds:
        for seat0 in (True, False):
            try:
                c = make_cand(f"c_{label}_{seed}_{int(seat0)}")
                o = p79.load_quiet(opp_path, f"o_{label}_{seed}_{int(seat0)}")
                if seat0:
                    b0, b1, stt, sec = p79.run(c, o, seed)
                    cb, ob = b0, b1
                else:
                    b0, b1, stt, sec = p79.run(o, c, seed)
                    ob, cb = b0, b1
                margin = cb - ob
                win = cb > ob
                wins += int(win)
                margins.append(margin)
                rows.append({"seed": seed, "margin": margin, "win": win, "cand": cb, "opp": ob})
                print(f"{label} s={seed} seat0={seat0} {cb:.0f}:{ob:.0f} m={margin:.0f} win={win}", flush=True)
            except Exception as e:
                print(f"FAIL {label} s={seed}: {e}", flush=True)
    n = len(margins)
    return {"n": n, "wins": wins, "win_rate": (wins / n) if n else 0,
            "mean_margin": (sum(margins) / n) if n else None, "rows": rows}


def main():
    payload = {}
    rec = payload["h3pp636"] = {}
    for opp_name, opp_path, seeds, key in (
        ("metav4", METAV4, (1, 2, 3, 4, 5, 6, 7, 8), "metav4"),
        ("shopv7", SHOPV7, (1, 2, 3, 4, 5, 6), "shop"),
        ("thomas", THOMAS, (1, 2, 3), "thomas"),
    ):
        print(f"\n== h3pp636 vs {opp_name} ==", flush=True)
        rec[key] = series(make_636, opp_path, seeds, f"h3pp_{opp_name}")
        print("SUM", key, rec[key]["win_rate"], rec[key]["mean_margin"], flush=True)

    mv, sh = rec["metav4"], rec["shop"]
    dual = mv.get("win_rate", 0) >= 0.6 and sh.get("win_rate", 0) >= 0.5
    rec["dual_gate"] = "PASS" if dual else "FAIL"
    print("DUAL", rec["dual_gate"], flush=True)

    if dual:
        base = METAV4.read_text(encoding="utf-8", errors="ignore")
        code = base + OVERLAY
        PUSH.mkdir(parents=True, exist_ok=True)
        main_py = PUSH / "main.py"
        main_py.write_text(code, encoding="utf-8")
        sha = hashlib.sha256(code.encode()).hexdigest()
        tar = PUSH / "submission.tar.gz"
        with tarfile.open(tar, "w:gz") as tf:
            tf.add(main_py, arcname="main.py")
        ns = {"__name__": "pkg", "__file__": str(main_py), "__builtins__": __builtins__}
        with redirect_stdout(io.StringIO()):
            exec(compile(code, "main.py", "exec"), ns)
        rec["package"] = str(tar)
        rec["sha"] = sha[:16]
        print("PACKAGED", tar, tar.stat().st_size, "load OK", ns.get("agent"), flush=True)

    OUTJSON.write_text(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "rows"} for k, v in payload.items()}, indent=2), encoding="utf-8")
    print("WROTE", OUTJSON, flush=True)


if __name__ == "__main__":
    main()
