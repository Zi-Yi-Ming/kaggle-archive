"""A6 forensic: V2-B seed 1 step-by-step diff (engine obs vs reconstructed).

Finds the FIRST_DIVERGENCE_STEP across money/shed/seeds/market, then dumps
the WHEAT-flow detail around it (unit actions, tiles, carried, shed).
"""
import importlib.util
import sys

sys.path.insert(0, "kaggriculture")
sys.path.insert(0, "_audit_tmp/route_transfer")
import _pm_pool as P
import executed_ledger as EL
from kaggle_environments import make

spec = importlib.util.spec_from_file_location("v2", "_audit_tmp/route_transfer/variants/v11e_multitape_router.py")
V2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V2)


def run(seed):
    opp = P.load_agent("closer_cleo")
    seat = 1 if seed % 2 == 1 else 0
    a, b = (V2.agent, opp) if seat == 0 else (opp, V2.agent)
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info["seed"] = seed
    env.run([a, b])
    return env.steps, seat


def diff_all(steps, seat):
    first = None
    for s in range(1, len(steps)):
        obs_p = steps[s - 1][seat].get("observation") or {}
        act_s = steps[s][seat].get("action") or {}
        obs_c = steps[s][seat].get("observation") or {}
        obs_o_p = steps[s - 1][1 - seat].get("observation") or {}
        obs_o_c = steps[s][1 - seat].get("observation") or {}
        EL._ACT_OTHER[seat] = steps[s][1 - seat].get("action") or {}
        led, ok, det, extra = EL.replay_step(
            obs_p, act_s, obs_c, seat, consume_step=s - 1,
            obs_cur_other=obs_o_c, obs_prev_other=obs_o_p, return_states=True)
        if not ok and first is None:
            first = (s, det)
            break
    return first


def dump_window(steps, seat, lo, hi):
    for s in range(lo, hi + 1):
        obs_p = steps[s - 1][seat].get("observation") or {}
        obs_c = steps[s][seat].get("observation") or {}
        act_s = steps[s][seat].get("action") or {}
        obs_o_p = steps[s - 1][1 - seat].get("observation") or {}
        obs_o_c = steps[s][1 - seat].get("observation") or {}
        EL._ACT_OTHER[seat] = steps[s][1 - seat].get("action") or {}
        led, ok, det, extra = EL.replay_step(
            obs_p, act_s, obs_c, seat, consume_step=s - 1,
            obs_cur_other=obs_o_c, obs_prev_other=obs_o_p, return_states=True)
        rec_shed = extra["states"][seat]["private"]["shed"]
        eng_shed = (obs_c.get("private") or {}).get("shed") or {}
        rec_money = extra["states"][seat]["farm"]["money"]
        eng_money = (obs_c.get("farms") or [{}])[seat].get("money")
        invs = (obs_c.get("private") or {}).get("inventories") or []
        carried_w = sum(int(inv.get("WHEAT", 0) or 0) for inv in invs)
        print(f"step {s}: ok={ok}")
        print(f"  shed[WHEAT] rec={rec_shed.get('WHEAT', 0)} eng={eng_shed.get('WHEAT', 0)} | money rec={rec_money:.0f} eng={eng_money:.0f} | carriedW(eng)={carried_w}")
        if det:
            print(f"  DETAIL: {det}")
        # unit actions (candidate seat)
        acts = [act_s.get("farmer", ["PASS"])] + list(act_s.get("hands") or [])
        wheat_acts = [u for u in acts if isinstance(u, (list, tuple)) and u and u[0] in
                      ("WATER", "HARVEST", "PLANT", "DROP", "PICKUP", "FEED", "FERTILIZE") and
                      (len(u) < 2 or u[1] in ("WHEAT", "CARROT", "STRAWBERRY", "MELON") or u[0] in ("DROP", "HARVEST", "PICKUP"))]
        # wheat tiles
        tiles = ((obs_p.get("farms") or [{}])[seat]).get("tiles") or []
        wts = []
        for y, row in enumerate(tiles):
            for x, t in enumerate(row):
                if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "WHEAT":
                    wts.append((x, y, t.get("age", "?"), t.get("yield_units", 0),
                                t.get("watered_today", False), t.get("fertilized_until_day", -1),
                                t.get("planted_day", "?")))
        print(f"  单位WHEAT动作: {wheat_acts[:8]}")
        print(f"  WHEAT格(obs前置 x,y,age,yield,watered,fertUntil,planted): {wts[:6]}")


if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    steps, seat = run(seed)
    print(f"V2-B seed {seed}: seat={seat} route={V2._LOCK.get(seat)}")
    first = diff_all(steps, seat)
    print(f"FIRST_DIVERGENCE_STEP: {first}")
    dump_window(steps, seat, max(1, first[0] - 4), first[0] + 2)
