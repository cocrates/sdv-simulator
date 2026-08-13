/**
 * Replay seek engine (T-019; spec ASR-015 M-3 / dashboard-seek-state-indexing).
 *
 * Pure module — no browser globals, so `scripts/check-replay.ts` can verify it
 * under Node's native type stripping.
 *
 * Model:
 *   - Events arrive sorted by (t_ms, seq) (server guarantees it for run, the
 *     log loader validates it). Build once, then:
 *       * seek(t)   — binary search + periodic snapshot + re-apply ≤ K events
 *                     (O(K) upper bound; snapshots every K events);
 *       * advance   — incremental forward application during playback
 *                     (O(events per frame), no snapshot work).
 *   - State captures exactly what the overlay draws (spec ASR-016):
 *       * per node: running tasks + last overrun time (transient signal);
 *       * per link: in-flight frames (tx start/end) + last drop time
 *                     (queue depth is NOT estimable from v1 events — drops are
 *                      an approximate signal only, no depth figures);
 *       * log events have no overlay effect.
 *   - Frame flight duration (spec M-2):
 *       * physical mode (run path, or load-log WITH arch_content): tx_ms
 *         computed from the architecture with the v1 core formula;
 *       * pulse mode (load-log without architecture, F-5): fixed pulse
 *         duration + the UI shows an "approximate" label.
 */

import type { Architecture, LinkKind, SimEvent } from "../types/schema";

// ------------------------------------------------------------- configuration

/** Snapshot period (M-3): every K events a full state snapshot is stored.
 * seek re-applies at most K events on top of a snapshot — O(K) cost bound.
 * 1M events ⇒ 500 snapshots; each snapshot is tiny (bounded by sim-scale
 * nodes/links), so building fits well inside the 2s load budget. */
export const SNAPSHOT_K = 2000;

/** Fixed pulse duration for the load-log fallback (F-5, M-2). */
export const PULSE_MS = 300;

/** Transient highlight window for overrun / drop signals. */
export const SIGNAL_MS = 500;

export type ReplayMode = "physical" | "pulse";

/** Event-type display filter (spec: 이벤트 타입 필터, task = start+end 그룹). */
export interface ReplayFilter {
  tx: boolean;
  rx: boolean;
  task: boolean;
  drop: boolean;
  overrun: boolean;
  log: boolean;
}

// ------------------------------------------------------------------ tx_ms

/**
 * v1 core transmission time — exact replica of `LinkRuntime.tx_ms`
 * (sdv_sim/core/engine.py): CAN `ceil((44 + 8*DLC) / bitrate_kbps)`,
 * Ethernet `ceil((dlc + 42) * 8 / (bitrate_Mbps * 1000))`.
 */
export function computeTxMs(kind: LinkKind, bitrate: number, dlc: number): number {
  if (kind === "can") return Math.ceil((44 + 8 * dlc) / bitrate);
  return Math.ceil(((dlc + 42) * 8) / (bitrate * 1000));
}

/** Map `"<link>:<frame>" → tx_ms` from an architecture (gateway remaps use the
 * target link's frame def, which is exactly what this map captures). */
export function buildTxMsMap(arch: Architecture): Map<string, number> {
  const map = new Map<string, number>();
  for (const link of arch.links) {
    for (const frame of link.frames ?? []) {
      map.set(`${link.name}:${frame.name}`, computeTxMs(link.kind, link.bitrate, frame.dlc));
    }
  }
  return map;
}

// ------------------------------------------------------------------- state

export interface InFlightFrame {
  frame: string;
  /** Sender node of the tx event (may not be an endpoint on routed links). */
  sender?: string;
  start: number;
  end: number;
}

export interface SeekState {
  nodeTasks: Map<string, Set<string>>;
  lastOverrun: Map<string, number>;
  lastDrop: Map<string, number>;
  inFlight: Map<string, InFlightFrame[]>;
}

export function freshState(): SeekState {
  return {
    nodeTasks: new Map(),
    lastOverrun: new Map(),
    lastDrop: new Map(),
    inFlight: new Map(),
  };
}

export function cloneState(s: SeekState): SeekState {
  const nodeTasks = new Map<string, Set<string>>();
  for (const [node, tasks] of s.nodeTasks) nodeTasks.set(node, new Set(tasks));
  const inFlight = new Map<string, InFlightFrame[]>();
  for (const [link, frames] of s.inFlight) inFlight.set(link, frames.slice());
  return {
    nodeTasks,
    lastOverrun: new Map(s.lastOverrun),
    lastDrop: new Map(s.lastDrop),
    inFlight,
  };
}

// ---------------------------------------------------------------- applying

function txDuration(ev: SimEvent, mode: ReplayMode, txMs: Map<string, number> | undefined): number {
  if (mode === "physical" && ev.link && ev.frame) {
    const ms = txMs?.get(`${ev.link}:${ev.frame}`);
    if (typeof ms === "number" && Number.isFinite(ms)) return ms;
  }
  return PULSE_MS;
}

/** Apply one event to the state. `rx` is informational — flights expire at
 * their end (rx lands exactly at end in physical mode; propagation delay 0). */
