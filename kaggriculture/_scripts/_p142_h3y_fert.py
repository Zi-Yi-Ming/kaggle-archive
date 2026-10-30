# -*- coding: utf-8 -*-
"""P142: H3y = H3x + aggressive fert collection+sell (the mirror-match 白饭 edge).

Evidence: winners sell ~2358 fert vs our 1357 (delta ~1000 = the loss gap).
"""
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
PUSH = PROJ / "_push_h3y_fert"
OUTJSON = PROJ / "_research" / "p142_h3y.json"
CASH = ("STRAWBERRY", "MELON", "MILK", "WOOL", "EGG", "TOMATO", "CARROT")

OVERLAY = r'''
# === P142 H3y: H3x terminal + aggressive fert collect/sell (白饭) ===
_P97_CASH = ("STRAWBERRY", "MELON", "MILK", "WOOL", "EGG", "TOMATO", "CARROT")
_P97_PARENT = agent
del agent

def agent(observation, configuration=None):
    action = _P97_PARENT(observation, configuration)
    try:
        step = int(observation.get("step", 0))
        day, hour = step // 24, step % 24
        if not isinstance(action, dict):
            return action
        market = [list(o) for o in (action.get("market") or [])]
        farmer = list(action.get("farmer") or ["PASS"])
        hands = [list(h) for h in (action.get("hands") or [])]
        shed = dict(((observation.get("private") or {}).get("shed") or {}))
        prices = (observation.get("market") or {}).get("prices") or {}

        # 1) always sell fert (白饭 cash)
        fert = int(shed.get("FERTILIZER") or 0)
        if fert > 0 and not any(len(o) >= 2 and o[0] == "SELL" and o[1] == "FERTILIZER" for o in market):
            market.append(["SELL", "FERTILIZER", fert])

        # 2) morning fert run: force collect on PASS slots h2-h4 (gold path to 3,3)
        if 2 <= hour <= 4 and day >= 1:
            if farmer[:1] in (["PASS"],) or farmer[0] in ("PASS", "WEST", "NORTH"):
                farmer = ["COLLECT_FERTILIZER"] if hour == 4 else (["WEST"] if hour == 2 else ["NORTH"])
            changed = False
            for i in range(len(hands)):
                if hands[i][:1] in (["PASS"],):
                    hands[i] = ["COLLECT_FERTILIZER"]
                    changed = True

        # 3) H3x terminal
        if step >= 642:
            already = {o[1] for o in market if len(o) >= 2 and o[0] == "SELL"}
            for item in _P97_CASH:
                if item in already:
                    continue
                stock = int(shed.get(item, 0) or 0)
                if stock <= 0 or int(prices.get(item, 0) or 0) < 1:
                    continue
                if len(market) >= 10:
                    break
                market.append(["SELL", item, min(stock, 60)])
                already.add(item)

        action = dict(action, market=market, farmer=farmer, hands=hands)
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


def make_h3y(tag, start=642):
    parent = load_mv(tag)

    def agent(obs, configuration=None):
        action = call(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            day, hour = step // 24, step % 24
            if not isinstance(action, dict):
                return action
            market = [list(o) for o in (action.get("market") or [])]
            farmer = list(action.get("farmer") or ["PASS"])
            hands = [list(h) for h in (action.get("hands") or [])]
            shed = dict(((obs.get("private") or {}).get("shed") or {}))
            prices = (obs.get("market") or {}).get("prices") or {}
            fert = int(shed.get("FERTILIZER") or 0)
            if fert > 0 and not any(len(o) >= 2 and o[0] == "SELL" and o[1] == "FERTILIZER" for o in market):
                market.append(["SELL", "FERTILIZER", fert])
            if 2 <= hour <= 4 and day >= 1:
                if farmer[:1] in (["PASS"],):
                    farmer = ["COLLECT_FERTILIZER"] if hour == 4 else (["WEST"] if hour == 2 else ["NORTH"])
                for i in range(len(hands)):
                    if hands[i][:1] in (["PASS"],):
                        hands[i] = ["COLLECT_FERTILIZER"]
            if step >= start:
                already = {o[1] for o in market if len(o) >= 2 and o[0] == "SELL"}
                for item in CASH:
                    if item in already:
                        continue
                    stock = int(shed.get(item, 0) or 0)
                    if stock <= 0 or int(prices.get(item, 0) or 0) < 1:
                        continue
                    if len(market) >= 10:
                        break
                    market.append(["SELL", item, min(stock, 60)])
                    already.add(item)
            return dict(action, market=market, farmer=farmer, hands=hands)
        except Exception:
            return action

    return agent


def series(make_cand, opp_path, seeds, label):
    wins = 0
    margins = []
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
                print(f"{label} s={seed} seat0={seat0} {cb:.0f}:{ob:.0f} m={margin:.0f} win={win}", flush=True)
            except Exception as e:
                print(f"FAIL {label} s={seed}: {e}", flush=True)
    n = len(margins)
    return {"n": n, "wins": wins, "win_rate": (wins / n) if n else 0,
            "mean_margin": (sum(margins) / n) if n else None}


def main():
    payload = {}
    rec = payload["h3y"] = {}
    for opp_name, opp_path, seeds, key in (
        ("metav4", METAV4, (1, 2, 3, 4, 5, 6), "metav4"),
        ("shopv7", SHOPV7, (1, 2, 3, 4), "shop"),
    ):
        print(f"\n== h3y vs {opp_name} ==", flush=True)
        rec[key] = series(make_h3y, opp_path, seeds, f"h3y_{opp_name}")
        print("SUM", key, rec[key], flush=True)
        if key == "shop" and rec[key].get("win_rate", 0) < 0.5:
            rec["verdict"] = "NO shop"
            OUTJSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            return
    mv, sh = rec["metav4"], rec["shop"]
    rec["verdict"] = "DUAL PASS" if (mv.get("win_rate", 0) >= 0.6 and sh.get("win_rate", 0) >= 0.5) else f"NO {mv} {sh}"
    print("VERDICT", rec["verdict"], flush=True)

    if rec["verdict"] == "DUAL PASS":
        code = METAV4.read_text(encoding="utf-8", errors="ignore") + OVERLAY
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
        print("PACKAGED", tar, tar.stat().st_size, flush=True)

    OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("WROTE", OUTJSON, flush=True)


if __name__ == "__main__":
    main()
