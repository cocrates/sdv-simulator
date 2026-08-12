# SDV Simulator v1 (sdv-sim)

## Requirement
하드웨어 없이 차량 소프트웨어 플랫폼(E/E 아키텍처, 차량 내 통신, 앱 런타임)을 **정의 → 실행 → 검증**할 수 있는 Python 기반 헤드리스 시뮬레이터. 차량 SW 개발자/아키텍트가 YAML 정의 파일로 아키텍처를 기술하고, CLI로 시나리오를 실행해 통신 동작을 자동 검증한다.

## Context
- SDV(Software Defined Vehicle)는 차량 기능이 하드웨어가 아닌 소프트웨어에 의해 정의되는 환경
- v1 = 라이브러리 코어 + CLI. v2(웹 대시보드, OTA), v3(데스크톱)은 후속 스테이징
- 상위 문서: `{project-root}/spec/PRD.md`
- 상세 설계 ADR 21건(1차 11건 + 2차 10건, 2026-08-12 사용자 승인)의 결정을 본 Spec에 인코딩함

## Decisions

### 언어/런타임 & 성능
- **언어/런타임**: Python 3.11+, 타입 힌트 + mypy. 배포는 pip 패키지 + CLI 진입점
- **성능 목표**: v1은 **순수 Python** 구현. 목표 규모 — 노드 ≤ 50, 링크 ≤ 20, 프레임 ≤ 200, 시나리오 duration ≤ 60s, 이벤트 ≤ 100만 건 → 수 초 내 실행. 병목 발생 시 후속 스테이징에서 확장 모듈(C로 재작성) 검토
- **결정성**: 난수 미사용 (`seed` 필드는 스키마에 유지하되 v1에서 무시)

### 패키지 & 아티팩트 구조
- **패키지 구조**: 배포(distribution) 이름 `sdv-sim`, 임포트(import) 이름 `sdv_sim`. 단일 패키지 + 모듈 경계: `sdv_sim/core`(엔진·모델), `sdv_sim/cli`

### 시뮬레이션 엔진 & 시간 모델
- **시뮬레이션 엔진**: 이산 사건(DES) 기반. 이벤트 큐 + 단일 스레드 + 고정 이벤트 순서로 **결정성 보장**. 이벤트가 없는 구간은 시간 도약(fast-forward)
- **시간 모델**: 모든 시간 값(주기·지연·타임아웃·타임스탬프)은 **정수 ms**. 이벤트는 `(t_ms, seq)` 쌍으로 완전 순서 결정. 같은 시각 이벤트는 seq(발생 순서)로 정렬
- **종료**: 시나리오 `duration_ms` 도달 시 종료. 전파 지연은 0 (지연은 큐잉/버스 점유로만 발생)
- **주기 이벤트**: 주기 프레임/태스크는 t=0에 첫 발생 후 매 period마다 재발생
- **같은 시각 처리 순서 (D-19)**: 동일 `t_ms` 이벤트는 **① 태스크 우선순위(작을수록 우선) → ② 파일 선언 순서(노드/컴포넌트/프레임 정의 순) → ③ seq(생성 순서)** 로 처리
- **같은 시각 비-태스크 이벤트 (D-19)**: tx/rx/drop 등 비-태스크 이벤트는 **모든 태스크 이벤트 뒤**에 처리한다 (우선순위 2^30 = 태스크 최대 우선순위보다 큼). 비-태스크 간에는 파일 선언 순서 → seq 순
- **종료 경계 (D-19)**: `t == duration_ms`인 이벤트까지 처리 후 종료 (**inclusive**) — exclusive가 아님

### 정의 형식 & 스키마
- **정의 형식**: YAML (사람 작성 우선). PyYAML 파싱, Pydantic 모델 기반 스키마 검증
- **스키마 구조 (2계층)**: 컴포넌트는 논리 **메시지**(`sends`/`receives`), 링크는 L2 **프레임**(`id`/`dlc`/`period`/`source`/`message`)을 소유
- **매핑 규칙**: 프레임의 `message` 필드가 명시되면 그 메시지에, 미명시면 프레임명 = 메시지명으로 매핑
- **파일 분리**: `architecture.yaml`(노드·링크·게이트웨이·컴포넌트) / `scenario.yaml`(duration, messages 주입, assertions)
- **컴포넌트 구현**: `class` 필드는 선택 — 미등록 시 스텁(통신 시뮬레이션만 수행)

