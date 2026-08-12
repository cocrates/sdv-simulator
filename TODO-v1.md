# TODO: SDV Simulator (Software Defined Vehicle)

> **Project root:** `sdv-simulator`
> **Updated:** 2026-08-12

## Snapshot

| Done | In progress | Pending | Blocked | Skipped |
|------|-------------|---------|---------|---------|
| 22   | 0           | 1       | 0       | 0       |

**Current focus:** — (v1 전체 완료)
**Recommended next:** T-017 — v2 스테이징(대시보드 등) 범위 논의 — 사용자 요청 시

## Active

- [x] **T-016** `done` — 재검증 게이트 (스펙 수정 + i18n 후 재검증 완료, 사용자 승인)
  - Phase: Verification (feedback loop)
  - Artifact: `sdv-simulator/verification/sdv-sim-v1.md`
  - Depends: T-009
  - Notes: 2026-08-12 Deviation 1·2 해소. 스펙 수정(공식 예시 + U-1~U-6 인코딩), i18n.py 신설 + SdvSimInputError code/params 구조화 + CLI 연동, 테스트 63→78건, mypy 13 files strict 통과. 재검증 결과 86 pass / 0 fail / 0 partial. T-018에서 U-1~U-6 ADR 설계 검토 승인 → **T-016 완료 처리**, T-009 done.

## Backlog

- [x] **T-018** `done` — Undocumented ASR(U-1~U-6) ADR 설계 검토 (ADR 6건 approved)
  - Phase: Verification feedback loop (design review)
  - Artifact: `sdv-simulator/adr/{event-ordering-non-task,ethernet-switch-selection,log-write-failure-exit-code,assertion-task-event-matching,assertion-count-minimum,ethernet-payload-basis}.md`
  - Depends: T-016
  - Notes: 2026-08-12 ADR 6건 작성 → 사용자 전체 승인("1", 전부 Option A — 스펙과 정합) → Status approved + ASR-008~013 designed 전환 + Resolution 기록. 스펙 변경 불필요(이미 인코딩됨).

- [ ] **T-017** `pending` — (후속 스테이징 대기) v2 대시보드 등 범위 결정
  - Phase: cross-cutting
  - Artifact: —
  - Depends: T-016
  - Notes: 사용자가 원할 때만. v1 완료 후 논의.

- [x] **T-019** `done` — README.md 작성 (과제 내용 · 실행/테스트 · PyPI 릴리스)
  - Phase: documentation
  - Artifact: `sdv-simulator/README.md`
  - Depends: T-016
  - Notes: 2026-08-12 완료. 사용자 승인(정의+구조 통합 게이트, "README.md 생성해줘"). 모든 수록 명령 실검증: pytest 78 passed, mypy 13 files strict, demo run exit 0, `uv build` → dist/sdv_sim-0.1.0(.whl+.tar.gz). uv는 ~/.bashrc PATH(line 120, `.local/bin`) — 비대화형 셸에서는 조기 return(6~9행)이라 수동 PATH export 필요.

- [x] **T-020** `done` — Gate: README 승인
  - Phase: documentation
  - Artifact: `sdv-simulator/README.md`
  - Depends: T-019
  - Notes: 2026-08-12 사용자 명시 승인("OK") — rev 2(4장 샘플 예제 포함, T-023) 기준.

- [x] **T-021** `done` — samples/ 샘플 작성 (기본 + 차량, 전 기능 검증)
  - Phase: documentation (samples)
  - Artifact: `sdv-simulator/samples/{basic,vehicle}/`
  - Depends: T-016
  - Notes: 2026-08-12 사용자 설계 승인(옵션 2 — components.py 포함 5개 파일). 모든 기능: CAN 중재·Ethernet FIFO·게이트웨이(remap/ID범위/delay)·오버런·테일드롭·supersede·주입·assertion 7종. 검증 완료: basic exit 0 (assertion 5건 pass), vehicle exit 0 (assertion 9건 pass, drop 2건 gear_state t=500/502, overrun 5건 diag wcet 110>period 100, supersede 12건), components.py demo exit 0 (log 11건 + 주입 data 전달), `--lang en` 출력 확인.

- [x] **T-022** `done` — Gate: samples/ 승인
  - Phase: documentation (samples)
  - Artifact: `sdv-simulator/samples/`
  - Depends: T-021
  - Notes: 2026-08-12 사용자 명시 승인("OK"). 실행 검증 완료(basic assertion 5건 / vehicle 9건 / components.py log 11건 — 전부 exit 0, drop 2 + overrun 5 + supersede 12 확인).

