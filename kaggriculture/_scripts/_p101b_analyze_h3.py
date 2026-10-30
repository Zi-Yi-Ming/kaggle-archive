# -*- coding: utf-8 -*-
"""P101b: parse H3 replays — sell timing, losses, free-lunch patterns. Find gold team sub id."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p101_replays")
RESEARCH = Path(r"D:\桌面\Kaggle\kaggriculture\_research")


def load_meta():
    return json.loads((OUT / "h3_meta.json").read_text(encoding="utf-8"))


def peek_replay(path: Path):
    """Replay JSON is huge; stream-scan keys without full load when possible."""
    # try full load first if < 40MB
    raw = path.read_text(encoding="utf-8", errors="replace")
    return json.loads(raw)


def summarize_episode(path: Path, meta_row: dict):
    data = peek_replay(path)
    # discover structure
    if not isinstance(data, dict):
        return {"path": path.name, "type": type(data).__name__}
    keys = sorted(data.keys())
    out = {"file": path.name, "top_keys": keys[:30]}
    # common shapes: steps / frames / observations
    steps = data.get("steps") or data.get("frames") or data.get("timeline") or []
    out["n_steps"] = len(steps) if isinstance(steps, list) else None
    # agents
    agents = meta_row.get("agents") or data.get("agents") or []
    out["agents"] = [
        {k: a.get(k) for k in ("index", "teamName", "teamId", "submissionId", "reward") if k in a}
        for a in agents
        if isinstance(a, dict)
    ]
    # scan market sells by player if present
    sell_by = Counter()
    money_end = {}
    if isinstance(steps, list) and steps:
        first = steps[0]
        out["step0_keys"] = sorted(first.keys())[:40] if isinstance(first, dict) else None
        # try to find actions
        for st in steps:
            if not isinstance(st, dict):
                continue
            acts = st.get("actions") or st.get("action") or {}
            if isinstance(acts, dict):
                for p, act in acts.items():
                    if not isinstance(act, dict):
                        continue
                    for o in act.get("market") or []:
                        if isinstance(o, (list, tuple)) and o and o[0] == "SELL":
                            sell_by[(str(p), o[1] if len(o) > 1 else "?")] += 1
        out["sell_counts"] = {f"{k[0]}:{k[1]}": v for k, v in sell_by.most_common(30)}
    return out


def main():
    meta = load_meta()
    results = []
    # class win/loss by ZiYiMing reward
    w = l = 0
    for row in meta:
        agents = row.get("agents") or []
        us = next((a for a in agents if a.get("teamName") == "ZiYiMing"), None)
        them = next((a for a in agents if a.get("teamName") != "ZiYiMing"), None)
        if not us or not them:
            continue
        ur = us.get("reward")
        tr = them.get("reward")
        try:
            win = float(ur) > float(tr)
        except Exception:
            win = False
        w += int(win)
        l += int(not win)
        # find file
        eid = row.get("episode_id")
        path = OUT / "h3" / f"episode-{eid}-replay.json"
        if not path.exists():
            path = OUT / "h3" / f"{eid}.json"
        rec = {
            "episode_id": eid,
            "win": win,
            "our_reward": ur,
            "opp_reward": tr,
            "opp_team": them.get("teamName"),
            "opp_team_id": them.get("teamId"),
            "opp_sub": them.get("submissionId"),
            "our_sub": us.get("submissionId"),
            "file": path.name if path.exists() else None,
        }
        results.append(rec)
        print(f"{eid} vs {them.get('teamName')}: {'W' if win else 'L'} {ur}:{tr} opp_sub={them.get('submissionId')}", flush=True)

    # hunt gold team in any opp
    gold_hits = [r for r in results if r.get("opp_team") == "吃白饭的大肥鱼" or r.get("opp_team_id") == 16854176]
    print("gold hits in H3 games:", gold_hits, flush=True)

    # dump structure of one win and one loss
    struct = []
    for r in results[:3]:
        if r.get("file"):
            p = OUT / "h3" / r["file"]
            if p.exists():
                try:
                    struct.append(summarize_episode(p, {"agents": [{"teamName": "ZiYiMing"}, {"teamName": r["opp_team"]}]}))
                except Exception as e:
                    struct.append({"file": r["file"], "error": str(e)[:200]})

    summary = {
        "n": len(results),
        "wins": w,
        "losses": l,
        "win_rate": w / max(w + l, 1),
        "results": results,
        "gold_hits": gold_hits,
        "struct_sample": struct,
    }
    (RESEARCH / "p101_h3_live_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )
    print(f"\nH3 live: {w}W-{l}L ({summary['win_rate']:.0%})", flush=True)
    print("WROTE p101_h3_live_summary.json", flush=True)
    # print one struct
    if struct:
        print("STRUCT sample:", json.dumps(struct[0], ensure_ascii=False, default=str)[:2000], flush=True)


if __name__ == "__main__":
    main()