### 정의 필드-레벨 스키마 & 메시지 주입 (D-12)
- **`architecture.yaml` 필드 트리**:
  - `nodes: [{name, type: ECU|HPC, components: [{name, sends: [msg], receives: [msg], tasks: [{name, period_ms, priority, wcet_ms}]}]}]`
  - `links: [{name, kind: can|ethernet, bitrate, nodes: [node], frames: [{name, id, dlc, period_ms, source, message?}], switches: [{name?, queue_depth}]}]`
  - `gateways: [{name, routes: [{from: {link, frame|id_min, id_max}, to: {link, remap_id?}, delay_ms?}]}]`
- **`scenario.yaml` 필드 트리**: `duration_ms`(필수), `seed?`(v1 무시), `messages: [{t_ms, link, frame, data?}]`, `assertions: [{name?, expect: {event, frame/message/node/link/task?, at_ms?, within_ms, count}}]`
- **메시지 주입 형식**: `messages` 항목은 `t_ms`(주입 시각), `link`(대상 링크), `frame`(대상 프레임), `data?`(선택 데이터)를 가진다
- **Pydantic 1:1**: 위 필드 트리는 `sdv_sim/schema/arch.py`(architecture)와 `sdv_sim/schema/scenario.py`(scenario) Pydantic 모델과 1:1 매핑 (구현 SSOT)
- **스키마 검증**: 미지정 필드·타입 불일치·미정의 참조(프레임 source가 링크 미연결 노드 등)는 스키마 오류. 오류 메시지는 파일명·필드 경로 포함
- **공식 예시** (실행 가능 — 검증됨: 주기 tx t=0~100 11건 + 주입 t=5 1건 = 12건, 첫 매칭 t=0):
  ```yaml
  # architecture.yaml
  nodes:
    - name: body_ecu
      type: ECU
      components:
        - name: door_ctrl
          sends: [door_cmd]
          receives: [door_state]
          tasks:
            - { name: main, period_ms: 10, priority: 1, wcet_ms: 1 }
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
        - { name: door_cmd, id: 0x100, dlc: 4, period_ms: 10, source: body_ecu }
        - { name: door_state, id: 0x101, dlc: 4, period_ms: 10, source: door_ecu }
  # scenario.yaml
  duration_ms: 100
  messages:
    - { t_ms: 5, link: can1, frame: door_cmd, data: { state: open } }
  assertions:
    - name: cmd_sent
      expect: { event: tx, frame: door_cmd, link: can1, at_ms: 0, count: 12 }
  ```

### 통신 충실도 (L2)
- **CAN 모델**: `tx_ms = ceil((44 + 8·DLC) / bitrate_kbps)` (CAN 표준 프레임 비트 수 기준). 동시 전송 시 **CAN ID가 작을수록 중재 우선**. 버스 점유 중이면 우선순위 큐에서 대기 → 지연 발생. 버스 부하(점유율 %)를 리포트에 포함
- **Ethernet 모델**: `bytes = dlc + 42` (오버헤드; payload = 프레임 DLC 바이트, `data` 객체 크기와 무관), `tx_ms = ceil(bytes·8 / (bitrate_mbps·1000))`. 링크당 단일 스위치(기본 1개), **FIFO 큐**, `queue_depth`(기본 1000) 초과 시 **테일 드롭** → `drop` 이벤트 기록. `switches`에 2개 이상 정의 시 **첫 번째만 사용** (스키마 오류 없음, U-2)
- **게이트웨이**: `routes: from(link + frame|id_min/id_max) → to(link + remap_id 선택)`. 매칭 우선순위: 명시 frame > ID 범위. 처리 지연 `delay_ms`(기본 0)

