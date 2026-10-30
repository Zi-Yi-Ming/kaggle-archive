# -*- coding: utf-8 -*-
"""P88: dual-gate untested local + new public candidates vs Metav4 + shop_v7.

Also Metav4 money-gap autopsy vs strongest locals (who beats Metav4?).
NO submit.
"""
from __future__ import annotations

import importlib.util
import json
import re
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
PIPE16 = PROJ / "_push_pipe16" / "main.py"
THOMAS = PROJ / "_push_thomas_2945" / "main.py"
EXT = PROJ / "_external"
NEW = EXT / "scan_p88_new"
OUTJSON = PROJ / "_research/p88_hunt.json"
AUTOJSON = PROJ / "_research/p88_metav4_autopsy.json"


def extract_nb_agent(nb_path: Path) -> Path | None:
    """Extract main.py from notebook into extracted/ if possible."""
    outdir = nb_path.parent / "extracted"
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / (nb_path.stem[:40] + "_main.py")
    if out.exists() and out.stat().st_size > 5000:
        return out
    try:
        nb = json.loads(nb_path.read_text(encoding="utf-8", errors="ignore"))
    except Exception as e:
        print("nb read fail", nb_path, e)
        return None
    cells = []
    for c in nb.get("cells", []):
        s = c.get("source", "")
        if isinstance(s, list):
            s = "".join(s)
        cells.append(s)
    text = "\n".join(cells)
    # try common embed patterns
    for pattern, name in [
        (r"SOURCE_BYTES\s*=\s*b''\.join\(\(([\s\S]*?)\)\)", "source_bytes"),
        (r"AGENT_B64\s*=\s*\(([\s\S]*?)\)", "agent_b64"),
        (r"AGENT_GZ_B64\s*=\s*\(([\s\S]*?)\)", "agent_b64"),
    ]:
        m = re.search(pattern, text)
        if not m:
            continue
        try:
            if name == "source_bytes":
                ns = {}
                exec(m.group(0), ns)
                src = ns.get("SOURCE_BYTES")
                if src:
                    out.write_bytes(src)
                    print("extracted SOURCE_BYTES", out, len(src))
                    return out
            else:
                import base64
                import gzip

                parts = re.findall(r"['\"]([A-Za-z0-9+/=]+)['\"]", m.group(1))
                packed = "".join(parts)
                src = gzip.decompress(base64.b64decode(packed))
                out.write_bytes(src)
                print("extracted AGENT_B64", out, len(src))
                return out
        except Exception as e:
            print("extract fail", name, e)
    # fallback: if notebook itself contains def agent at top level
    if "\ndef agent" in text or text.startswith("def agent"):
        # strip packaging tails
        code = text
        code = re.sub(r"(?m)^%%writefile.*\n", "", code)
        agent_i = code.find("\ndef agent")
        if agent_i < 0:
            agent_i = 0
        core = code[agent_i:]
        for marker in ("from kaggle_environments", "env.run(", "Path(\"main.py\")"):
            i = core.find(marker)
            if i > 20:
                core = core[:i]
                break
        if "def agent" in core:
            out.write_text(code if len(code) > 2000 else core, encoding="utf-8")
            print("extracted inline agent", out)
            return out
    print("no extract", nb_path.name)
    return None


def load_full(path: Path, tag: str):
    try:
        return p79.load_quiet(path, tag)
    except Exception:
        code = path.read_text(encoding="utf-8", errors="ignore")
        import io
        from contextlib import redirect_stdout

        ns = {"__name__": tag, "__file__": str(path), "__builtins__": __builtins__}
        with redirect_stdout(io.StringIO()):
            exec(compile(code, str(path), "exec"), ns)
        fn = ns.get("agent")
        if fn is None:
            raise RuntimeError("no_agent")
        n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)

        def agent(obs, configuration=None):
            return fn(obs) if n <= 1 else fn(obs, configuration)

        return agent


def series(fac_opp_path, cand_path, cand_name, opp_name, seeds, label_prefix=""):
    rows = []
    wins = n = 0
    margins = []
    for seed in seeds:
        for seat0 in (True, False):
            tag = f"{cand_name}_{opp_name}_{seed}_{int(seat0)}"
            try:
                try:
                    c = load_full(cand_path, f"c_{tag}")
                except Exception:
                    c = p79.load_quiet(cand_path, f"c_{tag}")
                try:
                    o = load_full(fac_opp_path, f"o_{tag}")
                except Exception:
                    o = p79.load_quiet(fac_opp_path, f"o_{tag}")
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
                print(f"FAIL {cand_name} {opp_name} s={seed} seat0={seat0}: {e}", flush=True)
                rows.append({"seed": seed, "seat0": seat0, "error": str(e)[:200]})
    sm = {
        "cand": cand_name, "opp": opp_name, "n": n, "wins": wins,
        "win_rate": round(wins / n, 3) if n else None,
        "mean_margin": round(sum(margins) / len(margins), 1) if margins else None,
    }
    print("SUM", sm, flush=True)
    return rows, sm


