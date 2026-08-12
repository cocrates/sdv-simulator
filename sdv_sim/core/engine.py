"""DES simulation engine for sdv-sim.

Implements the spec (spec/sdv-sim-v1.md):

- Discrete-event simulation with a single-threaded event queue and a fixed
  event order ``(t_ms, priority, declaration order, seq)`` for determinism.
- Integer millisecond time model; inclusive termination at ``duration_ms``.
- CAN: ``tx_ms = ceil((44 + 8*DLC) / bitrate_kbps)``, ID arbitration, priority
  queue. Ethernet: ``tx_ms = ceil((dlc + 42)*8 / (Mbps*1000))``, single-switch
  FIFO with tail drop and ``queue_depth``.
- Same-frame queue instances supersede (D-18); gateway rule chaining with a
  max of 8 hops (D-13); stub components are receiver-only (D-14); tasks use an
  absolute period with overrun detection and missed-instance skip (D-17).
"""

from __future__ import annotations

import heapq
import math
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence, TypeVar

from pydantic import BaseModel, ValidationError

from sdv_sim.core.component import Component, Message, TaskContext
from sdv_sim.core.errors import SdvSimInputError
from sdv_sim.core.events import Event
from sdv_sim.core.report import AssertionResult, LinkReport, Report, SimulationSummary, TaskReport
from sdv_sim.schema.arch import (
    Architecture,
    ComponentDef,
    FrameDef,
    GatewayRouteDef,
    LinkDef,
    TaskDef,
    _frame_message,
)
from sdv_sim.schema.scenario import Scenario

# Non-task events (tx/rx/...) sort after all task events at the same tick,
# because only tasks carry a priority (D-19: task priority -> decl -> seq).
MAX_PRIO = 1 << 30
# Max gateway routing hops per frame (D-13); exceeding it emits a drop event.
MAX_HOPS = 8

_T = TypeVar("_T", bound=BaseModel)


@dataclass(frozen=True)
class SimulationResult:
    """Deterministic result of one ``Simulator.run()`` (D-15)."""

    events: list[Event]
    report: Report
    assertions: list[AssertionResult]
    duration_ms: int


@dataclass
class Attempt:
    """A frame instance attempting to transmit on a link."""

    frame: FrameDef
    link_name: str
    node: str | None
    data: Any
    hops: int
    frame_decl: int
    periodic: bool = False
    arrival_t: int = 0
    arrival_seq: int = 0


@dataclass
class TaskRuntime:
    """Runtime state for one periodic task (per-task busy / overrun model)."""

    node: str
    component: str
    defn: TaskDef
    decl: int
    busy_until: int = 0
    running_since: int | None = None
    run_count: int = 0
    overrun_count: int = 0


@dataclass
class NodeRuntime:
    """A node and its component instances."""

    name: str
    type: str
    components: list[ComponentRuntime] = field(default_factory=list)


@dataclass
class ComponentRuntime:
    """A component definition bound to an instance."""

    defn: ComponentDef
    instance: Component
    decl: int = 0


