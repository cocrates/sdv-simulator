# TODO: SDV Simulator v2 (웹 대시보드)

> **Project root:** `/home/ubuntu/workspace/softwares/sdv-simulator`
> **Project type:** `software`
> **Project ID:** `software-4bfdd444-2f43-4c97-b6dd-abba9b3e9f17`
> **Updated:** 2026-08-12

## Snapshot

| Done | In progress | Pending | Blocked | Skipped |
|------|-------------|---------|---------|---------|
| 12   | 1           | 8       | 0       | 0       |

**Current focus:** T-008 in_progress — Step 5: v2 대시보드 생성 (T-013~T-015 완료)
**Recommended next:** T-016 — 프런트엔드 스캐폴딩 (Vite+React+TS, i18n ko/en, 해시 라우팅, API 클라이언트)

## Active

- [x] **T-001** `done` — Step 0/1: PRD v2 범위 갱신 (대시보드 스코프 확정)
  - Phase: Step 1 (PRD)
  - Artifact: `spec/PRD.md`
  - Depends: —
  - Notes: 2026-08-12 완료. Step 0 게이트 1 실패(PRD v1 대상) → Step 1 진입. 사용자 범위 확정: **v2 = 웹 대시보드만, OTA 미포함**. PRD v2 갱신 — 동작 방식(로컬 웹 서버, 파일 로드 겸용), 시각화 3종, 인터랙션, 제공 형태(serve 명령 — ASR/ADR 확정), 비목표·제약·성공 기준 v2 기준으로 개편.

## Backlog

- [x] **T-002** `done` — Gate: PRD v2 승인
  - Phase: Step 1 (PRD)
  - Artifact: `spec/PRD.md`
  - Depends: T-001
  - Notes: 2026-08-12 사용자 명시 승인("오케이"). 최종 범위 — 시각화 중심(구조 뷰 = 시뮬레이션 오버레이 캔버스), 편집(YAML 텍스트 + 실시간 동기화 + 스키마 검증, Option A), 로컬 저장, OTA 제외.

- [x] **T-003** `done` — Step 2: v2 ASR 식별·등록 (ASR.md에 신규 등록 + Dependency Order 갱신)
  - Phase: Step 2 (ASR)
  - Artifact: `spec/ASR.md`
  - Depends: T-002
  - Notes: 대시보드 ASR 7건 등록 완료 — ASR-014 기술 스택, ASR-015 데이터 흐름·리플레이, ASR-016 구조 뷰 렌더링·성능, ASR-017 파일시스템 보안, ASR-018 편집·검증, ASR-019 패키지 통합(serve), ASR-020 UI 언어. Dependency Order 5번 항목 기록.

- [x] **T-004** `done` — Step 3: v2 ASR 검토 (Direct Input / ADR)
  - Phase: Step 3 (ASR Review)
  - Artifact: `adr/*.md` (필요 시)
  - Depends: T-003
  - Notes: Dependency Order대로 1개씩 완료. **ASR-014** (dashboard-tech-stack — FastAPI + React/TS + Vite) / **ASR-019** (serve-packaging — 단일 프로세스 + 패키지 내부 정적 자산) / **ASR-015** (data-flow-replay — 코어 임베드 + 일괄 JSON) / **ASR-016** (topology-rendering-performance — SVG+React, 60fps/2s/100ms) / **ASR-018** (editor-validation-feedback — 서버 Pydantic + 디바운스). **ASR-017·ASR-020**은 direct-input으로 해소 (루트 제한 + 경로 정규화 / 프런트 i18n).

- [x] **T-005** `done` — Gate: v2 ADR 승인
  - Phase: Step 3 (ADR)
  - Artifact: —
  - Depends: T-004
  - Notes: 2026-08-12 사용자 자동 계속 지시("계속 진행해 주세요")로 권장 옵션 전부 승인 처리 — ADR 5건 approved + direct-input 2건 Resolution 기록. v2 ASR 7건 전부 designed.

