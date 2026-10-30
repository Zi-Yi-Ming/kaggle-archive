"""EXP-5 Phase-0 — Standing-on-work observer (RESEARCH ONLY).

Runs RAW v11E (no treatment) vs closer_cleo, fixed-RNG seeds 1-120; detects
"true standing-on-work misses" per the E1 definition:

  Condition 1: unit positioned on a task tile at step-s start
  Condition 2: a valid executable immediate task exists there (engine 1.32.7)
  Condition 3: v11E's issued action at step s is a MOVE (leaves the task)

OBS SEMANTICS (probe-verified in EXP-4): observation at step s reflects the
POST-action state of step s. Therefore the PRE-action state for step s is
obs(s-1); execution/validity signals must use state(s) - state(s-1).

Standing-task set (engine-valid, verifiable from obs):
  WATER   : tile kind PLANT, not watered_today, age in yield window
  PLANT   : tile is None (empty), a seed is held (private.seeds)
  HARVEST : tile yield_units > 0   (note: v11E scheduler already covers this)
FERTILIZE excluded (requires carried inventory, not observable in obs).

Per A-candidate, a one-step lookahead (step s+1) confirms the task is still
valid in the current action resolution (guard against s+1 invalidation).
"""
import importlib.util
import json
import multiprocessing as mp
import sys

sys.path.insert(0, "kaggriculture")
import _pm_pool as P
from kaggle_environments import make

CROPS = {  # engine 1.32.7
    "WHEAT": {"ongoing": False, "first": 2, "maxday": 4},
    "CARROT": {"ongoing": False, "first": 2, "maxday": 3},
    "TOMATO": {"ongoing": True, "first": 8, "maxday": 8, "interval": 1},
    "STRAWBERRY": {"ongoing": True, "first": 10, "maxday": 10, "interval": 2},
    "MELON": {"ongoing": False, "first": 10, "maxday": 12},
}
_MOVES = {"NORTH": (0, -1), "SOUTH": (0, 1), "WEST": (-1, 0), "EAST": (1, 0)}


