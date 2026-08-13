/**
 * Deterministic type-band layout for the structure view (spec/sdv-sim-v2.md,
 * ASR-016 + dashboard-layout-placement-rule Option A / F-6 / M-5).
 *
 * Rules (all deterministic — same YAML input ⇒ same coordinates; no D3 force,
 * no randomness):
 *   - Nodes are grouped into horizontal bands by type: HPC band (top),
 *     Gateway band (middle — gateways are routing infrastructure), ECU band
 *     (bottom). Empty type bands are omitted (e.g. no gateways ⇒ only
 *     HPC/ECU bands remain).
 *   - Within a band, nodes are ordered by connected-link count descending,
 *     then by name ascending (code-unit order — locale-independent).
 *   - Links are drawn between their node pairs: across bands as straight
 *     lines between facing edges; within the same band as a quadratic arc
 *     above the band.
 *   - CAN vs Ethernet is a *visual* attribute only (color/thickness/dash) —
 *     it never affects positions.
 *
 * This module imports types only, so it is also directly runnable under
 * Node's native TypeScript type stripping (see scripts/check-layout.ts).
 */

import type { Architecture, ArchitectureLink, LinkKind } from "./types/schema";

// ------------------------------------------------------------- layout constants

export const NODE_W = 150;
export const NODE_H = 54;
export const NODE_GAP_X = 46;
export const BAND_GAP_Y = 110;
export const MARGIN = 40;
/** How far a same-band arc rises above the band top. */
export const ARC_RISE = 44;

export type BandType = "HPC" | "Gateway" | "ECU";

// ------------------------------------------------------------------ result types

export interface LayoutNode {
  name: string;
  type: BandType;
  band: number; // index into LayoutResult.bands
  x: number; // top-left
  y: number; // top-left
  width: number;
  height: number;
  linkCount: number;
}

export interface LayoutFrame {
  name: string;
  id: number;
  period_ms: number;
}

export interface LayoutLink {
  name: string;
  kind: LinkKind;
  /** Endpoint node names (one layout link per consecutive node pair of the
   * architecture link) — used by the replay overlay to resolve the sender
   * endpoint of an in-flight frame. */
  nodes: [string, string];
  from: { x: number; y: number };
  to: { x: number; y: number };
  /** Present for same-band links (quadratic control point). */
  control?: { x: number; y: number };
  frames: LayoutFrame[];
}

export interface LayoutBand {
  type: BandType;
  y: number;
  nodeCount: number;
}

export interface LayoutResult {
  width: number;
  height: number;
  nodes: LayoutNode[];
  links: LayoutLink[];
  bands: LayoutBand[];
}

// ---------------------------------------------------------------------- helpers

/** Locale-independent code-unit order — fully deterministic. */
export function byName(a: string, b: string): number {
  if (a < b) return -1;
  if (a > b) return 1;
  return 0;
}

function center(n: LayoutNode): { cx: number; cy: number } {
  return { cx: n.x + n.width / 2, cy: n.y + n.height / 2 };
}

// --------------------------------------------------------------- main algorithm

