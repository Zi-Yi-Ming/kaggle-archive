# -*- coding: utf-8 -*-
"""P92: exact recheck of Kaito v43 (public 2882) — reopen trigger from external counsel.

Gates:
- Slot A (production): vs Metav4 >=60% AND vs shop_v7 >=50%, holdout
- Slot B (hedge): no 0/x collapse across hetero panel; local BT proxy
NOT submit without user auth.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
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
ALPEREN = PROJ / "_push_alperen" / "main.py"
PIPE16 = PROJ / "_push_pipe16" / "main.py"
KAITO = PROJ / "_external/public_nb/kaito_v43/main.py"
KAITO_ALT = PROJ / "_external/p51_extracted2/103_128_fresh_public_v43_sparse_shop_hybrid.py"
OUTJSON = PROJ / "_research/p92_kaito_v43.json"

EXPECT_SHA = "69f06a802b62aa08f28705dab5728eb924bb6a7c23ffe0164f65b104cc3dadf3"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def series(cand_path, cand_name, opp_path, opp_name, seeds):
    rows, margins, wins, n = [], [], 0, 0
    for seed in seeds:
        for seat0 in (True, False):
            tag = f"{cand_name}_{opp_name}_{seed}_{int(seat0)}"
            try:
                c = p79.load_quiet(cand_path, f"c_{tag}")
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
                print(f"{cand_name} vs {opp_name} s={seed} seat0={seat0} c={cb:.0f} o={ob:.0f} m={m:.0f} win={win}", flush=True)
                rows.append({"seed": seed, "seat0": seat0, "cb": cb, "ob": ob, "margin": m, "win": win})
            except Exception as e:
                print(f"FAIL {cand_name} {opp_name} s={seed} seat0={seat0}: {type(e).__name__}:{e}", flush=True)
                rows.append({"seed": seed, "seat0": seat0, "error": f"{type(e).__name__}:{e}"[:220]})
    sm = {
        "cand": cand_name, "opp": opp_name, "n": n, "wins": wins,
        "win_rate": round(wins / n, 3) if n else None,
        "mean_margin": round(sum(margins) / len(margins), 1) if margins else None,
    }
    print("SUM", sm, flush=True)
    return rows, sm


def bt_proxy(results: dict[str, dict]) -> float | None:
    """Crude BT proxy: points = wins + 0.5*ties over all games vs panel (not Metav4-only).
    Higher is better; compare candidate panel points vs Metav4 panel if we had both.
    Here return candidate overall win_rate weighted by n across panel.
    """
    tw = tn = 0
    for sm in results.values():
        n = sm.get("n") or 0
        w = sm.get("wins") or 0
        tw += w
        tn += n
    return round(tw / tn, 3) if tn else None


def main():
    print("=== P92 Kaito v43 recheck ===", flush=True)
    print("main.py", KAITO, "exists", KAITO.exists(), "size", KAITO.stat().st_size if KAITO.exists() else None, flush=True)
    if KAITO.exists():
        h = sha256(KAITO)
        print("sha256", h, "match_manifest", h == EXPECT_SHA, flush=True)
    # pick best loadable source
    src = None
    for p in (KAITO, KAITO_ALT):
        if not p.exists():
            continue
        try:
            p79.load_quiet(p, f"probe_{p.stem[:20]}")
            src = p
            print("LOAD OK", p, flush=True)
            break
        except Exception as e:
            print("LOAD FAIL", p, e, flush=True)
    if src is None:
        # try extract payload from p51 file via zlib b85
        print("attempt decode p51 payload", flush=True)
        text = KAITO_ALT.read_text(encoding="utf-8", errors="ignore")
        import base64
        import re
        import zlib

        parts = re.findall(r"'([^']+)'", text[text.find("payload"): text.find("payload") + 200000])
        packed = "".join(parts)
        try:
            blob = zlib.decompress(base64.b85decode(packed))
            out = PROJ / "_external/public_nb/kaito_v43/main_from_p51.py"
            out.write_bytes(blob)
            print("decoded", len(blob), out, flush=True)
            p79.load_quiet(out, "probe_decoded")
            src = out
        except Exception as e:
            print("decode fail", e, flush=True)
    if src is None:
        print("NO LOADABLE KAITO", flush=True)
        return

    payload = {
        "updated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "src": str(src),
        "sha256": sha256(src) if src.exists() else None,
        "results": {},
        "note": "P92 Kaito v43 exact recheck; no submit without auth",
    }
    if OUTJSON.exists():
        try:
            old = json.loads(OUTJSON.read_text(encoding="utf-8"))
            payload["results"] = old.get("results") or {}
        except Exception:
            pass

    panel = [
        ("metav4", METAV4, (1, 2, 3)),
        ("shop_v7", SHOPV7, (1, 2, 3)),
        ("thomas", THOMAS, (1, 2)),
        ("alperen", ALPEREN, (1, 2)),
        ("pipe16", PIPE16, (1, 2)),
    ]
    # holdout seeds if slot A looks good
    for name, path, seeds in panel:
        if not path.exists():
            print("skip missing", name, path, flush=True)
            continue
        key = f"vs_{name}"
        prev = payload["results"].get(key) or {}
        if (prev.get("n") or 0) >= len(seeds) * 2:
            print("cached", key, prev, flush=True)
            continue
        print(f"\n----- kaito_v43 vs {name} seeds={seeds} -----", flush=True)
        r, sm = series(src, "kaito_v43", path, name, seeds)
        payload["results"][key] = {**sm, "rows": r}
        payload["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    # Slot A decision
    s_mv = payload["results"].get("vs_metav4") or {}
    s_sp = payload["results"].get("vs_shop_v7") or {}
    wr_mv = s_mv.get("win_rate") or 0
    wr_sp = s_sp.get("win_rate") or 0
    slot_a = wr_mv >= 0.6 and wr_sp >= 0.5
    print(f"\nSLOT_A kaito_v43: mv={wr_mv}({s_mv.get('mean_margin')}) shop={wr_sp}({s_sp.get('mean_margin')}) pass={slot_a}", flush=True)

    if slot_a:
        print("ESCALATE holdout 4-6", flush=True)
        r2, s2 = series(src, "kaito_v43", METAV4, "metav4_h", (4, 5, 6))
        r3, s3 = series(src, "kaito_v43", SHOPV7, "shop_h", (4, 5, 6))
        payload["results"]["hold_mv"] = s2
        payload["results"]["hold_sp"] = s3
        payload["results"]["holdout_dual"] = (s2.get("win_rate") or 0) >= 0.6 and (s3.get("win_rate") or 0) >= 0.5
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"HOLDOUT mv={s2.get('win_rate')}({s2.get('mean_margin')}) shop={s3.get('win_rate')} dual={payload['results']['holdout_dual']}", flush=True)

    # Slot B: collapse check
    collapses = []
    for k, sm in payload["results"].items():
        if not k.startswith("vs_"):
            continue
        n = sm.get("n") or 0
        w = sm.get("wins") or 0
        if n >= 4 and w == 0:
            collapses.append(k)
    print("SLOT_B collapses(0/x n>=4):", collapses or "none", flush=True)
    print("panel_win_rate_proxy", bt_proxy({k: v for k, v in payload["results"].items() if k.startswith("vs_")}), flush=True)

    print("\n==== P92 TABLE ====", flush=True)
    for k, v in payload["results"].items():
        if isinstance(v, dict) and "win_rate" in v:
            print(k, "wr", v.get("win_rate"), "margin", v.get("mean_margin"), "n", v.get("n"), flush=True)
    print("holdout_dual", payload["results"].get("holdout_dual"), flush=True)


if __name__ == "__main__":
    main()
