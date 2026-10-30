# -*- coding: utf-8 -*-
"""P39-A sanity: same-elite worker+market tape should recover pure bank."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "p39_worker_tape"))

from harness import ELITES, load_elite, record_elite_tapes, run_vs_finn  # noqa: E402


def full_tape_agent(tape):
    def agent(observation, configuration=None):
        step = int((observation or {}).get("step") or 0)
        step = max(0, min(len(tape) - 1, step))
        w = tape[step] or {}
        return {
            "farmer": w.get("farmer") or ["PASS"],
            "hands": w.get("hands") or [],
            "market": w.get("market") or [],
        }
    return agent


def main():
    names = list(ELITES.keys())
    tapes = record_elite_tapes(names, seed=1)
    print("\n=== FULL TAPE REPLAY (worker+market from same elite) ===")
    for name in names:
        fn = full_tape_agent(tapes[name]["tape"])
        r = run_vs_finn(fn, 1)
        pure = tapes[name]["bank"]
        print(f"  {name:12s} pure={pure:.0f} replay={r['bank']:.0f} "
              f"delta={r['bank']-pure:.0f}")


if __name__ == "__main__":
    main()
