/**
 * Browser-side local file management (F-11 / dashboard-browser-file-access
 * Option C): File System Access API for Chrome/Edge (same-file save), upload +
 * Blob download fallback for Firefox/Safari, plus IndexedDB "recent files".
 * The server never touches the filesystem — it only receives content strings
 * (ASR-017); the browser permission prompt is the file boundary.
 *
 * The pure helpers (kind inference, templates, names) are free of browser
 * globals so `scripts/check-files.ts` can exercise them under plain Node.
 */

export type FileKind = "architecture" | "scenario";

export interface EditorFile {
  /** Stable id for tabs/recent entries (not the file name). */
  id: string;
  name: string;
  kind: FileKind;
  content: string;
  dirty: boolean;
  /** FS Access API handle — enables same-file save in Chrome/Edge (null in
   * fallback browsers). */
  handle: FileSystemFileHandle | null;
}

export interface RecentFileEntry {
  id: string;
  name: string;
  kind: FileKind;
  content: string;
  updatedAt: number;
}

// --------------------------------------------------------------- templates

/**
 * Architecture skeleton with the v1 schema's minimum required fields
 * (spec/sdv-sim-v1.md): nodes with components, links with frames, gateways.
 * Mirrors `samples/basic/architecture.yaml` (schema-validated by tests) so a
 * new file is immediately runnable.
 */
export function architectureTemplate(): string {
  return `\
schema_version: 1

# E/E architecture: nodes (ECU/HPC), links (CAN/Ethernet), gateways.
nodes:
  - name: body_ecu
    type: ECU
    components:
      - name: body_ctrl
        sends: [door_cmd]
        receives: [door_state]
        tasks:
          - name: main
            period_ms: 10
            priority: 1
            wcet_ms: 1
  - name: door_ecu
    type: ECU
    components:
      - name: door_act
        receives: [door_cmd]

links:
  - name: can1
    kind: can
    bitrate: 500
    nodes: [body_ecu, door_ecu]
    frames:
      - name: door_cmd
        id: 0x100
        dlc: 4
        period_ms: 10
        source: body_ecu
      - name: door_state
        id: 0x101
        dlc: 4
        period_ms: 10
        source: door_ecu

gateways: []
`;
}

/**
 * Scenario template mirroring `samples/basic/scenario.yaml` (schema-validated
 * by v1 tests): one injected message + five assertions, so a brand-new
 * editor session is immediately runnable — a first-time user can just press
 * "run" and watch the replay (T-023, user request 2026-08-13).
 */
export function scenarioTemplate(): string {
  return `\
# 기본 샘플 시나리오 — 문 제어 100ms 주행
#
# - t=5에 door_cmd 주입 (data 포함, tx 이벤트로 기록)
# - assertion 5건: tx / rx / task 이벤트, at_ms + count(≥) 검증
#
# 실행: [실행] 버튼 → 구조 뷰에서 리플레이
# 결과: pass (assertion 5건 모두 통과)

schema_version: 1
duration_ms: 100

messages:
  - { t_ms: 5, link: can1, frame: door_cmd, data: { state: open } }

assertions:
  # door_cmd tx: 주기 11건(t=0,10,...,100) + 주입 1건(t=5) = 12건, 첫 전송 t=0
  - name: cmd_sent
    expect: { event: tx, frame: door_cmd, link: can1, at_ms: 0, count: 12 }

  # door_cmd rx: tx 완료(+1ms) 후 door_ecu가 수신 — 11건(t=1,6,...,96; t=101은 범위 밖)
  - name: cmd_received
    expect: { event: rx, frame: door_cmd, link: can1, node: door_ecu, at_ms: 1, count: 11 }

  # door_state tx: 같은 tick에서 door_cmd에 밀려 1ms 지연 → CAN ID 중재 관찰
  # 10건(t=1,11,...,91; t=100 시도는 종료 전 미전송)
  - name: state_arbitrated
    expect: { event: tx, frame: door_state, link: can1, at_ms: 1, count: 10 }

  # door_state rx: body_ecu의 door_ctrl이 수신 — 10건(t=2,12,...,92)
  - name: state_received
    expect: { event: rx, frame: door_state, link: can1, node: body_ecu, at_ms: 2, count: 10 }

  # task 이벤트: event: task 는 task_start + task_end 둘 다 매칭 (U-4)
  # task_start 11건(t=0..100), task_end 10건(t=1..91) → 21건 ≥ 11
  - name: task_runs
    expect: { event: task, node: body_ecu, task: main, at_ms: 0, count: 11 }
`;
}