class LinkRuntime:
    """CAN/Ethernet link model with queueing, arbitration, and stats."""

    def __init__(self, defn: LinkDef, decl: int) -> None:
        self.name = defn.name
        self.defn = defn
        self.decl = decl
        self.frames: dict[str, FrameDef] = {f.name: f for f in defn.frames}
        self.frame_decl: dict[str, int] = {f.name: i for i, f in enumerate(defn.frames)}
        # message name -> nodes on this link whose components receive it
        self.receivers_by_message: dict[str, list[str]] = {}
        self.bus_free_at = 0
        self.queue: list[Attempt] = []
        self.pending: list[Attempt] = []
        self.tx_count = 0
        self.rx_count = 0
        self.drop_count = 0
        self.supersede_count = 0
        self.load_tx_ms = 0
        self.engine: Simulator | None = None
        # Ethernet: single switch FIFO, queue_depth default 1000 (spec).
        if defn.kind == "ethernet":
            self.queue_depth: int | None = defn.switches[0].queue_depth if defn.switches else 1000
        else:
            self.queue_depth = None

    def tx_ms(self, frame: FrameDef) -> int:
        """Transmission time formula per link kind (spec, L2)."""
        if self.defn.kind == "can":
            return math.ceil((44 + 8 * frame.dlc) / self.defn.bitrate)
        return math.ceil((frame.dlc + 42) * 8 / (self.defn.bitrate * 1000))

    def add_pending(self, attempt: Attempt, t: int, seq: int) -> None:
        attempt.arrival_t = t
        attempt.arrival_seq = seq
        self.pending.append(attempt)

    def drain(self, t: int) -> None:
        """Resolve pending attempts / queued frames at time ``t`` (post-tick)."""
        if not self.pending and (self.bus_free_at > t or not self.queue):
            return
        # D-18: an instance already waiting in the queue is replaced by a
        # newly arrived instance of the same frame, before bus allocation.
        # (Applies even when the bus frees at this tick: the old instance has
        # not started transmitting yet, so only the latest instance matters.)
        if self.queue and self.pending:
            queued = {a.frame.name: a for a in self.queue}
            kept: list[Attempt] = []
            for a in self.pending:
                if a.frame.name in queued:
                    del queued[a.frame.name]
                    self.supersede_count += 1
                kept.append(a)
            self.queue = list(queued.values())
            self.pending = kept
        candidates = self.pending + self.queue
        self.pending.clear()
        self.queue.clear()
        if self.bus_free_at > t:
            # bus busy at t: everything waits (D-18 supersede applies)
            for a in candidates:
                self._enqueue(a)
            return
        if self.defn.kind == "can":
            # CAN arbitration: lower ID wins, then decl order, then arrival.
            candidates.sort(key=lambda a: (a.frame.id, a.frame_decl, a.arrival_seq))
        else:
            # Ethernet switch FIFO: arrival order.
            candidates.sort(key=lambda a: (a.arrival_seq, a.frame_decl))
        for a in candidates:
            if self.bus_free_at <= t:
                if self.engine is None:
                    raise RuntimeError("link engine not attached")
                self.engine._start_transmission(self, a, max(self.bus_free_at, t))
            else:
                self._enqueue(a)

    def _enqueue(self, a: Attempt) -> None:
        """Enqueue with same-frame supersede (D-18) and Ethernet tail drop."""
        for i, x in enumerate(self.queue):
            if x.frame.name == a.frame.name:
                self.queue[i] = a
                self.supersede_count += 1
                return
        if self.queue_depth is not None and len(self.queue) >= self.queue_depth:
            if self.engine is None:
                raise RuntimeError("link engine not attached")
            self.engine._log_drop(self, a)
            return
        self.queue.append(a)


