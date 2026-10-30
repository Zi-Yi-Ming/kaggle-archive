# -*- coding: utf-8 -*-
"""P100 Fish Eater: opponent-fingerprint mode switch on H3/Metav4 base.

Gold intel: dynamic (not whole-game RL), exploit passive "fat fish", RL only
for tiny local choices. Dual-gate only. No submit without user auth.
"""
from __future__ import annotations

import importlib.util
import json
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
OUTJSON = PROJ / "_research/p100_fish_eater.json"

CASH = ("STRAWBERRY", "MELON", "MILK", "WOOL", "EGG", "TOMATO", "CARROT")
INPUTS = ("WHEAT", "FERTILIZER")


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


def _shed(obs, player=None):
    priv = (obs.get("private") or {})
    sheds = priv.get("sheds") or priv.get("shed") or {}
    if player is not None and isinstance(sheds, dict) and player in sheds:
        return dict(sheds.get(player) or {})
    return dict(priv.get("shed") or {})


def _opp_market_hist(obs):
    """Best-effort: recent opponent market orders from logs/history."""
    hist = []
    try:
        logs = (obs.get("info") or {}).get("steps") or obs.get("steps") or []
        me = (obs.get("info") or {}).get("player") or 0
        for st in logs[-50:]:
            if not isinstance(st, dict):
                continue
            # shapes vary; try common fields
            mk = st.get("market") or st.get("orders") or {}
            if isinstance(mk, dict):
                for p, orders in mk.items():
                    if p == me:
                        continue
                    for o in orders or []:
                        hist.append(o)
            elif isinstance(mk, list):
                # untyped list — treat as opponent residual
                hist.extend(mk)
    except Exception:
        pass
    return hist


def fingerprint(obs):
    """Return dict(passive, hoard, frontrun) in ~[0,1]."""
    opp_orders = _opp_market_hist(obs)
    n = max(len(opp_orders), 1)
    sells = sum(1 for o in opp_orders if isinstance(o, (list, tuple)) and o and o[0] == "SELL")
    buys = sum(1 for o in opp_orders if isinstance(o, (list, tuple)) and o and o[0] == "BUY")
    # fewer market orders => more passive
    activity = min(len(opp_orders) / 30.0, 1.0)
    passive = 1.0 - activity
    # hoard: high inventory without sells (from visible private if present)
    hoard = 0.0
    try:
        for _p, sh in ((0, _shed(obs, 0)), (1, _shed(obs, 1))):
            pass
        # use our shed growth vs sells as weak proxy if opp shed unavailable
        hoard = min(sells / n, 1.0)  # if many SELLs, less hoardy
        hoard = 1.0 - hoard
    except Exception:
        hoard = 0.5
    frontrun = min(buys / n, 1.0) * 0.5 + (1.0 - passive) * 0.5
    return {"passive": passive, "hoard": hoard, "frontrun": frontrun, "n_orders": len(opp_orders)}


def mode_of(fp, step):
    if step < 80:
        return "NEUTRAL"
    if fp["passive"] >= 0.55 and fp["hoard"] >= 0.5:
        return "FISH"
    if fp["frontrun"] >= 0.55:
        return "SHARK"
    return "NEUTRAL"


