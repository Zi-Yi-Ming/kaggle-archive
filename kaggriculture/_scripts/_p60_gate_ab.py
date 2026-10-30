# -*- coding: utf-8 -*-
"""P60: one defensive livestock gate on live alperen. vs guru/R2/V16."""
from __future__ import annotations

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
OPPS = {
    "guru": ROOT / "_external" / "p51_extracted2" / "kaggriculture_fully_dynamic_autonomous_agent.py",
    "R2": ROOT / "_push_medal" / "main.py",
    "V16": ROOT / "_external" / "p41_extracted" / "salem_2900_main.py",
}
SEEDS = (1, 2, 3, 4, 5, 11, 12, 13)

# ONE threshold from P59 (alp 12–14, guru 17)
ANIMAL_GATE = 15
GATE_D0, GATE_D1 = 12, 16  # d12–d15


def load_quiet(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    with redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


def count_animals(obs):
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
    n += int(shed.get("COW") or 0) + int(shed.get("SHEEP") or 0) + int(shed.get("GOOSE") or 0)
    return n


def make_gated(inner):
    """Single gate: d12–15, animals < 15 → top-up BUY_ANIMAL if cash allows."""
    def agent(observation, configuration=None):
        obs = observation or {}
        a = dict(inner(obs, configuration) or {})
        step = int(obs.get("step") or 0)
        day, hour = step // 24, step % 24
        if not (GATE_D0 <= day < GATE_D1 and hour == 0):
            return a
        if count_animals(obs) >= ANIMAL_GATE:
            return a
        player = int(obs.get("player") or 0)
        farms = obs.get("farms") or []
        farm = farms[player] if player < len(farms) else {}
        money = float(farm.get("money") or 0)
        market = [list(o) for o in (a.get("market") or []) if o]
        # gap to 17 like guru scale; cap 2/day to stay conservative
        gap = min(ANIMAL_GATE + 2 - count_animals(obs), 2)
        cash = money
        for _ in range(max(0, gap)):
            if len(market) >= 10:
                break
            if cash >= 420:
                market.append(["BUY_ANIMAL", "COW", 1])
                cash -= 400
            elif cash >= 520:
                market.append(["BUY_ANIMAL", "SHEEP", 1])
                cash -= 500
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


def d15_animals(make_us, opp_path, seed):
    """Snapshot animals at d15 midday for causal check."""
    snap = {}

    def wrap(obs, configuration=None):
        act = make_us_proxy["fn"](obs, configuration)
        step = int(obs.get("step") or 0)
        if step == 15 * 24 + 12:
            snap["animals"] = count_animals(obs)
            snap["money"] = float((obs.get("farms") or [{}])[int(obs.get("player") or 0)].get("money") or 0)
        return act

    make_us_proxy = {"fn": make_us()}
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info = {"seed": int(seed)}
    env.run([wrap, load_quiet(opp_path, f"d15_{seed}")])
    return snap.get("animals"), snap.get("money")


def main():
    def make_base():
        return load_quiet(ALPEREN, f"p60_base_{id(object())}")

    def make_cand():
        inner = load_quiet(ALPEREN, f"p60_cand_{id(object())}")
        return make_gated(inner)

    print("=== P60 A/B ===", flush=True)
    print(f"gate: d{GATE_D0}-d{GATE_D1-1} animals<{ANIMAL_GATE}", flush=True)

    rows = []
    print("\n-- baseline live alperen --", flush=True)
    base_res = {}
    for oname, opath in OPPS.items():
        w, d, l, m = h2h(make_base, opath, SEEDS, f"base_vs_{oname}")
        base_res[oname] = (w, d, l, m)
        print(f"  base vs {oname}: {w}-{d}-{l} bank={m:.0f}", flush=True)

    print("\n-- candidate (gate) --", flush=True)
    cand_res = {}
    for oname, opath in OPPS.items():
        w, d, l, m = h2h(make_cand, opath, SEEDS, f"cand_vs_{oname}")
        cand_res[oname] = (w, d, l, m)
        print(f"  cand vs {oname}: {w}-{d}-{l} bank={m:.0f}", flush=True)
        rows.append({
            "arm": "candidate", "opponent": oname,
            "W": w, "D": d, "L": l, "bank_mean": m,
        })
    for oname in OPPS:
        w, d, l, m = base_res[oname]
        rows.append({
            "arm": "baseline", "opponent": oname,
            "W": w, "D": d, "L": l, "bank_mean": m,
        })

    # causal: d15 animals vs guru
    print("\n-- d15 animals vs guru --", flush=True)
    for seed in SEEDS[:4]:
        ab, mb = d15_animals(make_base, OPPS["guru"], seed)
        ac, mc = d15_animals(make_cand, OPPS["guru"], seed)
        print(f"  s{seed}: base animals={ab} money={mb:.0f} | cand animals={ac} money={mc:.0f}", flush=True)

    gw, gd, gl, _ = base_res["guru"]
    cw, cd, cl, _ = cand_res["guru"]
    rw, rd, rl, _ = base_res["R2"]
    crw, crd, crl, _ = cand_res["R2"]
    vw, vd, vl, _ = base_res["V16"]
    cvw, cvd, cvl, _ = cand_res["V16"]

    guru_up = (cw - cl) > (gw - gl)
    r2_ok = (crw - crl) >= (rw - rl) - 1  # allow tiny noise
    v16_ok = (cvw - cvl) >= (vw - vl) - 1

    print("\n=== DECISION ===", flush=True)
    print(f"guru WL base {gw}-{gd}-{gl} → cand {cw}-{cd}-{cl}", flush=True)
    print(f"R2   WL base {rw}-{rd}-{rl} → cand {crw}-{crd}-{crl}", flush=True)
    print(f"V16  WL base {vw}-{vd}-{vl} → cand {cvw}-{cvd}-{cvl}", flush=True)

    if guru_up and r2_ok and v16_ok:
        verdict = "P60_PASS"
    elif guru_up and not (r2_ok and v16_ok):
        verdict = "P60_TRADEOFF"
    elif (cw + cd) > (gw + gd) and not guru_up:
        verdict = "P60_NO_CAUSAL_SIGNAL"
    else:
        verdict = "P60_REJECT"
    print(verdict, flush=True)

    with open(ROOT / "p60_gate_ab.csv", "w", newline="", encoding="utf-8") as f:
        wri = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        wri.writeheader()
        wri.writerows(rows)
    print("wrote p60_gate_ab.csv", flush=True)


if __name__ == "__main__":
    main()
