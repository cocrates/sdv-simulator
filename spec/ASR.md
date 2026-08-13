# Architecturally Significant Requirements

Living registry for sdv-simulator. Status of each ASR must stay current.

## Summary

| ID | Title | Category | Status | Related ADRs | Spec |
|----|-------|----------|--------|--------------|------|
| ASR-001 | 언어/기술 스택 | Constraints & Integration | approved | adr/language-tech-stack.md (approved), adr/performance-targets.md (approved) | spec/sdv-sim-v1.md |
| ASR-002 | 시뮬레이션 엔진 모델 | Structure & Organization | approved | adr/simulation-engine-model.md (approved), adr/simulation-time-model.md (approved), adr/communication-event-semantics.md (approved), adr/event-ordering-boundary.md (approved), adr/result-report-schema.md (approved) | spec/sdv-sim-v1.md |
| ASR-003 | 아키텍처/시나리오 정의 형식 | Structure & Organization | approved | adr/definition-file-format.md (approved), adr/definition-schema-structure.md (approved), adr/definition-field-schema.md (approved) | spec/sdv-sim-v1.md |
| ASR-004 | 통신 프로토콜 충실도 (CAN/Ethernet) | Structure & Organization | approved | adr/communication-fidelity-level.md (approved), adr/can-fidelity-model.md (approved), adr/ethernet-fidelity-model.md (approved), adr/gateway-routing-rules.md (approved), adr/communication-event-semantics.md (approved), adr/frame-queue-overflow-policy.md (approved), adr/result-report-schema.md (approved) | spec/sdv-sim-v1.md |
| ASR-005 | 앱 런타임 모델 | Structure & Organization | approved | adr/app-runtime-model.md (approved), adr/task-scheduling-policy.md (approved), adr/component-api.md (approved), adr/stub-component-behavior.md (approved), adr/public-api-contract.md (approved), adr/task-overrun-policy.md (approved) | spec/sdv-sim-v1.md |
| ASR-006 | 코어 API 경계 & 다중 아티팩트 구조 | Deliverable form & Structure | designed | adr/package-structure.md (approved), adr/component-api.md (approved), adr/cli-output-policy.md (approved), adr/public-api-contract.md (approved), adr/cli-io-contract.md (approved), adr/core-yaml-string-input.md (approved) | spec/sdv-sim-v1.md |
| ASR-007 | 검증·자동화 지원 | Quality bar | approved | adr/verification-automation.md (approved), adr/assertion-grammar.md (approved), adr/event-log-schema.md (approved), adr/cli-output-policy.md (approved), adr/cli-io-contract.md (approved), adr/assertion-evaluation-detail.md (approved), adr/result-report-schema.md (approved) | spec/sdv-sim-v1.md |
| ASR-008 | 동일 시각 비-태스크 이벤트 순서 | Structure & Organization | designed | adr/event-ordering-non-task.md (approved) | spec/sdv-sim-v1.md |
| ASR-009 | Ethernet 스위치 다중 정의 정책 | Structure & Organization | designed | adr/ethernet-switch-selection.md (approved) | spec/sdv-sim-v1.md |
| ASR-010 | 로그 쓰기 실패 종료 코드 | Quality bar | designed | adr/log-write-failure-exit-code.md (approved) | spec/sdv-sim-v1.md |
| ASR-011 | Assertion `event: task` 매칭 범위 | Quality bar | designed | adr/assertion-task-event-matching.md (approved) | spec/sdv-sim-v1.md |
| ASR-012 | Assertion count 비교 연산 | Quality bar | designed | adr/assertion-count-minimum.md (approved) | spec/sdv-sim-v1.md |
| ASR-013 | Ethernet payload 크기 기준 | Structure & Organization | designed | adr/ethernet-payload-basis.md (approved) | spec/sdv-sim-v1.md |
| ASR-014 | 대시보드 기술 스택 (백엔드·프런트엔드) | Constraints & Integration | approved | adr/dashboard-tech-stack.md (approved) | spec/sdv-sim-v2.md |
| ASR-015 | 데이터 흐름·리플레이 모델 | Structure & Organization | approved | adr/dashboard-data-flow-replay.md (approved), adr/dashboard-run-path.md (superseded), adr/dashboard-session-lifecycle.md (approved), adr/dashboard-load-log-report.md (approved), adr/core-yaml-string-input.md (approved), adr/dashboard-browser-file-access.md (approved) | spec/sdv-sim-v2.md |
| ASR-016 | 구조 뷰 렌더링·성능 | Structure & Organization | approved | adr/topology-rendering-performance.md (approved), adr/dashboard-replay-animation-timing.md (approved), adr/dashboard-seek-state-indexing.md (approved), adr/dashboard-layout-determinism.md (approved), adr/dashboard-layout-placement-rule.md (approved) | spec/sdv-sim-v2.md |
| ASR-017 | 파일시스템 접근·보안 경계 | Constraints | approved | adr/dashboard-browser-file-access.md (approved) | spec/sdv-sim-v2.md |
| ASR-018 | 편집·검증 피드백 | Quality bar | approved | adr/editor-validation-feedback.md (approved) | spec/sdv-sim-v2.md |
| ASR-019 | 패키지 통합·서버 명령 (serve) | Deliverable form | approved | adr/serve-packaging.md (approved), adr/dashboard-browser-file-access.md (approved) | spec/sdv-sim-v2.md |
| ASR-020 | UI 언어 지원 (ko/en) | Constraints | approved | — (direct-input) | spec/sdv-sim-v2.md |

