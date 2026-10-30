# -*- coding: utf-8 -*-
"""P55: live-alperen wrapper mutations (SELL landmark ±1). Baseline is live, not tape."""
from __future__ import annotations

import csv
import importlib.util
import io
import statistics
import sys
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

ALPEREN = ROOT / "_external" / "p51_extracted2" / "kaggriculture_metacounter_r1_scored_agent.py"
R2 = ROOT / "_push_medal" / "main.py"
SEEDS = (1, 2, 3, 4, 5)
ITEMS = ("MELON", "MILK", "WOOL", "STRAWBERRY", "FERTILIZER", "EGG")


def load_quiet(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    with redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


def make_shift_first_sell(inner, item, delta):
    """Live wrapper: delay/advance only the first SELL of `item` by `delta` steps.

    Preserves all other live decisions. state = per-game reset via step==0.
    """
    state = {"seen": False, "pending": None}  # pending = (qty,) or None

    def agent(observation, configuration=None):
        obs = observation or {}
        step = int(obs.get("step") or 0)
        if step == 0:
            state["seen"] = False
            state["pending"] = None

        a = dict(inner(obs, configuration) or {})
        market = [list(o) for o in (a.get("market") or []) if o]

        # inject delayed sell one step later
        if state["pending"] is not None and delta < 0:
            # advance: we already pulled it; inject now
            qty = state["pending"]
            state["pending"] = None
            if qty > 0 and len(market) < 10:
                # merge if exists
                hit = False
                for o in market:
                    if o[0] == "SELL" and o[1] == item:
                        o[2] = int(o[2]) + qty
                        hit = True
                        break
                if not hit:
                    market.append(["SELL", item, qty])
            a["market"] = market
            return a

        if state["pending"] is not None and delta > 0:
            # hold: sell would have been this step; skip one turn
            # actually pending means we removed last step; inject THIS step
            qty = state["pending"]
            state["pending"] = None
            if qty > 0 and len(market) < 10:
                hit = False
                for o in market:
                    if o[0] == "SELL" and o[1] == item:
                        o[2] = int(o[2]) + qty
                        hit = True
                        break
                if not hit:
                    market.append(["SELL", item, qty])
            a["market"] = market
            return a

        if not state["seen"]:
            new_m = []
            found = None
            for o in market:
                if found is None and o[0] == "SELL" and o[1] == item:
                    found = int(o[2])
                    continue
                new_m.append(o)
            if found is not None and found > 0:
                state["seen"] = True
                state["pending"] = found
                a["market"] = new_m
                # if delta < 0 we want earlier — too late this step; treat as +1 only for delay
                # for advance: inject immediately (same step is "earlier" only if we could see next;
                # we cannot, so ADVANCE is implemented as delay of next... skip true advance.)
                if delta < 0:
                    # cannot move into the past; re-insert now (no-op) — mark unused
                    market2 = list(new_m)
                    market2.append(["SELL", item, found])
                    a["market"] = market2[:10]
                    state["pending"] = None
        return a

    return agent


def run(a0, a1, seed):
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([a0, a1])
    f = env.steps[-1]
    return (
        float(f[0]["observation"]["farms"][0]["money"]),
        float(f[1]["observation"]["farms"][1]["money"]),
    )


def h2h(make_us, opp_path, seeds, label):
    w = d = l = 0
    banks = []
    for seed in seeds:
        a0, a1 = run(make_us(), load_quiet(opp_path, f"{label}_{seed}a"), seed)
        b0, b1 = run(load_quiet(opp_path, f"{label}_{seed}b"), make_us(), seed)
        our = (a0 + b1) / 2
        theirs = (a1 + b0) / 2
        banks.append(our)
        if our > theirs + 1:
            w += 1
        elif theirs > our + 1:
            l += 1
        else:
            d += 1
        print(f"    {label} s{seed}: us={our:.0f} opp={theirs:.0f}", flush=True)
    return w, d, l, statistics.mean(banks) if banks else 0


def main():
    print("loading live alperen baseline...", flush=True)
    # fresh load per game
    def make_base():
        return load_quiet(ALPEREN, f"p55_base_{id(object())}")

    cands = []
    cands.append(("c00_base", make_base, "none"))

    for item in ITEMS:
        def make_mut(item=item):
            inner = load_quiet(ALPEREN, f"p55_{item}_{id(object())}")
            return make_shift_first_sell(inner, item, +1)
        cands.append((f"c_{item.lower()}_delay1", make_mut, f"delay_first_{item}_1"))

    rows = []
    print("\n=== H2H vs live alperen and R2 ===", flush=True)
    results = []
    for cid, maker, mut in cands:
        print(f"  {cid} ...", flush=True)
        wa, da, la, ba = h2h(maker, ALPEREN, SEEDS, cid + "_vs_alp")
        wr, dr, lr, br = h2h(maker, R2, SEEDS, cid + "_vs_r2")
        print(f"  => {cid}: vs_alp {wa}-{da}-{la} bank={ba:.0f} | "
              f"vs_R2 {wr}-{dr}-{lr} bank={br:.0f} | {mut}", flush=True)
        rec = {
            "id": cid, "mutation": mut,
            "vs_alp_W": wa, "vs_alp_D": da, "vs_alp_L": la,
            "vs_alp_WL": wa - la, "vs_alp_bank": ba,
            "vs_R2_W": wr, "vs_R2_D": dr, "vs_R2_L": lr,
            "vs_R2_WL": wr - lr, "vs_R2_bank": br,
        }
        results.append(rec)
        rows.append(rec)

    results.sort(key=lambda r: (-(r["vs_alp_WL"] + r["vs_R2_WL"]), -(r["vs_alp_bank"] + r["vs_R2_bank"])))
    print("\n=== RANK ===", flush=True)
    for r in results:
        print(f"  {r['id']:22s} alpWL={r['vs_alp_WL']} r2WL={r['vs_R2_WL']}", flush=True)

    base = next(r for r in results if r["id"] == "c00_base")
    best = results[0]
    improve = (
        best["id"] != "c00_base"
        and best["vs_alp_WL"] > base["vs_alp_WL"]
        and best["vs_R2_WL"] >= base["vs_R2_WL"]
    )
    print(f"\nbest={best['id']} improve={improve}", flush=True)
    print("L1_LIVE_SIGNAL" if improve else "L1_LIVE_NO_SIGNAL", flush=True)

    with open(ROOT / "p55_live_sell.csv", "w", newline="", encoding="utf-8") as f:
        wri = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        wri.writeheader()
        wri.writerows(rows)
    print("wrote p55_live_sell.csv", flush=True)


if __name__ == "__main__":
    main()