### 통신 이벤트 기록 의미론 (D-13)
- **tx 이벤트 발생 경로 3가지**: (1) 주기 프레임(source 노드, t=0 첫 발생) (2) 컴포넌트 `ctx.send` (3) 시나리오 `messages` 주입 — 모두 송신 노드·프레임으로 tx 기록
- **rx 이벤트**: 해당 링크에서 `receives`에 매핑된 컴포넌트가 있는 **노드에만** 기록 (브로드캐스트 rx는 모든 노드에 남기지 않음). CAN/Ethernet 동일 규칙
- **게이트웨이 동작**: 명시적 노드로 기록하지 않음(인프라). 매칭 시 소스 링크 기준 rx → 라우팅 → 대상 링크에서 tx(remap_id 적용) → 대상 수신자 rx. 원본 프레임은 소스 링크에서 정상 전파 유지
- **다중 홉**: 라우팅된 프레임이 다시 게이트웨이 규칙에 매칭될 수 있음(규칙 체인). 프레임당 라우팅 홉 **최대 8** — 초과 시 drop 이벤트
- **Ethernet 흐름**: tx(송신 노드) → 스위치 FIFO 입장 → 방출 완료 시각에 수신자 rx. 스위치 큐 초과는 테일 드롭
- **주입 메시지도 tx로 기록**: 지연·라우팅 검증에 주입 시나리오 사용 가능

### 프레임 큐 인스턴스 정책 (D-18)
- 큐(CAN 우선순위 큐 / Ethernet FIFO)에 대기 중인 **동일 프레임의 새 주기 인스턴스 도착 시 최신 인스턴스로 교체**(supersede) — 기존 제거 후 신규로 대체
- CAN/Ethernet 동일 적용. 교체는 큐 depth를 소모하지 않음(Ethernet 테일 드롭과 별개 정책)
- 교체는 별도 이벤트로 기록하지 않음 — 로그는 최종 전송된 인스턴스만

### 앱 런타임
- **스케줄링**: **비선점**. 태스크는 `wcet_ms`(기본 0 = 즉시 완료)만큼 시뮬레이션 시간 경과. 주기 시작 시각을 넘기면 `overrun` 이벤트 + 리포트 경고
- **같은 시각 실행**: 우선순위(작을수록 우선) → seq 순
- **컴포넌트 API**: `Component` 베이스 클래스 — `on_periodic(ctx)` / `on_message(ctx, message)` 콜백 + `ctx.send(name, data)` / `ctx.log(...)`. 등록: `load(arch, scenario, components={"name": Class})`

### 스텁 컴포넌트 동작 (D-14)
- `class` 미등록 컴포넌트(스텁)는 **수신자로만 동작** — `sends`는 무시, 자동 송신 없음
- tx는 **3경로로만** 발생: (1) 주기 프레임(source 노드) (2) 시나리오 주입 (3) 실제 컴포넌트 `ctx.send` (D-13과 정합)
- 스텁은 `receives` 매핑에 따라 rx 기록만 수행. sends가 있는 스텁의 송신을 기대하는 assertion은 실패

### 태스크 오버런 정책 (D-17)
- 오버런 후 다음 인스턴스는 **절대 주기 유지**(원래 t=0 기준 주기)로 재스케줄링 — 오버런으로 밀리지 않음, 놓친 주기 인스턴스는 **스킵**
- 오버런 판정: `wcet_ms` 종료 시각 > 원래 주기 시작 시각
- 스킵된 인스턴스는 별도 이벤트 없음(overrun 이벤트만 기록)

