# -*- coding: utf-8 -*-
"""P70c: reconstruct 2820 V44+layers agent from notebook cells."""
from __future__ import annotations

import base64
import gzip
import hashlib
import importlib.util
import io
import json
import re
import sys
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

NB = ROOT / "_external" / "p70_learning_nb" / "kaggriculture-2820-score.ipynb"
OUT = ROOT / "_external" / "p70b_main" / "v44y_2820_main.py"
FINN = ROOT / "reference_agents" / "fallow_finn.py"
ALPEREN = ROOT / "_external" / "p51_extracted2" / "kaggriculture_metacounter_r1_scored_agent.py"

LAYER_FORMAT = {
    "layer1_preguard": ("\n", 1, 2),
    "layer2_lockstep": ("\r\n", 1, 1),
    "layer3_cadence": ("\n", 2, 1),
    "layer4_yarnherd": ("\r\n", 1, 1),
}


def play_wrap(inner):
    n = getattr(getattr(inner, "__code__", None), "co_argcount", 2)
    if n <= 1:
        def agent(obs):
            return inner(obs)
    else:
        def agent(obs, configuration=None):
            return inner(obs, configuration)
    return agent


def main():
    nb = json.loads(NB.read_text(encoding="utf-8"))
    # decode V44 base
    src3 = "".join(nb["cells"][3].get("source") or [])
    m = re.search(r"V44_GZ_B64\s*=\s*\((.*?)\)", src3, flags=re.S)
    if not m:
        print("no V44 blob")
        return
    b64 = "".join(re.findall(r"[\"']([^\"']+)[\"']", m.group(1)))
    v44 = gzip.decompress(base64.b64decode(b64))
    print("v44 bytes", len(v44), "has agent", b"def agent" in v44)

    # extract layers
    layers = {}
    for i, c in enumerate(nb["cells"]):
        if c.get("cell_type") != "code":
            continue
        src = "".join(c.get("source") or [])
        m = re.match(r"^%%writefile\s+(build/)?(layer\d+_\w+)\.py\n", src)
        if m:
            name = m.group(2)
            body = re.sub(r"^%%writefile[^\n]*\n", "", src)
            layers[name] = body
            print("layer", name, "bytes", len(body))

    names = ["layer1_preguard", "layer2_lockstep", "layer3_cadence", "layer4_yarnherd"]
    source = v44
    for name in names:
        if name not in layers:
            print("missing", name)
            continue
        newline, lead, trail = LAYER_FORMAT[name]
        text = layers[name].replace("\r", "").strip("\n")
        part = ("\n" * lead + text + "\n" * trail).replace("\n", newline).encode()
        source += part
        print("append", name, len(part))

    sha = hashlib.sha256(source).hexdigest()
    print("sha256", sha)
    print("expected four-layer fa9e47d81de5020847c1dbc7ca10d058b227be66deea7c019040fb12a1d99f19")
    OUT.write_bytes(source)
    print("wrote", OUT, len(source))

    # eval
    spec = importlib.util.spec_from_file_location("v44y", str(OUT))
    mod = importlib.util.module_from_spec(spec)
    with redirect_stdout(io.StringIO()):
        spec.loader.exec_module(mod)
    fn = mod.agent if hasattr(mod, "agent") else mod.build_agent({})

    def run(a0, a1, seed):
        env = make("kaggriculture", debug=False)
        env.configuration["episodeSteps"] = 720
        env.info = {"seed": int(seed)}
        env.run([play_wrap(a0), play_wrap(a1)])
        f = env.steps[-1]
        return float(f[0]["observation"]["farms"][0]["money"]), float(f[1]["observation"]["farms"][1]["money"])

    banks = []
    for seed in (1, 2, 3):
        b, _ = run(fn, load_finn(), seed)
        banks.append(b)
        print("finn", seed, b)
    print("finn mean", sum(banks) / 3)

    w = d = l = 0
    for seed in (1, 2, 3):
        a0, a1 = run(fn, load_alp(), seed)
        b0, b1 = run(load_alp(), fn, seed)
        our = (a0 + b1) / 2
        theirs = (a1 + b0) / 2
        if our > theirs + 1:
            w += 1
        elif theirs > our + 1:
            l += 1
        else:
            d += 1
        print("alp", seed, our, theirs)
    print("vs alperen", w, d, l)


def load_finn():
    return load_quiet(FINN, "f70c")


def load_alp():
    return load_quiet(ALPEREN, "a70c")


def load_quiet(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    with redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


if __name__ == "__main__":
    main()
