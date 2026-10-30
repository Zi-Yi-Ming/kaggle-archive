# -*- coding: utf-8 -*-
"""P98 dual-gate: extracted public agents vs Metav4 + shop_v7 (and thomas)."""
from __future__ import annotations

import importlib.util
import json
import sys
import time
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
EXT = PROJ / "_external/scan_p98_new/extracted"
OUTJSON = PROJ / "_research/p98_dual_gates.json"

CANDS = [
    ("v56", EXT / "v56_main.py"),
    ("orderbook", EXT / "orderbook_main.py"),
    ("v54leak", EXT / "v54leak_main.py"),
    ("v55", EXT / "v55_main.py"),
    ("pipe19", EXT / "pipe19_main.py"),
    ("pipe18", EXT / "pipe18_main.py"),
]

OPPS = [
    ("metav4", METAV4),
    ("shopv7", SHOPV7),
    ("thomas", THOMAS),
]


def series(cand_path: Path, cand_name: str, opp_path: Path, opp_name: str, seeds, label):
    rows = []
    wins = 0
    margins = []
    for seed in seeds:
        for seat0 in (True, False):
            try:
                c = p79.load_quiet(cand_path, f"c_{label}_{seed}_{int(seat0)}")
                o = p79.load_quiet(opp_path, f"o_{label}_{seed}_{int(seat0)}")
                if seat0:
                    b0, b1, st, sec = p79.run(c, o, seed)
                    cb, ob = b0, b1
                else:
                    b0, b1, st, sec = p79.run(o, c, seed)
                    ob, cb = b0, b1
                margin = cb - ob
                win = cb > ob
                wins += int(win)
                margins.append(margin)
                row = {
                    "seed": seed, "seat0": seat0, "cand": cb, "opp": ob,
                    "margin": margin, "win": win, "status": st, "sec": sec,
                }
                print(
                    f"{cand_name} vs {opp_name} s={seed} seat0={seat0} "
                    f"{cb:.0f}:{ob:.0f} m={margin:.0f} win={win} {sec}s",
                    flush=True,
                )
            except Exception as e:
                row = {"seed": seed, "seat0": seat0, "error": str(e)[:200]}
                print(f"FAIL {cand_name} vs {opp_name} s={seed} seat0={seat0}: {e}", flush=True)
            rows.append(row)
    n = len([r for r in rows if "win" in r])
    summary = {
        "n": n,
        "wins": wins,
        "win_rate": (wins / n) if n else 0.0,
        "mean_margin": (sum(margins) / len(margins)) if margins else None,
    }
    return rows, summary


def main():
    smoke = (1, 2)
    full = (1, 2, 3, 4)
    payload = {"results": {}}
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    payload.setdefault("results", {})

    for name, path in CANDS:
        if not path.exists():
            print("MISSING", name, path, flush=True)
            continue
        prev = payload["results"].get(name, {})
        print(f"\n===== {name} bytes={path.stat().st_size} =====", flush=True)
        # smoke first if no data
        need_full = True
        for opp_name, opp_path in OPPS:
            key = f"vs_{opp_name}"
            if not opp_path.exists():
                print("skip missing opp", opp_name, flush=True)
                continue
            have = (prev.get(key) or {}).get("summary") or {}
            if have.get("n", 0) >= 8:
                print("skip done", name, key, have, flush=True)
                continue
            # smoke
            rows, summary = series(path, name, opp_path, opp_name, smoke, f"{name}_{opp_name}_smoke")
            rec = prev.setdefault(key, {})
            rec["smoke_rows"] = rows
            rec["smoke_summary"] = summary
            print("SMOKE", name, key, summary, flush=True)
            # expand if not collapsed
            if summary.get("win_rate", 0) > 0.25 or (summary.get("mean_margin") or -1e9) > -5000:
                rows2, summary2 = series(path, name, opp_path, opp_name, full, f"{name}_{opp_name}_full")
                rec["full_rows"] = rows2
                rec["summary"] = summary2
                print("FULL", name, key, summary2, flush=True)
            else:
                rec["summary"] = summary
                print("STOP weak", name, key, summary, flush=True)
        payload["results"][name] = prev
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nWROTE", OUTJSON, flush=True)
    # compact table
    for name, rec in payload["results"].items():
        bits = []
        for opp_name, _ in OPPS:
            s = (rec.get(f"vs_{opp_name}") or {}).get("summary") or {}
            if s:
                bits.append(f"{opp_name} {s.get('win_rate', 0):.0%} m={s.get('mean_margin')}")
        print(f"TABLE {name}: " + " | ".join(bits), flush=True)


if __name__ == "__main__":
    main()
