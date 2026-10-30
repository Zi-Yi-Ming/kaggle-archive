# -*- coding: utf-8 -*-
"""P97b ORIGINAL: Metav4 backbone + terminal harvest / sale-advance hybrid.

Autopsy (p97_daygap): money swing is decided day26-29 (step 624-718),
not opening. Fieldcraft LEAD=8 / sale_horizon inspired, but implemented as
a thin market-order overlay on production Metav4. NEVER touch step0 or pasture.

Variants:
  H1 term_cap     — day26+ split large SELL (anti price-crush)
  H2 term_advance — day24-28 advance pure-cash SELL by 3 turns when stock in shed
  H3 term_greedy  — day27-29 extra SELL of surplus cash goods (no WHEAT/FERT input)
  H4 combo        — H1+H2+H3

NOT submit. Dual gate vs Metav4 AND shop_v7. User auth required later.
"""
from __future__ import annotations

import importlib.util
import io
import json
import time
from contextlib import redirect_stdout
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "p79", r"D:\桌面\\Kaggle\kaggriculture\_scripts\_p79_mass_gate_vs_thomas.py"
)
p79 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p79)

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
METAV4 = PROJ / "_push_metav4_v13" / "main.py"
SHOPV7 = PROJ / "_external/p70_extracted/kaggriculture_shop_router_reactive_v7__0.py"
THOMAS = PROJ / "_push_thomas_2945" / "main.py"
PIPE16 = PROJ / "_push_pipe16" / "main.py"
OUTJSON = PROJ / "_research/p97b_term_hybrid.json"

CASH_ITEMS = ("STRAWBERRY", "MELON", "MILK", "WOOL", "EGG", "TOMATO", "CARROT")
INPUT_ITEMS = ("WHEAT", "FERTILIZER")


def load_mv(tag: str):
    code = METAV4.read_text(encoding="utf-8", errors="ignore")
    ns = {"__name__": tag, "__file__": str(METAV4), "__builtins__": __builtins__}
    with redirect_stdout(io.StringIO()):
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


def _inv_total(obs):
    tot = 0
    for iv in (obs.get("private") or {}).get("inventories") or []:
        if isinstance(iv, dict):
            tot += sum(int(v or 0) for v in iv.values())
    return tot


