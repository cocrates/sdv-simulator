"""Shared helpers for sdv-sim tests."""

from __future__ import annotations

from sdv_sim.core.engine import Simulator, load
from sdv_sim.schema.arch import (
    Architecture,
    ComponentDef,
    FrameDef,
    LinkDef,
    NodeDef,
    TaskDef,
)
from sdv_sim.schema.scenario import (
    AssertionDef,
    AssertionExpect,
    MessageInjection,
    Scenario,
)


def make_task(name: str, period_ms: int, priority: int, wcet_ms: int = 0) -> TaskDef:
    return TaskDef(name=name, period_ms=period_ms, priority=priority, wcet_ms=wcet_ms)


def make_component(
    name: str,
    sends: list[str] | None = None,
    receives: list[str] | None = None,
    tasks: list[TaskDef] | None = None,
    class_name: str | None = None,
) -> ComponentDef:
    return ComponentDef(
        name=name,
        sends=sends or [],
        receives=receives or [],
        tasks=tasks or [],
        class_name=class_name,
    )


def make_frame(
    name: str,
    id: int,
    dlc: int,
    period_ms: int,
    source: str,
    message: str | None = None,
) -> FrameDef:
    return FrameDef(
        name=name,
        id=id,
        dlc=dlc,
        period_ms=period_ms,
        source=source,
        message=message,
    )


def make_link(
    name: str,
    kind: str,
    bitrate: int,
    nodes: list[str],
    frames: list[FrameDef] | None = None,
    queue_depth: int | None = None,
) -> LinkDef:
    switches = [{"name": "default", "queue_depth": queue_depth}] if queue_depth is not None else []
    return LinkDef(
        name=name,
        kind=kind,
        bitrate=bitrate,
        nodes=nodes,
        frames=frames or [],
        switches=switches,
    )


def make_arch(nodes: list[NodeDef], links: list[LinkDef], gateways: list[dict] | None = None) -> Architecture:
    return Architecture(nodes=nodes, links=links, gateways=gateways or [])


def make_scenario(
    duration_ms: int = 100,
    messages: list[MessageInjection] | None = None,
    assertions: list[AssertionDef] | None = None,
) -> Scenario:
    return Scenario(
        duration_ms=duration_ms,
        messages=messages or [],
        assertions=assertions or [],
    )


def expect(**kw: object) -> AssertionDef:
    return AssertionDef(expect=AssertionExpect(**kw))


def inject(t_ms: int, link: str, frame: str, data: dict | None = None) -> MessageInjection:
    return MessageInjection(t_ms=t_ms, link=link, frame=frame, data=data)