## Dependency Order (recommended review path)

1. ASR-001 (언어/기술 스택) → ASR-002 (시뮬레이션 엔진 모델) → ASR-003 (정의 형식) → ASR-004 (통신 충실도) → ASR-005 (앱 런타임 모델) → ASR-006 (코어 API 경계) → ASR-007 (검증·자동화)
2. 상세 설계 ADR (2026-08-12 전부 승인): simulation-time-model → definition-schema-structure → assertion-grammar → event-log-schema → can-fidelity-model → ethernet-fidelity-model → gateway-routing-rules → task-scheduling-policy → component-api → cli-output-policy → performance-targets
3. 2차 상세 설계 ADR (2026-08-12, D-12~D-21 전부 approved — Gate 5 재검토 미진 항목): definition-field-schema → communication-event-semantics → stub-component-behavior → public-api-contract → cli-io-contract → task-overrun-policy → frame-queue-overflow-policy → event-ordering-boundary → assertion-evaluation-detail → result-report-schema
4. 3차 검증 발굴 ADR (2026-08-12, U-1~U-6 전부 approved — 검증에서 식별된 미문서화 ASR 정식화): event-ordering-non-task → ethernet-switch-selection → log-write-failure-exit-code → assertion-task-event-matching → assertion-count-minimum → ethernet-payload-basis
5. v2 대시보드 (2026-08-12, ASR-014~020 신규 identified — PRD v2 승인 기반): ASR-014 (기술 스택) → ASR-019 (패키지 통합·serve) → ASR-015 (데이터 흐름·리플레이) → ASR-016 (구조 뷰 렌더링·성능) → ASR-017 (파일시스템 보안) → ASR-018 (편집·검증 피드백) → ASR-020 (UI 언어)
6. **F-11 방향 전환 재검토 (2026-08-12, 사용자 지시 — 서버-FS 샌드박스 탈피 + v1 문자열 입력 API):** ASR-006 (core-yaml-string-input proposed) → ASR-015 (core-yaml-string-input + dashboard-browser-file-access proposed, dashboard-run-path superseded) → ASR-017 (dashboard-browser-file-access proposed) → ASR-019 (`--root` 영향)

## ASR Detail

### ASR-001 — 언어/기술 스택

- **Category:** Constraints & Integration
- **Status:** approved
- **Statement:** 시뮬레이터 코어와 CLI를 구현할 프로그래밍 언어/런타임 선택
- **Why it matters:** 개발 생산성, 시뮬레이션 성능, 에코시스템(프로토콜 라이브러리, CI), 차량 SW 개발자와의 통합 용이성을 좌우
- **Depends on:** —
- **Related ADRs:**
  - `adr/language-tech-stack.md` — approved — 언어/기술 스택 비교 (Python/TypeScript/Go/Rust)
  - `adr/performance-targets.md` — approved — 성능 목표/확장 전략 (v1 순수 Python + 목표 규모)
- **Resolution path:** adr
- **Resolution:** Python 3.11+ 선택. 코어·CLI 모두 Python, 타입 힌트 + mypy, 배포는 pip 패키지 + CLI 진입점. 성능 병목 지점은 필요 시 확장 모듈로 이관 가능. v1 목표 규모: 노드 ≤ 50, 링크 ≤ 20, 프레임 ≤ 200, duration ≤ 60s, 이벤트 ≤ 100만.
- **Spec:** `spec/sdv-sim-v1.md` — Decisions/Constraints
- **Notes:** Spec 승인 (2026-08-12, T-007 통과 — 사용자 구현 지시) → approved 전환.

### ASR-002 — 시뮬레이션 엔진 모델

- **Category:** Structure & Organization
- **Status:** approved
- **Statement:** 시뮬레이션 진행 방식(이산 사건 vs 주기 기반 vs 연속 시간) 선택
- **Why it matters:** 코어 엔진 구조 전체를 결정. 통신 지연·메시지 라우팅을 정확하고 **결정적(deterministic)**으로 재현해야 검증 도구로 쓸 수 있음
- **Depends on:** ASR-001
- **Related ADRs:**
  - `adr/simulation-engine-model.md` — approved — 엔진 모델 비교 (DES/Time-step/Continuous)
  - `adr/simulation-time-model.md` — approved — 시간 표현·진행·종료 (정수 ms + (t_ms, seq) + duration_ms 종료 + 난수 없음)
  - `adr/communication-event-semantics.md` — approved — 통신 이벤트 기록 의미론 (rx 범위·게이트웨이·다중 홉)
  - `adr/event-ordering-boundary.md` — approved — 동일 시각 순서·종료 경계
  - `adr/result-report-schema.md` — approved — 실행 요약 리포트 항목
- **Resolution path:** adr
- **Resolution:** 이산 사건(DES) 기반 엔진 + 주기 태스크 하이브리드. 코어는 이벤트 큐, 앱 주기 태스크는 스케줄러가 이벤트로 생성·실행. 단일 스레드 + 고정 이벤트 순서로 결정성 보장. 모든 시간은 정수 ms, 이벤트는 (t_ms, seq) 완전 순서, 전파 지연 0.
- **Spec:** `spec/sdv-sim-v1.md` — Decisions/Requirements(시뮬레이션 엔진)
- **Notes:** Spec 승인 (2026-08-12, T-007 통과 — 사용자 구현 지시) → approved 전환.