def wrap_term_cap(parent):
    """H1: step>=624 cap single SELL of cash items to 80 (split anti-crush)."""

    def agent(obs, configuration=None):
        action = call(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            if step < 624 or not isinstance(action, dict):
                return action
            m = [list(o) for o in (action.get("market") or [])]
            changed = False
            for o in m:
                if len(o) >= 3 and o[0] == "SELL" and o[1] in CASH_ITEMS:
                    q = int(o[2] or 0)
                    if q >= 120:
                        o[2] = 80
                        changed = True
            return dict(action, market=m) if changed else action
        except Exception:
            return action

    return agent


def wrap_term_advance(parent):
    """H2: step 576-671, if pure-cash stock in shed and not already SELL this turn,
    push a LEAD=8-style early sell of min(stock, 40) for items with px>=2.
    Mirrors Fieldcraft LEAD idea without opening rewrite.
    """

    def agent(obs, configuration=None):
        action = call(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            if not (576 <= step <= 671) or not isinstance(action, dict):
                return action
            m = [list(o) for o in (action.get("market") or [])]
            already = {o[1] for o in m if len(o) >= 2 and o[0] == "SELL"}
            shed = _shed(obs)
            px = (obs.get("market") or {}).get("prices") or {}
            added = False
            for item in CASH_ITEMS:
                if item in already:
                    continue
                stock = int(shed.get(item, 0) or 0)
                if stock <= 0 or int(px.get(item, 0) or 0) < 2:
                    continue
                if len(m) >= 10:
                    break
                m.append(["SELL", item, min(stock, 40)])
                added = True
            return dict(action, market=m) if added else action
        except Exception:
            return action

    return agent


def wrap_term_greedy(parent):
    """H3: step>=648 night of day27+, dump surplus cash goods not already sold.
    Leave WHEAT/FERT alone. Cap 60/item/turn.
    """

    def agent(obs, configuration=None):
        action = call(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            if step < 648 or not isinstance(action, dict):
                return action
            m = [list(o) for o in (action.get("market") or [])]
            already = {o[1] for o in m if len(o) >= 2 and o[0] == "SELL"}
            shed = _shed(obs)
            px = (obs.get("market") or {}).get("prices") or {}
            added = False
            for item in CASH_ITEMS:
                if item in already:
                    continue
                stock = int(shed.get(item, 0) or 0)
                if stock <= 0 or int(px.get(item, 0) or 0) < 1:
                    continue
                if len(m) >= 10:
                    break
                m.append(["SELL", item, min(stock, 60)])
                added = True
            return dict(action, market=m) if added else action
        except Exception:
            return action

    return agent


def wrap_combo(parent):
    return wrap_term_greedy(wrap_term_advance(wrap_term_cap(parent)))


def series(fac, opp_path, opp_name, seeds, label):
    rows, margins, wins, n = [], [], 0, 0
    for seed in seeds:
        for seat0 in (True, False):
            tag = f"{label}_{opp_name}_{seed}_{int(seat0)}"
            try:
                c = fac(tag)
                o = load_mv and p79.load_quiet(opp_path, f"o_{tag}")
                if seat0:
                    b0, b1, st, sec = p79.run(c, o, seed)
                    cb, ob = b0, b1
                else:
                    b0, b1, st, sec = p79.run(o, c, seed)
                    cb, ob = b1, b0
                m = cb - ob
                win = cb > ob
                n += 1
                wins += int(win)
                margins.append(m)
                print(f"{label} vs {opp_name} s={seed} seat0={int(seat0)} c={cb:.0f} o={ob:.0f} m={m:.0f} win={win}", flush=True)
                rows.append({"seed": seed, "seat0": seat0, "cb": cb, "ob": ob, "margin": m, "win": win})
            except Exception as e:
                print(f"FAIL {label} {opp_name} s={seed}: {e}", flush=True)
                rows.append({"seed": seed, "seat0": seat0, "error": str(e)[:180]})
    sm = {
        "label": label, "opp": opp_name, "n": n, "wins": wins,
        "win_rate": round(wins / n, 3) if n else None,
        "mean_margin": round(sum(margins) / len(margins), 1) if margins else None,
    }
    print("SUM", sm, flush=True)
    return rows, sm


def main():
    print("=== P97b terminal hybrid ===", flush=True)

    def fac_wrap(w):
        def f(tag):
            return w(load_mv(tag))

        return f

    variants = [
        ("H0_metav4", lambda tag: load_mv(tag)),
        ("H1_term_cap", fac_wrap(wrap_term_cap)),
        ("H2_term_advance", fac_wrap(wrap_term_advance)),
        ("H3_term_greedy", fac_wrap(wrap_term_greedy)),
        ("H4_combo", fac_wrap(wrap_combo)),
    ]
    payload = {"variants": {}, "note": "P97b terminal hybrid; no submit", "updated": ""}
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    payload.setdefault("variants", {})

    for label, fac in variants:
        if (payload["variants"].get(label) or {}).get("vs_metav4", {}).get("n", 0) >= 4:
            print("skip", label, flush=True)
            continue
        print(f"\n===== {label} =====", flush=True)
        r_mv, s_mv = series(fac, METAV4, "metav4", (1, 2, 3), label)
        r_sp, s_sp = series(fac, SHOPV7, "shop_v7", (1, 2), label)
        r_th, s_th = series(fac, THOMAS, "thomas", (1,), label)
        payload["variants"][label] = {
            "vs_metav4": s_mv, "vs_shop_v7": s_sp, "vs_thomas": s_th,
            "rows": r_mv + r_sp + r_th,
        }
        wr_mv = s_mv.get("win_rate") or 0
        wr_sp = s_sp.get("win_rate") or 0
        dual = wr_mv >= 0.6 and wr_sp >= 0.5
        print(f"DUAL {label}: mv={wr_mv}({s_mv.get('mean_margin')}) shop={wr_sp}({s_sp.get('mean_margin')}) dual={dual}", flush=True)
        if dual:
            r2, s2 = series(fac, METAV4, "metav4_h", (4, 5, 6, 7), label)
            r3, s3 = series(fac, SHOPV7, "shop_h", (4, 5, 6), label)
            payload["variants"][label]["hold_mv"] = s2
            payload["variants"][label]["hold_sp"] = s3
            payload["variants"][label]["holdout_dual"] = (s2.get("win_rate") or 0) >= 0.6 and (s3.get("win_rate") or 0) >= 0.5
        payload["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n==== P97b TABLE ====", flush=True)
    for k, v in payload["variants"].items():
        print(k,
              "mv", (v.get("vs_metav4") or {}).get("win_rate"), (v.get("vs_metav4") or {}).get("mean_margin"),
              "shop", (v.get("vs_shop_v7") or {}).get("win_rate"), (v.get("vs_shop_v7") or {}).get("mean_margin"),
              "hold", v.get("holdout_dual"), flush=True)


if __name__ == "__main__":
    main()
