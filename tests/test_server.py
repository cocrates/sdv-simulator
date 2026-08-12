"""Server API contract tests (T-014/T-021) — validate/run/load-log/events/report.

Covers the v2 spec API section: F-4 validation scoping, F-7 409 session_invalid,
F-8 error envelope, M-1 load-log report derivation, M-4 session lifecycle.
The v1 log fixtures use the real CLI log writer (``cli.main._log_document``) so
the format under test is exactly what v1 ``sdv-sim run --log`` produces.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from sdv_sim.cli.main import _log_document
from sdv_sim.core.engine import loads
from sdv_sim.server import create_app
from sdv_sim.server.session import SessionStore

SAMPLES = Path(__file__).resolve().parents[1] / "samples" / "basic"

ARCH_YAML = (SAMPLES / "architecture.yaml").read_text(encoding="utf-8")
SCENARIO_YAML = (SAMPLES / "scenario.yaml").read_text(encoding="utf-8")

# Reference errors (unknown link) are NOT structure errors (F-4).
BAD_SCENARIO_REF = (
    "schema_version: 1\n"
    "duration_ms: 10\n"
    "messages:\n"
    "  - { t_ms: 5, link: nope, frame: door_cmd }\n"
)


@pytest.fixture()
def client() -> TestClient:
    # a fresh store per test keeps session tests isolated (last-write-wins is per app)
    return TestClient(create_app(lang="ko", store=SessionStore()))


@pytest.fixture(scope="module")
def v1_log_doc() -> dict:
    result = loads(ARCH_YAML, SCENARIO_YAML).run()
    return _log_document(result)


def _log_content(doc: dict) -> str:
    return json.dumps(doc, ensure_ascii=False)


# ---------------------------------------------------------------------- validate


def test_validate_architecture_valid(client: TestClient) -> None:
    r = client.post(
        "/api/validate", json={"kind": "architecture", "content": ARCH_YAML}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["valid"] is True
    assert body["errors"] == []


def test_validate_architecture_schema_error_has_path_line(client: TestClient) -> None:
    bad = "nodes:\n  - name: x\n    type: WRONG\nlinks: []\n"
    r = client.post(
        "/api/validate", json={"kind": "architecture", "content": bad}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["valid"] is False
    err = body["errors"][0]
    assert err["path"].startswith("arch")
    assert err["line"] is not None
    assert err["message"]


def test_validate_scenario_alone_skips_reference_checks(client: TestClient) -> None:
    """F-4: scenario alone validates structure only — unknown link is a
    reference error that requires an architecture to detect."""
    r = client.post(
        "/api/validate", json={"kind": "scenario", "content": BAD_SCENARIO_REF}
    )
    assert r.status_code == 200
    assert r.json()["valid"] is True


def test_validate_scenario_with_arch_runs_reference_checks(client: TestClient) -> None:
    r = client.post(
        "/api/validate",
        json={"kind": "scenario", "content": BAD_SCENARIO_REF, "arch": ARCH_YAML},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["valid"] is False
    assert body["errors"][0]["path"].startswith("scenario")


# ----------------------------------------------------------------- run + session


def test_run_creates_session_with_full_report(client: TestClient) -> None:
    r = client.post(
        "/api/run", json={"architecture": ARCH_YAML, "scenario": SCENARIO_YAML}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["duration_ms"] > 0
    assert body["event_count"] > 0
    rep = body["report"]
    assert rep["simulation"]["result"] in ("pass", "fail")
    # run path exposes the FULL v1 Report (M-1)
    assert all("supersede_count" in l for l in rep["links"])
    assert all("bus_load_percent" in l for l in rep["links"])
    assert all("period_ms" in t for t in rep["tasks"])

    ev = client.get("/api/events")
    assert ev.status_code == 200
    events = ev.json()
    assert len(events) == body["event_count"]
    keys = [(e["t_ms"], e["seq"]) for e in events]
    assert keys == sorted(keys)

    rep2 = client.get("/api/report")
    assert rep2.status_code == 200
    assert rep2.json() == rep


def test_run_invalid_yaml_422_envelope(client: TestClient) -> None:
    r = client.post(
        "/api/run", json={"architecture": "not: [valid", "scenario": SCENARIO_YAML}
    )
    assert r.status_code == 422
    body = r.json()
    assert body["error"]["code"] == "validation_error"
    assert body["error"]["detail"][0]["path"].startswith("arch")
    assert body["error"]["detail"][0]["line"] is not None


def test_events_report_without_session_409(client: TestClient) -> None:
    for path in ("/api/events", "/api/report"):
        r = client.get(path)
        assert r.status_code == 409
        assert r.json()["error"]["code"] == "session_invalid"


def test_validate_invalidates_session(client: TestClient) -> None:
    """M-4: the first edit invalidates the session — validate is the edit signal."""
    client.post(
        "/api/run", json={"architecture": ARCH_YAML, "scenario": SCENARIO_YAML}
    )
    r = client.post(
        "/api/validate", json={"kind": "architecture", "content": ARCH_YAML}
    )
    assert r.status_code == 200
    for path in ("/api/events", "/api/report"):
        assert client.get(path).status_code == 409


def test_unknown_api_404_envelope(client: TestClient) -> None:
    r = client.get("/api/nope")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "not_found"


def test_malformed_request_body_422_envelope(client: TestClient) -> None:
    r = client.post("/api/run", json={"architecture": "a"})  # scenario missing
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"


# ---------------------------------------------------------------------- load-log


def test_load_log_derives_partial_report(client: TestClient, v1_log_doc: dict) -> None:
    r = client.post(
        "/api/load-log",
        json={"name": "events.json", "content": _log_content(v1_log_doc)},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "events.json"
    assert body["event_count"] == len(v1_log_doc["events"])
    rep = body["report"]

    # derivable items (M-1)
    assert rep["simulation"]["result"] == v1_log_doc["simulation"]["result"]
    assert rep["simulation"]["duration_ms"] == v1_log_doc["simulation"]["duration_ms"]
    assert rep["assertions"] == v1_log_doc["assertions"]

    event_links = {e["link"] for e in v1_log_doc["events"] if "link" in e}
    assert event_links == {l["name"] for l in rep["links"]}
    event_tasks = {
        (e["node"], e["task"])
        for e in v1_log_doc["events"]
        if "task" in e and e["type"] == "task_start"
    }
    assert event_tasks == {(t["node"], t["task"]) for t in rep["tasks"]}

    # counts must match the full v1 report for the same log
    run_rep = loads(ARCH_YAML, SCENARIO_YAML).run().report
    by_name = {l["name"]: l for l in rep["links"]}
    for lr in run_rep.links:
        if lr.name in by_name:
            assert by_name[lr.name]["tx_count"] == lr.tx_count
            assert by_name[lr.name]["rx_count"] == lr.rx_count
            assert by_name[lr.name]["drop_count"] == lr.drop_count
    by_task = {(t["node"], t["task"]): t for t in rep["tasks"]}
    for trr in run_rep.tasks:
        if (trr.node, trr.task) in by_task:
            assert by_task[(trr.node, trr.task)]["run_count"] == trr.run_count
            assert by_task[(trr.node, trr.task)]["overrun_count"] == trr.overrun_count

    # NOT derivable from the log alone -> absent (UI shows "—")
    assert all("kind" not in l for l in rep["links"])
    assert all("bus_load_percent" not in l for l in rep["links"])
    assert all("supersede_count" not in l for l in rep["links"])
    assert all("period_ms" not in t for t in rep["tasks"])
    assert "warnings" not in rep


def test_load_log_with_arch_full_report(client: TestClient, v1_log_doc: dict) -> None:
    r = client.post(
        "/api/load-log",
        json={"content": _log_content(v1_log_doc), "arch_content": ARCH_YAML},
    )
    assert r.status_code == 200
    rep = r.json()["report"]

    # architecture-dependent fields now present (M-1 full Report)
    assert all("kind" in l and "bus_load_percent" in l for l in rep["links"])
    assert all("period_ms" in t for t in rep["tasks"])

    # bus load must match the v1 engine's definition+events computation
    run_rep = loads(ARCH_YAML, SCENARIO_YAML).run().report
    by_name = {l["name"]: l for l in rep["links"]}
    for lr in run_rep.links:
        if lr.name in by_name:
            assert by_name[lr.name]["bus_load_percent"] == pytest.approx(
                lr.bus_load_percent
            )

    # structurally impossible even with the architecture (v1 D-18 / log schema)
    assert all("supersede_count" not in l for l in rep["links"])
    assert "warnings" not in rep


def test_load_log_invalid_schema_version_422(client: TestClient, v1_log_doc: dict) -> None:
    doc = dict(v1_log_doc, schema_version=2)
    r = client.post("/api/load-log", json={"content": _log_content(doc)})
    assert r.status_code == 422
    body = r.json()
    assert body["error"]["code"] == "log_invalid"
    assert body["error"]["detail"][0]["path"] == "schema_version"


def test_load_log_unsorted_events_422(client: TestClient, v1_log_doc: dict) -> None:
    doc = dict(v1_log_doc, events=list(reversed(v1_log_doc["events"])))
    r = client.post("/api/load-log", json={"content": _log_content(doc)})
    assert r.status_code == 422
    body = r.json()
    assert body["error"]["code"] == "log_invalid"
    assert any(
        "t_ms, seq" in item["message"] or "오름차순" in item["message"]
        for item in body["error"]["detail"]
    )


def test_load_log_unknown_type_422(client: TestClient, v1_log_doc: dict) -> None:
    events = list(v1_log_doc["events"])
    events[0] = dict(events[0], type="junk")
    doc = dict(v1_log_doc, events=events)
    r = client.post("/api/load-log", json={"content": _log_content(doc)})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "log_invalid"


def test_load_log_bad_json_422_with_line(client: TestClient) -> None:
    r = client.post("/api/load-log", json={"content": "not json"})
    assert r.status_code == 422
    body = r.json()
    assert body["error"]["code"] == "log_invalid"
    assert body["error"]["detail"][0]["line"] is not None


def test_load_log_invalid_arch_422(client: TestClient, v1_log_doc: dict) -> None:
    r = client.post(
        "/api/load-log",
        json={"content": _log_content(v1_log_doc), "arch_content": "nodes: [\n"},
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"


def test_load_log_replaces_run_session(client: TestClient, v1_log_doc: dict) -> None:
    client.post(
        "/api/run", json={"architecture": ARCH_YAML, "scenario": SCENARIO_YAML}
    )
    r = client.post("/api/load-log", json={"content": _log_content(v1_log_doc)})
    assert r.status_code == 200
    ev = client.get("/api/events").json()
    assert len(ev) == len(v1_log_doc["events"])


# ------------------------------------------------------------------ localization


def test_english_error_localization() -> None:
    client = TestClient(create_app(lang="en", store=SessionStore()))
    r = client.get("/api/events")
    assert r.status_code == 409
    assert r.json()["error"]["message"] == (
        "session missing or invalidated — run or load a log again"
    )
