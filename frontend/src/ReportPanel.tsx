/**
 * Report panel (T-019; spec 리포트·assertion 표시).
 *
 * Full mode (run path / arch-content load-log): the complete v1 Report —
 * simulation, links (incl. bus_load_percent / supersede_count), tasks (incl.
 * period_ms), assertions, warnings.
 *
 * Derived mode (load-log without architecture, M-1): only fields derivable
 * from events — non-derivable cells render as "—" (spec: 미표시 또는 "—").
 * The same component also guards missing fields (the derived report omits
 * them from the payload), so it works without an explicit mode flag.
 */

import { useI18n } from "./i18n";
import type { MessageKey } from "./i18n/messages";
import type { Report } from "./types/schema";

const DASH = "—";

interface ReportPanelProps {
  report: Report;
  /** Log session without arch_content: force "—" for non-derivable fields. */
  derived?: boolean;
}

function cell(value: number | undefined, derived: boolean, derivable: boolean): string {
  if (derived && !derivable) return DASH;
  return typeof value === "number" ? String(value) : DASH;
}

export function ReportPanel({ report, derived = false }: ReportPanelProps) {
  const { t } = useI18n();

  const resultKey: MessageKey =
    report.simulation.result === "pass" ? "report.pass" : "report.fail";

  return (
    <div className="report-panel">
      <section className="report-section">
        <h3>{t("report.simulation")}</h3>
        <table className="report-table">
          <tbody>
            <tr>
              <th>{t("report.duration")}</th>
              <td>{report.simulation.duration_ms} ms</td>
            </tr>
            <tr>
              <th>{t("report.result")}</th>
              <td>
                <span
                  className={`result-badge ${
                    report.simulation.result === "pass" ? "pass" : "fail"
                  }`}
                >
                  {t(resultKey)}
                </span>
              </td>
            </tr>
            <tr>
              <th>{t("report.eventCount")}</th>
              <td>{cell(report.simulation.event_count, derived, true)}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <section className="report-section">
        <h3>{t("report.links")}</h3>
        <table className="report-table report-table-wide">
          <thead>
            <tr>
              <th>{t("report.name")}</th>
              <th>{t("report.kind")}</th>
              <th>{t("report.txCount")}</th>
              <th>{t("report.rxCount")}</th>
              <th>{t("report.dropCount")}</th>
              <th>{t("report.supersedeCount")}</th>
              <th>{t("report.busLoad")}</th>
            </tr>
          </thead>
          <tbody>
            {report.links.map((l) => (
              <tr key={l.name}>
                <td>{l.name}</td>
                <td>{l.kind ?? DASH}</td>
                <td>{cell(l.tx_count, derived, true)}</td>
                <td>{cell(l.rx_count, derived, true)}</td>
                <td>{cell(l.drop_count, derived, true)}</td>
                <td>{cell(l.supersede_count, derived, false)}</td>
                <td>
                  {derived
                    ? DASH
                    : typeof l.bus_load_percent === "number"
                      ? `${l.bus_load_percent.toFixed(1)}%`
                      : DASH}
                </td>
              </tr>
            ))}
            {report.links.length === 0 && (
              <tr>
                <td colSpan={7} className="report-none">
                  {t("report.none")}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </section>

      <section className="report-section">
        <h3>{t("report.tasks")}</h3>
        <table className="report-table report-table-wide">
          <thead>
            <tr>
              <th>{t("report.node")}</th>
              <th>{t("report.task")}</th>
              <th>{t("report.period")}</th>
              <th>{t("report.runCount")}</th>
              <th>{t("report.overrunCount")}</th>
            </tr>
          </thead>
          <tbody>
            {report.tasks.map((task) => (
              <tr key={`${task.node}:${task.task}`}>
                <td>{task.node}</td>
                <td>{task.task}</td>
                <td>{cell(task.period_ms, derived, false)}</td>
                <td>{cell(task.run_count, derived, true)}</td>
                <td>{cell(task.overrun_count, derived, true)}</td>
              </tr>
            ))}
            {report.tasks.length === 0 && (
              <tr>
                <td colSpan={5} className="report-none">
                  {t("report.none")}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </section>

      <section className="report-section">
        <h3>{t("report.assertions")}</h3>
        <table className="report-table report-table-wide">
          <thead>
            <tr>
              <th>{t("report.name")}</th>
              <th>{t("report.status")}</th>
              <th>{t("report.detail")}</th>
            </tr>
          </thead>
          <tbody>
            {report.assertions.map((a) => (
              <tr key={a.name}>
                <td>{a.name}</td>
                <td>
                  <span className={`result-badge ${a.status === "pass" ? "pass" : "fail"}`}>
                    {t(a.status === "pass" ? "report.pass" : "report.fail")}
                  </span>
                </td>
                <td className="report-detail">{a.detail || DASH}</td>
              </tr>
            ))}
            {report.assertions.length === 0 && (
              <tr>
                <td colSpan={3} className="report-none">
                  {t("report.none")}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </section>

      {!derived && report.warnings.length > 0 && (
        <section className="report-section">
          <h3>{t("report.warnings")}</h3>
          <ul className="report-warnings">
            {report.warnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
