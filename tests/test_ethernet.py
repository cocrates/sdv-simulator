"""Ethernet fidelity model tests (ethernet-fidelity-model, D-06 / ASR-004)."""

from __future__ import annotations

from sdv_sim.core.engine import Simulator
from sdv_sim.schema.arch import Architecture

from conftest import (
    inject,
    make_arch,
    make_component,
    make_frame,
    make_link,
    make_scenario,
)


def _eth_arch(queue_depth: int = 1000) -> Architecture:
    nodes = [
        {"name": "n1", "components": [make_component("c1")]},
        {"name": "n2", "components": [make_component("c2", receives=["a"])]},
        {"name": "n3", "components": [make_component("c3", receives=["a"])]},
    ]
    frames = [
        make_frame("a", 10, 8, 1000, "n1", message="a"),
        make_frame("b", 20, 8, 1000, "n1", message="b"),
        make_frame("c", 30, 8, 1000, "n2", message="c"),
    ]
    link = make_link("eth1", "ethernet", 100, ["n1", "n2", "n3"], frames=frames, queue_depth=queue_depth)
    return make_arch(nodes, [link])


class TestEthernet:
    def test_tx_ms_formula(self) -> None:
        arch = _eth_arch()
        sim = Simulator(arch, make_scenario(duration_ms=1))
        # ceil((8 + 42) * 8 / (100 Mbps * 1000)) = ceil(400/100000) = 1
        assert sim._links["eth1"].tx_ms(sim._links["eth1"].frames["a"]) == 1

    def test_fifo_switch_order(self) -> None:
        # Periodic 'a' fires at t=0 (path 1) alongside three injections;
        # switch FIFO: periodic a, then injected a, b, c back-to-back.
        arch = _eth_arch()
        scen = make_scenario(
            duration_ms=10,
            messages=[inject(0, "eth1", "a"), inject(0, "eth1", "b"), inject(0, "eth1", "c")],
        )
        result = Simulator(arch, scen).run()
        tx = [e for e in result.events if e.type == "tx" and e.link == "eth1"]
        assert [e.frame for e in tx] == ["a", "a", "b", "c"]
        assert [e.t_ms for e in tx] == [0, 1, 2, 3]

    def test_tail_drop_when_queue_full(self) -> None:
        # queue_depth=2. All periodic frames a/b/c (period 1000) fire at t=0
        # (D-13 path 1) alongside the injected a/b/c. per_a transmits; the
        # switch FIFO holds inj_a + per_b, inj_b supersedes per_b (D-18), and
        # both c instances (periodic + injected) tail-drop -> 3 tx, 2 drops.
        arch = _eth_arch(queue_depth=2)
        scen = make_scenario(
            duration_ms=10,
            messages=[inject(0, "eth1", "a"), inject(0, "eth1", "b"), inject(0, "eth1", "c")],
        )
        result = Simulator(arch, scen).run()
        report = result.report.links[0]
        assert report.tx_count == 3
        assert report.drop_count == 2  # periodic c + injected c tail-dropped
        assert report.supersede_count == 1  # injected b replaced periodic b
        drops = [e for e in result.events if e.type == "drop"]
        assert len(drops) == 2 and all(d.frame == "c" and d.t_ms == 0 for d in drops)

    def test_rx_after_switch_completion(self) -> None:
        arch = _eth_arch()
        scen = make_scenario(duration_ms=10, messages=[inject(0, "eth1", "a")])
        result = Simulator(arch, scen).run()
        rx = [e for e in result.events if e.type == "rx" and e.frame == "a"]
        # Both n2 and n3 receive "a" (message mapping); n1 never does.
        assert {e.node for e in rx} == {"n2", "n3"}
        assert all(e.t_ms > 0 for e in rx)  # rx only after the switch completes
