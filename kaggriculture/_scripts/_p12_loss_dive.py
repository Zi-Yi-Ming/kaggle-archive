# -*- coding: utf-8 -*-
"""Deep dive: inventory vs shed, end-of-day deposit, one P11 loss."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

LOG = ROOT / "_p12_loss_dive.txt"


def load_r2():
    spec = importlib.util.spec_from_file_location("r2_dive", str(ROOT / "_push_medal" / "main.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def main():
    from p11_planner import planner as pmod
    pmod._PLANNER = None
    fh = LOG.open("w", encoding="utf-8")
    stats = {"drop": 0, "place": 0, "pickup": 0, "eod_with_cargo": 0, "eod_deposit": 0,
             "cargo_lost_days": [], "harvest_to_inv": 0}

    def wrap(inner, tag):
        def agent(obs, configuration=None):
            step = int(obs.get("step") or 0)
            hour = step % 24
            day = step // 24
            action = inner(obs, configuration)
            player = int(obs.get("player") or 0)
            if player != 0 and tag == "P11":
                return action
            # only log P11 seat if P11 is player 0
            farm = (obs.get("farms") or [])[player]
            private = obs.get("private") or {}
            invs = list(private.get("inventories") or [])
            shed = dict(private.get("shed") or {})
            inv_sum = {}
            for inv in invs:
                for k, v in (inv or {}).items():
                    if int(v or 0):
                        inv_sum[k] = inv_sum.get(k, 0) + int(v or 0)
            cmds = [action.get("farmer") or ["PASS"]] + list(action.get("hands") or [])
            op0 = cmds[0][0] if cmds and cmds[0] else "PASS"
            n_cargo = sum(int(v or 0) for v in inv_sum.values())
            n_shed = sum(int(v or 0) for v in shed.values())

            if op0 == "HARVEST" or any(c and c[0] == "HARVEST" for c in cmds):
                stats["harvest_to_inv"] += 1
            if any(c and c[0] == "DROP" for c in cmds):
                stats["drop"] += 1
            if any(c and c[0] == "PLACE" for c in cmds):
                stats["place"] += 1
            if any(c and c and c[0] == "PICKUP" for c in cmds):
                stats["pickup"] += 1

            # last hour of day
            if hour == 23:
                if n_cargo > 0:
                    stats["eod_with_cargo"] += 1
                    deposited = any(c and c[0] in ("DROP", "PLACE") for c in cmds)
                    if deposited:
                        stats["eod_deposit"] += 1
                    else:
                        stats["cargo_lost_days"].append((day, dict(inv_sum)))

            interesting = (
                (8 <= day <= 16 and hour in (0, 6, 12, 18, 22, 23))
                or (n_cargo > 0 and hour >= 20)
                or (day in (10, 15) and hour == 0)
            )
            if interesting and tag == "P11":
                fh.write(
                    f"d{day:02d}h{hour:02d} s{step:3d} ${float(farm.get('money') or 0):.0f} "
                    f"hands={len(farm.get('hands') or [])} shed={n_shed} inv={n_cargo} "
                    f"shed={ {k:v for k,v in shed.items() if v} } "
                    f"inv={inv_sum} "
                    f"cmd0={op0} cmds={[c[0] if c else None for c in cmds[:6]]}\n"
                )
                fh.flush()
            return action
        return agent

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = 1
    # P11 seat 0 vs R2
    pmod._PLANNER = None
    env.run([wrap(pmod.agent, "P11"), wrap(load_r2(), "R2")])
    f = env.steps[-1]
    my = float(f[0]["observation"]["farms"][0]["money"])
    op = float(f[0]["observation"]["farms"][1]["money"])
    fh.write(f"\nFINAL P11={my:.0f} R2={op:.0f}\n")
    fh.write(f"STATS {stats}\n")
    fh.close()
    print(f"P11={my:.0f} R2={op:.0f}")
    print(f"STATS harvest_turns={stats['harvest_to_inv']} pickup={stats['pickup']} "
          f"drop={stats['drop']} place={stats['place']}")
    print(f"EOD with cargo: {stats['eod_with_cargo']}, deposited: {stats['eod_deposit']}, "
          f"lost_days={len(stats['cargo_lost_days'])}")
    print("lost examples:", stats["cargo_lost_days"][:12])
    print("wrote", LOG)


if __name__ == "__main__":
    main()
