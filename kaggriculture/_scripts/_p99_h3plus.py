# -*- coding: utf-8 -*-
"""P99 H3+: stronger terminal greedy on Metav4 base. Dual-gate only. No submit."""
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
OUTJSON = PROJ / "_research/p99_h3plus.json"

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


def _shed(obs):
    return dict(((obs.get("private") or {}).get("shed") or {}))


def wrap_h3plus(parent, start_step=648, cap=80, only_cash=True):
    """H3+: day27+ (step>=648) surplus cash goods SELL min(stock, cap)."""

    def agent(obs, configuration=None):
        action = call(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            if step < start_step or not isinstance(action, dict):
                return action
            m = [list(o) for o in (action.get("market") or [])]
            already = {o[1] for o in m if len(o) >= 2 and o[0] == "SELL"}
            shed = _shed(obs)
            for item, stock in shed.items():
                if only_cash and item in INPUTS:
                    continue
                if not only_cash and item in INPUTS:
                    continue
                if item in already:
                    continue
                q = min(int(stock or 0), cap)
                if q > 0:
                    m.append(["SELL", item, q])
                    already.add(item)
            return dict(action, market=m) if m else action
        except Exception:
            return action

    return agent


def wrap_h3_advance(parent, start_step=576, end_step=671, lead=8, cap=40):
    """Advance surplus cash SELL earlier (day24-28)."""

    def agent(obs, configuration=None):
        action = call(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            if not (start_step <= step <= end_step) or not isinstance(action, dict):
                return action
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
                    b0, b1, st, sec = p79.run(c, o, seed)
                    cb, ob = b0, b1
                else:
                    b0, b1, st, sec = p79.run(o, c, seed)
                    ob, cb = b0, b1
                margin = cb - ob
                win = cb > ob
                wins += int(win)
                margins.append(margin)
                row = {"seed": seed, "seat0": seat0, "cand": cb, "opp": ob, "margin": margin, "win": win}
                print(f"{label} s={seed} seat0={seat0} {cb:.0f}:{ob:.0f} m={margin:.0f} win={win} {sec}s", flush=True)
            except Exception as e:
                row = {"seed": seed, "seat0": seat0, "error": str(e)[:180]}
                print(f"FAIL {label} s={seed}: {e}", flush=True)
            rows.append(row)
    n = len([r for r in rows if "win" in r])
    summary = {"n": n, "wins": wins, "win_rate": (wins / n) if n else 0, "mean_margin": (sum(margins)/len(margins)) if margins else None}
    return rows, summary


def gate_variant(name, make_cand, payload):
    rec = payload.setdefault("variants", {}).setdefault(name, {})
    for opp_name, opp_path, seeds, key in (
        ("metav4", METAV4, (1, 2, 3, 4), "metav4"),
        ("shopv7", SHOPV7, (1, 2, 3, 4), "shop"),
        ("thomas", THOMAS, (1, 2), "thomas"),
    ):
        print(f"\n== {name} vs {opp_name} ==", flush=True)
        rows, summary = series(make_cand, opp_path, seeds, f"{name}_{opp_name}")
        rec[key] = {"rows": rows, "summary": summary}
        print("SUM", name, opp_name, summary, flush=True)
        if key == "shop" and summary.get("win_rate", 0) < 0.5:
            print("SHOP FAIL — kill variant", name, flush=True)
            rec["verdict"] = f"NO shop {summary}"
            return rec
    mv = rec.get("metav4", {}).get("summary", {})
    sh = rec.get("shop", {}).get("summary", {})
    if mv.get("win_rate", 0) >= 0.7 and sh.get("win_rate", 0) >= 0.5:
        rec["verdict"] = "DUAL PASS candidate"
    else:
        rec["verdict"] = f"NO metav4={mv} shop={sh}"
    return rec


def main():
    payload = {}
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            payload = {}

    variants = {
        # H3 original-ish: step>=648 cap 60
        "h3_cap60": lambda tag: wrap_h3plus(load_mv(tag), start_step=648, cap=60),
        # stronger: earlier + larger
        "h3_cap120_624": lambda tag: wrap_h3plus(load_mv(tag), start_step=624, cap=120),
        # advance + greedy
        "h3_adv_combo": lambda tag: wrap_h3plus(wrap_h3_advance(load_mv(tag)), start_step=648, cap=80),
    }
    for name, make in variants.items():
        if (payload.get("variants", {}).get(name, {}).get("verdict", "") or "").startswith(("DUAL", "NO shop")):
            print("skip done", name, flush=True)
            continue
        gate_variant(name, make, payload)
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n==== SUMMARY ====", flush=True)
    for name, rec in payload.get("variants", {}).items():
        print(name, rec.get("verdict"), flush=True)
    OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("WROTE", OUTJSON, flush=True)


if __name__ == "__main__":
    main()
