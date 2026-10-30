# -*- coding: utf-8 -*-
"""Tidy Kaggriculture workspace + read P73 results + write INDEX."""
from __future__ import annotations

import csv
import shutil
from pathlib import Path

KAGGLE = Path(r"D:\桌面\Kaggle")


def find_project():
    for p in KAGGLE.iterdir():
        if p.is_dir() and (p / "reference_agents" / "fallow_finn.py").exists():
            return p
    return None


def main():
    proj = find_project()
    if not proj:
        print("NO_PROJECT")
        return
    print("PROJECT", proj)

    # 1) target folders
    keep_roots = {
        "_production", "_research", "_scripts", "_external",
        "reference_agents", "_push_alperen", "_push_medal",
        "elite_corpus", "benchmark", "experiments",
    }
    for name in ("_production", "_research", "_scripts"):
        (proj / name).mkdir(exist_ok=True)

    # 2) read p73
    p73 = proj / "p73_top_tape_eval.csv"
    print("\n=== P73 RESULTS ===")
    if p73.exists():
        rows = list(csv.DictReader(p73.open(encoding="utf-8")))
        rows.sort(key=lambda r: -float(r.get("finn_mean3") or 0))
        for r in rows[:20]:
            print(f"  {r.get('team','')[:22]:22s} live={r.get('live_reward')} "
                  f"finn={float(r.get('finn_mean3') or 0):.0f} "
                  f"alpWL={r.get('vs_alp_WL','-')}")
        # move to research
        shutil.move(str(p73), str(proj / "_research" / "p73_top_tape_eval.csv"))
        print("moved p73 -> _research/")
    else:
        print(" p73 csv not at", p73)
        hits = list(proj.rglob("p73_top_tape_eval.csv"))
        print(" rglob hits", hits)

    # 3) move research csvs / md
    research_globs = [
        "RESEARCH_*.md", "p4*.csv", "p5*.csv", "p6*.csv", "p7*.csv",
        "p3*.csv", "RESUME_*.md", "CANONICAL_PATH.txt", "KAGGLE_BENCH_RUN.md",
    ]
    for pat in research_globs:
        for f in proj.glob(pat):
            if f.is_file():
                dest = proj / "_research" / f.name
                if not dest.exists():
                    try:
                        shutil.move(str(f), str(dest))
                        print("MOVED", f.name)
                    except Exception as e:
                        print("skip", f.name, e)

    # 4) move _p*.py to _scripts
    for f in proj.glob("_p*.py"):
        dest = proj / "_scripts" / f.name
        if not dest.exists():
            try:
                shutil.move(str(f), str(dest))
                print("MOVED", f.name, "-> _scripts/")
            except Exception as e:
                print("skip", f.name, e)
    for f in proj.glob("p*_*.py"):
        if f.is_file() and f.name.startswith("p"):
            dest = proj / "_scripts" / f.name
            if not dest.exists():
                try:
                    shutil.move(str(f), str(dest))
                except Exception:
                    pass

    # 5) stray typo folders
    for p in KAGGLE.iterdir():
        if not p.is_dir() or p == proj:
            continue
        if "ulture" not in p.name:
            continue
        if (p / "reference_agents" / "fallow_finn.py").exists():
            continue
        for f in list(p.iterdir()) if p.exists() else []:
            dest = proj / "_scripts" / f.name
            try:
                if f.is_file() and not dest.exists():
                    shutil.move(str(f), str(dest))
                    print("MOVED_STRAY", f, "->", dest)
            except Exception:
                pass

    # 6) production note
    prod = proj / "_production" / "STATUS.md"
    prod.write_text(
        "# Production (FROZEN)\n\n"
        "- alperen_meta ~2262.6 (ref 56244291)\n"
        "- last-2: alperen + V16 (~978) — team = better-of-two ≈ 2262\n"
        "- NO submit without new-family gate\n"
        "- Reopen: author R2 / reproducible 2400+ / new fp + H2H\n",
        encoding="utf-8",
    )

    # 7) INDEX
    index = proj / "INDEX.md"
    lines = [
        "# Kaggriculture Workspace",
        "",
        f"Canonical project: `{proj}`",
        "",
        "## Layout",
        "```",
        "_production/     production status (alperen FROZEN)",
        "_research/       RESEARCH_*.md + p*.csv experiment logs",
        "_scripts/        _p*.py experiment runners",
        "_external/       notebooks, extracts, replays",
        "reference_agents/ finn + pool",
        "_push_alperen/   last submitted alperen package",
        "_push_medal/     R2 champion package",
        "```",
        "",
        "## Key files",
        "- `_production/STATUS.md`",
        "- `_research/RESEARCH_FINAL_CLOSE.md`",
        "- `_research/p73_top_tape_eval.csv` (if present)",
        "- `_external/p51_extracted2/` alperen + guru",
        "",
        "## P73",
        "See terminal printout / `_research/p73_top_tape_eval.csv`.",
        "Frozen top-team tapes typically ≪ live reward vs finn.",
        "",
    ]
    # list research files
    res = proj / "_research"
    if res.exists():
        lines.append("## _research contents (sample)")
        for f in sorted(res.iterdir())[:40]:
            lines.append(f"- {f.name}")
        n = len(list(res.iterdir()))
        if n > 40:
            lines.append(f"- … +{n-40} more")
    index.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\nWROTE", index)
    print("WROTE", prod)


if __name__ == "__main__":
    main()
