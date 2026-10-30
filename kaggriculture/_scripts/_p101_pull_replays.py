# -*- coding: utf-8 -*-
"""P101: pull live episodes for gold team 吃白饭的大肥鱼 and our H3 losses."""
from __future__ import annotations

import json
import time
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
OUT = PROJ / "_external" / "p101_replays"
OUT.mkdir(parents=True, exist_ok=True)

OUR_SUB = 56453212  # H3
GOLD_TEAM_ID = 16854176
GOLD_TEAM_NAME = "吃白饭的大肥鱼"


def dump_eps(api, eps, tag: str, limit=25):
    eps = sorted(eps, key=lambda e: e.get("createTime") or "", reverse=True)
    print(f"[{tag}] completed episodes listed: {len(eps)}", flush=True)
    meta = []
    n = 0
    for e in eps:
        if n >= limit:
            break
        eid = e.get("id") or e.get("episodeId")
        if not eid:
            continue
        dest = OUT / tag
        dest.mkdir(parents=True, exist_ok=True)
        path = dest / f"{eid}.json"
        if not (path.exists() and path.stat().st_size > 500):
            try:
                api.competition_episode_replay(eid, path=str(dest), quiet=True)
                # file may be named episode-<id>-replay.json
            except Exception as exc:
                print(f"  dl fail {eid}: {exc}", flush=True)
                time.sleep(0.4)
                continue
            time.sleep(0.3)
        agents = e.get("agents") or []
        meta.append({
            "episode_id": eid,
            "createTime": e.get("createTime"),
            "state": e.get("state"),
            "agents": agents,
        })
        n += 1
        names = ",".join(str(a.get("teamName")) for a in agents)
        rewards = ",".join(str(a.get("reward")) for a in agents)
        print(f"  [{n}] {eid} agents={names} r={rewards}", flush=True)
    (OUT / f"{tag}_meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return meta


def main():
    api = KaggleApi()
    api.authenticate()

    # 1) our H3 episodes (see who we lose to)
    try:
        eps = [e.to_dict() for e in api.competition_list_episodes(submission_id=OUR_SUB)]
        print("our H3 episodes raw", len(eps), flush=True)
        dump_eps(api, [e for e in eps if (e.get("state") or "").upper() == "COMPLETED"], "h3", limit=20)
    except Exception as e:
        print("list our fail", e, flush=True)

    # 2) gold team: try various list endpoints
    for kwargs, tag in (
        ({"team_id": GOLD_TEAM_ID}, "gold_teamid"),
        ({"team_name": GOLD_TEAM_NAME}, "gold_name"),
    ):
        try:
            fn = getattr(api, "competition_list_episodes", None)
            eps = [e.to_dict() for e in fn(**kwargs)]
            print(f"{tag} raw", len(eps), flush=True)
            dump_eps(api, [e for e in eps if (e.get("state") or "").upper() == "COMPLETED"], tag, limit=15)
        except TypeError as e:
            print(f"{tag} bad kwargs", e, flush=True)
        except Exception as e:
            print(f"{tag} fail", e, flush=True)

    # 3) if we got gold meta from any source, also try submission ids listed in agents
    for meta_name in ("gold_teamid_meta.json", "gold_name_meta.json", "h3_meta.json"):
        p = OUT / meta_name
        if not p.exists():
            continue
        rows = json.loads(p.read_text(encoding="utf-8"))
        for row in rows[:30]:
            for a in row.get("agents") or []:
                if a.get("teamId") == GOLD_TEAM_ID and a.get("submissionId"):
                    sid = a["submissionId"]
                    try:
                        eps = [e.to_dict() for e in api.competition_list_episodes(submission_id=sid)]
                        print("gold sub", sid, "eps", len(eps), flush=True)
                        dump_eps(api, [e for e in eps if (e.get("state") or "").upper() == "COMPLETED"], f"gold_sub_{sid}", limit=15)
                    except Exception as e:
                        print("gold sub fail", sid, e, flush=True)
                    return  # one is enough

    print("done", flush=True)


if __name__ == "__main__":
    main()
