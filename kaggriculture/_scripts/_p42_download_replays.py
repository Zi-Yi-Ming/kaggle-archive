# -*- coding: utf-8 -*-
"""P42: download R2 live replays (same agent, different opponents)."""
from __future__ import annotations

import json
import time
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi

OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p42_replays")
OUT.mkdir(parents=True, exist_ok=True)

# R2 path-twin (most recent last-2)
SUB = 56181169
N = 30


def main():
    api = KaggleApi()
    api.authenticate()
    eps = [e.to_dict() for e in api.competition_list_episodes(submission_id=SUB)]
    eps = [e for e in eps if e.get("state") == "COMPLETED"]
    eps.sort(key=lambda e: e.get("createTime") or "", reverse=True)
    print(f"listing {len(eps)} completed, will pull {N}", flush=True)

    meta_rows = []
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
            time.sleep(0.35)
        agents = e.get("agents") or []
        ours = next((a for a in agents if a.get("submissionId") == SUB), None)
        opp = next((a for a in agents if a.get("submissionId") != SUB), None)
        meta_rows.append({
            "episode_id": eid,
            "create_time": e.get("createTime"),
            "our_seat": (ours or {}).get("index", 0),
            "our_reward": (ours or {}).get("reward"),
            "opp_team": (opp or {}).get("teamName"),
            "opp_team_id": (opp or {}).get("teamId"),
            "opp_sub": (opp or {}).get("submissionId"),
            "opp_reward": (opp or {}).get("reward"),
            "path": str(path),
        })
        done += 1
        print(f"  [{done}] {eid} opp={ (opp or {}).get('teamName') } "
              f"our={(ours or {}).get('reward')} opp_r={(opp or {}).get('reward')}", flush=True)

    (OUT / "meta.json").write_text(json.dumps(meta_rows, indent=2), encoding="utf-8")
    print(f"done {done} -> {OUT}/meta.json", flush=True)


if __name__ == "__main__":
    main()
