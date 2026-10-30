# -*- coding: utf-8 -*-
"""P91: F7 wider holdout + terminal price-walk stagger invention.

NOT submit. Dual gate required for any candidate.
"""
from __future__ import annotations

import importlib.util
import io
import json
import sys
import time
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
OUTJSON = PROJ / "_research/p91_f7_terminal.json"
BASE_SRC = METAV4.read_text(encoding="utf-8", errors="ignore")


def load_src(src: str, tag: str):
    ns = {"__name__": tag, "__file__": str(METAV4), "__builtins__": __builtins__}
    with redirect_stdout(io.StringIO()):
        exec(compile(src, tag, "exec"), ns)
    fn = ns.get("agent")
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)

    def agent(obs, configuration=None):
        return fn(obs) if n <= 1 else fn(obs, configuration)

    return agent, ns


def call_parent(fn, obs, configuration=None):
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)
    return fn(obs, configuration) if n > 1 else fn(obs)


# Engine price params from Metav4 source (R37)
_PARAMS = {
    "WHEAT": {"base": 25, "I0": 10000, "T": 400, "below_func": "sqrt", "below_target": 0.8,
              "above_func": "log", "above_target": 0.2},
    "CARROT": {"base": 35, "I0": 10000, "T": 450, "below_func": "hinge", "below_target": 1.0,
               "above_func": "sqrt", "above_target": 0.7},
    "TOMATO": {"base": 60, "I0": 10000, "T": 200, "below_func": "hinge", "below_target": 0.4,
               "above_func": "sqrt", "above_target": 0.6},
    "STRAWBERRY": {"base": 120, "I0": 10000, "T": 100, "below_func": "sqrt", "below_target": 0.7,
                   "above_func": "linear", "above_target": 1.6},
    "MELON": {"base": 250, "I0": 10000, "T": 300, "below_func": "log", "below_target": 0.2,
              "above_func": "sq", "above_target": 3.6},
    "EGG": {"base": 50, "I0": 10000, "T": 332, "below_func": "hinge", "below_target": 0.4,
            "above_func": "log", "above_target": 0.2},
    "MILK": {"base": 160, "I0": 10000, "T": 122, "below_func": "sqrt", "below_target": 0.6,
             "above_func": "linear", "above_target": 1.6},
    "WOOL": {"base": 200, "I0": 10000, "T": 105, "below_func": "log", "below_target": 0.2,
             "above_func": "sq", "above_target": 3.2},
    "FERTILIZER": {"base": 100, "I0": 10000, "T": 200, "below_func": "linear", "below_target": 0.4,
                   "above_func": "linear", "above_target": 0.4},
}


def _shape(func, x, T=None):
    import math
    x = max(0.0, x)
    if func == "linear":
        return x
    if func == "sq":
        return x * x
    if func == "sqrt":
        return math.sqrt(x)
    if func == "log":
        return math.log1p(x)
    if func == "hinge":
        return max(0.0, x - (T or 0)) if T is not None else x
    return x


def _price(item, inv):
    p = _PARAMS.get(item)
    if not p:
        return 1
    inv = int(inv)
    T = p["T"]
    base = p["base"]
    if inv <= p["I0"]:
        # simplified: below I0 use below shape relative to T
        factor = 1.0 + p["below_target"] * _shape(p["below_func"], max(0, T - inv) / max(T, 1), T)
        return max(1, int(base * factor))
    factor = 1.0 + p["above_target"] * _shape(p["above_func"], (inv - p["I0"]) / max(T, 1), T)
    return max(1, int(base / max(factor, 0.05)))