def collect_candidates():
    cands = []
    # new notebooks
    if NEW.exists():
        for nb in NEW.rglob("*.ipynb"):
            p = extract_nb_agent(nb)
            if p:
                cands.append((f"new_{nb.stem[:24]}", p))
        for py in NEW.rglob("*.py"):
            if "extracted" in str(py) or py.name.endswith("_main.py"):
                if py.stat().st_size > 3000:
                    cands.append((f"newpy_{py.stem[:24]}", py))
    # untested locals
    locals_ = [
        ("asajjadi", EXT / "asajjadi/main.py"),
        ("rayk_c95", EXT / "p41_extracted/rayk_c95_main.py"),
        ("shape_shop_top10", EXT / "p67_extracted/shape_the_shop_work_the_pasture_top_10.py"),
        ("adaptive_route_v2", EXT / "p67_extracted/adaptive_route_agent_v2.py"),
        ("dynamic_route", EXT / "p67_extracted/kaggriculture_dynamic_route_agent.py"),
        ("sovereign_swarm", EXT / "p62_extracted/sovereign_swarm_kinematics_the.py"),
        ("salem_2900", EXT / "p41_extracted/salem_2900_main.py"),
        ("no_cow_v40", EXT / "p62_extracted/no_cow_left_behind_v40_autopsy_fix.py"),
        ("top_farms_meta", EXT / "p62_extracted/kaggriculture_what_the_top_farms_do_a_live_meta.py"),
        ("what_2600", EXT / "p62_extracted/kaggriculture_what_2600_farms_do_differently.py"),
        ("v43_recover", EXT / "p62_extracted/kaggriculture_v43_recovering_lost_harvests.py"),
        ("terminal_logistics", EXT / "p62_extracted/kaggriculture_terminal_logistics.py"),
        ("router_938", EXT / "p62_extracted/kaggriculture_93_8_win_rate_public_state_router.py"),
        ("pipe16", PIPE16),
        ("thomas_prod", THOMAS),
        ("shop_v7_as_cand", SHOPV7),
    ]
    for name, path in locals_:
        if path.exists():
            cands.append((name, path))
    # dedup by path
    seen = set()
    out = []
    for n, p in cands:
        rp = str(p.resolve())
        if rp in seen:
            continue
        seen.add(rp)
        out.append((n, p))
    return out