### 공개 API 계약 (D-15)
- `load(arch: str|Path, scenario: str|Path, components: dict[str, type[Component]] | None = None) -> Simulator` — **파일 경로 기반** (str = 경로)
- `loads(arch_yaml: str, scenario_yaml: str, components: dict[str, type[Component]] | None = None) -> Simulator` — **YAML 문자열 기반** (core-yaml-string-input, 2026-08-12 추가 — v2 대시보드·테스트 하네스용 문자열 입력)
- `Simulator.load_scenario(scenario: str|Path) -> Simulator` — 시나리오 교체 (파일 경로)
- `Simulator.load_scenario_yaml(scenario_yaml: str) -> Simulator` — 시나리오 교체 (YAML 문자열, core-yaml-string-input 2026-08-12 추가)
- `Simulator.run() -> SimulationResult` — `events: list[Event]`(결정적, 전체 버퍼), `report: Report`, `assertions: list[AssertionResult]`, `duration_ms: int`
- `TaskContext`: `send(name: str, data: Any)` / `log(message: str)` / `now_ms() -> int`(현재 시뮬레이션 시각 조회)
- 이벤트 스트림 = `SimulationResult.events` **리스트** (소비자가 직접 순회 — 콜백/이터레이터 아님, v1)
- 문자열 입력의 오류 식별자: `SdvSimInputError`의 파일명 자리에 **의사 식별자** `arch`/`scenario` 사용 (경로 기반과 동일한 오류 형식, core-yaml-string-input)

### 검증·자동화 & CLI
- **assertion 문법**: YAML 선언형 `expect { event: tx|rx|task, frame/message/node/link/task, at_ms, within_ms(기본 0), count(기본 1) }`. 종료 후 **첫 매칭 이벤트** 기준 시간 검증 + count 개수 검증
- **이벤트 로그 스키마**: 단일 JSON 문서 — `{schema_version: 1, simulation{duration_ms, result}, events[{t_ms, seq, type, node?, link?, frame?, task?, data?}], assertions[{name, status, detail}]}`. `(t_ms, seq)` 오름차순, 해당 없는 필드 생략. `type` enum: `tx|rx|task_start|task_end|drop|overrun|log`
- **CLI 정책**: `sdv-sim run <architecture.yaml> <scenario.yaml>`. 언어 = `--lang ko|en` > `SDV_SIM_LANG` env > 시스템 로케일(ko/en 외 → ko). 종료 코드: **0=pass / 1=assertion fail / 2=입력 오류(스키마·파일) / 3=내부 오류**. 오류 메시지에 파일명·줄 번호·필드 경로 포함

### CLI 입출력 채널 (D-16)
- 커맨드: `sdv-sim run <architecture.yaml> <scenario.yaml> [--log <path>] [--quiet] [--lang ko|en]`
- **JSON 로그**: `--log <path>`(기본 `events.json`)로 파일 출력. `--log -`는 stdout 출력. **파일 쓰기 실패는 종료 코드 2(입력 오류)** (U-3)
- **사람용 요약**: 결과·통계·assertion 요약은 stdout — `--quiet` 시 요약 생략(종료 코드로만 판정)
- **오류 메시지 로컬라이즈 (D-16)**: 오류 카테고리·공통 메시지(`입력 오류`/`스키마 오류`/`YAML 구문 오류`/`파일을 읽을 수 없음` 등)는 CLI 언어(`--lang`)로 출력. **내부 예외 상세**(컴포넌트 예외 원문, OS 상세)는 원문 유지 — 번역으로 디버깅 정보가 흐려지지 않도록 함

### Assertion 평가 규칙 (D-20)
- **매칭**: event 타입 + 지정 속성(frame/message/node/link/task) **모두 일치**. `event: task`는 `task_start`와 `task_end` **둘 다** 매칭한다 (U-4)
- **시간 검증**: `at_ms` 명시 시 `|t_ms - at_ms| <= within_ms`(기본 0 = 정확 일치). **`at_ms` 생략 시 시간 무관**(시간 조건 없이 매칭)
- **count 검증**: 매칭 이벤트가 **최소 n건 이상**이면 통과 (≥ 의미, 시간 조건과 독립 — "시간대 관계없이 최소 n건". 초과는 실패 아님, U-5)
- **실패 메시지**: 매칭 이벤트 **최대 3건**(t_ms, seq, 속성) + 기대/실제 시각 + 기대/실제 count

### 결과 리포트 스키마 (D-21)
- **`Report` 구조**:
  - `simulation`: `{duration_ms, result: pass|fail, event_count}`
  - `links`: `[{name, kind, tx_count, rx_count, drop_count, supersede_count, bus_load_percent}]`
  - `tasks`: `[{node, task, period_ms, run_count, overrun_count}]`
  - `assertions`: `[{name, status: pass|fail, detail}]`
  - `warnings`: `[string]`
