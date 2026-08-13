/**
 * Determinism / band-rule check for the layout (M-5, F-6). Run with Node's
 * native TypeScript type stripping:
 *
 *   node scripts/check-layout.ts
 *
 * Verifies, on both a synthetic architecture and the bundled sample:
 *   1. determinism — same input twice ⇒ byte-identical coordinates;
 *   2. band ordering — HPC above Gateway above ECU (when present);
 *   3. within-band ordering — link count desc, then name asc;
 *   4. CAN/Ethernet are visual-only — kinds are preserved on links and
 *      different kinds never change positions.
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

// NOTE: runtime imports need explicit `.ts` extensions for Node's native type
// stripping; type-only imports are erased and may stay extensionless.
import { layoutArchitecture } from "../src/layout.ts";
import type { Architecture, LinkKind } from "../src/types/schema";
import { parseArchitecture } from "../src/yaml.ts";

let failures = 0;

function check(name: string, ok: boolean, detail?: string): void {
  if (!ok) {
    failures += 1;
    console.error(`FAIL ${name}${detail ? ` — ${detail}` : ""}`);
  } else {
    console.log(`ok   ${name}`);
  }
}

function archYaml(): string {
  const here = fileURLToPath(new URL(".", import.meta.url));
  // scripts/ → frontend/ → project root → samples/basic/architecture.yaml
  const text = readFileSync(`${here}../../samples/basic/architecture.yaml`, "utf8");
  return text;
}

// Synthetic architecture covering: HPC/ECU bands, a gateway, same-band links,
// mixed link kinds, and duplicate link counts (for the tie-break).
const synthetic: Architecture = {
  nodes: [
    { name: "z_ecu", type: "ECU", components: [] },
    { name: "a_ecu", type: "ECU", components: [] },
    { name: "main_hpc", type: "HPC", components: [] },
  ],
  links: [
    { name: "can_a", kind: "can", bitrate: 500, nodes: ["main_hpc", "a_ecu"], frames: [{ name: "f1", id: 1, dlc: 8, period_ms: 10, source: "main_hpc" }] },
    { name: "can_z", kind: "can", bitrate: 500, nodes: ["main_hpc", "z_ecu"], frames: [] },
    { name: "eth_same", kind: "ethernet", bitrate: 1000, nodes: ["a_ecu", "z_ecu"], frames: [] },
  ],
  gateways: [{ name: "gw1", routes: [] }],
};

function verify(arch: Architecture, label: string, expectBothKinds: boolean): void {
  const once = layoutArchitecture(arch);
  const twice = layoutArchitecture(arch);
  check(`${label}: determinism (identical coordinates)`, JSON.stringify(once) === JSON.stringify(twice));

  if (once.nodes.length === 0) return;

  const bands = once.bands.map((b) => b.type);
  const bandOrder: Record<string, number> = { HPC: 0, Gateway: 1, ECU: 2 };
  const orderOk = bands.every((b, i) => (i === 0 ? true : bandOrder[bands[i - 1]] < bandOrder[b]));
  check(`${label}: band order HPC < Gateway < ECU`, orderOk, `got ${bands.join(",")}`);

  // within-band ordering: link count desc, then name asc
  for (let bi = 0; bi < once.bands.length; bi += 1) {
    const list = once.nodes.filter((n) => n.band === bi);
    for (let i = 1; i < list.length; i += 1) {
      const prev = list[i - 1];
      const cur = list[i];
      const ok =
        cur.linkCount < prev.linkCount || (cur.linkCount === prev.linkCount && prev.name < cur.name);
      check(`${label}: band ${once.bands[bi].type} sorted (${prev.name} → ${cur.name})`, ok);
    }
  }

  if (expectBothKinds) {
    // link kinds preserved
    const kinds = new Set(once.links.map((l) => l.kind));
    check(`${label}: CAN + Ethernet kinds both present`, kinds.has("can") && kinds.has("ethernet"));
  }
}

verify(synthetic, "synthetic", true);
verify(parseArchitecture(archYaml()) ?? { nodes: [], links: [], gateways: [] }, "sample", false);

// Same-band links exist on the synthetic arch and carry a control point.
const synth = layoutArchitecture(synthetic);
const sameBand = synth.links.find((l) => l.control !== undefined);
check("synthetic: same-band arc has control point", sameBand !== undefined);

// Visual-only check: swapping a link kind must not move any node.
const canOnly = layoutArchitecture({ ...synthetic, links: synthetic.links.map((l) => ({ ...l, kind: "can" as LinkKind })) });
const ethOnly = layoutArchitecture({ ...synthetic, links: synthetic.links.map((l) => ({ ...l, kind: "ethernet" as LinkKind })) });
check(
  "kind change does not affect positions",
  JSON.stringify(canOnly.nodes) === JSON.stringify(ethOnly.nodes),
);

if (failures > 0) {
  console.error(`\n${failures} check(s) failed`);
  process.exit(1);
}
console.log("\nall layout checks passed");
