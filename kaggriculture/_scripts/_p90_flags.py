# -*- coding: utf-8 -*-
"""P90 invasive Metav4 flag mutants + tape-aware idle inject.

NOT submit. Dual gate vs Metav4 + shop_v7.
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

spec = importlib.util.spec_from_file_location(
    "p79", r"D:\桌面\Kaggle\kaggriculture\_scripts\_p79_mass_gate_vs_thomas.py"
)
p79 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p79)

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
METAV4 = PROJ / "_push_metav4_v13" / "main.py"
SHOPV7 = PROJ / "_external/p70_extracted/kaggriculture_shop_router_reactive_v7__0.py"
THOMAS = PROJ / "_push_thomas_2945" / "main.py"
PIPE16 = PROJ / "_push_pipe16" / "main.py"
OUTJSON = PROJ / "_research/p90_flags.json"
BASE_SRC = METAV4.read_text(encoding="utf-8", errors="ignore")


def load_mutant(src: str, tag: str):
    ns = {"__name__": tag, "__file__": str(METAV4), "__builtins__": __builtins__}
    with redirect_stdout(io.StringIO()):
        exec(compile(src, f"mutant_{tag}", "exec"), ns)
    fn = ns.get("agent")
    if fn is None:
        raise RuntimeError("no_agent")
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)

    def agent(obs, configuration=None):
        return fn(obs) if n <= 1 else fn(obs, configuration)

    return agent, ns


def apply_subs(src: str, pairs: list[tuple[str, str]]) -> str:
    out = src
    for old, new in pairs:
        if old not in out:
            print("  WARN missing pattern:", old[:60], flush=True)
        out = out.replace(old, new, 1)
    return out


def is_pass(cmd):
    if cmd is None:
        return True
    if isinstance(cmd, (list, tuple)):
        return len(cmd) == 0 or str(cmd[0]).upper() == "PASS"
    return str(cmd).upper() == "PASS"


def call_parent(fn, obs, configuration=None):
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)
    return fn(obs, configuration) if n > 1 else fn(obs)


def wrap_tape_aware(parent, ns):
    """Inject HybridOpening field cmds ONLY if Metav4 tape itself has PASS
    for that unit for the next 3 steps as well (truly idle window).
    Never touch market. Never pasture tile if tape plans BUILD there soon.
    """

    def agent(obs, configuration=None):
        action = call_parent(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            player = int((obs or {}).get("player", 0))
            if step == 0:
                agent._st = {}
            st = agent._st.setdefault(player, {"planted": False, "fires": 0})
            if not isinstance(action, dict):
                return action
            if step < 48 or step > 200:  # mid window only, skip opening
                # still allow day2-like late if planted
                if not (st.get("planted") and 48 <= step <= 80):
                    return action
            # yarn shop = shop-router family, abort inject
            shops = list((obs.get("town") or {}).get("unlocked_shops") or [])
            if shops.count("YARN_STORE") >= 2:
                return action
            impl = ns.get("_IMPL")
            if impl is None:
                return action
            chassis = getattr(impl, "chassis", None)
            if chassis is None:
                return action
            pst = chassis.players.get(player)
            if not pst:
                return action
            route = pst.get("route")
            routes = chassis.routes
            if route not in routes:
                return action
            tape = routes[route]

            def tape_cmd(t, unit):
                if t < 0 or t >= len(tape):
                    return ["PASS"]
                a = tape[t] if isinstance(tape[t], dict) else {}
                cmds = [a.get("farmer") or ["PASS"]] + list(a.get("hands") or [])
                if unit < len(cmds):
                    return cmds[unit] or ["PASS"]
                return ["PASS"]

            def tape_idle_window(unit, t, k=3):
                for dt in range(0, k):
                    if not is_pass(tape_cmd(t + dt, unit)):
                        return False
                return True

            hands = [list(h) if h else ["PASS"] for h in (action.get("hands") or [])]
            farmer = list(action.get("farmer") or ["PASS"])
            cmds = [farmer] + hands
            priv = obs.get("private") or {}
            seeds = priv.get("seeds") or {}
            farms = obs.get("farms") or []
            farm = farms[player] if player < len(farms) else {}
            pos = [tuple(farm.get("farmer") or (4, 4))] + [tuple(p) for p in farm.get("hands") or []]
            changed = False
            # find truly idle unit by tape
            for unit in range(min(len(cmds), len(pos))):
                if not is_pass(cmds[unit]):
                    continue
                if not tape_idle_window(unit, step, 3):
                    continue
                # find empty non-pasture tile
                target = None
                empties = []
                for y, row in enumerate(farm.get("tiles") or []):
                    for x, t in enumerate(row):
                        if t is None and (x, y) != (2, 4):
                            empties.append((x, y))
                if not empties:
                    continue
                access = ((4, 4), (5, 4), (4, 5), (5, 5))
                empties.sort(key=lambda xy: min(abs(xy[0] - a) + abs(xy[1] - b) for a, b in access))
                target = empties[0]
                # seed?
                if int(seeds.get("WHEAT", 0) or 0) <= 0:
                    money = float(farm.get("money") or 0)
                    if money < 500:
                        continue
                    # buy seed only if tape market this step has room and we're not in opening
                    m = [list(o) for o in (action.get("market") or [])]
                    if len(m) >= 10:
                        continue
                    if any(len(o) >= 2 and o[0] == "BUY_SEED" for o in m):
                        continue
                    m.append(["BUY_SEED", "WHEAT", 1])
                    action = dict(action, market=m)
                px, py = pos[unit]
                tx, ty = target
                if (px, py) != (tx, ty):
                    if px < tx:
                        cmd = ["EAST"]
                    elif px > tx:
                        cmd = ["WEST"]
                    elif py < ty:
                        cmd = ["SOUTH"]
                    else:
                        cmd = ["NORTH"]
                else:
                    tile = farm["tiles"][ty][tx]
                    if tile is None and int(seeds.get("WHEAT", 0) or 0) > 0:
                        cmd = ["PLANT", "WHEAT"]
                        st["planted"] = True
                    elif isinstance(tile, dict) and tile.get("crop") == "WHEAT":
                        if not tile.get("watered_today"):
                            cmd = ["WATER"]
                        elif int(tile.get("yield_units") or 0) > 0:
                            cmd = ["HARVEST"]
                        else:
                            cmd = ["PASS"]
                    else:
                        cmd = ["PASS"]
                if cmd == ["PASS"]:
                    continue
                if unit == 0:
                    farmer = cmd
                else:
                    hands[unit - 1] = cmd
                changed = True
                st["fires"] += 1
                break  # one unit per turn
            if changed:
                action = dict(action, farmer=farmer, hands=hands)
            return action
        except Exception:
            return action

    return agent


def series(factory, opp_path, opp_name, seeds, label):
    """factory(tag) -> callable agent"""
    rows, margins, wins, n = [], [], 0, 0
    for seed in seeds:
        for seat0 in (True, False):
            tag = f"{label}_{opp_name}_{seed}_{int(seat0)}"
            try:
                c = factory(tag)
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
                print(f"{label} vs {opp_name} s={seed} seat0={seat0} c={cb:.0f} o={ob:.0f} m={m:.0f} win={win}", flush=True)
                rows.append({"seed": seed, "seat0": seat0, "cb": cb, "ob": ob, "margin": m, "win": win})
            except Exception as e:
                print(f"FAIL {label} {opp_name} s={seed} seat0={seat0}: {e}", flush=True)
                rows.append({"seed": seed, "seat0": seat0, "error": str(e)[:200]})
    sm = {
        "label": label, "opp": opp_name, "n": n, "wins": wins,
        "win_rate": round(wins / n, 3) if n else None,
        "mean_margin": round(sum(margins) / len(margins), 1) if margins else None,
    }
    print("SUM", sm, flush=True)
    return rows, sm


def main():
    mutants = {
        "F0_metav4": [],
        "F1_no_feed_skip": [("_R85_FEED = True", "_R85_FEED = False")],
        "F2_no_fert_overlay": [("_R85_FERT = True", "_R85_FERT = False")],
        "F3_no_v219_fert": [("_V219_FERTILIZE = True", "_V219_FERTILIZE = False")],
        "F4_no_quote": [("_R37_QUOTE = True", "_R37_QUOTE = False")],
        "F5_no_adaptive": [("_R37_ADAPTIVE = True", "_R37_ADAPTIVE = False")],
        "F6_herd_loose": [("V9_HERD_MIN_WOOL = 150", "V9_HERD_MIN_WOOL = 100"),
                           ("V9_HERD_MIN_MILK = 150", "V9_HERD_MIN_MILK = 100")],
        "F7_fert_earlier": [("V9_FERT_FIRST_DAY = 14", "V9_FERT_FIRST_DAY = 10")],
        "F8_fert_later": [("V9_FERT_FIRST_DAY = 14", "V9_FERT_FIRST_DAY = 18")],
        "F9_race_tight": [("V9_RACE_MARGIN = 12", "V9_RACE_MARGIN = 4"),
                          ("V9_RACE_DEFAULT = 40", "V9_RACE_DEFAULT = 24")],
        "F10_race_loose": [("V9_RACE_MARGIN = 12", "V9_RACE_MARGIN = 24"),
                           ("V9_RACE_DEFAULT = 40", "V9_RACE_DEFAULT = 48")],
        "F11_courier_early": [("V9_COURIER_FROM_HOUR = 12", "V9_COURIER_FROM_HOUR = 0")],
        "F12_courier_late": [("V9_COURIER_FROM_HOUR = 12", "V9_COURIER_FROM_HOUR = 18")],
        "F13_carrot_early": [("V9_CARROT_FIRST_DAY = 10", "V9_CARROT_FIRST_DAY = 6")],
        "F14_carrot_late": [("V9_CARROT_FIRST_DAY = 10", "V9_CARROT_FIRST_DAY = 14"),
                            ("V9_CARROT_LAST_DAY = 23", "V9_CARROT_LAST_DAY = 20")],
        "F15_feed_days2": [("_CA_FEED_DAYS = 1", "_CA_FEED_DAYS = 2")],
        "F16_price_floor2": [("_R37_PRICE_FLOOR = 1", "_R37_PRICE_FLOOR = 2")],
        "F17_no_horizon_r88": [("_R88_HORIZON = True", "_R88_HORIZON = False")],
        "F18_input_workers1": [("_R51_INPUT_MAX_WORKERS=2", "_R51_INPUT_MAX_WORKERS=1")],
        "F19_input_workers3": [("_R51_INPUT_MAX_WORKERS=2", "_R51_INPUT_MAX_WORKERS=3")],
        "F20_combo_no_feed_no_quote": [("_R85_FEED = True", "_R85_FEED = False"),
                                       ("_R37_QUOTE = True", "_R37_QUOTE = False")],
        "F21_herd_and_fert10": [("V9_HERD_MIN_WOOL = 150", "V9_HERD_MIN_WOOL = 100"),
                                ("V9_FERT_FIRST_DAY = 14", "V9_FERT_FIRST_DAY = 10")],
        "F22_racepx0": [("V9_RACEPX_MARGIN=0", "V9_RACEPX_MARGIN=8")],
        "F23_shed99": [("_CH_SHED=90", "_CH_SHED=99")],
        "F24_v44y_reorder": [("_V44Y_REORDER_GATE=False", "_V44Y_REORDER_GATE=True")],
    }

    # also tape-aware as separate factory using base source ns
    payload = {"variants": {}, "note": "P90 flags + tape-aware; no submit", "updated": time.strftime("%Y-%m-%dT%H:%M:%S")}
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    payload.setdefault("variants", {})

    def make_flag_factory(pairs):
        src = apply_subs(BASE_SRC, pairs) if pairs else BASE_SRC

        def f(tag):
            agent, _ = load_mutant(src, tag)
            return agent

        return f

    # base ns for tape-aware
    base_agent, base_ns = load_mutant(BASE_SRC, "p90_base_ns")

    def make_tape_factory():
        def f(tag):
            agent, ns = load_mutant(BASE_SRC, f"tape_{tag}")
            return wrap_tape_aware(agent, ns)

        return f

    # prioritize: tape-aware + high-signal flags first
    ordered = [
        ("T1_tape_aware", make_tape_factory()),
        ("F1_no_feed_skip", make_flag_factory(mutants["F1_no_feed_skip"])),
        ("F4_no_quote", make_flag_factory(mutants["F4_no_quote"])),
        ("F6_herd_loose", make_flag_factory(mutants["F6_herd_loose"])),
        ("F7_fert_earlier", make_flag_factory(mutants["F7_fert_earlier"])),
        ("F9_race_tight", make_flag_factory(mutants["F9_race_tight"])),
        ("F10_race_loose", make_flag_factory(mutants["F10_race_loose"])),
        ("F11_courier_early", make_flag_factory(mutants["F11_courier_early"])),
        ("F13_carrot_early", make_flag_factory(mutants["F13_carrot_early"])),
        ("F20_combo_no_feed_no_quote", make_flag_factory(mutants["F20_combo_no_feed_no_quote"])),
        ("F21_herd_and_fert10", make_flag_factory(mutants["F21_herd_and_fert10"])),
        ("F0_metav4", make_flag_factory([])),
        ("P16_ctrl", lambda tag: p79.load_quiet(PIPE16, f"p16_{tag}")),
    ]

    for label, fac in ordered:
        if (payload["variants"].get(label) or {}).get("vs_metav4", {}).get("n", 0) >= 4:
            print("SKIP", label, flush=True)
            continue
        print(f"\n===== {label} =====", flush=True)
        r_mv, s_mv = series(fac, METAV4, "metav4", (1, 2), label)
        r_sp, s_sp = series(fac, SHOPV7, "shop_v7", (1, 2), label)
        r_th, s_th = series(fac, THOMAS, "thomas", (1,), label)
        payload["variants"][label] = {
            "vs_metav4": s_mv, "vs_shop_v7": s_sp, "vs_thomas": s_th,
            "rows": r_mv + r_sp + r_th,
        }
        payload["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        wr_mv = s_mv.get("win_rate") or 0
        wr_sp = s_sp.get("win_rate") or 0
        mm = s_mv.get("mean_margin")
        dual = wr_mv >= 0.6 and wr_sp >= 0.5
        # also flag promising if margin positive vs metav4 even if not 60% on 4 games
        interesting = dual or (mm is not None and mm > 20 and wr_sp >= 0.75)
        print(f"DUAL {label}: mv={wr_mv}({mm}) shop={wr_sp}({s_sp.get('mean_margin')}) th={s_th.get('win_rate')} dual={dual} interesting={interesting}", flush=True)
        if dual or interesting:
            print("ESCALATE", label, flush=True)
            r2, s2 = series(fac, METAV4, "metav4_h", (3, 4, 5, 6), label)
            r3, s3 = series(fac, SHOPV7, "shop_h", (3, 4, 5, 6), label)
            payload["variants"][label]["hold_mv"] = s2
            payload["variants"][label]["hold_sp"] = s3
            payload["variants"][label]["holdout_dual"] = (s2.get("win_rate") or 0) >= 0.6 and (s3.get("win_rate") or 0) >= 0.5
            OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"HOLD {label}: mv={s2.get('win_rate')}({s2.get('mean_margin')}) shop={s3.get('win_rate')} dual={payload['variants'][label]['holdout_dual']}", flush=True)

    print("\n==== P90 TABLE ====", flush=True)
    for k, v in payload["variants"].items():
        print(k,
              "mv", (v.get("vs_metav4") or {}).get("win_rate"), (v.get("vs_metav4") or {}).get("mean_margin"),
              "shop", (v.get("vs_shop_v7") or {}).get("win_rate"), (v.get("vs_shop_v7") or {}).get("mean_margin"),
              "th", (v.get("vs_thomas") or {}).get("win_rate"),
              "hold", v.get("holdout_dual"), flush=True)


if __name__ == "__main__":
    main()
