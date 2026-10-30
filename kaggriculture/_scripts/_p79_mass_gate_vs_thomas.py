# -*- coding: utf-8 -*-
"""P79 mass gate: exhaust remaining public agents vs production thomas.

Smoke: seeds 1-2 x both seats (4 games). If wins>=2, full seeds 1-4 (8 games).
Incremental JSON. No submit.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import time
import traceback
from pathlib import Path

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
THOMAS = PROJ / "_push_thomas_2945" / "main.py"
OUT = PROJ / "_research" / "p79_mass_gate_vs_thomas.json"
EXT = PROJ / "_external"
sys.path.insert(0, str(PROJ))
from kaggle_environments import make  # noqa: E402

# Priority candidates not already NO vs thomas
CANDS = [
    ("ahmed_v45", EXT / "scan_p75_mass/extracted/ahmedberatozer__kaggriculture-v45-first-.py"),
    ("ahmed_v47", EXT / "scan_p75_mass/extracted/ahmedberatozer__kaggriculture-v47-reacti.py"),
    ("ahmed_v48", EXT / "scan_p75_mass/extracted/ahmedberatozer__kaggriculture-v48-clear-.py"),
    ("ahmed_v49", EXT / "scan_p75_mass/extracted/ahmedberatozer__kaggriculture-v49-funded.py"),
    ("ahmed_v50", EXT / "scan_20260919/extracted/ahmed_v50_clean.py"),
    ("dmitrii_herd", EXT / "scan_p77/extracted/dmitriigluzdov__kaggriculture-herd-safe-sale-win.py"),
    ("prvsiyan_moon", EXT / "public_nb/prvsiyan_moon/main.py"),
    ("prvsiyan_rain", EXT / "git/danilchil/public/prvsiyan_rain/prvsiyan_agent.py"),
    ("kaito_v58", EXT / "public_nb/kaito_v58/main.py"),
    ("kaito_v48", EXT / "public_nb/kaito_v48/main.py"),
    ("aurax7_v7", EXT / "scan_p75_mass/extracted/aurax7__kaggriculture-shop-router-reacti.py"),
    ("lynnsakurai_v5", EXT / "scan_p77/extracted/lynnsakurai__farming-score-v5-timing-optimized.py"),
    ("crystalbaby_v38", EXT / "scan_p77/extracted/crystalbaby__kaggriculture-v38-public-submission.py"),
    ("arsgorynich_v40", EXT / "scan_p77/extracted/arsgorynich__kaggriculture-v40-challenger.py"),
    ("denizeryilmaz_v111", EXT / "scan_p77/extracted/denizeryilmaz__v111-8c4s-economic-core-premium-l.py"),
    ("andrewsokolovsky", EXT / "scan_p77/extracted/andrewsokolovsky__kaggriculture-breaking-the-tie.py"),
    ("municef_2448", EXT / "scan_p77/extracted/municef1__lb-2448-single-file-kaggriculture-agen.py"),
    ("guru_master_v3", EXT / "scan_20260919/extracted/guru_master_v3.py"),
    ("flexonafft", EXT / "top5_notebooks/flexonafft/flexonafft_main.py"),
    ("tetsu2131", EXT / "top5_notebooks/tetsu2131/tetsu2131_main.py"),
    ("prvsiyan_top5", EXT / "top5_notebooks/prvsiyan/prvsiyan_main.py"),
    ("gzmcr", EXT / "gzmcr/main.py"),
    ("lonespear", EXT / "lonespear/main.py"),
    ("sey_v21", EXT / "root_public_agents/sey_v21/main.py"),
    ("cok_v10", EXT / "root_public_agents/cok_v10/main.py"),
    ("pomagrenate", EXT / "pomagrenate/main.py"),
    ("octahedron", EXT / "Octahedron-BB_Kaggriculture/main.py"),
    ("rayk_c94", EXT / "p41_extracted/rayk_c94_main.py"),
    ("boatlee_v20", EXT / "public_nb/boatlee_v20/main.py"),
    ("p71_v48", EXT / "p71_new/v48_queue_main.py"),
    ("p71_evo", EXT / "p71_new/evolution_main.py"),
    ("nusrati_2650", EXT / "p71_spa_nb/nusrati_2650_main.py"),
    ("v44y_2820", EXT / "p70b_main/v44y_2820_main.py"),
    ("q30_2312", EXT / "p70b_main/2312_q30_main.py"),
    ("day3_cow", EXT / "p66_extracted/kaggriculture_day_3_cow_challenger.py"),
    ("pipe5", EXT / "p66_extracted/kaggriculture_pipe_5_terminal_boost.py"),
    ("v44_sale_race", EXT / "p66_extracted/kaggriculture_v44_winning_the_same_turn_sale_rac.py"),
    ("v45_wheat", EXT / "p66_extracted/kaggriculture_v45_first_turn_wheat_round_trip.py"),
    ("moon_melons", EXT / "p62_extracted/kaggriculture_frontier_the_moon_counts_melons.py"),
    ("score2710", EXT / "p51_extracted2/score2710_t23_kaggriculture_smart_harvest.py"),
    ("dynamic_route", EXT / "p67_extracted/kaggriculture_dynamic_route_agent.py"),
    ("multi_route", EXT / "p67_extracted/kaggriculture_multi_route_farming_agent.py"),
    ("harvestforge", EXT / "p62_extracted/harvestforge_x_high_throughput_farming.py"),
    ("terminal_logistics", EXT / "p62_extracted/kaggriculture_terminal_logistics.py"),
    ("cloning", EXT / "p66_extracted/kaggriculture_cloning_agent.py"),
    ("pure_rl", EXT / "p66_extracted/pure_rl_agent_bc_ppo_self_play.py"),
]

IPY_STUB = """
import sys, types
def _mod(name):
    m = types.ModuleType(name)
    m.__path__ = []
    sys.modules[name] = m
    return m