class Simulator:
    """A prepared simulation: loaded architecture + scenario + components.

    Create via the public ``load()`` function (D-15), then call ``run()``.
    """

    def __init__(
        self,
        arch: Architecture,
        scenario: Scenario,
        components: dict[str, type[Component]] | None = None,
    ) -> None:
        self._arch = arch
        self._scenario = scenario
        self._components = components or {}
        self._duration = scenario.duration_ms

        self._nodes: dict[str, NodeRuntime] = {}
        self._links: dict[str, LinkRuntime] = {}
        self._tasks: list[TaskRuntime] = []
        self._message_frames: dict[str, list[tuple[str, str]]] = {}
        self._frame_decl: dict[tuple[str, str], int] = {}
        self._link_decl: dict[str, int] = {}

        self._heap: list[tuple[int, int, int, int, str, Any]] = []
        self._events: list[Event] = []
        self._warnings: list[str] = []
        self._seq = 0
        self._now = 0

        self._build_runtime()
        self._validate_scenario()

    # ------------------------------------------------------------------ build

    def _build_runtime(self) -> None:
        # frame / link declaration indices (D-19 tie-breaking)
        for link in self._arch.links:
            self._link_decl[link.name] = self._arch.links.index(link)
            for frame in link.frames:
                self._frame_decl[(link.name, frame.name)] = link.frames.index(frame)
        # nodes and components
        for node in self._arch.nodes:
            nr = NodeRuntime(name=node.name, type=node.type)
            for ci, comp in enumerate(node.components):
                key = comp.class_name if comp.class_name is not None else comp.name
                cls = self._components.get(key, Component)
                instance = cls()
                nr.components.append(ComponentRuntime(defn=comp, instance=instance, decl=ci))
                for ti, task in enumerate(comp.tasks):
                    # task decl = global append order (D-19 tie-breaking)
                    self._tasks.append(
                        TaskRuntime(
                            node=node.name,
                            component=comp.name,
                            defn=task,
                            decl=len(self._tasks),
                        )
                    )
            self._nodes[node.name] = nr
        # links
        for link in self._arch.links:
            lr = LinkRuntime(link, self._link_decl[link.name])
            lr.engine = self
            self._links[link.name] = lr
        # (receivers computed after all links exist — see _build_receivers)
        self._build_receivers()
        # message -> frames mapping (declaration order)
        for link in self._arch.links:
            for frame in link.frames:
                self._message_frames.setdefault(_frame_message(frame), []).append(
                    (link.name, frame.name)
                )

    def _build_receivers(self) -> None:
        for link_name, lr in self._links.items():
            link_def = lr.defn
            for node_name in link_def.nodes:
                node = self._nodes[node_name]
                for c in node.components:
                    for msg in c.defn.receives:
                        lr.receivers_by_message.setdefault(msg, [])
                        if node_name not in lr.receivers_by_message[msg]:
                            lr.receivers_by_message[msg].append(node_name)

    # -------------------------------------------------------------- scenario

    def load_scenario(self, scenario: str | Path) -> Simulator:
        """Replace the scenario (from a file path) and re-validate it."""
        model = _load_yaml_model(scenario, Scenario)
        self._validate_scenario_model(model)
        self._scenario = model
        self._duration = model.duration_ms
        return self

    def load_scenario_yaml(self, scenario_yaml: str) -> Simulator:
        """Replace the scenario from a YAML string and re-validate it.

        Added for the v2 dashboard (core-yaml-string-input): the server passes
        the browser's YAML content directly without touching the filesystem.
        Diagnostics use the pseudo identifier ``scenario`` instead of a path.
        """
        model = _parse_yaml_text(scenario_yaml, Scenario, "scenario")
        try:
            self._validate_scenario_model(model)
        except SdvSimInputError as exc:
            raise _tagged_scenario_error(exc) from exc
        self._scenario = model
        self._duration = model.duration_ms
        return self

    def _validate_scenario(self) -> None:
        self._validate_scenario_model(self._scenario)

    def _validate_scenario_model(self, scenario: Scenario) -> None:
        known_links = set(self._links)
        known_nodes = set(self._nodes)
        known_frames = {f.name for l in self._links.values() for f in l.frames.values()}
        known_tasks = {t.defn.name for t in self._tasks}
        for inj in scenario.messages:
            if inj.link not in known_links:
                raise SdvSimInputError(
                    "injection_unknown_link",
                    params={"link": inj.link},
                )
            if inj.frame not in self._links[inj.link].frames:
                raise SdvSimInputError(
                    "injection_unknown_frame",
                    params={"frame": inj.frame, "link": inj.link},
                )
        for i, a in enumerate(scenario.assertions):
            exp = a.expect
            if exp.link is not None and exp.link not in known_links:
                raise SdvSimInputError(
                    "assertion_unknown_link",
                    params={"num": i + 1, "link": exp.link},
                )
            if exp.frame is not None and exp.frame not in known_frames:
                raise SdvSimInputError(
                    "assertion_unknown_frame",
                    params={"num": i + 1, "frame": exp.frame},
                )
            if exp.message is not None and exp.message not in self._message_frames:
                raise SdvSimInputError(
                    "assertion_unknown_message",
                    params={"num": i + 1, "message": exp.message},
                )
            if exp.node is not None and exp.node not in known_nodes:
                raise SdvSimInputError(
                    "assertion_unknown_node",
                    params={"num": i + 1, "node": exp.node},
                )
            if exp.task is not None and exp.task not in known_tasks:
                raise SdvSimInputError(
                    "assertion_unknown_task",
                    params={"num": i + 1, "task": exp.task},
                )

    # ---------------------------------------------------------------- running

    def run(self) -> SimulationResult:
        """Run the simulation to ``duration_ms`` and return the full result."""
        self._heap = []
        self._events = []
        self._warnings = []
        self._seq = 0
        for link in self._links.values():
            link.bus_free_at = 0
            link.queue.clear()
            link.pending.clear()
            link.tx_count = 0
            link.rx_count = 0
            link.drop_count = 0
            link.supersede_count = 0
            link.load_tx_ms = 0
        for task in self._tasks:
            task.busy_until = 0
            task.running_since = None
            task.run_count = 0
            task.overrun_count = 0

        self._schedule_initial()
        while self._heap and self._heap[0][0] <= self._duration:
            t = self._heap[0][0]
            self._now = t
            # process all events at tick t in (priority, decl, seq) order
            while self._heap and self._heap[0][0] == t:
                _, _, _, _, kind, payload = heapq.heappop(self._heap)
                if kind == "task_start":
                    self._on_task_start(payload, t)
                elif kind == "task_end":
                    self._on_task_end(payload, t)
                elif kind == "tx_attempt":
                    self._on_tx_attempt(payload, t)
                elif kind == "rx":
                    self._on_rx(payload, t)
                elif kind == "link_service":
                    pass
                else:  # pragma: no cover - internal invariant
                    raise RuntimeError(f"unknown event kind {kind!r}")
            # resolve bus/switch work after the whole tick (arbitration batch)
            for link in self._links.values():
                link.drain(t)

        self._events.sort(key=lambda e: (e.t_ms, e.seq))
        assertions = self._evaluate_assertions()
        report = self._build_report(assertions)
        return SimulationResult(
            events=list(self._events),
            report=report,
            assertions=assertions,
            duration_ms=self._duration,
        )

    def now_ms(self) -> int:
        return self._now

    # ------------------------------------------------------------- scheduling

    def _schedule_initial(self) -> None:
        # periodic frames: first occurrence at t=0, then every period
        for link in self._links.values():
            for frame in link.frames.values():
                decl = self._frame_decl[(link.name, frame.name)]
                self._schedule(
                    0,
                    "tx_attempt",
                    Attempt(
                        frame=frame,
                        link_name=link.name,
                        node=frame.source,
                        data=None,
                        hops=0,
                        frame_decl=decl,
                        periodic=True,
                    ),
                    MAX_PRIO,
                    decl,
                )
        # periodic tasks: first occurrence at t=0
        for task in self._tasks:
            self._schedule(0, "task_start", task, task.defn.priority, task.decl)
        # scenario injections (D-13 path 3)
        for inj in self._scenario.messages:
            link = self._links[inj.link]
            frame = link.frames[inj.frame]
            decl = self._frame_decl[(inj.link, inj.frame)]
            self._schedule(
                inj.t_ms,
                "tx_attempt",
                Attempt(
                    frame=frame,
                    link_name=inj.link,
                    node=frame.source,
                    data=inj.data,
                    hops=0,
                    frame_decl=decl,
                ),
                MAX_PRIO,
                decl,
            )

    def _schedule(self, t: int, kind: str, payload: Any, prio: int, decl: int) -> None:
        heapq.heappush(self._heap, (t, prio, decl, self._next_seq(), kind, payload))

    def _next_seq(self) -> int:
        seq = self._seq
        self._seq += 1
        return seq

    def _log(
        self,
        t: int,
        etype: str,
        *,
        node: str | None = None,
        link: str | None = None,
        frame: str | None = None,
        task: str | None = None,
        data: Any = None,
    ) -> None:
        self._events.append(
            Event(
                t_ms=t,
                seq=self._next_seq(),
                type=etype,
                node=node,
                link=link,
                frame=frame,
                task=task,
                data=data,
            )
        )

    # ------------------------------------------------------------- dispatchers

    def _on_task_start(self, task: TaskRuntime, t: int) -> None:
        # D-17: an instance covered by this task's own overrun is skipped
        # silently; the absolute schedule continues.
        if task.busy_until > t:
            self._schedule_task_next(task, t)
            return
        task.run_count += 1
        task.running_since = t
        self._log(t, "task_start", node=task.node, task=task.defn.name)
        ctx = TaskContext(self, task.node, task.component)
        instance = self._component_instance(task.node, task.component)
        try:
            instance.on_periodic(ctx)
        except Exception as exc:  # component bug -> internal error (exit 3)
            raise RuntimeError(
                f"component {task.component!r} on node {task.node!r} "
                f"on_periodic failed: {exc}"
            ) from exc
        wcet = task.defn.wcet_ms
        task.busy_until = t + wcet
        if wcet > 0:
            self._schedule(
                t + wcet,
                "task_end",
                task,
                task.defn.priority,
                task.decl,
            )
        else:
            self._log(t, "task_end", node=task.node, task=task.defn.name)
        self._schedule_task_next(task, t)

    def _on_task_end(self, task: TaskRuntime, t: int) -> None:
        self._log(t, "task_end", node=task.node, task=task.defn.name)
        if task.running_since is not None and t > task.running_since + task.defn.period_ms:
            task.overrun_count += 1
            self._log(t, "overrun", node=task.node, task=task.defn.name)
            self._warnings.append(
                f"task {task.node}.{task.defn.name} overrun at t={t} "
                f"(wcet end {t} > period start {task.running_since})"
            )
        task.running_since = None

    def _schedule_task_next(self, task: TaskRuntime, t: int) -> None:
        nxt = t + task.defn.period_ms
        if nxt <= self._duration:
            self._schedule(nxt, "task_start", task, task.defn.priority, task.decl)

    def _on_tx_attempt(self, attempt: Attempt, t: int) -> None:
        link = self._links[attempt.link_name]
        link.add_pending(attempt, t, self._next_seq())
        if attempt.periodic:
            nxt = t + attempt.frame.period_ms
            if nxt <= self._duration:
                self._schedule(
                    nxt,
                    "tx_attempt",
                    Attempt(
                        frame=attempt.frame,
                        link_name=attempt.link_name,
                        node=attempt.node,
                        data=attempt.data,
                        hops=attempt.hops,
                        frame_decl=attempt.frame_decl,
                        periodic=True,
                    ),
                    MAX_PRIO,
                    attempt.frame_decl,
                )

    def _on_rx(self, payload: Any, t: int) -> None:
        frame, link_name, node_name, data = payload
        link = self._links[link_name]
        link.rx_count += 1
        msg_name = _frame_message(frame)
        self._log(
            t,
            "rx",
            node=node_name,
            link=link_name,
            frame=frame.name,
            data=data,
        )
        node = self._nodes[node_name]
        for cr in node.components:
            if msg_name in cr.defn.receives:
                ctx = TaskContext(self, node_name, cr.defn.name)
                try:
                    cr.instance.on_message(
                        ctx,
                        Message(
                            name=msg_name,
                            frame=frame.name,
                            link=link_name,
                            node=node_name,
                            data=data,
                            t_ms=t,
                        ),
                    )
                except Exception as exc:  # component bug -> internal error
                    raise RuntimeError(
                        f"component {cr.defn.name!r} on node {node_name!r} "
                        f"on_message failed: {exc}"
                    ) from exc

    # -------------------------------------------------------------- transmission

    def _start_transmission(self, link: LinkRuntime, attempt: Attempt, start: int) -> None:
        frame = attempt.frame
        tx = link.tx_ms(frame)
        link.bus_free_at = start + tx
        link.tx_count += 1
        link.load_tx_ms += tx
        self._log(
            start,
            "tx",
            node=attempt.node,
            link=link.name,
            frame=frame.name,
            data=attempt.data,
        )
        completion = start + tx
        # rx at propagation completion on receives-mapped nodes (D-13)
        for node_name in link.receivers_by_message.get(_frame_message(frame), []):
            decl = link.frame_decl.get(frame.name, 0)
            self._schedule(
                completion,
                "rx",
                (frame, link.name, node_name, attempt.data),
                MAX_PRIO,
                decl,
            )
        # gateway routing at completion + delay (D-13, rule chaining)
        self._route_frame(link, attempt, completion)
        # wake the link at completion so queued frames transmit promptly
        self._schedule(completion, "link_service", link.name, MAX_PRIO, link.decl)

    def _route_frame(self, link: LinkRuntime, attempt: Attempt, completion: int) -> None:
        route = self._find_route(link.name, attempt.frame)
        if route is None:
            return
        target = self._links[route.to.link]
        at = completion + route.delay_ms
        if attempt.hops + 1 > MAX_HOPS:
            target.drop_count += 1
            self._log(at, "drop", link=target.name, frame=attempt.frame.name)
            return
        tframe = target.frames.get(attempt.frame.name)
        eff = attempt.frame.model_copy(
            update={
                "id": route.to.remap_id
                if route.to.remap_id is not None
                else (tframe.id if tframe else attempt.frame.id),
                "dlc": tframe.dlc if tframe else attempt.frame.dlc,
            }
        )
        decl = self._frame_decl.get((route.to.link, eff.name), link.decl)
        self._schedule(
            at,
            "tx_attempt",
            Attempt(
                frame=eff,
                link_name=route.to.link,
                node=attempt.node,
                data=attempt.data,
                hops=attempt.hops + 1,
                frame_decl=decl,
            ),
            MAX_PRIO,
            decl,
        )

    def _find_route(self, link_name: str, frame: FrameDef) -> GatewayRouteDef | None:
        # matching priority: explicit frame > ID range (spec)
        for gw in self._arch.gateways:
            for r in gw.routes:
                if r.from_.link == link_name and r.from_.frame == frame.name:
                    return r
        for gw in self._arch.gateways:
            for r in gw.routes:
                if (
                    r.from_.link == link_name
                    and r.from_.frame is None
                    and r.from_.id_min is not None
                    and r.from_.id_max is not None
                    and r.from_.id_min <= frame.id <= r.from_.id_max
                ):
                    return r
        return None

    def _log_drop(self, link: LinkRuntime, attempt: Attempt) -> None:
        link.drop_count += 1
        self._log(
            attempt.arrival_t,
            "drop",
            link=link.name,
            frame=attempt.frame.name,
        )

    # ------------------------------------------------------------- component API

    def _component_instance(self, node: str, component: str) -> Component:
        for cr in self._nodes[node].components:
            if cr.defn.name == component:
                return cr.instance
        raise RuntimeError(f"unknown component {component!r} on node {node!r}")

    def component_send(self, node: str, name: str, data: Any) -> None:
        """TaskContext.send: map a message to a frame and attempt a tx now."""
        frames = self._message_frames.get(name)
        if not frames:
            raise RuntimeError(f"node {node!r} sent unknown message {name!r}")
        for link_name, frame_name in frames:
            link = self._links[link_name]
            if node in link.defn.nodes and frame_name in link.frames:
                frame = link.frames[frame_name]
                decl = self._frame_decl[(link_name, frame_name)]
                self._schedule(
                    self._now,
                    "tx_attempt",
                    Attempt(
                        frame=frame,
                        link_name=link_name,
                        node=node,
                        data=data,
                        hops=0,
                        frame_decl=decl,
                    ),
                    MAX_PRIO,
                    decl,
                )
                return
        raise RuntimeError(
            f"node {node!r} is not connected to a link carrying message {name!r}"
        )

    def component_log(self, node: str, component: str, message: str) -> None:
        self._log(self._now, "log", node=node, data=message)

    # ------------------------------------------------------------ verification

    def _evaluate_assertions(self) -> list[AssertionResult]:
        results: list[AssertionResult] = []
        for i, a in enumerate(self._scenario.assertions):
            name = a.name or f"assertion_{i + 1}"
            exp = a.expect
            matched = [e for e in self._events if self._match_assertion(exp, e)]
            count_ok = len(matched) >= exp.count
            first = matched[0] if matched else None
            time_ok = True
            if exp.at_ms is not None:
                time_ok = first is not None and abs(first.t_ms - exp.at_ms) <= exp.within_ms
            status = "pass" if count_ok and time_ok else "fail"
            detail = self._assertion_detail(exp, matched, first, count_ok, time_ok)
            results.append(AssertionResult(name=name, status=status, detail=detail))
        return results

    def _match_assertion(self, exp: Any, e: Event) -> bool:
        if exp.event == "tx" and e.type != "tx":
            return False
        if exp.event == "rx" and e.type != "rx":
            return False
        if exp.event == "task" and e.type not in ("task_start", "task_end"):
            return False
        if exp.frame is not None and e.frame != exp.frame:
            return False
        if exp.link is not None and e.link != exp.link:
            return False
        if exp.node is not None and e.node != exp.node:
            return False
        if exp.task is not None and e.task != exp.task:
            return False
        if exp.message is not None:
            frame_names = {fn for _, fn in self._message_frames.get(exp.message, [])}
            if e.frame not in frame_names:
                return False
        return True

    def _assertion_detail(
        self,
        exp: Any,
        matched: list[Event],
        first: Event | None,
        count_ok: bool,
        time_ok: bool,
    ) -> str:
        if count_ok and time_ok:
            n = len(matched)
            if first is not None and exp.at_ms is not None:
                return f"matched {n} event(s); first at t={first.t_ms}"
            return f"matched {n} event(s)"
        parts: list[str] = []
        if not count_ok:
            parts.append(f"expected >= {exp.count} matching event(s), found {len(matched)}")
        if not time_ok:
            if first is not None:
                parts.append(f"expected t within {exp.at_ms}+-{exp.within_ms}, found t={first.t_ms}")
            else:
                parts.append(f"expected t={exp.at_ms} within {exp.within_ms}, found no match")
        for e in matched[:3]:
            attrs = [f"t={e.t_ms}", f"seq={e.seq}"]
            if e.node is not None:
                attrs.append(f"node={e.node}")
            if e.link is not None:
                attrs.append(f"link={e.link}")
            if e.frame is not None:
                attrs.append(f"frame={e.frame}")
            if e.task is not None:
                attrs.append(f"task={e.task}")
            parts.append("event(" + ", ".join(attrs) + ")")
        return "; ".join(parts)

    # ---------------------------------------------------------------- reporting

    def _build_report(self, assertions: list[AssertionResult]) -> Report:
        result = "pass" if all(a.status == "pass" for a in assertions) else "fail"
        links = [
            LinkReport(
                name=lr.defn.name,
                kind=lr.defn.kind,
                tx_count=lr.tx_count,
                rx_count=lr.rx_count,
                drop_count=lr.drop_count,
                supersede_count=lr.supersede_count,
                bus_load_percent=(
                    (lr.load_tx_ms / self._duration * 100.0) if self._duration > 0 else 0.0
                ),
            )
            for lr in self._links.values()
        ]
        tasks = [
            TaskReport(
                node=t.node,
                task=t.defn.name,
                period_ms=t.defn.period_ms,
                run_count=t.run_count,
                overrun_count=t.overrun_count,
            )
            for t in self._tasks
        ]
        return Report(
            simulation=SimulationSummary(
                duration_ms=self._duration,
                result=result,
                event_count=len(self._events),
            ),
            links=links,
            tasks=tasks,
            assertions=assertions,
            warnings=list(self._warnings),
        )


