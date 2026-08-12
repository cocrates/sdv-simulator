# Verification: SDV Simulator v1 (sdv-sim)

**Spec:** `{project-root}/spec/sdv-sim-v1.md` (Aligned with `{project-root}/spec/PRD.md`)
**Artifact(s):**
- `{project-root}/sdv_sim/core/{engine,component,events,report,errors}.py`
- `{project-root}/sdv_sim/schema/{arch,scenario}.py`
- `{project-root}/sdv_sim/i18n.py`
- `{project-root}/sdv_sim/cli/main.py`
- `{project-root}/pyproject.toml`
- `{project-root}/tests/` (10개 파일, 78건)

**Verified:** 2026-08-12 (1차) / 2026-08-12 (재검증 — 스펙 수정 + i18n 반영)
**환경:** uv 0.12.3, Python 3.12.3 (`.venv` 재생성 — gitignore 대상으로 세션 간 유지 안 됨)
**요약:** 86 pass, 0 fail, 0 partial, 0 not-verifiable (총 86건)

**실행 확인 (재검증):**
- `uv run pytest -q` → **78 passed** (0.19s) — 신규 `tests/test_i18n.py` 15건 포함
- `uv run mypy` → **Success: no issues found in 13 source files** (strict, `i18n.py` 추가)
- 공식 예시 실행 → **exit 0**, `cmd_sent: matched 12 event(s); first at t=0` (스펙 수정 후 정합)
- CLI `--lang ko|en` → 카테고리·공통 메시지 로컬라이즈 확인, 내부 예외 상세 원문 유지 확인

**1차 검증 (2026-08-12):** 78 pass / 1 fail / 2 partial — Deviation 1(공식 예시 비정합)·Deviation 2(로컬라이즈 불완전) 식별.
**재검증: 두 Deviation 모두 해소됨** — 스펙 공식 예시 수정(`door_ecu` 추가 + `at_ms: 0, count: 12`) 및 `sdv_sim/i18n.py` 기반 로컬라이즈 구현.

---

## Inventory & Results

### PRD 수준 (`spec/PRD.md`)

| # | Spec item | Status | Evidence / Notes |
|---|-----------|--------|------------------|
| 1 | [PRD Goal] 정의→실행→검증 시뮬레이터, 헤드리스 CLI | pass | `cli/main.py` `sdv-sim run`, `load()→run()` |
| 2 | [PRD Goal] 코어 엔진을 라이브러리로 임베드 | pass | `sdv_sim/core/engine.py` 공개 API (`load`, `Simulator`) |
| 3 | [PRD Goal] 모든 형태가 단일 코어 공유 | pass | 모듈 경계 `core`/`cli` 분리 (v2/v3 경계) |
| 4 | [PRD Audience] 차량 SW 개발자/아키텍트 | pass | YAML 정의 + Python API + assertion/CLI 검증 흐름 |
| 5 | [PRD v1] E/E 아키텍처 모델링 (ECU/HPC 노드, 토폴로지) | pass | `schema/arch.py` NodeDef/LinkDef |
| 6 | [PRD v1] 차량 내 통신 (CAN/Ethernet, 라우팅·지연·대역폭) | pass | `engine.py` LinkRuntime, 게이트웨이 라우팅 |
| 7 | [PRD v1] 앱 런타임 (가상 노드 SW 컴포넌트) | pass | `component.py` + 태스크 스케줄러 |
| 8 | [PRD v1] 제공 형태: 라이브러리 코어 + CLI | pass | `pyproject.toml` `[project.scripts] sdv-sim` |
| 9 | [PRD OoS] 동역학/ADAS/OTA/HIL/대시보드/데스크톱/안전 인증 미포함 | pass | 코드에 해당 기능 없음 |
| 10 | [PRD Constraint] ko/en CLI 출력 구조 | pass | `i18n.py` 카탈로그 + `--lang` 연동 (1차 partial → 해소) |
| 11 | [PRD Constraint] assertion 자동 검증 | pass | `_evaluate_assertions`, 종료 코드 반영 |
| 12 | [PRD Constraint] v2/v3 확장 경계 | pass | core/cli 분리, 이벤트·리포트 자료구조 재사용 가능 |

