/**
 * Dashboard shell (T-016 scaffold + T-018 editor wiring).
 *
 * Owns the editor state (architecture + scenario file slots), the debounced
 * server validation hooks, and the *last valid* architecture for the diagram
 * (spec: 오류 시 마지막 유효 상태를 유지). Save/run force a synchronous
 * validation and are refused on failure (spec: 저장/실행 시 강제 검증).
 */

import { useCallback, useEffect, useRef, useState } from "react";

import { useI18n } from "./i18n";
import type { MessageKey } from "./i18n/messages";
import useHashRoute, { navigate } from "./router";
import type { Route } from "./router";
import type { Lang } from "./i18n/messages";
import { StructureView } from "./StructureView";
import { parseArchitecture } from "./yaml";
import { EditorPane } from "./EditorPane";
import { useValidation } from "./useValidation";
import {
  addRecentFile,
  architectureTemplate,
  listRecentFiles,
  makeEditorFile,
  openLocalFile,
  saveLocalFile,
  scenarioTemplate,
  suggestFileName,
} from "./fileManager";
import type { EditorFile, FileKind, RecentFileEntry } from "./fileManager";
import { apiRun } from "./api/client";
import { ReplayView } from "./replay/ReplayView";
import { ReportView } from "./ReportView";
import type { Architecture, SessionMeta } from "./types/schema";
import "./styles.css";

function LangSwitch() {
  const { lang, setLang } = useI18n();
  const options: Lang[] = ["ko", "en"];
  return (
    <div className="lang-switch" role="group" aria-label="language">
      {options.map((opt) => (
        <button
          key={opt}
          type="button"
          className={lang === opt ? "lang-btn active" : "lang-btn"}
          onClick={() => setLang(opt)}
        >
          {opt === "ko" ? "한국어" : "English"}
        </button>
      ))}
    </div>
  );
}

const NAV_ITEMS: Array<{ route: Route; label: MessageKey }> = [
  { route: "editor", label: "nav.editor" },
  { route: "replay", label: "nav.replay" },
  { route: "report", label: "nav.report" },
];

interface Flash {
  key: MessageKey;
  tone: "ok" | "error";
  params?: Record<string, string | number>;
}

