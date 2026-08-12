"""CAN fidelity model tests (can-fidelity-model, D-05 / ASR-004)."""

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
    make_task,
)


def _can_arch(bitrate: int = 500, frames: list | None = None) -> Architecture:
    if frames is None:
        frames = [
            make_frame("a", 10, 1, 1000, "n1", message="a"),
            make_frame("b", 100, 1, 1000, "n1", message="b"),
        ]
    receives = [f.message if f.message is not None else f.name for f in frames]
    nodes = [
        {"name": "n1", "components": [make_component("c1")]},
        {"name": "n2", "components": [make_component("c2", receives=receives)]},
    ]
    link = make_link("can1", "can", bitrate, ["n1", "n2"], frames=frames)
    return make_arch(nodes, [link])


class TestCanTiming:
    def test_tx_ms_formula(self) -> None:
        # ceil((44 + 8*DLC) / bitrate_kbps)
        arch = _can_arch()
        scen = make_scenario(duration_ms=1, messages=[])
        sim = Simulator(arch, scen)
        assert sim._links["can1"].tx_ms(sim._links["can1"].frames["a"]) == 1  # ceil(52/500) = 1
        assert sim._links["can1"].tx_ms(sim._links["can1"].frames["b"]) == 1

    def test_dlc8_formula(self) -> None:
        arch = _can_arch(frames=[make_frame("a", 10, 8, 1000, "n1", message="a")])
        sim = Simulator(arch, make_scenario(duration_ms=1))
        assert sim._links["can1"].tx_ms(sim._links["can1"].frames["a"]) == 1  # ceil(108/500) = 1


class TestCanArbitration:
    def test_lower_id_wins_when_same_tick(self) -> None:
        # Both periodic frames fire at t=0; lower ID must transmit first.
        arch = _can_arch()
        scen = make_scenario(duration_ms=10)
        result = Simulator(arch, scen).run()

        tx = [e for e in result.events if e.type == "tx" and e.link == "can1"]
        assert tx[0].frame == "a" and tx[0].t_ms == 0
        assert tx[1].frame == "b" and tx[1].t_ms == 1  # queued behind the winner

        rx = [e for e in result.events if e.type == "rx" and e.link == "can1"]
        assert rx[0].frame == "a" and rx[0].t_ms == 1
        assert rx[1].frame == "b" and rx[1].t_ms == 2

    def test_rx_only_to_receives_mapped_nodes(self) -> None:
        # n2's component receives a+b; n1 receives nothing -> rx only on n2.
        arch = _can_arch()
        scen = make_scenario(duration_ms=10)
        result = Simulator(arch, scen).run()
        rx_nodes = {e.node for e in result.events if e.type == "rx"}
        assert rx_nodes == {"n2"}

    def test_supersede_queued_same_frame(self) -> None:
        # Slow bus (10 kbps, dlc 8 -> tx = 11ms) with a 1ms-period frame:
        # later instances must replace the queued one (D-18) instead of stacking.
        frames = [make_frame("a", 10, 8, 1, "n1", message="a")]
        arch = _can_arch(bitrate=10, frames=frames)
        scen = make_scenario(duration_ms=11)
        result = Simulator(arch, scen).run()
        link_report = result.report.links[0]
        assert link_report.tx_count == 2  # t=0 instance + final (t=11) instance
        assert link_report.supersede_count == 10  # t=1..11 replaced the queued one
        assert link_report.drop_count == 0

    def test_bus_load_percent(self) -> None:
        arch = _can_arch()
        scen = make_scenario(duration_ms=10)
        result = Simulator(arch, scen).run()
        # frames a,b at t=0 only (period 1000 > duration): 2 tx * 1ms / 10ms
        assert result.report.links[0].bus_load_percent == 20.0
