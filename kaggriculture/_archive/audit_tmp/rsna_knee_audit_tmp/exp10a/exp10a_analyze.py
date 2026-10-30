"""EXP-10A analysis: M1 agreement, M2 step entropy, M3 conditional entropy,
backbone ratio, edit distance, first-divergence cause classification
(pre-registered: SHOP > MARKET > OWN_STATE > OPPONENT > UNKNOWN), episodes.
Reads raw_{seed}_{seat}.jsonl (40 games) -> 3 CSVs + printed summary.
"""
import csv
import glob
import json
import math

RAW = "_audit_tmp/exp10a"
BASE_PRICE = {"WHEAT": 25, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100,
              "MELON": 80, "GOOSE": 300, "COW": 400, "SHEEP": 500, "EGG": 10,
              "MILK": 15, "WOOL": 12, "FERTILIZER": 100}

MOVE_OPS = {"NORTH", "SOUTH", "EAST", "WEST"}


def load_games():
    games = {}
    for path in sorted(glob.glob(f"{RAW}/raw_*.jsonl")):
        seed_seat = path.split("raw_")[1].replace(".jsonl", "")
        seed, seat = seed_seat.split("_")
        recs = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                recs.append(json.loads(line))
        games[(int(seed), int(seat))] = recs
    return games


def sub_canon(rec, kind):
    """Extract canonical sub-action by family from the recorded fields."""
    fam = {"farmer": [], "hands": [], "market": []}
    if isinstance(rec.get("act_farmer"), list):
        fam["farmer"] = rec["act_farmer"]
    for h in (rec.get("act_hands") or []):
        fam["hands"].append(h)
    for m in (rec.get("act_market") or []):
        fam["market"].append(m)
    if kind == "all":
        return rec["canon"]
    if kind == "movement":
        parts = []
        for u in [fam["farmer"]] + fam["hands"]:
            if u and u[0] in MOVE_OPS:
                parts.append(":".join(str(x) for x in u))
        return "|".join(parts)
    if kind == "market":
        return ",".join(":".join(str(x) for x in m) for m in fam["market"])
    if kind == "buy":
        return ",".join(":".join(str(x) for x in m) for m in fam["market"]
                        if m and m[0] in ("BUY_SEED", "BUY_PRODUCT", "BUY_ANIMAL"))
    if kind == "sell":
        return ",".join(":".join(str(x) for x in m) for m in fam["market"]
                        if m and m[0] == "SELL")
    if kind == "hire":
        return ",".join(":".join(str(x) for x in m) for m in fam["market"]
                        if m and m[0] == "HIRE")
    if kind == "land":
        return ",".join(":".join(str(x) for x in m) for m in fam["market"]
                        if m and m[0] == "BUY_LAND")
    return rec["canon"]


def entropy(vals):
    from collections import Counter
    n = len(vals)
    if n == 0:
        return 0.0
    c = Counter(vals)
    return -sum((k / n) * math.log(k / n) for k in c.values())


def money_bucket(m):
    for i, hi in enumerate((3000, 10000, 30000, 60000, 120000)):
        if m < hi:
            return i
    return 5


def price_bucket(item, price):
    base = BASE_PRICE.get(item)
    if not base or price is None:
        return "NA"
    return "FLAT" if abs(price - base) < 0.2 * base else ("UP" if price > base else "DOWN")


def mkt_state_key(rec):
    prices = rec.get("mkt_price") or {}
    return tuple(sorted((k, price_bucket(k, v)) for k, v in prices.items()))


def own_state_key(rec):
    money = rec.get("money") or 0
    shed = rec.get("shed") or {}
    inv = rec.get("inventories") or []
    tot = sum(shed.values()) + sum(sum(i.values()) for i in inv if isinstance(i, dict))
    return (money_bucket(money), (0 if tot == 0 else (1 if tot < 10 else (2 if tot < 50 else 3))),
            rec.get("tiles_crop", 0), rec.get("tiles_animal", 0))