function App() {
  const { t } = useI18n();
  const route = useHashRoute();

  // Editor state: both slots start seeded with the basic sample templates
  // (T-023, user request 2026-08-13) so a first-time user can just press
  // "run" without creating files. Scenario can be closed (null) afterwards.
  const [archFile, setArchFile] = useState<EditorFile>(() =>
    makeEditorFile(suggestFileName("architecture"), architectureTemplate()),
  );
  const [scenFile, setScenFile] = useState<EditorFile | null>(() =>
    makeEditorFile(suggestFileName("scenario"), scenarioTemplate()),
  );
  const [activeKind, setActiveKind] = useState<FileKind>("architecture");
  const [recent, setRecent] = useState<RecentFileEntry[]>([]);

  // Diagram state: last valid architecture (spec — keep on error).
  const [structureArch, setStructureArch] = useState<Architecture | null>(null);
  // Last valid architecture content, used for scenario reference validation.
  const [validArchContent, setValidArchContent] = useState<string | undefined>(undefined);
  // Server session summary (set by run/load-log). Cleared on file open/new
  // (M-4: 파일 열기/새로 만들기 시 세션 리셋) but kept on edit (M-4: 편집
  // 시작 시 세션 무효화 — the replay view then shows the "invalidated" notice).
  const [sessionMeta, setSessionMeta] = useState<SessionMeta | null>(null);

  const [flash, setFlash] = useState<Flash | null>(null);
  const flashTimer = useRef<number | null>(null);

  const archValidation = useValidation(archFile.kind, archFile.content);
  const scenValidation = useValidation(
    "scenario",
    scenFile?.content ?? "",
    archValidation.status === "valid" ? validArchContent : undefined,
  );

  const showFlash = useCallback((key: MessageKey, tone: Flash["tone"]) => {
    if (flashTimer.current !== null) window.clearTimeout(flashTimer.current);
    setFlash({ key, tone });
    flashTimer.current = window.setTimeout(() => setFlash(null), 4000);
  }, []);

  const refreshRecent = useCallback(() => {
    void listRecentFiles().then(setRecent);
  }, []);

  useEffect(() => {
    void refreshRecent();
  }, [refreshRecent]);

  // Keep the diagram on the last valid architecture; supply valid arch
  // content for scenario reference validation (F-4).
  useEffect(() => {
    if (archValidation.status === "valid") {
      const parsed = parseArchitecture(archFile.content);
      if (parsed) {
        setStructureArch(parsed);
        setValidArchContent(archFile.content);
      }
    }
  }, [archValidation.status, archFile.content]);

  // ------------------------------------------------------------- actions

  const handleEdit = useCallback(
    (kind: FileKind, content: string) => {
      if (kind === "scenario") {
        setScenFile((prev) => (prev ? { ...prev, content, dirty: true } : prev));
      } else {
        setArchFile((prev) => ({ ...prev, content, dirty: true }));
      }
      // M-4 (T-024): editing starts invalidates the session — frontend-local
      // flag; replay/report show "invalidated" without server involvement.
      setSessionMeta((prev) => (prev ? { ...prev, invalidated: true } : prev));
    },
    [],
  );

  const handleNewFile = useCallback((kind: FileKind) => {
    const file = makeEditorFile(
      suggestFileName(kind),
      kind === "architecture" ? architectureTemplate() : scenarioTemplate(),
    );
    setActiveKind(kind);
    if (kind === "scenario") setScenFile(file);
    else setArchFile(file);
    // M-4: 새로 만들기 시 세션 리셋
    setSessionMeta(null);
  }, []);

  const handleOpenFile = useCallback(
    async (_kind: FileKind) => {
      // The toolbar passes the active tab kind, but the opened file decides
      // its own slot (kind is inferred from name/content by makeEditorFile).
      const opened = await openLocalFile();
      if (!opened) return; // user cancelled
      setActiveKind(opened.kind);
      if (opened.kind === "scenario") setScenFile(opened);
      else setArchFile(opened);
      void addRecentFile(opened).then(refreshRecent);
      // M-4: 파일 열기 시 세션 리셋
      setSessionMeta(null);
    },
    [refreshRecent],
  );

  const handleOpenRecent = useCallback((entry: RecentFileEntry) => {
    const file = makeEditorFile(entry.name, entry.content, null);
    file.id = entry.id; // keep the stable id so the recent list stays consistent
    setActiveKind(entry.kind);
    if (entry.kind === "scenario") setScenFile(file);
    else setArchFile(file);
    // M-4: 파일 열기 시 세션 리셋
    setSessionMeta(null);
  }, []);

  const handleCloseScenario = useCallback(() => {
    setScenFile(null);
    setActiveKind("architecture");
    // M-4: 슬롯 닫기 = 열린 파일 구성 변경 → 세션 리셋
    setSessionMeta(null);
  }, []);

  const handleSave = useCallback(async () => {
    const target = activeKind === "scenario" ? scenFile : archFile;
    if (!target) return;
    const ok =
      activeKind === "scenario"
        ? await scenValidation.forceValidate()
        : await archValidation.forceValidate();
    if (!ok) {
      showFlash("editor.saveBlocked", "error");
      return;
    }
    const saved = await saveLocalFile(target);
    if (!saved) {
      showFlash("editor.saveFailed", "error");
      return;
    }
    if (activeKind === "scenario") setScenFile(saved);
    else setArchFile(saved);
    void addRecentFile(saved).then(refreshRecent);
    showFlash("editor.saved", "ok");
  }, [activeKind, scenFile, archFile, archValidation, scenValidation, showFlash, refreshRecent]);

  const handleRun = useCallback(async () => {
    if (!scenFile) {
      showFlash("editor.noScenario", "error");
      return;
    }
    const okArch = await archValidation.forceValidate();
    const okScen = await scenValidation.forceValidate();
    if (!okArch || !okScen) {
      showFlash("editor.runBlocked", "error");
      return;
    }
    const res = await apiRun(archFile.content, scenFile.content);
    if (!res.ok) {
      showFlash("editor.runFailed", "error");
      return;
    }
    setSessionMeta({
      duration_ms: res.data.duration_ms,
      source: "run",
      logWithArch: false,
      invalidated: false,
    });
    showFlash("editor.runDone", "ok");
    navigate("replay");
  }, [archFile, scenFile, archValidation, scenValidation, showFlash]);

  // --------------------------------------------------------------- render

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-title">
          <h1>{t("app.title")}</h1>
          <p className="app-tagline">{t("app.tagline")}</p>
        </div>
        <LangSwitch />
      </header>

      <nav className="app-nav" aria-label="views">
        {NAV_ITEMS.map(({ route: r, label }) => (
          <button
            key={r}
            type="button"
            className={route === r ? "nav-btn active" : "nav-btn"}
            onClick={() => navigate(r)}
          >
            {t(label)}
          </button>
        ))}
      </nav>

      {flash && (
        <div className={`flash ${flash.tone}`} role="status">
          {t(flash.key, flash.params)}
        </div>
      )}

      <main className="app-main">
        {route === "editor" && (
          <section className="view-editor" data-view="editor">
            <div className="editor-structure">
              <EditorPane
                archFile={archFile}
                scenFile={scenFile}
                activeKind={activeKind}
                archValidation={archValidation}
                scenValidation={scenFile ? scenValidation : null}
                recent={recent}
                onSwitchTab={setActiveKind}
                onEdit={handleEdit}
                onNewFile={handleNewFile}
                onOpenFile={handleOpenFile}
                onOpenRecent={handleOpenRecent}
                onCloseScenario={handleCloseScenario}
                onSave={handleSave}
                onRun={handleRun}
              />
            </div>
            <div className="editor-diagram">
              {structureArch ? (
                <StructureView architecture={structureArch} />
              ) : (
                <div className="structure-empty">{t("view.structureEmpty")}</div>
              )}
            </div>
          </section>
        )}
        {route === "replay" && (
          <ReplayView
            arch={structureArch}
            archContent={validArchContent}
            sessionMeta={sessionMeta}
            onSessionChange={setSessionMeta}
          />
        )}
        {route === "report" && (
          <ReportView
            derived={sessionMeta?.source === "log" && !sessionMeta.logWithArch}
            sessionMeta={sessionMeta}
          />
        )}
      </main>
    </div>
  );
}

export default App;
