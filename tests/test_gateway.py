"""Gateway routing tests (gateway-routing-rules D-07 / communication-event-semantics D-13)."""

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


def _hop_arch(n_links: int) -> Architecture:
    """Linear chain can1 -> ... -> canN with frame ``f`` only on can1.

    No components declare receives, so no rx events occur; ID-range routes
    carry the frame across links (frame keeps its id since no remap).
    """
    nodes = [{"name": f"n{i}"} for i in range(n_links + 1)]
    links = []
    for i in range(1, n_links + 1):
        frames = [make_frame("f", 50, 8, 1000, "n0", message="f")] if i == 1 else []
        links.append(make_link(f"can{i}", "can", 500, [f"n{i - 1}", f"n{i}"], frames=frames))
    routes = [
        {
            "name": f"gw{i}",
            "routes": [
                {
                    "from": {"link": f"can{i}", "id_min": 40, "id_max": 80},
                    "to": {"link": f"can{i + 1}"},
                }
            ],
        }
        for i in range(1, n_links)
    ]
    return make_arch(nodes, links, gateways=routes)


class TestGatewayRouting:
    def test_single_hop_remap_and_target_rx(self) -> None:
        # Explicit-frame route with remap_id: can1 f(id 50) -> can2 id 200.
        # Target link defines its own frame g carrying message "f", so target
        # receivers observe the routed frame (D-13: target receiver rx).
        nodes = [
            {"name": "n1", "components": [make_component("c1")]},
            {"name": "n2", "components": [make_component("c2", receives=["f"])]},
            {"name": "n3", "components": [make_component("c3", receives=["f"])]},
        ]
        l1 = make_link("can1", "can", 500, ["n1", "n2"], frames=[make_frame("f", 50, 8, 1000, "n1", message="f")])
        l2 = make_link("can2", "can", 500, ["n2", "n3"], frames=[make_frame("g", 200, 8, 1000, "n2", message="f")])
        arch = make_arch(
            nodes,
            [l1, l2],
            gateways=[
                {
                    "name": "gw",
                    "routes": [
                        {"from": {"link": "can1", "frame": "f"}, "to": {"link": "can2", "remap_id": 200}}
                    ],
                }
            ],
        )
        scen = make_scenario(duration_ms=10)
        result = Simulator(arch, scen).run()

        # source rx on can1 at t=1; routed tx on can2 at t=1; target rx at t=2
        rx1 = [e for e in result.events if e.type == "rx" and e.link == "can1" and e.frame == "f"]
        assert sorted((e.node, e.t_ms) for e in rx1) == [("n2", 1)]
        tx2 = [e for e in result.events if e.type == "tx" and e.link == "can2" and e.frame == "f"]
        assert len(tx2) == 1 and tx2[0].t_ms == 1
        rx2 = [e for e in result.events if e.type == "rx" and e.link == "can2" and e.frame == "f"]
        # n2 sits on both links (receives the routed frame too); n3 is the far target
        assert sorted((e.node, e.t_ms) for e in rx2) == [("n2", 2), ("n3", 2)]

    def test_route_chaining_multi_hop(self) -> None:
        arch = _hop_arch(n_links=3)
        scen = make_scenario(duration_ms=10)
        result = Simulator(arch, scen).run()

        tx_by_link: dict[str, list[int]] = {}
        for e in result.events:
            if e.type == "tx" and e.frame == "f":
                tx_by_link.setdefault(e.link or "", []).append(e.t_ms)
        # periodic on can1 at 0; routed on can2 at 1; routed on can3 at 2
        assert tx_by_link == {"can1": [0], "can2": [1], "can3": [2]}

    def test_hop_limit_drops(self) -> None:
        # 10-link chain: frame traverses can1..can9 (9 tx); the 10th hop drops.
        arch = _hop_arch(n_links=10)
        scen = make_scenario(duration_ms=20)
        result = Simulator(arch, scen).run()

        tx_count = len([e for e in result.events if e.type == "tx" and e.frame == "f"])
        assert tx_count == 9
        drops = [e for e in result.events if e.type == "drop" and e.frame == "f"]
        assert len(drops) == 1 and drops[0].link == "can10"
        assert result.report.links[-1].drop_count == 1

    def test_no_route_no_forward(self) -> None:
        arch = _hop_arch(n_links=1)  # no gateways at all
        scen = make_scenario(duration_ms=10)
        result = Simulator(arch, scen).run()
        tx_links = {e.link for e in result.events if e.type == "tx"}
        assert tx_links == {"can1"}

    def test_injection_data_forwarded(self) -> None:
        arch = _hop_arch(n_links=2)
        scen = make_scenario(duration_ms=10, messages=[inject(0, "can1", "f", {"v": 7})])
        result = Simulator(arch, scen).run()
        tx2 = [e for e in result.events if e.type == "tx" and e.link == "can2" and e.frame == "f"]
        # the injected data rides the routed frame (the periodic f also routes)
        assert any(e.data == {"v": 7} for e in tx2)
