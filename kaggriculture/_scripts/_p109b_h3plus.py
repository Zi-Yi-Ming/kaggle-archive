# -*- coding: utf-8 -*-
"""P109b: dual-gate H3+ (start=624, cap=60) and package if pass."""
from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "p79", r"D:\桌面\Kaggle\kaggriculture\_scripts\_p79_mass_gate_vs_thomas.py"
)
p79 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p79)

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
METAV4 = PROJ / "_push_metav4_v13" / "main.py"
SHOPV7 = PROJ / "_external/p70_extracted/kaggriculture_shop_router_reactive_v7__0.py"
THOMAS = PROJ / "_push_thomas_2945" / "main.py"
OUTJSON = PROJ / "_research" / "p109b_h3plus.json"
PUSH = PROJ / "_push_h3plus_term624"
INPUTS = ("WHEAT", "FERTILIZER")


def load_mv(tag: str):
    code = METAV4.read_text(encoding="utf-8", errors="ignore")
    ns = {"__name__": tag, "__file__": str(METAV4), "__builtins__": __builtins__}
    exec(compile(code, str(METAV4), "exec"), ns)
    fn = ns.get("agent")
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)

    def agent(obs, configuration=None):
        return fn(obs) if n <= 1 else fn(obs, configuration)

    return agent


def call(fn, obs, configuration=None):
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)
    return fn(obs, configuration) if n > 1 else fn(obs, obs and configuration)


def make_h3plus(tag, start=624, cap=60):
    parent = load_mv(tag)

    def agent(obs, configuration=None):
        action = call(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            if step < start or not isinstance(action, dict):
                return action
            m = [list(o) for o in (action.get("market") or [])]
            already = {o[1] for o in m if len(o) >= 2 and o[0] == "SELL"}
            shed = dict(((obs.get("private") or {}).get("shed") or {}))
            for item, stock in shed.items():
                if item in INPUTS or item in already:
                    continue
                q = min(int(stock or 0), cap)
                if q > 0:
                    m.append(["SELL", item, q])
                    already.add(item)
            return dict(action, market=m) if m else action
        except Exception:
            return action

    return agent


def series(make_cand, opp_path, seeds, label):
    wins = 0
    margins = []
    rows = []
    for seed in seeds:
        for seat0 in (True, False):
            try:
                c = make_cand(f"c_{label}_{seed}_{int(seat0)}")
                o = p79.load_quiet(opp_path, f"o_{label}_{seed}_{int(seat0)}")
                if seat0:
                    b0, b1, stt, sec = p79.run(c, o, seed)
                    cb, ob = b0, b1
                else:
                    b0, b1, stt, sec = p79.run(o, c, seed)
                    ob, cb = b0, b1
                margin = cb - ob
                win = cb > ob
                wins += int(win)
                margins.append(margin)
                rows.append({"seed": seed, "seat0": seat0, "cand": cb, "opp": ob, "margin": margin, "win": win})
                print(f"{label} s={seed} seat0={seat0} {cb:.0f}:{ob:.0f} m={margin:.0f} win={win} {sec}s", flush=True)
            except Exception as e:
                rows.append({"seed": seed, "seat0": seat0, "error": str(e)[:180]})
                print(f"FAIL {label} s={seed}: {e}", flush=True)
    n = len([r for r in rows if "win" in r])
    summary = {"n": n, "wins": wins, "win_rate": (wins / n) if n else 0,
               "mean_margin": (sum(margins) / len(margins)) if margins else None}
    return rows, summary


def main():
    payload = {}
    rec = payload["h3plus_624"] = {}
    for opp_name, opp_path, seeds, key in (
        ("metav4", METAV4, (1, 2, 3, 4, 5, 6, 7, 8), "metav4"),
        ("shopv7", SHOPV7, (1, 2, 3, 4, 5, 6), "shop"),
        ("thomas", THOMAS, (1, 2, 3), "thomas"),
    ):
        print(f"\n== h3plus vs {opp_name} ==", flush=True)
        rows, summary = series(make_h3plus, opp_path, seeds, f"h3p_{opp_name}")
        rec[key] = {"rows": rows, "summary": summary}
        print("SUM", key, summary, flush=True)

    mv = rec["metav4"]["summary"]
    sh = rec["shop"]["summary"]
    dual = mv.get("win_rate", 0) >= 0.6 and sh.get("win_rate", 0) >= 0.5
    rec["dual_gate"] = "PASS" if dual else "FAIL"
    print("DUAL", rec["dual_gate"], "mv", mv, "sh", sh, flush=True)

    if dual:
        PUSH.mkdir(parents=True, exist_ok=True)
        # package: main.py wrapping Metav4 + term624
        main_py = PUSH / "main.py"
        # reuse existing push package pattern: copy metav4 and write wrapper as submission
        # For submission we need a single runnable main.py. Build wrapper that inlines load.
        src = METAV4.read_text(encoding="utf-8", errors="replace")
        wrapper = (
            "INPUTS = ('WHEAT', 'FERTILIZER')\n"
            "START, CAP = 624, 60\n"
            "import types as _t\n"
            + src
            + "\n\n"
            + r'''
_base_agent = agent

def agent(observation, configuration=None):
    action = _base_agent(observation, configuration)
    try:
        step = int((observation or {}).get("step", 0))
        if step < START or not isinstance(action, dict):
            return action
        m = [list(o) for o in (action.get("market") or [])]
        already = {o[1] for o in m if len(o) >= 2 and o[0] == "SELL"}
        shed = dict(((observation.get("private") or {}).get("shed") or {}))
        for item, stock in shed.items():
            if item in INPUTS or item in already:
                continue
            q = min(int(stock or 0), CAP)
            if q > 0:
                m.append(["SELL", item, q])
                already.add(item)
        return dict(action, market=m) if m else action
    except Exception:
        return action
'''
        )
        main_py.write_text(wrapper, encoding="utf-8")
        # tar.gz
        import tarfile
        tar_path = PUSH / "submission.tar.gz"
        with tarfile.open(tar_path, "w:gz") as tf:
            tf.add(main_py, arcname="main.py")
        rec["package"] = str(tar_path)
        print("PACKAGED", tar_path, tar_path.stat().st_size, flush=True)

    OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("WROTE", OUTJSON, flush=True)


if __name__ == "__main__":
    main()
