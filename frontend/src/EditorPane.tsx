/**
 * YAML text editor pane (spec ASR-018 편집·파일 관리).
 *
 * - two fixed slots (architecture / scenario tabs) with open / new / save;
 * - server-side validation feedback (editor-validation-feedback Option A):
 *   line-level markers in the gutter + a clickable error list, with a status
 *   bar for validating / valid / invalid / offline;
 * - the parent owns the files and the ValidationState hooks; this component
 *   is a controlled view: content flows in via props, edits flow out via
 *   `onEdit`, and save/run are delegated (forced validation lives in App).
 */

import { useMemo, useRef, useState } from "react";

import { useI18n } from "./i18n";
import type { EditorFile, FileKind, RecentFileEntry } from "./fileManager";
import type { ValidationIssue, ValidationStatus, ValidationState } from "./useValidation";

export interface EditorPaneProps {
  archFile: EditorFile;
  scenFile: EditorFile | null;
  activeKind: FileKind;
  archValidation: ValidationState;
  scenValidation: ValidationState | null;
  recent: RecentFileEntry[];
  onSwitchTab: (kind: FileKind) => void;
  onEdit: (kind: FileKind, content: string) => void;
  onNewFile: (kind: FileKind) => void;
  onOpenFile: (kind: FileKind) => void;
  onOpenRecent: (entry: RecentFileEntry) => void;
  onCloseScenario: () => void;
  onSave: () => void;
  onRun: () => void;
}

