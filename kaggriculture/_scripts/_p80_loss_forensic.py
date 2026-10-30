# -*- coding: utf-8 -*-
"""P80: forensic of thomas ladder losses — where money diverges, market vs field."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

REPLAY_DIR = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p77_search\loss_replays")
LOSSES = json.loads(
    Path(r"D:\桌面\Kaggle\kaggriculture\_external\p77_search\thomas_losses.json").read_text(
        encoding="utf-8"
    )
)
TH_SUB = 56358711
OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_research\p80_loss_forensic.json")


def seat_of(agents, sub_id):
    for a in agents:
        if a.get("submissionId") == sub_id:
            return a
    return agents[0]


def analyze_episode(path: Path, our_sub: int, opp_sub: int | None) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    steps = data.get("steps") or data.get("environment") or []
    # kaggle replay schema: usually list of frames with each agent state
    # try common layouts
    if not steps and isinstance(data, list):
        steps = data
    # detect structure
    info = data.get("info") if isinstance(data, dict) else {}
    rewards = data.get("rewards") if isinstance(data, dict) else None
    agents = info.get("Agents") or info.get("agents") or []
    # find steps key
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, list) and v and isinstance(v[0], (list, dict)):
                # likely steps
                if k in ("steps", "environment", "trace", "frames"):
                    steps = v
                    break
        if not steps:
            # some replays nest under "steps"
            steps = data.get("steps", [])

    # identify seats
    team_names = []
    our_seat = 0
    opp_seat = 1
    if agents:
        for i, a in enumerate(agents):
            team_names.append(a.get("teamName") or a.get("Name"))
            if a.get("submissionId") == our_sub:
                our_seat = i
            elif opp_sub and a.get("submissionId") == opp_sub:
                opp_seat = i
    if rewards and len(rewards) == 2:
        our_final, opp_final = rewards[our_seat], rewards[opp_seat]
    else:
        our_final = opp_final = None

    money_series = {0: [], 1: []}
    market_ops = {0: Counter(), 1: Counter()}
    field_ops = {0: Counter(), 1: Counter()}
    first_diverge = None
    day_money = {0: defaultdict(float), 1: defaultdict(float)}

    def parse_state(frame, seat):
        # frame may be list of agent states or dict
        if isinstance(frame, list):
            if seat >= len(frame):
                return None
            st = frame[seat]
        elif isinstance(frame, dict):
            st = frame.get(str(seat)) or frame.get(seat) or frame
        else:
            return None
        if not isinstance(st, dict):
            return None
        obs = st.get("observation") or st.get("obs") or st
        action = st.get("action") or {}
        farm = None
        farms = obs.get("farms") if isinstance(obs, dict) else None
        if isinstance(farms, list) and len(farms) > seat:
            farm = farms[seat]
        money = None
        if isinstance(farm, dict):
            money = farm.get("money")
        elif isinstance(obs, dict) and "money" in obs:
            money = obs.get("money")
        step = None
        if isinstance(obs, dict):
            step = obs.get("step")
        elif isinstance(st, dict):
            step = st.get("step")
        return money, action, step, obs

    n = len(steps)
    for i, frame in enumerate(steps):
        # skip if looks like reward-only terminal
        for seat in (0, 1):
            parsed = parse_state(frame, seat)
            if not parsed:
                continue
            money, action, step, obs = parsed
            if money is not None:
                money_series[seat].append(float(money))
                day = int(step) // 24 if step is not None else i // 24
                day_money[seat][day] = float(money)
            if isinstance(action, dict):
                for o in action.get("market") or []:
                    if o and o[0] in ("SELL", "BUY_PRODUCT", "BUY_SEED", "HIRE", "BUY_ANIMAL", "BUY_LAND"):
                        market_ops[seat][o[0]] += 1
                for o in [action.get("farmer")] + list(action.get("hands") or []):
                    if o and isinstance(o, list) and o:
                        field_ops[seat][o[0]] += 1
        # first money diverge when both present
        if len(money_series[0]) == len(money_series[1]) and money_series[0]:
            if first_diverge is None and abs(money_series[0][-1] - money_series[1][-1]) > 2000:
                first_diverge = {
                    "frame": i,
                    "our": money_series[0][-1],
                    "opp": money_series[1][-1],
                    "delta": money_series[0][-1] - money_series[1][-1],
                }

    def series_stats(s):
        if not s:
            return None
        return {
            "n": len(s),
            "start": s[0],
            "end": s[-1],
            "min": min(s),
            "max": max(s),
            "peak_frame": s.index(max(s)),
        }

    # day-end gaps last 7 days
    gaps = []
    for d in sorted(set(day_money[0]) | set(day_money[1])):
        if d in day_money[0] and d in day_money[1]:
            gaps.append(
                {
                    "day": d,
                    "our": day_money[0][d],
                    "opp": day_money[1][d],
                    "gap": day_money[0][d] - day_money[1][d],
                }
            )

    return {
        "file": path.name,
        "team_names": team_names,
        "our_seat": our_seat,
        "opp_seat": opp_seat,
        "rewards": rewards,
        "our_final": our_final,
        "opp_final": opp_final,
        "n_frames": n,
        "our_money": series_stats(money_series[our_seat] if our_seat in money_series else money_series[0]),
        "opp_money": series_stats(money_series[opp_seat] if opp_seat in money_series else money_series[1]),
        "first_diverge": first_diverge,
        "market_ops_our": dict(market_ops[our_seat]),
        "market_ops_opp": dict(market_ops[opp_seat]),
        "field_ops_our": dict(field_ops[our_seat]),
        "field_ops_opp": dict(field_ops[opp_seat]),
        "day_gaps_tail": gaps[-8:] if gaps else [],
        "day_gaps_all_n": len(gaps),
    }


def main():
    reports = []
    for loss in LOSSES:
        eid = loss["episode_id"]
        # find replay file
        cands = list(REPLAY_DIR.glob(f"*{eid}*"))
        if not cands:
            reports.append({"episode_id": eid, "error": "replay_missing"})
            print("missing replay", eid)
            continue
        path = cands[0]
        print("analyze", path.name, "size", path.stat().st_size, flush=True)
        try:
            rep = analyze_episode(path, TH_SUB, loss.get("opp_sub"))
            rep["meta"] = loss
            reports.append(rep)
            # compact print
            print(
                f"  opp={loss.get('opp_team')} margin={loss.get('margin')} "
                f"frames={rep.get('n_frames')} diverge={rep.get('first_diverge')}",
                flush=True,
            )
            print(f"  market_our={rep.get('market_ops_our')} market_opp={rep.get('market_ops_opp')}", flush=True)
            print(f"  day_gaps_tail={rep.get('day_gaps_tail')}", flush=True)
        except Exception as e:
            reports.append({"episode_id": eid, "error": str(e)[:300], "meta": loss})
            print("  FAIL", e, flush=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(reports, indent=2, ensure_ascii=False), encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
