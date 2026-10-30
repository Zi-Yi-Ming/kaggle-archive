# -*- coding: utf-8 -*-
"""Inspect observation structure mid-game for opponent fingerprinting."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "p79", r"D:\桌面\Kaggle\kaggriculture\_scripts\_p79_mass_gate_vs_thomas.py"
)
p79 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p79)

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
METAV4 = PROJ / "_push_metav4_v13" / "main.py"
THOMAS = PROJ / "_push_thomas_2945" / "main.py"


def load_mv(tag: str):
    code = METAV4.read_text(encoding="utf-8", errors="ignore")
    ns = {"__name__": tag, "__file__": str(METAV4), "__builtins__": __builtins__}
    exec(compile(code, str(METAV4), "exec"), ns)
    fn = ns.get("agent")
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)

    def agent(obs, configuration=None):
        return fn(obs) if n <= 1 else fn(obs, configuration)

    return agent


snaps = []


def spy(parent):
    def agent(obs, configuration=None):
        step = (obs or {}).get("step")
        if step in (0, 24, 96, 200, 400, 600, 648, 700) and len(snaps) < 20:
            def brief(o):
                if not isinstance(o, dict):
                    return str(type(o))
                return {
                    "keys": sorted(o.keys()),
                    "step": o.get("step"),
                    "player": (o.get("info") or {}).get("player") if isinstance(o.get("info"), dict) else None,
                    "private_keys": sorted((o.get("private") or {}).keys()) if isinstance(o.get("private"), dict) else None,
                    "market_keys": sorted((o.get("market") or {}).keys()) if isinstance(o.get("market"), dict) else type(o.get("market")).__name__,
                    "info_keys": sorted((o.get("info") or {}).keys()) if isinstance(o.get("info"), dict) else None,
                }
            snaps.append({"step": step, "brief": brief(obs)})
            # dig one level
            for k, v in (obs or {}).items():
                if isinstance(v, dict):
                    snaps[-1][f"_{k}"] = sorted(v.keys())[:30]
                elif isinstance(v, list) and v:
                    snaps[-1][f"_{k}_list0"] = str(v[0])[:120]
        return parent(obs, configuration)

    return agent


def main():
    c = spy(load_mv("mv"))
    o = spy(load_mv("th")) if False else spy(p79.load_quiet(THOMAS, "th"))
    # run a few games to collect
    for seed in (1, 2):
        p79.run(c, o, seed)
    print(json.dumps(snaps, indent=2, ensure_ascii=False, default=str)[:8000])
    Path(r"D:\桌面\Kaggle\kaggriculture\_research\p100_obs_structure.json").write_text(
        json.dumps(snaps, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