ip = _mod('IPython')
ip.display = lambda *a, **k: None
ip.get_ipython = lambda: type('X', (), {
    'run_line_magic': lambda *a, **k: None,
    'magic': lambda *a, **k: None,
    'run_cell': lambda *a, **k: None,
    'events': type('E', (), {'register': lambda *a, **k: None})(),
})()
ip.version_info = (3, 11)
disp = _mod('IPython.display')
disp.display = lambda *a, **k: None
disp.FileLink = object; disp.HTML = object; disp.Markdown = object; disp.Image = object
disp.clear_output = lambda *a, **k: None
core = _mod('IPython.core')
magic = _mod('IPython.core.magic')
magic.register_line_magic = lambda f=None, **k: (f if f else (lambda g: g))
magic.magics_class = lambda cls=None, **k: (cls if cls else (lambda c: c))
pt = _mod('IPython.core.pylabtools'); pt.figsize = (6.4, 4.8)
dispmod = _mod('IPython.core.display'); dispmod.display = disp.display
ip.core = core; core.magic = magic; core.pylabtools = pt; core.display = dispmod
sys.modules['IPython.display'] = disp
import types as _t
matplotlib=_t.ModuleType('matplotlib'); matplotlib.use=lambda *a,**k:None
sys.modules['matplotlib']=matplotlib
plt=_t.ModuleType('matplotlib.pyplot')
plt.show=plt.close=lambda *a,**k:None
plt.subplots=lambda *a,**k: (_t.SimpleNamespace(), _t.SimpleNamespace())
plt.figure=lambda *a,**k: _t.SimpleNamespace()
plt.rcParams={}
sys.modules['matplotlib.pyplot']=plt
patches=_t.ModuleType('matplotlib.patches')
patches.FancyBboxPatch=object; patches.FancyArrowPatch=object
sys.modules['matplotlib.patches']=patches
matplotlib.pyplot=plt; matplotlib.patches=patches
"""


def load_quiet(path: Path, tag: str):
    code = path.read_text(encoding="utf-8", errors="ignore")
    code = re.sub(r"(?m)^%%writefile.*\n", "", code)
    code = re.sub(r"(?m)^get_ipython\(\).*\n", "", code)
    code = re.split(r"(?m)^data = Path\([\"']main\.py[\"']\)\.read_bytes\(\)", code, maxsplit=1)[0]
    code = re.split(r"(?m)^submission = gzip\.compress", code, maxsplit=1)[0]
    code = re.split(r"(?m)^def load_agent\(", code, maxsplit=1)[0]
    agent_i = code.find("\ndef agent")
    if agent_i > 0:
        for marker in ("from kaggle_environments", "env.run(", "Path(\"main.py\")", "Path('main.py')"):
            i = code.find(marker, agent_i)
            if i > agent_i:
                code = code[:i]
                break
    futures = re.findall(r"(?m)^from __future__ import .+$", code)
    for f in futures:
        code = code.replace(f + "\n", "", 1)
    if futures:
        code = "\n".join(futures) + "\n" + code
    if "IPython" in code or "matplotlib" in code or "salem" in path.name.lower():
        # jump to agent core when notebook presentation would import GUI
        keys = ["_ACTIONS =", "def _get", "def agent", "PRODUCTS =", "def build_agent"]
        idxs = [code.find(k) for k in keys if code.find(k) >= 0]
        if idxs and "IPython" in code[:5000]:
            start = min(idxs)
            core = code[start:]
            core = re.split(r"(?m)^(main_path|agent_bytes|archive_path)\s*=", core, maxsplit=1)[0]
            code = IPY_STUB + core
        else:
            code = IPY_STUB + code
    ns = {"__name__": tag, "__file__": str(path), "__builtins__": __builtins__}
    try:
        exec(compile(code, str(path), "exec"), ns)
    except Exception as e:
        raise RuntimeError(f"{type(e).__name__}:{e}") from e
    fn = ns.get("agent")
    if fn is None and callable(ns.get("build_agent")):
        fn = ns["build_agent"]({})
    if fn is None:
        raise RuntimeError("no_agent")
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)

    def agent(obs, configuration=None):
        return fn(obs) if n <= 1 else fn(obs, configuration)

    return agent


def run(a0, a1, seed: int):
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    t0 = time.time()
    env.run([a0, a1])
    f = env.steps[-1]
    return (
        float(f[0]["observation"]["farms"][0]["money"]),
        float(f[1]["observation"]["farms"][1]["money"]),
        [s.get("status") for s in f],
        round(time.time() - t0, 1),
    )


def summarize(rows):
    ok = [r for r in rows if "error" not in r]
    wins = sum(1 for r in ok if r.get("win"))
    return {
        "n": len(ok),
        "wins": wins,
        "win_rate": round(wins / len(ok), 3) if ok else None,
        "mean_margin": round(sum(r["margin"] for r in ok) / len(ok), 1) if ok else None,
        "errors": len(rows) - len(ok),
    }


def load_out():
    if OUT.exists():
        try:
            return json.loads(OUT.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_out(payload):
    payload["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    payload["thomas"] = str(THOMAS)
    payload["note"] = "P79 mass gate; smoke seeds1-2; escalate if wins>=2; no submit"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def gate_one(key, path, seeds):
    rows = []
    for seed in seeds:
        for seat0 in (True, False):
            tag = f"{key}_{seed}_{int(seat0)}"
            try:
                c = load_quiet(path, f"c_{tag}")
                t = load_quiet(THOMAS, f"t_{tag}")
                if seat0:
                    b0, b1, st, sec = run(c, t, seed)
                    cb, tb = b0, b1
                else:
                    b0, b1, st, sec = run(t, c, seed)
                    cb, tb = b1, b0
                row = {
                    "cand": key, "seed": seed, "seat0": seat0,
                    "cand_bank": cb, "thomas_bank": tb,
                    "margin": cb - tb, "win": cb > tb,
                    "status": st, "sec": sec,
                }
                print(f"{key} s={seed} seat0={seat0} cand={cb:.0f} thomas={tb:.0f} "
                      f"m={row['margin']:.0f} win={row['win']} {sec}s", flush=True)
            except Exception as e:
                row = {"cand": key, "seed": seed, "seat0": seat0, "error": str(e)[:180]}
                print(f"FAIL {key} s={seed} seat0={seat0}: {e}", flush=True)
            rows.append(row)
    return rows


def main():
    payload = load_out()
    payload.setdefault("results", {})
    save_out(payload)
    pending = []
    for key, path in CANDS:
        if not path.exists():
            print(f"MISSING {key} {path}", flush=True)
            continue
        prev = payload["results"].get(key, {})
        sm = prev.get("summary") or {}
        if sm.get("n", 0) >= 4 and (sm.get("win_rate") or 0) < 0.5:
            print(f"SKIP already weak {key}: {sm}", flush=True)
            continue
        if sm.get("n", 0) >= 8 and (sm.get("win_rate") or 0) < 0.5:
            print(f"SKIP done weak {key}: {sm}", flush=True)
            continue
        pending.append((key, path, prev))

    print(f"pending {len(pending)}", flush=True)
    for key, path, prev in pending:
        print(f"=== SMOKE {key} ===", flush=True)
        rows = gate_one(key, path, (1, 2))
        sm = summarize(rows)
        payload["results"][key] = {
            "path": str(path),
            "rows": rows,
            "summary": sm,
            "stage": "smoke",
        }
        save_out(payload)
        print(f"smoke {key}: {sm}", flush=True)
        if sm.get("wins", 0) >= 2 and sm.get("errors", 0) == 0:
            print(f"=== ESCALATE {key} full ===", flush=True)
            rows = gate_one(key, path, (3, 4))
            prev_rows = payload["results"][key]["rows"]
            all_rows = prev_rows + rows
            sm2 = summarize(all_rows)
            payload["results"][key] = {
                "path": str(path),
                "rows": all_rows,
                "summary": sm2,
                "stage": "full",
            }
            save_out(payload)
            print(f"full {key}: {sm2}", flush=True)
        # any promising?
        sm = payload["results"][key]["summary"]
        if (sm.get("win_rate") or 0) >= 0.6 and sm.get("n", 0) >= 4:
            print(f"PROMISING {key}: {sm}", flush=True)

    # final table
    print("\n==== SUMMARY ====", flush=True)
    for k, v in sorted(payload.get("results", {}).items()):
        print(f"{k:24s} {v.get('summary')}", flush=True)
    save_out(payload)


if __name__ == "__main__":
    main()
