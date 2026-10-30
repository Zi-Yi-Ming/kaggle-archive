# -*- coding: utf-8 -*-
"""Expanded Slot-B evaluation for Fieldcraft 2887."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
import importlib.util

spec = importlib.util.spec_from_file_location(
    "p79", r"D:\桌面\Kaggle\kaggriculture\_scripts\_p79_mass_gate_vs_thomas.py"
)
p79 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p79)

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
METAV4 = PROJ / "_push_metav4_v13" / "main.py"
SHOPV7 = PROJ / "_external/p70_extracted/kaggriculture_shop_router_reactive_v7__0.py"
THOMAS = PROJ / "_push_thomas_2945" / "main.py"
ALPEREN = PROJ / "_push_alperen" / "main.py"
PIPE16 = PROJ / "_push_pipe16" / "main.py"
KAITO48 = PROJ / "_external/public_nb/kaito_v48/main.py"
pkg = PROJ / "_external/scan_p95_again/extracted/fieldcraft_pkg"
main_py = pkg / "main.py"
OUTJSON = PROJ / "_research/p95_again_gates.json"

sys.path.insert(0, str(pkg))


def load_fc(tag):
    code = main_py.read_text(encoding="utf-8", errors="ignore")
    ns = {"__name__": tag, "__file__": str(main_py), "__builtins__": __builtins__}
    import io
    from contextlib import redirect_stdout
    with redirect_stdout(io.StringIO()):
        exec(compile(code, str(main_py), "exec"), ns)
    fn = ns.get("agent")
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)

    def agent(obs, configuration=None):
        return fn(obs) if n <= 1 else fn(obs, configuration)

    return agent


def series(opp_path, opp_name, seeds):
    wins = n = 0
    margins = []
    rows = []
    for seed in seeds:
        for seat0 in (True, False):
            tag = f"fc2887x_{opp_name}_{seed}_{int(seat0)}"
            try:
                c = load_fc(f"c_{tag}")
                o = p79.load_quiet(opp_path, f"o_{tag}")
                if seat0:
                    b0, b1, st, sec = p79.run(c, o, seed)
                    cb, ob = b0, b1
                else:
                    b0, b1, st, sec = p79.run(o, c, seed)
                    cb, ob = b1, b0
                m = cb - ob
                win = cb > ob
                n += 1
                wins += int(win)
                margins.append(m)
                print(f"FC vs {opp_name} s={seed} seat0={int(seat0)} c={cb:.0f} o={ob:.0f} m={m:.0f} win={win}", flush=True)
                rows.append({"seed": seed, "seat0": seat0, "cb": cb, "ob": ob, "margin": m, "win": win})
            except Exception as e:
                print(f"FAIL {opp_name} s={seed}: {type(e).__name__}:{e}", flush=True)
                rows.append({"seed": seed, "seat0": seat0, "error": str(e)[:200]})
    sm = {"cand": "fieldcraft2887", "opp": opp_name, "n": n, "wins": wins,
          "win_rate": round(wins / n, 3) if n else None,
          "mean_margin": round(sum(margins) / len(margins), 1) if margins else None}
    print("SUM", sm, flush=True)
    return sm, rows


def main():
    load_fc("probe")
    panel = [
        ("metav4", METAV4, range(1, 9)),
        ("shop_v7", SHOPV7, range(1, 7)),
        ("thomas", THOMAS, range(1, 5)),
        ("alperen", ALPEREN, range(1, 4)),
        ("pipe16", PIPE16, range(1, 4)),
    ]
    if KAITO48.exists():
        panel.append(("kaito_v48", KAITO48, range(1, 4)))
    results = {}
    all_rows = {}
    tw = tn = 0
    for name, path, seeds in panel:
        sm, rows = series(path, name, list(seeds))
        results[name] = sm
        all_rows[name] = rows
        tw += sm.get("wins") or 0
        tn += sm.get("n") or 0
    field_wr = round(tw / tn, 3) if tn else None
    mv = results.get("metav4") or {}
    shop = results.get("shop_v7") or {}
    collapses = [k for k, v in results.items() if (v.get("n") or 0) >= 4 and (v.get("wins") or 0) == 0]
    slot_a = (mv.get("win_rate") or 0) >= 0.6 and (shop.get("win_rate") or 0) >= 0.5
    # Slot B: no collapse, shop not dead, field proxy not worse than Metav4-ish, positive mean on field
    slot_b = (
        "shop_v7" not in collapses
        and (shop.get("win_rate") or 0) >= 0.5
        and field_wr is not None
        and field_wr >= 0.5
        and not collapses
    )
    gate = {
        "wr_mv": mv.get("win_rate"),
        "mean_margin_mv": mv.get("mean_margin"),
        "wr_shop": shop.get("win_rate"),
        "mean_margin_shop": shop.get("mean_margin"),
        "field_wr": field_wr,
        "collapses": collapses,
        "slot_a": slot_a,
        "slot_b_signal": slot_b,
        "decision": (
            "SLOT_A_NEEDS_HOLDOUT" if slot_a else
            "SLOT_B_SIGNAL_AUTH_REQUIRED" if slot_b else
            "STOP_NO_SIGNAL"
        ),
        "note": "Fieldcraft 2887 exact (main+mirror_plan); public claim 2887.4 sub 56258004",
    }
    print("\n==== EXPANDED GATE ====", flush=True)
    print(json.dumps(gate, indent=2, ensure_ascii=False), flush=True)
    print("results", json.dumps(results, indent=2), flush=True)

    payload = {"results": {}}
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    payload.setdefault("results", {})
    payload["results"]["fieldcraft_2887_expanded"] = {
        "path": str(main_py),
        "results": results,
        "gate": gate,
        "rows": all_rows,
        "updated": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("saved", OUTJSON, flush=True)


if __name__ == "__main__":
    main()
