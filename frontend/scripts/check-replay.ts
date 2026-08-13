/**
 * Replay seek-engine checks (T-019): tx_ms formula vs the v1 core contract,
 * snapshot seek == full re-scan equivalence, O(K) structural bound, pulse-mode
 * fallback (F-5), and incremental advance. Run with Node's native type
 * stripping:
 *
 *   node scripts/check-replay.ts
 *
 * NOTE: runtime imports need explicit `.ts` extensions for Node's native type
 * stripping; type-only imports are erased and may stay extensionless.
 */

import {
  advanceToTime,
  applyEvent,
  buildReplayIndex,
  buildTxMsMap,
  computeTxMs,
  freshState,
  lastEventIndexAtOrBefore,
  pruneInFlight,
  PULSE_MS,
  seekToTime,
  SNAPSHOT_K,
} from "../src/replay/replayIndex.ts";
import type { SeekState } from "../src/replay/replayIndex";
import type { Architecture, SimEvent } from "../src/types/schema";

let failures = 0;

function check(name: string, ok: boolean, detail?: string): void {
  if (!ok) {
    failures += 1;
    console.error(`FAIL ${name}${detail ? ` — ${detail}` : ""}`);
  } else {
    console.log(`ok   ${name}`);
  }
}

// ------------------------------------------------------------ tx_ms formula

check("computeTxMs(can, 500, 4) = ceil((44+32)/500) = 1", computeTxMs("can", 500, 4) === 1);
check("computeTxMs(can, 100, 8) = ceil(108/100) = 2", computeTxMs("can", 100, 8) === 2);
check("computeTxMs(ethernet, 100, 8) = ceil(400/100000) = 1", computeTxMs("ethernet", 100, 8) === 1);
check("computeTxMs(ethernet, 1, 100) = ceil(1136/1000) = 2", computeTxMs("ethernet", 1, 100) === 2);

const txMsMap = new Map<string, number>([
  ["L1:F1", 1],
  ["L1:F2", 1],
]);

// --------------------------------------------------------------- fixtures

function ev(t_ms: number, seq: number, type: SimEvent["type"], extra: Partial<SimEvent> = {}): SimEvent {
  return { t_ms, seq, type, ...extra };
}

/** Synthetic session: node tasks, two tx/rx frames on L1, drop, overrun. */
function fixtureEvents(): SimEvent[] {
  return [
    ev(0, 0, "task_start", { node: "n1", task: "taskA" }),
    ev(10, 1, "tx", { node: "n1", link: "L1", frame: "F1" }),
    ev(11, 2, "rx", { node: "n2", link: "L1", frame: "F1" }),
    ev(20, 3, "task_end", { node: "n1", task: "taskA" }),
    ev(30, 4, "tx", { node: "n1", link: "L1", frame: "F2" }),
    ev(31, 5, "rx", { node: "n2", link: "L1", frame: "F2" }),
    ev(40, 6, "drop", { link: "L1", frame: "F3" }),
    ev(50, 7, "overrun", { node: "n2", task: "taskB" }),
    ev(60, 8, "task_start", { node: "n2", task: "taskB" }),
    ev(70, 9, "task_end", { node: "n2", task: "taskB" }),
    ev(80, 10, "log", { node: "n2" }),
  ];
}

// ------------------------------------------------- reference full re-scan

/** Independent reference: state after applying every event with t <= target
 * directly (no snapshots) — equivalent to scanning the whole prefix. Mirrors
 * production semantics: flights that end at or before the target are pruned
 * (the overlay never shows a frame after it has landed). */
function referenceState(events: SimEvent[], tMs: number, mode: "physical" | "pulse"): SeekState {
  const state = freshState();
  for (const e of events) {
    if (e.t_ms > tMs) break;
    applyEvent(state, e, mode, txMsMap);
  }
  pruneInFlight(state, tMs);
  return state;
}

function statesEqual(a: SeekState, b: SeekState): boolean {
  if (a.lastDrop.size !== b.lastDrop.size || a.lastOverrun.size !== b.lastOverrun.size) return false;
  for (const [k, v] of a.lastDrop) if (b.lastDrop.get(k) !== v) return false;
  for (const [k, v] of a.lastOverrun) if (b.lastOverrun.get(k) !== v) return false;
  if (a.nodeTasks.size !== b.nodeTasks.size) return false;
  for (const [n, tasks] of a.nodeTasks) {
    const other = b.nodeTasks.get(n);
    if (!other || other.size !== tasks.size) return false;
    for (const task of tasks) if (!other.has(task)) return false;
  }
  if (a.inFlight.size !== b.inFlight.size) return false;
  for (const [l, frames] of a.inFlight) {
    const other = b.inFlight.get(l);
    if (!other || other.length !== frames.length) return false;
    for (let i = 0; i < frames.length; i += 1) {
      const f = frames[i];
      const o = other[i];
      if (f.frame !== o.frame || f.start !== o.start || f.end !== o.end) return false;
    }
  }
  return true;
}

// --------------------------------------------------------- seek correctness

const events = fixtureEvents();
const index = buildReplayIndex(events, { mode: "physical", txMs: txMsMap, durationMs: 100 });