### 정의 (모델) — `spec/sdv-sim-v1.md` Requirements

| # | Spec item | Status | Evidence / Notes |
|---|-----------|--------|------------------|
| 13 | YAML 정의 파일로 아키텍처 기술 | pass | `load(arch, scenario)` + `_load_yaml_model` |
| 14 | 노드: 이름/타입(ECU\|HPC)/연결 링크/컴포넌트 | pass | `NodeDef` (`type: Literal["ECU","HPC"]`) |
| 15 | Pydantic 검증 + 명확한 오류 메시지 | pass | `extra="forbid"`, `_resolve_references`, `SdvSimInputError.format()` (파일명·줄·필드) |
| 16 | scenario.yaml: duration/seed/messages/assertions | pass | `schema/scenario.py` (seed는 v1 무시) |
| 17 | architecture.yaml 필드 트리 (D-12) | pass | nodes/links/gateways — 스펙 필드 트리와 1:1 |
| 18 | scenario.yaml 필드 트리 (D-12) | pass | duration_ms(필수)/seed?/messages/assertions |
| 19 | 메시지-프레임 매핑 (message 필드 or 동일 이름) | pass | `_frame_message()` |
| 20 | class 미등록 시 스텁 (통신 시뮬레이션만) | pass | 기본 `Component` no-op, 테스트 `test_stub_component_does_not_auto_send` |
| 21 | 주입 메시지 tx 기록 (D-12/D-13) | pass | `_schedule_initial` 주입 → tx, 테스트 `test_injection_data_forwarded` |
| 22 | 미지정·타입 불일치·미정의 참조 → 스키마 오류 (D-12) | pass | 링크 미연결 노드·미정의 프레임·미정의 메시지 거부 (test_schema) |
| 23 | **공식 예시 (D-12)** | pass | 실행 확인 — `door_ecu` 노드 정의 + assertion `at_ms: 0, count: 12` → **exit 0**, matched 12, first at t=0 (1차 fail → 해소) |

### 시뮬레이션 엔진

| # | Spec item | Status | Evidence / Notes |
|---|-----------|--------|------------------|
| 24 | DES 이벤트 큐 + 결정적 처리 순서 | pass | `heapq`, `(t, prio, decl, seq)` |
| 25 | 동일 입력 → 동일 결과 (결정성) | pass | `test_determinism` |
| 26 | 이벤트 없는 구간 시간 도약 | pass | heap min-tick만 처리, 중간 시간 건너뜀 |
| 27 | 정수 ms | pass | 모든 시각 int, 스키마 검증 |
| 28 | (t_ms, seq) 완전 순서 | pass | `Event(t_ms, seq)`, 로그 정렬 |
| 29 | duration_ms 도달 시 종료 | pass | `while heap[0][0] <= duration` |
| 30 | 동일 시각: 우선순위→선언 순서→seq (D-19) | pass | 태스크 우선순위·frame/task decl·seq |
| 31 | 종료 경계 inclusive (D-19) | pass | `<=` 조건, 테스트 `test_periodic_runs` (t=50 포함) |
| 82 | **같은 시각 비-태스크 이벤트는 태스크 뒤 (D-19, U-1)** | pass | `MAX_PRIO = 1<<30`, t=0에서 `task_start`(seq 3) → `tx`(seq 10) 순서 확인 |

### 통신 (L2)