### ASR-003 — 아키텍처/시나리오 정의 형식

- **Category:** Structure & Organization
- **Status:** approved
- **Statement:** 노드·토폴로지·시나리오를 기술하는 정의 파일 형식 결정
- **Why it matters:** 사용자가 아키텍처를 기술하는 방식 = CLI의 1차 UX이자 검증 자동화의 입력 형식
- **Depends on:** ASR-002
- **Related ADRs:**
  - `adr/definition-file-format.md` — approved — 정의 형식 비교 (YAML/JSON/TOML/DSL)
  - `adr/definition-schema-structure.md` — approved — YAML 내부 스키마 (메시지-프레임 2계층 분리 + 매핑 규칙)
  - `adr/definition-field-schema.md` — approved — 필드-레벨 스키마 + 시나리오 메시지 주입 형식
- **Resolution path:** direct-input | adr
- **Resolution:** YAML 채택. 사람이 작성하는 정의 파일의 가독성·주석·계층 표현 우선. PyYAML 파싱 + Pydantic 모델 기반 스키마 검증. architecture.yaml/scenario.yaml 분리, 컴포넌트는 메시지·링크는 프레임 소유(매핑: message 필드 또는 동일 이름).
- **Spec:** `spec/sdv-sim-v1.md` — Decisions/Requirements(정의)
- **Notes:** Spec 승인 (2026-08-12, T-007 통과 — 사용자 구현 지시) → approved 전환.

### ASR-004 — 통신 프로토콜 충실도 (CAN/Ethernet)

- **Category:** Structure & Organization
- **Status:** approved
- **Statement:** CAN/Ethernet 통신을 어느 수준(신호/메시지/프레임, 지연·대역폭 모델)까지 재현할지
- **Why it matters:** 시뮬레이션 충실도와 구현 비용의 균형. "무엇을 검증하는가"를 결정
- **Depends on:** ASR-002
- **Related ADRs:**
  - `adr/communication-fidelity-level.md` — approved — 충실도 수준 비교 (L1/L2/L3)
  - `adr/can-fidelity-model.md` — approved — CAN 지연·중재·부하 (비트 수식 + ID 우선 중재 + 큐 대기)
  - `adr/ethernet-fidelity-model.md` — approved — Ethernet 스위치·큐잉 (FIFO + 테일 드롭)
  - `adr/gateway-routing-rules.md` — approved — 라우팅 규칙 (from/to + remap_id)
  - `adr/communication-event-semantics.md` — approved — 이벤트 기록 의미론 (rx 범위·게이트웨이·다중 홉)
  - `adr/frame-queue-overflow-policy.md` — approved — 큐 대기 중 주기 인스턴스 정책
  - `adr/result-report-schema.md` — approved — 버스 부하·드롭 집계 리포트
- **Resolution path:** adr | direct-input
- **Resolution:** L2(프레임/버스 수준) 채택. CAN: tx_ms=ceil((44+8·DLC)/bitrate), ID 작을수록 중재 우선, 버스 점유 시 큐 대기. Ethernet: bytes=data+42, tx_ms=ceil(bytes·8/(Mbps·1000)), 단일 스위치 FIFO + queue_depth(기본 1000) 테일 드롭. 게이트웨이: from(link+frame|id 범위) → to(link+remap_id), delay_ms 기본 0. L3는 v1 제외.
- **Spec:** `spec/sdv-sim-v1.md` — Decisions/Requirements(통신)
- **Notes:** Spec 승인 (2026-08-12, T-007 통과 — 사용자 구현 지시) → approved 전환.

### ASR-005 — 앱 런타임 모델

- **Category:** Structure & Organization
- **Status:** approved
- **Statement:** 가상 노드에서 SW 컴포넌트(앱)를 실행하는 모델 결정
- **Why it matters:** "앱 런타임"의 의미를 정의. 컴포넌트 API, 수명주기, 통신 인터페이스 방식이 여기서 결정
- **Depends on:** ASR-002, ASR-004
- **Related ADRs:**
  - `adr/app-runtime-model.md` — approved — 런타임 모델 비교 (메시지 구동/스레드/RTE)
  - `adr/task-scheduling-policy.md` — approved — 스케줄링 (비선점 + wcet_ms + overrun 기록)
  - `adr/component-api.md` — approved — 컴포넌트 API (베이스 클래스 + 콜백 + registry)
  - `adr/stub-component-behavior.md` — approved — 스텁 컴포넌트 통신 동작
  - `adr/public-api-contract.md` — approved — 공개 API 시그니처 + TaskContext
  - `adr/task-overrun-policy.md` — approved — 오버런 후속 스케줄링
- **Resolution path:** adr | direct-input
- **Resolution:** C(주기 태스크 + 이벤트 핸들러, RTE 스타일) 채택. 비선점 실행, wcet_ms(기본 0), 주기 초과 시 overrun 이벤트. Component 베이스 클래스(on_periodic/on_message) + ctx.send/log + load(components={...}) 등록. 미등록 시 스텁.
- **Spec:** `spec/sdv-sim-v1.md` — Decisions/Requirements(앱 런타임)
- **Notes:** Spec 승인 (2026-08-12, T-007 통과 — 사용자 구현 지시) → approved 전환.

