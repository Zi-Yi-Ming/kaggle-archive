# -*- coding: utf-8 -*-
"""P61: download alperen_meta (56244291) public episodes + loss forensic."""
from __future__ import annotations

import csv
import json
import time
from collections import Counter, defaultdict
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
OUT = ROOT / "_external" / "p61_alperen_replays"
OUT.mkdir(parents=True, exist_ok=True)
SUB = 56244291
N = 40


def load_agent_key(action):
    return json.dumps(
        {"m": action.get("market"), "f": action.get("farmer"), "h": action.get("hands")},
        sort_keys=True, default=str,
    )


def classify_div(a, b):
    ma = json.dumps(a.get("market"), sort_keys=True, default=str)
    mb = json.dumps(b.get("market"), sort_keys=True, default=str)
    if ma != mb:
        if any(o and o[0] == "SELL" for o in (a.get("market") or []) + (b.get("market") or [])):
            return "SELL"
        return "MARKET_OTHER"
    return "WORKER"


def main():
    api = KaggleApi()
    api.authenticate()
    eps = [e.to_dict() for e in api.competition_list_episodes(submission_id=SUB)]
    eps = [e for e in eps if e.get("state") == "COMPLETED"]
    eps.sort(key=lambda e: e.get("createTime") or "", reverse=True)
    print(f"completed episodes={len(eps)}", flush=True)

    meta = []
    done = 0
    for e in eps:
        if done >= N:
            break
        eid = e["id"]
        path = OUT / f"episode-{eid}-replay.json"
        if not (path.exists() and path.stat().st_size > 1000):
            try:
                api.competition_episode_replay(eid, path=str(OUT), quiet=True)
            except Exception as exc:
                print(f"  fail {eid}: {exc}", flush=True)
                continue
            time.sleep(0.3)
        agents = e.get("agents") or []
        ours = next((a for a in agents if a.get("submissionId") == SUB), None)
        opp = next((a for a in agents if a.get("submissionId") != SUB), None)
        our_r = (ours or {}).get("reward")
        opp_r = (opp or {}).get("reward")
        if our_r is None or opp_r is None:
            continue
        res = "W" if our_r > opp_r + 1 else ("L" if opp_r > our_r + 1 else "D")
        meta.append({
            "episode_id": eid,
            "create_time": e.get("createTime"),
            "our_seat": (ours or {}).get("index", 0),
            "our_reward": our_r,
            "opp_team": (opp or {}).get("teamName"),
            "opp_team_id": (opp or {}).get("teamId"),
            "opp_reward": opp_r,
            "result": res,
            "margin": our_r - opp_r,
            "path": str(path),
        })
        done += 1
        print(f"  [{done}] {eid} {res} our={our_r:.0f} opp={opp_r:.0f} vs={(opp or {}).get('teamName')}", flush=True)

    (OUT / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print("\n=== W-D-L ===", flush=True)
    print(Counter(m["result"] for m in meta), flush=True)

    losses = [m for m in meta if m["result"] == "L"]
    narrow_w = [m for m in meta if m["result"] == "W" and m["margin"] < 5000]
    print(f"losses={len(losses)} narrow_wins(<5k)={len(narrow_w)}", flush=True)

    # who beats us
    print("\n=== losses by opponent ===", flush=True)
    by_opp = Counter(m["opp_team"] for m in losses)
    for o, n in by_opp.most_common():
        print(f"  {n}x {o}", flush=True)

    # day profile of losses: divergent steps by day vs opponent
    print("\n=== loss first_div / peak day ===", flush=True)
    loss_rows = []
    peak_days = Counter()
    for m in losses:
        path = Path(m["path"])
        if not path.exists():
            continue
        d = json.loads(path.read_text(encoding="utf-8"))
        steps = d.get("steps") or []
        seat = int(m.get("our_seat") or 0)
        oseat = 1 - seat
        first_div = None
        day_div = Counter()
        for i, step in enumerate(steps):
            if not isinstance(step, list) or len(step) <= max(seat, oseat):
                continue
            a = step[seat].get("action") or {}
            b = step[oseat].get("action") or {}
            if load_agent_key(a) != load_agent_key(b):
                day_div[i // 24] += 1
                if first_div is None and i > 0:
                    first_div = i
        peak = None
        if day_div:
            peak = max(day_div.items(), key=lambda x: x[1])
            peak_days[peak[0]] += 1
        loss_rows.append({
            "episode_id": m["episode_id"],
            "opp_team": m["opp_team"],
            "our_reward": m["our_reward"],
            "opp_reward": m["opp_reward"],
            "margin": m["margin"],
            "first_div": first_div if first_div is not None else -1,
            "first_div_day": (first_div // 24) if first_div is not None else -1,
            "peak_div_day": peak[0] if peak else -1,
            "peak_div_n": peak[1] if peak else 0,
            "day_div": json.dumps(dict(day_div)),
        })
        print(f"  {m['episode_id']} vs {m['opp_team'][:20]} "
              f"margin={m['margin']:.0f} first_d={loss_rows[-1]['first_div_day']} "
              f"peak_d={peak[0] if peak else -1}:{peak[1] if peak else 0}", flush=True)

    print("\nloss peak-day histogram", peak_days.most_common(8), flush=True)

    # d15 animal snapshot on losses if possible
    print("\n=== d15 eco on losses ===", flush=True)
    for row, m in list(zip(loss_rows, losses))[:8]:
        d = json.loads(Path(m["path"]).read_text(encoding="utf-8"))
        steps = d.get("steps") or []
        seat = int(m.get("our_seat") or 0)
        t = 15 * 24 + 12
        if t >= len(steps):
            continue
        obs = steps[t][seat].get("observation") or {}
        player = int(obs.get("player") or seat)
        farms = obs.get("farms") or []
        farm = farms[player] if player < len(farms) else {}
        tiles = farm.get("tiles") or []
        animals = plants = 0
        for r in tiles:
            for tile in r:
                if isinstance(tile, dict):
                    if tile.get("kind") == "PLANT":
                        plants += 1
                    if tile.get("animal"):
                        animals += 1
        money = float(farm.get("money") or 0)
        print(f"  d15 ep={m['episode_id']}: money={money:.0f} plants={plants} animals={animals}", flush=True)
        row["d15_money"] = money
        row["d15_plants"] = plants
        row["d15_animals"] = animals

    if loss_rows:
        with open(ROOT_OUT := ROOT / "p61_loss_forensic.csv", "w", newline="", encoding="utf-8") as f:
            wri = csv.DictWriter(f, fieldnames=list(loss_rows[0].keys()))
            wri.writeheader()
            wri.writerows(loss_rows)
        print("wrote p61_loss_forensic.csv", flush=True)
    else:
        print("no losses in sample", flush=True)

    print(f"wrote meta.json n={len(meta)}", flush=True)


if __name__ == "__main__":
    main()