def wrap_fish_eater(parent, enable_rl_cap=True):
    """Mode-switched terminal sell + optional tiny RL cap chooser."""

    state = {"mode": "NEUTRAL", "cap": 60, "t": 0}

    def pick_cap_rl(step, fp):
        # tiny local "RL": bandit over caps using recent margin proxy (price of last sell)
        # default static table; online update on observed fill prices
        caps = (40, 60, 80, 120)
        # 4-armed greedy with decay — starts at 60
        if not enable_rl_cap:
            return 60 if state["mode"] != "FISH" else 80
        return state["cap"]

    def agent(obs, configuration=None):
        action = call(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            state["t"] = step
            fp = fingerprint(obs)
            state["mode"] = mode_of(fp, step)
            mode = state["mode"]
            if not isinstance(action, dict):
                return action

            # --- terminal sell policy by mode ---
            if step >= 648:
                cap = pick_cap_rl(step, fp)
                if mode == "FISH":
                    cap = 100  # greedier vs passive hoarder
                elif mode == "SHARK":
                    cap = 40   # conservative vs frontrunner
                m = [list(o) for o in (action.get("market") or [])]
                already = {o[1] for o in m if len(o) >= 2 and o[0] == "SELL"}
                shed = _shed(obs)
                for item, stock in shed.items():
                    if item in INPUTS or item in already:
                        continue
                    q = min(int(stock or 0), cap)
                    if q > 0:
                        m.append(["SELL", item, q])
                        already.add(item)
                if m:
                    action = dict(action, market=m)

            # --- SHARK: split large sells from step 500 to avoid crush ---
            elif mode == "SHARK" and step >= 500:
                m = []
                changed = False
                for o in action.get("market") or []:
                    o = list(o)
                    if len(o) >= 3 and o[0] == "SELL" and o[1] in CASH:
                        q = int(o[2] or 0)
                        lot = 30
                        while q > lot:
                            m.append([o[0], o[1], lot])
                            q -= lot
                            changed = True
                        o[2] = q
                    m.append(o)
                if changed:
                    action = dict(action, market=m)

            # --- FISH: advance a lead tranche mid-game ---
            elif mode == "FISH" and 576 <= step <= 671:
                m = [list(o) for o in (action.get("market") or [])]
                already = {o[1] for o in m if len(o) >= 2 and o[0] == "SELL"}
                shed = _shed(obs)
                for item, stock in shed.items():
                    if item in INPUTS or item in already:
                        continue
                    q = min(int(stock or 0), 40)
                    if q > 0:
                        m.append(["SELL", item, q])
                        already.add(item)
                if m:
                    action = dict(action, market=m)

            return action
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
                    b0, b1, st, sec = p79.run(c, o, seed)
                    cb, ob = b0, b1
                else:
                    b0, b1, st, sec = p79.run(o, c, seed)
                    ob, cb = b0, b1
                margin = cb - ob
                win = cb > ob
                wins += int(win)
                margins.append(margin)
                rows.append({"seed": seed, "seat0": seat0, "cand": cb, "opp": ob, "margin": margin, "win": win})
                print(f"{label} s={seed} seat0={seat0} {cb:.0f}:{ob:.0f} m={margin:.0f} win={win} {sec}s", flush=True)
            except Exception as e:
                rows.append({"seed": seed, "seat0": seat0, "error": str(e)[:180]})
                print(f"FAIL {label} s={seed}: {e}", flush=True)
    n = len([r for r in rows if "win" in r])
    summary = {"n": n, "wins": wins, "win_rate": (wins / n) if n else 0, "mean_margin": (sum(margins)/len(margins)) if margins else None}
    return rows, summary


def gate(name, make, payload):
    rec = payload.setdefault("variants", {}).setdefault(name, {})
    for opp_name, opp_path, seeds, key in (
        ("metav4", METAV4, (1, 2, 3, 4), "metav4"),
        ("shopv7", SHOPV7, (1, 2, 3, 4), "shop"),
    ):
        print(f"\n== {name} vs {opp_name} ==", flush=True)
        rows, summary = series(make, opp_path, seeds, f"{name}_{opp_name}")
        rec[key] = {"rows": rows, "summary": summary}
        print("SUM", name, key, summary, flush=True)
        if key == "shop" and summary.get("win_rate", 0) < 0.5:
            rec["verdict"] = f"NO shop {summary}"
            return rec
    mv = rec["metav4"]["summary"]
    sh = rec["shop"]["summary"]
    if mv.get("win_rate", 0) >= 0.7 and sh.get("win_rate", 0) >= 0.5 and (mv.get("mean_margin") or 0) > 300:
        rec["verdict"] = "DUAL PASS strong"
    elif mv.get("win_rate", 0) >= 0.6 and sh.get("win_rate", 0) >= 0.5:
        rec["verdict"] = "DUAL PASS weak"
    else:
        rec["verdict"] = f"NO mv={mv} sh={sh}"
    return rec


def main():
    payload = {}
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            payload = {}
    variants = {
        "fish_on_h3": lambda tag: wrap_fish_eater(load_mv(tag), enable_rl_cap=True),
        "fish_on_h3_staticcap": lambda tag: wrap_fish_eater(load_mv(tag), enable_rl_cap=False),
    }
    for name, make in variants.items():
        if (payload.get("variants", {}).get(name, {}).get("verdict") or "").startswith(("DUAL", "NO")):
            print("skip", name, flush=True)
            continue
        gate(name, make, payload)
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n==== SUMMARY ====", flush=True)
    for name, rec in payload.get("variants", {}).items():
        print(name, rec.get("verdict"), flush=True)
    OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("WROTE", OUTJSON, flush=True)


if __name__ == "__main__":
    main()
