"""Dashboard session state (dashboard-session-lifecycle, M-4).

A session is ``{events, report, duration_ms, source}``:

- ``POST /api/run`` and ``POST /api/load-log`` replace the session.
- Session invalidation on edit is a **frontend-local** state
  (``SessionMeta.invalidated`` — set when editing starts, T-024). The server
  does not derive invalidation from ``POST /api/validate`` calls; validate is
  pure validation. Absent sessions answer ``GET /api/events`` and
  ``GET /api/report`` with ``409 + {error: {code: session_invalid}}`` (v2 spec,
  F-7 — "세션 없음" 케이스).
- Multi-tab: a single server-global session, last-write-wins.
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


class SessionStore:
    """Server-global single-session store (last-write-wins, M-4)."""

    def __init__(self) -> None:
        self._session: Session | None = None

    @property
    def current(self) -> Session | None:
        return self._session

    def replace(self, session: Session) -> None:
        self._session = session

    def reset(self) -> None:
        """Clear the session (file open / new in the editor)."""
        self._session = None
