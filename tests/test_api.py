"""Component API / library contract tests (component-api D-09, public-api-contract D-15)."""

from __future__ import annotations

import pytest

from sdv_sim.core.component import Component, Message, TaskContext
from sdv_sim.core.engine import Simulator
from sdv_sim.schema.arch import Architecture

from conftest import (
    make_arch,
    make_component,
    make_frame,
    make_link,
    make_scenario,
    make_task,
)


class Sensor(Component):
    """Registers via class_name='Sensor'."""

    def __init__(self) -> None:
        self.send_count = 0

    def on_periodic(self, ctx: TaskContext) -> None:
        self.send_count += 1
        ctx.send("temp", {"v": ctx.now_ms()})
        ctx.log(f"sensed at {ctx.now_ms()}")


class Receiver(Component):
    """Registers via class_name='Receiver'; logs every received message."""

    def on_message(self, ctx: TaskContext, message: Message) -> None:
        ctx.log(f"got {message.name}")


def _arch() -> Architecture:
    nodes = [
        {
            "name": "n1",
            "components": [
                make_component(
                    "sensor",
                    sends=["temp"],
                    tasks=[make_task("sense", period_ms=10, priority=1, wcet_ms=0)],
                    class_name="Sensor",
                )
            ],
        },
        {
            "name": "n2",
            "components": [make_component("receiver", receives=["temp"], class_name="Receiver")],
        },
    ]
    link = make_link(
        "can1", "can", 500, ["n1", "n2"],
        frames=[make_frame("temp_frame", 10, 8, 1000, "n1", message="temp")],
    )
    return make_arch(nodes, [link])


class TestComponentApi:
    def test_component_send_via_taskcontext(self) -> None:
        arch = _arch()
        scen = make_scenario(duration_ms=100)
        result = Simulator(arch, scen, {"Sensor": Sensor, "Receiver": Receiver}).run()

        link = result.report.links[0]
        # 1 periodic tx (t=0, period 1000) + 11 component sends (t=0..100)
        assert link.tx_count == 12
        # rx for the t=100 send would land at t=101 > duration -> not processed
        assert link.rx_count == 11

        logs = [e for e in result.events if e.type == "log"]
        assert sum(1 for e in logs if e.data and "sensed at" in str(e.data)) == 11
        assert sum(1 for e in logs if e.data and str(e.data).startswith("got temp")) == 11

    def test_stub_component_does_not_auto_send(self) -> None:
        # Same arch but NO classes registered: base Component is a no-op,
        # so only the periodic frame transmits (D-14 stub = receiver-only).
        arch = _arch()
        scen = make_scenario(duration_ms=100)
        result = Simulator(arch, scen).run()

        link = result.report.links[0]
        assert link.tx_count == 1  # only the periodic frame at t=0
        assert not [e for e in result.events if e.type == "log"]
        # task still runs (base on_periodic is a no-op)
        assert len([e for e in result.events if e.type == "task_start"]) == 11

    def test_determinism(self) -> None:
        arch = _arch()
        scen = make_scenario(duration_ms=50)
        r1 = Simulator(arch, scen, {"Sensor": Sensor, "Receiver": Receiver}).run()
        r2 = Simulator(arch, scen, {"Sensor": Sensor, "Receiver": Receiver}).run()
        assert [(e.t_ms, e.seq, e.type, e.node, e.link, e.frame, e.task) for e in r1.events] == [
            (e.t_ms, e.seq, e.type, e.node, e.link, e.frame, e.task) for e in r2.events
        ]

    def test_load_scenario_replaces(self, tmp_path) -> None:
        import yaml

        arch = _arch()
        sim = Simulator(arch, make_scenario(duration_ms=10))
        # load_scenario takes a YAML path (D-15)
        scen_file = tmp_path / "scenario.yaml"
        scen_file.write_text(
            yaml.safe_dump({"duration_ms": 20, "messages": [], "assertions": []}),
            encoding="utf-8",
        )
        sim.load_scenario(scen_file)
        result = sim.run()
        assert result.duration_ms == 20

    def test_unknown_message_send_raises(self) -> None:
        from sdv_sim.core.component import TaskContext

        class Bad(Component):
            def on_periodic(self, ctx: TaskContext) -> None:
                ctx.send("nope", None)

        arch = _arch()
        with pytest.raises(RuntimeError, match="unknown message"):
            Simulator(arch, make_scenario(duration_ms=10), {"Sensor": Bad}).run()


def test_message_dataclass():
    from sdv_sim.core.component import Message

    m = Message(name="temp", frame="temp_frame", link="can1", node="n2", data={"v": 1}, t_ms=5)
    assert m.name == "temp" and m.t_ms == 5
