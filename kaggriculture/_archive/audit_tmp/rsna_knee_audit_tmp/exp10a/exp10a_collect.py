"""EXP-10A collection: Phase A deterministic control + Phase B cross-seed
per-step snapshots (canonical action / own state / market / opponent).

Gates: A (seed7 seat1 20 games double-run, streams byte-identical),
B (40 games 720/720), C (executed-ledger recon 0), D (fingerprint unchanged).
"""
import hashlib
import json
import multiprocessing as mp
import sys

sys.path.insert(0, "kaggriculture")
sys.path.insert(0, "_audit_tmp/route_transfer")
import _pm_pool as P
import executed_ledger as EL
from kaggle_environments import make

RAW_DIR = "_audit_tmp/exp10a"
PROD_PATH = "kaggriculture/main.py"
PROD_MD5 = "224a1c47cf9b07624f5faabbb5227891"


def load_prod():
    import importlib.util
    spec = importlib.util.spec_from_file_location("prod", PROD_PATH)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def canon_act(a):
    """Canonical per-step action string: farmer|hands|market."""
    if not isinstance(a, dict):
        a = {}
    farmer = a.get("farmer") or ["PASS"]
    hands = [list(h) for h in (a.get("hands") or [])]
    market = [list(m) for m in (a.get("market") or [])]
    def enc(u):
        return ":".join(str(x) for x in u)
    f = "F:" + enc(farmer)
    hs = "|".join("H" + str(i) + ":" + enc(u) for i, u in enumerate(hands))
    ms = ",".join("M:" + enc(m) for m in market)
    return f + "||" + hs + "||" + ms


def run_game(seed, seat):
    opp = P.load_agent("closer_cleo")
    cand = load_prod()
    a, b = (cand, opp) if seat == 0 else (opp, cand)
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info["seed"] = seed
    env.run([a, b])
    return env.steps


def phase_a_one(args):
    game_idx, run_idx = args
    steps = run_game(7, 1)
    canon = [canon_act(steps[s][1].get("action") or {}) for s in range(len(steps))]
    md5 = hashlib.md5("|".join(canon).encode()).hexdigest()
    return {"game": game_idx, "run": run_idx, "md5": md5,
            "steps": len(steps), "bank": steps[-1][1]["observation"]["farms"][1]["money"]}


def phase_b_one(args):
    seed, seat = args
    steps = run_game(seed, seat)
    # Gates B/C on this game
    agg, valid, n, mism = EL.replay_game(steps, seat)
    final = steps[-1][seat]["observation"]["farms"][seat]["money"]
    rev = agg["SELL"][1]
    cost = sum(agg[t][1] for t in ("BUY_SEED", "BUY_PRODUCT", "BUY_ANIMAL", "HIRE", "BUY_LAND"))
    recon = final - (EL.INITIAL_BANK + rev - cost)
    recs = []
    for s in range(len(steps)):
        obs = steps[s][seat].get("observation") or {}
        act = steps[s][seat].get("action") or {}
        opp_act = steps[s][1 - seat].get("action") or {}
        farm = (obs.get("farms") or [{}])[seat]
        priv = obs.get("private") or {}
        mkt = obs.get("market") or {}
        town = obs.get("town") or {}
        tiles = farm.get("tiles") or []
        crops = sum(1 for row in tiles for t in row if isinstance(t, dict) and t.get("kind") == "PLANT")
        animals = sum(1 for row in tiles for t in row if isinstance(t, dict) and "animal" in t)
        weeds = sum(1 for row in tiles for t in row if isinstance(t, dict) and t.get("kind") == "WEED")
        owned = sum(1 for row in tiles for t in row if t != "LOCKED")
        recs.append({
            "seed": seed, "seat": seat, "step": s, "day": obs.get("day", 0),
            "canon": canon_act(act),
            "act_farmer": act.get("farmer"), "act_hands": act.get("hands"),
            "act_market": act.get("market"),
            "money": farm.get("money"), "hands_n": len(farm.get("hands") or []),
            "farmer_pos": farm.get("farmer"), "hands_pos": farm.get("hands"),
            "tiles_owned": owned, "tiles_crop": crops, "tiles_animal": animals, "tiles_weed": weeds,
            "shed": priv.get("shed"), "seeds": priv.get("seeds"),
            "inventories": priv.get("inventories"),
            "shops": town.get("unlocked_shops"),
            "mkt_inv": mkt.get("inventory"), "mkt_price": mkt.get("prices"),
            "opp_act": canon_act(opp_act),
        })
    with open(f"{RAW_DIR}/raw_{seed}_{seat}.jsonl", "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return {"seed": seed, "seat": seat, "steps": len(steps), "valid": valid, "n": n,
            "recon": round(recon, 4), "bank": round(final, 2),
            "first_mismatch": mism[0][0] if mism else None}


def main():
    md5 = hashlib.md5(open(PROD_PATH, "rb").read()).hexdigest()
    print(f"Gate D fingerprint: {md5} match={md5 == PROD_MD5}")

    # Phase A: seed 7 seat 1, 20 games double-run
    tasks_a = [(i, r) for i in range(20) for r in (0, 1)]
    with mp.Pool(8) as pool:
        ra = list(pool.imap_unordered(phase_a_one, tasks_a))
    ra.sort(key=lambda x: (x["game"], x["run"]))
    by_game = {}
    for r in ra:
        by_game.setdefault(r["game"], []).append(r)
    ok_a = all(len(v) == 2 and v[0]["md5"] == v[1]["md5"] for v in by_game.values())
    md5s = set(r["md5"] for r in ra)
    print(f"Gate A: 20 games double-run identical = {ok_a} (unique streams: {len(md5s)}) | "
          f"steps all {set(r['steps'] for r in ra)} | banks all {set(r['bank'] for r in ra)}")

    # Phase B: seeds 1-20 x seats 0/1
    tasks_b = [(s, seat) for s in range(1, 21) for seat in (0, 1)]
    with mp.Pool(8) as pool:
        rb = list(pool.imap_unordered(phase_b_one, tasks_b))
    rb.sort(key=lambda x: (x["seed"], x["seat"]))
    ok_b = all(r["steps"] == 720 for r in rb)
    ok_c = all(abs(r["recon"]) < 0.005 for r in rb)
    print(f"Gate B: 40 games 720/720 = {ok_b} | Gate C: recon==0 = {ok_c} "
          f"({sum(1 for r in rb if abs(r['recon']) > 0.005)} failures)")
    print(f"Phase B 完成: {len(rb)} games | bank 范围 {min(r['bank'] for r in rb):.0f}-{max(r['bank'] for r in rb):.0f}")
    with open(f"{RAW_DIR}/phaseB_gates.json", "w", encoding="utf-8") as f:
        json.dump({"gateA": ok_a, "gateB": ok_b, "gateC": ok_c, "phaseB": rb}, f, ensure_ascii=False)
    print("DONE ->", RAW_DIR)


if __name__ == "__main__":
    main()
