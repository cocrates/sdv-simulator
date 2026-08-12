"""architecture.yaml schema (D-12 field tree).

Modeled 1:1 with the spec's architecture field tree:

    nodes: [{name, type: ECU|HPC,
             components: [{name, sends, receives, tasks: [{name, period_ms,
                           priority, wcet_ms}]}]}]
    links: [{name, kind: can|ethernet, bitrate, nodes, frames:
             [{name, id, dlc, period_ms, source, message?}], switches:
             [{name?, queue_depth}]}]
    gateways: [{name, routes: [{from: {link, frame|id_min, id_max},
               to: {link, remap_id?}, delay_ms?}]}]
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TaskDef(BaseModel):
    """A periodic task on a component."""

    model_config = ConfigDict(extra="forbid")

    name: str
    period_ms: int
    priority: int
    wcet_ms: int = 0

    @field_validator("period_ms")
    @classmethod
    def _period_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("period_ms must be > 0")
        return v

    @field_validator("wcet_ms")
    @classmethod
    def _wcet_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("wcet_ms must be >= 0")
        return v


class ComponentDef(BaseModel):
    """A software component hosted on a node."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    name: str
    sends: list[str] = []
    receives: list[str] = []
    tasks: list[TaskDef] = []
    class_name: str | None = Field(default=None, alias="class")


class NodeDef(BaseModel):
    """An ECU or HPC node."""

    model_config = ConfigDict(extra="forbid")

    name: str
    type: Literal["ECU", "HPC"] = "ECU"
    components: list[ComponentDef] = []


class FrameDef(BaseModel):
    """An L2 frame owned by a link."""

    model_config = ConfigDict(extra="forbid")

    name: str
    id: int
    dlc: int
    period_ms: int
    source: str
    message: str | None = None

    @field_validator("id")
    @classmethod
    def _id_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("id must be >= 0")
        return v

    @field_validator("dlc")
    @classmethod
    def _dlc_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("dlc must be >= 0")
        return v

    @field_validator("period_ms")
    @classmethod
    def _period_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("period_ms must be > 0")
        return v


class SwitchDef(BaseModel):
    """A link switch (Ethernet)."""

    model_config = ConfigDict(extra="forbid")

    name: str = "default"
    queue_depth: int = 1000

    @field_validator("queue_depth")
    @classmethod
    def _depth_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("queue_depth must be > 0")
        return v


class LinkDef(BaseModel):
    """A CAN or Ethernet link between nodes."""

    model_config = ConfigDict(extra="forbid")

    name: str
    kind: Literal["can", "ethernet"]
    bitrate: int
    nodes: list[str] = []
    frames: list[FrameDef] = []
    switches: list[SwitchDef] = []

    @field_validator("bitrate")
    @classmethod
    def _bitrate_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("bitrate must be > 0")
        return v


class FromRef(BaseModel):
    """Route source: a specific frame, or an ID range, on a link."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    link: str
    frame: str | None = None
    id_min: int | None = Field(default=None, alias="id_min")
    id_max: int | None = Field(default=None, alias="id_max")

    @model_validator(mode="after")
    def _exactly_one_match(self) -> FromRef:
        has_frame = self.frame is not None
        has_range = self.id_min is not None or self.id_max is not None
        if has_frame == has_range:
            raise ValueError("from must specify either frame or (id_min, id_max)")
        if has_range and (self.id_min is None or self.id_max is None):
            raise ValueError("id_min and id_max must be specified together")
        if has_range and self.id_min > self.id_max:  # type: ignore[operator]
            raise ValueError("id_min must be <= id_max")
        return self


class ToRef(BaseModel):
    """Route target: a link, with optional frame ID remapping."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    link: str
    remap_id: int | None = Field(default=None, alias="remap_id")

    @field_validator("remap_id")
    @classmethod
    def _remap_non_negative(cls, v: int | None) -> int | None:
        if v is not None and v < 0:
            raise ValueError("remap_id must be >= 0")
        return v


