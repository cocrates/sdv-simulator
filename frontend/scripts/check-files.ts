/**
 * Pure file-manager checks (T-018): templates parse and carry the v1 minimum
 * required fields with intact references; kind inference and file naming
 * follow the F-11 browser model. Run with Node's native type stripping:
 *
 *   node scripts/check-files.ts
 */

import { load } from "js-yaml";

// NOTE: runtime imports need explicit `.ts` extensions for Node's native type
// stripping; type-only imports are erased and may stay extensionless.
import {
  architectureTemplate,
  inferFileKind,
  makeEditorFile,
  scenarioTemplate,
  suggestFileName,
} from "../src/fileManager.ts";
import type { FileKind } from "../src/fileManager";

let failures = 0;

function check(name: string, ok: boolean, detail?: string): void {
  if (!ok) {
    failures += 1;
    console.error(`FAIL ${name}${detail ? ` — ${detail}` : ""}`);
  } else {
    console.log(`ok   ${name}`);
  }
}

type AnyRecord = Record<string, unknown>;

function asRecord(v: unknown): AnyRecord | null {
  return typeof v === "object" && v !== null ? (v as AnyRecord) : null;
}

function asArray(v: unknown): unknown[] {
  return Array.isArray(v) ? v : [];
}

function asString(v: unknown): string {
  return typeof v === "string" ? v : "";
}

function records(v: unknown): AnyRecord[] {
  return asArray(v)
    .map(asRecord)
    .filter((r): r is AnyRecord => r !== null);
}

// ---------------------------------------------------------- architecture template

const archText = architectureTemplate();
let archRaw: unknown = null;
try {
  archRaw = load(archText);
} catch (e) {
  console.error(`YAML parse of architecture template failed: ${String(e)}`);
}
const archRoot = asRecord(archRaw);
const archNodes = archRoot ? records(archRoot.nodes) : [];
const archLinks = archRoot ? records(archRoot.links) : [];

check("arch template parses as YAML", archRoot !== null);
check("arch template has nodes[] with >= 1 node", archNodes.length >= 1);
check("arch template has links[] with >= 1 link", archLinks.length >= 1);
check("arch template has gateways[]", archRoot ? Array.isArray(archRoot.gateways) : false);

const node0 = archNodes[0];
check(
  "arch node has name/type(ECU|HPC)/components[]",
  node0 != null &&
    asString(node0.name) !== "" &&
    (node0.type === "ECU" || node0.type === "HPC") &&
    Array.isArray(node0.components),
);

const link0 = archLinks[0];
const linkNodes = link0 ? asArray(link0.nodes).map(asString) : [];
const frames = link0 ? records(link0.frames) : [];
check(
  "arch link has name/kind/bitrate/nodes/frames",
  link0 != null &&
    asString(link0.name) !== "" &&
    (link0.kind === "can" || link0.kind === "ethernet") &&
    typeof link0.bitrate === "number" &&
    linkNodes.length >= 2 &&
    frames.length >= 1,
);

const frame0 = frames[0];
check(
  "arch frame has name/id/dlc/period_ms/source",
  frame0 != null &&
    asString(frame0.name) !== "" &&
    typeof frame0.id === "number" &&
    typeof frame0.dlc === "number" &&
    typeof frame0.period_ms === "number" &&
    asString(frame0.source) !== "",
);
check("arch frame.source is connected to the link", frame0 != null && linkNodes.includes(asString(frame0.source)));

const nodeNames = archNodes.map((n) => asString(n.name));
check("arch link.nodes exist as nodes", linkNodes.every((n) => nodeNames.includes(n)));

const frameMessages = frames.map((f) => asString(f.message) || asString(f.name));
const compMsgs: string[] = [];
for (const node of archNodes) {
  for (const comp of records(node.components)) {
    compMsgs.push(...asArray(comp.sends).map(asString), ...asArray(comp.receives).map(asString));
  }
}
const unresolved = compMsgs.filter((m) => m !== "" && !frameMessages.includes(m));
check(
  "component sends/receives map to a frame message",
  unresolved.length === 0,
  unresolved.length > 0 ? `unresolved: ${unresolved.join(", ")}` : undefined,
);

// ------------------------------------------------------------ scenario template

const scenText = scenarioTemplate();
let scenRaw: unknown = null;
try {
  scenRaw = load(scenText);
} catch (e) {
  console.error(`YAML parse of scenario template failed: ${String(e)}`);
}
const scenRoot = asRecord(scenRaw);
check("scenario template parses as YAML", scenRoot !== null);
check(
  "scenario template has duration_ms/messages[]/assertions[]",
  scenRoot != null &&
    typeof scenRoot.duration_ms === "number" &&
    Array.isArray(scenRoot.messages) &&
    Array.isArray(scenRoot.assertions),
);
check(
  "scenario template has >= 1 injected message (immediately runnable)",
  scenRoot != null && Array.isArray(scenRoot.messages) && scenRoot.messages.length >= 1,
);
check(
  "scenario template has >= 1 assertion",
  scenRoot != null && Array.isArray(scenRoot.assertions) && scenRoot.assertions.length >= 1,
);

// ---------------------------------------------------------------- inference

check("inferFileKind('architecture.yaml', …) = architecture", inferFileKind("architecture.yaml", "") === "architecture");
check("inferFileKind('scenario.yaml', …) = scenario", inferFileKind("scenario.yaml", "") === "scenario");
check("inferFileKind('arch_test.yml', …) = architecture", inferFileKind("arch_test.yml", "") === "architecture");
check("inferFileKind('my_scenario.yml', …) = scenario", inferFileKind("my_scenario.yml", "") === "scenario");
check(
  "inferFileKind(content duration_ms) = scenario",
  inferFileKind("random.txt", "duration_ms: 50\n") === "scenario",
);
check(
  "inferFileKind(content nodes+links) = architecture",
  inferFileKind("random.txt", "nodes: []\nlinks: []\n") === "architecture",
);
check("inferFileKind(unknown) defaults to architecture", inferFileKind("whatever.txt", "") === "architecture");

// ------------------------------------------------------------------- names

check(
  "suggestFileName(architecture) = new_architecture.yaml",
  suggestFileName("architecture" as FileKind) === "new_architecture.yaml",
);
check(
  "suggestFileName(scenario) = new_scenario.yaml",
  suggestFileName("scenario" as FileKind) === "new_scenario.yaml",
);

const made = makeEditorFile("x.yaml", archText);
check(
  "makeEditorFile starts clean with inferred kind and no handle",
  made.dirty === false && made.kind === "architecture" && made.handle === null,
);
check("makeEditorFile id is non-empty", made.id !== "");

if (failures > 0) {
  console.error(`\n${failures} check(s) FAILED`);
  process.exit(1);
}
console.log("\nall file-manager checks passed");
