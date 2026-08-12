"""v1 events.json loading and report derivation (dashboard-load-log-report, M-1).

The dashboard never writes logs. The browser reads a local v1 ``events.json``
(schema_version 1) and posts its content to ``POST /api/load-log``. This module
parses and validates that document, then derives a dashboard Report following
the M-1 rules (spec/sdv-sim-v2.md, API section):

- derivable from events alone: ``simulation{duration_ms, result}`,
  ``links[](tx_count/rx_count/drop_count)``, ``tasks[](run_count/overrun_count)``,
  ``assertions[]``
- NOT derivable without an architecture definition: ``links[].kind``,
  ``links[].bus_load_percent``, ``tasks[].period_ms`` (tx_ms needs DLC/bitrate
  from the frame/link definitions; period comes from task definitions)
- never derivable from a log, even with the architecture: ``links[].supersede_count``
  (v1 D-18: supersede is not recorded as an event) and ``warnings[]`` (the log
  schema has no warnings field) — both stay absent ("—" in the UI)

When the load-log request includes ``arch_content`` the session holds the
architecture snapshot and the report is computed from definitions + events
("report is derived from definition + events", v1 D-21), matching the run-path
Report shape except for the structurally impossible fields above.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from typing import Any, cast

from sdv_sim.core.events import EVENT_TYPES
from sdv_sim.i18n import tr
from sdv_sim.schema.arch import Architecture, FrameDef, LinkDef

#: Fields a v1 log event may carry (all other keys are dropped on load).
_EVENT_FIELDS = ("t_ms", "seq", "type", "node", "link", "frame", "task", "data")


class LogValidationError(Exception):
    """Log document failed validation.

    ``items`` is a list of ``{path, line, message}`` dicts matching the F-8
    error ``detail`` shape (messages already localized in the request language).
    """

    def __init__(self, items: list[dict[str, Any]]) -> None:
        super().__init__("log validation failed")
        self.items = items


@dataclass(frozen=True)
class LogDocument:
    """A validated v1 event log (schema_version 1)."""

    simulation: dict[str, Any]  # {"duration_ms": int, "result": "pass"|"fail"}
    events: list[dict[str, Any]]  # (t_ms, seq) ascending, None fields dropped
    assertions: list[dict[str, Any]]  # [{"name", "status", "detail"}]
    raw: dict[str, Any] = field(repr=False)  # the full parsed JSON document


def parse_log(content: str, lang: str = "en") -> LogDocument:
    """Parse and validate v1 events.json content (spec log validation rules).

    Raises :class:`LogValidationError` on the first category of failure, or
    with the full item list when individual events are invalid. Validation:

    - top-level JSON object with ``schema_version == 1``
    - ``simulation{duration_ms, result}`` valid
    - ``events`` is a list; each event has ``t_ms``/``seq`` ints, ``type`` in the
      7-type enum, and the list is sorted by ``(t_ms, seq)`` ascending
    - ``assertions`` (when present) is a list of ``{name?, status, detail}``
    """
    try:
        doc = json.loads(content)
    except json.JSONDecodeError as exc:
        raise LogValidationError(
            [
                {
                    "path": None,
                    "line": exc.lineno,
                    "message": tr(lang, "log_parse_error", detail=exc.msg),
                }
            ]
        ) from exc

    if not isinstance(doc, dict):
        raise LogValidationError(
            [{"path": None, "line": None, "message": tr(lang, "log_not_object")}]
        )

    if doc.get("schema_version") != 1:
        raise LogValidationError(
            [
                {
                    "path": "schema_version",
                    "line": None,
                    "message": tr(
                        lang,
                        "log_schema_version",
                        version=doc.get("schema_version"),
                    ),
                }
            ]
        )

    sim = doc.get("simulation")
    if not isinstance(sim, dict):
        raise LogValidationError(
            [
                {
                    "path": "simulation",
                    "line": None,
                    "message": tr(lang, "log_simulation_invalid", detail="not an object"),
                }
            ]
        )
    dur = sim.get("duration_ms")
    result = sim.get("result")
    sim_problems: list[str] = []
    if not isinstance(dur, int) or isinstance(dur, bool) or dur < 0:
        sim_problems.append("duration_ms must be a non-negative integer")
    if result not in ("pass", "fail"):
        sim_problems.append("result must be 'pass' or 'fail'")
    if sim_problems:
        raise LogValidationError(
            [
                {
                    "path": "simulation",
                    "line": None,
                    "message": tr(
                        lang, "log_simulation_invalid", detail="; ".join(sim_problems)
                    ),
                }
            ]
        )

    raw_events = doc.get("events")
    if not isinstance(raw_events, list):
        raise LogValidationError(
            [{"path": "events", "line": None, "message": tr(lang, "log_events_not_list")}]
        )

    items: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    prev: tuple[int, int] | None = None
    for i, raw in enumerate(raw_events):
        path = f"events[{i}]"
        if not isinstance(raw, dict):
            items.append(
                {
                    "path": path,
                    "line": None,
                    "message": tr(lang, "log_bad_event", index=i, detail="not an object"),
                }
            )
            continue
        t_ms = raw.get("t_ms")
        seq = raw.get("seq")
        etype = raw.get("type")
        problems: list[str] = []
        if not isinstance(t_ms, int) or isinstance(t_ms, bool) or t_ms < 0:
            problems.append("t_ms must be a non-negative integer")
        if not isinstance(seq, int) or isinstance(seq, bool) or seq < 0:
            problems.append("seq must be a non-negative integer")
        if etype not in EVENT_TYPES:
            problems.append(f"unknown type {etype!r}")
        if problems:
            items.append(
                {
                    "path": path,
                    "line": None,
                    "message": tr(
                        lang, "log_bad_event", index=i, detail="; ".join(problems)
                    ),
                }
            )
            continue
        # validated above: t_ms and seq are non-negative ints here
        key = (cast(int, t_ms), cast(int, seq))
        if prev is not None and key <= prev:
            items.append(
                {
                    "path": path,
                    "line": None,
                    "message": tr(
                        lang,
                        "log_unsorted",
                        index=i,
                        t_ms=t_ms,
                        seq=seq,
                    ),
                }
            )
            continue
        prev = key
        events.append({k: v for k, v in raw.items() if v is not None and k in _EVENT_FIELDS})

    assertions: list[dict[str, Any]] = []
    raw_assertions = doc.get("assertions")
    if raw_assertions is not None:
        if not isinstance(raw_assertions, list):
            items.append(
                {
                    "path": "assertions",
                    "line": None,
                    "message": tr(
                        lang, "log_assertions_invalid", detail="not a list"
                    ),
                }
            )
        else:
            for i, raw in enumerate(raw_assertions):
                if not isinstance(raw, dict) or raw.get("status") not in ("pass", "fail"):
                    items.append(
                        {
                            "path": f"assertions[{i}]",
                            "line": None,
                            "message": tr(lang, "log_bad_assertion", index=i),
                        }
                    )
                else:
                    assertions.append(
                        {
                            "name": raw.get("name"),
                            "status": raw.get("status"),
                            "detail": raw.get("detail"),
                        }
                    )

    if items:
        raise LogValidationError(items)

    return LogDocument(
        simulation={"duration_ms": dur, "result": result},
        events=events,
        assertions=assertions,
        raw=doc,
    )


def derive_report(doc: LogDocument, arch: Architecture | None) -> dict[str, Any]:
    """Derive the dashboard Report for a log session (M-1).

    Without ``arch`` only event-derivable fields are present. With ``arch`` the
    architecture-dependent fields (kind, bus_load_percent, task period_ms) are
    added, matching v1 "report = definition + events". ``supersede_count`` and
    ``warnings`` are never present: supersede is not recorded (v1 D-18) and
    warnings are not part of the log schema.
    """
    duration = doc.simulation["duration_ms"]
    events = doc.events

    # per-link counts and (with arch) accumulated tx_ms for bus load
    link_tx: dict[str, int] = {}
    link_rx: dict[str, int] = {}
    link_drop: dict[str, int] = {}
    link_load_ms: dict[str, int] = {}
    if arch is not None:
        link_map: dict[str, LinkDef] = {l.name: l for l in arch.links}
        frame_map: dict[str, dict[str, FrameDef]] = {
            l.name: {f.name: f for f in l.frames} for l in arch.links
        }
    else:
        link_map = {}
        frame_map = {}
    for e in events:
        link = e.get("link")
        if link is None:
            continue
        if e["type"] == "tx":
            link_tx[link] = link_tx.get(link, 0) + 1
            if link in frame_map:
                tx_ms = _event_tx_ms(link_map[link], frame_map[link], e.get("frame"))
                link_load_ms[link] = link_load_ms.get(link, 0) + tx_ms
        elif e["type"] == "rx":
            link_rx[link] = link_rx.get(link, 0) + 1
        elif e["type"] == "drop":
            link_drop[link] = link_drop.get(link, 0) + 1

    # per-(node, task) counts
    task_start: dict[tuple[str, str], int] = {}
    task_overrun: dict[tuple[str, str], int] = {}
    for e in events:
        node, task = e.get("node"), e.get("task")
        if node is None or task is None:
            continue
        key = (node, task)
        if e["type"] == "task_start":
            task_start[key] = task_start.get(key, 0) + 1
        elif e["type"] == "overrun":
            task_overrun[key] = task_overrun.get(key, 0) + 1

    if arch is not None:
        # full Report: definitions + events (v1 D-21 semantics)
        links = []
        for ldef in arch.links:
            name = ldef.name
            links.append(
                {
                    "name": name,
                    "kind": ldef.kind,
                    "tx_count": link_tx.get(name, 0),
                    "rx_count": link_rx.get(name, 0),
                    "drop_count": link_drop.get(name, 0),
                    "bus_load_percent": (
                        (link_load_ms.get(name, 0) / duration * 100.0)
                        if duration > 0
                        else 0.0
                    ),
                }
            )
        tasks = []
        for node in arch.nodes:
            for comp in node.components:
                for tdef in comp.tasks:
                    tasks.append(
                        {
                            "node": node.name,
                            "task": tdef.name,
                            "period_ms": tdef.period_ms,
                            "run_count": task_start.get((node.name, tdef.name), 0),
                            "overrun_count": task_overrun.get(
                                (node.name, tdef.name), 0
                            ),
                        }
                    )
    else:
        # derivable-only: names come from the events themselves
        links = sorted(
            (
                {
                    "name": name,
                    "tx_count": link_tx.get(name, 0),
                    "rx_count": link_rx.get(name, 0),
                    "drop_count": link_drop.get(name, 0),
                }
                for name in set(link_tx) | set(link_rx) | set(link_drop)
            ),
            key=lambda d: d["name"],
        )
        tasks = sorted(
            (
                {
                    "node": node,
                    "task": task,
                    "run_count": task_start.get((node, task), 0),
                    "overrun_count": task_overrun.get((node, task), 0),
                }
                for node, task in set(task_start) | set(task_overrun)
            ),
            key=lambda d: (d["node"], d["task"]),
        )

    return {
        "simulation": {
            "duration_ms": duration,
            "result": doc.simulation["result"],
            "event_count": len(events),
        },
        "links": links,
        "tasks": tasks,
        "assertions": list(doc.assertions),
    }


def _event_tx_ms(
    link: LinkDef, frames: dict[str, FrameDef], frame_name: str | None
) -> int:
    """v1 transmission time for one tx event (matches core LinkRuntime.tx_ms)."""
    if frame_name is None:
        return 0
    frame = frames.get(frame_name)
    if frame is None:
        return 0
    if link.kind == "can":
        return math.ceil((44 + 8 * frame.dlc) / link.bitrate)
    return math.ceil((frame.dlc + 42) * 8 / (link.bitrate * 1000))