- [x] **T-006** `done` — Step 4: v2 Spec 작성 (spec-writing 위임)
  - Phase: Step 4 (Spec)
  - Artifact: `spec/sdv-sim-v2.md`
  - Depends: T-005
  - Notes: **spec/sdv-sim-v2.md 작성 완료** (2026-08-12) — ASR-014~020 Resolution deep-copy (기술 스택/서버·패키징/데이터 흐름/렌더링·성능/편집·검증/파일시스템 보안/UI 언어) + 파생 세부(API 9종, 포트·종료 코드, 샌드박스 루트, 스텁 실행, 성능 기준, 오버레이 규칙). 자체-포함·테스트 가능한 불릿. ASR.md Spec 필드 동기화 완료 (7건).

- [x] **T-007** `done` — Gate: v2 Spec 승인
  - Phase: Step 4 (Spec)
  - Artifact: `spec/sdv-sim-v2.md`
  - Depends: T-006, T-012
  - Notes: **2026-08-12 사용자 명시 승인("v2 spec을 승인함. 구현을 시작해줘")** — F-1~F-11 전부 인코딩/해소 완료 상태에서 승인. 승인 후속: ASR-014~020 approved 전환 (완료), T-008 생성 시작 (진행 중).

- [x] **T-011** `done` — Gate: F-11 ADR 2건 승인 (core-yaml-string-input + dashboard-browser-file-access)
  - Phase: Step 3 (ADR) — 재검토
  - Artifact: `adr/core-yaml-string-input.md`, `adr/dashboard-browser-file-access.md`
  - Depends: —
  - Notes: 2026-08-12 사용자 승인("오케이") — core-yaml-string-input **Option A**(loads()), dashboard-browser-file-access **Option C**(하이브리드). ADR approved 전환, ASR-006/015/017/019 designed 재전환 + Resolution 갱신, dashboard-run-path superseded 유지.

- [x] **T-012** `done` — v2 Spec 수정 (F-1~F-10 + F-11 방향 인코딩) + PRD 개정
  - Phase: Step 4 (Spec) — 재작업
  - Artifact: `spec/sdv-sim-v2.md`, `spec/PRD.md`, `spec/sdv-sim-v1.md`(D-15 갱신), `spec/ASR.md`
  - Depends: T-011
  - Notes: 2026-08-12 완료. F-1(supersede 문구)·F-2(arch_content 단일 액션)·F-4(validate 범위)·F-5(시크 load-log 근사)·F-6(타입 밴드 규칙)·F-7(409 session_invalid)·F-8(오류 스키마)·F-10(해시 라우팅) 인코딩 + F-3 근거 명시 + F-9·F-11(파일 API·--root 제거, 브라우저 파일 = FS Access API + 폴백, v1 `loads()` 추가) 반영. PRD "v1 코어 무변경"→"문자열 입력 API 추가만" 개정 + v1 Spec D-15에 `loads()`/`load_scenario_yaml()` 기록 + Constraints/비목표/Open Questions 갱신.

- [ ] **T-008** `in_progress` — Step 5: v2 대시보드 생성 (spec 기반)
  - Phase: Step 5 (Generation)
  - Artifact: `sdv-simulator/` 내 대시보드 산출물
  - Depends: T-007
  - Notes: Spec이 유일 입력. v1 코어 재사용, Requirements/Decisions/Constraints 준수. **단위 작업 T-013~T-021로 분해 (2026-08-12).**

- [x] **T-013** `done` — v1 코어 문자열 입력 API (`loads`/`load_scenario_yaml`) + 테스트
  - Phase: Step 5 (Generation) — v1 코어 확장
  - Artifact: `sdv_sim/core/engine.py`, `sdv_sim/__init__.py`, `tests/test_string_input.py`
  - Depends: T-008
  - Notes: **2026-08-12 완료** — core-yaml-string-input Option A. `loads()`/`load_scenario_yaml()`/`_parse_yaml_text()`/`_tagged_scenario_error()` 추가, 의사 식별자 `arch`/`scenario` + 줄 번호 매핑. 기존 `load()` 계약 하위 호환 유지. pytest 85 passed, mypy strict clean (13 files).

