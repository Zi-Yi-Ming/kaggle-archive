"""EXP-8 Phase 5 aggregation: paired stats + route breakdown + migration gate.

Reads phase5_bench.jsonl (deduped by variant/opponent/seed), computes for the
closer_cleo pool and the heterogeneous pool separately:
  - V1-V0 / V2-V1 / V2-V0 mean bank delta (paired)
  - paired permutation p (two-sided, 20000 resamples)
  - Wilson CI on win rate (fraction of seeds where later > earlier)
  - V2 route breakdown
  - reconciliation summary
  - validation-gap summary (valid<n steps, documented as non-money drifts)
"""
import json
import math
import random
import sys
from collections import defaultdict

JSONL = "_audit_tmp/route_transfer/phase5_bench.jsonl"
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


def main():
    rows = {}
    with open(JSONL, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            rows[(r["variant"], r["opponent"], r["seed"])] = r
    games = list(rows.values())
    print(f"去重后 {len(games)} 局 | recon!=0: {sum(1 for r in games if abs(r['recon'])>0.005)}")
    pools = {"closer_cleo": {}, "heterogeneous": {}}
    for r in games:
        pool = "closer_cleo" if r["opponent"] == "closer_cleo" else "heterogeneous"
        pools[pool].setdefault(r["variant"], {})[r["seed"]] = r
    for pool, V in pools.items():
        seeds = sorted(set.intersection(*(set(d) for d in V.values())))
        print(f"\n=== {pool} 池（{len(seeds)} paired seeds）===")
        for a, b in (("V1", "V0"), ("V2", "V1"), ("V2", "V0")):
            da = [V[a][s]["final_bank"] - V[b][s]["final_bank"] for s in seeds]
            wins = sum(1 for d in da if d > 0)
            mean = sum(da) / len(da)
            p = perm_p(da)
            lo, hi = wilson(wins, len(seeds))
            print(f"  {a}-{b}: Δbank mean {mean:+.1f}/局 | wins {wins}/{len(seeds)} "
                  f"({100*wins/len(seeds):.1f}%, CI [{lo:.3f},{hi:.3f}]) | paired-p {p:.4f}")
        # V2 route breakdown
        v2 = V["V2"]
        from collections import Counter
        rc = Counter(r["route"] for r in v2.values())
        print(f"  V2 route: {dict(rc)}")
        # reconciliation + validation summary per variant
        for v in ("V0", "V1", "V2"):
            rs = [V[v][s] for s in seeds]
            nbad = sum(1 for r in rs if abs(r["recon"]) > 0.005)
            nv = sum(1 for r in rs if r["valid"] != r["n"])
            if nv:
                fm = Counter(r["first_mismatch"] for r in rs if r["valid"] != r["n"])
                print(f"  {v}: recon!=0 {nbad} | 校验<100% {nv}/{len(rs)} | 首分歧步分布(前3): {fm.most_common(3)}")
            else:
                print(f"  {v}: recon!=0 {nbad} | 校验 100%")


if __name__ == "__main__":
    main()