- [x] **T-023** `done` — README samples 섹션 추가 (README rev 2)
  - Phase: documentation
  - Artifact: `sdv-simulator/README.md`, `sdv-simulator/samples/vehicle/scenario.yaml`
  - Depends: T-021
  - Notes: 2026-08-12 사용자 지시("README.md에 samples에 관한 설명/실행 방법을 추가해줘"). 4장 샘플 예제 신설(4.1 기본 / 4.2 차량 / 4.3 커스텀 컴포넌트 / 4.4 구조) + 기존 4~6장 → 5~7장 재번호 + 프로젝트 구조 트리에 samples/ 반영. vehicle scenario의 stale 주석(queue_depth 8→4) 수정. 명령 3종 재실검증(basic assertion 5건 / vehicle 9건 / components.py log 11건 — 전부 exit 0). T-020 게이트가 갱신된 README 전체를 커버.

- [x] **T-009** `done` — spec-driven-verification으로 검증 (1차)
  - Phase: Verification
  - Artifact: `sdv-simulator/verification/sdv-sim-v1.md`
  - Depends: T-008
  - Notes: 2026-08-12 1차 리포트 (78 pass / 1 fail / 2 partial) → 사용자 승인("잘못된 스펙의 공식 예시 수정 + 오류 메시지 ko/en")으로 수정 루프 진입 → T-016에서 재검증 완료 후 done 처리.

- [x] **T-008** `done` — Step 5: 시뮬레이터 생성
  - Phase: Step 5 (Generation)
  - Artifact: `sdv-simulator/` (sdv_sim/, pyproject.toml, .venv, tests/)
  - Depends: T-007 ✓
  - Notes: 2026-08-12 생성 완료 — pytest 63 passed, mypy strict 통과. `.venv`은 gitignore 대상이라 재생성 필요(uv sync). 2026-08-12 T-009 진행 시점 done 처리.

- [x] **T-001** `done` — Step 1: PRD 작성
  - Phase: Step 1 (PRD)
  - Artifact: `sdv-simulator/spec/PRD.md`
  - Depends: —
  - Notes: 2026-08-12 작성

- [x] **T-002** `done` — Gate: PRD 승인
  - Phase: Step 1 (PRD)
  - Artifact: —
  - Depends: T-001
  - Notes: 2026-08-12 사용자 승인

- [x] **T-003** `done` — Step 2: ASR 식별 및 `spec/ASR.md` 등록
  - Phase: Step 2 (ASR)
  - Artifact: `sdv-simulator/spec/ASR.md`
  - Depends: T-002
  - Notes: ASR-001~007 등록, 의존성 순서 제시

- [x] **T-004** `done` — Step 3: ASR 검토 (Direct Input 또는 ADR)
  - Phase: Step 3 (ASR Review)
  - Artifact: `sdv-simulator/adr/*.md`
  - Depends: T-003
  - Notes: ASR-001~007 모두 designed (ADR 2건, Direct Input 5건)

- [x] **T-005** `done` — Gate: ADR 승인
  - Phase: Step 3 (ADR)
  - Artifact: —
  - Depends: T-004
  - Notes: ADR 2건 승인 (언어/엔진) — 이후 사후 ADR 5건 추가 승인 처리

- [x] **T-006** `done` — Step 4: Spec 작성 (spec-writing 위임)
  - Phase: Step 4 (Spec)
  - Artifact: `sdv-simulator/spec/sdv-sim-v1.md`
  - Depends: T-005
  - Notes: ASR-001~007 resolution 인코딩 완료. ASR.md 중복 항목 정리.

- [x] **T-007** `done` — Gate: Spec 승인
  - Phase: Step 4 (Spec)
  - Artifact: `sdv-simulator/spec/sdv-sim-v1.md`
  - Depends: T-011 ✓, T-012 ✓, T-015 ✓
  - Notes: 2026-08-12 사용자 "구현해줘" 지시 = 승인 신호로 간주. Gate 5 재검토 2회 통과(아키텍처/구현 SSOT 충분성 확인). 승인 후 ASR-001~007 → approved 전환, T-008 시작.

- [x] **T-010** `done` — Direct Input 결정 5건 사후 ADR 문서화
  - Phase: cross-cutting (audit trail)
  - Artifact: `sdv-simulator/adr/{definition-file-format,communication-fidelity-level,app-runtime-model,package-structure,verification-automation}.md`
  - Depends: —
  - Notes: 2026-08-12 작성. ASR-003~007 관련 ADR로 연결.