export function EditorPane(props: EditorPaneProps) {
  const { t } = useI18n();
  const [recentOpen, setRecentOpen] = useState(false);

  const activeKind = props.activeKind;
  const activeFile = activeKind === "scenario" ? props.scenFile : props.archFile;
  const activeValidation = activeKind === "scenario" ? props.scenValidation : props.archValidation;

  return (
    <div className="editor-pane">
      <div className="editor-toolbar">
        <button type="button" className="tool-btn" onClick={() => props.onNewFile("architecture")}>
          {t("editor.new.architecture")}
        </button>
        <button type="button" className="tool-btn" onClick={() => props.onNewFile("scenario")}>
          {t("editor.new.scenario")}
        </button>
        <button type="button" className="tool-btn" onClick={() => props.onOpenFile(activeKind)}>
          {t("common.openFile")}
        </button>
        <div className="recent-wrap">
          <button type="button" className="tool-btn" onClick={() => setRecentOpen((o) => !o)}>
            {t("editor.recentFiles")} ▾
          </button>
          {recentOpen && (
            <div className="recent-menu">
              {props.recent.length === 0 ? (
                <div className="recent-empty">{t("editor.noRecentFiles")}</div>
              ) : (
                props.recent.map((entry) => (
                  <button
                    key={entry.id}
                    type="button"
                    className="recent-item"
                    onClick={() => {
                      setRecentOpen(false);
                      props.onOpenRecent(entry);
                    }}
                  >
                    <span className="recent-kind">{entry.kind === "architecture" ? "A" : "S"}</span>
                    <span className="recent-name">{entry.name}</span>
                  </button>
                ))
              )}
            </div>
          )}
        </div>
        <div className="toolbar-spacer" />
        <button type="button" className="tool-btn" onClick={props.onSave} disabled={!activeFile}>
          {t("common.save")}
        </button>
        <button type="button" className="tool-btn btn-run" onClick={props.onRun} disabled={!activeFile}>
          {t("common.run")}
        </button>
      </div>

      <div className="editor-tabs" role="tablist">
        <TabButton
          label={t("editor.kind.architecture")}
          file={props.archFile}
          active={activeKind === "architecture"}
          onSelect={() => props.onSwitchTab("architecture")}
          dirtyTitle={t("editor.dirty")}
          closeLabel={t("common.close")}
        />
        {props.scenFile ? (
          <TabButton
            label={t("editor.kind.scenario")}
            file={props.scenFile}
            active={activeKind === "scenario"}
            onSelect={() => props.onSwitchTab("scenario")}
            onClose={props.onCloseScenario}
            dirtyTitle={t("editor.dirty")}
            closeLabel={t("common.close")}
          />
        ) : (
          <button
            type="button"
            role="tab"
            aria-selected={false}
            className="editor-tab inactive"
            onClick={() => props.onSwitchTab("scenario")}
          >
            <span className="editor-tab-label">{t("editor.kind.scenario")}</span>
            <span className="editor-tab-empty">{t("editor.emptyScenario")}</span>
          </button>
        )}
      </div>

      {activeFile && activeValidation ? (
        <>
          <CodeEditor
            kind={activeFile.kind}
            content={activeFile.content}
            issues={activeValidation.issues}
            onChange={(content) => props.onEdit(activeFile.kind, content)}
          />
          <ValidationBar status={activeValidation.status} issueCount={activeValidation.issues.length} />
        </>
      ) : (
        <div className="editor-empty">
          <p>{t("editor.emptyScenario")}</p>
          <div className="editor-empty-actions">
            <button type="button" className="tool-btn" onClick={() => props.onNewFile("scenario")}>
              {t("editor.new.scenario")}
            </button>
            <button type="button" className="tool-btn" onClick={() => props.onOpenFile("scenario")}>
              {t("common.openFile")}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// ------------------------------------------------------------------- tabs

interface TabButtonProps {
  label: string;
  file: EditorFile;
  active: boolean;
  onSelect: () => void;
  onClose?: () => void;
  dirtyTitle: string;
  closeLabel: string;
}

function TabButton({ label, file, active, onSelect, onClose, dirtyTitle, closeLabel }: TabButtonProps) {
  return (
    <button
      type="button"
      role="tab"
      aria-selected={active}
      className={"editor-tab" + (active ? " active" : "") + (file.dirty ? " dirty" : "")}
      onClick={onSelect}
    >
      <span className="editor-tab-label">{label}</span>
      <span className="editor-tab-name">{file.name}</span>
      {file.dirty && (
        <span className="editor-tab-dirty" title={dirtyTitle} aria-label={dirtyTitle}>
          ●
        </span>
      )}
      {onClose && (
        <span
          className="editor-tab-close"
          role="button"
          aria-label={closeLabel}
          onClick={(e) => {
            e.stopPropagation();
            onClose();
          }}
        >
          ×
        </span>
      )}
    </button>
  );
}

// ------------------------------------------------------------ code editor

const LINE_HEIGHT = 20; // must match .editor-textarea line-height

interface CodeEditorProps {
  kind: FileKind;
  content: string;
  issues: ValidationIssue[];
  onChange: (content: string) => void;
}

function CodeEditor({ kind, content, issues, onChange }: CodeEditorProps) {
  const { t } = useI18n();
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const gutterRef = useRef<HTMLDivElement>(null);

  const lineCount = content.split("\n").length;
  const errorLines = useMemo(() => {
    const set = new Set<number>();
    for (const issue of issues) {
      if (issue.line != null && issue.line >= 1) set.add(issue.line);
    }
    return set;
  }, [issues]);

  const syncScroll = () => {
    if (gutterRef.current && textareaRef.current) {
      gutterRef.current.scrollTop = textareaRef.current.scrollTop;
    }
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Tab") {
      e.preventDefault();
      const el = e.currentTarget;
      const start = el.selectionStart;
      const end = el.selectionEnd;
      const next = el.value.slice(0, start) + "  " + el.value.slice(end);
      onChange(next);
      requestAnimationFrame(() => {
        el.selectionStart = el.selectionEnd = start + 2;
      });
    }
  };

  const gotoLine = (line: number) => {
    const el = textareaRef.current;
    if (!el) return;
    const lines = content.split("\n");
    let pos = 0;
    for (let i = 0; i < line - 1 && i < lines.length; i++) pos += lines[i].length + 1;
    el.focus();
    el.setSelectionRange(pos, pos);
    el.scrollTop = Math.max(0, (line - 1) * LINE_HEIGHT - 60);
  };

  return (
    <div className="editor-code">
      <div className="editor-code-row">
        <div className="editor-gutter" ref={gutterRef} aria-hidden="true">
          {Array.from({ length: lineCount }, (_, i) => (
            <div key={i} className={"editor-line-no" + (errorLines.has(i + 1) ? " error" : "")}>
              {i + 1}
            </div>
          ))}
        </div>
        <textarea
          ref={textareaRef}
          className="editor-textarea"
          value={content}
          spellCheck={false}
          wrap="off"
          onChange={(e) => onChange(e.target.value)}
          onScroll={syncScroll}
          onKeyDown={onKeyDown}
          aria-label={t(kind === "architecture" ? "editor.kind.architecture" : "editor.kind.scenario")}
        />
      </div>
      {issues.length > 0 && (
        <div className="editor-errors">
          {issues.map((issue, i) => (
            <button
              key={i}
              type="button"
              className="editor-error"
              onClick={() => issue.line != null && gotoLine(issue.line)}
            >
              <span className="editor-error-line">{issue.line ?? "–"}</span>
              <span className="editor-error-path">{issue.path ?? ""}</span>
              <span className="editor-error-msg">{issue.message}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// ----------------------------------------------------------- status bar

function ValidationBar({ status, issueCount }: { status: ValidationStatus; issueCount: number }) {
  const { t } = useI18n();
  const labels: Record<ValidationStatus, string> = {
    idle: t("editor.idle"),
    validating: t("editor.validating"),
    valid: t("editor.valid"),
    invalid: t("editor.invalid"),
    offline: t("editor.offline"),
  };
  return (
    <div className={`editor-status ${status}`}>
      <span className="editor-status-dot" aria-hidden="true" />
      <span className="editor-status-label">{labels[status]}</span>
      {status === "invalid" && issueCount > 0 && (
        <span className="editor-status-count">{t("editor.errorsCount", { n: issueCount })}</span>
      )}
    </div>
  );
}
