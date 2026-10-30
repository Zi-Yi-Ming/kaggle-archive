# -*- coding: utf-8 -*-
"""P101c: pull gold team episodes and parse both gold + H3 replay structure."""
from __future__ import annotations

import json
import time
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi

OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p101_replays")
RESEARCH = Path(r"D:\桌面\Kaggle\kaggriculture\_research")
GOLD_SUB = 56450063
GOLD_SUB2 = 56449978


def pull_sub(api, sid, tag, limit=20):
    dest = OUT / tag
    dest.mkdir(parents=True, exist_ok=True)
    eps = [e.to_dict() for e in api.competition_list_episodes(submission_id=sid)]
    eps = [e for e in eps if (e.get("state") or "").upper() == "COMPLETED"]
    eps.sort(key=lambda e: e.get("createTime") or "", reverse=True)
    print(f"[{tag}] {sid} completed={len(eps)}", flush=True)
    meta = []
    for i, e in enumerate(eps[:limit]):
        eid = e.get("id")
        path = dest / f"episode-{eid}-replay.json"
        if not (path.exists() and path.stat().st_size > 1000):
            try:
                api.competition_episode_replay(eid, path=str(dest), quiet=True)
            except Exception as exc:
                print("  fail", eid, exc, flush=True)
                time.sleep(0.4)
                continue
            time.sleep(0.3)
        agents = e.get("agents") or []
        meta.append({"episode_id": eid, "createTime": e.get("createTime"), "agents": agents})
        names = ",".join(str(a.get("teamName")) for a in agents)
        rewards = ",".join(str(a.get("reward")) for a in agents)
        print(f"  [{i+1}] {eid} {names} r={rewards}", flush=True)
    (OUT / f"{tag}_meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return meta


def parse_replay(path: Path):
    data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    steps = data.get("steps") or []
    out = {
        "file": path.name,
        "n_steps": len(steps),
        "rewards": data.get("rewards"),
        "step_type0": type(steps[0]).__name__ if steps else None,
    }
    if not steps:
        return out
    s0 = steps[0]
    if isinstance(s0, list):
        out["n_agents_in_step"] = len(s0)
        out["agent0_type"] = type(s0[0]).__name__ if s0 else None
        if s0 and isinstance(s0[0], dict):
            out["agent0_keys"] = sorted(s0[0].keys())
            for k, v in s0[0].items():
                if isinstance(v, dict):
                    out[f"a0_{k}_keys"] = sorted(v.keys())[:25]
                elif isinstance(v, list):
                    out[f"a0_{k}_len"] = len(v)
        # sample action at a mid step
        for idx in (1, 200, 600, 700):
            if idx >= len(steps):
                continue
            st = steps[idx]
            if isinstance(st, list) and st and isinstance(st[0], dict):
                act = st[0].get("action") or st[0].get("actions")
                obs = st[0].get("observation") or st[0].get("obs")
                out[f"s{idx}_action_keys"] = sorted(act.keys()) if isinstance(act, dict) else type(act).__name__
                if isinstance(act, dict) and act.get("market"):
                    out[f"s{idx}_market"] = act["market"]
                if isinstance(obs, dict):
                    out[f"s{idx}_obs_keys"] = sorted(obs.keys())[:20]
    return out


def main():
    api = KaggleApi()
    api.authenticate()
    pull_sub(api, GOLD_SUB, "gold", limit=12)
    # structure of one gold + one h3
    gold_dir = OUT / "gold"
    h3_dir = OUT / "h3"
    sample = {}
    gfiles = list(gold_dir.glob("episode-*-replay.json"))
    hfiles = list(h3_dir.glob("episode-*-replay.json"))
    if gfiles:
        sample["gold"] = parse_replay(gfiles[0])
    if hfiles:
        sample["h3"] = parse_replay(hfiles[0])
    (RESEARCH / "p101_replay_structure.json").write_text(
        json.dumps(sample, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )
    print(json.dumps(sample, indent=2, ensure_ascii=False, default=str)[:4000], flush=True)


if __name__ == "__main__":
    main()