- [x] **T-011** `done` — 상세 설계 ADR 작성·승인 (D-01~D-11)
  - Phase: Step 4 보강 (상세 설계 검토)
  - Artifact: `sdv-simulator/adr/{simulation-time-model,definition-schema-structure,assertion-grammar,event-log-schema,can-fidelity-model,ethernet-fidelity-model,gateway-routing-rules,task-scheduling-policy,component-api,cli-output-policy,performance-targets}.md`
  - Depends: T-006
  - Notes: Gate 5 갭 14건 → 설계 결정 concern 11건. 2026-08-12 전부 작성·승인 완료 (Decision/Approved 기록).

- [x] **T-012** `done` — Step 4 보강: 상세 설계 ADR 결정 Spec 인코딩 (spec-writing)
  - Phase: Step 4 (Spec)
  - Artifact: `sdv-simulator/spec/sdv-sim-v1.md`, `sdv-simulator/spec/ASR.md`
  - Depends: T-011
  - Notes: 승인 11건 결정 deep-copy로 Spec에 인코딩 (시간 모델, 스키마 2계층, assertion, 로그 스키마, CAN/Eth 모델, 게이트웨이, 스케줄링, 컴포넌트 API, CLI 정책, 성능 목표). ASR.md → designed 상태 유지 (Spec 승인 후 approved 전환).

- [x] **T-013** `done` — Step 4 보강: 2차 상세 설계 ADR 작성·검토 (D-12~D-21, 10건)
  - Phase: Step 4 보강 (상세 설계 검토 2차)
  - Artifact: `sdv-simulator/adr/{definition-field-schema,communication-event-semantics,stub-component-behavior,public-api-contract,cli-io-contract,task-overrun-policy,frame-queue-overflow-policy,event-ordering-boundary,assertion-evaluation-detail,result-report-schema}.md`
  - Depends: —
  - Notes: Gate 5 재검토(그룹 A 5건 + 그룹 B 6건 + C-14) → ADR concern 10건으로 재구성, 2026-08-12 전부 작성.

- [x] **T-014** `done` — Gate: 2차 상세 설계 ADR 승인 (D-12~D-21)
  - Phase: Step 4 보강 (상세 설계 검토 2차)
  - Artifact: —
  - Depends: T-013
  - Notes: 2026-08-12 사용자 승인 (각 ADR `Approved: 2026-08-12, user confirmed` 기록 확인). Status → approved.

- [x] **T-015** `done` — Step 4 보강: 2차 ADR 결정 Spec 인코딩 (spec-writing)
  - Phase: Step 4 (Spec)
  - Artifact: `sdv-simulator/spec/sdv-sim-v1.md`, `sdv-simulator/spec/ASR.md`
  - Depends: T-014
  - Notes: D-12~D-21 결정 10건을 Spec에 deep-copy 인코딩 완료 (2026-08-12). Context·Decisions 9개 하위 섹션·Requirements·Out of Scope·Related 갱신.

## Notes

