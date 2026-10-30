# -*- coding: utf-8 -*-
"""P97c expand H3/H4: more seeds + hetero panel + selfplay."""
from __future__ import annotations

import importlib.util
import io
import json
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
ALPEREN = PROJ / "_push_alperen" / "main.py"
PIPE16 = PROJ / "_push_pipe16" / "main.py"
OUTJSON = PROJ / "_research/p97c_expand.json"
CASH = ("STRAWBERRY", "MELON", "MILK", "WOOL", "EGG", "TOMATO", "CARROT")


def load_mv(tag):
    code = METAV4.read_text(encoding="utf-8", errors="ignore")
    ns = {"__name__": tag, "__file__": str(METAV4), "__builtins__": __builtins__}
    with redirect_stdout(io.StringIO()):
        exec(compile(code, str(METAV4), "exec"), ns)
    fn = ns.get("agent")
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)

    def agent(obs, configuration=None):
        return fn(obs) if n <= 1 else fn(obs, configuration)

    return agent


def call(parent, obs, configuration=None):
    n = getattr(getattr(parent, "__code__", None), "co_argcount", 2)
    return parent(obs, configuration) if n > 1 else parent(obs)


def wrap_h3(parent):
    def agent(obs, configuration=None):
        action = call(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            if step < 648 or not isinstance(action, dict):
                return action
            m = [list(o) for o in (action.get("market") or [])]
            already = {o[1] for o in m if len(o) >= 2 and o[0] == "SELL"}
            shed = dict(((obs.get("private") or {}).get("shed") or {}))
            px = (obs.get("market") or {}).get("prices") or {}
            added = False
            for item in CASH:
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


def wrap_h4(parent):
    def agent(obs, configuration=None):
        action = call(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            if step < 624 or not isinstance(action, dict):
                return action
            m = [list(o) for o in (action.get("market") or [])]
            changed = False
            for o in m:
                if len(o) >= 3 and o[0] == "SELL" and o[1] in CASH and int(o[2] or 0) >= 120:
                    o[2] = 80
                    changed = True
            already = {o[1] for o in m if len(o) >= 2 and o[0] == "SELL"}
            shed = dict(((obs.get("private") or {}).get("shed") or {}))
            px = (obs.get("market") or {}).get("prices") or {}
            for item in CASH:
                if item in already:
                    continue
                stock = int(shed.get(item, 0) or 0)
                if stock <= 0:
                    continue
                if step >= 648:
                    if int(px.get(item, 0) or 0) < 1:
                        continue
                    qty = min(stock, 60)
                elif step >= 576 and int(px.get(item, 0) or 0) >= 2:
                    qty = min(stock, 40)
                else:
                    continue
                if len(m) >= 10:
                    break
                m.append(["SELL", item, qty])
                changed = True
            return dict(action, market=m) if changed else action
        except Exception:
            return action

    return agent


def series(factory, opp_path, opp_name, seeds, label):
    wins = n = 0
    margins = []
    rows = []
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
                print(f"{label} vs {opp_name} s={seed} seat0={int(seat0)} c={cb:.0f} o={ob:.0f} m={m:.0f} win={win}", flush=True)
                rows.append({"seed": seed, "seat0": seat0, "margin": m, "win": win})
            except Exception as e:
                print(f"FAIL {label} {opp_name} s={seed}: {e}", flush=True)
    sm = {"label": label, "opp": opp_name, "n": n, "wins": wins,
          "win_rate": round(wins / n, 3) if n else None,
          "mean_margin": round(sum(margins) / len(margins), 1) if margins else None}
    print("SUM", sm, flush=True)
    return sm, rows


def main():
    payload = {"results": {}, "updated": "", "note": "P97c expand"}
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    payload.setdefault("results", {})

    for label, wrap in (("H3", wrap_h3), ("H4", wrap_h4)):

        def factory(tag, w=wrap):
            return w(load_mv(tag))

        print(f"\n===== {label} WIDE =====", flush=True)
        s_mv, r_mv = series(factory, METAV4, "metav4", (8, 9, 10, 11), label)
        s_sp, r_sp = series(factory, SHOPV7, "shop_v7", (8, 9, 10), label)
        s_th, _ = series(factory, THOMAS, "thomas", (3, 4), label)
        s_al, _ = series(factory, ALPEREN, "alperen", (2, 3), label)
        s_p16, _ = series(factory, PIPE16, "pipe16", (2, 3), label)
        try:
            a1 = factory(label + "_sp1")
            a2 = factory(label + "_sp2")
            b0, b1, st, sec = p79.run(a1, a2, 30)
            sp = {"s0": b0, "s1": b1, "margin": b0 - b1}
            print("SELFPLAY", label, sp, flush=True)
        except Exception as e:
            sp = {"error": str(e)}
            print("SELFPLAY FAIL", e, flush=True)
        dual = (s_mv.get("win_rate") or 0) >= 0.6 and (s_sp.get("win_rate") or 0) >= 0.5
        collapses = [k for k, v in (("metav4", s_mv), ("shop", s_sp), ("thomas", s_th), ("alperen", s_al), ("pipe16", s_p16)) if (v.get("n") or 0) >= 4 and (v.get("wins") or 0) == 0]
        payload["results"][label] = {
            "mv": s_mv, "shop": s_sp, "thomas": s_th, "alperen": s_al, "pipe16": s_p16,
            "selfplay": sp, "dual": dual, "collapses": collapses,
            "rows_mv": r_mv, "rows_shop": r_sp,
        }
        payload["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"DUAL_WIDE {label}={dual} collapses={collapses}", flush=True)

    print("\n==== P97c TABLE ====", flush=True)
    for k, v in payload["results"].items():
        print(k, "mv", v.get("mv"), "shop", v.get("shop"), "dual", v.get("dual"), "col", v.get("collapses"), flush=True)


if __name__ == "__main__":
    main()
