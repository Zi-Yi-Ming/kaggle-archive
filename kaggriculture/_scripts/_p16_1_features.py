# -*- coding: utf-8 -*-
"""P16.1: log d7-d10 trajectory features for SKEL and SKEL+BR arms."""
from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402


def load_r2():
    spec = importlib.util.spec_from_file_location(
        "r2_p161_" + str(id(object())), str(ROOT / "_push_medal" / "main.py")
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def run_trace(label, seed, seat, skeleton, branch):
    import p13_1_melon
    import p13_3_water
    import p14_1_on
    import p14_2_on
    import p16_branch
    p13_1_melon.set_enabled(False)
    p13_3_water.set_enabled(skeleton)
    p14_1_on.set_enabled(skeleton)
    p14_2_on.set_enabled(False)
    p16_branch.set_skeleton(skeleton)
    p16_branch.set_branch(branch)
    from p11_planner import planner as pmod
    pmod._PLANNER = None
    own = pmod.agent
    opp = load_r2()
    agents = [None, None]
    agents[seat] = own
    agents[1 - seat] = opp

    snaps = {}  # day -> features

    def wrap(inner, is_own):
        def agent(obs, configuration=None):
            step = int(obs.get("step") or 0)
            day = step // 24
            hour = step % 24
            action = inner(obs, configuration)
            if not is_own:
                return action
            if 7 <= day <= 10 and hour == 0:
                farm = (obs.get("farms") or [])[int(obs.get("player") or 0)]
                private = obs.get("private") or {}
                shed = dict(private.get("shed") or {})
                seeds = dict(private.get("seeds") or {})
                tiles = farm.get("tiles") or []
                field_melon = field_wheat = field_straw = 0
                melon_ready = 0
                for row in tiles:
                    for t in row:
                        if isinstance(t, dict) and t.get("kind") == "PLANT":
                            c = t.get("crop")
                            if c == "MELON":
                                field_melon += 1
                                if int(t.get("yield_units") or 0) > 0:
                                    melon_ready += 1
                            elif c == "WHEAT":
                                field_wheat += 1
                            elif c == "STRAWBERRY":
                                field_straw += 1
                snaps[day] = {
                    "money": float(farm.get("money") or 0),
                    "hands": len(farm.get("hands") or []),
                    "field_melon": field_melon,
                    "melon_ready": melon_ready,
                    "shed_melon": int(shed.get("MELON") or 0),
                    "field_wheat": field_wheat,
                    "field_straw": field_straw,
                    "shed_total": sum(int(v or 0) for v in shed.values()),
                    "shed_milk": int(shed.get("MILK") or 0),
                    "shed_wool": int(shed.get("WOOL") or 0),
                    "seed_melon": int(seeds.get("MELON") or 0),
                    "n_land": len(farm.get("unlocked_quadrants") or []),
                }
            return action
        return agent

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([wrap(agents[0], seat == 0), wrap(agents[1], seat == 1)])
    f = env.steps[-1]
    my = float(f[seat]["observation"]["farms"][seat]["money"])
    rows = []
    for d, s in snaps.items():
        rec = {"label": label, "seed": seed, "seat": seat, "day": d, "final": my, **s}
        rows.append(rec)
    print(f"{label} s{seed} seat{seat}: final={my:.0f} "
          f"d10={snaps.get(10, {}).get('money')} m_f={snaps.get(10, {}).get('field_melon')} "
          f"m_s={snaps.get(10, {}).get('shed_melon')} ready={snaps.get(10, {}).get('melon_ready')}", flush=True)
    return rows, my


def main():
    all_rows = []
    finals = []
    for seat in (0, 1):
        for seed in (1, 2):
            for lab, sk, br in (("SKEL", True, False), ("BR", True, True)):
                rows, fin = run_trace(lab, seed, seat, sk, br)
                all_rows.extend(rows)
                finals.append({"label": lab, "seed": seed, "seat": seat, "final": fin})

    out = ROOT / "p16_1_trigger_features.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        w.writeheader()
        w.writerows(all_rows)
    out2 = ROOT / "p16_1_counterfactual.csv"
    with open(out2, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["seed", "seat", "skel_final", "br_final", "delta"])
        for seat in (0, 1):
            for seed in (1, 2):
                s = next(x for x in finals if x["label"]=="SKEL" and x["seed"]==seed and x["seat"]==seat)
                b = next(x for x in finals if x["label"]=="BR" and x["seed"]==seed and x["seat"]==seat)
                w.writerow([seed, seat, s["final"], b["final"], b["final"]-s["final"]])
    print("wrote", out.name, out2.name)


if __name__ == "__main__":
    main()
