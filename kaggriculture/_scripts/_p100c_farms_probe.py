# -*- coding: utf-8 -*-
"""Dump farms[0]/farms[1] structure for opponent fingerprint."""
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


def load_any(path, tag):
    return p79.load_quiet(path, tag)


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


def farm_brief(f):
    if not isinstance(f, dict):
        return {"type": str(type(f))}
    out = {"keys": sorted(f.keys())}
    for k in ("money", "name", "player"):
        if k in f:
            out[k] = f[k]
    tiles = f.get("tiles")
    if isinstance(tiles, list):
        kinds = {}
        crops = {}
        for row in tiles:
            if not isinstance(row, list):
                continue
            for cell in row:
                if isinstance(cell, dict):
                    kinds[cell.get("kind")] = kinds.get(cell.get("kind"), 0) + 1
                    if cell.get("crop"):
                        crops[cell.get("crop")] = crops.get(cell.get("crop"), 0) + 1
        out["tile_kinds"] = kinds
        out["crops"] = crops
    for k in f:
        if k not in out and k not in ("tiles",):
            v = f[k]
            if isinstance(v, (int, float, str, bool)) or v is None:
                out[k] = v
            elif isinstance(v, dict):
                out[k + "_keys"] = sorted(v.keys())[:20]
            elif isinstance(v, list):
                out[k + "_len"] = len(v)
    return out


def spy(parent, my_id="x"):
    def agent(obs, configuration=None):
        step = (obs or {}).get("step")
        if step in (0, 48, 120, 300, 600, 680) and len(snaps) < 12:
            farms = (obs or {}).get("farms") or []
            rec = {
                "step": step,
                "player": (obs or {}).get("player"),
                "n_farms": len(farms),
                "farms": [farm_brief(f) for f in farms],
                "market": (obs or {}).get("market"),
                "private": (obs or {}).get("private"),
            }
            snaps.append(rec)
        return parent(obs, configuration)

    return agent


def main():
    c = spy(load_mv("mv"))
    o = spy(load_any(THOMAS, "th"))
    p79.run(c, o, 1)
    p79.run(o, c, 2)
    out = Path(r"D:\桌面\Kaggle\kaggriculture\_research\p100_farms_structure.json")
    out.write_text(json.dumps(snaps, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(json.dumps(snaps[:4], indent=2, ensure_ascii=False, default=str)[:6000])
    print("wrote", out, "n", len(snaps))


if __name__ == "__main__":
    main()
