# 대시보드 브라우저 로컬 파일 접근 (dashboard-browser-file-access)

## Concern
대시보드에서 사용자가 로컬 파일을 읽고 쓸 때 **브라우저가 파일을 직접 다루는 방식**을 무엇으로 할 것인가? (F-11 — "서버에 저장한다는 개념은 부적절", 서버-FS 샌드박스 탈피)

## Status
approved

## Context
- **F-11 사용자 방향 전환 (2026-08-12):** "서버에 저장한다는 개념은 부적절" — 브라우저가 로컬 파일을 직접 읽기/쓰기. 서버는 파일 **내용(문자열)**만 수신해 검증·실행 (검증·실행은 v1 코어가 있는 서버에서만 가능).
- 기존 설계(ASR-017, direct-input): 서버-FS 샌드박스 — `--root`(기본 CWD) 제한 + 서버 REST 파일 API(`GET/POST /api/files*`) + realpath 검증. **이번 방향으로 대체**.
- 브라우저 제약: 파일을 직접 다루는 표준 API는 두 계열 — (a) File System Access API(`showOpenFilePicker`/`showSaveFilePicker`/`showDirectoryPicker`), (b) `<input type=file>` + Blob 다운로드. FS Access API는 **Chrome/Edge 전용** (Firefox/Safari 미지원, 2026-08-12 현재).
- PRD v2 "편집·파일 관리": "프로젝트 내 YAML 파일 목록·열기·새로 만들기·편집·**로컬 저장 (파일시스템 직접 읽기/쓰기)**". "파일 목록" 기능의 브라우저 측 대응이 파생 질문.
- 실행·검증 경로: `POST /api/run`·`POST /api/validate`는 이미 YAML **문자열**을 받는 설계 (dashboard-run-path) — 파일 API만 브라우저 측으로 이동하면 됨.

## Decision
**Option C — 하이브리드 (FS Access 우선 + 업로드/다운로드 폴백)** (2026-08-12 사용자 승인 "오케이"): Chrome/Edge는 File System Access API로 로컬 파일을 직접 읽고 같은 파일에 저장, Firefox/Safari는 업로드(`<input type=file>`)·다운로드(Blob) 폴백. 서버 파일 API(`/api/files*`)와 `--root` 샌드박스는 제거 — 서버는 `validate`/`run`/`load-log`(문자열 입력)만 보유.

## Options
### Option A — File System Access API 전용 (Chrome/Edge)
- 브라우저가 `showOpenFilePicker`/`showSaveFilePicker`(또는 디렉터리 핸들)로 실제 로컬 파일을 직접 읽고 **같은 파일에 저장**. `POST /api/files*` 불필요.
- Pro: 진짜 "로컬 저장" UX (덮어쓰기 포함), 서버 파일 API·샌드박스·`--root` 전부 제거 가능, 경로 이탈 보안 문제 소멸
- Con: **Chrome/Edge 전용** — Firefox/Safari에서 대시보드 파일 기능 미동작 (또는 별도 폴백 필수), 파일 목록은 디렉터리 핸들 권한에 의존

### Option B — 업로드/다운로드 방식 (범용)
- 읽기: `<input type="file">` (로컬 파일 선택 → 내용 문자열로 서버 전달). 저장: 서버가 생성한 텍스트를 **Blob 다운로드**(브라우저 다운로드 폴더)로 반환.
- Pro: **모든 주요 브라우저** 동작, 구현 단순, 추가 권한 프롬프트 없음
- Con: "저장"이 원래 파일 덮어쓰기가 아니라 **다운로드 파일 생성** — "로컬 저장" 의미 퇴색, 파일 목록/새 파일 위치 관리가 브라우저 다운로드 폴더에 의존, 서버는 파일을 저장하지 않으므로 "최근 파일"은 브라우저 로컬스토리지에 별도 관리

