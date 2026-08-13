# TODO: SDV Simulator v2 (웹 대시보드)

> **Project root:** `/home/ubuntu/workspace/softwares/sdv-simulator`
> **Project type:** `software`
> **Project ID:** `software-4bfdd444-2f43-4c97-b6dd-abba9b3e9f17`
> **Updated:** 2026-08-13

## Snapshot

| Done | In progress | Pending | Blocked | Skipped |
|------|-------------|---------|---------|---------|
| 22   | 1           | 1       | 0       | 0       |

**Current focus:** T-024 — 리포트 409: validate가 세션을 무효화하지 않도록 분리 (M-4 재설계)
**Recommended next:** T-024 완료 후 T-010 — Gate: v2 완료 승인

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

- [x] **T-008** `done` — Step 5: v2 대시보드 생성 (spec 기반)
  - Phase: Step 5 (Generation)
  - Artifact: `sdv-simulator/` 내 대시보드 산출물
  - Depends: T-007
  - Notes: Spec이 유일 입력. v1 코어 재사용, Requirements/Decisions/Constraints 준수. **단위 작업 T-013~T-021로 분해 (2026-08-12). 2026-08-13 T-013~T-021 전부 done으로 전체 완료 처리.**

- [x] **T-013** `done` — v1 코어 문자열 입력 API (`loads`/`load_scenario_yaml`) + 테스트
  - Phase: Step 5 (Generation) — v1 코어 확장
  - Artifact: `sdv_sim/core/engine.py`, `sdv_sim/__init__.py`, `tests/test_string_input.py`
  - Depends: T-008
  - Notes: **2026-08-12 완료** — core-yaml-string-input Option A. `loads()`/`load_scenario_yaml()`/`_parse_yaml_text()`/`_tagged_scenario_error()` 추가, 의사 식별자 `arch`/`scenario` + 줄 번호 매핑. 기존 `load()` 계약 하위 호환 유지. pytest 85 passed, mypy strict clean (13 files).

- [x] **T-014** `done` — 서버 백엔드 (`sdv_sim/server/`): 세션·로그 로더·FastAPI 앱·API 5종
  - Phase: Step 5 (Generation) — 서버
  - Artifact: `sdv_sim/server/{__init__,app,session,log_loader}.py`, `sdv_sim/i18n.py`(서버 키), `pyproject.toml`(fastapi/uvicorn/httpx)
  - Depends: T-013
  - Notes: `/api/validate`·`/api/run`·`/api/load-log`·`/api/events`·`/api/report`. 세션 수명주기(M-4)·load-log 파생 규칙(M-1)·409 session_invalid(F-7)·오류 스키마(F-8)·스태틱 서빙. **2026-08-12 완료** — session.py(세션 모델), log_loader.py(v1 events.json 검증·M-1 파생 — arch 포함 시 kind/bus_load_percent/period_ms 추가, supersede_count·warnings는 구조적으로 불가 → 미포함), app.py(API 5종 + F-8 오류 엔벨로프 + 409 + 스태틱 조건부 서빙), i18n 서버 키 13종, pyproject fastapi/uvicorn/httpx. 구현 결정 — **세션 무효화 트리거 = `/api/validate` 호출** (M-4 "첫 변경" 기준; API 5종에 전용 엔드포인트가 없어 편집 시 자동 호출되는 validate가 무효화 신호). load-log arch_content = arch 스키마 검증만. **검증: pytest 104 passed (server 19종 포함), mypy strict 17 files clean.** (TODO Sync 2026-08-13 — 코드 존재·테스트 통과 재확인으로 done 확정, pytest 107 passed / mypy 18 files clean)

- [x] **T-015** `done` — CLI `serve` 명령 (--port/--lang/--dev, 포트 점유 → exit 2)
  - Phase: Step 5 (Generation) — CLI
  - Artifact: `sdv_sim/cli/main.py`, `sdv_sim/cli/serve.py`
  - Depends: T-014
  - Notes: 단일 프로세스, 시작 URL 출력, Ctrl+C 종료. `--dev`는 Vite dev server 프록시(HMR). **2026-08-13 완료** — main.py에 serve 서브커맨드(--port 기본 8888/--lang/--dev), serve.py에 run_serve·_bind(점유 시 exit 2)·stdout 로그·시작 URL 출력. tests/test_cli.py serve 테스트(help 옵션·포트 점유 → exit 2) 포함 107 passed 확인.