def autopsy_metav4(strong_paths):
    """Day-end money gap: Metav4 vs agents that beat it or are close."""
    print("\n=== Metav4 AUTOPTY money by day ===", flush=True)
    payload = {"games": []}
    steps_of_interest = (0, 24, 48, 72, 96, 120, 144, 192, 240, 288, 336, 384, 432, 480, 528, 576, 624, 672, 696, 718)

    def run_trace(a0, a1, seed, labels):
        env = p79.make("kaggriculture", debug=False)
        env.configuration["episodeSteps"] = 720
        if env.info is None:
            env.info = {}
        env.info["seed"] = int(seed)
        trace = {0: {}, 1: {}}

        def wrap(fn, seat):
            def agent(obs, configuration=None):
                st = int((obs or {}).get("step", -1))
                if st in steps_of_interest:
                    try:
                        farm = obs["farms"][seat]
                        opp = obs["farms"][1 - seat]
                        priv = obs.get("private") or {}
                        shed = priv.get("shed") or {}
                        invs = priv.get("inventories") or []
                        carried = 0
                        for iv in invs:
                            if isinstance(iv, dict):
                                carried += sum(int(v or 0) for v in iv.values())
                        plants = animals = 0
                        for row in farm.get("tiles") or []:
                            for t in row:
                                if isinstance(t, dict):
                                    if t.get("crop"):
                                        plants += 1
                                    if t.get("animal"):
                                        animals += 1
                        trace[seat][st] = {
                            "money": float(farm.get("money") or 0),
                            "opp_money": float(opp.get("money") or 0),
                            "gap": float(farm.get("money") or 0) - float(opp.get("money") or 0),
                            "hands": len(farm.get("hands") or []),
                            "plants": plants,
                            "animals": animals,
                            "shed": sum(int(v or 0) for v in shed.values()),
                            "carried": carried,
                        }
                    except Exception:
                        pass
                return p79.load_quiet and fn(obs, configuration) if False else (fn(obs, configuration) if getattr(fn, "__code__", None) and fn.__code__.co_argcount > 1 else fn(obs))

            return agent

        # simpler wrap
        def wrap2(fn, seat):
            n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)

            def agent(obs, configuration=None):
                st = int((obs or {}).get("step", -1))
                if st in steps_of_interest:
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
                        trace[seat][st] = {
                            "money": float(farm.get("money") or 0),
                            "opp_money": float(opp.get("money") or 0),
                            "gap": float(farm.get("money") or 0) - float(opp.get("money") or 0),
                            "hands": len(farm.get("hands") or []),
                            "plants": plants,
                            "animals": animals,
                            "shed": sum(int(v or 0) for v in (shed or {}).values()),
                        }
                    except Exception:
                        pass
                return fn(obs) if n <= 1 else fn(obs, configuration)

            return agent

        env.run([wrap2(a0, 0), wrap2(a1, 1)])
        f = env.steps[-1]
        m0 = float(f[0]["observation"]["farms"][0]["money"])
        m1 = float(f[1]["observation"]["farms"][1]["money"])
        return trace, m0, m1

    mv = load_full(METAV4, "mv_auto")
    for name, path in strong_paths:
        if not path.exists():
            continue
        try:
            opp = load_full(path, f"auto_{name}")
        except Exception as e:
            print("skip", name, e)
            continue
        for seed in (1, 2):
            try:
                tr, m0, m1 = run_trace(mv, opp, seed, (name, "mv"))
                row = {
                    "opp": name, "seed": seed, "mv": m0, "opp_bank": m1,
                    "margin": m0 - m1, "mv_trace": tr[0],
                }
                payload["games"].append(row)
                print(f"AUTOPT {name} s={seed} mv={m0:.0f} opp={m1:.0f} m={m0-m1:.0f}", flush=True)
                # print day gaps
                for st in (96, 192, 288, 384, 480, 576, 672, 718):
                    t = tr[0].get(st)
                    if t:
                        print(f"    step{st}: gap={t['gap']:.0f} mv$={t['money']:.0f} hands={t['hands']} plants={t['plants']} ani={t['animals']} shed={t['shed']}", flush=True)
            except Exception as e:
                print("AUTOPT FAIL", name, seed, e, flush=True)
                payload["games"].append({"opp": name, "seed": seed, "error": str(e)[:200]})
        AUTOJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("autopsy written", AUTOJSON, flush=True)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "gates"
    payload = {"updated": time.strftime("%Y-%m-%dT%H:%M:%S"), "results": {}, "note": "P88 hunt dual-gate; no submit"}
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    payload.setdefault("results", {})

    cands = collect_candidates()
    print(f"candidates: {len(cands)}", flush=True)
    for n, p in cands:
        print(f"  {n}: {p} exists={p.exists()} size={p.stat().st_size if p.exists() else 0}", flush=True)

    if mode == "list":
        return

    seeds = (1, 2)
    hold_seeds = (3, 4, 5)
    strong_for_autopsy = []

    for name, path in cands:
        if not path.exists() or path.stat().st_size < 2000:
            print("SKIP missing", name, flush=True)
            continue
        prev = payload["results"].get(name) or {}
        sm_mv = (prev.get("vs_metav4") or {})
        if sm_mv.get("n", 0) >= 4 and (sm_mv.get("win_rate") or 0) < 0.45 and name not in ("pipe16", "thomas_prod", "shop_v7_as_cand"):
            print("SKIP already weak", name, sm_mv, flush=True)
            continue
        print(f"\n===== GATE {name} =====", flush=True)
        r_mv, s_mv = series(METAV4, path, name, "metav4", seeds)
        r_sp, s_sp = series(SHOPV7, path, name, "shop_v7", seeds)
        r_th, s_th = series(THOMAS, path, name, "thomas", (1,))
        prev.update({
            "path": str(path),
            "vs_metav4": s_mv, "vs_shop_v7": s_sp, "vs_thomas": s_th,
            "rows": (prev.get("rows") or []) + r_mv + r_sp + r_th,
            "stage": "smoke",
        })
        payload["results"][name] = prev
        payload["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        wr_mv = s_mv.get("win_rate") or 0
        wr_sp = s_sp.get("win_rate") or 0
        dual = wr_mv >= 0.6 and wr_sp >= 0.5
        print(f"DUAL {name}: mv={wr_mv}({s_mv.get('mean_margin')}) shop={wr_sp}({s_sp.get('mean_margin')}) th={s_th.get('win_rate')} dual={dual}", flush=True)
        if wr_mv >= 0.45 or (s_mv.get("mean_margin") or 0) > -50:
            strong_for_autopsy.append((name, path))
        if dual:
            print("ESCALATE", name, flush=True)
            r2, s2 = series(METAV4, path, name, "metav4_h", hold_seeds)
            r3, s3 = series(SHOPV7, path, name, "shop_h", hold_seeds)
            prev["hold_mv"] = s2
            prev["hold_sp"] = s3
            prev["holdout_dual"] = (s2.get("win_rate") or 0) >= 0.6 and (s3.get("win_rate") or 0) >= 0.5
            prev["stage"] = "holdout"
            payload["results"][name] = prev
            OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"HOLDOUT {name}: mv={s2.get('win_rate')} shop={s3.get('win_rate')} dual={prev['holdout_dual']}", flush=True)

    print("\n==== P88 TABLE ====", flush=True)
    for k, v in payload["results"].items():
        print(
            k,
            "mv", (v.get("vs_metav4") or {}).get("win_rate"), (v.get("vs_metav4") or {}).get("mean_margin"),
            "shop", (v.get("vs_shop_v7") or {}).get("win_rate"), (v.get("vs_shop_v7") or {}).get("mean_margin"),
            "th", (v.get("vs_thomas") or {}).get("win_rate"),
            "hold_dual", v.get("holdout_dual"),
            flush=True,
        )

    if mode in ("all", "autopsy") and strong_for_autopsy:
        autopsy_metav4(strong_for_autopsy[:6])


if __name__ == "__main__":
    main()
