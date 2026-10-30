# -*- coding: utf-8 -*-
"""P52: H2H generalization — gate-pass candidates vs full elite pool."""
from __future__ import annotations

import csv
import importlib.util
import io
import statistics
import sys
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

EXT = ROOT / "_external" / "p51_extracted2"
CANDS = {
    "alperen_meta": EXT / "kaggriculture_metacounter_r1_scored_agent.py",
    "guru_dynamic": EXT / "kaggriculture_fully_dynamic_autonomous_agent.py",
}
OPPONENTS = {
    "R2": ROOT / "_push_medal" / "main.py",
    "V16": ROOT / "_external" / "p41_extracted" / "salem_2900_main.py",
    "kaito_v27": ROOT / "_external" / "public_nb" / "kaito_v27" / "main.py",
    "qeinstein": ROOT / "_external" / "git" / "qeinstein" / "dist" / "sub-009-moev2" / "main.py",
    "rayk_rank": ROOT / "_external" / "public_nb" / "rayk_rank" / "main.py",
}
FINN = ROOT / "reference_agents" / "fallow_finn.py"
# R2 twin is same policy as R2 locally (P46 path twin); include R2 once.
# If twin file exists, add it.
TWIN = ROOT / "_push_medal" / "main.py"  # same as R2 for local H2H; noted in report

SEEDS = (1, 2, 3, 4, 5, 11, 12, 13)


def load_quiet(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    with redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


def run(a0, a1, seed):
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([a0, a1])
    f = env.steps[-1]
    return (
        float(f[0]["observation"]["farms"][0]["money"]),
        float(f[1]["observation"]["farms"][1]["money"]),
    )


def h2h_vs(our_fn, opp_path, seeds, opp_label, cand_label):
    w = d = l = 0
    banks = []
    for seed in seeds:
        a0, a1 = run(our_fn, load_quiet(opp_path, f"{cand_label}_{opp_label}_{seed}a"), seed)
        b0, b1 = run(load_quiet(opp_path, f"{opp_label}_{cand_label}_{seed}b"), our_fn, seed)
        our = (a0 + b1) / 2
        theirs = (a1 + b0) / 2
        banks.append(our)
        if our > theirs + 1:
            w += 1
            res = "W"
        elif theirs > our + 1:
            l += 1
            res = "L"
        else:
            d += 1
            res = "D"
        print(f"    s{seed}: us={our:.0f} opp={theirs:.0f} {res}", flush=True)
    return w, d, l, statistics.mean(banks) if banks else 0


def classify(w, d, l):
    n = w + d + l
    if n == 0:
        return "EMPTY"
    if w >= n * 0.75:
        return "STRONG"
    if w > l:
        return "FAVOR"
    if w == l:
        return "EVEN"
    return "UNDERDOG"


def main():
    opps = dict(OPPONENTS)
    opps["finn"] = FINN  # weak ref; expected W
    # note: R2 twin not a separate local file; R2 covers family

    rows = []
    print("=== P52 H2H Generalization Gate ===", flush=True)
    print(f"seeds={SEEDS} both seats", flush=True)

    for cname, cpath in CANDS.items():
        print(f"\n######## {cname} ########", flush=True)
        cfn = load_quiet(cpath, f"p52_{cname}")
        summary = []
        for oname, opath in opps.items():
            print(f"  vs {oname}", flush=True)
            w, d, l, mean = h2h_vs(cfn, opath, SEEDS, oname, cname)
            cls = classify(w, d, l)
            print(f"  => {cname} vs {oname}: {w}-{d}-{l} bank_mean={mean:.0f} {cls}", flush=True)
            rec = {
                "candidate": cname, "opponent": oname,
                "W": w, "D": d, "L": l, "W-L": w - l,
                "bank_mean": mean, "class": cls,
            }
            rows.append(rec)
            summary.append(rec)

        elite = [r for r in summary if r["opponent"] not in ("finn",)]
        wtot = sum(r["W"] for r in elite)
        dtot = sum(r["D"] for r in elite)
        ltot = sum(r["L"] for r in elite)
        n_strong = sum(1 for r in elite if r["class"] in ("STRONG", "FAVOR"))
        print(f"\n  {cname} ELITE POOL (ex finn): {wtot}-{dtot}-{ltot} "
              f"favor/strong opponents={n_strong}/{len(elite)}", flush=True)

        # submit recommendation
        if wtot >= 30 and ltot <= 12 and n_strong >= 3:
            verdict = "CROSS_ELITE_STRONG_SUBMIT_OK"
        elif wtot > ltot and n_strong >= 2:
            verdict = "CROSS_ELITE_FAVOR_SUBMIT_MAYBE"
        elif any(r["opponent"] == "R2" and r["W"] >= 5 for r in elite) and wtot < ltot:
            verdict = "R2_COUNTER_ONLY_NO_SUBMIT"
        else:
            verdict = "MIXED_NO_SUBMIT"
        print(f"  P52_VERDICT_{cname}={verdict}", flush=True)

    with open(ROOT / "p52_h2h_generalization.csv", "w", newline="", encoding="utf-8") as f:
        wri = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        wri.writeheader()
        wri.writerows(rows)
    print("\nwrote p52_h2h_generalization.csv", flush=True)

    # final table
    print("\n=== TABLE ===", flush=True)
    for r in rows:
        print(f"  {r['candidate'][:14]:14s} vs {r['opponent'][:10]:10s} "
              f"{r['W']}-{r['D']}-{r['L']} {r['class']}", flush=True)


if __name__ == "__main__":
    main()