| # | Spec item | Status | Evidence / Notes |
|---|-----------|--------|------------------|
| 32 | CAN 프레임 전송·수신 | pass | tx/rx 이벤트, test_can |
| 33 | CAN 지연·큐잉 (ID 우선 중재) | pass | `(frame.id, frame_decl, arrival_seq)` 정렬, `test_lower_id_wins_when_same_tick` |
| 34 | Ethernet 대역폭·스위치 FIFO 큐잉 | pass | `drain()`, FIFO 정렬, test_ethernet |
| 35 | 게이트웨이 라우팅 | pass | `_find_route`/`_route_frame`, test_gateway |
| 36 | CAN tx_ms = ceil((44+8·DLC)/bitrate_kbps) | pass | `tx_ms()`, bitrate=kbps 단위 |
| 37 | CAN ID 작을수록 중재 우선, 버스 점유 시 큐 대기 | pass | 정렬 + `bus_free_at` |
| 38 | Ethernet tx_ms = ceil((dlc+42)·8/(Mbps·1000)) — payload = DLC | pass | `tx_ms()` `dlc+42` (U-6 스펙 명시 — `bytes = dlc + 42`로 갱신됨) |
| 39 | queue_depth 초과 테일 드롭 → drop 이벤트 | pass | `_enqueue`→`_log_drop`, `test_tail_drop_when_queue_full` |
| 40 | routes from→to, remap_id 선택, delay_ms 기본 0 | pass | `GatewayRouteDef` |
| 41 | 매칭 우선순위: 명시 frame > ID 범위 | pass | `_find_route` 2패스 |
| 42 | rx는 receives 매핑 노드만 (D-13) | pass | `receivers_by_message`, `test_rx_only_to_receives_mapped_nodes` |
| 43 | 게이트웨이 인프라: 소스 rx→대상 tx(remap)→대상 rx, 원본 정상 전파 (D-13) | pass | `_start_transmission`+`_route_frame`, test_single_hop |
| 44 | 홉 8 초과 drop (D-13) | pass | `MAX_HOPS=8`, `test_hop_limit_drops` |
| 45 | 큐 동일 프레임 최신 교체, depth 미소모, 이벤트 없음 (D-18) | pass | `drain()`/`_enqueue` supersede, `test_supersede_queued_same_frame` |
| 83 | **switches 2개 이상 정의 시 첫 번째만 사용 (U-2)** | pass | `LinkRuntime.__init__` `defn.switches[0].queue_depth`, 실행 확인 exit 0 |

### 앱 런타임

| # | Spec item | Status | Evidence / Notes |
|---|-----------|--------|------------------|
| 46 | 주기 태스크 + 메시지 수신 핸들러 | pass | `on_periodic`/`on_message` |
| 47 | 스케줄러가 태스크를 이벤트로 스케줄링, 결정성 | pass | `_schedule_task_next` |
| 48 | 전송/수신 API로 버스 통신 | pass | `TaskContext.send`, rx 디스패치 |
| 49 | 비선점 + wcet_ms(기본 0) | pass | `busy_until`, `test_wcet_advances_time` |
| 50 | 주기 초과 overrun 이벤트 + 리포트 경고 | pass | `_on_task_end`, `test_overrun_detected...` |
| 51 | 스텁 수신자 전용, 자동 송신 없음 (D-14) | pass | `test_stub_component_does_not_auto_send` |
| 52 | 오버런 후 절대 주기, 놓친 주기 스킵 (D-17) | pass | `test_overrun_detected_and_absolute_period_kept` |

### API (라이브러리)

| # | Spec item | Status | Evidence / Notes |
|---|-----------|--------|------------------|
| 53 | `load(arch, scenario, components?) -> Simulator` (D-15) | pass | `engine.py: load()` 시그니처 일치 |
| 54 | `run() -> SimulationResult` (events/report/assertions/duration_ms) | pass | dataclass `SimulationResult` |
| 55 | 이벤트 스트림 = 리스트 (D-15) | pass | `SimulationResult.events: list[Event]` |
| 56 | TaskContext: send/log/now_ms (D-15) | pass | `component.py` |
| 57 | load_scenario(시나리오 YAML) | pass | `Simulator.load_scenario` (요구사항 문구 일치) |
| 58 | 컴포넌트 Python 클래스 등록 (components 매핑) | pass | `cls = self._components.get(key, Component)` |

### CLI

