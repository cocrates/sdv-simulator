/**
 * Event detail panel (T-019; spec ASR-016 보조 패널) — virtualized list of
 * the filtered events, click-to-seek, auto-follow during playback.
 *
 * Virtualization: fixed row height + scroll-window slice, so very large logs
 * (up to 1M events) stay responsive without rendering every row.
 */

import { useEffect, useMemo, useRef, useState } from "react";

import { useI18n } from "./i18n";
import type { MessageKey } from "./i18n/messages";
import { lastEventIndexAtOrBefore } from "./replay/replayIndex";
import type { SimEvent } from "./types/schema";

const ROW_H = 22;

const TYPE_CLASS: Record<SimEvent["type"], string> = {
  tx: "ev-tx",
  rx: "ev-rx",
  task_start: "ev-task",
  task_end: "ev-task",
  drop: "ev-drop",
  overrun: "ev-overrun",
  log: "ev-log",
};

const TYPE_LABEL: Record<SimEvent["type"], MessageKey> = {
  tx: "event.type.tx",
  rx: "event.type.rx",
  task_start: "event.type.task",
  task_end: "event.type.task",
  drop: "event.type.drop",
  overrun: "event.type.overrun",
  log: "event.type.log",
};

function entityText(ev: SimEvent): string {
  const parts: string[] = [];
  if (ev.node) parts.push(ev.node);
  if (ev.link) parts.push(ev.link);
  if (ev.frame) parts.push(ev.frame);
  if (ev.task) parts.push(ev.task);
  return parts.length > 0 ? parts.join(" · ") : "—";
}

interface EventPanelProps {
  events: SimEvent[];
  /** Current playhead — the highlighted row is the last event with t <= it. */
  playTime: number;
  playing: boolean;
  onSeek: (tMs: number) => void;
}

export function EventPanel({ events, playTime, playing, onSeek }: EventPanelProps) {
  const { t } = useI18n();
  const scrollerRef = useRef<HTMLDivElement | null>(null);
  const [scrollTop, setScrollTop] = useState(0);
  const [viewH, setViewH] = useState(300);

  const currentRow = useMemo(
    () => lastEventIndexAtOrBefore(events, playTime),
    [events, playTime],
  );

  useEffect(() => {
    const scroller = scrollerRef.current;
    if (!scroller) return;
    const onScroll = () => setScrollTop(scroller.scrollTop);
    const measure = () => setViewH(scroller.clientHeight);
    onScroll();
    measure();
    scroller.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", measure);
    return () => {
      scroller.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", measure);
    };
  }, []);

  // Auto-follow the playhead while playing.
  useEffect(() => {
    const scroller = scrollerRef.current;
    if (!scroller || !playing || currentRow < 0) return;
    const rowTop = currentRow * ROW_H;
    const rowBottom = rowTop + ROW_H;
    if (rowTop < scroller.scrollTop || rowBottom > scroller.scrollTop + scroller.clientHeight) {
      scroller.scrollTop = rowTop - scroller.clientHeight / 3;
    }
  }, [currentRow, playing]);

  const start = Math.max(0, Math.floor(scrollTop / ROW_H) - 10);
  const end = Math.min(events.length, Math.ceil((scrollTop + viewH) / ROW_H) + 10);
  const rows = events.slice(start, end);

  return (
    <div className="event-panel">
      <div className="event-panel-header">
        <span className="ev-col-time">{t("event.time")}</span>
        <span className="ev-col-type">{t("event.typeLabel")}</span>
        <span className="ev-col-entity">{t("event.entity")}</span>
      </div>
      <div className="event-panel-body" ref={scrollerRef}>
        {events.length === 0 ? (
          <div className="event-empty">{t("event.empty")}</div>
        ) : (
          <div className="event-rows" style={{ height: events.length * ROW_H }}>
            {rows.map((ev, i) => {
              const idx = start + i;
              const isCurrent = idx === currentRow;
              return (
                <button
                  key={idx}
                  type="button"
                  className={`event-row${isCurrent ? " current" : ""}`}
                  style={{ top: idx * ROW_H }}
                  onClick={() => onSeek(ev.t_ms)}
                >
                  <span className="ev-col-time">{ev.t_ms}</span>
                  <span className={`ev-col-type ev-badge ${TYPE_CLASS[ev.type]}`}>
                    {t(TYPE_LABEL[ev.type])}
                  </span>
                  <span className="ev-col-entity" title={entityText(ev)}>
                    {entityText(ev)}
                  </span>
                </button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
