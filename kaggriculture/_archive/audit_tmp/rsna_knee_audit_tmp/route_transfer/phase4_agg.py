"""EXP-9 Phase 4 aggregation: paired T1-T0 stats per pool/seat/opponent.

Reads phase4_bench.jsonl (deduped by kind/opponent/seed), computes:
  - per pool: T0/T1 mean bank, mean/median/std Δ, 95% CI, Wilson CI on T1
    win rate, paired permutation p, effect size (Cohen's d)
  - seat breakdown
  - opponent breakdown
  - SELL failure / execution rate (T1 vs T0)
  - accounting audit (reconciliation != 0 count)
"""
import json
import math
import random
from collections import defaultdict

JSONL = "_audit_tmp/route_transfer/phase4_bench.jsonl"
HET = {"broker_bea", "slotter_silas", "ledger_lena", "melon_mateo", "rancher_rita"}


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    m = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / d
    return (c - m, c + m)


def perm_p(deltas, n_perm=20000, seed=7):
    rnd = random.Random(seed)
    obs = sum(deltas)
    cnt = 0
    for _ in range(n_perm):
        s = sum(d if rnd.random() < 0.5 else -d for d in deltas)
        if abs(s) >= abs(obs):
            cnt += 1
    return (cnt + 1) / (n_perm + 1)


def ci95(xs):
    n = len(xs)
    m = sum(xs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1)) if n > 1 else 0.0
    return m - 1.96 * sd / math.sqrt(n), m + 1.96 * sd / math.sqrt(n)


def cohen_d(deltas):
    n = len(deltas)
    m = sum(deltas) / n
    sd = math.sqrt(sum((d - m) ** 2 for d in deltas) / (n - 1)) if n > 1 else 0.0
    return m / sd if sd > 0 else 0.0


def main():
    rows = {}
    with open(JSONL, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            rows[(r["kind"], r["opponent"], r["seed"])] = r
    games = list(rows.values())
    print(f"去重后 {len(games)} 局 | recon!=0: {sum(1 for r in games if abs(r['recon']) > 0.005)}")
    pools = {"closer_cleo": {}, "heterogeneous": {}}
    for r in games:
        pool = "closer_cleo" if r["opponent"] == "closer_cleo" else "heterogeneous"
        pools[pool].setdefault(r["kind"], {})[(r["opponent"], r["seed"])] = r

    for pool, D in pools.items():
        keys = sorted(set.intersection(*(set(d) for d in D.values())))
        t0 = [D["T0"][k]["final_bank"] for k in keys]
        t1 = [D["T1"][k]["final_bank"] for k in keys]
        dl = [a - b for a, b in zip(t1, t0)]
        wins = sum(1 for d in dl if d > 0)
        ties = sum(1 for d in dl if d == 0)
        mean_d = sum(dl) / len(dl)
        med = sorted(dl)[len(dl) // 2]
        std = math.sqrt(sum((d - mean_d) ** 2 for d in dl) / (len(dl) - 1))
        lo, hi = ci95(dl)
        wlo, whi = wilson(wins, len(dl))
        p = perm_p(dl)
        d_eff = cohen_d(dl)
        print(f"\n=== {pool}（n={len(dl)} paired）===")
        print(f"T0 mean {sum(t0)/len(t0):.0f} | T1 mean {sum(t1)/len(t1):.0f} | Δ mean {mean_d:+.0f} "
              f"median {med:+.0f} std {std:.0f}")
        print(f"Δ 95%CI [{lo:+.0f}, {hi:+.0f}] | T1 win {wins}/{len(dl)} (ties {ties}) "
              f"rate {100*wins/len(dl):.1f}% CI [{wlo:.3f},{whi:.3f}] | paired-p {p:.4f} | d {d_eff:.2f}")
        # seat breakdown
        for seat in (0, 1):
            ks = [k for k in keys if k[1] % 2 == (1 - seat)]  # seat = 0 if seed even
            dl_s = [D["T1"][k]["final_bank"] - D["T0"][k]["final_bank"] for k in ks]
            w_s = sum(1 for d in dl_s if d > 0)
            if ks:
                print(f"  seat {seat}: n={len(ks)} Δ {sum(dl_s)/len(dl_s):+.0f} T1 win {100*w_s/len(dl_s):.0f}%")
        # SELL failure
        for kind in ("T0", "T1"):
            fs = [D[kind][k]["issued_sell"] - D[kind][k]["exec_sell"] for k in keys]
            ex = sum(D[kind][k]["exec_sell"] for k in keys)
            iss = sum(D[kind][k]["issued_sell"] for k in keys)
            print(f"  {kind}: SELL issued {iss} executed {ex} failed {iss-ex} "
                  f"failure-rate {100*(iss-ex)/iss:.1f}%")

    print("\n=== opponent breakdown (heterogeneous) ===")
    for opp in sorted(HET):
        ks = sorted(k for k in rows if k[1] == opp)
        ks = [(k[2]) for k in ks if k[0] == "T0"]
        t0b = [rows[("T0", opp, s)]["final_bank"] for s in ks]
        t1b = [rows[("T1", opp, s)]["final_bank"] for s in ks]
        dl = [a - b for a, b in zip(t1b, t0b)]
        w = sum(1 for d in dl if d > 0)
        print(f"  {opp}: n={len(dl)} Δ {sum(dl)/len(dl):+.0f} T1 wins {w} losses {len(dl)-w}")


if __name__ == "__main__":
    main()
