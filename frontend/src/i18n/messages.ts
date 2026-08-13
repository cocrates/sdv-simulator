/**
 * i18n message catalogs (ASR-020): every UI string comes from this catalog —
 * hardcoded strings are prohibited. Extend the `MessageKey` union and both
 * catalogs together when adding UI text.
 */

export type Lang = "ko" | "en";

/** All UI message keys. Add new keys here and in both catalogs below. */
export type MessageKey =
  | "app.title"
  | "app.tagline"
  | "lang.label"
  | "nav.editor"
  | "nav.replay"
  | "nav.report"
  | "status.ready"
  | "status.loading"
  | "status.noSession"
  | "status.sessionInvalid"
  | "status.serverOffline"
  | "view.editorPlaceholder"
  | "view.replayPlaceholder"
  | "view.reportPlaceholder"
  | "view.structureEmpty"
  | "common.openFile"
  | "common.newFile"
  | "common.save"
  | "common.run"
  | "common.cancel"
  | "common.close"
  | "editor.kind.architecture"
  | "editor.kind.scenario"
  | "editor.new.architecture"
  | "editor.new.scenario"
  | "editor.recentFiles"
  | "editor.noRecentFiles"
  | "editor.noFiles"
  | "editor.emptyScenario"
  | "editor.dirty"
  | "editor.idle"
  | "editor.validating"
  | "editor.valid"
  | "editor.invalid"
  | "editor.offline"
  | "editor.errorsCount"
  | "editor.saveBlocked"
  | "editor.saveFailed"
  | "editor.saved"
  | "editor.runBlocked"
  | "editor.runFailed"
  | "editor.runDone"
  | "editor.noScenario"
  | "editor.openFailed"
  | "replay.play"
  | "replay.pause"
  | "replay.restart"
  | "replay.timeline"
  | "replay.speed"
  | "replay.loadLog"
  | "replay.noStructure"
  | "replay.filters"
  | "replay.entityFilter"
  | "replay.clearFilter"
  | "replay.approximate"
  | "event.time"
  | "event.typeLabel"
  | "event.entity"
  | "event.empty"
  | "event.type.tx"
  | "event.type.rx"
  | "event.type.task"
  | "event.type.drop"
  | "event.type.overrun"
  | "event.type.log"
  | "report.simulation"
  | "report.duration"
  | "report.result"
  | "report.eventCount"
  | "report.links"
  | "report.tasks"
  | "report.assertions"
  | "report.warnings"
  | "report.name"
  | "report.kind"
  | "report.txCount"
  | "report.rxCount"
  | "report.dropCount"
  | "report.supersedeCount"
  | "report.busLoad"
  | "report.node"
  | "report.task"
  | "report.period"
  | "report.runCount"
  | "report.overrunCount"
  | "report.status"
  | "report.detail"
  | "report.pass"
  | "report.fail"
  | "report.none";

type Catalog = Record<MessageKey, string>;