- [x] **T-014** `done` — 서버 백엔드 (`sdv_sim/server/`): 세션·로그 로더·FastAPI 앱·API 5종
  - Phase: Step 5 (Generation) — 서버
  - Artifact: `sdv_sim/server/{__init__,app,session,log_loader}.py`, `sdv_sim/i18n.py`(서버 키), `pyproject.toml`(fastapi/uvicorn/httpx)
  - Depends: T-013
  - Notes: `/api/validate`·`/api/run`·`/api/load-log`·`/api/events`·`/api/report`. 세션 수명주기(M-4)·load-log 파생 규칙(M-1)·409 session_invalid(F-7)·오류 스키마(F-8)·스태틱 서빙. **2026-08-12 완료** — session.py(세션 모델), log_loader.py(v1 events.json 검증·M-1 파생 — arch 포함 시 kind/bus_load_percent/period_ms 추가, supersede_count·warnings는 구조적으로 불가 → 미포함), app.py(API 5종 + F-8 오류 엔벨로프 + 409 + 스태틱 조건부 서빙), i18n 서버 키 13종, pyproject fastapi/uvicorn/httpx. 구현 결정 — **세션 무효화 트리거 = `/api/validate` 호출** (M-4 "첫 변경" 기준; API 5종에 전용 엔드포인트가 없어 편집 시 자동 호출되는 validate가 무효화 신호). load-log arch_content = arch 스키마 검증만. **검증: pytest 104 passed (server 19종 포함), mypy strict 17 files clean.**

- [x] **T-015** `done` — CLI `serve` 명령 (--port/--lang/--dev, 포트 점유 → exit 2)
  - Phase: Step 5 (Generation) — CLI
  - Artifact: `sdv_sim/cli/main.py`, `sdv_sim/cli/serve.py`
  - Depends: T-014
  - Notes: **2026-08-12 완료 (Sync 확인)** — serve.py(사전 바인딩 → 포트 점유 시 exit 2, stdout 로그, fd 기반 uvicorn 실행, `--dev`는 Vite 프록시용) + main.py serve 서브커맨드(`--port`/`--lang`/`--dev`). 테스트 — help 옵션, 포트 점유 exit 2, 실제 uvicorn 서브프로세스 라이브 스모크(시작 URL stdout, SIGTERM 정상 종료) 포함. **검증: pytest 107 passed (test_cli.py 17개 — serve 3종 포함), mypy strict 18 files clean.**

- [ ] **T-016** `pending` — 프런트엔드 스캐폴딩 (Vite+React+TS, i18n ko/en, 해시 라우팅, API 클라이언트)
  - Phase: Step 5 (Generation) — 프런트엔드
  - Artifact: `frontend/` (package.json, vite.config, src/)
  - Depends: T-015
  - Notes: Node v24.18.1(nvm). UI 문자열 하드코딩 금지(ASR-020). 해시 라우팅(F-10).

- [ ] **T-017** `pending` — 구조 뷰: SVG 렌더 + 타입 밴드 자동 레이아웃 (결정적, F-6/M-5)
  - Phase: Step 5 (Generation) — 프런트엔드
  - Artifact: `frontend/src/StructureView.tsx`, `frontend/src/layout.ts`
  - Depends: T-016
  - Notes: HPC 상단/게이트웨이 중앙/ECU 하단. 밴드 내 = 링크 수 내림차순 → 이름 사전순. CAN/Ethernet 시각 구분.

- [ ] **T-018** `pending` — 편집기·파일 관리 (FS Access API+폴백, IndexedDB 최근 파일, 디바운스 500ms 검증)
  - Phase: Step 5 (Generation) — 프런트엔드
  - Artifact: `frontend/src/EditorPane.tsx`, `frontend/src/fileManager.ts`, `frontend/src/useValidation.ts`
  - Depends: T-016
  - Notes: 실시간 동기화(유효 시 다이어그램 갱신, 오류 시 마지막 유효 상태 유지). 저장/실행 시 강제 검증. 편집 시작 시 세션 무효화(M-4).

- [ ] **T-019** `pending` — 리플레이: 컨트롤·타임라인·시크(O(K))·오버레이 애니메이션·필터·이벤트 패널·리포트
  - Phase: Step 5 (Generation) — 프런트엔드
  - Artifact: `frontend/src/replay/`, `frontend/src/ReportPanel.tsx`, `frontend/src/EventPanel.tsx`
  - Depends: T-016, T-017
  - Notes: tx_ms 물리 재생(run 경로)/고정 펄스 폴백(load-log, F-5). 배속 0.5x/1x/2x/4x. task=task_start+task_end 그룹 필터.

