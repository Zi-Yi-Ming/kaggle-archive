# -*- coding: utf-8 -*-
"""P75: pull live episode meta for last-2 submissions (opponent intel)."""
from __future__ import annotations

import json
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi

OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p75_episode_meta")
OUT.mkdir(parents=True, exist_ok=True)
SUBS = {
    "thomas": 56358711,
    "twin": 56346424,
}


def main() -> None:
    api = KaggleApi()
    api.authenticate()
    summary = {}
    for name, sub in SUBS.items():
        try:
            eps = [e.to_dict() for e in api.competition_list_episodes(submission_id=sub)]
        except Exception as e:
            print(f"FAIL list {name} {sub}: {e}")
            summary[name] = {"error": str(e)}
            continue
        completed = [e for e in eps if e.get("state") == "COMPLETED"]
        running = [e for e in eps if e.get("state") not in ("COMPLETED",)]
        opponents = {}
        rewards = []
        for e in completed[:80]:
            for a in e.get("agents") or []:
                if a.get("submissionId") == sub:
                    rewards.append(a.get("reward"))
                else:
                    t = a.get("teamName") or "?"
                    opponents[t] = opponents.get(t, 0) + 1
        top_opp = sorted(opponents.items(), key=lambda x: -x[1])[:15]
        summary[name] = {
            "submission_id": sub,
            "n_listed": len(eps),
            "n_completed": len(completed),
            "n_other": len(running),
            "sample_our_rewards": rewards[:20],
            "top_opponents": top_opp,
        }
        print(f"\n{name} sub={sub} completed={len(completed)} other={len(running)}")
        print("  top opponents:", top_opp[:10])
        print("  sample rewards:", rewards[:10])
        (OUT / f"{name}_episodes.json").write_text(
            json.dumps(summary[name], indent=2), encoding="utf-8"
        )
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("\nWROTE", OUT / "summary.json")


if __name__ == "__main__":
    main()