# ------------------------------------------------------------- public helpers


def load(
    arch: str | Path,
    scenario: str | Path,
    components: dict[str, type[Component]] | None = None,
) -> Simulator:
    """Load architecture + scenario YAML files and prepare a :class:`Simulator`."""
    arch_model = _load_yaml_model(arch, Architecture)
    scenario_model = _load_yaml_model(scenario, Scenario)
    return Simulator(arch_model, scenario_model, components)


def loads(
    arch_yaml: str,
    scenario_yaml: str,
    components: dict[str, type[Component]] | None = None,
) -> Simulator:
    """Load architecture + scenario from **YAML strings** (core-yaml-string-input).

    Added for the v2 dashboard run path (``POST /api/run``): the server passes
    the browser-provided YAML content directly, never a filesystem path.
    Diagnostics use the pseudo identifiers ``arch`` / ``scenario`` with line
    numbers mapped against the supplied text.
    """
    arch_model = _parse_yaml_text(arch_yaml, Architecture, "arch")
    scenario_model = _parse_yaml_text(scenario_yaml, Scenario, "scenario")
    try:
        return Simulator(arch_model, scenario_model, components)
    except SdvSimInputError as exc:
        # Scenario reference errors raised by the constructor (unknown link /
        # frame / node / task / message) carry no filename; tag the pseudo
        # identifier so server diagnostics are uniform (core-yaml-string-input).
        raise _tagged_scenario_error(exc) from exc


