# Modified by mohui666 in 2026; see NOTICE for the change summary.
"""Sanitized v66 Kaggriculture submission."""
from candidate_v66_meta_closed_loop import agent as _raw_agent
from kaggriculture_agent.env.adapter import sanitize_action

_OBSERVATION_ERRORS = (AttributeError, IndexError, KeyError, TypeError, ValueError)


def agent(obs, configuration=None):
    try:
        return sanitize_action(_raw_agent(obs, configuration), obs, configuration)
    except _OBSERVATION_ERRORS:
        return {"farmer": ["PASS"], "hands": [], "market": []}


# ---------------------------------------------------------------------------
# V66_R7_FERT: market-only fertilizer sell boost (no unit-action stealing)
# ---------------------------------------------------------------------------
_R7_PARENT = agent
_R7_MIN_STOCK = 6
_R7_MIN_PRICE = 2


def _r7_fert(obs, action):
    step = int(obs.get("step") or 0)
    if step >= 716 or step < 96:
        return action
    private = obs.get("private") or {}
    shed = private.get("shed") or {}
    stock = int(shed.get("FERTILIZER") or 0)
    if stock < _R7_MIN_STOCK:
        return action
    prices = ((obs.get("market") or {}).get("prices") or {})
    price = int(prices.get("FERTILIZER") or 1)
    if price < _R7_MIN_PRICE:
        return action
    market = [list(o) for o in (action.get("market") or [])]
    already = sum(
        int(o[2] or 0) for o in market if o and o[0] == "SELL" and len(o) > 2 and o[1] == "FERTILIZER"
    )
    excess = stock - already
    if excess < 4 or len(market) >= 10:
        return action
    merged = False
    for o in market:
        if o and o[0] == "SELL" and len(o) > 2 and o[1] == "FERTILIZER":
            o[2] = int(o[2] or 0) + excess
            merged = True
            break
    if not merged:
        market.append(["SELL", "FERTILIZER", excess])
    result = dict(action)
    result["market"] = market[:10]
    return result


def agent(observation, configuration=None):
    action = _R7_PARENT(observation, configuration)
    try:
        return _r7_fert(observation, action)
    except Exception:
        return action