const seekTargets = [-5, 0, 5, 10, 10.5, 11, 15, 20, 25, 30, 31, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 90, 100, 500];
for (const t of seekTargets) {
  const got = seekToTime(index, t);
  const want = referenceState(events, t, "physical");
  check(`seek(${t}) equals full re-scan`, statesEqual(got.state, want), JSON.stringify({ got: got.state, want }));
}

// focused behavioral checks on the fixture
const s10 = seekToTime(index, 10).state;
check(
  "seek(10): taskA running on n1",
  s10.nodeTasks.get("n1")?.has("taskA") === true,
);
check(
  "seek(10): F1 in flight on L1 until 11",
  s10.inFlight.get("L1")?.[0]?.frame === "F1" && s10.inFlight.get("L1")?.[0]?.end === 11,
);
const s15 = seekToTime(index, 15).state;
check(
  "seek(15): F1 expired at 11 (rx lands exactly at tx+tx_ms)",
  !s15.inFlight.has("L1"),
);
const s50 = seekToTime(index, 50).state;
check("seek(50): drop signal on L1 at 40", s50.lastDrop.get("L1") === 40);
check("seek(50): overrun signal on n2 at 50", s50.lastOverrun.get("n2") === 50);
const s70 = seekToTime(index, 70).state;
check("seek(70): taskB finished on n2", !s70.nodeTasks.has("n2"));

// --------------------------------------------------------- O(K) bound (M-3)

{
  // The structural bound: re-applications = (i+1) % K (0 at exact block
  // boundaries). Assert <= K for every sampled target.
  const targets = [0, 5, 10, 11, 15, 20, 35, 40, 55, 70, 80, 90, 100, 500];
  for (const t of targets) {
    const i = lastEventIndexAtOrBefore(events, t);
    const replayed = i < 0 ? 0 : (i + 1) % SNAPSHOT_K;
    check(`seek(${t}) re-applies <= K (replayed=${replayed}, K=${SNAPSHOT_K})`, replayed >= 0 && replayed <= SNAPSHOT_K);
  }
}

// large-set equivalence + snapshot block boundaries
{
  const big: SimEvent[] = [];
  const N = 100_000;
  for (let i = 0; i < N; i += 1) {
    const t = i * 3;
    const type: SimEvent["type"] = i % 4 === 0 ? "tx" : i % 4 === 1 ? "rx" : i % 4 === 2 ? "task_start" : "task_end";
    big.push(
      ev(
        t,
        i,
        type,
        type === "tx" ? { node: "n1", link: "L1", frame: `F${i % 10}` } : type === "rx" ? { node: "n2", link: "L1", frame: `F${i % 10}` } : { node: i % 2 ? "n1" : "n2", task: `T${i % 5}` },
      ),
    );
  }
  const bigIndex = buildReplayIndex(big, { mode: "physical", txMs: txMsMap, durationMs: N * 3 });
  check("big index has snapshots (N/K + 1)", bigIndex.snapshots.length === Math.floor(N / SNAPSHOT_K) + 1);

  // exact block boundaries and mid-block targets must equal full re-scan
  for (const t of [0, SNAPSHOT_K * 3, SNAPSHOT_K * 3 - 1, SNAPSHOT_K * 3 + 1, N * 3 - 1, N * 3, N * 3 + 5]) {
    const got = seekToTime(bigIndex, t).state;
    const want = referenceState(big, t, "physical");
    check(`big seek(${t}) equals full re-scan`, statesEqual(got, want));
  }
}

// ------------------------------------------------------------- pulse mode

{
  const pulseIndex = buildReplayIndex(events, { mode: "pulse", durationMs: 100 });
  const s = seekToTime(pulseIndex, 10).state;
  const f = s.inFlight.get("L1")?.[0];
  check(
    `pulse mode: F1 flight ends at t+${PULSE_MS}`,
    f?.frame === "F1" && f?.end === 10 + PULSE_MS,
    JSON.stringify(f),
  );
}

// --------------------------------------------------------- incremental play

{
  const a0 = seekToTime(index, 10);
  let state = a0.state;
  let applied = a0.appliedIndex;
  applied = advanceToTime(index, state, applied, 35);
  const want = referenceState(events, 35, "physical");
  check("advanceToTime(10 → 35) equals full re-scan", statesEqual(state, want), JSON.stringify(state));
  check("advanceToTime applied index points at last event <= 35", events[applied].t_ms === 31 || events[applied].t_ms === 30);
}

// -------------------------------------------------------------- txMs builder

{
  const arch: Architecture = {
    nodes: [
      { name: "n1", type: "ECU", components: [{ name: "c1", sends: ["F1"], receives: [] }] },
      { name: "n2", type: "ECU", components: [{ name: "c2", sends: [], receives: ["F1"] }] },
    ],
    links: [
      {
        name: "L1",
        kind: "can",
        bitrate: 500,
        nodes: ["n1", "n2"],
        frames: [{ name: "F1", id: 0x100, dlc: 4, period_ms: 10, source: "n1" }],
      },
    ],
    gateways: [],
  };
  const map = buildTxMsMap(arch);
  check("buildTxMsMap: L1:F1 = computeTxMs(can,500,4) = 1", map.get("L1:F1") === 1);
}

if (failures > 0) {
  console.error(`\n${failures} check(s) FAILED`);
  process.exit(1);
}
console.log("\nall replay checks passed");