- 프로젝트 루트: `sdv-simulator/` (워크스페이스 Type 2 — peer projects)
- 워크플로우: spec-driven-generation (Step 0 → 1 → 2 → 3 → 4 → 5)
- 2026-08-12: 세션 시작. Step 0에서 Gate 1 실패(PRD 없음) → Step 1로 진입.
- **범위 결정**: 시뮬레이션 대상 = (A) 차량 소프트웨어 플랫폼 (E/E 아키텍처, HPC/ECU, 차량 내 통신, OTA, 앱 런타임). 대상 청중 = (a) 차량 SW 개발자/아키텍트 (개발·검증 도구). 아티팩트 형태 = 전부(CLI, 라이브러리, 웹 대시보드, 데스크톱) — 스테이징 승인됨: 1차(코어+CLI) → 2차(대시보드) → 3차(데스크톱).
- **ASR 확정 요약**: ASR-001 Python(ADR) / ASR-002 DES 하이브리드(ADR) / ASR-003 YAML(ADR 사후 문서화) / ASR-004 L2 통신(ADR 사후 문서화) / ASR-005 RTE 스타일(ADR 사후 문서화) / ASR-006 단일 패키지 `sdv-sim`(ADR 사후 문서화) / ASR-007 선언형 assertion + JSON 스트림(ADR 사후 문서화). **현재 상태: 전부 `designed`, Spec 승인(T-007) 후 `approved` 전환**
- **ADR 목록**: `adr/` 아래 18개 — 7개 상위(전부 승인): language-tech-stack, simulation-engine-model, definition-file-format, communication-fidelity-level, app-runtime-model, package-structure, verification-automation + 11개 상세 설계(전부 승인): simulation-time-model, definition-schema-structure, assertion-grammar, event-log-schema, can-fidelity-model, ethernet-fidelity-model, gateway-routing-rules, task-scheduling-policy, component-api, cli-output-policy, performance-targets
- **Gate 5 재검토 (2026-08-12, T-012 이후)**: spec-driven-verification 스킬로 `spec/sdv-sim-v1.md`를 PRD·ASR·ADR 11건 대비 항목별 검토.
  - 판정: **아키텍처 SSOT = 충분** (ASR-001~007 resolution + 상세 설계 ADR 결정이 Decisions/Requirements/Constraints에 인코딩, Out of Scope 정합) / **구현 SSOT = 불충분** (스펙만으로 구현 시 발명 필연 지점 존재)
  - 미진 설계 **그룹 A (차단성 5건)**: ① 필드-레벨 YAML 스키마(architecture/scenario 전체 필드 트리 + scenario `messages` 주입 형식) ② 통신 이벤트 의미론(CAN rx 범위, Ethernet 노드↔스위치 흐름, 게이트웨이 라우팅 이벤트 기록·다중 홉, 주입 메시지→tx 유발 여부) ③ 스텁 컴포넌트 동작(주기 송신 vs 주입 반응) ④ 공개 API 시그니처(load/load_scenario/run 인자·반환, 이벤트 스트림 형태, TaskContext 메서드) ⑤ CLI 출력 채널·플래그(JSON 로그 출력 위치, 요약 포맷)
  - 미진 설계 **그룹 B (정책·엣지 6건)**: overrun 후 주기 처리, CAN 큐 대기 중 period 초과, 같은 시각·같은 우선순위 순서(컴포넌트 정의 순서), assertion 평가 세부(count 대상·at_ms 생략 의미 인코딩 누락·실패 메시지), 종료 경계(t==duration_ms 포함 여부), 버스 부하 리포트 항목·drop 집계
  - 미진 설계 **그룹 C (경미 3건)**: 성능 판정 벤치마크 시나리오, schema_version 정책, i18n 오류 메시지 범위
  - 근거: ADR 11건의 Downstream open 체크박스 ~11개 중 v1 관련 ~8건 미해소 + assertion-grammar의 `at_ms` 생략 의미(시간 무관)가 스펙 미인코딩(SSOT 위반 사례)
  - 권고: T-007 승인 전 그룹 A 해소(스펙에 스키마 예시·이벤트 의미론·API/CLI 계약 인코딩) — 선택지: ① spec-writing 상세화(권장) ② 신규 ADR 5~6건 ③ 범위 축소 ④ 경미 항목 명시적 기본값 승격
- **2차 상세 설계 ADR 배치 (2026-08-12, T-013)**: 사용자 지시("미진한 내용에 대해 ADR 생성") → 미진 항목(그룹 A 5건 + B 6건 + C-14)을 ADR concern 10건으로 재구성, 전부 `proposed` 작성:
  - D-12 definition-field-schema (ASR-003) / D-13 communication-event-semantics (ASR-002·004) / D-14 stub-component-behavior (ASR-005) / D-15 public-api-contract (ASR-005·006) / D-16 cli-io-contract (ASR-006·007) / D-17 task-overrun-policy (ASR-005) / D-18 frame-queue-overflow-policy (ASR-004) / D-19 event-ordering-boundary (ASR-002) / D-20 assertion-evaluation-detail (ASR-007) / D-21 result-report-schema (ASR-002·004·007)
  - Direct Input(ADR 제외): C-12 벤치마크(구현 태스크), C-13 schema_version(스펙에 이미 `schema_version: 1`)
  - ASR.md 동기화: ASR-002~007 → `reviewing` 전환, Related ADRs에 신규 10건(proposed) 연결, Dependency Order에 2차 배치 추가
  - 추천 옵션(전부 A): 완전 스키마+예시 / 수신자 매핑 rx+규칙 체인 / 스텁 수신자 전용 / 경로+결과 객체 / --log 파일+요약 stdout / 절대 주기+스킵 / 최신 교체 / 정의 순서+inclusive / 전체 count+시간 무관 / 구조화 리포트