### ASR-006 — 코어 API 경계 & 다중 아티팩트 구조

- **Category:** Deliverable form & Structure
- **Status:** designed
- **Statement:** 코어 라이브러리와 CLI의 경계, v2/v3(대시보드/데스크톱)가 코어를 재사용할 구조 설계
- **Why it matters:** "모든 형태가 단일 코어 공유"라는 PRD 목표의 실현 수단. API 안정성 = 라이브러리 임베드(테스트 하네스)의 품질 기준
- **Depends on:** ASR-001, ASR-002, ASR-003, ASR-004, ASR-005
- **Related ADRs:**
  - `adr/package-structure.md` — approved — 패키지 구조 비교 (단일/멀티/단일 모듈)
  - `adr/component-api.md` — approved — 컴포넌트/공개 API 계약
  - `adr/cli-output-policy.md` — approved — CLI 출력·오류·종료 코드 (--lang + 0/1/2/3)
  - `adr/public-api-contract.md` — approved — 공개 API 시그니처
  - `adr/cli-io-contract.md` — approved — CLI 출력 채널·플래그
  - `adr/core-yaml-string-input.md` — approved — YAML 문자열 입력 API 추가 (`loads()`, F-11 방향 전환, 2026-08-12)
- **Resolution path:** direct-input | adr
- **Resolution:** A(단일 패키지 + 모듈 경계) 채택. 배포(distribution) 이름: `sdv-sim`, 임포트 이름: `sdv_sim` (Python 관례). 내부 모듈: `sdv_sim/core`(엔진·모델), `sdv_sim/cli`. 공개 API 계약(load/run/events/results)으로 임베드 지원. v2 대시보드는 같은 코어 백엔드 + 별도 프런트엔드. CLI 언어: --lang > env > 로케일. **F-11 (2026-08-12)로 YAML 문자열 입력 API(`loads()`, `load_scenario_yaml()`) 추가 — 기존 `load()`/`load_scenario()` 경로 기반 계약은 하위 호환으로 유지 (core-yaml-string-input Option A 승인). v1 Spec D-15에 `loads()`/`load_scenario_yaml()` 기록 완료 (2026-08-12).**
- **Spec:** `spec/sdv-sim-v1.md` — Decisions/Requirements(API, CLI)
- **Notes:** Spec 승인 (2026-08-12, T-007 통과 — 사용자 구현 지시) → approved 전환. **2026-08-12 F-11 방향 전환으로 reviewing 복귀 → core-yaml-string-input 승인("오케이")으로 designed 재전환.**

### ASR-007 — 검증·자동화 지원

- **Category:** Quality bar
- **Status:** approved
- **Statement:** 자동 검증(assertion) 수단과 CI 친화적 출력(결정적 로그, 종료 코드) 정의
- **Why it matters:** 개발자 대상 검증 도구의 핵심 가치. "무인 실행"을 가능하게 하는 품질 기준
- **Depends on:** ASR-003, ASR-006
- **Related ADRs:**
  - `adr/verification-automation.md` — approved — 검증 방식 비교 (선언형/스트림/결합)
  - `adr/assertion-grammar.md` — approved — assertion 문법 (YAML 선언형 expect 블록)
  - `adr/event-log-schema.md` — approved — 로그 스키마 (단일 JSON, type enum 7종)
  - `adr/cli-output-policy.md` — approved — 종료 코드 (0/1/2/3)
  - `adr/cli-io-contract.md` — approved — CLI 로그 채널·플래그
  - `adr/assertion-evaluation-detail.md` — approved — 평가 규칙 (count·at_ms·실패 메시지)
  - `adr/result-report-schema.md` — approved — assertion 요약 리포트
- **Resolution path:** direct-input
- **Resolution:** C(선언형 assertion + JSON 이벤트 스트림) 채택. expect{event, 속성, at_ms, within_ms, count} 평가(첫 매칭 이벤트 기준). 단일 JSON 로그(schema_version/simulation/events/assertions), (t_ms, seq) 오름차순. CLI 종료 코드 0=pass/1=assertion fail/2=입력 오류/3=내부 오류.
- **Spec:** `spec/sdv-sim-v1.md` — Decisions/Requirements(검증·자동화)
- **Notes:** Spec 승인 (2026-08-12, T-007 통과 — 사용자 구현 지시) → approved 전환.

### ASR-008 — 동일 시각 비-태스크 이벤트 순서

- **Category:** Structure & Organization
- **Status:** designed
- **Statement:** 같은 시각(`t_ms`)에서 비-태스크 이벤트(tx/rx/drop 등)는 태스크 이벤트와 어떤 순서로 처리되는가
- **Why it matters:** 태스크 실행의 부수효과(컴포넌트 `ctx.send` → tx)가 같은 tick의 tx보다 먼저 처리되어야 "원인 → 결과" 관측 순서가 보장됨 — assertion 결과에 영향
- **Depends on:** ASR-002
- **Related ADRs:**
  - `adr/event-ordering-non-task.md` — approved — 비-태스크는 모든 태스크 뒤 (가상 우선순위 2^30)