export function layoutArchitecture(arch: Architecture): LayoutResult {
  const hpc: LayoutNode[] = [];
  const ecu: LayoutNode[] = [];
  const gateway: LayoutNode[] = [];

  // Count connected links per node (a link may list its nodes in any order).
  const linkCount = new Map<string, number>();
  for (const link of arch.links) {
    const seen = new Set<string>();
    for (const nodeName of link.nodes) {
      if (!seen.has(nodeName)) {
        seen.add(nodeName);
        linkCount.set(nodeName, (linkCount.get(nodeName) ?? 0) + 1);
      }
    }
  }

  for (const node of arch.nodes) {
    if (node.type === "HPC") {
      hpc.push({ name: node.name, type: "HPC", band: 0, x: 0, y: 0, width: NODE_W, height: NODE_H, linkCount: linkCount.get(node.name) ?? 0 });
    } else {
      ecu.push({ name: node.name, type: "ECU", band: 0, x: 0, y: 0, width: NODE_W, height: NODE_H, linkCount: linkCount.get(node.name) ?? 0 });
    }
  }
  for (const gw of arch.gateways ?? []) {
    gateway.push({ name: gw.name, type: "Gateway", band: 0, x: 0, y: 0, width: NODE_W, height: NODE_H, linkCount: linkCount.get(gw.name) ?? 0 });
  }

  const sortBand = (a: LayoutNode, b: LayoutNode): number =>
    b.linkCount - a.linkCount || byName(a.name, b.name);

  hpc.sort(sortBand);
  ecu.sort(sortBand);
  gateway.sort(sortBand);

  const bands: LayoutBand[] = [];
  const bandNodes: LayoutNode[][] = [];
  let bandIndex = 0;
  for (const [type, list] of [
    ["HPC", hpc],
    ["Gateway", gateway],
    ["ECU", ecu],
  ] as const) {
    if (list.length === 0) continue;
    bands.push({ type, y: 0, nodeCount: list.length });
    bandNodes.push(list);
    for (const n of list) n.band = bandIndex;
    bandIndex += 1;
  }

  if (bands.length === 0) {
    return { width: MARGIN * 2, height: MARGIN * 2, nodes: [], links: [], bands: [] };
  }

  // Assign band tops and node positions (x per order within the band).
  let y = MARGIN;
  for (let i = 0; i < bands.length; i += 1) {
    bands[i].y = y;
    const list = bandNodes[i];
    let x = MARGIN;
    for (const n of list) {
      n.x = x;
      n.y = y;
      x += NODE_W + NODE_GAP_X;
    }
    y += NODE_H + BAND_GAP_Y;
  }
  const height = y - BAND_GAP_Y + MARGIN;

  const maxInBand = Math.max(0, ...bands.map((b) => b.nodeCount));
  const width =
    maxInBand === 0 ? MARGIN * 2 : MARGIN * 2 + maxInBand * NODE_W + (maxInBand - 1) * NODE_GAP_X;

  const byNode = new Map<string, LayoutNode>();
  for (const list of bandNodes) for (const n of list) byNode.set(n.name, n);

  // Build link geometry. Links keep their input order (deterministic).
  const links: LayoutLink[] = [];
  for (const link of arch.links) {
    const frames = linkFrames(link);
    const positions = link.nodes.map((name) => byNode.get(name)).filter((n): n is LayoutNode => n !== undefined);
    // Pair consecutive nodes; skip degenerate/self pairs.
    for (let i = 0; i + 1 < positions.length; i += 1) {
      const a = positions[i];
      const b = positions[i + 1];
      if (a.name === b.name) continue;
      const { cx: ax } = center(a);
      const { cx: bx } = center(b);
      let from: { x: number; y: number };
      let to: { x: number; y: number };
      let control: { x: number; y: number } | undefined;
      if (a.band < b.band) {
        from = { x: ax, y: a.y + a.height }; // bottom of A
        to = { x: bx, y: b.y }; // top of B
      } else if (a.band > b.band) {
        from = { x: ax, y: a.y }; // top of A
        to = { x: bx, y: b.y + b.height }; // bottom of B
      } else {
        const topY = Math.min(a.y, b.y);
        from = { x: ax, y: topY };
        to = { x: bx, y: topY };
        control = { x: (ax + bx) / 2, y: topY - ARC_RISE };
      }
      links.push({ name: link.name, kind: link.kind, nodes: [a.name, b.name], from, to, control, frames });
    }
  }

  return { width, height, nodes: bandNodes.flat(), links, bands };
}

function linkFrames(link: ArchitectureLink): LayoutFrame[] {
  return (link.frames ?? []).map((f) => ({
    name: f.name ?? "",
    id: f.id ?? 0,
    period_ms: f.period_ms ?? 0,
  }));
}
