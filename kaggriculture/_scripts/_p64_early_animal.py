# -*- coding: utf-8 -*-
"""P64: one early livestock gate on live alperen (d3–d8, ≤1 animal/day)."""
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
OPPS = {
    "alperen": ALPEREN,
    "R2": ROOT / "_push_medal" / "main.py",
    "V16": ROOT / "_external" / "p41_extracted" / "salem_2900_main.py",
    "guru": ROOT / "_external" / "p51_extracted2" / "kaggriculture_fully_dynamic_autonomous_agent.py",
}
FINN = ROOT / "reference_agents" / "fallow_finn.py"
SEEDS = (1, 2, 3, 4, 5)

# ONE conservative gate: d3–d8, animals < 6, +1 animal per dawn if cash ok
GATE_D0, GATE_D1 = 3, 9
ANIMAL_TARGET = 6


def load_quiet(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    with redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


def animals_and_cash(obs):
    player = int(obs.get("player") or 0)
    farms = obs.get("farms") or []
    farm = farms[player] if player < len(farms) else {}
    tiles = farm.get("tiles") or []
    n = 0
    for row in tiles:
        for t in row:
            if isinstance(t, dict) and t.get("animal"):
                n += 1
    shed = dict((obs.get("private") or {}).get("shed") or {})
    n += sum(int(shed.get(a) or 0) for a in ("COW", "SHEEP", "GOOSE"))
    return n, float(farm.get("money") or 0)


def make_gated(inner):
    def agent(observation, configuration=None):
        obs = observation or {}
        a = dict(inner(obs, configuration) or {})
        step = int(obs.get("step") or 0)
        day, hour = step // 24, step % 24
        if not (GATE_D0 <= day < GATE_D1 and hour == 0):
            return a
        n, cash = animals_and_cash(obs)
        if n >= ANIMAL_TARGET:
            return a
        market = [list(o) for o in (a.get("market") or []) if o]
        if len(market) < 10:
            if cash >= 420:
                market.append(["BUY_ANIMAL", "COW", 1])
            elif cash >= 520:
                market.append(["BUY_ANIMAL", "SHEEP", 1])
        a["market"] = market[:10]
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
            res = "W"
        elif theirs > our + 1:
            l += 1
            res = "L"
        else:
            d += 1
            res = "D"
        print(f"    {label} s{seed}: us={our:.0f} opp={theirs:.0f} {res}", flush=True)
    return w, d, l, statistics.mean(banks) if banks else 0


def d5_animals(make_us, opp_path, seed):
    got = {}

    def wrap(obs, configuration=None):
        act = make_us_proxy["fn"](obs, configuration)
        if int(obs.get("step") or 0) == 5 * 24 + 12:
            got["n"], got["cash"] = animals_and_cash(obs)
        return act

    make_us_proxy = {"fn": make_us()}
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info = {"seed": int(seed)}
    env.run([wrap, load_quiet(opp_path, f"d5_{seed}")])
    return got.get("n"), got.get("cash")


def main():
    def make_base():
        return load_quiet(ALPEREN, f"p64b_{id(object())}")

    def make_cand():
        return make_gated(load_quiet(ALPEREN, f"p64c_{id(object())}"))

    print(f"gate d{GATE_D0}-{GATE_D1-1} animals<{ANIMAL_TARGET} +1/day", flush=True)

    base_res, cand_res = {}, {}
    rows = []
    print("\n-- baseline --", flush=True)
    for oname, opath in OPPS.items():
        w, d, l, m = h2h(make_base, opath, SEEDS, f"base_{oname}")
        base_res[oname] = (w, d, l, m)
        print(f"  base vs {oname}: {w}-{d}-{l} bank={m:.0f}", flush=True)

    print("\n-- candidate --", flush=True)
    for oname, opath in OPPS.items():
        w, d, l, m = h2h(make_cand, opath, SEEDS, f"cand_{oname}")
        cand_res[oname] = (w, d, l, m)
        print(f"  cand vs {oname}: {w}-{d}-{l} bank={m:.0f}", flush=True)
        rows.append({"arm": "cand", "opponent": oname, "W": w, "D": d, "L": l, "bank": m})
    for oname in OPPS:
        w, d, l, m = base_res[oname]
        rows.append({"arm": "base", "opponent": oname, "W": w, "D": d, "L": l, "bank": m})

    # finn quick
    print("\n-- finn --", flush=True)
    for arm, maker in (("base", make_base), ("cand", make_cand)):
        banks = []
        for seed in SEEDS:
            b0, _ = run(maker(), load_quiet(FINN, f"f_{arm}_{seed}"), seed)
            banks.append(b0)
        print(f"  {arm} finn mean={sum(banks)/len(banks):.0f}", flush=True)

    print("\n-- d5 animals vs R2 --", flush=True)
    for seed in SEEDS[:3]:
        ab, _ = d5_animals(make_base, OPPS["R2"], seed)
        ac, _ = d5_animals(make_cand, OPPS["R2"], seed)
        print(f"  s{seed}: base={ab} cand={ac}", flush=True)

    print("\n=== DECISION ===", flush=True)
    for oname in OPPS:
        print(f"  {oname}: {base_res[oname][:3]} → {cand_res[oname][:3]}", flush=True)

    # PASS: improve alperen or guru without losing R2/V16 badly
    alp_up = (cand_res["alperen"][0] - cand_res["alperen"][2]) > (base_res["alperen"][0] - base_res["alperen"][2])
    guru_up = (cand_res["guru"][0] - cand_res["guru"][2]) > (base_res["guru"][0] - base_res["guru"][2])
    r2_ok = (cand_res["R2"][0] - cand_res["R2"][2]) >= (base_res["R2"][0] - base_res["R2"][2]) - 1
    v16_ok = (cand_res["V16"][0] - cand_res["V16"][2]) >= (base_res["V16"][0] - base_res["V16"][2]) - 1

    if (alp_up or guru_up) and r2_ok and v16_ok:
        verdict = "P64_SIGNAL"
    elif not r2_ok or not v16_ok:
        verdict = "P64_TRADEOFF_OR_REJECT"
    else:
        verdict = "P64_NO_SIGNAL"
    print(verdict, flush=True)

    with open(ROOT / "p64_early_animal.csv", "w", newline="", encoding="utf-8") as f:
        wri = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        wri.writeheader()
        wri.writerows(rows)
    print("wrote p64_early_animal.csv", flush=True)


if __name__ == "__main__":
    main()