class GatewayRouteDef(BaseModel):
    """One gateway routing rule (D-13: matching priority frame > id range)."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    from_: FromRef = Field(alias="from")
    to: ToRef
    delay_ms: int = 0

    @field_validator("delay_ms")
    @classmethod
    def _delay_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("delay_ms must be >= 0")
        return v


class GatewayDef(BaseModel):
    """An infrastructure gateway with routing rules."""

    model_config = ConfigDict(extra="forbid")

    name: str
    routes: list[GatewayRouteDef] = []


class Architecture(BaseModel):
    """Top-level architecture.yaml model."""

    model_config = ConfigDict(extra="forbid")

    schema_version: int = 1
    nodes: list[NodeDef] = []
    links: list[LinkDef] = []
    gateways: list[GatewayDef] = []

    @model_validator(mode="after")
    def _unique_names(self) -> Architecture:
        for kind, names in (
            ("node", [n.name for n in self.nodes]),
            ("link", [l.name for l in self.links]),
            ("gateway", [g.name for g in self.gateways]),
        ):
            dup = _first_duplicate(names)
            if dup is not None:
                raise ValueError(f"duplicate {kind} name: {dup!r}")
        for link in self.links:
            dup = _first_duplicate([f.name for f in link.frames])
            if dup is not None:
                raise ValueError(f"duplicate frame name on link {link.name!r}: {dup!r}")
            dup_node = _first_duplicate(link.nodes)
            if dup_node is not None:
                raise ValueError(f"duplicate node reference on link {link.name!r}: {dup_node!r}")
        for node in self.nodes:
            dup = _first_duplicate([c.name for c in node.components])
            if dup is not None:
                raise ValueError(f"duplicate component name on node {node.name!r}: {dup!r}")
        return self

    @model_validator(mode="after")
    def _resolve_references(self) -> Architecture:
        node_names = {n.name for n in self.nodes}
        link_names = {l.name for l in self.links}
        # every link node must exist
        for link in self.links:
            missing = [n for n in link.nodes if n not in node_names]
            if missing:
                raise ValueError(
                    f"link {link.name!r} references unknown node(s): {missing}"
                )
        # every frame source must be connected to its link
        for link in self.links:
            for frame in link.frames:
                if frame.source not in link.nodes:
                    raise ValueError(
                        f"frame {frame.name!r} on link {link.name!r}: source "
                        f"{frame.source!r} is not connected to the link"
                    )
        # gateway route references must exist
        for gw in self.gateways:
            for idx, route in enumerate(gw.routes):
                if route.from_.link not in link_names:
                    raise ValueError(
                        f"gateway {gw.name!r} route #{idx}: unknown from link "
                        f"{route.from_.link!r}"
                    )
                if route.to.link not in link_names:
                    raise ValueError(
                        f"gateway {gw.name!r} route #{idx}: unknown to link "
                        f"{route.to.link!r}"
                    )
                from_link = _link_by_name(self.links, route.from_.link)
                if route.from_.frame is not None and route.from_.frame not in {
                    f.name for f in from_link.frames
                }:
                    raise ValueError(
                        f"gateway {gw.name!r} route #{idx}: frame "
                        f"{route.from_.frame!r} is not defined on link "
                        f"{route.from_.link!r}"
                    )
        # component sends/receives must map to a frame on a connected link
        for node in self.nodes:
            node_links = [l for l in self.links if node.name in l.nodes]
            node_frames = {
                _frame_message(f)
                for l in node_links
                for f in l.frames
            }
            for comp in node.components:
                for msg in comp.sends + comp.receives:
                    if msg not in node_frames:
                        raise ValueError(
                            f"component {comp.name!r} on node {node.name!r}: "
                            f"message {msg!r} does not map to a frame on any "
                            f"connected link"
                        )
        return self


def _first_duplicate(items: list[str]) -> str | None:
    seen: set[str] = set()
    for item in items:
        if item in seen:
            return item
        seen.add(item)
    return None


def _link_by_name(links: list[LinkDef], name: str) -> LinkDef:
    for link in links:
        if link.name == name:
            return link
    raise KeyError(name)


def _frame_message(frame: FrameDef) -> str:
    """Mapping rule: ``message`` field, or the frame name itself."""
    return frame.message if frame.message is not None else frame.name
