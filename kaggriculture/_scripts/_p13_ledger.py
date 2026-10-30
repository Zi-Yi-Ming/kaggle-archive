# -*- coding: utf-8 -*-
"""P13: reconstruct per-step cash ledger from engine observations + actions."""
from __future__ import annotations

import csv
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

ANIMAL_COST = {"GOOSE": 300, "COW": 400, "SHEEP": 500}
SEED_COST = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}
LAND_PRICES = [1000, 2000, 4000]


def fib(n):
    a, b = 1, 1
    for _ in range(max(0, n)):
        a, b = b, a + b
    return a


def classify_orders(action, prices, money_before, n_land_before, hires_today_before):
    """Estimate expected cash delta from market orders. Engine may clamp."""
    events = []
    cash = 0.0
    for o in action.get("market") or []:
        if not o:
            continue
        op = o[0]
        if op == "SELL" and len(o) >= 3:
            item, q = o[1], int(o[2] or 0)
            px = int(prices.get(item) or 0)
            events.append(("SALE", item, q, px, q * px))
            cash += q * px
        elif op == "HIRE":
            # cost unknown without hires_today; use fib estimate later
            events.append(("HIRE", "", 1, None, None))
        elif op == "BUY_LAND":
            n = n_land_before - 1
            cost = LAND_PRICES[n] if 0 <= n < len(LAND_PRICES) else 0
            events.append(("BUY_LAND", "", 1, cost, -cost))
            cash -= cost
        elif op == "BUY_ANIMAL" and len(o) >= 3:
            item, q = o[1], int(o[2] or 0)
            cost = ANIMAL_COST.get(item, 0) * q
            events.append(("ANIMAL_BUY", item, q, ANIMAL_COST.get(item), -cost))
            cash -= cost
        elif op == "BUY_SEED" and len(o) >= 3:
            item, q = o[1], int(o[2] or 0)
            cost = SEED_COST.get(item, 0) * q
            events.append(("SEED_BUY", item, q, SEED_COST.get(item), -cost))
            cash -= cost
        elif op == "BUY_PRODUCT" and len(o) >= 3:
            item, q = o[1], int(o[2] or 0)
            px = int(prices.get(item) or 0)
            events.append(("PRODUCT_BUY", item, q, px, -px * q))
            cash -= px * q
    return events, cash


