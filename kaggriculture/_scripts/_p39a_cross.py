# -*- coding: utf-8 -*-
"""P39-A: does elite worker tape carry independent production value?

Cross:
  1. pure elite
  2. elite worker tape + weak market
  3. elite market tape + PASS workers
  4. elite market tape + p11 workers
  5. p11 full
  6. weak_market only
"""
from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "p39_worker_tape"))

from harness import (  # noqa: E402
    ELITES, load_elite, record_elite_tapes, run_vs_finn,
    weak_market_agent, weak_worker_from_p11,
    tape_worker_agent, tape_market_agent, tape_market_p11_worker_agent,
)


def setup_b():
    import p13_1_melon, p13_3_water, p14_1_on, p14_2_on, p16_branch, p17_1_library, p18_selector
    p13_1_melon.set_enabled(False)
    p13_3_water.set_enabled(True)
    p14_1_on.set_enabled(True)
    p14_2_on.set_enabled(False)
    p16_branch.set_branch_mode("off")
    p17_1_library.set_enabled(False)
    p18_selector.set_selector("S0")
    from p11_planner import planner as pmod
    pmod._PLANNER = None
    if hasattr(weak_worker_from_p11, "_pl"):
        delattr(weak_worker_from_p11, "_pl")
    try:
        from harness import tape_market_p11_worker_agent as tm
        if hasattr(tm, "_pl"):
            delattr(tm, "_pl")
    except Exception:
        pass


def main():
    t0 = time.time()
    seed = 1
    names = list(ELITES.keys())

    print("=== RECORD ELITE TAPES seed1 ===", flush=True)
    tapes = record_elite_tapes(names, seed=seed)

    rows = []

    def log(label, bank, extra=""):
        rows.append({"label": label, "bank": bank, "seed": seed, "extra": extra})
        print(f"  {label:40s} {bank:10.0f} {extra}", flush=True)

    # baselines
    print("\n=== BASELINES ===", flush=True)
    setup_b()
    r = run_vs_finn(weak_market_agent, seed)
    log("weak_market_only", r["bank"])

    setup_b()

    def p11_agent(obs, configuration=None):
        return weak_worker_from_p11(obs, configuration)

    r = run_vs_finn(p11_agent, seed)
    log("p11_full", r["bank"])

    # per-elite crosses
    print("\n=== ELITE CROSSES ===", flush=True)
    for name in names:
        pure = tapes[name]["bank"]
        log(f"pure_{name}", pure, "ref")

        setup_b()
        wfn = tape_worker_agent(tapes[name]["tape"])
        r = run_vs_finn(wfn, seed)
        log(f"{name}_worker+weak_mkt", r["bank"])

        setup_b()
        mfn = tape_market_agent(tapes[name]["tape"])
        r = run_vs_finn(mfn, seed)
        log(f"{name}_market+PASS_wkr", r["bank"])

        setup_b()
        mp = tape_market_p11_worker_agent(tapes[name]["tape"])
        r = run_vs_finn(mp, seed)
        log(f"{name}_market+p11_wkr", r["bank"])

    out = ROOT / "p39a_crosses.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print("\n=== SUMMARY ===", flush=True)
    print(f"wrote {out.name} dt={time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
