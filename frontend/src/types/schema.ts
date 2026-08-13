/**
 * Shared types for the v2 dashboard frontend.
 *
 * Mirrors the wire contracts in spec/sdv-sim-v2.md and the v1 schemas in
 * spec/sdv-sim-v1.md (event log schema D-18, Report D-21, arch/scenario
 * field trees D-12). These are *client-side views* of the server payloads —
 * the server remains the validation authority (v1 Pydantic schemas are not
 * ported to the frontend; ASR-018).
 */

// ------------------------------------------------------------------ events

/** v1 event log schema: type enum 7종 (v1 D-18). */
export type EventType = "tx" | "rx" | "task_start" | "task_end" | "drop" | "overrun" | "log";

/**
 * One simulation event as recorded by the v1 log writer.
 * Absent fields are omitted on the wire (same rule as the v1 writer).
 */
export interface SimEvent {
  t_ms: number;
  seq: number;
  type: EventType;
  node?: string;
  link?: string;
  frame?: string;
  task?: string;
  data?: Record<string, unknown>;
}

/** v1 event log document (schema_version 1) as produced by the v1 CLI. */
export interface EventLogDocument {
  schema_version: 1;
  simulation: {
    duration_ms: number;
    result: "pass" | "fail";
  };
  events: SimEvent[];
  assertions: AssertionResult[];
}

// ------------------------------------------------------------------ report

export type LinkKind = "can" | "ethernet";

/** v1 Report.links[] (v1 D-21). */
export interface ReportLink {
  name: string;
  kind: LinkKind;
  tx_count: number;
  rx_count: number;
  drop_count: number;
  supersede_count: number;
  bus_load_percent: number;
}

/** v1 Report.tasks[] (v1 D-21). */
export interface ReportTask {
  node: string;
  task: string;
  period_ms: number;
  run_count: number;
  overrun_count: number;
}

export interface AssertionResult {
  name: string;
  status: "pass" | "fail";
  detail: string;
}

/**
 * v1 Report (v1 D-21). The dashboard displays the full report on the run
 * path; the load-log path only shows derivable items (M-1) — the frontend
 * renders missing/derivable-only fields as "—" rather than hiding them here,
 * so the same type serves both paths.
 */
export interface Report {
  simulation: {
    duration_ms: number;
    result: "pass" | "fail";
    event_count: number;
  };
  links: ReportLink[];
  tasks: ReportTask[];
  assertions: AssertionResult[];
  warnings: string[];
}

// ---------------------------------------------------------------- arch/scenario

/** v1 architecture.yaml field tree (v1 D-12). */
export interface Architecture {
  nodes: ArchitectureNode[];
  links: ArchitectureLink[];
  gateways?: ArchitectureGateway[];
}

export interface ArchitectureNode {
  name: string;
  type: "ECU" | "HPC";
  components: ArchitectureComponent[];
}

export interface ArchitectureComponent {
  name: string;
  sends: string[];
  receives: string[];
  tasks?: ArchitectureTask[];
}

export interface ArchitectureTask {
  name: string;
  period_ms: number;
  priority: number;
  wcet_ms?: number;
}

export interface ArchitectureLink {
  name: string;
  kind: LinkKind;
  bitrate: number;
  nodes: string[];
  frames: ArchitectureFrame[];
  switches?: ArchitectureSwitch[];
}

export interface ArchitectureFrame {
  name: string;
  id: number;
  dlc: number;
  period_ms: number;
  source: string;
  message?: string;
}

export interface ArchitectureSwitch {
  name?: string;
  queue_depth?: number;
}

export interface ArchitectureGateway {
  name: string;
  routes: GatewayRoute[];
}

export interface GatewayRoute {
  from: { link: string; frame?: string; id_min?: number; id_max?: number };
  to: { link: string; remap_id?: number };
  delay_ms?: number;
}

/** v1 scenario.yaml field tree (v1 D-12). */
export interface Scenario {
  duration_ms: number;
  seed?: unknown;
  messages: ScenarioMessage[];
  assertions: ScenarioAssertion[];
}

export interface ScenarioMessage {
  t_ms: number;
  link: string;
  frame: string;
  data?: Record<string, unknown>;
}

export interface ScenarioAssertion {
  name?: string;
  expect: {
    event: "tx" | "rx" | "task";
    frame?: string;
    message?: string;
    node?: string;
    link?: string;
    task?: string;
    at_ms?: number;
    within_ms?: number;
    count?: number;
  };
}

// ------------------------------------------------------------------- API (F-8)

/**
 * F-8 error envelope: every API error is `{error: {code, message, detail?}}`.
 * `code` is machine-readable; `message` is localized in the server language.
 */
export interface ApiErrorBody {
  error: {
    code: ApiErrorCode;
    message: string;
    detail?: Array<{ path: string | null; line: number | null; message: string }>;
  };
}

export type ApiErrorCode =
  | "validation_error"
  | "log_invalid"
  | "session_invalid"
  | "not_found"
  | "internal";

/** Discriminated result of an API call: either the payload or the F-8 error. */
export type ApiResult<T> = { ok: true; data: T } | { ok: false; error: ApiErrorBody["error"] };

// --------------------------------------------------------------- API payloads

/** POST /api/validate — {valid, errors: [{path, line, message}]}. */
export interface ValidateResponse {
  valid: boolean;
  errors: Array<{ path: string | null; line: number | null; message: string }>;
}

/** POST /api/run — lightweight result; events come from GET /api/events. */
export interface RunResponse {
  duration_ms: number;
  event_count: number;
  report: Report;
}

/** POST /api/load-log — session replaced; events come from GET /api/events. */
export interface LoadLogResponse {
  name?: string;
  duration_ms: number;
  event_count: number;
  report: Report;
}

/** Client-side summary of the current server session (set by run/load-log
 * responses; drives the replay timeline length and report derivation flag).
 * `invalidated` is a **frontend-local** flag (M-4, T-024): set when editing
 * starts so replay/report can show "invalidated" without relying on the server
 * deriving invalidation from validate calls. */
export interface SessionMeta {
  duration_ms: number;
  source: "run" | "log";
  /** load-log session that included arch_content (full report + physical
   * playback — M-1 / M-2). */
  logWithArch: boolean;
  /** true once the editor content has changed since this session (edit-time
   * invalidation, M-4). Cleared by run/load-log. */
  invalidated: boolean;
}