- **Resolution path:** adr
- **Resolution:** 비-태스크 이벤트는 가상 우선순위 2^30으로 모든 태스크 이벤트 뒤에 처리. 비-태스크 간에는 파일 선언 순서 → seq. (스펙 D-19 인코딩 완료, 2026-08-12)
- **Spec:** `spec/sdv-sim-v1.md` — Decisions/Requirements(시뮬레이션 엔진, D-19)
- **Notes:** 검증(1차)에서 Undocumented ASR U-1로 식별 → 스펙 인코딩(2026-08-12) → ADR 설계 검토로 정식화 (2026-08-12). 사용자 승인("1") → designed.

### ASR-009 — Ethernet 스위치 다중 정의 정책

- **Category:** Structure & Organization
- **Status:** designed
- **Statement:** Ethernet 링크의 `switches`에 2개 이상 정의되면 어떻게 처리하는가
- **Why it matters:** v1은 단일 스위치 모델 — 다중 정의를 무시할지·오류로 거부할지가 정의 파일 UX와 오류 정책에 영향
- **Depends on:** ASR-004
- **Related ADRs:**
  - `adr/ethernet-switch-selection.md` — approved — 첫 번째만 사용 (스키마 오류 없음)
- **Resolution path:** adr
- **Resolution:** `switches` 첫 항목만 큐잉 파라미터로 사용, 나머지는 무시 (스키마 오류 없음). 다중 스위치는 v2+ 후보. (스펙 인코딩 완료, 2026-08-12)
- **Spec:** `spec/sdv-sim-v1.md` — Decisions/Requirements(통신 충실도)
- **Notes:** 검증(1차)에서 Undocumented ASR U-2로 식별 → 스펙 인코딩(2026-08-12) → ADR 설계 검토로 정식화 (2026-08-12). 사용자 승인("1") → designed.

### ASR-010 — 로그 쓰기 실패 종료 코드

- **Category:** Quality bar
- **Status:** designed
- **Statement:** `--log` 파일 쓰기 실패(I/O 오류) 시 CLI 종료 코드는 무엇인가
- **Why it matters:** CI에서 파일 문제와 assertion 실패(1)·내부 오류(3)를 구분해야 하며, 종료 코드 계약의 의미론적 일관성이 필요
- **Depends on:** ASR-006, ASR-007
- **Related ADRs:**
  - `adr/log-write-failure-exit-code.md` — approved — 종료 코드 2 (입력 오류로 분류)
- **Resolution path:** adr
- **Resolution:** 로그 파일 쓰기 실패는 "파일" 범주 오류로 분류해 exit 2. 종료 코드 계약(0/1/2/3) 유지. (스펙 D-16 인코딩 완료, 2026-08-12)
- **Spec:** `spec/sdv-sim-v1.md` — Decisions/Requirements(CLI, D-16)
- **Notes:** 검증(1차)에서 Undocumented ASR U-3로 식별 → 스펙 인코딩(2026-08-12) → ADR 설계 검토로 정식화 (2026-08-12). 사용자 승인("1") → designed.

### ASR-011 — Assertion `event: task` 매칭 범위

- **Category:** Quality bar
- **Status:** designed
- **Statement:** assertion `expect: {event: task}`는 `task_start`와 `task_end` 중 무엇을 매칭하는가
- **Why it matters:** 태스크 생명주기(시작/완료) 검증의 의미를 결정 — count 해석과 검증 표현력에 영향
- **Depends on:** ASR-007
- **Related ADRs:**
  - `adr/assertion-task-event-matching.md` — approved — task_start와 task_end 둘 다 매칭
- **Resolution path:** adr
- **Resolution:** `event: task`는 task_start+task_end 둘 다 매칭하고 `task` 속성으로 특정 태스크 한정. (스펙 D-20 인코딩 완료, 2026-08-12)
- **Spec:** `spec/sdv-sim-v1.md` — Decisions/Requirements(Assertion 평가 규칙, D-20)
- **Notes:** 검증(1차)에서 Undocumented ASR U-4로 식별 → 스펙 인코딩(2026-08-12) → ADR 설계 검토로 정식화 (2026-08-12). 사용자 승인("1") → designed.

### ASR-012 — Assertion count 비교 연산

- **Category:** Quality bar
- **Status:** designed
- **Statement:** assertion `count: n`은 정확히 n건(==)인가, 최소 n건 이상(≥)인가
- **Why it matters:** "최소 발생 보장" vs "정확 개수 검증"의 트레이드오프 — 경계(종료 inclusive)·부수 이벤트 내성과 검증 의도에 영향
- **Depends on:** ASR-007
- **Related ADRs:**
  - `adr/assertion-count-minimum.md` — approved — 최소 n건 이상 (≥)
- **Resolution path:** adr
- **Resolution:** `count: n`은 매칭 이벤트 ≥ n이면 통과 (초과는 실패 아님, 시간 조건과 독립). (스펙 D-20 인코딩 완료, 2026-08-12)
- **Spec:** `spec/sdv-sim-v1.md` — Decisions/Requirements(Assertion 평가 규칙, D-20)
- **Notes:** 검증(1차)에서 Undocumented ASR U-5로 식별 → 스펙 인코딩(2026-08-12) → ADR 설계 검토로 정식화 (2026-08-12). 사용자 승인("1") → designed.

### ASR-013 — Ethernet payload 크기 기준

