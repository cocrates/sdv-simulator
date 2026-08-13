/**
 * Report view (T-019, route #/report) — fetches the current session Report
 * (GET /api/report, F-7: 409 session_invalid when the session is absent) and
 * renders `ReportPanel`.
 *
 * T-024: when `sessionMeta?.invalidated` is set (editing started since the
 * session), the view shows the "invalidated" notice locally instead of asking
 * the server — invalidation is frontend-local and validate no longer kills the
 * session.
 */

import { useEffect, useState } from "react";

import { useI18n } from "./i18n";
import { apiReport } from "./api/client";
import { ReportPanel } from "./ReportPanel";
import type { Report, SessionMeta } from "./types/schema";

type Status =
  | { kind: "loading" }
  | { kind: "ready"; report: Report }
  | { kind: "error"; message: string };

export function ReportView({
  derived,
  sessionMeta,
}: {
  derived?: boolean;
  sessionMeta?: SessionMeta | null;
}) {
  const { t } = useI18n();
  const [status, setStatus] = useState<Status>({ kind: "loading" });

  useEffect(() => {
    let cancelled = false;
    // M-4 (T-024): editing since the session invalidates the report locally.
    if (sessionMeta?.invalidated) {
      setStatus({ kind: "error", message: t("status.sessionInvalid") });
      return;
    }
    setStatus({ kind: "loading" });
    void apiReport().then((res) => {
      if (cancelled) return;
      if (res.ok) setStatus({ kind: "ready", report: res.data });
      else if (res.error.code === "session_invalid") {
        setStatus({ kind: "error", message: t("status.noSession") });
      } else {
        setStatus({ kind: "error", message: t("status.serverOffline") });
      }
    });
    return () => {
      cancelled = true;
    };
  }, [t, sessionMeta]);

  if (status.kind === "loading") {
    return <div className="view-placeholder">{t("status.loading")}</div>;
  }
  if (status.kind === "error") {
    return <div className="view-placeholder">{status.message}</div>;
  }
  return <ReportPanel report={status.report} derived={derived} />;
}
