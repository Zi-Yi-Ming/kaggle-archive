# -*- coding: utf-8 -*-
"""P78 local gate: public candidates vs production thomas_2945. No submit.

Win-rate first (bank only decides win/loss). finn not used.
Saves incrementally to _research/p78_gate_vs_thomas.json
"""
from __future__ import annotations

import importlib.util
import io
import json
import re
import sys
import time
from contextlib import redirect_stdout
from pathlib import Path

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
THOMAS = PROJ / "_push_thomas_2945" / "main.py"
OUT = PROJ / "_research" / "p78_gate_vs_thomas.json"
EXT = PROJ / "_external" / "scan_p77" / "extracted"

CANDIDATES = {
    "yhay81_0913": EXT / "yhay81__shop-router-0913.py",
    "salemali7_2900": EXT / "salemali7__kaggriculture-2900.py",
}

SEEDS = (1, 2, 3, 4)
sys.path.insert(0, str(PROJ))
from kaggle_environments import make  # noqa: E402


IPY_STUB = """
import sys, types
def _mod(name):
    m = types.ModuleType(name)
    m.__path__ = []
    sys.modules[name] = m
    return m
if 'IPython' not in sys.modules or not hasattr(sys.modules.get('IPython'), '__path__'):
    ip = _mod('IPython')
    ip.display = lambda *a, **k: None
    ip.get_ipython = lambda: type('X', (), {
        'run_line_magic': lambda *a, **k: None,
        'magic': lambda *a, **k: None,
        'run_cell': lambda *a, **k: None,
    })()
    ip.version_info = (3, 11)
    disp = _mod('IPython.display')
    disp.display = lambda *a, **k: None
    disp.FileLink = object
    disp.HTML = object
    disp.Markdown = object
    disp.Image = object
    disp.clear_output = lambda *a, **k: None
    core = _mod('IPython.core')
    magic = _mod('IPython.core.magic')
    magic.register_line_magic = lambda f=None, **k: (f if f else (lambda g: g))
    magic.magics_class = lambda cls=None, **k: (cls if cls else (lambda c: c))
    ip.core = core
    core.magic = magic
    disp_mod = _mod('IPython.core.display')
    disp_mod.display = disp.display
    core.display = disp_mod
    pt = _mod('IPython.core.pylabtools')
    pt.figsize = (6.4, 4.8)
    core.pylabtools = pt
    sys.modules['IPython.display'] = disp
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
        make_i = code.find("from kaggle_environments", agent_i)
        if make_i > agent_i:
            code = code[:make_i]
        run_i = code.find("env.run(", agent_i)
        if run_i > agent_i:
            code = code[:run_i]
    futures = re.findall(r"(?m)^from __future__ import .+$", code)
    for f in futures:
        code = code.replace(f + "\n", "", 1)
    if futures:
        code = "\n".join(futures) + "\n" + code

    MPL_STUB = (
        "import sys, types, copy, json, zlib, base64, math\n"
        "matplotlib=types.ModuleType('matplotlib'); matplotlib.use=lambda *a,**k:None\n"
        "sys.modules['matplotlib']=matplotlib\n"
        "plt=types.ModuleType('matplotlib.pyplot')\n"
        "plt.show=plt.close=lambda *a,**k:None\n"
        "plt.subplots=lambda *a,**k: (types.SimpleNamespace(), types.SimpleNamespace())\n"
        "plt.figure=lambda *a,**k: types.SimpleNamespace()\n"
        "plt.rcParams={}\n"
        "sys.modules['matplotlib.pyplot']=plt\n"
        "patches=types.ModuleType('matplotlib.patches')\n"
        "patches.FancyBboxPatch=object; patches.FancyArrowPatch=object\n"
        "sys.modules['matplotlib.patches']=patches\n"
        "matplotlib.pyplot=plt; matplotlib.patches=patches\n"
    )

    if "salemali7" in path.name:
        keys = (
            "_ACTIONS =",
            "def _get",
            "def _copy_action",
            "def _weed_repair_action",
            "def _fr_state",
            "def _repay",
            "def _front_run",
            "def _align_hands",
            "def agent",
        )
        idxs = [code.find(k) for k in keys if code.find(k) >= 0]
        start = min(idxs) if idxs else 0
        core = code[start:]
        core = re.split(r"(?m)^(main_path|agent_bytes|archive_path|t_info\s*=)", core, maxsplit=1)[0]
        core = re.split(r'(?m)^.*Path\("main\.py"\)', core, maxsplit=1)[0]
        core = re.split(r"(?m)^from kaggle_environments import make", core, maxsplit=1)[0]
        code = IPY_STUB + MPL_STUB + core
    elif "IPython" in code or "matplotlib" in code:
        code = IPY_STUB + MPL_STUB + code

    ns = {"__name__": tag, "__file__": str(path), "__builtins__": __builtins__}
    try:
        with redirect_stdout(io.StringIO()):
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


def load_module_agent(path: Path, tag: str):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    try:
        with redirect_stdout(io.StringIO()):
            spec.loader.exec_module(m)
    except Exception:
        spec.loader.exec_module(m)
    if hasattr(m, "agent"):
        fn = m.agent
    elif hasattr(m, "build_agent"):
        fn = m.build_agent({})
    else:
        raise RuntimeError("no agent")
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


def load_cand(path: Path, tag: str):
    if path.name.endswith("_clean.py") or "thomas" in path.name:
        return load_module_agent(path, tag)
    try:
        return load_quiet(path, tag)
    except Exception:
        return load_module_agent(path, tag)


def gate_one(key: str, cand_path: Path) -> dict:
    rows = []
    for seed in SEEDS:
        for seat0 in (True, False):
            tag = f"{key}_{seed}_{int(seat0)}"
            try:
                c = load_cand(cand_path, f"c_{tag}")
                t = load_module_agent(THOMAS, f"t_{tag}")
                if seat0:
                    b0, b1, st, sec = run(c, t, seed)
                    cb, tb = b0, b1
                else:
                    b0, b1, st, sec = run(t, c, seed)
                    cb, tb = b1, b0
                row = {
                    "cand": key,
                    "seed": seed,
                    "seat0": seat0,
                    "cand_bank": cb,
                    "thomas_bank": tb,
                    "margin": cb - tb,
                    "win": cb > tb,
                    "tie": cb == tb,
                    "status": st,
                    "sec": sec,
                }
                print(
                    f"{key} vs thomas s={seed} seat0={seat0} "
                    f"cand={cb:.0f} thomas={tb:.0f} m={row['margin']:.0f} "
                    f"win={row['win']} st={st} {sec}s",
                    flush=True,
                )
            except Exception as e:
                row = {"cand": key, "seed": seed, "seat0": seat0, "error": str(e)[:200]}
                print(f"FAIL {key} s={seed} seat0={seat0}: {e}", flush=True)
            rows.append(row)
            # incremental save
            payload = load_out()
            payload.setdefault("results", {}).setdefault(key, {"path": str(cand_path), "rows": []})
            payload["results"][key]["rows"] = rows
            payload["results"][key]["summary"] = summarize(rows)
            save_out(payload)
    return {"path": str(cand_path), "rows": rows, "summary": summarize(rows)}


def summarize(rows: list) -> dict:
    ok = [r for r in rows if "error" not in r]
    wins = sum(1 for r in ok if r.get("win"))
    ties = sum(1 for r in ok if r.get("tie"))
    losses = sum(1 for r in ok if not r.get("win") and not r.get("tie"))
    margins = [r["margin"] for r in ok]
    return {
        "n": len(ok),
        "wins": wins,
        "ties": ties,
        "losses": losses,
        "win_rate": round(wins / len(ok), 3) if ok else None,
        "mean_margin": round(sum(margins) / len(margins), 1) if margins else None,
        "errors": len(rows) - len(ok),
    }


def load_out() -> dict:
    if OUT.exists():
        try:
            return json.loads(OUT.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_out(payload: dict) -> None:
    payload["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    payload["thomas"] = str(THOMAS)
    payload["seeds"] = list(SEEDS)
    payload["note"] = "local gate only; no submit; vs production thomas"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    payload = load_out()
    payload.setdefault("results", {})
    save_out(payload)
    for key, path in CANDIDATES.items():
        if not path.exists():
            print(f"SKIP missing {key}: {path}", flush=True)
            continue
        prev = payload.get("results", {}).get(key, {}).get("summary")
        if prev and prev.get("n", 0) >= 8 and prev.get("errors", 0) == 0:
            print(f"SKIP done {key}: {prev}", flush=True)
            continue
        print(f"=== GATE {key} ===", flush=True)
        payload["results"][key] = gate_one(key, path)
        save_out(payload)
    print("DONE", OUT, flush=True)
    print(json.dumps({k: v.get("summary") for k, v in payload.get("results", {}).items()}, indent=2), flush=True)


if __name__ == "__main__":
    main()
