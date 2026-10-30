# -*- coding: utf-8 -*-
"""Fetch newest high-signal discussion threads."""
from __future__ import annotations

import re
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi

OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p70_discussions")
OUT.mkdir(parents=True, exist_ok=True)

TOPICS = {
    741743: "silver_rl",
    741320: "rl_variance_tax",
    741730: "rl_selfplay",
    741414: "final_week_replay_analyzer",
    741596: "h2h_arena",
    741722: "generalization_overfit",
    741653: "ai_coding_agents",
}


def strip_html(s: str) -> str:
    s = re.sub(r"<br\s*/?>", "\n", s or "")
    s = re.sub(r"</p>", "\n\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    for a, b in [("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"')]:
        s = s.replace(a, b)
    return s


def main():
    api = KaggleApi()
    api.authenticate()
    for tid, name in TOPICS.items():
        try:
            mr = api.competition_list_topic_messages(competition="kaggriculture", topic_id=tid)
            msgs = mr.messages or []
        except Exception as e:
            print("FAIL", tid, e)
            continue
        lines = [f"# Topic {tid} ({name}) n={len(msgs)}\n"]
        for m in msgs:
            author = getattr(m, "author_name", "?")
            raw = getattr(m, "raw_markdown", None) or strip_html(getattr(m, "content", ""))
            lines.append(f"\n---\n## {author}\n\n{raw}\n")
            for r in getattr(m, "replies", None) or []:
                ra = getattr(r, "author_name", "?")
                rr = getattr(r, "raw_markdown", None) or strip_html(getattr(r, "content", ""))
                lines.append(f"\n### reply {ra}\n\n{rr}\n")
        p = OUT / f"{tid}_{name}.md"
        p.write_text("\n".join(lines), encoding="utf-8")
        print(f"wrote {p.name} msgs={len(msgs)} bytes={p.stat().st_size}")


if __name__ == "__main__":
    main()