- **Category:** Structure & Organization
- **Status:** designed
- **Statement:** Ethernet 전송 시간 계산 `bytes = data + 42`에서 payload(`data`)의 크기 기준은 프레임 DLC 바이트인가, 주입 데이터 객체 크기인가
- **Why it matters:** 전송 시간·대역폭 계산의 결정성과 CAN 모델 일관성 — 주입 데이터 내용이 전송 크기에 영향 주는지 여부
- **Depends on:** ASR-004
- **Related ADRs:**
  - `adr/ethernet-payload-basis.md` — approved — payload = 프레임 DLC 바이트 (data 객체 크기와 무관)
- **Resolution path:** adr
- **Resolution:** 전송 크기는 프레임 정의(DLC) 기준 — `bytes = dlc + 42`, 주입 `data` 객체 크기와 무관. (스펙 인코딩 완료, 2026-08-12)
- **Spec:** `spec/sdv-sim-v1.md` — Decisions/Requirements(통신 충실도)
- **Notes:** 검증(1차)에서 Undocumented ASR U-6로 식별 → 스펙 인코딩(2026-08-12) → ADR 설계 검토로 정식화 (2026-08-12). 사용자 승인("1") → designed.

### ASR-014 — 대시보드 기술 스택 (백엔드·프런트엔드)

- **Category:** Constraints & Integration
- **Status:** approved
- **Statement:** 웹 대시보드의 백엔드·프런트엔드 기술 스택 선택
- **Why it matters:** 대시보드 전체 구조 결정. v1(Python 3.11+, `sdv-sim` 단일 패키지)과의 정합, 프런트엔드 개발 생산성·시각화 능력·패키징 비용에 영향
- **Depends on:** ASR-001, ASR-006
- **Related ADRs:** adr/dashboard-tech-stack.md (approved, 2026-08-12)
- **Resolution path:** adr (추천 — 스택 비교 트레이드오프 큼)
- **Resolution:** FastAPI(백엔드) + React/TypeScript + Vite(프런트엔드) — 사용자 승인 (2026-08-12). Pydantic 네이티브 재사용, 커스텀 캔버스·이벤트 스트리밍 자유도 확보.
- **Spec:** spec/sdv-sim-v2.md
- **Notes:** v2 (2026-08-12) — PRD v2 "동작 방식/제공 형태"에서 파생. **2026-08-12 v2 Spec 승인 (T-007 done) → approved 전환.**

### ASR-015 — 데이터 흐름·리플레이 모델

- **Category:** Structure & Organization
- **Status:** approved
- **Statement:** 대시보드가 시뮬레이션 데이터를 얻고 재생하는 방식 — v1 코어 백엔드 임베드 실행 vs JSON 이벤트 로그 파일 로드, 구조 뷰 오버레이 리플레이(재생/일시정지/탐색)의 의미론
- **Why it matters:** 코어와 대시보드의 결합 방식(동일 프로세스 vs 로그 재사용), 이벤트 전달(전체 vs 청크), 리플레이 UX·성능을 결정
- **Depends on:** ASR-002, ASR-014
- **Related ADRs:**
  - `adr/dashboard-data-flow-replay.md` — approved — 코어 임베드 실행 + 일괄 JSON 전달 (2026-08-12)
  - `adr/dashboard-run-path.md` — **superseded** — v1 무변경 결정 폐기 (F-11 방향 전환, 2026-08-12) → `core-yaml-string-input` 교체
  - `adr/dashboard-session-lifecycle.md` — approved — 세션 = `{events, report, duration_ms, source, 스냅샷}`, 편집 시 무효화, last-write-wins (2026-08-12)
  - `adr/dashboard-load-log-report.md` — approved — load-log 리포트 파생 규칙: 파생 가능 항목만 + arch 연동 시 전체 (2026-08-12)
  - `adr/core-yaml-string-input.md` — approved — YAML 문자열 입력 API로 run 경로 재설계 (`loads()`, F-11, 2026-08-12)
  - `adr/dashboard-browser-file-access.md` — approved — load-log 경로 입력 방식 변경 (하이브리드, F-11, 2026-08-12)