def wrap_terminal_stagger(parent):
    """P91 original: day29 / step>=696, rewrite SELL qty to maximize sum of
    marginal prices using public inventory walk. Cap per-turn so we don't dump.
    Leave WHEAT/FERTILIZER alone (input obligations).
    """

    def agent(obs, configuration=None):
        action = call_parent(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            if step < 696 or step > 718 or not isinstance(action, dict):
                return action
            inv0 = (obs.get("market") or {}).get("inventory") or {}
            m = [list(o) for o in (action.get("market") or [])]
            new_m = []
            for o in m:
                if len(o) >= 3 and o[0] == "SELL" and o[1] not in ("WHEAT", "FERTILIZER"):
                    item = o[1]
                    q = int(o[2] or 0)
                    if q <= 0:
                        new_m.append(o)
                        continue
                    inv = int(inv0.get(item, 10000) or 10000)
                    # greedy: take units while marginal price >= 55% of first unit price
                    p0 = _price(item, inv)
                    take = 0
                    acc = 0
                    for j in range(q):
                        pj = _price(item, inv + j)
                        if pj < max(1, int(p0 * 0.55)) and take >= 5:
                            break
                        take += 1
                        acc += pj
                    take = max(5, min(q, take, 60))  # never zero; cap 60/turn
                    new_m.append([o[0], item, take])
                else:
                    new_m.append(o)
            return dict(action, market=new_m)
        except Exception:
            return action

    return agent


def wrap_f7(src_base):
    return src_base.replace("V9_FERT_FIRST_DAY = 14", "V9_FERT_FIRST_DAY = 10", 1)


def series(factory, opp_path, opp_name, seeds, label):
    rows, margins, wins, n = [], [], 0, 0
    for seed in seeds:
        for seat0 in (True, False):
            tag = f"{label}_{opp_name}_{seed}_{int(seat0)}"
            try:
                c = factory(tag)
                o = p79.load_quiet(opp_path, f"o_{tag}")
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
                print(f"{label} vs {opp_name} s={seed} seat0={seat0} c={cb:.0f} o={ob:.0f} m={m:.0f} win={win}", flush=True)
                rows.append({"seed": seed, "seat0": seat0, "cb": cb, "ob": ob, "margin": m, "win": win})
            except Exception as e:
                print(f"FAIL {label} {opp_name} s={seed} seat0={seat0}: {e}", flush=True)
                rows.append({"seed": seed, "seat0": seat0, "error": str(e)[:200]})
    sm = {
        "label": label, "opp": opp_name, "n": n, "wins": wins,
        "win_rate": round(wins / n, 3) if n else None,
        "mean_margin": round(sum(margins) / len(margins), 1) if margins else None,
    }
    print("SUM", sm, flush=True)
    return rows, sm


def main():
    f7_src = wrap_f7(BASE_SRC)

    def fac_f7(tag):
        a, _ = load_src(f7_src, tag)
        return a

    def fac_base(tag):
        a, _ = load_src(BASE_SRC, tag)
        return a

    def fac_term(tag):
        a, _ = load_src(BASE_SRC, f"term_{tag}")
        return wrap_terminal_stagger(a)

    def fac_f7_term(tag):
        a, _ = load_src(f7_src, f"f7t_{tag}")
        return wrap_terminal_stagger(a)

    payload = {"variants": {}, "note": "P91 F7 wide + terminal stagger; no submit",
               "updated": time.strftime("%Y-%m-%dT%H:%M:%S")}
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    payload.setdefault("variants", {})

    jobs = [
        ("W1_f7_wide", fac_f7, (7, 8, 9, 10, 11, 12), (7, 8, 9)),
        ("W2_term_stagger", fac_term, (1, 2, 3), (1, 2)),
        ("W3_f7_term", fac_f7_term, (1, 2, 3), (1, 2)),
        ("W0_base_ctrl", fac_base, (7, 8), (7,)),
    ]

    for label, fac, mv_seeds, sp_seeds in jobs:
        if (payload["variants"].get(label) or {}).get("vs_metav4", {}).get("n", 0) >= 6:
            print("SKIP", label, flush=True)
            continue
        print(f"\n===== {label} =====", flush=True)
        r_mv, s_mv = series(fac, METAV4, "metav4", mv_seeds, label)
        r_sp, s_sp = series(fac, SHOPV7, "shop_v7", sp_seeds, label)
        r_th, s_th = series(fac, THOMAS, "thomas", (1,), label)
        payload["variants"][label] = {
            "vs_metav4": s_mv, "vs_shop_v7": s_sp, "vs_thomas": s_th,
            "rows": r_mv + r_sp + r_th,
        }
        payload["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        wr_mv = s_mv.get("win_rate") or 0
        wr_sp = s_sp.get("win_rate") or 0
        dual = wr_mv >= 0.6 and wr_sp >= 0.5
        print(f"DUAL {label}: mv={wr_mv}({s_mv.get('mean_margin')}) shop={wr_sp}({s_sp.get('mean_margin')}) th={s_th.get('win_rate')} dual={dual}", flush=True)

    print("\n==== P91 TABLE ====", flush=True)
    for k, v in payload["variants"].items():
        print(k,
              "mv", (v.get("vs_metav4") or {}).get("win_rate"), (v.get("vs_metav4") or {}).get("mean_margin"),
              "shop", (v.get("vs_shop_v7") or {}).get("win_rate"), (v.get("vs_shop_v7") or {}).get("mean_margin"),
              "th", (v.get("vs_thomas") or {}).get("win_rate"), flush=True)


if __name__ == "__main__":
    main()
