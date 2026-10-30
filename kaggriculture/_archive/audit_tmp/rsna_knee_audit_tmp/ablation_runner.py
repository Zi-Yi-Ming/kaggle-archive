"""EXP-7 Phase-1: COK causal ablation benchmark runner.

Variant-parameterized: runs COK-FULL or one ablation (COK-A..E) vs pure v11E,
paired fixed-RNG seeds 1-120, alternating seats, engine 1.32.7.

Per game records: banks, win, per-day bank trajectory, production actions,
SELL volume + realized price by item, and trigger counts peeked from the
module-level meta-state registry (_META_STATE[seat]: h4_evidence/h4_active/
h5_due) after the episode.

Variant map:
  full -> _audit_tmp/repoC/main.py            (COK V10 HEAD, unmodified)
  a    -> variants/cok_a.py  (H4 disabled)      b -> variants/cok_b.py (town demand)
  c    -> variants/cok_c.py  (meta front-run)   d -> variants/cok_d.py (cow choreography)
  e    -> variants/cok_e.py  (route selection)
"""
import importlib.util
import json
import multiprocessing as mp
import sys

sys.path.insert(0, "kaggriculture")
import _pm_pool as P
from kaggle_environments import make

VARIANTS = {
    "full": "_audit_tmp/repoC/main.py",
    "a": "_audit_tmp/variants/cok_a.py",
    "b": "_audit_tmp/variants/cok_b.py",
    "c": "_audit_tmp/variants/cok_c.py",
    "d": "_audit_tmp/variants/cok_d.py",
    "e": "_audit_tmp/variants/cok_e.py",
}
PRODUCTIVE = {"WATER", "PLANT", "HARVEST", "FERTILIZE", "FEED", "CARE",
              "COLLECT_FERTILIZER", "PLACE", "PICKUP", "DROP"}
ITEMS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
         "MILK", "WOOL", "EGG", "FERTILIZER"]


def load_agent(path):
    spec = importlib.util.spec_from_file_location("cok_var_" + path.replace("/", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_v11e():
    spec = importlib.util.spec_from_file_location("v11e_prod", "kaggriculture/main.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent


def play_one(args):
    seed, path = args
    mod = load_agent(path)
    ag = mod.agent
    v_left = seed % 2 == 0
    v11e = load_v11e()
    a, b = (ag, v11e) if v_left else (v11e, ag)
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info["seed"] = seed
    env.run([a, b])
    steps = env.steps
    fin = steps[-1]
    vseat = 0 if v_left else 1

    if v_left:
        bank_v, bank_v11 = fin[0]["observation"]["farms"][0]["money"], fin[1]["observation"]["farms"][1]["money"]
    else:
        bank_v11, bank_v = fin[0]["observation"]["farms"][0]["money"], fin[1]["observation"]["farms"][1]["money"]
    rv = fin[vseat]["reward"]
    r11 = fin[1 - vseat]["reward"]

    day_bank = {}
    prod = {i: 0 for i in PRODUCTIVE}
    sell = {i: [0, 0.0] for i in ITEMS}
    for st in steps:
        obs = st[vseat].get("observation") or {}
        act = st[vseat].get("action") or {}
        day = int(obs.get("day", 0) or 0)
        if day not in day_bank:
            farm = (obs.get("farms") or [{}])[vseat]
            day_bank[day] = float(farm.get("money", 0) or 0)
        prices = (obs.get("market") or {}).get("prices", {}) or {}
        for o in (act.get("market") or []):
            if isinstance(o, (list, tuple)) and len(o) >= 3 and o[0] == "SELL" and o[1] in ITEMS:
                sell[o[1]][0] += int(o[2])
                sell[o[1]][1] += float(prices.get(o[1], 0) or 0) * int(o[2])
        for u in ([act.get("farmer", ["PASS"])] + list(act.get("hands") or [])):
            if isinstance(u, (list, tuple)) and u and u[0] in PRODUCTIVE:
                prod[u[0]] += 1

    # trigger counts peeked from module-level meta registry (seat-keyed)
    mst = getattr(mod, "_META_STATE", None)
    trg = {}
    if mst:
        stt = mst.get(vseat, {}) or {}
        trg = {"h4_evidence": int(stt.get("h4_evidence", 0) or 0),
               "h4_active": int(bool(stt.get("h4_active", False))),
               "h5_due": len(stt.get("h5_due", {}) or {})}

    return {"seed": seed, "vseat": vseat, "bank_v": bank_v, "bank_v11": bank_v11,
            "win_v": int(rv > r11), "win_v11": int(r11 > rv), "tie": int(rv == r11),
            "day_bank": {str(k): v for k, v in day_bank.items()},
            "prod": prod, "sell": sell, "trg": trg}


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", required=True, choices=list(VARIANTS))
    ap.add_argument("--n", type=int, default=120)
    ap.add_argument("--seed0", type=int, default=1)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    jobs = [(s, VARIANTS[a.variant]) for s in range(a.seed0, a.seed0 + a.n)]
    recs = []
    with mp.Pool(a.workers) as pool:
        for i, r in enumerate(pool.imap_unordered(play_one, jobs)):
            recs.append(r)
            if (i + 1) % 10 == 0:
                print(f"[ab] {a.variant}: {i + 1}/{len(jobs)}")
    recs.sort(key=lambda r: r["seed"])
    with open(a.out, "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    print(f"DONE {a.variant} -> {a.out}")


if __name__ == "__main__":
    main()
