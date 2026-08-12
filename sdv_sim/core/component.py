"""Component author API (component-api / public-api-contract, D-15)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sdv_sim.core.engine import Simulator


@dataclass(frozen=True)
class Message:
    """A message delivered to a component's ``on_message`` handler."""

    name: str
    frame: str
    link: str
    node: str
    data: Any = None
    t_ms: int = 0


class Component:
    """Base class for user-defined simulator components.

    Subclass and register via ``load(..., components={"name": MyComponent})``.
    Unregistered components behave as stubs (receiver-only, D-14).
    """

    def on_periodic(self, ctx: TaskContext) -> None:
        """Called when a periodic task of this component fires."""

    def on_message(self, ctx: TaskContext, message: Message) -> None:
        """Called when this component receives a mapped message."""


class TaskContext:
    """Per-invocation context handed to component callbacks."""

    def __init__(self, engine: Simulator, node: str, component: str) -> None:
        self._engine = engine
        self._node = node
        self._component = component

    def now_ms(self) -> int:
        """Current simulation time in integer milliseconds."""
        return self._engine.now_ms()

    def send(self, name: str, data: Any = None) -> None:
        """Send a message (mapped to a frame) onto the bus at the current time."""
        self._engine.component_send(self._node, name, data)

    def log(self, message: str) -> None:
        """Emit a ``log`` event into the deterministic event stream."""
        self._engine.component_log(self._node, self._component, message)