- [ ] **T-020** `pending` — 프런트엔드 빌드 + 정적 자산 패키징 (`sdv_sim/server/static/`, wheel 포함)
  - Phase: Step 5 (Generation) — 패키징
  - Artifact: `sdv_sim/server/static/`, `pyproject.toml` (hatch force-include)
  - Depends: T-019
  - Notes: 빌드 산출물만 런타임 사용. `npm run build` → outDir `../sdv_sim/server/static`.

- [ ] **T-021** `pending` — 통합 테스트 + 전체 스위트 (pytest·mypy) 통과
  - Phase: Step 5 (Generation) — 품질
  - Artifact: `tests/test_server.py`, `tests/test_string_input.py`
  - Depends: T-014, T-015, T-020
  - Notes: serve 스모크 테스트(TestClient), API 계약(409/오류 스키마/load-log 파생), v1 회귀 전체.

- [ ] **T-009** `pending` — v2 검증 (spec-driven-verification)
  - Phase: Verification
  - Artifact: `verification/sdv-sim-v2.md`
  - Depends: T-008
  - Notes: PRD·v2 스펙 대비 항목별 비교, deviation/미문서화 ASR 식별 → 피드백 루프.

- [ ] **T-010** `pending` — Gate: v2 완료 승인
  - Phase: Verification (feedback loop)
  - Artifact: —
  - Depends: T-009
  - Notes: 검증 결과 리뷰 후 사용자 명시 승인. 이후 v3(데스크톱) 논의 가능.

## Notes

- **Sync (2026-08-12, 진행 상황 확인 시점)**: T-014(서버 백엔드)·T-015(CLI serve)는 파일·테스트가 실제 완료 상태였으나 status 미반영 drift 확인 → `done` 처리. 검증: pytest 107 passed, mypy strict 18 files clean (serve 스모크 포함). Snapshot 12/1/8로 재계산.
- **v2 Spec 승인 (2026-08-12, T-007 done)**: 사용자 명시 승인("v2 spec을 승인함. 구현을 시작해줘"). ASR-014~020 전부 approved 전환 완료. **T-008 생성 진입** — 단위 T-013~T-021 (v1 문자열 입력 API → 서버 → CLI serve → 프런트엔드 → 패키징 → 통합 테스트).
- **v1 아카이브**: 2026-08-12 v1 완료 시점의 TODO.md를 `TODO-v1.md`로 복사 보존 (v1: Done 22 / Pending 1 — T-017 v2 스테이징).
- **v2 시작 (2026-08-12)**: 사용자 지시("v2 진행을 위한 TODO.md 파일을 다시 생성하고 v2를 진행하자"). v1 스코프 전부 승인 완료 상태에서 진입.
- **프로젝트 루트**: `/home/ubuntu/workspace/softwares/sdv-simulator` — 기존 폴더 재사용 (신규 생성 없음).
- **v2 워크플로우**: spec-driven-generation (Step 0 → 1 → 2 → 3 → 4 → 5 → 검증). v1과 동일.
- **v2 범위 (PRD 기준)**: 웹 대시보드 — 아키텍처·메시지 흐름·노드 상태 시각화 및 인터랙션. OTA(업데이트 캠페인·버전 관리·배포 흐름)는 PRD v2 절에 포함돼 있으나 이번 스테이지 포함 여부는 T-001에서 사용자 확정 필요.
- **v2 범위 확정 (2026-08-12, T-001)**: 사용자 지시("OTA는 포함하지 않음") → **v2 = 웹 대시보드만**. OTA는 후속 후보로 PRD에 명시. PRD v2 갱신 완료(동작 방식·시각화·인터랙션·제공 형태, 비목표/제약/성공 기준 v2 기준).
- **v1 코어 재사용**: ASR-006 Resolution — "v2 대시보드는 같은 코어 백엔드 + 별도 프런트엔드". 대시보드는 v1 코어 API(`load`/`run`/`events`)를 재사용하는 방향.
- **F-11 방향 전환 (2026-08-12)**: 사용자 지시 — "서버에 저장한다는 개념은 부적절" → (1) v1 core/cli에 YAML 문자열 입력 API(`loads()`) 추가, (2) 브라우저 로컬 파일 직접 사용 (Server-FS 샌드박스 탈피). 기존 "v1 코어 무변경"(PRD 제약·성공 기준 5) 개정 필요. `dashboard-run-path` ADR superseded, ASR-006/015/017 reviewing 복귀.
