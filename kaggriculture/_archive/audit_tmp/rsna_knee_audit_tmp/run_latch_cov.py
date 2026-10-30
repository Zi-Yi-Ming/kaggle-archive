"""EXP-2 Phase A — heterogeneous trigger coverage runner (file-based for mp.Pool).

Usage: python _audit_tmp/run_latch_cov.py [opp1 opp2 ...]  (default all 5)
Per-opponent Pool batch (120 seeds), flush to _audit_tmp/latch_coverage.jsonl.
"""
import json
import multiprocessing as mp
import sys
import time

sys.path.insert(0, "_audit_tmp")
sys.path.insert(0, "kaggriculture")
import latch_coverage as L

OUT = "_audit_tmp/latch_coverage.jsonl"
ALL = ["broker_bea", "slotter_silas", "ledger_lena", "melon_mateo", "rancher_rita"]


def main():
    ops = sys.argv[1:] if len(sys.argv) > 1 else ALL
    t0 = time.time()
    mode = "a" if len(ops) < len(ALL) else "w"
    with open(OUT, mode, encoding="utf-8") as f:
        for op in ops:
            jobs = [(op, s) for s in range(1, 121)]
            with mp.Pool(12) as pool:
                recs = list(pool.imap_unordered(L.one, jobs))
            recs.sort(key=lambda r: r["seed"])
            for r in recs:
                f.write(json.dumps(r) + "\n")
            f.flush()
            print(f"[cov] {op} done ({len(recs)}) @{time.time()-t0:.0f}s", flush=True)
    print("DONE")


if __name__ == "__main__":
    main()