- **버스 부하**: `bus_load_percent = tx_ms 합 / duration_ms` (점유율 %)
- **CLI 요약** = 리포트의 요약판(링크 부하·오버런·assertion 결과). 리포트는 이벤트 로그로부터 파생(결정적), JSON 로그와는 별개 산출물

## Requirements

### 정의 (모델)
- 사용자는 YAML 정의 파일로 차량 아키텍처(ECU/HPC 노드, 토폴로지)를 기술할 수 있다
- 노드는 이름, 타입(ECU/HPC), 연결 링크(CAN/Ethernet), 탑재 컴포넌트 목록을 가진다
- 정의 파일은 Pydantic 스키마로 검증되며, 오류 시 명확한 오류 메시지를 반환한다
- 사용자는 YAML 시나리오 파일로 실행 시나리오(시작 조건, 메시지 전송, assertion)를 기술할 수 있다
- `architecture.yaml`은 노드(`type`, `components`), 링크(`kind`, `bitrate`, `nodes`, `frames`, `switches`), 게이트웨이(`routes`)를 정의한다
- `scenario.yaml`은 `duration_ms`(필수), `seed`(선택·무시), `messages`(주입), `assertions`를 정의한다
- 컴포넌트의 sends/receives 메시지는 링크 프레임(`message` 필드 또는 동일 이름)에 매핑된다
- 컴포넌트 `class` 미등록 시 스텁으로 동작한다 (통신 시뮬레이션만)
- architecture.yaml은 D-12 필드 트리(nodes/links/gateways)를 따른다
- scenario.yaml은 D-12 필드 트리(duration_ms/seed/messages/assertions)를 따른다
- scenario의 `messages` 주입 항목은 `t_ms`/`link`/`frame`/`data?`를 가지며 주입된 메시지는 tx 이벤트로 기록된다 (D-12, D-13)
- 미지정 필드·타입 불일치·미정의 참조는 스키마 오류로 처리된다 (D-12)

### 시뮬레이션 엔진
- 엔진은 이산 사건 기반으로 동작한다 (이벤트 큐, 결정적 처리 순서)
- 동일 입력(정의+시나리오)에 대해 실행 결과(이벤트 로그)가 결정적으로 동일하다
- 엔진은 이벤트가 없는 구간을 시간 도약으로 건너뛴다
- 모든 시간 값은 정수 ms로 표현된다
- 이벤트는 `(t_ms, seq)` 순서로 결정적으로 처리된다
- `duration_ms` 도달 시 시뮬레이션이 종료된다
- 동일 시각 이벤트는 우선순위(작을수록) → 파일 선언 순서 → seq 순으로 처리된다 (D-19)
- 같은 시각의 비-태스크 이벤트는 모든 태스크 이벤트 뒤에 처리된다 (D-19)
- `t == duration_ms`인 이벤트까지 처리 후 종료된다 (inclusive, D-19)

### 통신 (L2)
- CAN 링크에서 프레임(ID, 주기, DLC)의 전송·수신이 시뮬레이션된다
- CAN 버스 부하에 따른 지연·큐잉이 우선순위 기반으로 모델링된다
- Ethernet 링크에서 대역폭 제약과 스위치 큐잉이 모델링된다
- 게이트웨이는 라우팅 규칙에 따라 한 링크에서 수신한 메시지를 대상 링크로 라우팅한다
- CAN 프레임 전송 시간은 `ceil((44 + 8·DLC) / bitrate_kbps)` ms로 계산된다
- CAN 동시 전송은 ID가 작은 프레임이 우선이며, 버스 점유 중 프레임은 우선순위 큐에서 대기한다
- Ethernet 프레임 전송 시간은 `ceil((dlc + 42)·8 / (bitrate_mbps·1000))` ms로 계산된다 (payload = 프레임 DLC 바이트)
- Ethernet 스위치 큐가 `queue_depth`를 초과하면 테일 드롭되어 `drop` 이벤트가 기록된다
- 게이트웨이는 `routes` 규칙(`from`→`to`, `remap_id` 선택)에 따라 프레임을 라우팅한다
- rx 이벤트는 해당 링크에서 `receives`에 매핑된 컴포넌트가 있는 노드에만 기록된다 (D-13)
- 게이트웨이는 인프라로 동작하며, 라우팅은 소스 링크 rx → 대상 링크 tx(remap_id 적용) → 대상 수신자 rx로 관찰된다 (D-13)
- 라우팅된 프레임의 홉 수가 8을 초과하면 drop 이벤트가 기록된다 (D-13)
- 큐에 대기 중인 동일 프레임의 새 주기 인스턴스는 최신 인스턴스로 교체된다 (D-18)

