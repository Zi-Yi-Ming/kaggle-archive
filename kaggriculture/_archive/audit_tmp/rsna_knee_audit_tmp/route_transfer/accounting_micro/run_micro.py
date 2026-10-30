"""EXP-8 A3: micro-validation of the executed-ledger reconstruction.

Crafted one-shot agents issue targeted market orders; the executed ledger is
reconstructed with executed_ledger.replay_game and checked against the
engine's observable state (money/shed/seeds) and the case's expected
executed quantities. Every case requires reconciliation_error == 0 and
full step validation (valid == total).

Cases (per the A3 spec):
  1 normal BUY (affordable BUY_SEED)
  2 no-cash BUY (order dies at the first unaffordable unit -> partial)
  3 no-stock SELL (empty shed -> all units fail)
  4 partial BUY (BUY_ANIMAL beyond money -> 7/10 executed)
  5 partial SELL (SELL beyond shed stock -> 8/10 executed)
  6 multi-unit BUY (two animal orders in one queue)
  7 multi-unit SELL (two sell orders in one queue)
  8 BUY+SELL same step
  9 multi-order interleaving (closer_cleo vs closer_cleo)
  10 V2 route-B misalignment (tape B vs current game state; mass order
      failures must reconcile exactly)
"""
import importlib.util
import json
import sys

sys.path.insert(0, "kaggriculture")
sys.path.insert(0, "_audit_tmp/route_transfer")
import _pm_pool as P
import executed_ledger as EL
from kaggle_environments import make


def pass_agent(obs, config=None):
    return {"farmer": ["PASS"], "hands": [], "market": []}


def make_crafted(market_orders, step=1):
    def ag(obs, config=None):
        s = int(obs.get("step", 0) or 0)
        if s == step:
            return {"farmer": ["PASS"], "hands": [], "market": list(market_orders)}
        return {"farmer": ["PASS"], "hands": [], "market": []}
    return ag


def run_game(agents, seed=7):
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info["seed"] = seed
    env.run(agents)
    return env.steps


def check(steps, seat, expect=None, label=""):
    agg, valid, n, mism = EL.replay_game(steps, seat)
    final = steps[-1][seat]["observation"]["farms"][seat]["money"]
    rev = agg["SELL"][1]
    cost = sum(agg[t][1] for t in ("BUY_SEED", "BUY_PRODUCT", "BUY_ANIMAL", "HIRE", "BUY_LAND"))
    recon = final - (EL.INITIAL_BANK + rev - cost)
    ok = (abs(recon) < 0.005) and (valid == n)
    exp_ok = True
    exp_note = ""
    if expect is not None:
        for t, q in expect.items():
            if agg[t][0] != q:
                exp_ok = False
                exp_note = f" 期望 {t}={q} 实际 {agg[t][0]}"
    return {"label": label, "valid": f"{valid}/{n}", "recon": round(recon, 3),
            "exec": {k: v[0] for k, v in agg.items() if k != "issued"},
            "ok": ok, "exp_ok": exp_ok, "exp_note": exp_note, "mism": mism[:1]}


