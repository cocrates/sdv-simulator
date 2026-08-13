/**
 * API client for the v2 dashboard (spec/sdv-sim-v2.md, API section).
 *
 * All five endpoints are wrapped as typed `ApiResult<T>` returns. Errors
 * follow F-8: the server answers `{error: {code, message, detail?}}`, and
 * this client unwraps that envelope so callers can switch on the
 * machine-readable `code` (e.g. 409 -> `session_invalid`, F-7).
 *
 * The server never touches the filesystem for user files (F-11): content
 * always travels as strings and the browser manages local files itself.
 */

import type {
  ApiErrorCode,
  ApiResult,
  LoadLogResponse,
  Report,
  RunResponse,
  SimEvent,
  ValidateResponse,
} from "../types/schema";

/** F-8 envelope as it arrives on the wire. */
interface ErrorEnvelope {
  error?: {
    code?: ApiErrorCode;
    message?: string;
    detail?: unknown;
  };
}

async function request<T>(path: string, init?: RequestInit): Promise<ApiResult<T>> {
  let res: Response;
  try {
    res = await fetch(path, init);
  } catch (err) {
    // Network-level failure (server down / unreachable) — not an F-8 body.
    return { ok: false, error: { code: "internal", message: String(err) } };
  }
  let body: unknown = null;
  try {
    body = await res.json();
  } catch {
    // non-JSON error body (e.g. proxy 502) — fall through to the F-8 shape
  }
  if (!res.ok) {
    const envelope = body as ErrorEnvelope | null;
    return {
      ok: false,
      error: {
        code: envelope?.error?.code ?? "internal",
        message: envelope?.error?.message ?? `HTTP ${res.status}`,
      },
    };
  }
  return { ok: true, data: body as T };
}

function post<T>(path: string, payload: unknown): Promise<ApiResult<T>> {
  return request<T>(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

/** POST /api/validate — schema validation; also invalidates the session (M-4). */
export function apiValidate(
  kind: "architecture" | "scenario",
  content: string,
  arch?: string,
): Promise<ApiResult<ValidateResponse>> {
  return post<ValidateResponse>("/api/validate", { kind, content, arch });
}

/** POST /api/run — v1 loads(arch, scenario) + run; replaces the session. */
export function apiRun(architecture: string, scenario: string): Promise<ApiResult<RunResponse>> {
  return post<RunResponse>("/api/run", { architecture, scenario });
}

/** POST /api/load-log — browser-provided v1 events.json; replaces the session. */
export function apiLoadLog(
  content: string,
  name?: string,
  archContent?: string,
): Promise<ApiResult<LoadLogResponse>> {
  return post<LoadLogResponse>("/api/load-log", {
    name,
    content,
    arch_content: archContent,
  });
}

/** GET /api/events — full event list of the current session (409 when invalid). */
export function apiEvents(): Promise<ApiResult<SimEvent[]>> {
  return request<SimEvent[]>("/api/events");
}

/** GET /api/report — current session Report (409 when invalid; M-1 rules). */
export function apiReport(): Promise<ApiResult<Report>> {
  return request<Report>("/api/report");
}
