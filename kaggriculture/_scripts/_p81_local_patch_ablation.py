# -*- coding: utf-8 -*-
"""P81 local single-variable tests vs production thomas. NO SUBMIT.

Variants:
1. thomas_late_sell_cap — wrap thomas: compress large SELL qty on step>=700
2. thomas_no_race — reuse _research/p76_ablation_agents/thomas_no_race.py
3. thomas_no_courier — p76 ablation
Opponents: production thomas; optional shop_router_v7 as non-mirror stand-in
"""
from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "p79", r"D:\桌面\Kaggle\kaggriculture\_scripts\_p79_mass_gate_vs_thomas.py"
)
p79 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p79)

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
THOMAS = PROJ / "_push_thomas_2945" / "main.py"
NORACE = PROJ / "_research/p76_ablation_agents/thomas_no_race.py"
NOCOUR = PROJ / "_research/p76_ablation_agents/thomas_no_courier.py"
NOHERD = PROJ / "_research/p76_ablation_agents/thomas_no_herd.py"
SHOPV7 = PROJ / "_external/p70_extracted/kaggriculture_shop_router_reactive_v7__0.py"
OUT = PROJ / "_research/p81_local_patch_ablation.json"
SEEDS = (1, 2, 3, 4)


def wrap_late_sell_cap(fn, cap_each=2000, start_step=700):
    """Reduce per-order SELL qty late in the game to reduce own price smash."""

    def agent(obs, configuration=None):
        action = fn(obs, configuration) if _argc(fn) > 1 else fn(obs)
        try:
            step = int(obs.get("step", 0) if isinstance(obs, dict) else 0)
            if step < start_step:
                return action
            market = action.get("market") if isinstance(action, dict) else None
            if not market:
                return action
            new_m = []
            for o in market:
                if o and o[0] == "SELL" and len(o) >= 3 and int(o[2] or 0) > cap_each:
                    new_m.append([o[0], o[1], cap_each])
                else:
                    new_m.append(o)
            return dict(action, market=new_m)
        except Exception:
            return action

    return agent


def _argc(fn):
    return getattr(getattr(fn, "__code__", None), "co_argcount", 2)


def load_agent(path: Path, tag: str):
    fn = p79.load_quiet(path, tag)
    return fn


def run(a0, a1, seed: int):
    return p79.run(a0, a1, seed)


def series(cand_fn_factory, opp_path: Path, opp_name: str, cand_name: str, seeds=SEEDS):
    rows = []
    for seed in seeds:
        for seat0 in (True, False):
            tag = f"{cand_name}_vs_{opp_name}_{seed}_{int(seat0)}"
            try:
                c = cand_fn_factory(tag)
                o = load_agent(opp_path, f"o_{tag}")
                if seat0:
                    b0, b1, st, sec = run(c, o, seed)
                    cb, ob = b0, b1
                else:
                    b0, b1, st, sec = run(o, c, seed)
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
                    "tie": cb == ob,
                    "status": st,
                    "sec": sec,
                }
                print(
                    f"{cand_name} vs {opp_name} s={seed} seat0={seat0} "
                    f"c={cb:.0f} o={ob:.0f} m={row['margin']:.0f} win={row['win']} {sec}s",
                    flush=True,
                )
            except Exception as e:
                row = {"cand": cand_name, "opp": opp_name, "seed": seed, "seat0": seat0, "error": str(e)[:200]}
                print(f"FAIL {cand_name} vs {opp_name} s={seed}: {e}", flush=True)
            rows.append(row)
    ok = [r for r in rows if "error" not in r]
    wins = sum(1 for r in ok if r.get("win"))
    ties = sum(1 for r in ok if r.get("tie"))
    margins = [r["margin"] for r in ok]
    summary = {
        "cand": cand_name,
        "opp": opp_name,
        "n": len(ok),
        "wins": wins,
        "ties": ties,
        "losses": len(ok) - wins - ties,
        "win_rate": round(wins / len(ok), 3) if ok else None,
        "mean_margin": round(sum(margins) / len(margins), 1) if margins else None,
        "errors": len(rows) - len(ok),
    }
    print("SUMMARY", summary, flush=True)
    return rows, summary


def factory_from_file(path: Path, wrap=None):
    def f(tag):
        fn = load_agent(path, tag)
        return wrap(fn) if wrap else fn

    return f


def factory_late_cap():
    def f(tag):
        fn = load_agent(THOMAS, tag)
        return wrap_late_sell_cap(fn)

    return f


def main():
    payload = {"note": "P81 local research only; no submit", "results": []}
    jobs = [
        (
            "thomas_late_sell_cap2000_s700",
            factory_late_cap(),
            THOMAS,
            "thomas_prod",
        ),
        (
            "thomas_no_race",
            factory_from_file(NORACE),
            THOMAS,
            "thomas_prod",
        ),
        (
            "thomas_no_courier",
            factory_from_file(NOCOUR),
            THOMAS,
            "thomas_prod",
        ),
        (
            "thomas_no_herd",
            factory_from_file(NOHERD),
            THOMAS,
            "thomas_prod",
        ),
        (
            "thomas_prod",
            factory_from_file(THOMAS),
            SHOPV7,
            "shop_router_v7",
        ),
        (
            "thomas_no_race",
            factory_from_file(NORACE),
            SHOPV7,
            "shop_router_v7",
        ),
        (
            "thomas_late_sell_cap2000_s700",
            factory_late_cap(),
            SHOPV7,
            "shop_router_v7",
        ),
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    for cand_name, fac, opp_path, opp_name in jobs:
        if not opp_path.exists():
            print("missing opp", opp_path)
            continue
        if cand_name.startswith("thomas_no") and "p76" in str(fac):
            pass
        print(f"===== {cand_name} vs {opp_name} =====", flush=True)
        rows, summary = series(fac, opp_path, opp_name, cand_name)
        payload["results"].append({"summary": summary, "rows": rows})
        OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n==== P81 TABLE ====", flush=True)
    for r in payload["results"]:
        s = r["summary"]
        print(
            f"{s['cand']:32s} vs {s['opp']:16s} "
            f"W{s['wins']}/{s['n']} tie{s['ties']} WR={s['win_rate']} m={s['mean_margin']} err={s['errors']}",
            flush=True,
        )


if __name__ == "__main__":
    main()
