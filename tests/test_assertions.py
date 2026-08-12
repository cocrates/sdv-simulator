"""Assertion evaluation tests (assertion-grammar D-03 / assertion-evaluation-detail D-20)."""

from __future__ import annotations

from sdv_sim.core.engine import Simulator
from sdv_sim.schema.arch import Architecture

from conftest import (
    expect,
    make_arch,
    make_component,
    make_frame,
    make_link,
    make_scenario,
)


def _arch() -> Architecture:
    nodes = [
        {"name": "n1", "components": [make_component("c1")]},
        {"name": "n2", "components": [make_component("c2", receives=["temp"])]},
    ]
    link = make_link(
        "can1", "can", 500, ["n1", "n2"],
        frames=[make_frame("temp_frame", 10, 8, 100, "n1", message="temp")],
    )
    return make_arch(nodes, [link])


class TestAssertionEvaluation:
    def test_count_is_minimum_over_whole_log(self) -> None:
        # frame period 100ms, duration 1000ms -> 11 tx (t=0..1000 inclusive)
        result = Simulator(_arch(), make_scenario(duration_ms=1000, assertions=[expect(event="tx", count=11)])).run()
        assert result.report.simulation.result == "pass"
        assert result.assertions[0].status == "pass"

        result2 = Simulator(_arch(), make_scenario(duration_ms=1000, assertions=[expect(event="tx", count=12)])).run()
        assert result2.assertions[0].status == "fail"

    def test_at_ms_exact_and_within(self) -> None:
        arch = _arch()  # tx at t=0 -> rx at t=1
        exact = Simulator(arch, make_scenario(duration_ms=10, assertions=[expect(event="rx", node="n2", at_ms=1, within_ms=0)])).run()
        assert exact.assertions[0].status == "pass"

        off = Simulator(arch, make_scenario(duration_ms=10, assertions=[expect(event="rx", node="n2", at_ms=2, within_ms=0)])).run()
        assert off.assertions[0].status == "fail"

        within = Simulator(arch, make_scenario(duration_ms=10, assertions=[expect(event="rx", node="n2", at_ms=5, within_ms=4)])).run()
        assert within.assertions[0].status == "pass"

    def test_at_ms_omitted_is_time_independent(self) -> None:
        arch = _arch()  # rx at t=1 only within 10ms
        scen = make_scenario(
            duration_ms=10,
            assertions=[expect(event="rx", node="n2", count=1)],
        )
        result = Simulator(arch, scen).run()
        assert result.assertions[0].status == "pass"

    def test_message_matching(self) -> None:
        arch = _arch()
        scen = make_scenario(duration_ms=10, assertions=[expect(event="rx", message="temp", count=1)])
        result = Simulator(arch, scen).run()
        assert result.assertions[0].status == "pass"

    def test_task_event_matching(self) -> None:
        nodes = [
            {
                "name": "n1",
                "components": [
                    make_component("c1", tasks=[{"name": "sense", "period_ms": 10, "priority": 1, "wcet_ms": 0}])
                ],
            }
        ]
        arch = make_arch(nodes, [])
        scen = make_scenario(
            duration_ms=10,
            assertions=[expect(event="task", node="n1", task="sense", count=2)],
        )
        result = Simulator(arch, scen).run()
        assert result.assertions[0].status == "pass"

    def test_first_match_basis_for_time(self) -> None:
        # rx at t=1, 11, 21, ...: at_ms=1 must pass on the FIRST match (D-20).
        nodes = [
            {"name": "n1", "components": [make_component("c1")]},
            {"name": "n2", "components": [make_component("c2", receives=["temp"])]},
        ]
        arch = make_arch(
            nodes,
            [
                make_link(
                    "can1", "can", 500, ["n1", "n2"],
                    frames=[make_frame("temp_frame", 10, 8, 10, "n1", message="temp")],
                )
            ],
        )
        scen = make_scenario(duration_ms=30, assertions=[expect(event="rx", node="n2", at_ms=1, within_ms=0, count=3)])
        result = Simulator(arch, scen).run()
        assert result.assertions[0].status == "pass"

    def test_failure_detail_reports_match(self) -> None:
        arch = _arch()
        scen = make_scenario(duration_ms=10, assertions=[expect(event="rx", node="n2", at_ms=99, within_ms=0, count=1)])
        result = Simulator(arch, scen).run()
        a = result.assertions[0]
        assert a.status == "fail"
        assert "expected t" in a.detail and "found t=1" in a.detail