### 앱 런타임
- 컴포넌트는 주기 태스크(주기, 우선순위)와 메시지 수신 핸들러를 정의할 수 있다
- 스케줄러가 태스크 실행을 이벤트로 스케줄링하며 결정성을 유지한다
- 컴포넌트는 전송/수신 API로 통신 버스에 메시지를 보내고 받을 수 있다
- 태스크는 비선점으로 실행되며 `wcet_ms`(기본 0)만큼 시뮬레이션 시간이 경과한다
- 주기 시작 시각을 초과하면 `overrun` 이벤트가 기록되고 리포트에 경고가 표시된다
- `class` 미등록 컴포넌트(스텁)는 수신자로만 동작하며 자동 송신하지 않는다 (D-14)
- 오버런 후 주기 태스크의 다음 인스턴스는 절대 주기(원래 t=0 기준)로 스케줄링되며, 놓친 주기는 스킵된다 (D-17)

### API (라이브러리)
- 공개 API를 제공한다: `load(아키텍처 YAML)` / `loads(아키텍처 YAML 문자열)` / `load_scenario(시나리오 YAML)` / `load_scenario_yaml(시나리오 YAML 문자열)` / `run()` / 이벤트 스트림 / 결과 리포트
- 라이브러리 사용자는 이벤트 스트림을 직접 소비하여 커스텀 검증을 수행할 수 있다
- `load()`는 `components` 매핑 인자로 컴포넌트 Python 클래스를 등록할 수 있다
- `Component`는 `on_periodic(ctx)`와 `on_message(ctx, message)` 콜백을 제공한다
- `load(arch, scenario, components?)`는 `Simulator`를 반환하고, `run()`은 `SimulationResult`(events/report/assertions/duration_ms)를 반환한다 (D-15)
- `loads(arch_yaml, scenario_yaml, components?)`는 YAML 문자열로 같은 동작을 수행한다 (D-15, core-yaml-string-input — v2 대시보드 문자열 전달용)
- 이벤트 스트림은 `SimulationResult.events` 리스트다 (D-15)
- `TaskContext`는 `send(name, data)` / `log(message)` / `now_ms()`를 제공한다 (D-15)

### CLI
- CLI 명령으로 실행한다: `sdv-sim run <architecture.yaml> <scenario.yaml>`
- CLI는 헤드리스로 동작하며 실행 중 사람 개입이 없다
- CLI는 검증 결과(pass/fail), 실행 요약, 이벤트 로그를 출력한다
- `--lang ko|en` 플래그(기본: `SDV_SIM_LANG` env → 시스템 로케일, ko/en 외 → ko)로 출력 언어를 결정한다
- CLI 종료 코드: **0=pass, 1=assertion fail, 2=입력 오류(스키마·파일), 3=내부 오류**
- 오류 메시지는 파일명·줄 번호·필드 경로를 포함한다
- 오류 카테고리·공통 메시지는 `--lang`에 따라 ko/en으로 출력되고, 내부 예외 상세는 원문을 유지한다 (D-16)
- JSON 로그는 `--log <path>`(기본 `events.json`)로 출력되며 `--log -`는 stdout으로 출력된다 (D-16)
- 사람용 요약은 stdout에 출력되고 `--quiet` 시 생략된다 (D-16)

