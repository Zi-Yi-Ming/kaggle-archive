# -*- coding: utf-8 -*-
"""P82 brute-force wrappers on production thomas. Local only, NO SUBMIT.

Grid:
- late sell cap / total sell per turn / sell delay (buffer until next day)
- start_step x cap
Opponents: thomas_prod, shop_router_v7, alperen
Smoke seeds 1-2; escalate if wins>=2 vs thomas_prod.
"""
from __future__ import annotations

import importlib.util
import json
import time
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "p79", r"D:\桌面\Kaggle\kaggriculture\_scripts\_p79_mass_gate_vs_thomas.py"
)
p79 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p79)

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
THOMAS = PROJ / "_push_thomas_2945" / "main.py"
ALPEREN = PROJ / "_push_alperen" / "main.py"
SHOPV7 = PROJ / "_external/p70_extracted/kaggriculture_shop_router_reactive_v7__0.py"
OUT = PROJ / "_research" / "p82_bruteforce_wrappers.json"


def _argc(fn):
    return getattr(getattr(fn, "__code__", None), "co_argcount", 2)


def load_thomas(tag: str):
    return p79.load_quiet(THOMAS, tag)


def make_cap_wrapper(fn, start_step=700, cap_each=2000, cap_total=None):
    def agent(obs, configuration=None):
        action = fn(obs, configuration) if _argc(fn) > 1 else fn(obs)
        try:
            step = int((obs or {}).get("step", 0))
            if step < start_step:
                return action
            market = action.get("market") if isinstance(action, dict) else None
            if not market:
                return action
            new_m = []
            total = 0
            for o in market:
                if o and o[0] == "SELL" and len(o) >= 3:
                    q = int(o[2] or 0)
                    q = min(q, cap_each) if cap_each else q
                    if cap_total is not None and total + q > cap_total:
                        q = max(0, cap_total - total)
                    total += q
                    new_m.append([o[0], o[1], q] if q else [])
                else:
                    new_m.append(o)
            return dict(action, market=new_m)
        except Exception:
            return action

    return agent


def make_delay_wrapper(fn, start_step=650, delay_turns=24, hold_max_orders=6):
    """Park large sells in a buffer; flush next day / when buffer full."""
    state = {"buf": []}

    def agent(obs, configuration=None):
        action = fn(obs, configuration) if _argc(fn) > 1 else fn(obs)
        try:
            step = int((obs or {}).get("step", 0))
            if step < start_step:
                state["buf"].clear()
                return action
            market = list(action.get("market") or []) if isinstance(action, dict) else []
            # flush buffer first
            out = list(state["buf"][: max(0, 10 - len(market))])
            state["buf"] = state["buf"][len(out) :]
            kept = []
            for o in market:
                if o and o[0] == "SELL" and len(o) >= 3 and int(o[2] or 0) >= 3000 and len(state["buf"]) < hold_max_orders:
                    state["buf"].append(list(o))
                else:
                    kept.append(o)
            new_m = out + kept
            if new_m != market and isinstance(action, dict):
                return dict(action, market=new_m)
            return action
        except Exception:
            return action

    return agent


def make_split_wrapper(fn, start_step=650, chunk=2500):
    """Split large SELL into multiple smaller orders (respect 10-order cap)."""

    def agent(obs, configuration=None):
        action = fn(obs, configuration) if _argc(fn) > 1 else fn(obs)
        try:
            step = int((obs or {}).get("step", 0))
            if step < start_step:
                return action
            market = action.get("market") if isinstance(action, dict) else None
            if not market:
                return action
            out = []
            for o in market:
                if o and o[0] == "SELL" and len(o) >= 3 and int(o[2] or 0) > chunk:
                    q = int(o[2] or 0)
                    item = o[1]
                    while q > 0 and len(out) < 10:
                        take = min(chunk, q)
                        out.append(["SELL", item, take])
                        q -= take
                    if q > 0 and out:
                        out[-1] = ["SELL", item, int(out[-1][2]) + q]
                else:
                    out.append(o)
                    if len(out) >= 10:
                        break
            out = out[:10]
            return dict(action, market=out)
        except Exception:
            return action

    return agent


def make_race_off_hint(fn):
    """Best-effort: flip telemetry/global flags if present after load."""
    for name in (
        "_RACE_ON",
        "_V9_RACE",
        "RACE_ON",
        "_RACEPX",
        "RACEPX",
        "_ENABLE_RACE",
    ):
        if hasattr(fn, "__globals__") and name in fn.__globals__:
            try:
                fn.__globals__[name] = False
            except Exception:
                pass
    # also walk closure/module
    g = getattr(fn, "__globals__", None)
    if g:
        for k, v in list(g.items()):
            if isinstance(v, bool) and ("RACE" in k.upper() or "RACEPX" in k.upper()):
                try:
                    g[k] = False
                except Exception:
                    pass
    return fn


