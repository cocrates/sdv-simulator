"""scenario.yaml schema (D-12 field tree).

    duration_ms (required), seed? (v1 ignored),
    messages: [{t_ms, link, frame, data?}],
    assertions: [{name?, expect: {event, frame/message/node/link/task?,
                 at_ms?, within_ms, count}}]
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class MessageInjection(BaseModel):
    """A scenario message injected onto a link at a given time."""

    model_config = ConfigDict(extra="forbid")

    t_ms: int
    link: str
    frame: str
    data: dict[str, Any] | None = None

    @field_validator("t_ms")
    @classmethod
    def _t_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("t_ms must be >= 0")
        return v


class AssertionExpect(BaseModel):
    """The declarative ``expect`` block (D-20 evaluation rules)."""

    model_config = ConfigDict(extra="forbid")

    event: Literal["tx", "rx", "task"]
    frame: str | None = None
    message: str | None = None
    node: str | None = None
    link: str | None = None
    task: str | None = None
    at_ms: int | None = None
    within_ms: int = 0
    count: int = 1

    @field_validator("within_ms", "count")
    @classmethod
    def _non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("must be >= 0")
        return v

    @field_validator("at_ms")
    @classmethod
    def _at_non_negative(cls, v: int | None) -> int | None:
        if v is not None and v < 0:
            raise ValueError("at_ms must be >= 0")
        return v


class AssertionDef(BaseModel):
    """One named (or anonymous) assertion."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    expect: AssertionExpect


class Scenario(BaseModel):
    """Top-level scenario.yaml model."""

    model_config = ConfigDict(extra="forbid")

    schema_version: int = 1
    duration_ms: int
    seed: int | None = None
    messages: list[MessageInjection] = []
    assertions: list[AssertionDef] = []

    @field_validator("duration_ms")
    @classmethod
    def _duration_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("duration_ms must be >= 0")
        return v
