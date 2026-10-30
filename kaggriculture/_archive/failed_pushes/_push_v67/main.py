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