- **Resolution path:** adr (추천 — 결합·전달 방식 트레이드오프)
- **Resolution:** 코어 임베드 실행 + 일괄 JSON 전달. **F-11 (2026-08-12) 후 run 경로 = v1 공개 `loads(arch_yaml, scenario_yaml)` 사용 (파일 경로 불필요, core-yaml-string-input Option A)** — 서버는 브라우저가 보낸 YAML 문자열을 그대로 v1 API로 전달. 파일은 브라우저가 직접 관리(FS Access API 또는 업로드/다운로드 — dashboard-browser-file-access Option C), 서버 파일 API·샌드박스 없음. 로그 로드도 브라우저가 JSON 내용을 `POST /api/load-log`로 전송. 타임스탬프 정렬 전체 이벤트를 `GET /api/events`로 반환, 프런트엔드 로컬 재생/시크. 세션·리포트 파생 규칙은 session-lifecycle/load-log-report ADR에 따라 spec 인코딩. SSE/WebSocket 비목표. 사용자 승인 (2026-08-12).
- **Spec:** spec/sdv-sim-v2.md
- **Notes:** v2 (2026-08-12) — PRD v2 "시뮬레이션(구조 뷰 오버레이)"에서 파생. spec review C-1·M-1·M-4 해소로 ADR 3건 추가 승인 (2026-08-12) — reviewing → designed. **2026-08-12 F-11 방향 전환으로 reviewing 복귀 (run-path superseded) → 신규 ADR 2건 승인("오케이")으로 designed 재전환.** **2026-08-12 v2 Spec 승인 (T-007 done) → approved 전환.** **2026-08-13 T-009 검증 U-1 인코딩 (사용자 승인) — 세션 무효화 신호 = `POST /api/validate` 호출 명시 (M-4 절·API 절·Requirements 절에 반영), E15 partial(무효화 500ms 지연) 수용.** **2026-08-13 T-024 재설계 (사용자 승인, 버그 수정) — U-1 폐기: validate는 순수 검증으로 전환하고, 세션 무효화는 프런트 로컬 상태(`SessionMeta.invalidated` — 편집 시작 시 세팅)로 이동. 이유: 편집 없이도 validate가 불리는 경로(마운트/재마운트 디바운스)에서 run 후 세션이 죽는 버그(리포트 409) 발생. 스펙 M-4 절·API 절·Requirements 절 재반영 완료.**

### ASR-016 — 구조 뷰 렌더링·성능

- **Category:** Structure & Organization
- **Status:** approved
- **Statement:** 토폴로지 다이어그램 렌더링 기술(SVG/Canvas/그래프 라이브러리)과 대용량 이벤트(≤100만, v1 성능 목표) 리플레이 시 렌더링 성능 기준
- **Why it matters:** 구조 뷰가 기본 화면 — 렌더링 기술이 클릭·애니메이션 인터랙션 품질과 대용량 이벤트 처리 가능 여부를 결정
- **Depends on:** ASR-014, ASR-015
- **Related ADRs:**
  - `adr/topology-rendering-performance.md` — approved — SVG+React, D3 레이아웃 보조, 성능 기준 (2026-08-12)
  - `adr/dashboard-replay-animation-timing.md` — approved — 리플레이 애니메이션 시간 모델: 물리 재생(tx_ms) + load-log 고정 폴백 (2026-08-12)
  - `adr/dashboard-seek-state-indexing.md` — approved — 시크 상태 계산: 주기적 스냅샷 + 잔여 ≤ K 재적용 (2026-08-12)
  - `adr/dashboard-layout-determinism.md` — approved — 자동 레이아웃 결정성 요구 (2026-08-12)
  - `adr/dashboard-layout-placement-rule.md` — approved — 자동 레이아웃 배치 규칙: 타입 밴드 (Option A, 사용자 승인 2026-08-12, spec review F-6 해소)
- **Resolution path:** adr (추천) 또는 direct-input
- **Resolution:** SVG + React 커스텀 (D3 레이아웃 보조). 성능 기준 — 노드 ≤200/링크 ≤500에서 60fps, ≤100만 이벤트 로드·정렬 ≤ 2s, 시크 반영 ≤ 100ms. 애니메이션 시간·시크·레이아웃 결정성·배치 규칙은 상기 ADR 4건에 따라 spec 인코딩 (배치 규칙 = 타입 밴드, F-6 해소). 사용자 위임 계속 진행 (2026-08-12).
- **Spec:** spec/sdv-sim-v2.md
- **Notes:** v2 (2026-08-12) — PRD v2 "구조 뷰(기본 화면)"·성공 기준 2에서 파생. spec review M-2·M-3·M-5 해소로 ADR 3건 추가 승인 (2026-08-12). **2026-08-12 v2 Spec 승인 (T-007 done) → approved 전환.**

### ASR-017 — 파일시스템 접근·보안 경계

- **Category:** Constraints
- **Status:** approved
- **Statement:** 대시보드가 로컬 YAML/JSON 파일을 읽고 쓰는 방식과 보안 경계 — 서버-FS 샌드박스(`--root`) vs 브라우저 로컬 파일 직접 접근
- **Why it matters:** "로컬 저장"(PRD)의 실현 수단. F-11 방향 전환(브라우저 로컬 파일 직접 사용)으로 **서버 파일 API·샌드박스 제거** — 파일 경계가 브라우저 권한으로 대체됨
- **Depends on:** ASR-014, ASR-015
- **Related ADRs:**
  - `adr/dashboard-browser-file-access.md` — approved — 브라우저 로컬 파일 접근 방식: **하이브리드** (FS Access API 우선 + 업로드/다운로드 폴백, F-11, 2026-08-12)
- **Resolution path:** direct-input | adr
- **Resolution:** **브라우저 파일 권한 경계 (F-11, 2026-08-12 승인)** — 서버 파일 API·`--root` 샌드박스 **제거**. 파일 읽기/쓰기는 브라우저가 직접: Chrome/Edge는 File System Access API(같은 파일 저장, 사용자 권한 프롬프트), Firefox/Safari는 업로드(`<input type=file>`)·다운로드(Blob) 폴백. 서버는 파일 내용(문자열)만 수신 — 경로 검증·traversal 문제 소멸. 파일 삭제·이름 변경 미지원 유지 (PRD).
- **Spec:** spec/sdv-sim-v2.md
- **Notes:** v2 (2026-08-12) — PRD v2 "편집·파일 관리"·제약(파일시스템 접근 범위 제한)에서 파생. **2026-08-12 F-11 방향 전환으로 reviewing 복귀 → dashboard-browser-file-access 승인("오케이")으로 designed 재전환.** **2026-08-12 v2 Spec 승인 (T-007 done) → approved 전환.**

