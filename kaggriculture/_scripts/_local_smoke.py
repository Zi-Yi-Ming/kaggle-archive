# -*- coding: utf-8 -*-
"""本机冒烟：各跑 1 局，验证两套 agent 都能跑通，并粗略看耗时。"""
import os, sys, time
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
sys.path.insert(0, os.path.join(BASE, "_kaggle_nb", "code"))
from kaggle_environments import make
import importlib.util

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent

sub = load("sub", "kaggriculture/kaggriculture_submission.py")
v11e = load("v11e", "_kaggle_nb/code/v11e_agent.py")
cleo = load("cleo", "_kaggle_nb/code/closer_cleo.py")

pairs = [
    ("sub","idle"),
    ("v11e","cleo"),
    ("v11e","sub"),
    ("cleo","sub"),
]
for a_name,b_name in pairs:
    a = sub if a_name=="sub" else (v11e if a_name=="v11e" else cleo)
    b = sub if b_name=="idle" else (v11e if b_name=="v11e" else cleo)
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = 7
    t0=time.time(); env.run([a,b]); dt=time.time()-t0
    last=env.steps[-1]
    print(a_name, "vs", b_name, "steps=", len(env.steps), "sec=", round(dt,2), "bank=", round(last[0]["observation"]["farms"][0]["money"],2), round(last[1]["observation"]["farms"][1]["money"],2))
