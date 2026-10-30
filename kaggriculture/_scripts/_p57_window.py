# -*- coding: utf-8 -*-
"""P57: d7–d12 window path features vs d20+ branch. Read-only + LOSO."""
from __future__ import annotations

import csv
import importlib.util
import io
import json
import statistics
import sys
from collections import defaultdict
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

ALPEREN = ROOT / "_external" / "p51_extracted2" / "kaggriculture_metacounter_r1_scored_agent.py"
R2 = ROOT / "_push_medal" / "main.py"
SEEDS = (1, 2, 3, 4, 5, 11, 12, 13)
D0, D1 = 7, 13  # window [d7, d13)
L0, L1 = 20, 30  # late [d20, d30)


def load_quiet(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    with redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


def akey(a):
    return json.dumps({"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                      sort_keys=True, default=str)


def snap(obs, act):
    player = int(obs.get("player") or 0)
    farms = obs.get("farms") or []
    farm = farms[player] if player < len(farms) else {}
    private = obs.get("private") or {}
    shed = dict(private.get("shed") or {})
    prices = dict((obs.get("market") or {}).get("prices") or {})
    shops = list((obs.get("town") or {}).get("unlocked_shops") or [])
    tiles = farm.get("tiles") or []
    plants = animals = 0
    for row in tiles:
        for t in row:
            if isinstance(t, dict):
                if t.get("kind") == "PLANT":
                    plants += 1
                if t.get("animal"):
                    animals += 1
    n_sell = sum(1 for o in (act.get("market") or []) if o and o[0] == "SELL")
    n_buy = sum(1 for o in (act.get("market") or []) if o and o[0] and o[0].startswith("BUY"))
    n_hire = sum(1 for o in (act.get("market") or []) if o and o[0] == "HIRE")
    sell_qty = sum(int(o[2]) for o in (act.get("market") or []) if o and o[0] == "SELL" and len(o) >= 3)
    return {
        "money": float(farm.get("money") or 0),
        "hands": len(farm.get("hands") or []),
        "plants": plants,
        "animals": animals,
        "shed": sum(int(v or 0) for v in shed.values()),
        "n_shops": len(shops),
        "px_w": int(prices.get("WHEAT") or 0),
        "px_m": int(prices.get("MELON") or 0),
        "n_sell": n_sell, "n_buy": n_buy, "n_hire": n_hire,
        "sell_qty": sell_qty,
    }


def window_features(snaps, acts, lo, hi):
    """lo/hi are day indices inclusive-exclusive."""
    t0, t1 = lo * 24, hi * 24
    n = min(len(snaps), t1)
    sl = snaps[t0:n]
    al = acts[t0:n]
    if not sl:
        return {}
    m0, m1 = sl[0]["money"], sl[-1]["money"]
    p0, p1 = sl[0]["plants"], sl[-1]["plants"]
    a0, a1 = sl[0]["animals"], sl[-1]["animals"]
    h0, h1 = sl[0]["hands"], sl[-1]["hands"]
    sell_n = sum(s["n_sell"] for s in sl)
    buy_n = sum(s["n_buy"] for s in sl)
    hire_n = sum(s["n_hire"] for s in sl)
    sell_q = sum(s["sell_qty"] for s in sl)
    # shop change count during window
    shop_changes = 0
    prev = sl[0]["n_shops"]
    for s in sl:
        if s["n_shops"] != prev:
            shop_changes += 1
            prev = s["n_shops"]
    # action diversity
    keys = [akey(a) for a in al]
    uniq = len(set(keys))
    return {
        "dmoney": m1 - m0,
        "dplants": p1 - p0,
        "danimals": a1 - a0,
        "dhands": h1 - h0,
        "money_end": m1,
        "plants_end": p1,
        "sell_events": sell_n,
        "buy_events": buy_n,
        "hire_events": hire_n,
        "sell_qty": sell_q,
        "shop_changes": shop_changes,
        "uniq_actions": uniq,
        "n_steps": len(sl),
    }


def late_label(acts_a, acts_b, lo, hi):
    t0, t1 = lo * 24, hi * 24
    n = min(len(acts_a), len(acts_b), t1)
    tot = max(1, n - t0)
    div = sum(1 for t in range(t0, n) if akey(acts_a[t]) != akey(acts_b[t]))
    frac = div / tot
    # discrete label for LOSO
    if frac >= 0.85:
        return 2, frac  # full branch
    if frac >= 0.5:
        return 1, frac
    return 0, frac


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return 0.0
    mx, my = statistics.mean(xs), statistics.mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = (sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)) ** 0.5
    return num / den if den else 0.0


def main():
    print("recording alperen vs R2 on 8 seeds...", flush=True)
    corpus = []
    for seed in SEEDS:
        alp = load_quiet(ALPEREN, f"p57a_{seed}")
        r2 = load_quiet(R2, f"p57r_{seed}")
        sa, sb, aa, ab = [], [], [], []

        def wa(obs, configuration=None):
            act = alp(obs, configuration)
            sa.append(snap(obs, act))
            aa.append(act)
            return act

        def wb(obs, configuration=None):
            act = r2(obs, configuration)
            sb.append(snap(obs, act))
            ab.append(act)
            return act

        env = make("kaggriculture", debug=False)
        env.configuration["episodeSteps"] = 720
        if env.info is None:
            env.info = {}
        env.info["seed"] = int(seed)
        env.run([wa, wb])
        f = env.steps[-1]
        ba = float(f[0]["observation"]["farms"][0]["money"])
        br = float(f[1]["observation"]["farms"][1]["money"])
        feat = window_features(sa, aa, D0, D1)
        lab, frac = late_label(aa, ab, L0, L1)
        # early control
        _, efrac = late_label(aa, ab, 2, 6)
        rec = {"seed": seed, "alp_bank": ba, "r2_bank": br,
               "late_label": lab, "late_frac": round(frac, 4),
               "early_frac": round(efrac, 4), **feat}
        corpus.append(rec)
        print(f"  s{seed}: late_frac={frac:.3f} lab={lab} "
              f"dmoney={feat['dmoney']:.0f} sell_ev={feat['sell_events']} "
              f"uniq={feat['uniq_actions']} shop_ch={feat['shop_changes']}", flush=True)

    # feature → late_frac correlation
    print("\n=== feature vs late_frac (all seeds) ===", flush=True)
    feats = [k for k in corpus[0] if k.startswith("d") or k.endswith(
        ("_end", "_events", "_qty", "_changes", "_actions", "_steps"))]
    corrs = []
    for fk in feats:
        xs = [r[fk] for r in corpus]
        ys = [r["late_frac"] for r in corpus]
        c = pearson(xs, ys)
        corrs.append((abs(c), c, fk))
        print(f"  {fk:16s} pearson={c:+.3f}", flush=True)
    corrs.sort(reverse=True)
    print("top |corr|", [(fk, round(c, 3)) for _, c, fk in corrs[:5]], flush=True)

    # LOSO: simple threshold rule on best feature — majority vote on train
    print("\n=== LOSO single-threshold rules (top 3 |corr| features) ===", flush=True)
    for _, _, fk in corrs[:3]:
        correct = []
        for held in SEEDS:
            train = [r for r in corpus if r["seed"] != held]
            test = next(r for r in corpus if r["seed"] == held)
            vals = sorted(r[fk] for r in train)
            # try mid threshold; predict label 2 if above median of high-late train
            hi = [r for r in train if r["late_label"] == 2]
            lo = [r for r in train if r["late_label"] != 2]
            if not hi or not lo:
                thr = statistics.median(vals)
            else:
                thr = (statistics.mean(r[fk] for r in hi) + statistics.mean(r[fk] for r in lo)) / 2
            pred = 2 if test[fk] >= thr else 0
            correct.append(int(pred == test["late_label"] or
                                (pred == 2 and test["late_frac"] >= 0.85) or
                                (pred == 0 and test["late_frac"] < 0.85)))
        acc = sum(correct) / len(correct)
        print(f"  rule {fk}: LOSO_acc={acc:.3f} hits={sum(correct)}/{len(correct)}", flush=True)

    # always-2 baseline
    base = sum(1 for r in corpus if r["late_frac"] >= 0.85) / len(corpus)
    print(f"  always_predict_full_branch acc={base:.3f}", flush=True)

    with open(ROOT / "p57_window_features.csv", "w", newline="", encoding="utf-8") as f:
        wri = csv.DictWriter(f, fieldnames=list(corpus[0].keys()))
        wri.writeheader()
        wri.writerows(corpus)

    best_c = corrs[0][0] if corrs else 0
    loso_best = 0
    # recompute best loso quickly from printed logic — store
    print(f"\nmax |corr|={best_c:.3f}", flush=True)
    if best_c < 0.7 or base >= 0.5:
        print("P57_STOP CONDITIONAL_POLICY_EXTRACTION_CLOSED", flush=True)
    else:
        print("P57_WINDOW_SIGNAL_WEAK_OR_PRESENT_REVIEW_MANUALLY", flush=True)
    print("wrote p57_window_features.csv", flush=True)


if __name__ == "__main__":
    main()
