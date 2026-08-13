/**
 * Debounced server validation hook (editor-validation-feedback Option A,
 * spec ASR-018): the *server* validates with the v1 Pydantic schemas —
 * nothing is ported to the frontend.
 *
 * - edits are validated 500 ms after the last change (spec: 편집 중 디바운스
 *   500ms 자동 검증);
 * - `forceValidate()` validates immediately — the spec requires a forced
 *   validation on save/run (실패 시 저장·실행 거부);
 * - stale responses are ignored via a sequence guard;
 * - a scenario is validated against the architecture only when a *valid*
 *   architecture is supplied (F-4: scenario-alone = structure only, with arch
 *   = structure + reference validation). The caller decides whether to pass
 *   `arch` (it should only pass a currently-valid architecture).
 */

import { useCallback, useEffect, useRef, useState } from "react";

import { apiValidate } from "./api/client";
import type { FileKind } from "./fileManager";

export type ValidationStatus = "idle" | "validating" | "valid" | "invalid" | "offline";

export interface ValidationIssue {
  path: string | null;
  line: number | null;
  message: string;
}

export interface ValidationState {
  status: ValidationStatus;
  issues: ValidationIssue[];
  /** Force an immediate (non-debounced) validation; resolves to `valid`. */
  forceValidate: () => Promise<boolean>;
}

const DEBOUNCE_MS = 500;

export function useValidation(kind: FileKind, content: string, arch?: string): ValidationState {
  const [status, setStatus] = useState<ValidationStatus>("idle");
  const [issues, setIssues] = useState<ValidationIssue[]>([]);

  // Latest inputs, read at fire time so the debounce timer always validates
  // the most recent content even if the component hasn't re-rendered.
  const latest = useRef({ kind, content, arch });
  latest.current = { kind, content, arch };

  const seq = useRef(0);
  const timer = useRef<number | null>(null);

  const run = useCallback(async (): Promise<boolean> => {
    const id = ++seq.current;
    const { kind: k, content: c, arch: a } = latest.current;
    if (c.trim() === "") {
      setStatus("idle");
      setIssues([]);
      return true;
    }
    setStatus("validating");
    const res = await apiValidate(k, c, k === "scenario" ? a : undefined);
    if (id !== seq.current) return false; // superseded by a newer call
    if (!res.ok) {
      if (res.error.code === "validation_error") {
        const detail = Array.isArray(res.error.detail)
          ? (res.error.detail as ValidationIssue[])
          : [];
        setStatus("invalid");
        setIssues(detail);
      } else {
        setStatus("offline");
        setIssues([]);
      }
      return false;
    }
    setStatus(res.data.valid ? "valid" : "invalid");
    setIssues(res.data.errors);
    return res.data.valid;
  }, []);

  const forceValidate = useCallback(async (): Promise<boolean> => {
    if (timer.current !== null) {
      window.clearTimeout(timer.current);
      timer.current = null;
    }
    return run();
  }, [run]);

  useEffect(() => {
    if (timer.current !== null) window.clearTimeout(timer.current);
    timer.current = window.setTimeout(() => {
      void run();
    }, DEBOUNCE_MS);
    return () => {
      if (timer.current !== null) window.clearTimeout(timer.current);
    };
  }, [kind, content, arch, run]);

  return { status, issues, forceValidate };
}
