# -*- coding: utf-8 -*-
"""Heterogeneous benchmark analysis (TEMP, NOT production).

输入: _pm_bench.csv (agent,opp,seed,win,bank_a,bank_b)
输出:
  1. E/D/A/closer_cleo × opponent matchup matrix(win rate + Wilson CI)
  2. E-D delta(逐 opponent + aggregate), 95% CI
  3. synthetic regime 与 community/historical 分开 aggregate(不等权混算)

用法:
    python _pm_analyze.py                      # 读默认 CSV,打印全部
"""
import os
import math
import json

BASE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(BASE, "_pm_bench.csv")

AGENTS = ["v11E", "D", "A", "closer_cleo"]
AGENT_LABEL = {"v11E": "E", "D": "D", "A": "A(≈v10 approx)",
               "closer_cleo": "closer_cleo(≈v9 approx)"}

# 对手 regime 分组:synthetic = 我们自造的卖货节奏极值;comm = 社区/历史策略
SYNTHETIC_OPPS = {"aggressive", "hoarder", "balanced", "delayed"}
# 被测近似标注(报告用,防与字节级历史版本混淆)
APPROX_AGENTS = {"A": "A=all-off rollback,≈v10(approximate historical policy,非字节级复刻)",
                 "closer_cleo": "社区 tier9,≈v9(approximate historical policy,非字节级复刻)"}


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0, 0.0)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return p, max(0.0, c - h), min(1.0, c + h)


def load():
    rows = []
    for line in open(CSV, encoding="utf-8"):
        p = line.strip().split(",")
        if len(p) < 6:
            continue
        agent, opp, seed, win, ba, bb = p[0], p[1], int(p[2]), p[3], float(p[4]), float(p[5])
        # win 字段: 1/0/tie
        if win == "tie":
            w = None
        else:
            w = int(win)
        rows.append({"agent": agent, "opp": opp, "seed": seed, "win": w,
                     "bank_a": ba, "bank_b": bb})
    return rows


def matchup_table(rows):
    """逐 (agent, opp) 统计。"""
    from collections import defaultdict
    agg = defaultdict(lambda: {"n": 0, "wins": 0, "ties": 0, "bank_diff_sum": 0.0})
    for r in rows:
        k = (r["agent"], r["opp"])
        a = agg[k]
        a["n"] += 1
        if r["win"] == 1:
            a["wins"] += 1
        elif r["win"] is None:
            a["ties"] += 1
        a["bank_diff_sum"] += r["bank_a"] - r["bank_b"]
    return agg


def aggregate(agg, agents, opps):
    """对指定被测集合 × 对手集合聚合(opps 用于 regime 分层)。"""
    out = {}
    for a in agents:
        n = wins = 0
        bd = 0.0
        for op in opps:
            k = (a, op)
            if k in agg:
                n += agg[k]["n"]
                wins += agg[k]["wins"]
                bd += agg[k]["bank_diff_sum"]
        p, lo, hi = wilson(wins, n)
        out[a] = {"n": n, "wins": wins, "win_rate": p, "ci_lo": lo, "ci_hi": hi,
                  "mean_bank_diff": bd / max(1, n)}
    return out


def main():
    rows = load()
    if not rows:
        print("无数据:", CSV, " — 等 benchmark 跑完回传 CSV")
        return
    agg = matchup_table(rows)
    print("总数据行:", len(rows))
    # 数据里的被测名可能用 pool key(v11E)或别名(E)——统一
    # 按 CSV 中出现的 agent 名处理
    present = sorted({r["agent"] for r in rows})
    print("CSV 中出现的被测:", present)

    comm_opps = sorted({r["opp"] for r in rows} - SYNTHETIC_OPPS)
    synth_opps = sorted({r["opp"] for r in rows} & SYNTHETIC_OPPS)
    all_opps = sorted({r["opp"] for r in rows})

    # 1) 逐 opponent matchup matrix(只看数据中实际存在的被测)
    print("\n===== 1. Matchup matrix (win rate, Wilson 95% CI) =====")
    header = "opponent          " + "".join("%-22s" % a for a in present)
    print(header)
    for op in all_opps:
        cells = []
        for a in present:
            k = (a, op)
            if k not in agg:
                cells.append("(n=0)".ljust(22))
                continue
            st = agg[k]
            p, lo, hi = wilson(st["wins"], st["n"])
            cells.append("%.3f [%s-%s] n=%d" % (p, round(lo, 2), round(hi, 2), st["n"])).ljust(22) if False else None
            cells.append(("%.3f[%.2f-%.2f]n=%d" % (p, lo, hi, st["n"])).ljust(22))
        print("%-14s %s" % (op, "".join(cells)))

    # 2) E-D delta(逐 opponent)——需 E 与 D 都测了同一对手
    print("\n===== 2. E-D delta (per opponent) =====")
    e_key = next((a for a in present if a in ("v11E", "E")), None)
    d_key = "D"
    if e_key and d_key in present:
        print("%-14s %-10s %-10s %-10s" % ("opponent", "E win", "D win", "E-D"))
        ed_rows = []
        for op in all_opps:
            ke, kd = (e_key, op), (d_key, op)
            if ke not in agg or kd not in agg:
                continue
            pe = agg[ke]["wins"] / agg[ke]["n"]
            pd_ = agg[kd]["wins"] / agg[kd]["n"]
            ne, nd = agg[ke]["n"], agg[kd]["n"]
            # E-D delta CI(近似:两独立比例差)
            se = math.sqrt(pe * (1 - pe) / ne + pd_ * (1 - pd_) / nd) if (ne and nd) else 0.0
            dlt = pe - pd_
            print("%-14s %-10.3f %-10.3f %+.3f (95%%CI ±%.3f, nE=%d nD=%d)" % (
                op, pe, pd_, dlt, 1.96 * se, ne, nd))
            ed_rows.append((op, dlt, se))
        if ed_rows:
            # 按 E-D delta 排序看集中哪类 opponent
            print("\nE-D delta 排序(升序):")
            for op, dlt, se in sorted(ed_rows, key=lambda x: x[1]):
                print("  %-14s %+.3f" % (op, dlt))
    else:
        print("  (E 或 D 数据缺失,需等 benchmark 跑完)")

    # 3) regime 分层 aggregate
    print("\n===== 3. Regime 分层 aggregate =====")
    for regime, opps in [("ALL opponents", all_opps),
                         ("Community/historical", comm_opps),
                         ("Synthetic regime", synth_opps)]:
        if not opps:
            continue
        out = aggregate(agg, present, opps)
        print("  %-24s" % regime)
        for a, st in out.items():
            print("    %-24s n=%-3d win=%.3f CI[%.2f, %.2f] mean_bank_diff=%+.0f" % (
                a, st["n"], st["win_rate"], st["ci_lo"], st["ci_hi"], st["mean_bank_diff"]))

    # 4) 近似标注(防误读)
    print("\n===== 4. Approximate-policy 标注 =====")
    for a, note in APPROX_AGENTS.items():
        print("  %s: %s" % (a, note))


if __name__ == "__main__":
    main()