- **2차 ADR 승인 확인 (2026-08-12, T-014)**: D-12~D-21 10건 전부 `Approved: 2026-08-12, user confirmed` — Status approved (파일 검증). ASR-002~007 → designed 전환 완료.
- **2차 ADR Spec 인코딩 완료 (2026-08-12, T-015)**: spec/sdv-sim-v1.md에 D-12~D-21 결정 deep-copy 인코딩 완료 — Context(21건), Decisions 신규 하위 섹션 9개(스키마/이벤트 의미론/스텁/API/CLI/오버런/큐/순서·종료/assertion/리포트), Requirements·Out of Scope·Related 갱신. 다음: T-007 Gate 재검토·승인.
- **T-007 승인 + Step 5 시작 (2026-08-12)**: 사용자 지시("1. src/ 폴더에 구현해줘. 2. uv로 venv를 생성하고 개발해줘.") = Spec 승인 신호로 간주. Gate 5 2회 통과 확인 → T-007 done, ASR-001~007 → approved 전환, T-008(in_progress) 시작. 환경: uv 0.11.3, Python 3.12.3 (Spec 요구 3.11+ 충족).
- **생성 시 해석 결정 (2026-08-12, 조용한 발명 방지용 명시)**: ① tx 이벤트 시각 = 실제 전송 시작 시각 (D-18 "최종 전송된 인스턴스만" 정합) ② Ethernet payload = 프레임 dlc 바이트 (bytes = dlc + 42) ③ assertion count = "최소 n건"(≥, 공식 예시 정합) ④ 태스크 스케줄링 = 자체 오버런에 덮인 인스턴스만 스킵(노드 자원 경쟁 미모델 — v1 제외 정합) ⑤ on_message 핸들러 = 시간 진행 없음(D-17 downstream open 기본값 명시화). spec-driven-verification(T-009)에서 재확인 예정.
- **T-009 검증 완료 (2026-08-12)**: spec-driven-verification 수행 — `verification/sdv-sim-v1.md` 작성 (78 pass / 1 fail / 2 partial).
  - 실행 확인: pytest 63 passed, mypy strict 통과. `.venv` 재생성 필요(uv sync --extra dev).
  - **Deviation 1 (Major, 스펙 결함)**: D-12 공식 예시가 자기 의미론과 비정합 — `door_ecu` 노드 미정의 → exit 2, assertion `at_ms:5`가 주기 t=0 tx에 먼저 매칭 → exit 1. 코드가 아니라 **스펙 수정 대상**.
  - **Deviation 2 (Minor)**: 오류 메시지 카테고리 라벨만 로컬라이즈, Pydantic/YAML 상세는 영어 (D-16 partial).
  - **Undocumented ASR U-1~U-6**: U-1 같은 tick 비-태스크 이벤트는 태스크 뒤(MAX_PRIO) / U-2 스위치 다중 정의 시 첫 번째만 사용 / U-3 로그 쓰기 실패 = exit 2 / U-4 `event: task` = start+end 둘 다 / U-5 count ≥ (최소) / U-6 Ethernet payload = DLC 바이트. U-1·U-5·U-6은 생성 시 해석 ③⑤와 정합.
  - **다음 액션 게이트**: 사용자 리뷰 → ① spec-writing으로 예시·문구 수정(권장) → 재검증, 또는 수용 결정.
- **T-016 수정 루프 완료 (2026-08-12)**: 사용자 승인("1" = 권장안) 후 Deviation 1·2 해소, 재검증 86 pass / 0 fail / 0 partial.
  - **스펙 수정 (spec-writing)**: 공식 예시 `door_ecu` 노드 추가 + assertion `{event: tx, frame: door_cmd, link: can1, at_ms: 0, count: 12}`. U-1~U-6 전부 스펙 인코딩 (D-19 비-태스크 순서 / U-2 첫 스위치 / U-3 로그 실패 exit 2 / U-4 task=start+end / U-5 count ≥ / U-6 bytes=dlc+42).
  - **i18n 구현**: `sdv_sim/i18n.py` 신설(ko/en 카탈로그 + `tr()`), `SdvSimInputError` code+params 구조화 + `format(lang)`, engine/cli 오류 지점 연동. 로컬라이즈 경계 = 카테고리·공통 메시지 ko/en, 내부 예외 상세 원문 유지 (사용자 승인).
  - **검증**: pytest 63→78 (test_i18n.py 15건 신규), mypy 12→13 files strict 통과. 공식 예시 exit 0, `--lang ko|en` 출력 확인, U-1~U-4 실행 확인.
  - **리포트 갱신**: `verification/sdv-sim-v1.md` 재검증 버전 작성 (86 pass, Deviations 해소 표기, U-1~U-6 인코딩 위치 기록).
  - **다음**: T-016 사용자 승인 게이트 → T-009 done → 세션 종료 또는 v2 스테이징 논의.
