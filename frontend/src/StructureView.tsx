/**
 * Structure view: SVG topology rendering over the deterministic type-band
 * layout (spec ASR-016). Pure presentation — all geometry comes from
 * `layoutArchitecture`.
 *
 * Visual conventions:
 *   - Node fill/stroke by type (HPC / Gateway / ECU);
 *   - Link kind is a visual attribute only: CAN = solid + thick, Ethernet =
 *     dashed + thin (spec: "CAN/Ethernet 시각 구분");
 *   - Frames are rendered as a small label next to each link.
 */

import { useMemo, type ReactNode } from "react";

import { useI18n } from "./i18n";
import { ARC_RISE, layoutArchitecture, NODE_H, NODE_W } from "./layout";
import type { LayoutBand, LayoutLink, LayoutNode, LayoutResult } from "./layout";
import type { Architecture } from "./types/schema";

const NODE_STYLE: Record<LayoutNode["type"], { fill: string; stroke: string; text: string }> = {
  HPC: { fill: "#efe6fb", stroke: "#7c3aed", text: "#4c1d95" },
  Gateway: { fill: "#fdeee3", stroke: "#ea7317", text: "#9a4d06" },
  ECU: { fill: "#e2f4e9", stroke: "#16a34a", text: "#14532d" },
};

function labelPoint(link: LayoutLink): { x: number; y: number } {
  if (link.control) {
    // quadratic bezier midpoint
    const q = 0.25;
    return {
      x: q * link.from.x + 0.5 * link.control.x + q * link.to.x,
      y: q * link.from.y + 0.5 * link.control.y + q * link.to.y,
    };
  }
  return { x: (link.from.x + link.to.x) / 2, y: (link.from.y + link.to.y) / 2 };
}

function framesText(link: LayoutLink): string {
  const names = link.frames.map((f) => f.name);
  if (names.length === 0) return "";
  if (names.length <= 2) return names.join(", ");
  return `${names.slice(0, 2).join(", ")} …`;
}

function LinkPath({ link, onSelectLink }: { link: LayoutLink; onSelectLink?: (name: string) => void }) {
  const d = link.control
    ? `M ${link.from.x} ${link.from.y} Q ${link.control.x} ${link.control.y} ${link.to.x} ${link.to.y}`
    : `M ${link.from.x} ${link.from.y} L ${link.to.x} ${link.to.y}`;
  const isCan = link.kind === "can";
  const p = labelPoint(link);
  const text = framesText(link);
  // offset the label a little to the side so it does not sit on the line
  const lx = p.x + 8;
  const ly = p.y - 8;
  return (
    <g
      className={onSelectLink ? "structure-link selectable" : "structure-link"}
      onClick={onSelectLink ? () => onSelectLink(link.name) : undefined}
    >
      <path
        d={d}
        className={isCan ? "link-can" : "link-eth"}
        fill="none"
      >
        <title>{`${link.name} (${link.kind})${text ? ` — ${text}` : ""}`}</title>
      </path>
      {text && (
        <g className="link-label">
          <rect x={lx - 4} y={ly - 11} width={text.length * 6.4 + 8} height={15} rx={3} />
          <text x={lx} y={ly}>
            {text}
          </text>
        </g>
      )}
    </g>
  );
}

function NodeRect({ node, onSelectNode }: { node: LayoutNode; onSelectNode?: (name: string) => void }) {
  const style = NODE_STYLE[node.type];
  return (
    <g
      className={onSelectNode ? "structure-node selectable" : "structure-node"}
      onClick={onSelectNode ? () => onSelectNode(node.name) : undefined}
    >
      <rect
        x={node.x}
        y={node.y}
        width={node.width}
        height={node.height}
        rx={8}
        fill={style.fill}
        stroke={style.stroke}
        strokeWidth={1.5}
      >
        <title>{`${node.name} (${node.type}) — ${node.linkCount} link(s)`}</title>
      </rect>
      <text
        x={node.x + node.width / 2}
        y={node.y + node.height / 2}
        textAnchor="middle"
        dominantBaseline="central"
        className="node-text"
        fill={style.text}
      >
        {node.name}
      </text>
    </g>
  );
}

function BandLabel({ band }: { band: LayoutBand }) {
  return (
    <text x={8} y={band.y + NODE_H / 2} className="band-label">
      {band.type}
    </text>
  );
}

export interface StructureViewProps {
  architecture: Architecture;
  /** Precomputed geometry — the replay view shares one layout between the
   * structure and its overlay so both render in the same coordinate space. */
  layout?: LayoutResult;
  onSelectNode?: (name: string) => void;
  onSelectLink?: (name: string) => void;
  /** Extra SVG content rendered inside the same <svg> after the nodes
   * (replay overlay, T-019). */
  overlay?: ReactNode;
}

export function StructureView({
  architecture,
  layout: externalLayout,
  onSelectNode,
  onSelectLink,
  overlay,
}: StructureViewProps) {
  const { t } = useI18n();
  const computed = useMemo(() => layoutArchitecture(architecture), [architecture]);
  const layout = externalLayout ?? computed;

  if (layout.nodes.length === 0) {
    return <div className="structure-empty">{t("view.structureEmpty")}</div>;
  }

  return (
    <div className="structure-scroll">
      <svg
        className="structure-svg"
        viewBox={`0 0 ${layout.width} ${layout.height}`}
        role="img"
        aria-label={`SDV ${t("app.title")} topology`}
      >
        {layout.bands.map((b, i) => (
          <BandLabel key={`${b.type}-${i}`} band={b} />
        ))}
        {layout.links.map((l, i) => (
          <LinkPath key={`${l.name}-${i}`} link={l} onSelectLink={onSelectLink} />
        ))}
        {layout.nodes.map((n) => (
          <NodeRect key={n.name} node={n} onSelectNode={onSelectNode} />
        ))}
        {overlay}
      </svg>
    </div>
  );
}

// Re-export for callers that want the geometry (e.g. replay overlay T-019).
export { ARC_RISE, NODE_H, NODE_W };
