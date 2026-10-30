# -*- coding: utf-8 -*-
"""P44 Phase5-8: bounded market overlays on distilled tape. W-L fitness."""
from __future__ import annotations

import csv
import copy
import hashlib
import importlib.util
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

TAPES = ROOT / "p44_distilled_tapes"
FINN_PATH = ROOT / "reference_agents" / "fallow_finn.py"
R2_PATH = ROOT / "_push_medal" / "main.py"


def load_agent(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


def load_base_tape():
    d = json.loads((TAPES / "r2_live_distilled.json").read_text(encoding="utf-8"))
    return d["tape"], d["tape_hash"], d["stats"]


def tape_agent(tape):
    def agent(observation, configuration=None):
        step = int((observation or {}).get("step") or 0)
        step = max(0, min(len(tape) - 1, step))
        a = tape[step]
        return {
            "farmer": a.get("farmer") or ["PASS"],
            "hands": a.get("hands") or [],
            "market": a.get("market") or [],
        }
    return agent


def run_both_seats(tape, seed):
    """Return our_mean, opp_mean, banks detail. finn never wrapped."""
    fn = load_agent(FINN_PATH, f"finn44o_{seed}")
    us0 = tape_agent(tape)
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info = {"seed": int(seed)}
    env.run([us0, fn])
    f = env.steps[-1]
    us_s0 = float(f[0]["observation"]["farms"][0]["money"])
    fn_s1 = float(f[1]["observation"]["farms"][1]["money"])

    fn2 = load_agent(FINN_PATH, f"finn44p_{seed}")
    us1 = tape_agent(tape)
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info = {"seed": int(seed)}
    env.run([fn2, us1])
    f = env.steps[-1]
    fn_s0 = float(f[0]["observation"]["farms"][0]["money"])
    us_s1 = float(f[1]["observation"]["farms"][1]["money"])

    our = (us_s0 + us_s1) / 2
    opp = (fn_s1 + fn_s0) / 2
    if our > opp + 1:
        res = "W"
    elif opp > our + 1:
        res = "L"
    else:
        res = "D"
    return our, opp, res, (us_s0, us_s1, fn_s0, fn_s1)


def find_first_sell_step(tape, item):
    for t, a in enumerate(tape):
        for o in a.get("market") or []:
            if o and o[0] == "SELL" and len(o) >= 3 and o[1] == item:
                return t
    return None


def shift_first_sell(tape, item, delta):
    """Move first SELL of item by delta steps. Bounded, interpretable.
    If destination already has SELL same item, merge qty. Record changed_steps.
    """
    t0 = find_first_sell_step(tape, item)
    if t0 is None:
        return None, []
    t1 = t0 + delta
    if t1 < 0 or t1 >= len(tape):
        return None, []
    if t1 == t0:
        return tape, [t0]
    new = copy.deepcopy(tape)
    # remove first sell from t0
    mk0 = []
    moved = None
    for o in new[t0]["market"]:
        if moved is None and o and o[0] == "SELL" and len(o) >= 3 and o[1] == item:
            moved = list(o)
            continue
        mk0.append(o)
    if moved is None:
        return None, []
    new[t0]["market"] = mk0
    # insert at t1
    mk1 = list(new[t1]["market"])
    # merge if same item exists
    merged = False
    for o in mk1:
        if o and o[0] == "SELL" and len(o) >= 3 and o[1] == item:
            o[2] = int(o[2]) + int(moved[2])
            merged = True
            break
    if not merged:
        if len(mk1) >= 10:
            # drop last non-critical or fail
            return None, []
        mk1.append(moved)
    new[t1]["market"] = mk1
    return new, sorted({t0, t1})


def bump_opening_wheat_buy(tape, dq):
    """Find early BUY_SEED WHEAT (step<24) and change qty by dq. dq can be -1..+1."""
    new = copy.deepcopy(tape)
    changed = []
    for t in range(0, 24):
        mk = new[t]["market"]
        for o in mk:
            if o and o[0] == "BUY_SEED" and len(o) >= 3 and o[1] == "WHEAT":
                q = int(o[2]) + dq
                if q <= 0:
                    return None, []
                o[2] = q
                changed.append(t)
                return new, changed
    return None, []


def make_candidates(base):
    """≤12 bounded overlays from P43 historical granularity."""
    cands = []
    cands.append(("c00_baseline", base, [], "none"))

    # P43/V16: one-turn premium lead (shift earlier by 1)
    for item in ("MELON", "MILK", "STRAWBERRY", "WOOL"):
        for d in (-1, 1, -2):
            t, ch = shift_first_sell(base, item, d)
            if t is not None:
                cid = f"c_{item.lower()}_d{d:+d}"
                cands.append((cid, t, ch, f"shift_first_{item}_sell_{d:+d}"))
            if len(cands) >= 12:
                break
        if len(cands) >= 12:
            break

    # opening wheat ±1 if room
    if len(cands) < 12:
        for dq in (1, -1):
            t, ch = bump_opening_wheat_buy(base, dq)
            if t is not None:
                cands.append((f"c_wheat_open_{dq:+d}", t, ch, f"opening_wheat_qty_{dq:+d}"))
            if len(cands) >= 12:
                break

    return cands[:12]


def eval_candidate(tape, seeds, label, changed):
    w = d = l = 0
    banks = []
    rows = []
    for seed in seeds:
        our, opp, res, detail = run_both_seats(tape, seed)
        banks.append(our)
        if res == "W":
            w += 1
        elif res == "L":
            l += 1
        else:
            d += 1
        rows.append({
            "label": label, "seed": seed, "our_mean": our, "opp_mean": opp,
            "result": res, "us_s0": detail[0], "us_s1": detail[1],
            "changed_steps": "|".join(map(str, changed)),
        })
        print(f"    {label} s{seed} our={our:.0f} {res}", flush=True)
    return {
        "label": label, "W": w, "D": d, "L": l, "W-L": w - l,
        "bank_mean": statistics.mean(banks),
        "bank_std": statistics.pstdev(banks) if len(banks) > 1 else 0,
        "changed": changed, "rows": rows,
    }


def main():
    t0 = time.time()
    base, tape_hash, stats = load_base_tape()
    print(f"loaded base tape hash={tape_hash} market_unanimous={stats['market_unanimous_ratio']:.3f}", flush=True)

    cands = make_candidates(base)
    print(f"n_candidates={len(cands)}", flush=True)
    for cid, _, ch, mut in cands:
        print(f"  {cid}: {mut} changed={ch}", flush=True)

    seeds = (1, 2, 3)
    results = []
    all_rows = []
    for cid, tape, ch, mut in cands:
        print(f"\n=== {cid} ===", flush=True)
        r = eval_candidate(tape, seeds, cid, ch)
        r["mutation"] = mut
        results.append(r)
        all_rows.extend(r["rows"])

    # rank by W-L then bank
    results.sort(key=lambda r: (-r["W-L"], -r["bank_mean"]))
    print("\n=== RANKING (W-L first) ===", flush=True)
    for r in results:
        print(f"  {r['label']:28s} {r['W']}-{r['D']}-{r['L']} W-L={r['W-L']} "
              f"bank={r['bank_mean']:.0f}±{r['bank_std']:.0f} {r['mutation']}", flush=True)

    best = results[0]
    base_r = next(r for r in results if r["label"] == "c00_baseline")

    # H2H improvement signal
    signal = best["W-L"] > base_r["W-L"]
    # also compare bank-only
    bank_up = best["bank_mean"] > base_r["bank_mean"] + 1000

    print(f"\nbest={best['label']} W-L={best['W-L']} vs baseline W-L={base_r['W-L']}", flush=True)
    print(f"W-L improvement={signal} bank_up={bank_up}", flush=True)

    with open(ROOT / "p44_h2h.csv", "w", newline="", encoding="utf-8") as f:
        fields = ["label", "W", "D", "L", "W-L", "bank_mean", "bank_std", "mutation", "changed"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in results:
            w.writerow({
                "label": r["label"], "W": r["W"], "D": r["D"], "L": r["L"],
                "W-L": r["W-L"], "bank_mean": r["bank_mean"], "bank_std": r["bank_std"],
                "mutation": r["mutation"],
                "changed": "|".join(map(str, r["changed"])),
            })

    with open(ROOT / "p44_candidate_results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        w.writeheader()
        w.writerows(all_rows)

    # Decision
    if not signal and not (best["W-L"] == base_r["W-L"] and bank_up):
        decision = "P44_NO_OVERLAY_SIGNAL"
    elif signal and best["W"] + best["D"] >= len(seeds):
        # genuine W-L improvement
        if best["label"] != "c00_baseline":
            decision = "PARTIALLY_REPRODUCED"  # recon OK + overlay signal
        else:
            decision = "REPRODUCED"  # base already max W-L
    else:
        decision = "PARTIALLY_REPRODUCED"

    # if baseline already 3-0 and no overlay beats it
    if base_r["W-L"] == len(seeds) and best["W-L"] <= base_r["W-L"]:
        decision = "REPRODUCED" if best["label"] == "c00_baseline" else "P44_NO_OVERLAY_SIGNAL"

    print(f"\nP44_DECISION={decision}", flush=True)
    print(f"dt={time.time()-t0:.0f}s", flush=True)

    summary = {
        "decision": decision,
        "base_wl": base_r["W-L"],
        "best_label": best["label"],
        "best_wl": best["W-L"],
        "best_bank": best["bank_mean"],
        "n_candidates": len(cands),
        "tape_hash": tape_hash,
    }
    (ROOT / "p44_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
