# -*- coding: utf-8 -*-
"""P35-B ablation: skeleton vs R2 vs controls (pinned)."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402
from p26_harness import load_r2, load_pool  # noqa: E402


def setup_b_flags():
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


def run_vs_finn(own_fn, seed):
    finn = load_pool("fallow_finn")
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([own_fn, finn])
    f = env.steps[-1]
    return float(f[0]["observation"]["farms"][0]["money"])


def main():
    rows = []
    seeds = (1, 2, 3)
    for seed in seeds:
        # R2
        setup_b_flags()
        bank_r2 = run_vs_finn(load_r2(), seed)
        # skeleton normal
        import p35_skeleton as sk
        setup_b_flags()
        sk.reset()
        bank_sk = run_vs_finn(sk.make_agent("normal"), seed)
        # landmark only (weaker sell)
        setup_b_flags()
        sk.reset()
        bank_lm = run_vs_finn(sk.make_agent("landmark_only"), seed)
        # random shift falsification
        setup_b_flags()
        sk.reset()
        bank_rnd = run_vs_finn(sk.make_agent("normal", shift=7), seed)

        rec = {
            "seed": seed, "R2": bank_r2, "skeleton": bank_sk,
            "landmark_only": bank_lm, "random_shift7": bank_rnd,
        }
        rows.append(rec)
        print(f"s{seed}: R2={bank_r2:.0f} SKEL={bank_sk:.0f} LM={bank_lm:.0f} RND={bank_rnd:.0f}", flush=True)

    out = ROOT / "p35_skeleton_ablation.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print("\n=== MEANS ===")
    for k in ("R2", "skeleton", "landmark_only", "random_shift7"):
        vals = [r[k] for r in rows]
        print(f"  {k}: {sum(vals)/len(vals):.0f}")
    print("wrote", out.name)


if __name__ == "__main__":
    main()
