# -*- coding: utf-8 -*-
"""P107: steal only the 白饭 layer — COLLECT_FERT + SELL FERT on working H3/Metav4.

Minimal safe steal. Physical engine unchanged except inject fert harvest when idle-adjacent.
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
OUTJSON = PROJ / "_research" / "p107_fert_steal.json"

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


def wrap_fert_steal(parent, collect_every=24):
    """Add: try COLLECT_FERTILIZER on farmer/hands when step%collect_every==2..4;
    always SELL any FERTILIZER in shed (白饭 cash). Keep all other actions."""

    def agent(obs, configuration=None):
        action = call(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            if not isinstance(action, dict):
                action = {"farmer": ["PASS"], "hands": [], "market": []}
            shed = dict(((obs.get("private") or {}).get("shed") or {}))
            fert = int(shed.get("FERTILIZER") or 0)

            m = [list(o) for o in (action.get("market") or [])]
            if fert > 0 and not any(len(o) >= 2 and o[0] == "SELL" and o[1] == "FERTILIZER" for o in m):
                m.append(["SELL", "FERTILIZER", fert])
            action = dict(action, market=m)

            # inject collect on a few hours — only overwrite PASS slots to avoid breaking route
            hour = step % 24
            if hour in (3, 4) and step > 10:
                f = list(action.get("farmer") or ["PASS"])
                if f[:1] in (["PASS"], []):
                    f = ["COLLECT_FERTILIZER"]
                    action = dict(action, farmer=f)
                hands = [list(h) for h in (action.get("hands") or [])]
                changed = False
                for i, h in enumerate(hands):
                    if h[:1] in (["PASS"], []):
                        hands[i] = ["COLLECT_FERTILIZER"]
                        changed = True
                if changed:
                    action = dict(action, hands=hands)
            return action
        except Exception:
            return action

    return agent


def wrap_fert_sell_only(parent):
    """Even safer: only sell fert if present, never touch physical."""

    def agent(obs, configuration=None):
        action = call(parent, obs, configuration)
        try:
            shed = dict(((obs.get("private") or {}).get("shed") or {}))
            fert = int(shed.get("FERTILIZER") or 0)
            if fert <= 0 or not isinstance(action, dict):
                return action
            m = [list(o) for o in (action.get("market") or [])]
            if any(len(o) >= 2 and o[0] == "SELL" and o[1] == "FERTILIZER" for o in m):
                return action
            m.append(["SELL", "FERTILIZER", fert])
            return dict(action, market=m)
        except Exception:
            return action

    return agent


def wrap_h3_term(parent, start=648, cap=60):
    def agent(obs, configuration=None):
        action = call(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            if step < start or not isinstance(action, dict):
                return action
            m = [list(o) for o in (action.get("market") or [])]
            already = {o[1] for o in m if len(o) >= 2 and o[0] == "SELL"}
            shed = dict(((obs.get("private") or {}).get("shed") or {}))
            for item, stock in shed.items():
                if item in INPUTS or item in already:
                    continue
                q = min(int(stock or 0), cap)
                if q > 0:
                    m.append(["SELL", item, q])
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
                rows.append({"seed": seed, "seat0": seat0, "cand": cb, "opp": ob, "margin": margin, "win": win})
                print(f"{label} s={seed} seat0={seat0} {cb:.0f}:{ob:.0f} m={margin:.0f} win={win} {sec}s", flush=True)
            except Exception as e:
                rows.append({"seed": seed, "seat0": seat0, "error": str(e)[:180]})
                print(f"FAIL {label} s={seed}: {e}", flush=True)
    n = len([r for r in rows if "win" in r])
    summary = {"n": n, "wins": wins, "win_rate": (wins / n) if n else 0,
               "mean_margin": (sum(margins) / len(margins)) if margins else None}
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
    # compare to H3 baseline +369
    if (mv.get("mean_margin") or -1e9) > 300 and sh.get("win_rate", 0) >= 0.5:
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
        # H3 + fert sell only
        "h3_fertsell": lambda tag: wrap_fert_sell_only(wrap_h3_term(load_mv(tag))),
        # H3 + fert collect inject + sell
        "h3_fertfull": lambda tag: wrap_fert_steal(wrap_h3_term(load_mv(tag))),
        # pure metav4 + fert sell only (no term) as control
        "mv_fertsell": lambda tag: wrap_fert_sell_only(load_mv(tag)),
    }
    for name, make in variants.items():
        if (payload.get("variants", {}).get(name, {}).get("verdict") or "").startswith(("DUAL", "NO")):
            print("skip", name, flush=True)
            continue
        gate(name, make, payload)
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n==== SUMMARY (H3 baseline vs metav4 = +369) ====", flush=True)
    for n, rec in payload.get("variants", {}).items():
        print(n, rec.get("verdict"),
              "mv", rec.get("metav4", {}).get("summary"),
              "sh", rec.get("shop", {}).get("summary"), flush=True)
    OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("WROTE", OUTJSON, flush=True)


if __name__ == "__main__":
    main()
