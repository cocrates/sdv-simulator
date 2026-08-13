/**
 * Best-effort YAML parsing for rendering only (spec ASR-018: the *server*
 * remains the validation authority — the frontend does not port the Pydantic
 * schemas). This parser extracts just enough structure for the layout/render;
 * invalid or missing fields are tolerated and normalized to safe defaults.
 */

import { load } from "js-yaml";

import type { Architecture, ArchitectureLink, ArchitectureNode, LinkKind } from "./types/schema";

function asRecord(v: unknown): Record<string, unknown> | null {
  return typeof v === "object" && v !== null ? (v as Record<string, unknown>) : null;
}

function asString(v: unknown): string {
  return typeof v === "string" ? v : "";
}

function asStringArray(v: unknown): string[] {
  if (!Array.isArray(v)) return [];
  return v.map(asString).filter((s) => s.length > 0);
}

export function parseArchitecture(text: string): Architecture | null {
  let raw: unknown;
  try {
    raw = load(text);
  } catch {
    return null;
  }
  const root = asRecord(raw);
  if (!root) return null;

  const nodes: ArchitectureNode[] = [];
  if (Array.isArray(root.nodes)) {
    for (const item of root.nodes) {
      const rec = asRecord(item);
      if (!rec || asString(rec.name) === "") continue;
      nodes.push({
        name: asString(rec.name),
        type: rec.type === "HPC" ? "HPC" : "ECU",
        components: [],
      });
    }
  }

  const links: ArchitectureLink[] = [];
  if (Array.isArray(root.links)) {
    for (const item of root.links) {
      const rec = asRecord(item);
      if (!rec || asString(rec.name) === "") continue;
      const kind: LinkKind = rec.kind === "ethernet" ? "ethernet" : "can";
      const frames: ArchitectureLink["frames"] = [];
      if (Array.isArray(rec.frames)) {
        for (const f of rec.frames) {
          const fr = asRecord(f);
          if (!fr || asString(fr.name) === "") continue;
          frames.push({
            name: asString(fr.name),
            id: typeof fr.id === "number" ? fr.id : 0,
            dlc: typeof fr.dlc === "number" ? fr.dlc : 0,
            period_ms: typeof fr.period_ms === "number" ? fr.period_ms : 0,
            source: asString(fr.source),
            message: asString(fr.message) || undefined,
          });
        }
      }
      links.push({
        name: asString(rec.name),
        kind,
        bitrate: typeof rec.bitrate === "number" ? rec.bitrate : 0,
        nodes: asStringArray(rec.nodes),
        frames,
        switches: Array.isArray(rec.switches)
          ? rec.switches.map((s) => asRecord(s) ?? {}).map((s) => ({
              name: asString(s.name) || undefined,
              queue_depth: typeof s.queue_depth === "number" ? s.queue_depth : undefined,
            }))
          : undefined,
      });
    }
  }

  const gateways: Architecture["gateways"] = [];
  if (Array.isArray(root.gateways)) {
    for (const item of root.gateways) {
      const rec = asRecord(item);
      if (!rec || asString(rec.name) === "") continue;
      gateways.push({ name: asString(rec.name), routes: [] });
    }
  }

  return { nodes, links, gateways: gateways.length > 0 ? gateways : undefined };
}
