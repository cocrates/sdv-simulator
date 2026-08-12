"""Task scheduling / app runtime tests (task-scheduling-policy D-08, task-overrun-policy D-17)."""

from __future__ import annotations

from sdv_sim.core.engine import Simulator
from sdv_sim.schema.arch import Architecture

from conftest import (
    make_arch,
    make_component,
    make_link,
    make_scenario,
    make_task,
)


def _task_arch(tasks: list) -> Architecture:
    nodes = [{"name": "n1", "components": [make_component("c1", tasks=tasks)]}]
    return make_arch(nodes, [])


class TestTaskScheduling:
    def test_periodic_runs(self) -> None:
        arch = _task_arch([make_task("t", period_ms=10, priority=1, wcet_ms=0)])
        result = Simulator(arch, make_scenario(duration_ms=50)).run()
        report = result.report.tasks[0]
        assert report.run_count == 6  # t=0,10,20,30,40,50 (inclusive end)

    def test_priority_order_at_same_tick(self) -> None:
        arch = _task_arch(
            [
                make_task("low", period_ms=10, priority=2, wcet_ms=0),
                make_task("high", period_ms=10, priority=1, wcet_ms=0),
            ]
        )
        result = Simulator(arch, make_scenario(duration_ms=10)).run()
        starts = [e.task for e in result.events if e.type == "task_start"]
        assert starts[0] == "high"  # lower priority value runs first (D-19)
        assert starts[1] == "low"

    def test_wcet_advances_time(self) -> None:
        arch = _task_arch([make_task("t", period_ms=10, priority=1, wcet_ms=3)])
        result = Simulator(arch, make_scenario(duration_ms=10)).run()
        events = result.events
        start = next(e for e in events if e.type == "task_start")
        end = next(e for e in events if e.type == "task_end")
        assert start.t_ms == 0 and end.t_ms == 3

    def test_wcet_zero_logs_end_immediately(self) -> None:
        arch = _task_arch([make_task("t", period_ms=10, priority=1, wcet_ms=0)])
        result = Simulator(arch, make_scenario(duration_ms=5)).run()
        start = next(e for e in result.events if e.type == "task_start")
        end = next(e for e in result.events if e.type == "task_end")
        assert start.t_ms == 0 and end.t_ms == 0


class TestTaskOverrun:
    def test_overrun_detected_and_absolute_period_kept(self) -> None:
        # wcet 15 > period 10: instance at t=10 is skipped, next runs at t=20
        # (absolute schedule, D-17). Overrun recorded at wcet end t=15.
        arch = _task_arch([make_task("t", period_ms=10, priority=1, wcet_ms=15)])
        result = Simulator(arch, make_scenario(duration_ms=50)).run()
        report = result.report.tasks[0]
        assert report.run_count == 3  # t=0, 20, 40
        assert report.overrun_count == 2  # wcet ends at 15 and 35

        starts = [e.t_ms for e in result.events if e.type == "task_start"]
        assert starts == [0, 20, 40]
        overruns = [e.t_ms for e in result.events if e.type == "overrun"]
        assert overruns == [15, 35]
        assert len(result.report.warnings) == 2

    def test_no_overrun_when_wcet_within_period(self) -> None:
        arch = _task_arch([make_task("t", period_ms=10, priority=1, wcet_ms=5)])
        result = Simulator(arch, make_scenario(duration_ms=20)).run()
        report = result.report.tasks[0]
        assert report.overrun_count == 0
        assert not [e for e in result.events if e.type == "overrun"]
