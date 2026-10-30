# -*- coding: utf-8 -*-
"""P54 L1: SELL timing ±1 on alperen_meta tape. Eval vs alperen + R2."""
from __future__ import annotations

import copy
import csv
import importlib.util
import io
import json
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
SELL_ITEMS = ("MELON", "MILK", "WOOL", "STRAWBERRY", "EGG", "FERTILIZER", "WHEAT")


def load_quiet(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    with redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


def record_tape(fn, seed=1):
    """Run alperen vs R2 (or finn-less) and capture 720 actions."""
    opp = load_quiet(R2, f"p54_opp_{seed}")
    acts = []

    def wrap(obs, configuration=None):
        a = fn(obs, configuration)
        acts.append({
            "market": a.get("market") or [],
            "farmer": a.get("farmer") or ["PASS"],
            "hands": a.get("hands") or [],
        })
        return a

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([wrap, opp])
    bank = float(env.steps[-1][0]["observation"]["farms"][0]["money"])
    return acts, bank


def find_first_sell(tape, item):
    for t, a in enumerate(tape):
        for o in a.get("market") or []:
            if o and o[0] == "SELL" and len(o) >= 3 and o[1] == item:
                return t
    return None


def shift_first_sell(tape, item, delta):
    t0 = find_first_sell(tape, item)
    if t0 is None:
        return None, []
    t1 = t0 + delta
    if t1 < 0 or t1 >= 720 or t1 == t0:
        return None, []
    new = copy.deepcopy(tape)
    moved = None
    mk0 = []
    for o in new[t0]["market"]:
        if moved is None and o and o[0] == "SELL" and len(o) >= 3 and o[1] == item:
            moved = list(o)
            continue
        mk0.append(o)
    if moved is None:
        return None, []
    new[t0]["market"] = mk0
    mk1 = list(new[t1]["market"])
    merged = False
    for o in mk1:
        if o and o[0] == "SELL" and len(o) >= 3 and o[1] == item:
            o[2] = int(o[2]) + int(moved[2])
            merged = True
            break
    if not merged:
        if len(mk1) >= 10:
            return None, []
        mk1.append(moved)
    new[t1]["market"] = mk1
    return new, [t0, t1]


def tape_agent(tape):
    def agent(observation, configuration=None):
        step = int((observation or {}).get("step") or 0)
        step = max(0, min(len(tape) - 1, step))
        a = tape[step]
        return {"farmer": a["farmer"], "hands": a["hands"], "market": a["market"]}
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


def h2h(tape, opp_path, seeds, label):
    w = d = l = 0
    banks = []
    for seed in seeds:
        a0, a1 = run(tape_agent(tape), load_quiet(opp_path, f"{label}_{seed}a"), seed)
        b0, b1 = run(load_quiet(opp_path, f"{label}_{seed}b"), tape_agent(tape), seed)
        our = (a0 + b1) / 2
        theirs = (a1 + b0) / 2
        banks.append(our)
        if our > theirs + 1:
            w += 1
        elif theirs > our + 1:
            l += 1
        else:
            d += 1
    return w, d, l, statistics.mean(banks) if banks else 0


def main():
    alp = load_quiet(ALPEREN, "p54_alperen")
    tape, bank = record_tape(alp, 1)
    print(f"recorded alperen tape vs R2 s1 bank={bank:.0f} n={len(tape)}", flush=True)

    # first sell landmarks
    for item in SELL_ITEMS:
        t = find_first_sell(tape, item)
        print(f"  first SELL {item}: step={t}", flush=True)

    cands = [("c00_base", tape, [], "none")]
    for item in SELL_ITEMS:
        t0 = find_first_sell(tape, item)
        if t0 is None:
            print(f"  SKIP {item}", flush=True)
            continue
        for dlt in (-1, 1):
            nt, ch = shift_first_sell(tape, item, dlt)
            if nt is None:
                print(f"  SKIP {item} {dlt:+d}", flush=True)
                continue
            cands.append((f"c_{item.lower()}_d{dlt:+d}", nt, ch, f"shift_{item}_{dlt:+d}"))
    print(f"n_cands={len(cands)}", flush=True)

    rows = []
    print("\n=== H2H vs alperen (frozen original tape) and R2 ===", flush=True)
    # baseline live agent for comparison too
    results = []
    for cid, ct, ch, mut in cands:
        wa, da, la, ba = h2h(ct, ALPEREN, SEEDS, cid + "_vs_alp")
        wr, dr, lr, br = h2h(ct, R2, SEEDS, cid + "_vs_r2")
        wl_a = wa - la
        wl_r = wr - lr
        print(f"  {cid:20s} vs_alp {wa}-{da}-{la} bank={ba:.0f} | "
              f"vs_R2 {wr}-{dr}-{lr} bank={br:.0f} | {mut}", flush=True)
        rec = {
            "id": cid, "mutation": mut,
            "vs_alp_W": wa, "vs_alp_D": da, "vs_alp_L": la, "vs_alp_WL": wl_a, "vs_alp_bank": ba,
            "vs_R2_W": wr, "vs_R2_D": dr, "vs_R2_L": lr, "vs_R2_WL": wl_r, "vs_R2_bank": br,
            "changed": "|".join(map(str, ch)),
        }
        results.append(rec)
        rows.append(rec)

    results.sort(key=lambda r: (-(r["vs_alp_WL"] + r["vs_R2_WL"]), -(r["vs_alp_bank"] + r["vs_R2_bank"])))
    print("\n=== RANK (vs_alp_WL + vs_R2_WL) ===", flush=True)
    for r in results:
        print(f"  {r['id']:20s} alpWL={r['vs_alp_WL']} r2WL={r['vs_R2_WL']}", flush=True)

    base = next(r for r in results if r["id"] == "c00_base")
    best = results[0]
    improve = (
        best["id"] != "c00_base"
        and best["vs_alp_WL"] > base["vs_alp_WL"]
        and best["vs_R2_WL"] >= base["vs_R2_WL"]
    )
    print(f"\nbest={best['id']} improve_over_base={improve}", flush=True)

    if improve:
        print("L1_SIGNAL — expand seeds before any submit", flush=True)
    else:
        print("L1_NO_SIGNAL — do not submit", flush=True)

    with open(ROOT / "p54_l1_sell.csv", "w", newline="", encoding="utf-8") as f:
        wri = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        wri.writeheader()
        wri.writerows(rows)
    print("wrote p54_l1_sell.csv", flush=True)


if __name__ == "__main__":
    main()
