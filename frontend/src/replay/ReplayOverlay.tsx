/**
 * Replay overlay (T-019) — SVG content rendered inside the shared structure
 * <svg> by `StructureView` (same coordinate space as the topology).
 *
 * Draws (spec ASR-016 오버레이 렌더 규칙):
 *   - in-flight frames moving sender → link → receiver with duration tx_ms
 *     (physical mode) or the fixed pulse (pulse mode, F-5 — "approximate"
 *     label shown);
 *   - node highlights: running tasks + transient overrun signal;
 *   - link highlights: transient drop signal (queue depth is NOT estimated —
 *     drop events only);
 *   - per-link bus load badges (run path or arch-content load-log).
 *
 * This component emits SVG fragments (`<g>`) only — it never creates its own
 * <svg> or layout. All geometry comes from the shared `LayoutResult`.
 */

import { useMemo } from "react";

import type { LayoutLink, LayoutNode, LayoutResult } from "../layout";
import { useI18n } from "../i18n";
import { SIGNAL_MS } from "./replayIndex";
import type { ReplayFilter, ReplayMode, SeekState } from "./replayIndex";
import type { ReportLink } from "../types/schema";

interface ReplayOverlayProps {
  layout: LayoutResult;
  state: SeekState;
  playTime: number;
  mode: ReplayMode;
  filter: ReplayFilter;
  /** Report link stats by link name (undefined when not derivable). */
  reportLinks?: Map<string, ReportLink>;
}

type Point = { x: number; y: number };

function lerp(a: Point, b: Point, t: number): Point {
  return { x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t };
}

function quad(a: Point, c: Point, b: Point, t: number): Point {
  const u = 1 - t;
  return {
    x: u * u * a.x + 2 * u * t * c.x + t * t * b.x,
    y: u * u * a.y + 2 * u * t * c.y + t * t * b.y,
  };
}

/** Travel point at progress t along the link path, from `from` to `to`
 * (control, when present, arcs above the band — the same control works for
 * the reversed traversal since a quadratic Bézier is direction-symmetric). */
function pointOn(link: LayoutLink, from: Point, to: Point, t: number): Point {
  return link.control ? quad(from, link.control, to, t) : lerp(from, to, t);
}

/** Resolve the travel endpoints of a frame on a link pair. The tx event's node
 * is the sender when it is an endpoint; for gateway-routed frames the node is
 * the original sender (not on this link) — then the gateway endpoint is used
 * (spec: 소스 링크 전송 완료 → 대상 링크 tx 체인). */
function travelEndpoints(
  link: LayoutLink,
  sender: string | undefined,
  nodeByName: Map<string, LayoutNode>,
): { from: Point; to: Point } {
  const [a, b] = link.nodes;
  const aNode = nodeByName.get(a);
  const bNode = nodeByName.get(b);
  const aPos: Point = aNode
    ? { x: aNode.x + aNode.width / 2, y: aNode.y + aNode.height / 2 }
    : link.from;
  const bPos: Point = bNode
    ? { x: bNode.x + bNode.width / 2, y: bNode.y + bNode.height / 2 }
    : link.to;

  let senderIsA = sender === a;
  if (sender !== undefined && sender !== a && sender !== b) {
    // routed frame — prefer the gateway endpoint as the visible sender
    senderIsA = aNode?.type === "Gateway" && bNode?.type !== "Gateway";
  }
  return senderIsA ? { from: aPos, to: bPos } : { from: bPos, to: aPos };
}

// ------------------------------------------------------------------ parts

function FlightDot({
  link,
  from,
  to,
  start,
  end,
  frame,
  playTime,
}: {
  link: LayoutLink;
  from: Point;
  to: Point;
  start: number;
  end: number;
  frame: string;
  playTime: number;
}) {
  const dur = Math.max(1, end - start);
  const raw = (playTime - start) / dur;
  const t = Math.max(0, Math.min(1, raw));
  const p = pointOn(link, from, to, t);
  return (
    <g className="replay-flight">
      <circle cx={p.x} cy={p.y} r={5} className="replay-flight-dot" />
      <text x={p.x + 8} y={p.y - 6} className="replay-flight-label">
        {frame}
      </text>
    </g>
  );
}

function BusLoadBadge({ link, percent }: { link: LayoutLink; percent: number }) {
  const p = { x: (link.from.x + link.to.x) / 2 + 8, y: (link.from.y + link.to.y) / 2 + 14 };
  return (
    <g className="replay-busload">
      <rect x={p.x - 4} y={p.y - 9} width={36} height={14} rx={3} />
      <text x={p.x} y={p.y}>
        {Math.round(percent)}%
      </text>
    </g>
  );
}

// ------------------------------------------------------------------- main

