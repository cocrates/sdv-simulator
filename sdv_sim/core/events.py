"""Simulation event model (event-log-schema, type enum of 7)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

EVENT_TYPES = ("tx", "rx", "task_start", "task_end", "drop", "overrun", "log")


@dataclass(frozen=True)
class Event:
    """One deterministic simulation event.

    ``(t_ms, seq)`` forms a complete order. Fields that do not apply to an
    event type are ``None`` and omitted from the JSON log.
    """

    t_ms: int
    seq: int
    type: str
    node: str | None = None
    link: str | None = None
    frame: str | None = None
    task: str | None = None
    data: Any = None
