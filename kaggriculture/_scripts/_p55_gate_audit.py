# -*- coding: utf-8 -*-
"""P55 Sparse Dynamic Gate Audit: live alperen vs elite family divergences."""
from __future__ import annotations

import csv
import importlib.util
import io
import json
import statistics
import sys
from collections import Counter, defaultdict
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

ALPEREN = ROOT / "_external" / "p51_extracted2" / "kaggriculture_metacounter_r1_scored_agent.py"
ELITES = {
    "R2": ROOT / "_push_medal" / "main.py",
    "V16": ROOT / "_external" / "p41_extracted" / "salem_2900_main.py",
    "kaito_v27": ROOT / "_external" / "public_nb" / "kaito_v27" / "main.py",
    "qeinstein": ROOT / "_external" / "git" / "qeinstein" / "dist" / "sub-009-moev2" / "main.py",
    "rayk_rank": ROOT / "_external" / "public_nb" / "rayk_rank" / "main.py",
    "guru_dynamic": ROOT / "_external" / "p51_extracted2" / "kaggriculture_fully_dynamic_autonomous_agent.py",
}
SEEDS = (1, 2, 3)


def load_quiet(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    with redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


def akey(a):
    return json.dumps({"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                      sort_keys=True, default=str)


def classify(a, b):
    ma, mb = json.dumps(a.get("market"), sort_keys=True, default=str), json.dumps(b.get("market"), sort_keys=True, default=str)
    if ma != mb:
        def ops(ms):
            return {tuple(o[:2]) if o else () for o in ms}
        if any(o and o[0] == "SELL" for o in (a.get("market") or []) + (b.get("market") or [])):
            return "SELL"
        if ops(a.get("market") or []) != ops(b.get("market") or []):
            return "BUY_HIRE"
        return "MARKET_QTY"
    fa = json.dumps({"f": a.get("farmer"), "h": a.get("hands")}, sort_keys=True, default=str)
    fb = json.dumps({"f": b.get("farmer"), "h": b.get("hands")}, sort_keys=True, default=str)
    if fa != fb:
        return "WORKER"
    return "OTHER"


def state_sig(obs):
    player = int(obs.get("player") or 0)
    farms = obs.get("farms") or []
    farm = farms[player] if player < len(farms) else {}
    private = obs.get("private") or {}
    shed = dict(private.get("shed") or {})
    prices = dict((obs.get("market") or {}).get("prices") or {})
    shops = list((obs.get("town") or {}).get("unlocked_shops") or [])
    tiles = farm.get("tiles") or []
    plants = animals = empty = weeds = 0
    for row in tiles:
        for t in row:
            if t is None:
                empty += 1
            elif isinstance(t, dict):
                if t.get("kind") == "PLANT":
                    plants += 1
                elif t.get("kind") == "WEED":
                    weeds += 1
                if t.get("animal"):
                    animals += 1
    return {
        "money": float(farm.get("money") or 0),
        "hands": len(farm.get("hands") or []),
        "n_land": len(farm.get("unlocked_quadrants") or []),
        "plants": plants, "animals": animals, "empty": empty, "weeds": weeds,
        "shed_total": sum(int(v or 0) for v in shed.values()),
        "n_shops": len(shops),
        "shops": shops,
        "px_wheat": int(prices.get("WHEAT") or 0),
        "px_melon": int(prices.get("MELON") or 0),
        "px_milk": int(prices.get("MILK") or 0),
    }


def record_pair(a_fn, b_fn, seed):
    acts_a, acts_b, st_a, st_b = [], [], [], []

    def wa(obs, configuration=None):
        act = a_fn(obs, configuration)
        acts_a.append(act)
        st_a.append(state_sig(obs))
        return act

    def wb(obs, configuration=None):
        act = b_fn(obs, configuration)
        acts_b.append(act)
        st_b.append(state_sig(obs))
        return act

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([wa, wb])
    f = env.steps[-1]
    bank_a = float(f[0]["observation"]["farms"][0]["money"])
    bank_b = float(f[1]["observation"]["farms"][1]["money"])
    return acts_a, acts_b, st_a, st_b, bank_a, bank_b


def main():
    alp = load_quiet(ALPEREN, "p55_alp")
    pair_rows = []
    landmark_days = Counter()
    landmark_types = Counter()
    state_diff_at = Counter()

    print("=== alperen vs each elite (seed1 live) ===", flush=True)
    for oname, opath in ELITES.items():
        print(f"\n-- vs {oname} --", flush=True)
        opp = load_quiet(opath, f"p55_o_{oname}")
        acts_a, acts_b, st_a, st_b, ba, bb = record_pair(alp, opp, 1)
        print(f"  banks alperen={ba:.0f} opp={bb:.0f}", flush=True)

        fd = None
        for t in range(min(len(acts_a), len(acts_b))):
            if akey(acts_a[t]) != akey(acts_b[t]):
                fd = t
                break
        if fd is None:
            print("  no divergence (identical?)", flush=True)
            continue
        day = fd // 24
        typ = classify(acts_a[fd], acts_b[fd])
        sa, sb = st_a[fd - 1] if fd else st_a[0], st_b[fd - 1] if fd else st_b[0]
        diffs = [k for k in sa if sa.get(k) != sb.get(k) and k != "shops"]
        print(f"  first_div step={fd} day={day} hour={fd%24} type={typ} state_diff={diffs}", flush=True)
        print(f"    alp_money={sa['money']:.0f} opp_money={sb['money']:.0f} "
              f"alp_shops={sa['shops']} opp_shops={sb['shops']}", flush=True)
        pair_rows.append({
            "opponent": oname, "step": fd, "day": day, "hour": fd % 24,
            "type": typ, "state_diff": "|".join(diffs),
            "alp_money": sa["money"], "opp_money": sb["money"],
            "alp_shops": "|".join(sa["shops"]), "opp_shops": "|".join(sb["shops"]),
            "alp_bank": ba, "opp_bank": bb,
        })
        landmark_days[day] += 1
        landmark_types[typ] += 1
        for d in diffs:
            state_diff_at[d] += 1

        # count divergences in landmark windows
        for win_name, lo, hi in (("d6", 6, 7), ("d7", 7, 8), ("d9", 9, 10),
                                  ("d10", 10, 11), ("d12", 12, 13)):
            n_div = sum(
                1 for t in range(lo * 24, min(hi * 24, len(acts_a), len(acts_b)))
                if akey(acts_a[t]) != akey(acts_b[t])
            )
            print(f"    divergent steps in {win_name}: {n_div}/24", flush=True)

    print("\n=== first_div day histogram ===", flush=True)
    print(landmark_days.most_common(), flush=True)
    print("types", landmark_types.most_common(), flush=True)
    print("state_diff", state_diff_at.most_common(), flush=True)

    with open(ROOT / "p55_gate_landmarks.csv", "w", newline="", encoding="utf-8") as f:
        wri = csv.DictWriter(f, fieldnames=list(pair_rows[0].keys()))
        wri.writeheader()
        wri.writerows(pair_rows)

    # Stage2: alperen vs R2 multi-seed first_div
    print("\n=== alperen vs R2 multi-seed first_div ===", flush=True)
    r2 = load_quiet(ELITES["R2"], "p55_r2ms")
    ms = []
    for seed in SEEDS:
        alp2 = load_quiet(ALPEREN, f"p55_alp_{seed}")
        r2b = load_quiet(ELITES["R2"], f"p55_r2_{seed}")
        aa, bb, sa, sb, ba, bbank = record_pair(alp2, r2b, seed)
        fd = next((t for t in range(min(len(aa), len(bb))) if akey(aa[t]) != akey(bb[t])), None)
        day = fd // 24 if fd is not None else -1
        typ = classify(aa[fd], bb[fd]) if fd is not None else "NONE"
        print(f"  s{seed}: fd={fd} d{day} {typ} alp={ba:.0f} r2={bbank:.0f}", flush=True)
        ms.append({"seed": seed, "fd": fd, "day": day, "type": typ, "alp": ba, "r2": bbank})

    print("wrote p55_gate_landmarks.csv", flush=True)


if __name__ == "__main__":
    main()
