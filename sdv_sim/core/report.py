"""Result report models (result-report-schema, D-21)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SimulationSummary:
    duration_ms: int
    result: str  # "pass" | "fail"
    event_count: int


@dataclass(frozen=True)
class LinkReport:
    name: str
    kind: str
    tx_count: int
    rx_count: int
    drop_count: int
    supersede_count: int
    bus_load_percent: float


@dataclass(frozen=True)
class TaskReport:
    node: str
    task: str
    period_ms: int
    run_count: int
    overrun_count: int


@dataclass(frozen=True)
class AssertionResult:
    name: str
    status: str  # "pass" | "fail"
    detail: str


@dataclass(frozen=True)
class Report:
    simulation: SimulationSummary
    links: list[LinkReport] = field(default_factory=list)
    tasks: list[TaskReport] = field(default_factory=list)
    assertions: list[AssertionResult] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