def load_v11e():
    spec = importlib.util.spec_from_file_location("v11e_prod", "kaggriculture/main.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent


def in_window(crop, age):
    cd = CROPS[crop]
    if cd["ongoing"]:
        dsf = age - cd["first"]
        return dsf >= 0 and dsf % cd["interval"] == 0
    ws = (cd["maxday"] + 1) // 2
    return ws <= age <= cd["maxday"]


def standing_tasks(tile, seeds):
    """Return list of engine-valid standing task names at a tile (pre-action state)."""
    out = []
    if isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop"):
        crop = tile["crop"]
        age = int(tile.get("age", 0) or 0)
        if not tile.get("watered_today") and in_window(crop, age):
            out.append("WATER")
        if int(tile.get("yield_units", 0) or 0) > 0:
            out.append("HARVEST")
    elif tile is None and any(int(v or 0) > 0 for v in seeds.values()):
        out.append("PLANT")
    return out


def play_one(seed, seat_e):
    agent = load_v11e()
    opp = P.load_agent("closer_cleo")
    a, b = (agent, opp) if seat_e == 0 else (opp, agent)
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info["seed"] = seed
    env.run([a, b])
    steps = env.steps
    fin = steps[-1]
    e_idx = 0 if seat_e == 0 else 1

    opps = []       # A-candidates: {seed, day, step, unit, pos, task, dist, confirmed}
    invalid = []    # B-candidates: standing but task invalid / not productive
    idle = []       # C-candidates: standing with no useful task + issued PASS
    n_units_seen = 0

    for s in range(1, len(steps)):
        obs_prev = steps[s - 1][e_idx].get("observation") or {}
        act = steps[s][e_idx].get("action") or {}
        obs_cur = steps[s][e_idx].get("observation") or {}
        farm_p = (obs_prev.get("farms") or [{}])[0]
        farm_c = (obs_cur.get("farms") or [{}])[0]
        tiles_p = farm_p.get("tiles") or []
        tiles_c = farm_c.get("tiles") or []
        seeds_p = dict((obs_prev.get("private") or {}).get("seeds", {}) or {})
        day = int(obs_prev.get("day", 0) or 0)
        step = int(obs_prev.get("step", 0) or 0)

        fp = list(farm_p.get("farmer", [0, 0]))
        hs = list(farm_p.get("hands") or [])
        up = [fp] + [list(h) for h in hs]
        fc = list(farm_c.get("farmer", [0, 0]))
        hc = list(farm_c.get("hands") or [])
        uc = [fc] + [list(h) for h in hc]
        ua = [act.get("farmer", ["PASS"])] + list(act.get("hands") or [])
        n_units_seen = max(n_units_seen, len(up))

        for u in range(min(len(up), len(ua))):
            pos = up[u]
            fx, fy = int(pos[0]), int(pos[1])
            tile = tiles_p[fy][fx] if 0 <= fy < len(tiles_p) and 0 <= fx < len(tiles_p[fy]) else None
            tasks = standing_tasks(tile, seeds_p)
            op = ua[u][0] if isinstance(ua[u], (list, tuple)) and ua[u] else "PASS"

            if op in _MOVES or (op == "MOVE" and len(ua[u]) >= 3):
                # Condition 3: v11E moves away
                if u < len(uc):
                    npos = uc[u]
                    dist = abs(int(npos[0]) - fx) + abs(int(npos[1]) - fy)
                else:
                    npos, dist = pos, 0
                if tasks:
                    # lookahead (step s+1): task still valid?
                    ok_next = False
                    if s + 1 < len(steps):
                        obs_n = steps[s + 1][e_idx].get("observation") or {}
                        fn = (obs_n.get("farms") or [{}])[0]
                        tn = (fn.get("tiles") or [])
                        tt = tn[fy][fx] if 0 <= fy < len(tn) and 0 <= fx < len(tn[fy]) else None
                        ok_next = len(standing_tasks(tt, seeds_p)) > 0
                    else:
                        ok_next = True
                    if ok_next:
                        opps.append({"seed": seed, "day": day, "step": step, "unit": u,
                                     "pos": [fx, fy], "task": tasks[0], "all_tasks": tasks,
                                     "dist": dist, "confirmed": 1})
                    else:
                        invalid.append({"seed": seed, "day": day, "step": step, "unit": u,
                                        "pos": [fx, fy], "task": tasks[0], "why": "expired_next_step"})
                else:
                    idle.append({"seed": seed, "day": day, "step": step, "unit": u, "pos": [fx, fy]})
            elif tasks and op not in ("WATER", "PLANT", "HARVEST"):
                invalid.append({"seed": seed, "day": day, "step": step, "unit": u,
                                "pos": [fx, fy], "task": tasks[0], "why": "issued_non_task"})
            # if issued op IS the standing task (WATER/PLANT/HARVEST) -> v11E did it -> not a miss

    return {"seed": seed, "seat": seat_e,
            "bank_e": fin[e_idx]["observation"]["farms"][e_idx]["money"],
            "bank_o": fin[1 - e_idx]["observation"]["farms"][1 - e_idx]["money"],
            "win": int(fin[e_idx]["reward"] > fin[1 - e_idx]["reward"]),
            "opps": opps, "invalid": invalid, "idle": idle, "units_max": n_units_seen}


def run_one(args):
    return play_one(args[0], args[1])


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=120)
    ap.add_argument("--seed0", type=int, default=1)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--out", default="_audit_tmp/standing_obs.jsonl")
    a = ap.parse_args()
    jobs = [(s, 0 if s % 2 == 0 else 1) for s in range(a.seed0, a.seed0 + a.n)]
    recs = []
    with mp.Pool(a.workers) as pool:
        for i, r in enumerate(pool.imap_unordered(run_one, jobs)):
            recs.append(r)
            if (i + 1) % 10 == 0:
                print(f"[st] {i + 1}/{len(jobs)} 局")
    recs.sort(key=lambda r: r["seed"])
    with open(a.out, "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    print(f"DONE {len(recs)} 局 -> {a.out}")


if __name__ == "__main__":
    main()