def main():
    out = []
    # Case 1: affordable BUY_SEED WHEAT x10 (100 <= 3000)
    s = run_game([make_crafted([["BUY_SEED", "WHEAT", 10]]), pass_agent])
    out.append(check(s, 0, {"BUY_SEED": 10}, "1 正常BUY"))
    # Case 2+4: BUY_SEED MELON x50 (4000 > 3000 -> partial at unit 38) & BUY_ANIMAL COW x10 (7/10)
    s = run_game([make_crafted([["BUY_SEED", "MELON", 50]]), pass_agent])
    out.append(check(s, 0, {"BUY_SEED": 37}, "2 无现金BUY(部分37/50)"))
    s = run_game([make_crafted([["BUY_ANIMAL", "COW", 10]]), pass_agent])
    out.append(check(s, 0, {"BUY_ANIMAL": 7}, "4 部分BUY(7/10)"))
    # Case 3: no-stock SELL (empty shed -> 0)
    s = run_game([make_crafted([["SELL", "WHEAT", 10]]), pass_agent])
    out.append(check(s, 0, {"SELL": 0}, "3 无库存SELL"))
    # Case 5: partial SELL — buy 8 WHEAT (BUY_PRODUCT -> shed) at step 1, sell 10 at step 2
    def sell_after_buy(obs, config=None):
        st = int(obs.get("step", 0) or 0)
        if st == 1:
            return {"farmer": ["PASS"], "hands": [], "market": [["BUY_PRODUCT", "WHEAT", 8]]}
        if st == 2:
            return {"farmer": ["PASS"], "hands": [], "market": [["SELL", "WHEAT", 10]]}
        return {"farmer": ["PASS"], "hands": [], "market": []}
    s = run_game([sell_after_buy, pass_agent])
    out.append(check(s, 0, {"BUY_PRODUCT": 8, "SELL": 8}, "5 部分SELL(8/10)"))
    # Case 6: multi-unit BUY in one queue
    s = run_game([make_crafted([["BUY_ANIMAL", "COW", 2], ["BUY_ANIMAL", "SHEEP", 1]]), pass_agent])
    out.append(check(s, 0, {"BUY_ANIMAL": 3}, "6 多unit BUY"))
    # Case 7: multi-unit SELL (needs stock: buy products then sell two items)
    def sell_two(obs, config=None):
        st = int(obs.get("step", 0) or 0)
        if st == 1:
            return {"farmer": ["PASS"], "hands": [], "market": [["BUY_PRODUCT", "WHEAT", 3], ["BUY_PRODUCT", "FERTILIZER", 2]]}
        if st == 2:
            return {"farmer": ["PASS"], "hands": [], "market": [["SELL", "WHEAT", 3], ["SELL", "FERTILIZER", 2]]}
        return {"farmer": ["PASS"], "hands": [], "market": []}
    s = run_game([sell_two, pass_agent])
    out.append(check(s, 0, {"SELL": 5}, "7 多unit SELL"))
    # Case 8: BUY+SELL same step
    def buy_sell(obs, config=None):
        st = int(obs.get("step", 0) or 0)
        if st == 1:
            return {"farmer": ["PASS"], "hands": [], "market": [["BUY_PRODUCT", "WHEAT", 4]]}
        if st == 2:
            return {"farmer": ["PASS"], "hands": [], "market": [["SELL", "WHEAT", 4], ["BUY_PRODUCT", "CARROT", 3]]}
        return {"farmer": ["PASS"], "hands": [], "market": []}
    s = run_game([buy_sell, pass_agent])
    out.append(check(s, 0, {"SELL": 4, "BUY_PRODUCT": 4}, "8 BUY+SELL同步"))
    # Case 9: interleaving — closer_cleo vs closer_cleo (both seats)
    s = run_game([P.load_agent("closer_cleo"), P.load_agent("closer_cleo")])
    out.append(check(s, 0, None, "9 interleaving seat0"))
    out.append(check(s, 1, None, "9 interleaving seat1"))
    # Case 10: V2 route-B misalignment vs closer_cleo
    spec = importlib.util.spec_from_file_location("v2", "_audit_tmp/route_transfer/variants/v11e_multitape_router.py")
    V2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(V2)
    b_seed = None
    for sd in range(1, 17):
        s = run_game([pass_agent, V2.agent], seed=sd)
        if V2._LOCK[1] == "B":
            b_seed = sd
            break
    s = run_game([P.load_agent("closer_cleo"), V2.agent], seed=b_seed)
    out.append(check(s, 1, None, f"10 V2-B错位(seed {b_seed})"))
    return out


if __name__ == "__main__":
    results = main()
    for r in results:
        flag = "PASS" if (r["ok"] and r["exp_ok"]) else "FAIL"
        print(f"[{flag}] {r['label']}: 校验 {r['valid']} | recon {r['recon']} | exec {r['exec']}{r['exp_note']}{' | mism '+str(r['mism']) if r['mism'] else ''}")
    with open("_audit_tmp/route_transfer/accounting_micro/micro_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    print("DONE -> accounting_micro/micro_results.json")