const ko: Catalog = {
  "app.title": "SDV 시뮬레이터",
  "app.tagline": "소프트웨어 정의 차량 E/E 아키텍처 시뮬레이션 대시보드",
  "lang.label": "언어",
  "nav.editor": "편집기",
  "nav.replay": "리플레이",
  "nav.report": "리포트",
  "status.ready": "준비됨",
  "status.loading": "로딩 중…",
  "status.noSession": "아직 실행된 시뮬레이션이 없습니다. 편집기에서 [실행]을 눌러주세요.",
  "status.sessionInvalid": "정의 변경으로 리플레이가 무효화되었습니다. 다시 실행하세요.",
  "status.serverOffline": "서버에 연결할 수 없습니다.",
  "view.editorPlaceholder": "편집기 뷰가 여기에 렌더링됩니다.",
  "view.replayPlaceholder": "리플레이 뷰가 여기에 렌더링됩니다.",
  "view.reportPlaceholder": "리포트 뷰가 여기에 렌더링됩니다.",
  "view.structureEmpty": "구조를 표시할 아키텍처가 없습니다.",
  "common.openFile": "파일 열기",
  "common.newFile": "새 파일",
  "common.save": "저장",
  "common.run": "실행",
  "common.cancel": "취소",
  "common.close": "닫기",
  "editor.kind.architecture": "아키텍처",
  "editor.kind.scenario": "시나리오",
  "editor.new.architecture": "새 아키텍처",
  "editor.new.scenario": "새 시나리오",
  "editor.recentFiles": "최근 파일",
  "editor.noRecentFiles": "최근 파일 없음",
  "editor.noFiles": "열린 파일이 없습니다.",
  "editor.emptyScenario": "새 시나리오 또는 파일 열기로 시나리오를 추가하세요.",
  "editor.dirty": "저장되지 않음",
  "editor.idle": "대기",
  "editor.validating": "검증 중…",
  "editor.valid": "유효",
  "editor.invalid": "오류",
  "editor.offline": "서버 연결 없음",
  "editor.errorsCount": "오류 {n}건",
  "editor.saveBlocked": "검증 실패로 저장할 수 없습니다.",
  "editor.saveFailed": "저장하지 못했습니다.",
  "editor.saved": "저장됨",
  "editor.runBlocked": "검증 실패로 실행할 수 없습니다.",
  "editor.runFailed": "실행 실패",
  "editor.runDone": "실행 완료 — 리플레이로 이동",
  "editor.noScenario": "실행하려면 시나리오 파일이 필요합니다.",
  "editor.openFailed": "파일을 열 수 없습니다.",
  "replay.play": "재생",
  "replay.pause": "일시정지",
  "replay.restart": "처음",
  "replay.timeline": "타임라인",
  "replay.speed": "배속",
  "replay.loadLog": "로그 파일 열기",
  "replay.noStructure": "표시할 아키텍처가 없습니다.",
  "replay.filters": "필터",
  "replay.entityFilter": "{name} 이벤트만 보기",
  "replay.clearFilter": "필터 해제",
  "replay.approximate": "≈ 근사 표시",
  "event.time": "시간",
  "event.typeLabel": "유형",
  "event.entity": "엔티티",
  "event.empty": "표시할 이벤트가 없습니다.",
  "event.type.tx": "tx",
  "event.type.rx": "rx",
  "event.type.task": "task",
  "event.type.drop": "drop",
  "event.type.overrun": "overrun",
  "event.type.log": "log",
  "report.simulation": "시뮬레이션",
  "report.duration": "지속 시간",
  "report.result": "결과",
  "report.eventCount": "이벤트 수",
  "report.links": "링크",
  "report.tasks": "태스크",
  "report.assertions": "Assertion",
  "report.warnings": "경고",
  "report.name": "이름",
  "report.kind": "종류",
  "report.txCount": "tx",
  "report.rxCount": "rx",
  "report.dropCount": "drop",
  "report.supersedeCount": "supersede",
  "report.busLoad": "버스 부하",
  "report.node": "노드",
  "report.task": "태스크",
  "report.period": "주기(ms)",
  "report.runCount": "실행 횟수",
  "report.overrunCount": "오버런",
  "report.status": "상태",
  "report.detail": "상세",
  "report.pass": "통과",
  "report.fail": "실패",
  "report.none": "없음",
};