def series(fac, opp_path, opp_name, cand_name, seeds=(1, 2)):
    rows = []
    for seed in seeds:
        for seat0 in (True, False):
            tag = f"{cand_name}_{opp_name}_{seed}_{int(seat0)}"
            try:
                c = fac(tag)
                o = p79.load_quiet(opp_path, f"o_{tag}")
                if seat0:
                    b0, b1, st, sec = p79.run(c, o, seed)
                    cb, ob = b0, b1
                else:
                    b0, b1, st, sec = p79.run(o, c, seed)
                    cb, ob = b1, b0
                row = {
                    "cand": cand_name,
                    "opp": opp_name,
                    "seed": seed,
                    "seat0": seat0,
                    "cand_bank": cb,
                    "opp_bank": ob,
                    "margin": cb - ob,
                    "win": cb > ob,
                    "status": st,
                    "sec": sec,
                }
                print(
                    f"{cand_name} vs {opp_name} s={seed} seat0={seat0} "
                    f"c={cb:.0f} o={ob:.0f} m={row['margin']:.0f} win={row['win']}",
                    flush=True,
                )
            except Exception as e:
                row = {"cand": cand_name, "opp": opp_name, "seed": seed, "seat0": seat0, "error": str(e)[:180]}
                print(f"FAIL {cand_name} {opp_name} s={seed}: {e}", flush=True)
            rows.append(row)
    ok = [r for r in rows if "error" not in r]
    wins = sum(1 for r in ok if r.get("win"))
    ties = sum(1 for r in ok if not r.get("win") and abs(r.get("margin") or 1) < 1e-9)
    summary = {
        "cand": cand_name,
        "opp": opp_name,
        "n": len(ok),
        "wins": wins,
        "ties": sum(1 for r in ok if abs(r.get("margin") or 1) < 1e-9),
        "win_rate": round(wins / len(ok), 3) if ok else None,
        "mean_margin": round(sum(r["margin"] for r in ok) / len(ok), 1) if ok else None,
        "errors": len(rows) - len(ok),
    }
    print("SUM", summary, flush=True)
    return rows, summary


def fac_cap(start, cap_each, cap_total=None):
    def f(tag):
        fn = load_thomas(tag)
        return make_cap_wrapper(fn, start, cap_each, cap_total)

    return f


def fac_delay(start, delay_turns=24):
    def f(tag):
        fn = load_thomas(tag)
        return make_delay_wrapper(fn, start, delay_turns)

    return f


def fac_split(start, chunk):
    def f(tag):
        fn = load_thomas(tag)
        return make_split_wrapper(fn, start, chunk)

    return f


def fac_raceoff(tag):
    fn = load_thomas(tag)
    return make_race_off_hint(fn)


def main():
    payload = {"note": "P82 brute force local; no submit", "results": []}
    jobs = []
    # cap grid vs thomas
    for start in (500, 600, 650, 700):
        for cap in (500, 1000, 1500, 3000):
            jobs.append((f"cap_s{start}_q{cap}", fac_cap(start, cap), THOMAS, "thomas_prod"))
    # total cap
    jobs.append(("cap_s600_q1500_total4000", fac_cap(600, 1500, 4000), THOMAS, "thomas_prod"))
    jobs.append(("cap_s650_q1000_total3000", fac_cap(650, 1000, 3000), THOMAS, "thomas_prod"))
    # delay
    jobs.append(("delay_s600", fac_delay(600), THOMAS, "thomas_prod"))
    jobs.append(("delay_s650", fac_delay(650), THOMAS, "thomas_prod"))
    jobs.append(("delay_s700", fac_delay(700), THOMAS, "thomas_prod"))
    # split
    jobs.append(("split_s650_c2000", fac_split(650, 2000), THOMAS, "thomas_prod"))
    jobs.append(("split_s600_c1500", fac_split(600, 1500), THOMAS, "thomas_prod"))
    # race off
    jobs.append(("race_off_hint", fac_raceoff, THOMAS, "thomas_prod"))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    best = []
    for cand_name, fac, opp_path, opp_name in jobs:
        print(f"===== {cand_name} vs {opp_name} =====", flush=True)
        rows, summary = series(fac, opp_path, opp_name, cand_name)
        payload["results"].append({"summary": summary, "rows": rows})
        OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        if summary.get("win_rate") is not None and summary["win_rate"] >= 0.5 and summary.get("wins", 0) >= 2:
            best.append(summary)
            print("PROMISING", summary, flush=True)
            # broader panel smoke
            for opp_p, opp_n in ((SHOPV7, "shop_router_v7"), (ALPEREN, "alperen")):
                if not opp_p.exists():
                    continue
                print(f"--- panel {cand_name} vs {opp_n} ---", flush=True)
                r2, s2 = series(fac, opp_p, opp_n, cand_name)
                payload["results"].append({"summary": s2, "rows": r2})
                OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n==== P82 BEST vs thomas ====", flush=True)
    for r in payload["results"]:
        s = r["summary"]
        if s.get("opp") == "thomas_prod":
            print(
                f"{s['cand']:32s} W{s['wins']}/{s['n']} WR={s['win_rate']} m={s['mean_margin']}",
                flush=True,
            )


if __name__ == "__main__":
    main()
