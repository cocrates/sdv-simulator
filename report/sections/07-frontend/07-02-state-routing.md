# 7.2 상태 관리·라우팅

프런트엔드는 전역 상태를 하나의 트리로 관리한다.

## 전역 상태 (App.tsx)

| 상태 | 내용 | 수명 |
|------|------|------|
| `archFile`, `scenarioFile` | 편집 중인 두 YAML **EditorFile** `{name, content, saved}` | 세션 |
| `session` | 서버 세션 메타 `{events_count, duration_ms, result, createdAt}` | 세션 |
| `invalidated` | 세션 무효화 플래그 — 현재 편집 내용이 실행 결과와 다름을 표시 (T-024, 6.4절) | 세션 |
| `recentFiles` | 최근 연 파일 목록 (IndexedDB, 최대 20개) | 영속 (7.5절) |
| `lang` | UI 언어 (7.7절) | 영속 |

- **EditorFile**: 파일 내용이 항상 상태에 있으므로, 저장되지 않은 편집은 서버와 무관하게
  브라우저 안에서만 존재한다.
- **invalidated**: `archFile`/`scenarioFile`이 수정되면 `true`가 되고, `run`/`load-log` 성공 시
  `false`로 돌아온다. 리플레이/리포트 진입 시 `invalidated`면 재실행을 안내한다.
  서버가 세션을 강제로 무효화하지 않는 대신, 브라우저가 "표시 중인 결과 = 현재 입력"을 보장한다.

## 라우팅 (hash)

- `#/editor` — 편집·구조 뷰·실행 (기본)
- `#/replay` — 리플레이 뷰 (7.4절)
- `#/report` — 리포트 패널

라우팅은 해시 기반이라 서버 정적 서빙에 추가 경로 규칙이 필요 없다 — SPA가
단일 `index.html`에서 동작한다. 브라우저 새로고침 시에도 해시로 상태를 복원한다.