def load_r2():
    spec = importlib.util.spec_from_file_location(
        "r2_p13_" + str(id(object())), str(ROOT / "_push_medal" / "main.py")
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def load_b():
    from p11_planner import planner as pmod
    pmod._PLANNER = None
    return pmod.agent


def run_ledger(own_factory, opp_factory, seed, own_seat, label):
    own = own_factory()
    opp = opp_factory()
    agents = [None, None]
    agents[own_seat] = own
    agents[1 - own_seat] = opp

    # capture actions per step for own seat
    own_actions = {}

    def wrap(inner, is_own):
        def agent(obs, configuration=None):
            step = int(obs.get("step") or 0)
            action = inner(obs, configuration)
            if is_own:
                own_actions[step] = {
                    "action": action,
                    "prices": dict((obs.get("market") or {}).get("prices") or {}),
                    "player": int(obs.get("player") or 0),
                }
            return action
        return agent

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([wrap(agents[0], own_seat == 0), wrap(agents[1], own_seat == 1)])

    # reconstruct money path from env.steps
    money_path = []  # (step, money, n_land, hires_today, shed, seeds)
    for idx, s in enumerate(env.steps):
        rec = s[own_seat]
        if not rec:
            continue
        obs = rec.get("observation") or {}
        step = int(obs.get("step") or idx)
        farm = (obs.get("farms") or [])[own_seat]
        private = obs.get("private") or {}
        money_path.append({
            "step": step,
            "money": float(farm.get("money") or 0),
            "n_land": len(farm.get("unlocked_quadrants") or []),
            "hires_today": int(farm.get("hires_today") or 0),
            "hands": len(farm.get("hands") or []),
            "shed": dict(private.get("shed") or {}),
            "seeds": dict(private.get("seeds") or {}),
            "prices": dict((obs.get("market") or {}).get("prices") or {}),
        })

    rows = []
    for i in range(1, len(money_path)):
        prev, cur = money_path[i - 1], money_path[i]
        # if step jumped (new day), still ok
        delta = cur["money"] - prev["money"]
        step = prev["step"]
        # action that *produced* this transition is at step (agent acts, then env steps)
        # In kaggle env, action at step s results in observation at step s+1
        act_rec = own_actions.get(step) or {}
        action = act_rec.get("action") or {}
        prices = act_rec.get("prices") or prev["prices"]
        events, expected = classify_orders(
            action, prices, prev["money"], prev["n_land"], prev["hires_today"]
        )
        # hire cost estimate
        hire_n = sum(1 for o in (action.get("market") or []) if o and o[0] == "HIRE")
        if hire_n:
            hcost = sum(fib(prev["hires_today"] + j) for j in range(hire_n))
            events.append(("HIRE", "", hire_n, None, -hcost))
            expected -= hcost

        # shed inventory delta for products (not cash but production signal)
        shed_delta = {}
        for k in set(cur["shed"]) | set(prev["shed"]):
            d = int(cur["shed"].get(k) or 0) - int(prev["shed"].get(k) or 0)
            if d:
                shed_delta[k] = d

        # if no market events explain delta, residual
        residual = delta - expected if events else delta

        etype = "UNKNOWN"
        product = ""
        qty = 0
        unit = 0
        if events:
            # pick dominant expected event
            ev = max(events, key=lambda e: abs(e[4] or 0))
            etype, product, qty, unit, _ = ev

        rows.append({
            "label": label, "seed": seed, "seat": own_seat,
            "step": step, "day": step // 24, "hour": step % 24,
            "cash_before": prev["money"], "cash_after": cur["money"],
            "cash_delta": delta,
            "expected_from_orders": expected,
            "residual": residual,
            "event_type": etype,
            "product": product,
            "qty": qty,
            "unit": unit,
            "n_events": len(events),
            "events_json": json.dumps(
                [{"t": e[0], "p": e[1], "q": e[2], "u": e[3], "d": e[4]} for e in events],
                ensure_ascii=False,
            ),
            "shed_delta": json.dumps(shed_delta, ensure_ascii=False),
            "hands": cur["hands"],
            "n_land": cur["n_land"],
            "market_n": len(action.get("market") or []),
        })

    final = money_path[-1]["money"] if money_path else None
    init = money_path[0]["money"] if money_path else None
    inflow = sum(r["cash_delta"] for r in rows if r["cash_delta"] > 0)
    outflow = sum(r["cash_delta"] for r in rows if r["cash_delta"] < 0)
    identity_err = (init or 0) + inflow + outflow - (final or 0)
    meta = {
        "label": label, "seed": seed, "seat": own_seat,
        "init": init, "final": final, "inflow": inflow, "outflow": outflow,
        "identity_err": identity_err,
    }
    return rows, meta


def main():
    all_rows = []
    metas = []
    for seat in (0,):
        for seed in (1, 2):
            rows, meta = run_ledger(load_r2, load_b, seed, seat, "R2")
            all_rows.extend(rows)
            metas.append(meta)
            print(f"R2 s{seed} seat{seat}: init={meta['init']} final={meta['final']:.0f} "
                  f"in={meta['inflow']:.0f} out={meta['outflow']:.0f} id_err={meta['identity_err']:.2f}", flush=True)
            rows, meta = run_ledger(load_b, load_r2, seed, seat, "B")
            all_rows.extend(rows)
            metas.append(meta)
            print(f"B  s{seed} seat{seat}: init={meta['init']} final={meta['final']:.0f} "
                  f"in={meta['inflow']:.0f} out={meta['outflow']:.0f} id_err={meta['identity_err']:.2f}", flush=True)

    out = ROOT / "p13_cash_ledger.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        w.writeheader()
        w.writerows(all_rows)

    outm = ROOT / "p13_cash_ledger_meta.csv"
    with open(outm, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(metas[0].keys()))
        w.writeheader()
        w.writerows(metas)

    print("wrote", out.name, outm.name, "events", len(all_rows))


if __name__ == "__main__":
    main()
