# -*- coding: utf-8 -*-
"""P48 Stage1b: leave-one-seed-out — is day_hour_shop generalization or memorization?"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
TRACES = ROOT / "p48_traces"
SEEDS = (1, 2, 3, 4, 5, 11, 12, 13)


def load_all():
    rows = []
    for seed in SEEDS:
        p = TRACES / f"trace_seed{seed}.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        for r in data:
            r["seed"] = seed
            rows.append(r)
    return rows


def shop_key(shops):
    return "|".join(shops) if shops else "NONE"


def mkey(a):
    return json.dumps(a.get("market"), sort_keys=True, default=str)


def wkey(a):
    return json.dumps({"f": a.get("farmer"), "h": a.get("hands")}, sort_keys=True, default=str)


def train_table(rows, key_fn):
    """key → majority (mkey, wkey)."""
    gm = defaultdict(Counter)
    gw = defaultdict(Counter)
    for r in rows:
        k = key_fn(r)
        gm[k][mkey(r["action"])] += 1
        gw[k][wkey(r["action"])] += 1
    table = {}
    for k in gm:
        table[k] = (gm[k].most_common(1)[0][0], gw[k].most_common(1)[0][0])
    return table


def eval_table(table, rows, key_fn):
    """Return hit stats; unseen keys count as miss."""
    hit = hit_m = hit_w = unseen = tot = 0
    for r in rows:
        tot += 1
        k = key_fn(r)
        if k not in table:
            unseen += 1
            continue
        ma, wa = table[k]
        if mkey(r["action"]) == ma:
            hit_m += 1
        if wkey(r["action"]) == wa:
            hit_w += 1
        if mkey(r["action"]) == ma and wkey(r["action"]) == wa:
            hit += 1
    return {
        "acc": hit / tot if tot else 0,
        "mkt": hit_m / tot if tot else 0,
        "wkr": hit_w / tot if tot else 0,
        "unseen_rate": unseen / tot if tot else 0,
        "n": tot,
    }


KEYS = {
    "day_hour": lambda r: (r["day"], r["hour"]),
    "hour_nshop": lambda r: (r["hour"], r["n_shops"]),
    "day_hour_nshop": lambda r: (r["day"], r["hour"], r["n_shops"]),
    "day_hour_shop": lambda r: (r["day"], r["hour"], shop_key(r["shops"])),
    "day_nshop": lambda r: (r["day"], r["n_shops"]),
    "day_hour_shopid_set": lambda r: (r["day"], r["hour"], frozenset(r["shops"])),
}


def main():
    rows = load_all()
    print(f"n={len(rows)}", flush=True)

    # LOSO for each schema
    print("\n=== leave-one-seed-out ===", flush=True)
    loso = {name: [] for name in KEYS}
    for held in SEEDS:
        train = [r for r in rows if r["seed"] != held]
        test = [r for r in rows if r["seed"] == held]
        for name, fn in KEYS.items():
            table = train_table(train, fn)
            st = eval_table(table, test, fn)
            loso[name].append(st)
        print(f"  held={held} n_test={len(test)}", flush=True)

    print(f"\n{'schema':22s} {'acc':8s} {'mkt':8s} {'wkr':8s} {'unseen':8s}")
    summary = {}
    for name, stats in loso.items():
        acc = sum(s["acc"] for s in stats) / len(stats)
        mkt = sum(s["mkt"] for s in stats) / len(stats)
        wkr = sum(s["wkr"] for s in stats) / len(stats)
        uns = sum(s["unseen_rate"] for s in stats) / len(stats)
        summary[name] = {"acc": acc, "mkt": mkt, "wkr": wkr, "unseen": uns}
        print(f"{name:22s} {acc:8.4f} {mkt:8.4f} {wkr:8.4f} {uns:8.4f}", flush=True)

    # multi-obs consistency only (train-internal)
    print("\n=== train-internal consistency on multi-obs keys only ===", flush=True)
    for name, fn in KEYS.items():
        groups = defaultdict(list)
        for r in rows:
            groups[fn(r)].append(r)
        multi = {k: v for k, v in groups.items() if len(v) > 1}
        if not multi:
            print(f"  {name}: no multi-obs keys", flush=True)
            continue
        corr = tot = 0
        for k, items in multi.items():
            am = Counter(mkey(r["action"]) for r in items)
            ma = am.most_common(1)[0][0]
            for r in items:
                tot += 1
                if mkey(r["action"]) == ma:
                    corr += 1
        print(f"  {name}: multi_keys={len(multi)} obs={tot} "
              f"mkt_acc={corr/tot if tot else 0:.4f}", flush=True)

    # best LOSO
    best = max(summary.items(), key=lambda x: x[1]["acc"])
    print(f"\nbest LOSO schema={best[0]} acc={best[1]['acc']:.4f} "
          f"unseen={best[1]['unseen']:.4f}", flush=True)

    if best[1]["acc"] >= 0.95 and best[1]["unseen"] < 0.05:
        gate = "GENERALIZES"
    elif best[1]["acc"] >= 0.85 and best[1]["unseen"] < 0.2:
        gate = "PARTIAL_GENERALIZATION"
    elif best[1]["unseen"] >= 0.5:
        gate = "MEMORIZATION_RISK_HIGH"
    else:
        gate = "WEAK_GENERALIZATION"

    # day_hour is the only schema with full coverage
    dh = summary["day_hour"]
    print(f"day_hour LOSO acc={dh['acc']:.4f} (unseen=0 expected)", flush=True)
    print(f"P48_STAGE1B={gate}", flush=True)

    with open(ROOT / "p48_loso.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["schema", "acc", "mkt", "wkr", "unseen"])
        w.writeheader()
        for name, s in summary.items():
            w.writerow({"schema": name, **s})

    (ROOT / "p48_stage1b_summary.json").write_text(json.dumps({
        "gate": gate,
        "best": best[0],
        "summary": summary,
        "day_hour": dh,
    }, indent=2), encoding="utf-8")
    print("wrote p48_loso.csv p48_stage1b_summary.json", flush=True)


if __name__ == "__main__":
    main()
