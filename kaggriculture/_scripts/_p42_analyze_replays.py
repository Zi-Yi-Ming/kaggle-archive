# -*- coding: utf-8 -*-
"""P42 replay differential: same R2, different live opponents."""
from __future__ import annotations

import csv
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
REP = ROOT / "_external" / "p42_replays"


def load_corpus():
    meta = json.loads((REP / "meta.json").read_text(encoding="utf-8"))
    rows = []
    for m in meta:
        path = Path(m["path"])
        if not path.exists():
            continue
        d = json.loads(path.read_text(encoding="utf-8"))
        steps = d.get("steps") or []
        seat = int(m.get("our_seat") or 0)
        opp_seat = 1 - seat
        our_actions = []
        opp_snap = []
        for i, step in enumerate(steps):
            if not isinstance(step, list) or len(step) <= max(seat, opp_seat):
                our_actions.append({})
                opp_snap.append({})
                continue
            a = step[seat].get("action") or {}
            our_actions.append(a)
            oobs = step[opp_seat].get("observation") or {}
            ofarm = {}
            farms = oobs.get("farms") or []
            if opp_seat < len(farms):
                ofarm = farms[opp_seat] or {}
            private = oobs.get("private") or {}
            # opponent private is only visible to that player; in replay each
            # agent slot has its own observation. Use that slot's farm + shed if present.
            shed = dict(private.get("shed") or {})
            opp_snap.append({
                "money": float(ofarm.get("money") or 0),
                "hands": len(ofarm.get("hands") or []),
                "n_shops": len((oobs.get("town") or {}).get("unlocked_shops") or []),
                "shed_total": sum(int(v or 0) for v in shed.values()) if shed else None,
            })
        rows.append({
            "episode_id": m["episode_id"],
            "opp_team": m["opp_team"],
            "our_seat": seat,
            "our_reward": m.get("our_reward"),
            "opp_reward": m.get("opp_reward"),
            "seed_info": (d.get("info") or {}).get("seed"),
            "actions": our_actions,
            "opp_snap": opp_snap,
        })
    return rows


