/**
 * Replay playback clock (T-019): a requestAnimationFrame-driven playhead.
 *
 * The clock owns wall-clock time translation at a playback `speed`
 * (0.5x/1x/2x/4x, spec ASR-016 컨트롤). It only moves time — the consumer
 * (ReplayView) reacts to `playTime` changes and advances/seeks the replay
 * state (incremental forward application vs O(K) snapshot seek).
 *
 * Auto-pauses when the playhead reaches the timeline end.
 */

import { useCallback, useEffect, useRef, useState } from "react";

export interface ReplayClock {
  playTime: number;
  playing: boolean;
  speed: number;
  toggle: () => void;
  pause: () => void;
  setSpeed: (speed: number) => void;
  /** Scrub: jump the playhead (clamped). Does not change the play state. */
  seekTo: (tMs: number) => void;
  /** Jump back to 0 and pause. */
  restart: () => void;
}

export function useReplayClock(durationMs: number): ReplayClock {
  const [playTime, setPlayTime] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeedState] = useState(1);

  const timeRef = useRef(0);
  const durationRef = useRef(durationMs);
  const speedRef = useRef(1);
  const playingRef = useRef(false);
  const rafRef = useRef<number | null>(null);
  const lastNowRef = useRef<number | null>(null);

  durationRef.current = durationMs;

  // Reset the playhead when the session changes (new run / new log).
  useEffect(() => {
    timeRef.current = 0;
    lastNowRef.current = null;
    setPlayTime(0);
  }, [durationMs]);

  const setTime = useCallback((tMs: number) => {
    const clamped = Math.max(0, Math.min(durationRef.current, tMs));
    timeRef.current = clamped;
    lastNowRef.current = null;
    setPlayTime(clamped);
  }, []);

  useEffect(() => {
    if (!playing) {
      if (rafRef.current !== null) {
        cancelAnimationFrame(rafRef.current);
        rafRef.current = null;
      }
      return;
    }
    playingRef.current = true;
    lastNowRef.current = null;

    const tick = (now: number) => {
      if (lastNowRef.current !== null) {
        const dt = (now - lastNowRef.current) * speedRef.current;
        const next = Math.min(timeRef.current + dt, durationRef.current);
        if (next >= durationRef.current) {
          timeRef.current = durationRef.current;
          setPlayTime(durationRef.current);
          playingRef.current = false;
          setPlaying(false);
          return; // reached the end — stop the loop
        }
        timeRef.current = next;
        setPlayTime(next);
      }
      lastNowRef.current = now;
      rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);

    return () => {
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    };
  }, [playing]);

  const toggle = useCallback(() => {
    if (playingRef.current) {
      playingRef.current = false;
      setPlaying(false);
    } else {
      playingRef.current = true;
      setPlaying(true);
    }
  }, []);

  const pause = useCallback(() => {
    playingRef.current = false;
    setPlaying(false);
  }, []);

  const setSpeed = useCallback((s: number) => {
    speedRef.current = s;
    setSpeedState(s);
  }, []);

  const seekTo = useCallback(
    (tMs: number) => {
      setTime(tMs);
    },
    [setTime],
  );

  const restart = useCallback(() => {
    pause();
    setTime(0);
  }, [pause, setTime]);

  return { playTime, playing, speed, toggle, pause, setSpeed, seekTo, restart };
}
