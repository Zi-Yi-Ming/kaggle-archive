# -*- coding: utf-8 -*-
"""P83: reverse-engineer ladder opponents from thomas loss/episode replays.

For each opponent submission id in thomas_episodes / losses:
- production fingerprint: hires, animals, land, crop tiles by day
- market fingerprint: sell volume by product/day, buy pattern, first sell step
- compare vs thomas template
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p77_search")
REPLAYS = ROOT / "loss_replays"
EPS = json.loads((ROOT / "thomas_episodes.json").read_text(encoding="utf-8"))
LOSSES = json.loads((ROOT / "thomas_losses.json").read_text(encoding="utf-8"))
OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_research\p83_opponent_fingerprint.json")
OUR_SUB = 56358711
OUR_TEAM = "ZiYiMing"

# extra: try fetch more episodes via existing files only (offline)


def fingerprint_replay(path: Path, our_team: str = OUR_TEAM) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    info = data.get("info") or {}
    names = info.get("TeamNames") or [a.get("Name") for a in (info.get("Agents") or [])]
    rewards = data.get("rewards") or [None, None]
    steps = data.get("steps") or []
    seed = info.get("seed")

    if our_team in names:
        our = names.index(our_team)
    else:
        our = 0
    opp = 1 - our

    def agent_fp(seat: int) -> dict:
        money = []
        sell = Counter()
        buy = Counter()
        sell_by_day = defaultdict(Counter)
        first_sell = None
        last_hire_day = None
        hires_total = 0
        animals_bought = Counter()
        land_bought = 0
        seeds_bought = Counter()
        # track farm private for crops at day ends
        day_end_tiles = {}
        day_end_animals = {}
        for si, frame in enumerate(steps):
            if seat >= len(frame):
                continue
            st = frame[seat]
            obs = st.get("observation") or {}
            farms = obs.get("farms") or []
            farm = farms[seat] if seat < len(farms) else {}
            priv = obs.get("private") or {}
            # inventories structure varies
            invs = priv.get("inventories") or []
            shed = priv.get("shed") or {}
            step = int(obs.get("step", si))
            day = step // 24
            hour = step % 24
            if isinstance(farm, dict) and "money" in farm:
                money.append(float(farm["money"]))
            act = st.get("action") or {}
            for o in act.get("market") or []:
                if not o:
                    continue
                op = o[0]
                if op == "SELL" and len(o) >= 3:
                    item, q = o[1], int(o[2] or 0)
                    sell[item] += q
                    sell_by_day[day][item] += q
                    if first_sell is None:
                        first_sell = step
                elif op == "HIRE":
                    hires_total += 1
                    last_hire_day = day
                elif op == "BUY_ANIMAL" and len(o) >= 3:
                    animals_bought[o[1]] += int(o[2] or 1)
                elif op == "BUY_LAND":
                    land_bought += 1
                elif op == "BUY_SEED" and len(o) >= 3:
                    seeds_bought[o[1]] += int(o[2] or 0)
                elif op == "BUY_PRODUCT" and len(o) >= 3:
                    buy[o[1]] += int(o[2] or 0)
            if hour == 23 and isinstance(farm, dict):
                tiles = farm.get("tiles") or []
                crops = Counter()
                structs = Counter()
                for row in tiles:
                    for t in row:
                        if t is None or t == "LOCKED":
                            continue
                        s = str(t)
                        if s in ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"):
                            crops[s] += 1
                        elif s in ("COOP", "PASTURE", "WEED"):
                            structs[s] += 1
                day_end_tiles[day] = dict(crops)
                # animals in inventories / shed
                animals = {}
                if isinstance(shed, dict):
                    for a in ("GOOSE", "COW", "SHEEP"):
                        if shed.get(a):
                            animals[a] = int(shed[a])
                # also from farm hands inventory if present
                day_end_animals[day] = animals
                # unlocked quadrants
                uq = farm.get("unlocked_quadrants")
                if uq:
                    day_end_tiles[day]["_quads"] = len(uq)
                day_end_tiles[day]["_hands"] = len(farm.get("hands") or [])
        return {
            "final_money": money[-1] if money else None,
            "first_sell_step": first_sell,
            "hires_total": hires_total,
            "last_hire_day": last_hire_day,
            "land_bought": land_bought,
            "animals_bought": dict(animals_bought),
            "seeds_bought": dict(seeds_bought),
            "sell_total": dict(sell),
            "buy_product_total": dict(buy),
            "sell_day5": dict(sell_by_day.get(5, {})),
            "sell_day10": dict(sell_by_day.get(10, {})),
            "sell_day20": dict(sell_by_day.get(20, {})),
            "sell_day29": dict(sell_by_day.get(29, {})),
            "day5_tiles": day_end_tiles.get(5),
            "day10_tiles": day_end_tiles.get(10),
            "day15_tiles": day_end_tiles.get(15),
            "day20_tiles": day_end_tiles.get(20),
            "day29_tiles": day_end_tiles.get(29),
            "day10_animals": day_end_animals.get(10),
            "day20_animals": day_end_animals.get(20),
        }

    our_fp = agent_fp(our)
    opp_fp = agent_fp(opp)
    # similarity score on sell totals
    items = set(our_fp["sell_total"]) | set(opp_fp["sell_total"])
    if items:
        nums = [min(our_fp["sell_total"].get(i, 0), opp_fp["sell_total"].get(i, 0)) for i in items]
        dens = [max(our_fp["sell_total"].get(i, 0), opp_fp["sell_total"].get(i, 0)) or 1 for i in items]
        sell_jaccard = sum(nums) / sum(dens)
    else:
        sell_jaccard = 1.0
    hire_delta = abs(our_fp["hires_total"] - opp_fp["hires_total"])
    land_delta = abs(our_fp["land_bought"] - opp_fp["land_bought"])
    animal_delta = abs(
        sum(our_fp["animals_bought"].values()) - sum(opp_fp["animals_bought"].values())
    )
    return {
        "file": path.name,
        "seed": seed,
        "names": names,
        "our_seat": our,
        "rewards": rewards,
        "our_final": rewards[our] if rewards and len(rewards) > our else None,
        "opp_final": rewards[opp] if rewards and len(rewards) > opp else None,
        "margin": (rewards[our] - rewards[opp]) if rewards and len(rewards) > max(our, opp) else None,
        "sell_jaccard": round(sell_jaccard, 4),
        "hire_delta": hire_delta,
        "land_delta": land_delta,
        "animal_delta": animal_delta,
        "family": (
            "mirror_tape" if sell_jaccard > 0.9 and hire_delta <= 2 and land_delta <= 1
            else "near_family" if sell_jaccard > 0.7
            else "heterogeneous"
        ),
        "our_fp": our_fp,
        "opp_fp": opp_fp,
    }


def cluster_from_episodes():
    """Summarize all thomas public episodes by opponent team."""
    by_opp = defaultdict(list)
    for e in EPS:
        agents = e.get("agents") or []
        us = next((a for a in agents if a.get("submissionId") == OUR_SUB), None)
        opp = next((a for a in agents if a.get("submissionId") != OUR_SUB), None)
        if not us or not opp:
            continue
        margin = us["reward"] - opp["reward"]
        by_opp[opp.get("teamName")].append(
            {
                "episode_id": e.get("id"),
                "opp_sub": opp.get("submissionId"),
                "our": us["reward"],
                "opp": opp["reward"],
                "margin": margin,
                "win": margin > 0,
            }
        )
    summary = []
    for team, games in by_opp.items():
        wins = sum(1 for g in games if g["win"])
        summary.append(
            {
                "team": team,
                "opp_sub": games[0].get("opp_sub"),
                "n": len(games),
                "wins": wins,
                "losses": len(games) - wins,
                "mean_margin": round(sum(g["margin"] for g in games) / len(games), 1),
                "games": games,
            }
        )
    summary.sort(key=lambda x: (x["wins"], x["mean_margin"]))
    return summary


def main():
    reports = []
    for loss in LOSSES:
        eid = loss["episode_id"]
        files = list(REPLAYS.glob(f"*{eid}*"))
        if not files:
            reports.append({"episode_id": eid, "error": "missing_replay", "meta": loss})
            continue
        print("FP", eid, loss.get("opp_team"), flush=True)
        try:
            fp = fingerprint_replay(files[0])
            fp["meta"] = loss
            reports.append(fp)
            print(
                f"  family={fp['family']} sellJ={fp['sell_jaccard']} "
                f"hireΔ={fp['hire_delta']} landΔ={fp['land_delta']} aniΔ={fp['animal_delta']}",
                flush=True,
            )
            print(f"  our sell {fp['our_fp']['sell_total']}", flush=True)
            print(f"  opp sell {fp['opp_fp']['sell_total']}", flush=True)
            print(f"  our d10 tiles {fp['our_fp']['day10_tiles']} animals {fp['our_fp']['day10_animals']}", flush=True)
            print(f"  opp d10 tiles {fp['opp_fp']['day10_tiles']} animals {fp['opp_fp']['day10_animals']}", flush=True)
            print(f"  our hires {fp['our_fp']['hires_total']} last_hire_d {fp['our_fp']['last_hire_day']}", flush=True)
            print(f"  opp hires {fp['opp_fp']['hires_total']} last_hire_d {fp['opp_fp']['last_hire_day']}", flush=True)
        except Exception as e:
            reports.append({"episode_id": eid, "error": str(e)[:300], "meta": loss})
            print("  FAIL", e, flush=True)

    opp_sum = cluster_from_episodes()
    OUT.write_text(
        json.dumps({"loss_fingerprints": reports, "episode_opponent_summary": opp_sum}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print("\n==== episode opponents (worst first) ====")
    for s in opp_sum[:15]:
        print(f"{s['team'][:28]:28s} sub={s['opp_sub']} {s['wins']}/{s['n']} m={s['mean_margin']}")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
