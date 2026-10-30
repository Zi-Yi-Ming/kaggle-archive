# -*- coding: utf-8 -*-
"""Dump key Kaggle discussion threads for strategy intel."""
from __future__ import annotations

import re
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi

OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p50_discussions")
OUT.mkdir(parents=True, exist_ok=True)

TOPICS = {
    730708: "discord_official",
    739273: "replay_pipeline",
    741258: "rl_learning",
    740588: "copying_opponent",
    741003: "optimization_planning",
    740792: "rl_how",
    740969: "20k_to_start",
    731215: "daily_top_episodes",
}


def strip_html(s: str) -> str:
    s = re.sub(r"<br\s*/?>", "\n", s or "")
    s = re.sub(r"</p>", "\n\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
    return s


def main():
    api = KaggleApi()
    api.authenticate()
    for tid, name in TOPICS.items():
        try:
            mr = api.competition_list_topic_messages(competition="kaggriculture", topic_id=tid)
            msgs = mr.messages or []
        except Exception as e:
            print(f"FAIL {tid}: {e}")
            continue
        lines = [f"# Topic {tid} ({name}) n={len(msgs)}\n"]
        for m in msgs:
            author = getattr(m, "author_name", "?")
            raw = getattr(m, "raw_markdown", None) or strip_html(getattr(m, "content", ""))
            votes = getattr(m, "votes", 0)
            lines.append(f"\n---\n## {author} (votes={votes})\n\n{raw}\n")
            for r in getattr(m, "replies", None) or []:
                ra = getattr(r, "author_name", "?")
                rr = getattr(r, "raw_markdown", None) or strip_html(getattr(r, "content", ""))
                lines.append(f"\n### reply {ra}\n\n{rr}\n")
        p = OUT / f"{tid}_{name}.md"
        p.write_text("\n".join(lines), encoding="utf-8")
        print(f"wrote {p.name} msgs={len(msgs)} bytes={p.stat().st_size}")


if __name__ == "__main__":
    main()