def action_key(a):
    return json.dumps(
        {"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
        sort_keys=True, default=str,
    )


def market_key(a):
    return json.dumps(a.get("market"), sort_keys=True, default=str)


def worker_key(a):
    return json.dumps({"f": a.get("farmer"), "h": a.get("hands")}, sort_keys=True, default=str)


def extract_sells(a, step):
    out = []
    for o in a.get("market") or []:
        if o and o[0] == "SELL" and len(o) >= 3:
            out.append((step, o[1], int(o[2])))
    return out


def first_divergence(a_keys, b_keys):
    n = min(len(a_keys), len(b_keys))
    for i in range(n):
        if a_keys[i] != b_keys[i]:
            return i
    return None


def classify_div(a, b, step):
    """What kind of first difference."""
    ma, mb = (a.get("market") or []), (b.get("market") or [])
    if json.dumps(ma, sort_keys=True, default=str) != json.dumps(mb, sort_keys=True, default=str):
        # sell vs buy vs hire
        def kinds(ms):
            ks = []
            for o in ms:
                if not o:
                    continue
                ks.append(o[0])
            return set(ks)
        ka, kb = kinds(ma), kinds(mb)
        if "SELL" in ka or "SELL" in kb:
            return "SELL"
        if ka != kb:
            return "BUY"
        return "MARKET_QTY"
    fa, ha = a.get("farmer"), a.get("hands")
    fb, hb = b.get("farmer"), b.get("hands")
    def wops(f, hs):
        ops = []
        if f:
            ops.append(f[0] if f else "PASS")
        for h in hs or []:
            if h:
                ops.append(h[0])
        return ops
    oa, ob = wops(fa, ha), wops(fb, hb)
    for x, y in zip(oa, ob):
        if x != y:
            if x in ("PLANT", "HARVEST", "WATER", "DIG") or y in ("PLANT", "HARVEST", "WATER", "DIG"):
                return "CROP"
            if x in ("FEED", "CARE", "PLACE", "PICKUP", "COLLECT_FERTILIZER") or y in (
                "FEED", "CARE", "PLACE", "PICKUP", "COLLECT_FERTILIZER"
            ):
                return "ANIMAL"
            if x in ("NORTH", "SOUTH", "EAST", "WEST", "PASS") and y in (
                "NORTH", "SOUTH", "EAST", "WEST", "PASS"
            ):
                return "WORKER"
            return "OTHER"
    return "OTHER"


def sim_list(a, b):
    n = min(len(a), len(b))
    if n == 0:
        return 0.0
    return sum(1 for i in range(n) if a[i] == b[i]) / n


def main():
    corpus = load_corpus()
    print(f"loaded {len(corpus)} replays", flush=True)

    # --- corpus csv ---
    with open(ROOT / "p42_replay_corpus.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "episode_id", "opp_team", "our_seat", "our_reward", "opp_reward", "seed_info", "n_steps",
        ])
        w.writeheader()
        for r in corpus:
            w.writerow({
                "episode_id": r["episode_id"],
                "opp_team": r["opp_team"],
                "our_seat": r["our_seat"],
                "our_reward": r["our_reward"],
                "opp_reward": r["opp_reward"],
                "seed_info": r["seed_info"],
                "n_steps": len(r["actions"]),
            })

    # precompute keys
    for r in corpus:
        r["keys"] = [action_key(a) for a in r["actions"]]
        r["mkeys"] = [market_key(a) for a in r["actions"]]
        r["wkeys"] = [worker_key(a) for a in r["actions"]]
        r["sells"] = []
        for i, a in enumerate(r["actions"]):
            r["sells"].extend(extract_sells(a, i))

    # --- pairwise similarity ---
    sim_rows = []
    n = len(corpus)
    for i in range(n):
        for j in range(i + 1, n):
            A, B = corpus[i], corpus[j]
            fd = first_divergence(A["keys"], B["keys"])
            fd_m = first_divergence(A["mkeys"], B["mkeys"])
            fd_w = first_divergence(A["wkeys"], B["wkeys"])
            # prefix sims
            def pref(keys_a, keys_b, k):
                return sim_list(keys_a[:k], keys_b[:k])
            rec = {
                "ep_a": A["episode_id"], "ep_b": B["episode_id"],
                "opp_a": A["opp_team"], "opp_b": B["opp_team"],
                "same_opp": A["opp_team"] == B["opp_team"],
                "sim_full": sim_list(A["keys"], B["keys"]),
                "sim_mkt": sim_list(A["mkeys"], B["mkeys"]),
                "sim_wkr": sim_list(A["wkeys"], B["wkeys"]),
                "sim_0_72": pref(A["keys"], B["keys"], 72),
                "sim_0_144": pref(A["keys"], B["keys"], 144),
                "sim_0_216": pref(A["keys"], B["keys"], 216),
                "first_div_step": fd if fd is not None else -1,
                "first_div_day": (fd // 24) if fd is not None else -1,
                "first_div_mkt": fd_m if fd_m is not None else -1,
                "first_div_wkr": fd_w if fd_w is not None else -1,
                "div_type": classify_div(A["actions"][fd], B["actions"][fd], fd) if fd is not None else "NONE",
            }
            sim_rows.append(rec)

    fields = list(sim_rows[0].keys())
    with open(ROOT / "p42_tape_similarity.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(sim_rows)

    # --- divergence points (first div for each pair, plus same-opp pairs) ---
    div_rows = []
    for r in sim_rows:
        if r["first_div_step"] < 0:
            continue
        div_rows.append({
            "ep_a": r["ep_a"], "ep_b": r["ep_b"],
            "same_opp": r["same_opp"],
            "first_div_step": r["first_div_step"],
            "first_div_day": r["first_div_day"],
            "div_type": r["div_type"],
            "sim_full": r["sim_full"],
            "sim_0_144": r["sim_0_144"],
        })
    with open(ROOT / "p42_divergence_points.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(div_rows[0].keys()) if div_rows else ["ep_a"])
        w.writeheader()
        w.writerows(div_rows)

    # --- sell-only diffs (pairwise, sell event multiset by (item) timing) ---
    sell_rows = []
    for i in range(n):
        for j in range(i + 1, n):
            A, B = corpus[i], corpus[j]
            # align by step: sell at step t of item
            sa = defaultdict(list)  # item -> [(step, qty)]
            sb = defaultdict(list)
            for st, item, q in A["sells"]:
                sa[item].append((st, q))
            for st, item, q in B["sells"]:
                sb[item].append((st, q))
            items = set(sa) | set(sb)
            for item in sorted(items):
                ta = sa.get(item, [])
                tb = sb.get(item, [])
                # first sell step
                fa = ta[0][0] if ta else None
                fb = tb[0][0] if tb else None
                qa = sum(q for _, q in ta)
                qb = sum(q for _, q in tb)
                # timing delta of k-th sell if both exist
                timing_deltas = []
                for k in range(min(len(ta), len(tb))):
                    timing_deltas.append(ta[k][0] - tb[k][0])
                sell_rows.append({
                    "ep_a": A["episode_id"], "ep_b": B["episode_id"],
                    "same_opp": A["opp_team"] == B["opp_team"],
                    "item": item,
                    "n_sells_a": len(ta), "n_sells_b": len(tb),
                    "first_sell_step_a": fa, "first_sell_step_b": fb,
                    "first_sell_delta": (fa - fb) if (fa is not None and fb is not None) else None,
                    "qty_a": qa, "qty_b": qb,
                    "qty_delta": qa - qb,
                    "mean_timing_delta": (sum(timing_deltas) / len(timing_deltas)) if timing_deltas else None,
                })
    if sell_rows:
        with open(ROOT / "p42_sell_diff.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(sell_rows[0].keys()))
            w.writeheader()
            w.writerows(sell_rows)
    else:
        (ROOT / "p42_sell_diff.csv").write_text("NOT_AVAILABLE\n", encoding="utf-8")

    # --- opponent conditioning: does sell timing correlate with opp state? ---
    # For each replay, compute mean first-sell-step for MELON/STRAW/MILK/WOOL
    # and opp features at day 5 / day 10
    cond_rows = []
    for r in corpus:
        sells_by_item = defaultdict(list)
        for st, item, q in r["sells"]:
            sells_by_item[item].append(st)
        # opp state at fixed steps
        def opp_at(step):
            if step < len(r["opp_snap"]):
                return r["opp_snap"][step]
            return {}
        o5, o10, o144 = opp_at(5 * 24), opp_at(10 * 24), opp_at(6 * 24)
        for item in ("MELON", "STRAWBERRY", "MILK", "WOOL", "EGG", "FERTILIZER", "WHEAT"):
            ts = sells_by_item.get(item) or []
            cond_rows.append({
                "episode_id": r["episode_id"],
                "opp_team": r["opp_team"],
                "item": item,
                "n_sells": len(ts),
                "first_sell_step": ts[0] if ts else None,
                "mean_sell_step": (sum(ts) / len(ts)) if ts else None,
                "opp_money_d5": o5.get("money"),
                "opp_hands_d5": o5.get("hands"),
                "opp_shops_d6": o144.get("n_shops"),
                "opp_money_d10": o10.get("money"),
                "our_reward": r["our_reward"],
                "opp_reward": r["opp_reward"],
            })
    with open(ROOT / "p42_opponent_conditioning.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(cond_rows[0].keys()))
        w.writeheader()
        w.writerows(cond_rows)

    # ========== SUMMARY STATS ==========
    print("\n=== CORPUS ===")
    print(f"n_replays={len(corpus)} unique_opponents={len({r['opp_team'] for r in corpus})}")
    rewards = [r["our_reward"] for r in corpus if r["our_reward"] is not None]
    print(f"our_reward mean={statistics.mean(rewards):.0f} min={min(rewards)} max={max(rewards)}")
    wins = sum(1 for r in corpus if (r["our_reward"] or 0) > (r["opp_reward"] or 0))
    print(f"live W-L approx: {wins}-{len(corpus)-wins}")

    print("\n=== PAIRWISE SIMILARITY (all pairs) ===")
    fulls = [r["sim_full"] for r in sim_rows]
    mids = [r["sim_mkt"] for r in sim_rows]
    wkrs = [r["sim_wkr"] for r in sim_rows]
    print(f"sim_full  mean={statistics.mean(fulls):.4f} min={min(fulls):.4f} max={max(fulls):.4f}")
    print(f"sim_mkt   mean={statistics.mean(mids):.4f} min={min(mids):.4f}")
    print(f"sim_wkr   mean={statistics.mean(wkrs):.4f} min={min(wkrs):.4f}")
    p72 = [r["sim_0_72"] for r in sim_rows]
    p144 = [r["sim_0_144"] for r in sim_rows]
    print(f"sim_0_72  mean={statistics.mean(p72):.4f}")
    print(f"sim_0_144 mean={statistics.mean(p144):.4f}")

    same = [r for r in sim_rows if r["same_opp"]]
    diff = [r for r in sim_rows if not r["same_opp"]]
    print(f"\nsame-opponent pairs: {len(same)}")
    if same:
        print(f"  sim_full mean={statistics.mean([r['sim_full'] for r in same]):.4f}")
        print(f"  first_div median={statistics.median([r['first_div_step'] for r in same if r['first_div_step']>=0])}")
    print(f"diff-opponent pairs: {len(diff)}")
    print(f"  sim_full mean={statistics.mean([r['sim_full'] for r in diff]):.4f}")
    fds = [r["first_div_step"] for r in diff if r["first_div_step"] is not None and r["first_div_step"] >= 0]
    print(f"  first_div median={statistics.median(fds):.0f} p10={sorted(fds)[len(fds)//10]} p90={sorted(fds)[9*len(fds)//10]}")
    print(f"  first_div_day median={statistics.median([x//24 for x in fds]):.0f}")

    print("\n=== DIVERGENCE TYPE (first) ===")
    print(Counter(r["div_type"] for r in sim_rows).most_common())

    # sell timing variance across opponents
    print("\n=== SELL TIMING VARIANCE (first sell by item) ===")
    by_item = defaultdict(list)
    for r in cond_rows:
        if r["first_sell_step"] is not None:
            by_item[r["item"]].append(r["first_sell_step"])
    for item, ts in sorted(by_item.items(), key=lambda x: -len(x[1])):
        if len(ts) >= 3:
            print(f"  {item:12s} n={len(ts):2d} first_sell step mean={statistics.mean(ts):.1f} "
                  f"stdev={statistics.pstdev(ts):.1f} range={min(ts)}-{max(ts)}")

    # correlation: first sell MELON vs opp money d5/d10
    print("\n=== OPP STATE vs FIRST MELON SELL ===")
    pairs = [(r["opp_money_d5"], r["first_sell_step"]) for r in cond_rows
             if r["item"] == "MELON" and r["first_sell_step"] is not None and r["opp_money_d5"] is not None]
    if len(pairs) >= 5:
        xs = [p[0] for p in pairs]
        ys = [p[1] for p in pairs]
        # pearson
        mx, my = statistics.mean(xs), statistics.mean(ys)
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        den = (sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)) ** 0.5
        corr = num / den if den else 0
        print(f"  n={len(pairs)} pearson(opp_money_d5, first_melon_sell)={corr:.3f}")

    pairs2 = [(r["opp_money_d10"], r["first_sell_step"]) for r in cond_rows
              if r["item"] == "MELON" and r["first_sell_step"] is not None and r["opp_money_d10"] is not None]
    if len(pairs2) >= 5:
        xs = [p[0] for p in pairs2]
        ys = [p[1] for p in pairs2]
        mx, my = statistics.mean(xs), statistics.mean(ys)
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        den = (sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)) ** 0.5
        corr = num / den if den else 0
        print(f"  n={len(pairs2)} pearson(opp_money_d10, first_melon_sell)={corr:.3f}")

    # seed uniqueness
    seeds = [r["seed_info"] for r in corpus]
    print(f"\n=== SEEDS ===")
    print(f"unique env.info seeds: {len(set(seeds))} / {len(seeds)}")

    print("\nwrote p42_replay_corpus.csv p42_tape_similarity.csv "
          "p42_divergence_points.csv p42_sell_diff.csv p42_opponent_conditioning.csv")


if __name__ == "__main__":
    main()