### Option C — 하이브리드 (FS Access 우선 + 업로드/다운로드 폴백)
- FS Access API 지원 브라우저(Chrome/Edge): Option A의 직접 읽기/같은 파일 저장. 미지원 브라우저(Firefox/Safari): Option B의 업로드/다운로드.
- Pro: 현대 브라우저에서 최상 UX + 범용 브라우저 지원 유지, 서버 파일 API 제거 가능
- Con: 두 경로 구현·테스트 (기능 분기), 파일 목록 UX가 브라우저별 상이 (디렉터리 핸들 vs 없음)

## Tradeoffs
| 차원 | A (FS Access 전용) | B (업로드/다운로드) | C (하이브리드) |
|------|--------------------|--------------------|----------------|
| "로컬 저장" UX 충실도 | ★★★★★ (같은 파일 저장) | ★★ (다운로드) | ★★★★★ (지원 시) |
| 브라우저 범용성 | ★★ (Chrome/Edge) | ★★★★★ | ★★★★ |
| 서버 파일 API 제거 | ★★★★★ | ★★★★★ | ★★★★★ |
| 구현·테스트 비용 | ★★★★ | ★★★★★ | ★★ (2배) |
| 파일 목록 기능 | ★★★★ (디렉터리 핸들) | ★ (없음) | ★★★ |

## Recommendation
- **Option C (하이브리드)** 권장. 목표 사용자(차량 SW 개발자)는 Chrome 기반이 대부분이므로 주요 경험은 FS Access API의 "같은 파일 저장"으로 제공하되, Firefox/Safari 사용자가 완전히 배제되지 않도록 업로드/다운로드 폴백 유지. 서버 파일 API(`/api/files*`)는 **제거**하고 `--root` 샌드박스도 제거 — 파일 경계가 브라우저 권한으로 대체됨.

## Consequences
- `spec/sdv-sim-v2.md` 파일시스템 보안 절(ASR-017)·파일 API 절 전면 개편 — 서버는 `validate`/`run`/`load-log`(문자열 입력)만 보유
- `--root` 옵션 제거(또는 비권장 처리), 서버 파일 목록/열기/저장/새로 만들기 API 제거
- load-log 경로: 브라우저가 JSON 파일을 읽어 **내용 문자열**을 `POST /api/load-log`로 전송 — `{path}` 대신 `{content}` (또는 `{name, content}`)
- PRD "파일 목록" 항목: 브라우저 측 최근 파일(IndexedDB/localStorage) 또는 디렉터리 핸들 목록으로 재해석
- ASR-017은 "브라우저 파일 권한 경계"로 재정의 (파일 삭제·이름 변경은 여전히 미지원)

## Related ASRs
- ASR-017 — 파일시스템 접근·보안 경계 — 서버 샌드박스 → **브라우저 파일 권한 경계**로 재정의
- ASR-015 — 데이터 흐름·리플레이 — load-log 경로 입력 방식 변경
- ASR-019 — 패키지 통합·서버 명령 (serve) — `--root` 옵션 제거 영향

## Downstream Concerns
- [ ] **최근 파일/프로젝트 개념**: 브라우저 측 파일 목록을 "최근 파일"로 제공할지, 디렉터리 핸들 기반 프로젝트로 제공할지 — spec 인코딩 필요
- [ ] **파일 API 응답 형태**: 제거되는 파일 API를 대체할 브라우저-서버 인터페이스(문자열 POST)의 응답·오류 스키마 — spec 인코딩
- [ ] **저장 후 동기화**: 브라우저가 파일을 저장한 뒤 서버 세션/검증 상태와 동기화 방식 — session-lifecycle ADR과 정합

## Related
- `adr/core-yaml-string-input.md` — 동반 ADR (F-11의 서버 측 — YAML 문자열 입력 API)
- `adr/dashboard-run-path.md` — run 경로 (문자열 입력 전환)
- `spec/sdv-sim-v2.md` — 파일 API·보안 절 수정 대상 (spec-writing)
- `spec/PRD.md` — "로컬 저장"·"파일 목록" 재해석 대상

## Tags
`dashboard`, `browser`, `file-access`, `fs-access-api`, `local-storage`, `f-11`

## Approved
- 2026-08-12: Option C (하이브리드 — FS Access API 우선 + 업로드/다운로드 폴백), user confirmed ("오케이")