### ASR-018 — 편집·검증 피드백

- **Category:** Quality bar
- **Status:** approved
- **Statement:** YAML 텍스트 편집 UX와 스키마 검증 피드백 방식 — 검증 시점(저장 시/입력 중), 오류 표시 위치, v1 Pydantic 스키마 재사용 전략(서버 API 검증 vs 프런트엔드 포팅)
- **Why it matters:** "편집 → 실행" 흐름의 품질 기준. 검증 지연·피드백 UX가 사용자 경험과 개발 비용을 좌우
- **Depends on:** ASR-003(v1 정의 형식), ASR-017
- **Related ADRs:** adr/editor-validation-feedback.md (approved, 2026-08-12)
- **Resolution path:** adr (추천 — 검증 위치 트레이드오프) 또는 direct-input
- **Resolution:** 서버 Pydantic 검증 (v1 스키마 그대로 진실 소스) + 디바운스(500ms) 자동 검증 + 저장/실행 시 최종 검증. 오류는 줄 단위 인라인 표시. 유효 파싱 시에만 다이어그램 동기화. 프런트엔드 스키마 포팅 비목표. 사용자 위임 계속 진행 (2026-08-12).
- **Spec:** spec/sdv-sim-v2.md
- **Notes:** v2 (2026-08-12) — PRD v2 "편집·파일 관리"·성공 기준 6에서 파생. **2026-08-12 v2 Spec 승인 (T-007 done) → approved 전환.**

### ASR-019 — 패키지 통합·서버 명령 (serve)

- **Category:** Deliverable form
- **Status:** designed
- **Statement:** 대시보드를 `sdv-sim` 패키지에 통합하는 방식 — `serve` 명령 형태, 프런트엔드 정적 자산 패키징(wheel 포함 여부), 서버 수명주기·포트 정책
- **Why it matters:** 설치·실행 UX 결정. v1 단일 패키지 구조(ASR-006)의 확장 방식
- **Depends on:** ASR-006, ASR-014
- **Related ADRs:**
  - `adr/serve-packaging.md` — approved — 단일 프로세스 + 패키지 내부 정적 자산 (2026-08-12)
  - `adr/dashboard-browser-file-access.md` — approved — `--root` 샌드박스 제거 영향 (F-11, 2026-08-12)
  - `adr/serve-network-binding.md` — approved — 외부 접근·바인딩 정책 (2026-08-13, 사용자 승인 — `--host` 옵션 추가, 기본 127.0.0.1)
- **Resolution path:** adr (추천) 또는 direct-input
- **Resolution:** `sdv-sim serve` = 단일 프로세스 — FastAPI 앱 + 패키지 내부 정적 자산(`sdv_sim/server/static/`, wheel 포함). 개발 중 `--dev` 모드로 Vite dev server(HMR) 프록시. **F-11 (2026-08-12)로 `--root` 옵션 제거** — 파일 접근이 브라우저 측으로 이동(dashboard-browser-file-access). 옵션 세트: `--port`/`--lang`/`--dev`. **2026-08-13 `--host` 옵션 추가 (serve-network-binding 승인)** — 기본 `127.0.0.1`(루프백, 안전 기본), `--host 0.0.0.0`으로 외부 접근 가능. 사용자 승인 (2026-08-12).
- **Spec:** spec/sdv-sim-v2.md
- **Notes:** v2 (2026-08-12) — PRD v2 "제공 형태"(예: `sdv-sim serve`)에서 파생. **2026-08-12 F-11로 --root 제거 반영 (dashboard-browser-file-access).** **2026-08-12 v2 Spec 승인 (T-007 done) → approved 전환.** **2026-08-13 serve-network-binding 승인("1") → designed 재전환 (외부 접근 허용 결정 — 스펙 반영 필요).**

### ASR-020 — UI 언어 지원 (ko/en)

- **Category:** Constraints
- **Status:** approved
- **Statement:** 대시보드 UI의 언어 지원 방식 — v1 i18n 패턴(ko/en, `--lang`/env/로케일 우선순위)을 프런트엔드에 적용하는 메커니즘
- **Why it matters:** PRD 제약("문서·CLI·대시보드 UI 출력은 한국어/영어 지원 구조"). v1은 Python `i18n.py` — 프런트엔드용 i18n 메커니즘이 별도 필요
- **Depends on:** ASR-014
- **Related ADRs:** — (direct-input 해소)
- **Resolution path:** direct-input (권장 — v1 패턴을 프런트엔드에 대응)
- **Resolution:** 프런트엔드 i18n 메시지 카탈로그(ko/en, React 대상) — v1 우선순위 패턴(--lang/env/브라우저 로케일) 대응. UI 문자열 하드코딩 금지, 카탈로그 외부화. 언어 선택 UI 포함. 사용자 위임 계속 진행 (2026-08-12).
- **Spec:** spec/sdv-sim-v2.md
- **Notes:** v2 (2026-08-12) — PRD v2 제약에서 파생. **2026-08-12 v2 Spec 승인 (T-007 done) → approved 전환.**
