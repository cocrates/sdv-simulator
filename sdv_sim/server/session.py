"""Dashboard session state (dashboard-session-lifecycle, M-4).

A session is ``{events, report, duration_ms, source, snapshots}``:

- ``POST /api/run`` and ``POST /api/load-log`` replace the session.
- The first edit of the open YAML invalidates the session (overlay cleared,
  "replay invalidated" notice). File open / new resets the session.
- Multi-tab: a single server-global session, last-write-wins.

Invalidated/absent sessions answer ``GET /api/events`` and ``GET /api/report``
with ``409 + {error: {code: session_invalid}}`` (v2 spec, F-7).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

SessionSource = Literal["run", "log"]


@dataclass
class Session:
    """One replayable simulation session on the dashboard."""

    source: SessionSource
    events: list[dict[str, Any]]
    report: dict[str, Any]
    duration_ms: int
    arch_content: str | None = None
    scenario_content: str | None = None
    invalidated: bool = False


class SessionStore:
    """Server-global single-session store (last-write-wins, M-4)."""

    def __init__(self) -> None:
        self._session: Session | None = None

    @property
    def current(self) -> Session | None:
        return self._session

    def replace(self, session: Session) -> None:
        self._session = session

    def invalidate(self) -> None:
        """Mark the current session invalid (first edit of the open YAML)."""
        if self._session is not None:
            self._session.invalidated = True

    def reset(self) -> None:
        """Clear the session (file open / new in the editor)."""
        self._session = None