export function ReplayOverlay({
  layout,
  state,
  playTime,
  mode,
  filter,
  reportLinks,
}: ReplayOverlayProps) {
  const { t } = useI18n();

  const nodeByName = useMemo(() => {
    const m = new Map<string, LayoutNode>();
    for (const n of layout.nodes) m.set(n.name, n);
    return m;
  }, [layout]);

  const linkByName = useMemo(() => {
    const m = new Map<string, LayoutLink[]>();
    for (const l of layout.links) {
      const list = m.get(l.name) ?? [];
      list.push(l);
      m.set(l.name, list);
    }
    return m;
  }, [layout]);

  // ------------------------------ node highlights (task / overrun)

  const nodeHighlights: Array<{ name: string; kind: "running" | "overrun" }> = [];
  if (filter.task) {
    for (const [name, tasks] of state.nodeTasks) {
      if (tasks.size > 0) nodeHighlights.push({ name, kind: "running" });
    }
  }
  if (filter.overrun) {
    for (const [name, at] of state.lastOverrun) {
      if (playTime >= at && playTime - at <= SIGNAL_MS) {
        nodeHighlights.push({ name, kind: "overrun" });
      }
    }
  }

  // ------------------------------ link highlights (drop signal)

  const dropLinks = new Set<string>();
  if (filter.drop) {
    for (const [name, at] of state.lastDrop) {
      if (playTime >= at && playTime - at <= SIGNAL_MS) dropLinks.add(name);
    }
  }

  // ------------------------------ in-flight frames

  const flights: Array<{
    link: LayoutLink;
    from: Point;
    to: Point;
    start: number;
    end: number;
    frame: string;
  }> = [];
  if (filter.tx) {
    for (const [linkName, frames] of state.inFlight) {
      for (const f of frames) {
        if (playTime < f.start || playTime >= f.end) continue;
        const pairs = linkByName.get(linkName) ?? [];
        // a frame travels on the pair that contains its sender endpoint
        const pair =
          pairs.find((p) => f.sender !== undefined && p.nodes.includes(f.sender)) ??
          pairs.find((p) => p.nodes.some((n) => nodeByName.get(n)?.type === "Gateway")) ??
          pairs[0];
        if (!pair) continue;
        const { from, to } = travelEndpoints(pair, f.sender, nodeByName);
        flights.push({ link: pair, from, to, start: f.start, end: f.end, frame: f.frame });
      }
    }
  }

  return (
    <g className="replay-overlay">
      {mode === "pulse" && (
        <g className="replay-approx">
          <rect x={6} y={6} width={120} height={18} rx={4} />
          <text x={14} y={18}>{t("replay.approximate")}</text>
        </g>
      )}

      {/* active flight links (under the dots) */}
      {flights.map((f, i) => (
        <path
          key={`active-${i}`}
          d={`M ${f.from.x} ${f.from.y} L ${f.to.x} ${f.to.y}`}
          className="replay-link-active"
          fill="none"
        />
      ))}

      {/* drop flashes */}
      {[...dropLinks].map((name) => {
        const pair = linkByName.get(name)?.[0];
        if (!pair) return null;
        const p = quadPoint(pair, 0.5);
        return (
          <g key={`drop-${name}`} className="replay-drop">
            <path d={`M ${p.x - 4} ${p.y - 4} L ${p.x + 4} ${p.y + 4} M ${p.x + 4} ${p.y - 4} L ${p.x - 4} ${p.y + 4}`} />
            <title>{`drop on ${name}`}</title>
          </g>
        );
      })}

      {/* bus load badges (physical mode with a full report) */}
      {mode === "physical" &&
        reportLinks &&
        layout.links.map((l) => {
          const stats = reportLinks.get(l.name);
          if (!stats || typeof stats.bus_load_percent !== "number") return null;
          return <BusLoadBadge key={`load-${l.name}`} link={l} percent={stats.bus_load_percent} />;
        })}

      {/* in-flight frame dots */}
      {flights.map((f, i) => (
        <FlightDot
          key={`flight-${i}`}
          link={f.link}
          from={f.from}
          to={f.to}
          start={f.start}
          end={f.end}
          frame={f.frame}
          playTime={playTime}
        />
      ))}

      {/* node highlights */}
      {nodeHighlights.map((h) => {
        const n = nodeByName.get(h.name);
        if (!n) return null;
        return (
          <g key={`${h.kind}-${h.name}`}>
            <rect
              x={n.x}
              y={n.y}
              width={n.width}
              height={n.height}
              rx={8}
              className={h.kind === "running" ? "replay-node-running" : "replay-node-overrun"}
              fill="none"
            />
            <circle
              cx={n.x + n.width - 10}
              cy={n.y + 10}
              r={4}
              className={h.kind === "running" ? "replay-node-running-dot" : "replay-node-overrun-dot"}
            />
          </g>
        );
      })}
    </g>
  );
}

function quadPoint(link: LayoutLink, t: number): Point {
  return pointOn(link, link.from, link.to, t);
}