- [x] **T-016** `done` — 프런트엔드 스캐폴딩 (Vite+React+TS, i18n ko/en, 해시 라우팅, API 클라이언트)
  - Phase: Step 5 (Generation) — 프런트엔드
  - Artifact: `frontend/` (package.json, vite.config, src/)
  - Depends: T-015
  - Notes: **2026-08-13 완료** — Vite+React+TS 스캐폴딩. 설정: vite.config(빌드 outDir `../sdv_sim/server/static`, dev 5173 고정), tsconfig 3종(strict), package.json(react 19). src/: types/schema.ts(SimEvent·Report·Architecture·Scenario·ApiError(F-8)·API payload — v1 스키마 D-12·D-18·D-21 반영), api/client.ts(API 5종, F-8 엔벨로프 언랩, ApiResult), i18n/(ko/en 카탈로그 + 언어 결정: 사용자 선택(localStorage) > 서버 주입 `window.__SDV_SIM_LANG__`(serve --lang/SDV_SIM_LANG — T-020 서버 주입 예정) > 브라우저 로케일 > ko, 스위치), router.ts(해시 라우팅 F-10 — #/editor|replay|report), App.tsx(헤더·언어 스위치·내비·뷰 플레이스홀더). **검증: `npm run build` 성공(tsc -b + vite build → sdv_sim/server/static/ 산출물), `npm run typecheck` 통과. TestClient로 GET / = 200 index.html 서빙 + GET /api/events = 409 session_invalid(F-7) 확인.** 구현 결정 — i18n `index.ts`는 JSX 포함이라 `index.tsx`로 생성. esbuild postinstall approve 필요.

- [x] **T-017** `done` — 구조 뷰: SVG 렌더 + 타입 밴드 자동 레이아웃 (결정적, F-6/M-5)
  - Phase: Step 5 (Generation) — 프런트엔드
  - Artifact: `frontend/src/StructureView.tsx`, `frontend/src/layout.ts`
  - Depends: T-016
  - Notes: **2026-08-13 완료** — layout.ts(결정적 타입 밴드: HPC 상단/게이트웨이 중앙/ECU 하단, 빈 밴드 생략, 밴드 내 링크 수 내림차순 → 이름 사전순(코드 유닛 순), 밴드 간 직선·동일 밴드 Q-arc(ARC_RISE), CAN/Ethernet은 위치에 무관한 시각 속성만), StructureView.tsx(SVG — 노드 타입별 색, CAN 실선 두꺼움/Ethernet 대시, 링크 위 프레임 라벨, 밴드 라벨), yaml.ts(렌더링용 방어적 YAML 파서 — 서버가 검증 권위자, ASR-018), scripts/check-layout.ts(결정성·밴드 순서·밴드 내 정렬·kind 시각 전용 검증 9종). App editor 뷰에 샘플(samples/basic) 데모 시드 연결. **검증: `npm run check:layout` all passed, typecheck 통과, build 성공.** 구현 결정 — D3 미사용(비결정적 포스 금지 M-5, 순수 결정형 레이아웃), js-yaml 의존성 추가, Node 타입 스트리핑 호환(type-only import + runtime .ts 확장자).

- [x] **T-018** `done` — 편집기·파일 관리 (FS Access API+폴백, IndexedDB 최근 파일, 디바운스 500ms 검증)
  - Phase: Step 5 (Generation) — 프런트엔드
  - Artifact: `frontend/src/EditorPane.tsx`, `frontend/src/fileManager.ts`, `frontend/src/useValidation.ts`
  - Depends: T-016
  - Notes: **2026-08-13 완료** — fileManager.ts(FS Access API `showOpenFilePicker`/`showSaveFilePicker` + `<input type=file>`/Blob 다운로드 폴백, IndexedDB 최근 파일 20개 한정, 아키텍처/시나리오 스켈레톤 템플릿, kind 추론: 파일명 arch/scen → 내용 마커 → 기본 arch), useValidation.ts(디바운스 500ms 자동 검증 + `forceValidate`(저장/실행 시 강제, 실패 시 거부), seq 가드로 늦은 응답 무시, 시나리오는 **유효한 아키텍처 제공 시에만** 참조 검증 — F-4), EditorPane.tsx(2-탭 고정: 아키텍처+시나리오, 툴바: 새/열기/최근/저장/실행, 줄 번호 gutter+오류 줄 마커, 오류 패널 클릭 시 줄 이동, Tab=2-space, 상태바: 검증 중/유효/오류 n건/서버 오프라인), App.tsx(demo seed 제거 — 구조 뷰가 편집 내용과 연동, **마지막 유효 아키텍처 유지**(스펙), 실행: 강제 검증 → `apiRun` → #/replay), i18n 키 26종 추가 + `t()` 파라미터 치환(`{n}`). **검증: `npm run check:files` 23 checks passed, typecheck 통과, build 성공, serve 통합 확인(템플릿 3종 `/api/validate` 전부 valid, index.html 서빙).** 구현 결정 — 아키텍처/시나리오 각 1개 슬롯의 고정 탭 모델(파일 열기/새로 만들기로 슬롯 교체)로 검증 훅 2개 고정·단순화, 최근 파일은 소형 YAML 내용을 저장(로그 JSON은 편집 대상 아님), 저장 성공 시에만 dirty 해제.

- [x] **T-019** `done` — 리플레이: 컨트롤·타임라인·시크(O(K))·오버레이 애니메이션·필터·이벤트 패널·리포트
  - Phase: Step 5 (Generation) — 프런트엔드
  - Artifact: `frontend/src/replay/`, `frontend/src/ReportPanel.tsx`, `frontend/src/ReportView.tsx`, `frontend/src/EventPanel.tsx`, `frontend/src/layout.ts`, `frontend/src/StructureView.tsx`, `frontend/src/App.tsx`, `frontend/src/styles.css`, `frontend/scripts/check-replay.ts`
  - Depends: T-016, T-017
  - Notes: **2026-08-13 완료** — 시크 엔진(replayIndex.ts: `computeTxMs` v1 공식 그대로, `buildReplayIndex` 정렬 검증+스냅샷 K=2000, `seekToTime` O(K) 상한, `advanceToTime` 증분+prune → **불변식 advance(t)==seek(t)**), 재생 클록(useReplayClock.ts: rAF, 배속 0.5/1/2/4x, 끝 도달 자동 정지), 오버레이(ReplayOverlay.tsx: 구조 SVG 동일 좌표계 `<g>` — 비행 프레임·활성 링크·drop×오버런 플래시·실행 태스크 테두리·물리 모드 bus_load 배지·pulse 모드 "≈ 근사 표시" 라벨 F-5), 이벤트 패널(EventPanel.tsx: 고정 행고 22px 가상화, 재생 중 자동 팔로우, 클릭 시크, 타입 배지), 리포트(ReportPanel.tsx+ReportView.tsx: 전체 리포트 + M-1 파생 모드 — bus_load/kind/period/supersede "—", **event_count는 파생에도 항상 존재해 표시**), ReplayView.tsx(모드 판정: bus_load_percent 존재 ⇔ 물리), 구조 클릭 엔티티 필터(layout.ts `LayoutLink.nodes`+StructureView overlay/onSelect props), load-log(openLogFile→apiLoadLog→arch_content 전달, M-4 세션 교체), App sessionMeta(파일 열기/새로 만들기/슬롯 교체 → 세션 리셋, run → #/replay), i18n 40+ 키(ko/en 동일 세트). **검증: `npm run check:replay` all passed (tx_ms 공식 4종·시크 24개 타겟=전체 재스캔 동등·O(K) 구조 상한·블록 경계 대형 10만 이벤트·pulse 폴백·증분=시크), check:layout·check:files 통과, typecheck 통과, build 성공, serve 통합(8888) — run→physical(64 events), 편집 → 409 session_invalid, load-log arch 있음→physical(bus_load 1)/없음→pulse(0), 로그 무효 → 422 log_invalid, 정적 에셋 서빙 확인.** 구현 결정 — **시크 시 만료 프레임 prune을 seek와 advance 양쪽에 적용**해 재생 중·시크 후 표시가 항상 일치(참조 재스캔에 prune 미러링 — 초기 21건 실패 → 수정), task_end 시 빈 태스크 Set 자동 삭제("has(node) ⇔ 실행 중").

- [x] **T-020** `done` — 프런트엔드 빌드 + 정적 자산 패키징 (`sdv_sim/server/static/`, wheel 포함)
  - Phase: Step 5 (Generation) — 패키징
  - Artifact: `sdv_sim/server/static/`, `pyproject.toml` (hatch force-include), `sdv_sim/server/app.py` (index.html 언어 주입), `README.md` (serve 문서)
  - Depends: T-019
  - Notes: **2026-08-13 완료** — 빌드 산출물(`npm run build` → outDir `../sdv_sim/server/static`)만 런타임 사용. **index.html 언어 주입(ASR-020)**: `serve --lang`/`SDV_SIM_LANG` → `_inject_lang()`로 `<head>`에 `window.__SDV_SIM_LANG__` 스크립트 삽입 (주입 위치 검증 테스트 포함). **wheel 패키징(ASR-019)**: hatch `force-include` + `exclude`로 static을 정확히 1회 포함 (force-include만 사용 시 double-add ValueError 발생 → `exclude = ["sdv_sim/server/static"]` 병행으로 해결). static 누락 시 FileNotFoundError로 빌드 실패(fail-fast — UI 없는 wheel 방지). **검증**: wheel 내용 25 entries 중 static 3건(index.html + assets js/css) 1회 포함 확인, serve 통합 --lang en → `"en"` 주입 + assets 200 확인, pytest 111 passed, mypy strict 18 files clean.

- [x] **T-021** `done` — 통합 테스트 + 전체 스위트 (pytest·mypy) 통과
  - Phase: Step 5 (Generation) — 품질
  - Artifact: `tests/test_server.py`, `tests/test_string_input.py`
  - Depends: T-014, T-015, T-020
  - Notes: **2026-08-13 완료** — serve 스모크 테스트(TestClient, GET / 200 + 정적 에셋), API 계약(409/오류 스키마/load-log 파생), index.html 언어 주입 테스트(ko/en + `<head>` 내 위치), v1 회귀 포함. **pytest 111 passed, mypy strict 18 files clean.**

- [x] **T-009** `done` — v2 검증 (spec-driven-verification)
  - Phase: Verification
  - Artifact: `verification/sdv-sim-v2.md`
  - Depends: T-008
  - Notes: **2026-08-13 완료** — `verification/sdv-sim-v2.md` 작성 (43 pass / 1 partial / 3 not-verifiable, fail 0, Out of Scope 침범 0). **피드백 루프 (사용자 승인)**: E15 partial 수용 → U-1(무효화 신호 = validate 호출)을 `spec/sdv-sim-v2.md` M-4 절·API 절·Requirements 절 3곳에 인코딩, ASR-015 Notes 기록. F1/F2 실측 벤치마크는 추후 진행으로 확정. 서버 테스트 23 passed 회귀 없음. 검증 근거: 서버 코드 전문 독해 + TestClient 통합 스모크 9종 + pytest 111 passed + mypy 18 files clean + check-{layout,files,replay} + typecheck + wheel 내용. **다음: T-010 게이트 (사용자 승인 필요).**

- [x] **T-022** `done` — serve 외부 접근 (`--host` 옵션 + OS 방화벽 8888 허용)
  - Phase: Step 5 (Generation) — CLI (피드백)
  - Artifact: `adr/serve-network-binding.md`, `sdv_sim/cli/{serve,main}.py`, `sdv_sim/i18n.py`, `tests/test_cli.py`, `spec/sdv-sim-v2.md`, `spec/PRD.md`, `spec/ASR.md`, `README.md`
  - Depends: T-015, T-020
  - Notes: **2026-08-13 완료 (사용자 요청 "외부 브라우저 접근" → ADR "1" 승인)** — serve-network-binding ADR(Option B: `--host` 옵션, 기본 127.0.0.1) 작성·승인·ASR-019 designed 재전환. 스펙 인코딩(sdv-sim-v2.md Context/제공 형태/Requirements/Constraints/Out of Scope + PRD.md + ASR-019 Resolution). 구현: `--host` 파싱·전달, `0.0.0.0` 시 외부 노출 경고 출력(ko/en i18n), 시작 URL에 host 반영. **OS 방화벽(OCI) 8888 허용 규칙 추가 + netfilter-persistent 영속화** — 기존에 8787/8080/11434/22만 허용, 8888은 기본 REJECT였음. **검증**: pytest 113 passed(신규 2종: --host 전달·경고 출력), mypy 18 files clean, i18n 41키 패리티, **외부 접근 확인 — check-host.net 전 세계 58/58 노드 HTTP 200**, 서버 로그에 외부 IP(141.98.234.68) 접근 200 기록. README serve 섹션에 --host + 외부 노출 경고 문서화. **다음: T-010 게이트.**

- [x] **T-023** `done` — 기본 시나리오 basic 샘플 시드 (즉시 실행 가능)
  - Phase: Step 5 (Generation) — 프런트엔드 (피드백)
  - Artifact: `frontend/src/fileManager.ts`, `frontend/src/App.tsx`, `frontend/scripts/check-files.ts`, `spec/sdv-sim-v2.md`
  - Depends: T-018
  - Notes: **2026-08-13 완료 (사용자 요청 — "기본 실행에서 시나리오도 basic 샘플로, 모르는 사람도 그냥 실행")** — `scenarioTemplate()`을 `samples/basic/scenario.yaml` 미러로 교체 (문 제어 100ms: 주입 메시지 1건 + assertion 5건), App.tsx 시나리오 슬롯 기본 시드(null → template, 닫기 가능 유지), 스펙 L77(새로 만들기·기본 시드) + Requirements 불릿 추가, check-files 검증 강화(메시지 ≥1·assertion ≥1). **검증**: check:files all passed(신규 2종 포함), typecheck·build 성공, 새 빌드 서빙 확인(asset index-11yoEP0a.js), **통합 확인 — 기본 시드 시나리오로 run: exit 0 + report result pass + assertions 5/5 pass, validate arch/scen 200 True**, pytest 113 passed, mypy 18 files clean. 서버 재시작으로 외부 접근 유지(58/58 노드 OK). **다음: T-010 게이트.**

- [ ] **T-010** `pending` — Gate: v2 완료 승인
  - Phase: Verification (feedback loop)
  - Artifact: —
  - Depends: T-009
  - Notes: 검증 결과 + 외부 접근 + 기본 샘플 반영 리뷰 후 사용자 명시 승인. 이후 v3(데스크톱) 논의 가능. **2026-08-13 T-024(리포트 409 버그) 수정 후 재승인 필요.**

- [ ] **T-024** `in_progress` — [버그수정] 리포트 409: validate가 세션을 무효화하지 않도록 분리 (M-4 재설계)
  - Phase: Step 5 (Generation) — 크로스컷 (피드백)
  - Artifact: `sdv_sim/server/{app,session}.py`, `frontend/src/{App.tsx,ReportView.tsx,replay/ReplayView.tsx,types/schema.ts,i18n/messages.ts}`, `spec/sdv-sim-v2.md`, `spec/ASR.md`, `tests/test_server.py`
  - Depends: T-009
  - Notes: **2026-08-13 사용자 버그 리포트** — "실행→재생 후 리포트로 가면 로그 파일이 필요하다고 함". 원인: (1) 서버 `/api/validate`가 호출마다 세션 무효화(M-4 무효화 신호=validate), (2) 프런트 `useValidation`이 편집 없이도(마운트/재마운트 디바운스) validate 호출 → run 후 편집기 방문/재로드 시 세션 사망, (3) 리포트 409 → noSession 문구가 "로그 파일" 오해 유발. **수정 방향 (사용자 승인)**: validate는 순수 검증으로 전환(무효화 제거), 세션 무효화는 **프런트 로컬 상태**(SessionMeta.invalidated — handleEdit에서 편집 시작 시 표시)로 이동, ReplayView/ReportView가 invalidated면 서버 조회 전 "무효" 표시, 스펙 M-4/API/Requirements + ASR-015 U-1 문구 갱신, noSession 문구 개선. **2026-08-13 T-024 버그(리포트 409 세션 무효화)로 승인 보류 — T-024 완료 후 재승인 필요.**

- [ ] **T-024** `in_progress` — [버그수정] 리포트 409: validate가 세션을 무효화하지 않도록 분리 (M-4 재설계)
  - Phase: Step 5 (Generation) — 크로스컷 (피드백)
  - Artifact: `sdv_sim/server/{app,session}.py`, `frontend/src/{App.tsx,ReportView.tsx,replay/ReplayView.tsx,types/schema.ts,i18n/messages.ts}`, `spec/sdv-sim-v2.md`, `spec/ASR.md`, `tests/test_server.py`
  - Depends: T-009
  - Notes: **2026-08-13 사용자 버그 리포트** — "실행→재생 후 리포트로 가면 로그 파일이 필요하다고 함". 원인: (1) 서버 `/api/validate`가 호출마다 세션 무효화(M-4 무효화 신호=validate), (2) 프런트 `useValidation`이 편집 없이도(마운트/재마운트 디바운스) validate 호출 → run 후 편집기 방문/재로드 시 세션 사망, (3) 리포트 409 → noSession 문구가 "로그 파일" 오해 유발. **수정 방향 (사용자 승인)**: validate는 순수 검증으로 전환(무효화 제거), 세션 무효화는 **프런트 로컬 상태**(SessionMeta.invalidated — handleEdit에서 편집 시작 시 표시)로 이동, ReplayView/ReportView가 invalidated면 서버 조회 전 "무효" 표시, 스펙 M-4/API/Requirements + ASR-015 U-1 문구 갱신, noSession 문구 개선.

## Notes

- **T-023 기본 샘플 시드 완료 (2026-08-13)**: 시나리오 슬롯도 basic 샘플로 시작 — 새 세션에서 파일 생성 없이 [실행]만 누르면 리플레이·리포트 확인 가능 (assertions 5건 pass 확인). 시나리오는 탭 닫기로 제거 가능(기존 동작 유지).
- **T-022 serve 외부 접근 완료 (2026-08-13)**: 사용자 요청("외부 브라우저에서 http://161.33.194.12:8888 접근") → serve-network-binding ADR Option B 승인("1"). `--host 0.0.0.0`로 외부 접근 가능 + OCI OS 방화벽 8888 허용·영속화. **현재 서버 실행 중** (`sdv-sim serve --port 8888 --host 0.0.0.0 --lang ko`, setsid) — 외부에서 `http://161.33.194.12:8888` 접속 가능 (58/58 노드 확인). 주의: 인증 없음 — 방화벽 출발지 IP 제한 권장.
- **T-020 패키징 완료 (2026-08-13)**: wheel에 대시보드 UI 포함 + 언어 주입 마무리 → **Step 5(v2 대시보드 생성) 전체 완료, T-008 done.** 다음 단계는 **T-009 v2 검증**(spec-driven-verification) — PRD·v2 스펙 대비 항목별 비교 후 사용자 승인(T-010).
- **T-019 리플레이 완료 (2026-08-13)**: run→#/replay 흐름이 닫힘 — 편집기 실행 → 리플레이(물리 tx_ms 재생 + 오버레이) → 리포트 뷰. load-log는 arch_content 유무로 물리/근사(pulse) 모드가 자동 전환(F-5, M-1/M-2). 시크 O(K)는 `check:replay`가 전역 재스캔 동등성 + 구조 상한(≤K 재적용)으로 검증. **다음: T-020 패키징** — index.html 언어 주입(`serve --lang`/`SDV_SIM_LANG` → `window.__SDV_SIM_LANG__`)과 hatch wheel force-include 포함.
- **T-018 편집기·파일 관리 완료 (2026-08-13)**: 구조 뷰가 실제 편집 내용과 연동됨 (데모 시드 제거). 서버 검증은 500ms 디바운스 자동 + 저장/실행 시 강제(실패 시 거부), 오류는 줄 마커+클릭 가능 오류 패널. 파일은 브라우저 로컬(FS Access API → 업로드/다운로드 폴백), 최근 파일은 IndexedDB. 시나리오 참조 검증은 아키텍처가 유효할 때만 arch 전달(F-4). **다음: T-019 리플레이** — 편집기 실행 버튼이 `apiRun` 성공 시 `#/replay`로 이동하므로, 리플레이 뷰가 완성되면 run→replay 흐름이 닫힌다.
- **기본 포트 8000 → 8888 변경 (2026-08-13)**: 사용자 요청. 스펙(sdv-sim-v2.md 2곳)·main.py(--port 기본값/help)·vite.config.ts 주석·TODO 기록 갱신. `sdv-sim serve --help`에 default 8888 표시, 실제 기본 실행이 127.0.0.1:8888 바인딩 확인, pytest 107 passed 회귀 확인.
- **T-017 구조 뷰 완료 (2026-08-13)**: 결정성·밴드 규칙을 Node 실행 스크립트(`npm run check:layout`)로 자동 검증. **T-018에서 편집 내용과 연동 완료** — 현재는 마지막 유효 아키텍처를 렌더링.
- **T-016 프런트엔드 스캐폴딩 완료 (2026-08-13)**: 빌드 산출물이 `sdv_sim/server/static/`에 생성 → serve가 SPA를 서빙. **ASR-020 언어 주입 미완성 항목**: 프런트 i18n은 `window.__SDV_SIM_LANG__`(서버 주입)을 지원하도록 구현했으나, 서버가 index.html에 언어를 주입하는 코드는 아직 없음 — **T-020 패키징 단계에서 index.html 언어 주입을 함께 처리 필요** (serve --lang/SDV_SIM_LANG → 프런트 초기 언어). 그 전까지는 브라우저 로케일 + localStorage 스위치로 동작.
- **TODO Sync (2026-08-13)**: 실제 파일·테스트 검증으로 드리프트 해소 — T-014(서버 백엔드)·T-015(CLI serve)는 코드가 이미 구현·통과 상태였으므로 `done` 처리 (pytest 107 passed, mypy strict 18 files clean). T-008(Step 5 생성)은 프런트엔드 단위(T-016~T-021)를 남겨두고 있어 `in_progress` 유지. 다음 작업 = T-016 프런트엔드 스캐폴딩.
- **v2 Spec 승인 (2026-08-12, T-007 done)**: 사용자 명시 승인("v2 spec을 승인함. 구현을 시작해줘"). ASR-014~020 전부 approved 전환 완료. **T-008 생성 진입** — 단위 T-013~T-021 (v1 문자열 입력 API → 서버 → CLI serve → 프런트엔드 → 패키징 → 통합 테스트).
- **v1 아카이브**: 2026-08-12 v1 완료 시점의 TODO.md를 `TODO-v1.md`로 복사 보존 (v1: Done 22 / Pending 1 — T-017 v2 스테이징).
- **v2 시작 (2026-08-12)**: 사용자 지시("v2 진행을 위한 TODO.md 파일을 다시 생성하고 v2를 진행하자"). v1 스코프 전부 승인 완료 상태에서 진입.
- **프로젝트 루트**: `/home/ubuntu/workspace/softwares/sdv-simulator` — 기존 폴더 재사용 (신규 생성 없음).
- **v2 워크플로우**: spec-driven-generation (Step 0 → 1 → 2 → 3 → 4 → 5 → 검증). v1과 동일.
- **v2 범위 (PRD 기준)**: 웹 대시보드 — 아키텍처·메시지 흐름·노드 상태 시각화 및 인터랙션. OTA(업데이트 캠페인·버전 관리·배포 흐름)는 PRD v2 절에 포함돼 있으나 이번 스테이지 포함 여부는 T-001에서 사용자 확정 필요.
- **v2 범위 확정 (2026-08-12, T-001)**: 사용자 지시("OTA는 포함하지 않음") → **v2 = 웹 대시보드만**. OTA는 후속 후보로 PRD에 명시. PRD v2 갱신 완료(동작 방식·시각화·인터랙션·제공 형태, 비목표/제약/성공 기준 v2 기준).
- **v1 코어 재사용**: ASR-006 Resolution — "v2 대시보드는 같은 코어 백엔드 + 별도 프런트엔드". 대시보드는 v1 코어 API(`load`/`run`/`events`)를 재사용하는 방향.
- **F-11 방향 전환 (2026-08-12)**: 사용자 지시 — "서버에 저장한다는 개념은 부적절" → (1) v1 core/cli에 YAML 문자열 입력 API(`loads()`) 추가, (2) 브라우저 로컬 파일 직접 사용 (Server-FS 샌드박스 탈피). 기존 "v1 코어 무변경"(PRD 제약·성공 기준 5) 개정 필요. `dashboard-run-path` ADR superseded, ASR-006/015/017 reviewing 복귀.
