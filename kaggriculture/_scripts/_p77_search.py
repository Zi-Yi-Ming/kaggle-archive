# -*- coding: utf-8 -*-
"""P77: pull discussions + thomas recent episodes for loss forensics."""
from __future__ import annotations

import json
import re
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi

OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p77_search")
OUT.mkdir(parents=True, exist_ok=True)
THOMAS_SUB = 56358711


def strip_html(s: str) -> str:
    s = re.sub(r"<br\s*/?>", "\n", s or "")
    s = re.sub(r"</p>", "\n\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    for a, b in [("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"')]:
        s = s.replace(a, b)
    return s


def main() -> None:
    api = KaggleApi()
    api.authenticate()

    # 1) thomas episodes full dump
    eps = [e.to_dict() for e in api.competition_list_episodes(submission_id=THOMAS_SUB)]
    (OUT / "thomas_episodes.json").write_text(json.dumps(eps, indent=2), encoding="utf-8")
    comp = [e for e in eps if e.get("state") == "COMPLETED"]
    print(f"thomas episodes {len(eps)} completed {len(comp)}")

    losses = []
    for e in comp:
        our = opp = None
        opp_t = opp_sub = None
        for a in e.get("agents") or []:
            if a.get("submissionId") == THOMAS_SUB:
                our = a.get("reward")
            else:
                opp = a.get("reward")
                opp_t = a.get("teamName")
                opp_sub = a.get("submissionId")
        if our is not None and opp is not None and our < opp:
            losses.append(
                {
                    "episode_id": e.get("id"),
                    "create_time": e.get("createTime"),
                    "our": our,
                    "opp": opp,
                    "margin": our - opp,
                    "opp_team": opp_t,
                    "opp_sub": opp_sub,
                }
            )
    losses.sort(key=lambda x: x["margin"])
    (OUT / "thomas_losses.json").write_text(json.dumps(losses, indent=2), encoding="utf-8")
    print(f"losses {len(losses)}")
    for row in losses[:15]:
        print(
            f"  {row['create_time']} margin={row['margin']} "
            f"our={row['our']} opp={row['opp']} vs={row['opp_team']}"
        )

    # 2) try download a few loss replays
    rep_dir = OUT / "loss_replays"
    rep_dir.mkdir(exist_ok=True)
    for row in losses[:6]:
        eid = row["episode_id"]
        try:
            api.competition_episode_replay(eid, path=str(rep_dir), quiet=True)
            print(f"  replay ok {eid}")
        except Exception as ex:
            print(f"  replay FAIL {eid}: {ex}")

    # 3) discussions — list competition topics if API allows
    disc_dir = OUT / "discussions"
    disc_dir.mkdir(exist_ok=True)
    try:
        # newer CLI/API may expose competition_list_topics
        topics = []
        for attr in dir(api):
            if "topic" in attr.lower() or "forum" in attr.lower() or "discussion" in attr.lower():
                print("api attr:", attr)
        if hasattr(api, "competition_list_topics"):
            raw = api.competition_list_topics(competition="kaggriculture")
            items = raw if isinstance(raw, list) else getattr(raw, "topics", raw)
            (disc_dir / "topics_raw.json").write_text(
                json.dumps(items, indent=2, default=str)[:200000], encoding="utf-8"
            )
            print("topics dumped")
    except Exception as ex:
        print("discussion list fail", ex)

    # known high-signal topic ids from earlier research + likely new
    topic_ids = [
        736439,
        738325,
        736219,
        741743,
        741320,
        741730,
        741414,
        741596,
        741722,
        741653,
        742000,
        742100,
        742200,
        742500,
        743000,
    ]
    for tid in topic_ids:
        try:
            mr = api.competition_list_topic_messages(competition="kaggriculture", topic_id=tid)
            msgs = mr.messages or []
        except Exception as e:
            print(f"topic {tid} fail: {e}")
            continue
        if not msgs:
            print(f"topic {tid} empty")
            continue
        lines = [f"# Topic {tid} n={len(msgs)}\n"]
        for m in msgs:
            author = getattr(m, "author_name", "?")
            raw = getattr(m, "raw_markdown", None) or strip_html(getattr(m, "content", ""))
            lines.append(f"\n---\n## {author}\n\n{raw}\n")
        (disc_dir / f"topic_{tid}.md").write_text("\n".join(lines), encoding="utf-8")
        print(f"topic {tid} saved n={len(msgs)}")

    print("WROTE", OUT)


if __name__ == "__main__":
    main()