export function applyEvent(
  state: SeekState,
  ev: SimEvent,
  mode: ReplayMode,
  txMs: Map<string, number> | undefined,
): void {
  switch (ev.type) {
    case "task_start": {
      if (!ev.node || !ev.task) return;
      let tasks = state.nodeTasks.get(ev.node);
      if (!tasks) {
        tasks = new Set();
        state.nodeTasks.set(ev.node, tasks);
      }
      tasks.add(ev.task);
      break;
    }
    case "task_end": {
      if (!ev.node || !ev.task) return;
      const tasks = state.nodeTasks.get(ev.node);
      if (tasks) {
        tasks.delete(ev.task);
        if (tasks.size === 0) state.nodeTasks.delete(ev.node);
      }
      break;
    }
    case "overrun": {
      if (ev.node) state.lastOverrun.set(ev.node, ev.t_ms);
      break;
    }
    case "drop": {
      if (ev.link) state.lastDrop.set(ev.link, ev.t_ms);
      break;
    }
    case "tx": {
      if (!ev.link) return;
      const frames = state.inFlight.get(ev.link) ?? [];
      const end = ev.t_ms + txDuration(ev, mode, txMs);
      // A bus transmits serially — drop expired flights of this link first so
      // the array stays bounded (typically 0–1 entries per link).
      const live = frames.filter((f) => f.end > ev.t_ms);
      live.push({ frame: ev.frame ?? "", sender: ev.node, start: ev.t_ms, end });
      state.inFlight.set(ev.link, live);
      break;
    }
    default:
      break; // rx / log — no overlay state
  }
}

/** Drop flights whose end passed — used after a seek so old flights don't
 * linger past their completion. */
export function pruneInFlight(state: SeekState, tMs: number): void {
  for (const [link, frames] of state.inFlight) {
    const live = frames.filter((f) => f.end > tMs);
    if (live.length === 0) state.inFlight.delete(link);
    else if (live.length !== frames.length) state.inFlight.set(link, live);
  }
}

// ------------------------------------------------------------------- index

export interface ReplayIndex {
  events: SimEvent[];
  mode: ReplayMode;
  /** Timeline length (run: scenario.duration_ms, log: simulation.duration_ms). */
  durationMs: number;
  snapshots: SeekState[];
  /** Architecture-derived tx_ms map — undefined in pulse mode (F-5). */
  txMs: Map<string, number> | undefined;
}

export interface BuildIndexOptions {
  mode: ReplayMode;
  txMs?: Map<string, number>;
  durationMs: number;
}

export function buildReplayIndex(events: SimEvent[], opts: BuildIndexOptions): ReplayIndex {
  for (let i = 1; i < events.length; i += 1) {
    const a = events[i - 1];
    const b = events[i];
    if (b.t_ms < a.t_ms || (b.t_ms === a.t_ms && b.seq < a.seq)) {
      throw new Error("events are not sorted by (t_ms, seq)");
    }
  }

  const state = freshState();
  const snapshots: SeekState[] = [cloneState(state)];
  for (let i = 0; i < events.length; i += 1) {
    applyEvent(state, events[i], opts.mode, opts.txMs);
    if ((i + 1) % SNAPSHOT_K === 0) snapshots.push(cloneState(state));
  }

  return { events, mode: opts.mode, durationMs: opts.durationMs, snapshots, txMs: opts.txMs };
}

/** Largest index with `events[i].t_ms <= tMs`, or -1. */
export function lastEventIndexAtOrBefore(events: SimEvent[], tMs: number): number {
  let lo = 0;
  let hi = events.length - 1;
  let ans = -1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    if (events[mid].t_ms <= tMs) {
      ans = mid;
      lo = mid + 1;
    } else {
      hi = mid - 1;
    }
  }
  return ans;
}

export interface SeekResult {
  state: SeekState;
  appliedIndex: number;
}

/**
 * Seek to `tMs`: snapshot at floor((i+1)/K) + re-apply the remaining ≤ K
 * events (M-3). Cost is O(K) regardless of total event count.
 */
export function seekToTime(index: ReplayIndex, tMs: number): SeekResult {
  const { events, snapshots } = index;
  const i = lastEventIndexAtOrBefore(events, tMs);
  if (i < 0) return { state: cloneState(snapshots[0]), appliedIndex: -1 };

  const snapIdx = Math.min(Math.floor((i + 1) / SNAPSHOT_K), snapshots.length - 1);
  const state = cloneState(snapshots[snapIdx]);
  const from = snapIdx * SNAPSHOT_K;
  for (let j = from; j <= i; j += 1) {
    applyEvent(state, events[j], index.mode, index.txMs);
  }
  pruneInFlight(state, tMs);
  return { state, appliedIndex: i };
}

/**
 * Incremental forward application used by the playback loop: applies events
 * with t_ms ≤ `tMs` on top of `state`, returning the new applied index.
 * Only valid for forward motion — a backward move must use `seekToTime`.
 * Prunes flights that expire at or before `tMs`, so the invariant
 * `advance(tMs) == seek(tMs)` holds at every playback tick.
 */
export function advanceToTime(
  index: ReplayIndex,
  state: SeekState,
  appliedIndex: number,
  tMs: number,
): number {
  const { events } = index;
  let i = appliedIndex;
  while (i + 1 < events.length && events[i + 1].t_ms <= tMs) {
    i += 1;
    applyEvent(state, events[i], index.mode, index.txMs);
  }
  pruneInFlight(state, tMs);
  return i;
}
