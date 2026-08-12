"""Tests for the v2 YAML string input API (core-yaml-string-input, D-15).

``loads(arch_yaml, scenario_yaml)`` and ``Simulator.load_scenario_yaml`` let the
v2 dashboard server parse browser-provided YAML content without touching the
filesystem. Diagnostics use the pseudo identifiers ``arch`` / ``scenario`` with
line numbers mapped against the supplied text (v2 spec, Decisions).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sdv_sim.core.engine import load, loads
from sdv_sim.core.errors import SdvSimInputError

SAMPLES = Path(__file__).resolve().parents[1] / "samples" / "basic"

ARCH_YAML = (SAMPLES / "architecture.yaml").read_text(encoding="utf-8")
SCENARIO_YAML = (SAMPLES / "scenario.yaml").read_text(encoding="utf-8")


def _event_keys(result) -> list[tuple[int, int, str]]:
    return [(e.t_ms, e.seq, e.type) for e in result.events]


def test_loads_equals_load_from_files() -> None:
    """String input produces the identical deterministic result as file input."""
    from_path = load(
        SAMPLES / "architecture.yaml",
        SAMPLES / "scenario.yaml",
    ).run()
    from_string = loads(ARCH_YAML, SCENARIO_YAML).run()

    assert _event_keys(from_string) == _event_keys(from_path)
    assert from_string.report == from_path.report
    assert from_string.duration_ms == from_path.duration_ms
    assert from_string.assertions == from_path.assertions


def test_loads_arch_parse_error_uses_pseudo_identifier() -> None:
    bad_arch = "nodes:\n  - name: x\n   bad_indent: [\n"
    with pytest.raises(SdvSimInputError) as excinfo:
        loads(bad_arch, SCENARIO_YAML)
    exc = excinfo.value
    assert exc.code == "yaml_parse_error"
    assert exc.filename == "arch"
    assert exc.line is not None and exc.line >= 1


def test_loads_scenario_parse_error_uses_pseudo_identifier() -> None:
    bad_scenario = "duration_ms: 10\nmessages: [\n"
    with pytest.raises(SdvSimInputError) as excinfo:
        loads(ARCH_YAML, bad_scenario)
    exc = excinfo.value
    assert exc.code == "yaml_parse_error"
    assert exc.filename == "scenario"
    assert exc.line is not None and exc.line >= 1


def test_loads_schema_error_maps_line_and_field() -> None:
    # schema_version 999 violates nothing; a missing required field does.
    bad_arch = (
        "schema_version: 1\n"
        "nodes:\n"
        "  - name: body_ecu\n"
        "    type: WRONG\n"  # invalid literal -> schema error at this line
        "links: []\n"
    )
    with pytest.raises(SdvSimInputError) as excinfo:
        loads(bad_arch, SCENARIO_YAML)
    exc = excinfo.value
    assert exc.code == "schema_error"
    assert exc.filename == "arch"
    assert exc.field is not None and "type" in exc.field


def test_loads_reference_validation_runs() -> None:
    """Scenario reference checks (unknown link) still apply on the string path."""
    bad_scenario = (
        "schema_version: 1\n"
        "duration_ms: 10\n"
        "messages:\n"
        "  - { t_ms: 5, link: nope, frame: door_cmd }\n"
    )
    with pytest.raises(SdvSimInputError) as excinfo:
        loads(ARCH_YAML, bad_scenario)
    assert excinfo.value.code == "injection_unknown_link"
    assert excinfo.value.filename == "scenario"


def test_load_scenario_yaml_replaces_and_validates() -> None:
    sim = loads(ARCH_YAML, SCENARIO_YAML)
    first = sim.run()
    # A second, shorter scenario replaces the first (v1 semantics).
    replacement = "schema_version: 1\nduration_ms: 5\nmessages: []\nassertions: []\n"
    sim.load_scenario_yaml(replacement)
    second = sim.run()
    assert second.duration_ms == 5
    assert second.report.simulation.duration_ms == 5
    assert len(second.events) < len(first.events)

    # Reference validation against the architecture still runs.
    with pytest.raises(SdvSimInputError) as excinfo:
        sim.load_scenario_yaml(
            "schema_version: 1\nduration_ms: 5\n"
            "messages: [{ t_ms: 0, link: missing, frame: door_cmd }]\n"
        )
    assert excinfo.value.code == "injection_unknown_link"
    assert excinfo.value.filename == "scenario"


def test_load_path_api_still_works() -> None:
    """Backward compatibility: the file-path API is unchanged (D-15)."""
    sim = load(SAMPLES / "architecture.yaml", SAMPLES / "scenario.yaml")
    result = sim.run()
    assert result.report.simulation.result == "pass"
