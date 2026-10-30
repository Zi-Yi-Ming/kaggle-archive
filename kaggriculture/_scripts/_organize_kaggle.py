# -*- coding: utf-8 -*-
"""Organize Kaggle workspace: find canonical kaggriculture project, tidy strays."""
from __future__ import annotations

import shutil
from pathlib import Path

KAGGLE = Path(r"D:\桌面\Kaggle")


def find_project() -> Path | None:
    """Directory that actually contains the competition harness."""
    cands = []
    for p in KAGGLE.iterdir():
        if not p.is_dir():
            continue
        if (p / "reference_agents" / "fallow_finn.py").exists():
            cands.append(p)
        elif (p / "_push_alperen" / "main.py").exists():
            cands.append(p)
        elif (p / "p26_harness.py").exists():
            cands.append(p)
    return cands[0] if cands else None


def main():
    proj = find_project()
    if proj is None:
        print("NO_CANONICAL_PROJECT")
        for p in KAGGLE.iterdir():
            if p.is_dir() and "ulture" in p.name:
                print(" candidate:", repr(p.name), "emptyish=", not any(p.rglob("*.py")))
        return
    print("CANONICAL_PROJECT", proj)
    print("  finn", (proj / "reference_agents" / "fallow_finn.py").exists())
    print("  alperen", (proj / "_external" / "p51_extracted2").exists())
    print("  p68", (proj / "_external" / "p68_daily_top").exists())

    # move stray p73 script / logs from typo folders into canonical _scripts
    scripts = proj / "_scripts"
    scripts.mkdir(exist_ok=True)
    for p in KAGGLE.iterdir():
        if not p.is_dir() or p == proj:
            continue
        if "ulture" not in p.name:
            continue
        for f in list(p.glob("_p7*")) + list(p.glob("_p6*")) + list(p.glob("p7*")):
            dest = scripts / f.name
            try:
                shutil.move(str(f), str(dest))
                print("MOVED", f, "->", dest)
            except Exception as e:
                print("MOVE_FAIL", f, e)

    # index key artifacts
    print("\nKEY ARTIFACTS under", proj.name)
    for rel in [
        "_push_alperen/main.py",
        "_external/p51_extracted2/kaggraviculture_metacounter_r1_scored_agent.py",
        "RESEARCH_FINAL_CLOSE.md",
        "RESEARCH_P53_LEADERBOARD_CHECK.md",
        "p52_h2h_generalization.csv",
        "p73_top_tape_eval.csv",
    ]:
        fp = proj / rel
        # fuzzy
        if not fp.exists():
            hits = list(proj.glob(rel.split("/")[-1]))
            fp = hits[0] if hits else fp
        print(" ", rel, "->", fp.exists(), fp if fp.exists() else "")

    # write canonical path note
    note = proj / "CANONICAL_PATH.txt"
    note.write_text(str(proj) + "\n", encoding="utf-8")
    print("\nWROTE", note)


if __name__ == "__main__":
    main()