// ---------------------------------------------------------- pure inference

/**
 * Infer the file kind from the file name first (arch/scen), then from content
 * markers. Unknown files default to architecture.
 */
export function inferFileKind(name: string, content: string): FileKind {
  const lower = name.toLowerCase();
  if (lower.includes("arch")) return "architecture";
  if (lower.includes("scen")) return "scenario";
  if (/\bnodes\s*:/.test(content) && /\blinks\s*:/.test(content)) return "architecture";
  if (/duration_ms\s*:/.test(content)) return "scenario";
  return "architecture";
}

export function suggestFileName(kind: FileKind): string {
  return kind === "architecture" ? "new_architecture.yaml" : "new_scenario.yaml";
}

/** Create an editor file from raw content (untouched on disk — not dirty). */
export function makeEditorFile(
  name: string,
  content: string,
  handle: FileSystemFileHandle | null = null,
): EditorFile {
  const id =
    typeof crypto !== "undefined" && typeof crypto.randomUUID === "function"
      ? crypto.randomUUID()
      : `f-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
  return {
    id,
    name,
    kind: inferFileKind(name, content),
    content,
    dirty: false,
    handle,
  };
}

// ------------------------------------------------------------ open / save

interface PickerType {
  description: string;
  accept: Record<string, string[]>;
}

const PICKER_TYPES: PickerType[] = [
  { description: "YAML definitions", accept: { "text/yaml": [".yaml", ".yml"] } },
  { description: "Event log JSON", accept: { "application/json": [".json"] } },
];

interface WindowWithPickers {
  showOpenFilePicker?: (opts?: unknown) => Promise<FileSystemFileHandle[]>;
  showSaveFilePicker?: (opts?: unknown) => Promise<FileSystemFileHandle>;
}

/**
 * Open a local file: File System Access API (Chrome/Edge) with an
 * `<input type=file>` fallback (Firefox/Safari). Returns null on cancel.
 */
export async function openLocalFile(): Promise<EditorFile | null> {
  const w = window as WindowWithPickers;
  if (typeof w.showOpenFilePicker === "function") {
    try {
      const [handle] = await w.showOpenFilePicker({ types: PICKER_TYPES, multiple: false });
      const file = await handle.getFile();
      return makeEditorFile(file.name, await file.text(), handle);
    } catch {
      return null; // user cancelled (AbortError) or picker failure
    }
  }
  return openViaInput();
}

/** `<input type=file>` fallback — resolves the selected file or null on cancel. */
function openViaInput(): Promise<EditorFile | null> {
  return new Promise((resolve) => {
    let done = false;
    const finish = (value: EditorFile | null) => {
      if (done) return;
      done = true;
      window.removeEventListener("focus", onFocus);
      input.remove();
      resolve(value);
    };
    // Closing the dialog without choosing does not always fire "change";
    // a subsequent window focus with no files means the user cancelled.
    const onFocus = () => {
      if (!input.files || input.files.length === 0) finish(null);
    };
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".yaml,.yml,.json";
    input.style.display = "none";
    input.addEventListener(
      "change",
      () => {
        const file = input.files?.[0];
        if (!file) {
          finish(null);
          return;
        }
        void file.text().then((content) => finish(makeEditorFile(file.name, content, null)));
      },
      { once: true },
    );
    window.addEventListener("focus", onFocus);
    document.body.appendChild(input);
    input.click();
  });
}

/** Opened v1 events.json log (not an editor slot — content only). */
export interface LogFile {
  name: string;
  content: string;
}

const LOG_PICKER_TYPES: PickerType[] = [
  { description: "Event log JSON", accept: { "application/json": [".json"] } },
];

function openLogViaInput(): Promise<LogFile | null> {
  return new Promise((resolve) => {
    let done = false;
    const finish = (value: LogFile | null) => {
      if (done) return;
      done = true;
      window.removeEventListener("focus", onFocus);
      input.remove();
      resolve(value);
    };
    const onFocus = () => {
      if (!input.files || input.files.length === 0) finish(null);
    };
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".json";
    input.style.display = "none";
    input.addEventListener(
      "change",
      () => {
        const file = input.files?.[0];
        if (!file) {
          finish(null);
          return;
        }
        void file.text().then((content) => finish({ name: file.name, content }));
      },
      { once: true },
    );
    window.addEventListener("focus", onFocus);
    document.body.appendChild(input);
    input.click();
  });
}

/**
 * Open a v1 event log JSON (replay path): File System Access API with an
 * `<input type=file>` fallback. Returns null on cancel.
 */
export async function openLogFile(): Promise<LogFile | null> {
  const w = window as WindowWithPickers;
  if (typeof w.showOpenFilePicker === "function") {
    try {
      const [handle] = await w.showOpenFilePicker({ types: LOG_PICKER_TYPES, multiple: false });
      const file = await handle.getFile();
      return { name: file.name, content: await file.text() };
    } catch {
      return null; // user cancelled (AbortError) or picker failure
    }
  }
  return openLogViaInput();
}

/**
 * Save a file: same-file write via an existing FS Access handle, save-picker
 * for a first FS Access save, Blob download as the final fallback. Returns the
 * updated (clean) file, or null when the user cancelled.
 */
export async function saveLocalFile(file: EditorFile): Promise<EditorFile | null> {
  const w = window as WindowWithPickers;
  if (file.handle) {
    try {
      await writeToHandle(file.handle, file.content);
      return { ...file, dirty: false };
    } catch {
      return null;
    }
  }
  if (typeof w.showSaveFilePicker === "function") {
    try {
      const handle = await w.showSaveFilePicker({ suggestedName: file.name, types: PICKER_TYPES });
      await writeToHandle(handle, file.content);
      return { ...file, handle, dirty: false };
    } catch {
      return null;
    }
  }
  downloadBlob(file.name, file.content);
  return { ...file, dirty: false };
}

async function writeToHandle(handle: FileSystemFileHandle, content: string): Promise<void> {
  const writable = await handle.createWritable();
  await writable.write(content);
  await writable.close();
}

function downloadBlob(name: string, content: string): void {
  const blob = new Blob([content], { type: "text/yaml;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.style.display = "none";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

// ------------------------------------------------- recent files (IndexedDB)

const DB_NAME = "sdv-sim";
const DB_VERSION = 1;
const RECENT_STORE = "recent-files";
const MAX_RECENT = 20;

function openDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION);
    req.onupgradeneeded = () => {
      if (!req.result.objectStoreNames.contains(RECENT_STORE)) {
        req.result.createObjectStore(RECENT_STORE, { keyPath: "id" });
      }
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error ?? new Error("indexedDB open failed"));
  });
}

function txDone(tx: IDBTransaction): Promise<void> {
  return new Promise((resolve, reject) => {
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error ?? new Error("indexedDB transaction failed"));
    tx.onabort = () => reject(tx.error ?? new Error("indexedDB transaction aborted"));
  });
}

/** Recent YAML files, newest first (spec: browser-side recent list, not a
 * directory listing). */
export async function listRecentFiles(): Promise<RecentFileEntry[]> {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(RECENT_STORE, "readonly");
    const req = tx.objectStore(RECENT_STORE).getAll();
    req.onsuccess = () => {
      const all = (req.result as RecentFileEntry[]).slice().sort((a, b) => b.updatedAt - a.updatedAt);
      resolve(all);
    };
    req.onerror = () => reject(req.error ?? new Error("recent list failed"));
  });
}

export async function addRecentFile(file: EditorFile): Promise<void> {
  const db = await openDb();
  const tx = db.transaction(RECENT_STORE, "readwrite");
  const store = tx.objectStore(RECENT_STORE);
  store.put({ id: file.id, name: file.name, kind: file.kind, content: file.content, updatedAt: Date.now() });
  const allReq = store.getAll();
  allReq.onsuccess = () => {
    const all = (allReq.result as RecentFileEntry[]).sort((a, b) => b.updatedAt - a.updatedAt);
    for (const old of all.slice(MAX_RECENT)) store.delete(old.id);
  };
  await txDone(tx);
}

export async function removeRecentFile(id: string): Promise<void> {
  const db = await openDb();
  const tx = db.transaction(RECENT_STORE, "readwrite");
  tx.objectStore(RECENT_STORE).delete(id);
  await txDone(tx);
}
