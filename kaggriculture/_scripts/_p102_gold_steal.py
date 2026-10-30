# -*- coding: utf-8 -*-
"""P102 Gold Steal: no day0 roundtrip, spread sells, keep safe terminal. Dual-gate."""
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
OUTJSON = PROJ / "_research/p102_gold_steal.json"

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


def wrap_no_day0_sell(parent):
    """Block SELL in first day (step < 24) — gold starts selling at step~24."""

    def agent(obs, configuration=None):
        action = call(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            if step >= 24 or not isinstance(action, dict):
                return action
            m = []
            changed = False
            for o in action.get("market") or []:
                if isinstance(o, (list, tuple)) and o and o[0] == "SELL":
                    changed = True
                    continue
                m.append(list(o) if isinstance(o, (list, tuple)) else o)
            return dict(action, market=m) if changed else action
        except Exception:
            return action

    return agent


def wrap_spread_sell(parent, start=288, end=648, batch=25):
    """Mid-game drip sell to match gold's even distribution (not just terminal dump)."""

    def agent(obs, configuration=None):
        action = call(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            if not (start <= step <= end) or not isinstance(action, dict):
                return action
            # only add sells every 12 steps to avoid spam
            if step % 12 != 0:
                return action
            m = [list(o) for o in (action.get("market") or [])]
            already = {o[1] for o in m if len(o) >= 2 and o[0] == "SELL"}
            for item, stock in _shed(obs).items():
                if item in INPUTS or item in already:
                    continue
                q = min(int(stock or 0), batch)
                if q > 0:
                    m.append(["SELL", item, q])
                    already.add(item)
            return dict(action, market=m) if m else action
        except Exception:
            return action

    return agent


def wrap_term_gentle(parent, start=648, cap=40):
    """Gentle terminal (smaller than H3's 60) to avoid crush."""

    def agent(obs, configuration=None):
        action = call(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            if step < start or not isinstance(action, dict):
                return action
            m = [list(o) for o in (action.get("market") or [])]
            already = {o[1] for o in m if len(o) >= 2 and o[0] == "SELL"}
            for item, stock in _shed(obs).items():
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
        # A: just kill day0 sell (minimal change from Metav4/H3)
        "no_day0": lambda tag: wrap_no_day0_sell(load_mv(tag)),
        # B: no day0 + gentle term (H3-like but milder)
        "no_day0_term40": lambda tag: wrap_term_gentle(wrap_no_day0_sell(load_mv(tag)), cap=40),
        # C: full gold steal: no day0 + mid drip + gentle term
        "gold_steal": lambda tag: wrap_term_gentle(
            wrap_spread_sell(wrap_no_day0_sell(load_mv(tag))), cap=40
        ),
    }
    for name, make in variants.items():
        if (payload.get("variants", {}).get(name, {}).get("verdict") or "").startswith(("DUAL", "NO")):
            print("skip", name, flush=True)
            continue
        gate(name, make, payload)
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n==== SUMMARY ====", flush=True)
    for name, rec in payload.get("variants", {}).items():
        print(name, rec.get("verdict"), rec.get("metav4", {}).get("summary"), rec.get("shop", {}).get("summary"), flush=True)
    OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("WROTE", OUTJSON, flush=True)


if __name__ == "__main__":
    main()