| # | Spec item | Status | Evidence / Notes |
|---|-----------|--------|------------------|
| 59 | `sdv-sim run <arch> <scen>` | pass | argparse subcommand |
| 60 | 헤드리스 동작 | pass | 사람 개입 없음 |
| 61 | pass/fail·요약·이벤트 로그 출력 | pass | 요약 stdout, 로그 파일 |
| 62 | 언어: --lang > SDV_SIM_LANG > 로케일(외→ko) | pass | `_resolve_lang`, test_lang_* |
| 63 | 종료 코드 0/1/2/3 | pass | `EXIT_*` 상수, test_cli |
| 64 | 오류 메시지 파일명·줄·필드 경로 | pass | `SdvSimInputError.format()` |
| 65 | --log 기본 events.json, --log - = stdout (D-16) | pass | `_write_json_log`, test_cli |
| 66 | --quiet 시 요약 생략 (D-16) | pass | test_pass |
| 67 | 오류 카테고리·공통 메시지 로컬라이즈, 내부 상세 원문 유지 (D-16) | pass | `i18n.py` `tr()` + `SdvSimInputError.format(lang)` — `--lang ko|en` 출력 확인 (1차 partial → 해소) |
| 84 | **로그 쓰기 실패 = 종료 코드 2 (U-3)** | pass | `_write_json_log` OSError → `tr('error_write')` + `EXIT_INPUT_ERROR`, 실행 확인 exit 2 |

### 검증·자동화

| # | Spec item | Status | Evidence / Notes |
|---|-----------|--------|------------------|
| 68 | assertion 선언 (시간 제약·속성·이벤트 조건) | pass | `AssertionExpect` |
| 69 | assertion 결과 리포트 + 종료 코드 반영 | pass | `_build_report`, `EXIT_ASSERTION_FAIL` |
| 70 | 결정적 JSON 로그 (CI 재사용) | pass | `_log_document`, `test_events_sorted` |
| 71 | expect 블록 문법 | pass | `event/속성/at_ms/within_ms/count` |
| 72 | 단일 JSON 문서 (schema_version/simulation/events/assertions) | pass | `_log_document` |
| 73 | type enum 7종 | pass | `EVENT_TYPES` |
| 74 | event 타입 + 속성 모두 일치 매칭 (D-20) | pass | `_match_assertion` |
| 75 | at_ms/within_ms, 생략 시 시간 무관 (D-20) | pass | `_evaluate_assertions`, test_assertions |
| 76 | count = **최소 n건 이상** (≥, D-20) | pass | `len(matched) >= exp.count` — 스펙 문구 "최소 n건 이상"으로 명확화 (U-5) |
| 77 | 실패 메시지 최대 3건 + 기대/실제 시각·count (D-20) | pass | `_assertion_detail` |
| 78 | Report 구조 (simulation/links/tasks/assertions/warnings, D-21) | pass | `report.py` |
| 79 | bus_load_percent = tx_ms 합 / duration_ms (D-21) | pass | `_build_report` (`duration==0` 가드 포함) |
| 80 | CLI 요약 = 리포트 요약판 (D-21) | pass | `_format_summary` |
| 81 | Out of Scope 준수 (L3·신호 변환·선점·브로드캐스트 rx·게이트웨이 노드화·상대 주기·큐 복수 큐잉·콜백/이터레이터·홉 8 초과) | pass | 해당 기능/API 코드에 없음 |
| 85 | **assertion `event: task` = task_start + task_end 모두 매칭 (U-4)** | pass | `_match_assertion` `e.type not in ("task_start","task_end")`, 실행 확인 count 21 (11 start + 10 end, t=100 인스턴스의 end는 duration 초과로 미발생) |

---

## Deviations (Non-compliance)

**해소됨 (2026-08-12 재검증 기준 없음 — 0 fail / 0 partial).**

1차 검증에서 식별된 Deviation 2건은 아래와 같이 해소되어 인벤토리에 pass로 반영됨:

### ~~Deviation 1~~ — 스펙 공식 예시(D-12) 자기 비정합 (Major, 해소)
- **수정**: `spec/sdv-sim-v1.md` 공식 예시에 `door_ecu` 노드 정의 추가, assertion을 `{ event: tx, frame: door_cmd, link: can1, at_ms: 0, count: 12 }`로 변경
- **검증**: 실행 결과 `cmd_sent: matched 12 event(s); first at t=0`, exit 0 (주기 tx t=0~100 11건 + 주입 t=5 1건, U-5 ≥ 의미와 정합)

### ~~Deviation 2~~ — 오류 메시지 로컬라이즈 불완전 (Minor, 해소)
- **수정**: `sdv_sim/i18n.py` 신설 (ko/en 카탈로그 + `tr()`), `SdvSimInputError`를 `code + params` + `format(lang)` 구조로 재구성, `engine.py`/`cli/main.py` 오류 발생 지점 i18n 연동
- **로컬라이즈 경계** (사용자 승인): 오류 카테고리·공통 메시지(입력 오류/스키마 오류/YAML 구문 오류/파일을 읽을 수 없음 등)는 `--lang` 따라 ko/en, **내부 예외 상세**(컴포넌트 예외 원문·OS 상세)는 원문 유지 — 테스트 `test_internal_error_keeps_original_detail` 확인
- **검증**: `--lang ko` → `입력 오류: ... 스키마 오류: ... (필드: ...)`, `--lang en` → `input error: ... schema error: ... (field: ...)`

---

## Undocumented ASRs (Specification Gaps)

1차 검증에서 식별된 U-1~U-6은 **2026-08-12 전부 스펙에 인코딩 완료** (해소). 검증 시점의 기록:

| # | 결정 내용 | 스펙 인코딩 위치 | 상태 |
|---|-----------|------------------|------|
| U-1 | 같은 tick에서 비-태스크 이벤트는 모든 태스크 이벤트 뒤 처리 (`MAX_PRIO = 2^30`) | D-19 "같은 시각 비-태스크 이벤트" + Requirements "비-태스크 이벤트는 모든 태스크 이벤트 뒤" | 해소 (인벤토리 #82) |
| U-2 | Ethernet `switches` 2개 이상 시 첫 번째만 사용 | 통신 충실도 "switches에 2개 이상 정의 시 첫 번째만 사용" | 해소 (인벤토리 #83) |
| U-3 | 로그 파일 쓰기 실패 시 종료 코드 2 | CLI 입출력 채널 "파일 쓰기 실패는 종료 코드 2" | 해소 (인벤토리 #84) |
| U-4 | assertion `event: task`는 task_start와 task_end 둘 다 매칭 | D-20 "event: task는 task_start와 task_end 둘 다 매칭" | 해소 (인벤토리 #85) |
| U-5 | count 검증 = 최소 n건 (≥) | D-20 "최소 n건 이상이면 통과 (≥ 의미, 초과는 실패 아님)" + Requirements | 해소 (인벤토리 #76) |
| U-6 | Ethernet payload = 프레임 DLC 바이트 (`bytes = dlc + 42`) | 통신 충실도 "payload = 프레임 DLC 바이트" + Requirements | 해소 (인벤토리 #38) |

---

## Recommended Next Steps

1. ~~스펙 수정 (공식 예시 + U-1~U-6)~~ — **완료** (2026-08-12, 사용자 승인 "1")
2. ~~Deviation 2 i18n~~ — **완료** (로컬라이즈 경계: 카테고리·공통 메시지 ko/en, 내부 상세 원문)
3. ~~재검증~~ — **완료** (86 pass / 0 fail / 0 partial)
4. **최종 게이트**: 사용자 리뷰 — 리포트 승인 시 TODO T-009 done 처리, 세션 종료 또는 후속 스테이징(v2 대시보드) 논의 가능
5. 참고: 1차 검증에서 추가로 발견된 무해한 관찰 3건(해석 #1 tx 시각 = 실제 전송 시작, #4 자체 오버런만 스킵, #5 on_message 시간 진행 없음)은 v1 Out of Scope·D-17/D-18과 정합 확인 — 스펙 변경 불필요

## User Review

(비어 있음 — 사용자 리뷰 대기)
