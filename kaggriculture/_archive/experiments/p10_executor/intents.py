# -*- coding: utf-8 -*-
"""P10.1 Intent API + executor contract."""
from __future__ import annotations

from enum import Enum


class Intent(str, Enum):
    MAINTAIN_PRODUCTION = "MAINTAIN_PRODUCTION"
    SELL_AVAILABLE = "SELL_AVAILABLE"
    LIQUIDATE = "LIQUIDATE"
    RECOVER = "RECOVER"
    CLEAR_WEED = "CLEAR_WEED"
    NOOP = "NOOP"


class Status(str, Enum):
    SUCCESS = "SUCCESS"
    REPAIRED = "REPAIRED"
    NOOP = "NOOP"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"


class ExecutorResult:
    def __init__(self, action, status, repair_used=None, reason="", assumptions=None):
        self.action = action or {"farmer": ["PASS"], "hands": [], "market": []}
        self.status = status
        self.repair_used = repair_used or []
        self.reason = reason
        self.assumptions = assumptions or {}

    def as_dict(self):
        return {
            "action": self.action,
            "status": self.status.value if hasattr(self.status, "value") else self.status,
            "repair_used": list(self.repair_used),
            "reason": self.reason,
            "assumptions": dict(self.assumptions),
        }


PASS_ACTION = {"farmer": ["PASS"], "hands": [], "market": []}
