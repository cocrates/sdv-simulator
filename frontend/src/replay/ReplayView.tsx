/**
 * Replay view (T-019, route #/replay) — the simulation overlay stage.
 *
 * Fetches the current session (events + report) and drives local playback:
 *   - controls: play/pause, restart, timeline scrub, speed 0.5/1/2/4x
 *     (spec ASR-016 컨트롤);
 *   - timeline length: run = scenario.duration_ms, log = simulation.duration_ms
 *     (from SessionMeta; last-event fallback after a page refresh);
 *   - seek: O(K) snapshot+re-apply engine (M-3), incremental advance while
 *     playing;
 *   - overlay: in-flight frames / task · overrun · drop highlights / bus load
 *     badges (ASR-016), pulse + "approximate" label for arch-less logs (F-5);
 *   - filters: event-type checkboxes + structure-click entity filter;
 *   - load-log: browser-picked v1 events.json → POST /api/load-log, with the
 *     current valid architecture as arch_content when available (F-2).
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { useI18n } from "../i18n";
import { apiEvents, apiLoadLog, apiReport } from "../api/client";
import { layoutArchitecture } from "../layout";
import { StructureView } from "../StructureView";
import { EventPanel } from "../EventPanel";
import { ReplayOverlay } from "./ReplayOverlay";
import { useReplayClock } from "./useReplayClock";
import {
  advanceToTime,
  buildReplayIndex,
  buildTxMsMap,
  seekToTime,
} from "./replayIndex";
import type { ReplayFilter, ReplayIndex, ReplayMode, SeekState } from "./replayIndex";
import { openLogFile } from "../fileManager";
import type { Architecture, Report, ReportLink, SessionMeta, SimEvent } from "../types/schema";

type ViewStatus = "loading" | "ready" | "invalid" | "noSession" | "error";

const DEFAULT_FILTER: ReplayFilter = {
  tx: true,
  rx: true,
  task: true,
  drop: true,
  overrun: true,
  log: true,
};

const SPEEDS = [0.5, 1, 2, 4] as const;

function typeGroup(type: SimEvent["type"]): keyof ReplayFilter {
  return type === "task_start" || type === "task_end" ? "task" : type;
}

interface ReplayViewProps {
  arch: Architecture | null;
  archContent: string | undefined;
  sessionMeta: SessionMeta | null;
  onSessionChange: (meta: SessionMeta) => void;
}

export function ReplayView({ arch, archContent, sessionMeta, onSessionChange }: ReplayViewProps) {
  const { t } = useI18n();

  const [status, setStatus] = useState<ViewStatus>("loading");
  const [index, setIndex] = useState<ReplayIndex | null>(null);
  const [report, setReport] = useState<Report | null>(null);
  const [filter, setFilter] = useState<ReplayFilter>(DEFAULT_FILTER);
  const [entityFilter, setEntityFilter] = useState<{ kind: "node" | "link"; name: string } | null>(null);
  const [logError, setLogError] = useState<string | null>(null);

  // ------------------------------------------------------------ session fetch

  useEffect(() => {
    let cancelled = false;
    // M-4 (T-024): editing since the session invalidates the replay locally —
    // the server session may still exist, so the frontend must not ask for it.
    if (sessionMeta?.invalidated) {
      setStatus("invalid");
      return;
    }
    setStatus("loading");
    void (async () => {
      const [evRes, repRes] = await Promise.all([apiEvents(), apiReport()]);
      if (cancelled) return;
      if (!evRes.ok || !repRes.ok) {
        const failed = evRes.ok ? repRes : evRes;
        if (!failed.ok && failed.error.code === "session_invalid") {
          setStatus(sessionMeta ? "invalid" : "noSession");
        } else {
          setStatus("error");
        }
        return;
      }
      // Full report present (bus_load_percent) ⇔ the session has an
      // architecture (run always; load-log only with arch_content, M-1) ⇒
      // physical tx_ms playback. Otherwise pulse + approximate (F-5).
      const mode: ReplayMode =
        repRes.data.links.some((l) => typeof l.bus_load_percent === "number")
          ? "physical"
          : "pulse";
      const durationMs =
        sessionMeta?.duration_ms ?? evRes.data[evRes.data.length - 1]?.t_ms ?? 0;
      try {
        const built = buildReplayIndex(evRes.data, {
          mode,
          txMs: mode === "physical" && arch ? buildTxMsMap(arch) : undefined,
          durationMs,
        });
        if (cancelled) return;
        setIndex(built);
        setReport(repRes.data);
        setStatus("ready");
      } catch (e) {
        if (!cancelled) setStatus("error");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [sessionMeta, arch]);

  const durationMs = index?.durationMs ?? 0;
  const clock = useReplayClock(durationMs);

  // --------------------------------------------------------- seek / advance

  const stateRef = useRef<SeekState | null>(null);
  const appliedRef = useRef(-1);
  const lastTimeRef = useRef(-1);
  const [state, setState] = useState<SeekState | null>(null);

  useEffect(() => {
    if (!index) {
      stateRef.current = null;
      setState(null);
      return;
    }
    const at = seekToTime(index, 0);
    stateRef.current = at.state;
    appliedRef.current = at.appliedIndex;
    lastTimeRef.current = 0;
    setState(at.state);
  }, [index]);

  useEffect(() => {
    if (!index || !stateRef.current) return;
    const t = clock.playTime;
    if (t < lastTimeRef.current) {
      const at = seekToTime(index, t);
      stateRef.current = at.state;
      appliedRef.current = at.appliedIndex;
    } else {
      appliedRef.current = advanceToTime(index, stateRef.current, appliedRef.current, t);
    }
    lastTimeRef.current = t;
    setState(stateRef.current);
  }, [clock.playTime, index]);

  // --------------------------------------------------------------- helpers

  const reportLinks = useMemo(() => {
    if (!report) return undefined;
    const m = new Map<string, ReportLink>();
    for (const l of report.links) m.set(l.name, l);
    return m;
  }, [report]);

  const layout = useMemo(() => (arch ? layoutArchitecture(arch) : null), [arch]);

  const filteredEvents = useMemo(() => {
    if (!index) return [];
    return index.events.filter((ev) => {
      const group = typeGroup(ev.type);
      if (!filter[group]) return false;
      if (entityFilter) {
        const entity = ev.node ?? ev.link;
        if (entity !== entityFilter.name) return false;
      }
      return true;
    });
  }, [index, filter, entityFilter]);

  // ---------------------------------------------------------------- actions

  const toggleFilter = useCallback((key: keyof ReplayFilter) => {
    setFilter((f) => ({ ...f, [key]: !f[key] }));
  }, []);

  const handleSelectNode = useCallback((name: string) => {
    setEntityFilter((f) => (f?.kind === "node" && f.name === name ? null : { kind: "node", name }));
  }, []);

  const handleSelectLink = useCallback((name: string) => {
    setEntityFilter((f) => (f?.kind === "link" && f.name === name ? null : { kind: "link", name }));
  }, []);

  const handleLoadLog = useCallback(async () => {
    const file = await openLogFile();
    if (!file) return;
    const res = await apiLoadLog(file.content, file.name, archContent);
    if (!res.ok) {
      setLogError(res.error.message);
      return;
    }
    setLogError(null);
    onSessionChange({
      duration_ms: res.data.duration_ms,
      source: "log",
      logWithArch: archContent !== undefined,
      invalidated: false,
    });
  }, [archContent, onSessionChange]);

  // ----------------------------------------------------------------- render

  if (status === "loading") {
    return <div className="view-placeholder">{t("status.loading")}</div>;
  }
  if (status === "noSession") {
    return <div className="view-placeholder">{t("status.noSession")}</div>;
  }
  if (status === "invalid") {
    return <div className="view-placeholder">{t("status.sessionInvalid")}</div>;
  }
  if (status === "error" || !index) {
    return <div className="view-placeholder">{t("status.serverOffline")}</div>;
  }

  const mode = index.mode;
  const filterKeys: Array<keyof ReplayFilter> = ["tx", "rx", "task", "drop", "overrun", "log"];

  return (
    <section className="view-replay" data-view="replay">
      <div className="replay-toolbar">
        <button type="button" className="tool-btn btn-run" onClick={clock.toggle}>
          {clock.playing ? t("replay.pause") : t("replay.play")}
        </button>
        <button type="button" className="tool-btn" onClick={clock.restart}>
          {t("replay.restart")}
        </button>
        <input
          type="range"
          className="replay-timeline"
          min={0}
          max={Math.max(1, durationMs)}
          step={1}
          value={Math.min(clock.playTime, Math.max(1, durationMs))}
          onChange={(e) => clock.seekTo(Number(e.target.value))}
          aria-label={t("replay.timeline")}
        />
        <span className="replay-time">
          {Math.round(clock.playTime)} / {durationMs} ms
        </span>
        <div className="replay-speeds" role="group" aria-label={t("replay.speed")}>
          {SPEEDS.map((s) => (
            <button
              key={s}
              type="button"
              className={`tool-btn${clock.speed === s ? " active" : ""}`}
              onClick={() => clock.setSpeed(s)}
            >
              {s}x
            </button>
          ))}
        </div>
        <span className="toolbar-spacer" />
        <button type="button" className="tool-btn" onClick={() => void handleLoadLog()}>
          {t("replay.loadLog")}
        </button>
      </div>

      <div className="replay-filterbar">
        <span className="replay-filter-label">{t("replay.filters")}</span>
        {filterKeys.map((key) => (
          <label key={key} className="replay-filter-chip">
            <input
              type="checkbox"
              checked={filter[key]}
              onChange={() => toggleFilter(key)}
            />
            {t(`event.type.${key === "task" ? "task" : key}` as const)}
          </label>
        ))}
        {entityFilter && (
          <span className="replay-entity-filter">
            {t("replay.entityFilter", { name: entityFilter.name })}
            <button type="button" className="replay-entity-clear" onClick={() => setEntityFilter(null)}>
              ×
            </button>
          </span>
        )}
      </div>

      {logError && <div className="replay-log-error">{logError}</div>}

      <div className="replay-body">
        <div className="replay-stage">
          {arch && layout ? (
            <StructureView
              architecture={arch}
              layout={layout}
              onSelectNode={handleSelectNode}
              onSelectLink={handleSelectLink}
              overlay={
                state ? (
                  <ReplayOverlay
                    layout={layout}
                    state={state}
                    playTime={clock.playTime}
                    mode={mode}
                    filter={filter}
                    reportLinks={reportLinks}
                  />
                ) : null
              }
            />
          ) : (
            <div className="structure-empty">{t("replay.noStructure")}</div>
          )}
        </div>
        <EventPanel
          events={filteredEvents}
          playTime={clock.playTime}
          playing={clock.playing}
          onSeek={clock.seekTo}
        />
      </div>
    </section>
  );
}