### 검증·자동화
- 시나리오 YAML에 assertion(시간 제약, 메시지 속성, 이벤트 조건)을 선언할 수 있다
- assertion 결과가 리포트에 포함되고 CLI 종료 코드에 반영된다
- 이벤트 로그는 결정적 JSON 형식으로 출력되어 CI에서 재사용 가능하다
- assertion은 `expect` 블록(`event`/속성/`at_ms`/`within_ms`/`count`)으로 선언된다
- 이벤트 로그는 단일 JSON 문서(`schema_version`, `simulation`, `events`, `assertions`)로 출력된다
- 이벤트 `type`은 `tx`/`rx`/`task_start`/`task_end`/`drop`/`overrun`/`log` 7종이다
- assertion은 event 타입 + 지정 속성 모두 일치로 매칭된다 (D-20)
- `at_ms` 생략 시 assertion은 시간 조건 없이 매칭한다 (시간 무관, D-20)
- `count`는 매칭 이벤트가 **최소 n건 이상**이어야 통과한다 (≥ 의미, 시간 조건과 독립, D-20)
- assertion 실패 메시지는 매칭 이벤트 최대 3건 + 기대/실제 시각 + 기대/실제 count를 포함한다 (D-20)
- 실행 결과 리포트는 simulation/links/tasks/assertions/warnings를 포함하며, 링크별 버스 부하는 tx_ms 합 / duration_ms로 계산된다 (D-21)

## Constraints
- Python 3.11+, 타입 힌트 + mypy로 정적 검사 유지
- 문서·CLI 출력은 한국어/영어 지원 가능한 구조 (1차는 사용자 언어 기준)
- 단일 스레드 실행으로 결정성 보장 (난수 사용 시 고정 시드 — v1은 난수 미사용)
- v2/v3(대시보드, OTA)가 코어 변경 없이 추가될 수 있는 모듈 경계 유지
- 시간 단위는 정수 ms — 서브-ms 정밀도는 v1 제외
- v1은 순수 Python 구현 (목표 규모: 노드 ≤ 50, 링크 ≤ 20, 프레임 ≤ 200, duration ≤ 60s, 이벤트 ≤ 100만 건)

## Out of Scope
- 차량 동역학/물리 시뮬레이션
- ADAS/자율주행 시나리오·센서 시뮬레이션
- OTA (v2로 연기)
- 실제 하드웨어 연동 (HIL)
- 웹 대시보드, 데스크톱 앱 (v2/v3로 연기)
- L3 통신 충실도 (비트 타이밍, 프로토콜 스택, Some/IP)
- 실시간/안전 필수(Safety-Critical) 인증 지원
- CAN 오류 프레임·재전송·버스 오프
- Ethernet VLAN·우선순위 큐(802.1p)
- 게이트웨이 신호 변환(데이터 내용 변경)
- 선점형 스케줄링·우선순위 역전 메커니즘
- 서브-ms 정밀도 (시간 단위는 정수 ms)
- 목표 규모 초과 대규모 시나리오 (수천 노드)
- assertion 논리 결합(and/or)·이벤트 순서(sequence) 검증
- 스텁 컴포넌트 자동 송신 (스텁은 수신자 전용, D-14)
- 브로드캐스트 rx 이벤트 (rx는 receives 매핑 기반, D-13)
- 게이트웨이 노드화·게이트웨이 자체 rx/tx 이벤트 (게이트웨이는 인프라, D-13)
- 상대 주기(밀림) 재스케줄링 (오버런 후 절대 주기 유지, D-17)
- 큐 복수 인스턴스 큐잉 (동일 프레임은 최신 교체, D-18)
- 콜백·이터레이터 이벤트 스트림 API (v1은 리스트 반환, D-15)
- 라우팅 홉 8 초과 (D-13)

## Related
- `{project-root}/spec/PRD.md` — 상위 제품 요구사항
- `{project-root}/spec/ASR.md` — 아키텍처 중요 요구사항 레지스트리
- `{project-root}/adr/*.md` — 결정 근거 (참고용, 생성에 필수 아님)
- `{project-root}/adr/simulation-time-model.md` 등 상세 설계 ADR 21건 (1차 11건 + 2차 10건) — 결정 근거 (참고용, 생성에 필수 아님)

## Tags
`sdv-simulator`, `simulation`, `discrete-event`, `python`, `cli`, `v1`
