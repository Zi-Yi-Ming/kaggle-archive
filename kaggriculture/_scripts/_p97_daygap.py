# -*- coding: utf-8 -*-
"""P97a day-gap autopsy: Fieldcraft win-seed vs Metav4 money ledger."""
from __future__ import annotations

import importlib.util
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "p79", r"D:\桌面\Kaggle\kaggriculture\_scripts\_p79_mass_gate_vs_thomas.py"
)
p79 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p79)

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
METAV4 = PROJ / "_push_metav4_v13" / "main.py"
pkg = PROJ / "_external/scan_p95_again/extracted/fieldcraft_pkg"
main_py = pkg / "main.py"
OUT = PROJ / "_research/p97_daygap_fieldcraft.json"
sys.path.insert(0, str(pkg))

STEPS = list(range(0, 720, 12)) + [216, 240, 264, 288, 336, 384, 432, 480, 528, 576, 624, 672, 696, 718]


def load_fc(tag):
    code = main_py.read_text(encoding="utf-8", errors="ignore")
    ns = {"__name__": tag, "__file__": str(main_py), "__builtins__": __builtins__}
    with redirect_stdout(io.StringIO()):
        exec(compile(code, str(main_py), "exec"), ns)
    fn = ns.get("agent")
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)

    def agent(obs, configuration=None):
        return fn(obs) if n <= 1 else fn(obs, configuration)

    return agent


def load_mv(tag):
    code = METAV4.read_text(encoding="utf-8", errors="ignore")
    ns = {"__name__": tag, "__file__": str(METAV4), "__builtins__": __builtins__}
    with redirect_stdout(io.StringIO()):
        exec(compile(code, str(METAV4), "exec"), ns)
    fn = ns.get("agent")
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)

    def agent(obs, configuration=None):
        return fn(obs) if n <= 1 else fn(obs, configuration)

    return agent, ns


def run_trace(a_fc, a_mv, seed, fc_seat0=True):
    env = p79.make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    trace = {0: [], 1: []}

    def wrap(fn, seat, name):
        n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)

        def agent(obs, configuration=None):
            st = int((obs or {}).get("step", -1))
            if st in set(STEPS) or st % 24 == 23:
                try:
                    farm = obs["farms"][seat]
                    opp = obs["farms"][1 - seat]
                    priv = obs.get("private") or {}
                    shed = priv.get("shed") or {}
                    plants = animals = 0
                    for row in farm.get("tiles") or []:
                        for t in row:
                            if isinstance(t, dict):
                                if t.get("crop"):
                                    plants += 1
                                if t.get("animal"):
                                    animals += 1
                    mkt = obs.get("market") or {}
                    trace[seat].append({
                        "step": st,
                        "money": float(farm.get("money") or 0),
                        "opp": float(opp.get("money") or 0),
                        "gap": float(farm.get("money") or 0) - float(opp.get("money") or 0),
                        "hands": len(farm.get("hands") or []),
                        "plants": plants,
                        "animals": animals,
                        "shed": sum(int(v or 0) for v in shed.values()),
                        "wheat_px": int((mkt.get("prices") or {}).get("WHEAT", 0) or 0),
                        "milk_px": int((mkt.get("prices") or {}).get("MILK", 0) or 0),
                        "wool_px": int((mkt.get("prices") or {}).get("WOOL", 0) or 0),
                    })
                except Exception:
                    pass
            return fn(obs) if n <= 1 else fn(obs, configuration)

        return agent

    if fc_seat0:
        env.run([wrap(a_fc, 0, "fc"), wrap(a_mv, 1, "mv")])
        f = env.steps[-1]
        return float(f[0]["observation"]["farms"][0]["money"]), float(f[1]["observation"]["farms"][1]["money"]), trace
    env.run([wrap(a_mv, 0, "mv"), wrap(a_fc, 1, "fc")])
    f = env.steps[-1]
    return float(f[1]["observation"]["farms"][1]["money"]), float(f[0]["observation"]["farms"][0]["money"]), trace


def main():
    results = []
    for seed, seat0, expect in [(1, True, "fc_win"), (2, True, "fc_lose"), (7, True, "fc_win")]:
        print(f"\n==== seed={seed} seat0={seat0} expect={expect} ====", flush=True)
        a_fc = load_fc(f"fc_{seed}")
        a_mv, _ = load_mv(f"mv_{seed}")
        cb, ob, trace = run_trace(a_fc, a_mv, seed, fc_seat0=seat0)
        fc_seat = 0 if seat0 else 1
        rows = trace[fc_seat]
        print(f"final fc={cb:.0f} mv={ob:.0f} margin={cb-ob:.0f}", flush=True)
        print("step  day  fc$     mv$     gap     hands pl an shed", flush=True)
        for r in rows:
            if r["step"] % 24 == 23 or r["step"] in (0, 72, 144, 216, 288, 360, 432, 504, 576, 648, 718):
                print(
                    f"{r['step']:4d} {r['step']//24:3d} {r['money']:7.0f} {r['opp']:7.0f} {r['gap']:7.0f} "
                    f"{r['hands']:3d} {r['plants']:2d} {r['animals']:2d} {r['shed']:3d}",
                    flush=True,
                )
        results.append({"seed": seed, "seat0": seat0, "expect": expect, "fc": cb, "mv": ob, "margin": cb - ob, "trace": rows})
    OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print("wrote", OUT, flush=True)


if __name__ == "__main__":
    main()
