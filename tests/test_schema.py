"""Schema-level validation tests (D-12 field tree, ASR-003)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from sdv_sim.core.engine import Simulator
from sdv_sim.schema.arch import Architecture, FromRef, LinkDef
from sdv_sim.schema.scenario import Scenario

from conftest import (
    expect,
    inject,
    make_arch,
    make_component,
    make_frame,
    make_link,
    make_scenario,
    make_task,
)


class TestArchitectureSchema:
    def test_duplicate_node_name_rejected(self) -> None:
        nodes = [
            {"name": "n1", "type": "ECU"},
            {"name": "n1", "type": "HPC"},
        ]
        with pytest.raises(ValidationError, match="duplicate node name"):
            Architecture(nodes=nodes, links=[], gateways=[])

    def test_duplicate_frame_name_rejected(self) -> None:
        link = make_link(
            "l1", "can", 500, ["n1", "n2"],
            frames=[
                make_frame("f1", 10, 8, 100, "n1"),
                make_frame("f1", 20, 8, 100, "n1"),
            ],
        )
        with pytest.raises(ValidationError, match="duplicate frame name"):
            make_arch(
                [{"name": "n1"}, {"name": "n2"}],
                [link],
            )

    def test_unknown_link_node_rejected(self) -> None:
        link = make_link("l1", "can", 500, ["n1", "ghost"])
        with pytest.raises(ValidationError, match="unknown node"):
            make_arch([{"name": "n1"}], [link])

    def test_frame_source_must_be_connected(self) -> None:
        link = make_link(
            "l1", "can", 500, ["n1", "n2"],
            frames=[make_frame("f1", 10, 8, 100, "ghost")],
        )
        with pytest.raises(ValidationError, match="not connected"):
            make_arch([{"name": "n1"}, {"name": "n2"}], [link])

    def test_route_from_requires_frame_or_range(self) -> None:
        with pytest.raises(ValidationError, match="either frame or"):
            FromRef(link="l1")

    def test_route_from_frame_must_exist(self) -> None:
        link = make_link(
            "l1", "can", 500, ["n1", "n2"],
            frames=[make_frame("f1", 10, 8, 100, "n1")],
        )
        with pytest.raises(ValidationError, match="not defined on link"):
            make_arch(
                [{"name": "n1"}, {"name": "n2"}],
                [link],
                gateways=[{"name": "gw", "routes": [{"from": {"link": "l1", "frame": "nope"}, "to": {"link": "l1"}}]}],
            )

    def test_component_message_must_map_to_connected_frame(self) -> None:
        link = make_link(
            "l1", "can", 500, ["n1", "n2"],
            frames=[make_frame("f1", 10, 8, 100, "n1", message="ok")],
        )
        node = {"name": "n1", "type": "ECU", "components": [make_component("c", sends=["bad"])]}
        with pytest.raises(ValidationError, match="does not map to a frame"):
            make_arch([node, {"name": "n2"}], [link])

    def test_extra_fields_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Architecture(nodes=[{"name": "n1", "bogus": 1}], links=[], gateways=[])


class TestScenarioSchema:
    def test_duration_required(self) -> None:
        with pytest.raises(ValidationError):
            Scenario(schema_version=1)

    def test_negative_duration_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Scenario(duration_ms=-1)

    def test_extra_field_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Scenario(duration_ms=10, bogus=1)


class TestEngineScenarioValidation:
    def test_injection_unknown_link(self) -> None:
        from sdv_sim.core.errors import SdvSimInputError

        arch = make_arch(
            [{"name": "n1"}, {"name": "n2"}],
            [make_link("l1", "can", 500, ["n1", "n2"], frames=[make_frame("f1", 10, 8, 100, "n1")])],
        )
        scen = make_scenario(messages=[inject(0, "nope", "f1")])
        with pytest.raises(SdvSimInputError, match="unknown link"):
            Simulator(arch, scen)

    def test_injection_unknown_frame(self) -> None:
        from sdv_sim.core.errors import SdvSimInputError

        arch = make_arch(
            [{"name": "n1"}, {"name": "n2"}],
            [make_link("l1", "can", 500, ["n1", "n2"], frames=[make_frame("f1", 10, 8, 100, "n1")])],
        )
        scen = make_scenario(messages=[inject(0, "l1", "nope")])
        with pytest.raises(SdvSimInputError, match="not defined"):
            Simulator(arch, scen)

    def test_assertion_unknown_reference(self) -> None:
        from sdv_sim.core.errors import SdvSimInputError

        arch = make_arch(
            [{"name": "n1"}, {"name": "n2"}],
            [make_link("l1", "can", 500, ["n1", "n2"], frames=[make_frame("f1", 10, 8, 100, "n1")])],
        )
        scen = make_scenario(assertions=[expect(event="tx", link="nope", count=1)])
        with pytest.raises(SdvSimInputError, match="unknown link"):
            Simulator(arch, scen)


class TestYamlLoad:
    def test_unknown_link_task_defs(self) -> None:
        """Task fields parse correctly through the pydantic model."""
        task = make_task("t", 10, 1, 5)
        comp = make_component("c", tasks=[task])
        assert comp.tasks[0].wcet_ms == 5