def _tagged_scenario_error(exc: SdvSimInputError) -> SdvSimInputError:
    if exc.filename is None:
        return SdvSimInputError(
            exc.code,
            params=exc.params,
            filename="scenario",
            line=exc.line,
            field=exc.field,
        )
    return exc


def _load_yaml_model(path: str | Path, model_cls: type[_T]) -> _T:
    filename = str(path)
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise SdvSimInputError(
            "file_read_error", filename=filename
        ) from exc
    return _parse_yaml_text(text, model_cls, filename)


def _parse_yaml_text(text: str, model_cls: type[_T], filename: str) -> _T:
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        line = getattr(getattr(exc, "problem_mark", None), "line", None)
        raise SdvSimInputError(
            "yaml_parse_error",
            params={"detail": _yaml_error_text(exc)},
            filename=filename,
            line=(line + 1) if line is not None else None,
        ) from exc
    try:
        return model_cls.model_validate(data)
    except ValidationError as exc:
        err = exc.errors()[0]
        loc_path: Sequence[str | int] = err.get("loc", ())
        raise SdvSimInputError(
            "schema_error",
            params={"detail": err.get("msg", "invalid")},
            filename=filename,
            line=_locate_line(text, loc_path),
            field=_format_path(loc_path),
        ) from exc


def _yaml_error_text(exc: yaml.YAMLError) -> str:
    problem = getattr(exc, "problem", None)
    if problem is not None:
        context = getattr(exc, "context", None)
        if context:
            return f"{context} - {problem}"
        return str(problem)
    return str(exc)


def _format_path(path: Sequence[str | int]) -> str:
    out = ""
    for part in path:
        if isinstance(part, int):
            out += f"[{part}]"
        else:
            out += f".{part}" if out else str(part)
    return out


def _locate_line(text: str, path: Sequence[str | int]) -> int | None:
    """Map a Pydantic error path to a 1-based YAML line via compose marks."""
    try:
        node: Any = yaml.compose(text)
    except yaml.YAMLError:
        return None
    for key in path:
        if node is None:
            return None
        if isinstance(node, yaml.MappingNode):
            for k, v in node.value:
                if k.value == str(key):
                    node = v
                    break
            else:
                return None
        elif isinstance(node, yaml.SequenceNode) and isinstance(key, int):
            if 0 <= key < len(node.value):
                node = node.value[key]
            else:
                return None
        else:
            return None
    if node is not None and hasattr(node, "start_mark"):
        line: int = getattr(node, "start_mark").line
        return line + 1
    return None
