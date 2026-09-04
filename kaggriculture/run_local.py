# -*- coding: utf-8 -*-
"""本地验证: 让提交 agent 打满 720 回合 vs 随机对手,校验 action 合法性与分数。"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import kaggriculture_submission as sub  # 提交物(纯 stdlib,无依赖)
from local_sim import LocalKaggricultureEnv


def random_agent(obs):
    """什么都不做的随机对手(偶尔 PASS)。"""
    return {"farmer": ["PASS"], "hands": [], "market": []}


def idle_agent(obs):
    """纯空转对手,用来对照"什么都不做"的下限分数。"""
    return {"farmer": ["PASS"], "hands": [], "market": []}


def main():
    seed = 42
    env = LocalKaggricultureEnv(seed=seed, n_players=2)
    players = [sub.agent, idle_agent]
    invalid = 0
    act_count = {"market": 0, "farmer_act": 0}
    while not env.done:
        actions = [players[p](env.observe(p)) for p in range(2)]
        for p, a in enumerate(actions):
            if not isinstance(a, dict) or not isinstance(a.get("farmer"), list) \
                    or not isinstance(a.get("market"), list):
                invalid += 1
                print(f"[校验] turn {env.turn} player {p} 非法 action: {a!r}")
        act_count["market"] += sum(len(a.get("market") or []) for a in actions)
        act_count["farmer_act"] += sum(
            1 for a in actions if a.get("farmer") and a["farmer"][0] != "PASS")
        env.step(actions)

    s_agent = env.score(0)
    s_idle = env.score(1)
    print(f"回合数      : {env.turn} (期望 {24 * 30} = 720)")
    print(f"非法 action : {invalid}")
    print(f"市场操作次数: {act_count['market']}  farmer 有效行动: {act_count['farmer_act']}")
    print(f"策略 agent  : {s_agent}")
    print(f"空转对手    : {s_idle}")

    assert env.turn == 24 * 30, "应跑满 720 回合"
    assert invalid == 0, "出现非法 action"
    assert s_agent > s_idle, "策略 agent 应显著高于空转对手"
    print("本地验证通过 ✅")


if __name__ == "__main__":
    main()