def main():
    games = load_games()
    keys = sorted(games.keys())
    n_steps = 720
    kinds = ["all", "movement", "market", "buy", "sell", "hire", "land"]
    N = len(keys)

    # M1 agreement + M2 entropy + backbone per step
    step_stats = {}
    for s in range(n_steps):
        row = {"step": s, "day": games[keys[0]][s]["day"]}
        for k in kinds:
            vals = [sub_canon(games[key][s], k) for key in keys]
            agr = sum(1 for v in vals if v == vals[0]) / N
            row[f"agr_{k}"] = round(agr, 4)
            row[f"H_{k}"] = round(entropy(vals), 4)
        row["backbone_all"] = 1 if row["agr_all"] == 1.0 else 0
        row["H_mov"] = row["H_movement"]
        # M3 conditional entropy (on 'all' actions)
        conds = {
            "shop": lambda r: tuple(r.get("shops") or ()),
            "day": lambda r: r.get("day"),
            "market": mkt_state_key,
            "opp": lambda r: r.get("opp_act"),
            "own": own_state_key,
        }
        for cn, fn in conds.items():
            groups = {}
            for key in keys:
                cv = fn(games[key][s])
                groups.setdefault(cv, []).append(sub_canon(games[key][s], "all"))
            h = sum((len(v) / N) * entropy(v) for v in groups.values())
            row[f"H|{cn}"] = round(h, 4)
        step_stats[s] = row

    # write ENTROPY.csv (step-level H + conditionals)
    with open(f"{RAW}/EXP10A_ENTROPY.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(step_stats[0].keys()))
        w.writeheader()
        for s in range(n_steps):
            w.writerow(step_stats[s])

    # BEHAVIOR.csv: per-game aggregate + stability vs bank
    from collections import Counter
    behavior = []
    for key in keys:
        recs = games[key]
        bank = None
        # bank not in raw; recompute from last step? raw has no bank; use tiles/money last step
        bank = recs[-1]["money"]
        agrs = []
        for s in range(n_steps):
            agrs.append(1 if sub_canon(recs[s], "all") == step_stats[s].get("agr_all", 0) else 0)
        # per-game modal agreement at each step
        agree = 0
        for s in range(n_steps):
            modal = Counter(sub_canon(games[k][s], "all") for k in keys).most_common(1)[0][0]
            if sub_canon(recs[s], "all") == modal:
                agree += 1
        behavior.append({"seed": key[0], "seat": key[1], "bank": bank,
                         "modal_agreement": round(agree / n_steps, 4)})
    with open(f"{RAW}/EXP10A_BEHAVIOR.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["seed", "seat", "bank", "modal_agreement"])
        w.writeheader()
        for b in sorted(behavior, key=lambda x: (x["seed"], x["seat"])):
            w.writerow(b)

    # backbone + entropy summaries
    backbone = sum(1 for s in range(n_steps) if step_stats[s]["backbone_all"]) / n_steps
    hs = [step_stats[s]["H_all"] for s in range(n_steps)]
    hs_sorted = sorted(hs)
    dyn = [s for s in range(n_steps) if hs[s] > 0.5]
    # day segments
    seg = {}
    for s in range(n_steps):
        d = s // 24
        seg.setdefault(d // 5, []).append(step_stats[s]["backbone_all"])
    by_day = {f"Day {i*5+1}-{min(30,(i+1)*5)}": round(sum(v) / len(v), 3) for i, v in sorted(seg.items())}

    # DIVERGENCE.csv: seed pairs (same seat) first divergence + cause + episodes
    div_rows = []
    first_dist = []
    ep_lens = []
    causes = Counter()
    seats = (0, 1)
    for seat in seats:
        sk = sorted([k for k in keys if k[1] == seat])
        for i in range(len(sk)):
            for j in range(i + 1, len(sk)):
                A, B = sk[i], sk[j]
                diff_steps = [s for s in range(n_steps)
                              if sub_canon(games[A][s], "all") != sub_canon(games[B][s], "all")]
                if not diff_steps:
                    first_dist.append(None)
                    continue
                fd = diff_steps[0]
                first_dist.append(fd)
                # cause classification (pre-registered priority)
                cause = "UNKNOWN"
                recA, recB = games[A][fd], games[B][fd]
                if tuple(recA.get("shops") or ()) != tuple(recB.get("shops") or ()):
                    cause = "SHOP"
                elif mkt_state_key(recA) != mkt_state_key(recB):
                    cause = "MARKET"
                elif own_state_key(recA) != own_state_key(recB):
                    cause = "OWN_STATE"
                elif recA.get("opp_act") != recB.get("opp_act"):
                    cause = "OPPONENT"
                causes[cause] += 1
                div_rows.append({"seat": seat, "seedA": A[0], "seedB": B[0],
                                 "first_divergence": fd, "day": recA.get("day"),
                                 "cause": cause,
                                 "actionA": sub_canon(recA, "all"),
                                 "actionB": sub_canon(recB, "all"),
                                 "n_diff": len(diff_steps)})
                # divergence episodes
                if diff_steps:
                    runs = []
                    cur = [diff_steps[0]]
                    for x in diff_steps[1:]:
                        if x == cur[-1] + 1:
                            cur.append(x)
                        else:
                            runs.append(len(cur))
                            cur = [x]
                    runs.append(len(cur))
                    ep_lens.extend(runs)
    with open(f"{RAW}/EXP10A_DIVERGENCE.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["seat", "seedA", "seedB", "first_divergence",
                                          "day", "cause", "actionA", "actionB", "n_diff"])
        w.writeheader()
        for r in sorted(div_rows, key=lambda x: (x["seat"], x["seedA"], x["seedB"])):
            w.writerow(r)

    # summary print
    print(f"games={N} 40/40 | steps={n_steps}")
    print(f"BACKBONE_RATIO(all) = {backbone:.4f}")
    print(f"dynamic points (>0.5 bit) = {len(dyn)}/720 = {len(dyn)/720:.4f}")
    for t in (0.25, 0.5, 0.75, 1.0):
        print(f"  threshold {t}: {sum(1 for h in hs if h > t)} steps")
    print(f"H mean {sum(hs)/len(hs):.3f} median {hs_sorted[len(hs)//2]:.3f} "
          f"p90 {hs_sorted[int(len(hs)*0.9)]:.3f} max {max(hs):.3f}")
    print("backbone by day:", by_day)
    fd_ok = [x for x in first_dist if x is not None]
    print(f"seed-pairs={len(first_dist)} first-divergence: "
          f"median {sorted(fd_ok)[len(fd_ok)//2]} p90 {sorted(fd_ok)[int(len(fd_ok)*0.9)]} "
          f"max {max(fd_ok)} | 完全一致 pairs: {first_dist.count(None)}")
    print("causes:", dict(causes))
    if ep_lens:
        print(f"divergence episodes n={len(ep_lens)} median {sorted(ep_lens)[len(ep_lens)//2]} "
              f"p90 {sorted(ep_lens)[int(len(ep_lens)*0.9)]} longest {max(ep_lens)}")
    # stability vs bank
    import statistics
    banks = [b["bank"] for b in behavior]
    ags = [b["modal_agreement"] for b in behavior]
    if len(set(ags)) > 1:
        mb, ma = statistics.mean(banks), statistics.mean(ags)
        num = sum((x - mb) * (y - ma) for x, y in zip(banks, ags))
        den = math.sqrt(sum((x - mb) ** 2 for x in banks) * sum((y - ma) ** 2 for y in ags))
        print(f"stability-vs-bank Pearson r = {num / den if den else 0:.3f}")

    # sequence-level similarity: Levenshtein / LCP / LCS / common runs (same seat pairs)
    def lev(a, b):
        n, m = len(a), len(b)
        prev = list(range(m + 1))
        for i in range(1, n + 1):
            cur = [i] + [0] * m
            for j in range(1, m + 1):
                cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] != b[j - 1]))
            prev = cur
        return prev[m]

    def lcs_len(a, b):
        n, m = len(a), len(b)
        dp = [[0] * (m + 1) for _ in range(2)]
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                dp[1][j] = dp[0][j - 1] + 1 if a[i - 1] == b[j - 1] else max(dp[0][j], dp[1][j - 1])
            dp[0] = dp[1][:]
        return dp[1][m]

    seq_sim = []
    for seat in seats:
        sk = sorted([k for k in keys if k[1] == seat])
        for i in range(len(sk)):
            for j in range(i + 1, len(sk)):
                A, B = sk[i], sk[j]
                ca = [sub_canon(games[A][s], "all") for s in range(n_steps)]
                cb = [sub_canon(games[B][s], "all") for s in range(n_steps)]
                lcp = 0
                while lcp < n_steps and ca[lcp] == cb[lcp]:
                    lcp += 1
                lcsf = 0
                while lcsf < n_steps and ca[n_steps - 1 - lcsf] == cb[n_steps - 1 - lcsf]:
                    lcsf += 1
                d = lev(ca, cb)
                lc = lcs_len(ca, cb)
                seq_sim.append({"seat": seat, "seedA": A[0], "seedB": B[0],
                                "lev": d, "lev_norm": round(d / n_steps, 4),
                                "lcp": lcp, "lcs_suffix": lcsf, "lcs": lc})
    with open(f"{RAW}/EXP10A_SEQUENCE.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["seat", "seedA", "seedB", "lev", "lev_norm",
                                          "lcp", "lcs_suffix", "lcs"])
        w.writeheader()
        for r in sorted(seq_sim, key=lambda x: (x["seat"], x["seedA"], x["seedB"])):
            w.writerow(r)
    if seq_sim:
        ln = sorted(r["lev_norm"] for r in seq_sim)
        lc = sorted(r["lcp"] for r in seq_sim)
        print(f"seq-sim pairs={len(seq_sim)} lev_norm median {ln[len(ln)//2]:.4f} "
              f"max {ln[-1]:.4f} | LCP median {lc[len(lc)//2]} max {max(lc)}")


if __name__ == "__main__":
    main()