const en: Catalog = {
  "app.title": "SDV Simulator",
  "app.tagline": "Software Defined Vehicle E/E architecture simulation dashboard",
  "lang.label": "Language",
  "nav.editor": "Editor",
  "nav.replay": "Replay",
  "nav.report": "Report",
  "status.ready": "Ready",
  "status.loading": "Loading…",
  "status.noSession": "No simulation has been run yet. Press Run in the editor.",
  "status.sessionInvalid": "Definition changed; the replay is invalidated. Run again.",
  "status.serverOffline": "Cannot reach the server.",
  "view.editorPlaceholder": "Editor view renders here.",
  "view.replayPlaceholder": "Replay view renders here.",
  "view.reportPlaceholder": "Report view renders here.",
  "view.structureEmpty": "No architecture to display.",
  "common.openFile": "Open file",
  "common.newFile": "New file",
  "common.save": "Save",
  "common.run": "Run",
  "common.cancel": "Cancel",
  "common.close": "Close",
  "editor.kind.architecture": "Architecture",
  "editor.kind.scenario": "Scenario",
  "editor.new.architecture": "New architecture",
  "editor.new.scenario": "New scenario",
  "editor.recentFiles": "Recent files",
  "editor.noRecentFiles": "No recent files",
  "editor.noFiles": "No open files.",
  "editor.emptyScenario": "Add a scenario via New scenario or Open file.",
  "editor.dirty": "Unsaved",
  "editor.idle": "Idle",
  "editor.validating": "Validating…",
  "editor.valid": "Valid",
  "editor.invalid": "Invalid",
  "editor.offline": "Server offline",
  "editor.errorsCount": "{n} errors",
  "editor.saveBlocked": "Cannot save — validation failed.",
  "editor.saveFailed": "Save failed.",
  "editor.saved": "Saved",
  "editor.runBlocked": "Cannot run — validation failed.",
  "editor.runFailed": "Run failed",
  "editor.runDone": "Run complete — opening replay",
  "editor.noScenario": "A scenario file is required to run.",
  "editor.openFailed": "Cannot open file.",
  "replay.play": "Play",
  "replay.pause": "Pause",
  "replay.restart": "Restart",
  "replay.timeline": "Timeline",
  "replay.speed": "Speed",
  "replay.loadLog": "Load log",
  "replay.noStructure": "No architecture to display.",
  "replay.filters": "Filters",
  "replay.entityFilter": "Showing only {name} events",
  "replay.clearFilter": "Clear filter",
  "replay.approximate": "≈ approximate",
  "event.time": "Time",
  "event.typeLabel": "Type",
  "event.entity": "Entity",
  "event.empty": "No events to show.",
  "event.type.tx": "tx",
  "event.type.rx": "rx",
  "event.type.task": "task",
  "event.type.drop": "drop",
  "event.type.overrun": "overrun",
  "event.type.log": "log",
  "report.simulation": "Simulation",
  "report.duration": "Duration",
  "report.result": "Result",
  "report.eventCount": "Event count",
  "report.links": "Links",
  "report.tasks": "Tasks",
  "report.assertions": "Assertions",
  "report.warnings": "Warnings",
  "report.name": "Name",
  "report.kind": "Kind",
  "report.txCount": "Tx",
  "report.rxCount": "Rx",
  "report.dropCount": "Drops",
  "report.supersedeCount": "Superseded",
  "report.busLoad": "Bus load",
  "report.node": "Node",
  "report.task": "Task",
  "report.period": "Period (ms)",
  "report.runCount": "Runs",
  "report.overrunCount": "Overruns",
  "report.status": "Status",
  "report.detail": "Detail",
  "report.pass": "Pass",
  "report.fail": "Fail",
  "report.none": "None",
};

export const catalogs: Record<Lang, Catalog> = { ko, en };

/**
 * Language resolution (ASR-020). Precedence:
 *   1. user's explicit switch choice (localStorage) — the spec requires a UI
 *      switch, so an explicit user choice wins over everything;
 *   2. server-provided language (`serve --lang` > `SDV_SIM_LANG` env, injected
 *      into the served index.html as `window.__SDV_SIM_LANG__`; T-020 wires
 *      the injection on the server side);
 *   3. browser locale (ko/en only, otherwise ko).
 */
export function resolveInitialLang(): Lang {
  const stored = localStorage.getItem("sdv-sim.lang");
  if (stored === "ko" || stored === "en") return stored;

  const injected = (window as unknown as { __SDV_SIM_LANG__?: string }).__SDV_SIM_LANG__;
  if (injected === "ko" || injected === "en") return injected;

  const nav = navigator.language.toLowerCase();
  if (nav.startsWith("ko")) return "ko";
  if (nav.startsWith("en")) return "en";
  return "ko";
}

export function persistLang(lang: Lang): void {
  localStorage.setItem("sdv-sim.lang", lang);
}