- **T-018 ADR 설계 검토 완료 (2026-08-12)**: 사용자 지시("Undocumented ASR에 대해서 설계 검토가 필요한 내용을 ADR로 작성") → 검증에서 식별된 U-1~U-6을 ADR 6건으로 정식화.
  - **ADR 6건 작성·승인**: event-ordering-non-task(비-태스크는 태스크 뒤) / ethernet-switch-selection(첫 스위치만, 오류 없음) / log-write-failure-exit-code(exit 2) / assertion-task-event-matching(start+end 둘 다) / assertion-count-minimum(≥ 최소) / ethernet-payload-basis(DLC 바이트). 전부 Option A = 스펙 인코딩 내용과 정합 → 사용자 전체 승인("1").
  - **ASR.md 동기화**: ASR-008~013 신규 등록 → designed 전환 + Resolution 기록, Related ADRs(approved) 연결, Dependency Order에 3차 배치 추가.
  - **스펙 변경 없음**: 결정 6건은 이미 `sdv-sim-v1.md`에 인코딩되어 있고 재검증(86 pass) 통과 상태 — ADR은 감사 추적(사후 설계 검토) 완성 목적.
  - **다음**: T-016·T-018 done, T-009 done 처리 → v1 마무리 확인 또는 v2 스테이징 논의.
- **samples/ 검증 완료 (2026-08-12, T-021)**: 옵션 2 설계(사용자 승인)대로 `samples/basic/`·`samples/vehicle/` + `components.py` 작성, 전 항목 실행 검증 완료.
  - **basic** (`samples/basic/`): 공식 예시 확장 — body_ecu(door_ctrl) + door_ecu(door_act stub), can1. duration 100, 주입 t=5 door_cmd {state: open}, assertion 5건. **exit 0** (tx 12/rx 11/state tx 10/rx 10/task ≥11).
  - **vehicle** (`samples/vehicle/`): 3도메인 — body_can/pt_can/eth_backbone + domain_gw. 기능 데모: CAN ID 중재(0x100>0x101>0x102), 게이트웨이 명시 remap(door_state→0x520, delay 2ms) + ID 범위 라우트(0x200~0x202→eth, delay 1ms), Ethernet FIFO, 오버런(body_ecu.diag period 100 < wcet 110 → 5회), 테일 드롭(queue_depth 4 → gear_state t=500/502 2건), supersede 12건, 주입 버스트(t=500~502 15건), assertion 9건. **exit 0**.
  - **components.py**: 커스텀 컴포넌트 API 데모 — `door_act` 클래스(on_message → ctx.log + ctx.send door_state), `load(..., components={...})`. 실행 **exit 0**, log 11건, 주입 data({state: open}) 전달 확인.
  - **CLI 확인**: `--lang en` 요약·리포트 출력, `--log` JSON(이벤트 2009건), `--quiet` exit 0.
  - **다음**: T-022 승인 게이트 (T-020 README 승인도 함께).
- **README rev 2 (2026-08-12, T-023)**: 사용자 지시로 4장 "샘플 예제 (samples/)" 섹션 신설 — 4.1 기본 샘플(basic, assertion 5건), 4.2 차량 샘플(vehicle, assertion 9건 + 기능 데모 표), 4.3 커스텀 컴포넌트 데모(components.py, log 11건), 4.4 샘플 구조. 기존 4~6장 → 5~7장 재번호, 프로젝트 구조 트리에 samples/ 반영. vehicle scenario.yml stale 주석(queue_depth 8→4) 수정. 수록 명령 3종 전부 재실검증 exit 0. T-020 승인 게이트에 rev 2 포함.
- **v1 완료 (2026-08-12, T-020·T-022 승인)**: 사용자 명시 승인("OK")으로 README rev 2(T-020)와 samples/(T-022) 게이트 done. **v1 스코프 태스크 전부 완료 — Done 22 / Pending 1(T-017 v2 스테이징, 사용자 요청 시)**. v1 산출물: sdv_sim 코어+CLI(78 테스트, mypy strict), spec/PRD/ASR/ADR 18건, verification 리포트(86 pass), README rev 2, samples 2세트+커스텀 컴포넌트 데모. 이후 v2 스테이징(웹 대시보드) 논의는 T-017로 진입 가능.