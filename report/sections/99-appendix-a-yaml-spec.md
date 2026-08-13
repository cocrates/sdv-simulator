# 부록 A. SDV 정의 — YAML 사양

- **범위**: `architecture.yaml` / `scenario.yaml`의 모든 필드·제약·예시 (본문 3장의 필드 단위 상세판)
- **정합**: 본 부록의 필드 트리는 `spec/sdv-sim-v1.md` D-12와 `sdv_sim/schema/arch.py`·`sdv_sim/schema/scenario.py` Pydantic 모델에 1:1로 대응한다 (구현 SSOT)
- **표기 규칙**: `[필수]` = 지정해야 하는 필드, `(기본 X)` = 생략 시 기본값. 모든 모델은 `extra="forbid"` — 스키마에 정의되지 않은 필드는 오류

## A.1 architecture.yaml

최상위 구조:

```yaml
schema_version: 1
nodes:    [ ... ]
links:    [ ... ]
gateways: [ ... ]
```

### A.1.1 최상위

| 필드 | 타입 | 필수 | 설명 | 제약 |
|------|------|------|------|------|
| `schema_version` | int | 아니오 (기본 1) | 스키마 버전 | — |
| `nodes` | list[Node] | 아니오 (기본 []) | ECU/HPC 노드 목록 | 이름 전역 유일 |
| `links` | list[Link] | 아니오 (기본 []) | CAN/Ethernet 링크 목록 | 이름 전역 유일 |
| `gateways` | list[Gateway] | 아니오 (기본 []) | 게이트웨이 목록 | 이름 전역 유일 |

### A.1.2 Node

| 필드 | 타입 | 필수 | 설명 | 제약 |
|------|------|------|------|------|
| `name` | str | 예 | 노드 이름 | 전역 유일, 링크 `nodes`에서 참조됨 |
| `type` | `ECU` \| `HPC` | 아니오 (기본 `ECU`) | 노드 종류 | — |
| `components` | list[Component] | 아니오 (기본 []) | 탑재 소프트웨어 컴포넌트 | 노드 내 이름 유일 |

### A.1.3 Component

| 필드 | 타입 | 필수 | 설명 | 제약 |
|------|------|------|------|------|
| `name` | str | 예 | 컴포넌트 이름 | 노드 내 유일 |
| `sends` | list[str] | 아니오 (기본 []) | 송신 논리 메시지명 | 각 메시지가 연결 링크 프레임에 매핑되어야 함 (A.3.3) |
| `receives` | list[str] | 아니오 (기본 []) | 수신 논리 메시지명 | 각 메시지가 연결 링크 프레임에 매핑되어야 함 (A.3.3) |
| `tasks` | list[Task] | 아니오 (기본 []) | 주기 태스크 | — |
| `class` | str \| null | 아니오 (기본 null) | Python 컴포넌트 클래스 등록명 (`load(..., components={...})` 키와 일치) | 미지정 시 스텁 동작 (D-14) |

### A.1.4 Task

| 필드 | 타입 | 필수 | 설명 | 제약 |
|------|------|------|------|------|
| `name` | str | 예 | 태스크 이름 | — |
| `period_ms` | int | 예 | 주기 (정수 ms) | > 0 |
| `priority` | int | 예 | 우선순위 | 작을수록 우선 |
| `wcet_ms` | int | 아니오 (기본 0) | 최악 실행 시간 | ≥ 0 (0 = 즉시 완료) |

### A.1.5 Link

| 필드 | 타입 | 필수 | 설명 | 제약 |
|------|------|------|------|------|
| `name` | str | 예 | 링크 이름 | 전역 유일 |
| `kind` | `can` \| `ethernet` | 예 | 링크 종류 | — |
| `bitrate` | int | 예 | 전송 속도 (CAN: kbps, Ethernet: Mbps) | > 0 |
| `nodes` | list[str] | 아니오 (기본 []) | 연결 노드 이름 | 전부 정의된 노드여야 하며, 링크 내 중복 참조 금지 |
| `frames` | list[Frame] | 아니오 (기본 []) | 링크가 소유한 L2 프레임 | 링크 내 이름 유일 |
| `switches` | list[Switch] | 아니오 (기본 []) | Ethernet 스위치 | 2개 이상 정의해도 **첫 번째만 사용** (U-2) |

### A.1.6 Frame

| 필드 | 타입 | 필수 | 설명 | 제약 |
|------|------|------|------|------|
| `name` | str | 예 | 프레임 이름 | 링크 내 유일 |
| `id` | int | 예 | CAN ID / 프레임 식별자 | ≥ 0 (CAN 중재: 작을수록 우선) |
| `dlc` | int | 예 | 데이터 길이 코드 (바이트) | ≥ 0 |
| `period_ms` | int | 예 | 주기 (t=0 첫 발생) | > 0 |
| `source` | str | 예 | 송신 노드 이름 | 해당 링크 `nodes`에 포함되어야 함 |
| `message` | str \| null | 아니오 (기본 null) | 매핑할 논리 메시지명 | 미지정 시 프레임명 = 메시지명 (A.3.3) |

### A.1.7 Switch

| 필드 | 타입 | 필수 | 설명 | 제약 |
|------|------|------|------|------|
| `name` | str | 아니오 (기본 `"default"`) | 스위치 이름 | — |
| `queue_depth` | int | 아니오 (기본 1000) | FIFO 큐 깊이 | > 0, 초과 시 테일 드롭 → `drop` 이벤트 |

### A.1.8 Gateway

| 필드 | 타입 | 필수 | 설명 | 제약 |
|------|------|------|------|------|
| `name` | str | 예 | 게이트웨이 이름 | 전역 유일 |
| `routes` | list[Route] | 아니오 (기본 []) | 라우팅 규칙 | 규칙 순서대로 매칭 시도, 명시 frame > ID 범위 우선 |

### A.1.9 Route (`from` / `to`)

| 필드 | 타입 | 필수 | 설명 | 제약 |
|------|------|------|------|------|
| `from.link` | str | 예 | 소스 링크 이름 | 정의된 링크 |
| `from.frame` | str | 아니오 | 특정 프레임 지정 | `frame` 또는 `(id_min, id_max)` 중 **정확히 하나**만 지정, 소스 링크에 정의된 프레임 |
| `from.id_min` / `from.id_max` | int | 아니오 | ID 범위 지정 | 함께 지정해야 하며 `id_min <= id_max` |
| `to.link` | str | 예 | 대상 링크 이름 | 정의된 링크 |
| `to.remap_id` | int \| null | 아니오 (기본 null) | 라우팅 시 ID 재매핑 | ≥ 0 |
| `delay_ms` | int | 아니오 (기본 0) | 라우팅 처리 지연 | ≥ 0 |

## A.2 scenario.yaml

최상위 구조:

```yaml
schema_version: 1
duration_ms: 100
seed:          # v1에서 무시
messages:    [ ... ]
assertions:  [ ... ]
```

### A.2.1 최상위

| 필드 | 타입 | 필수 | 설명 | 제약 |
|------|------|------|------|------|
| `schema_version` | int | 아니오 (기본 1) | 스키마 버전 | — |
| `duration_ms` | int | 예 | 시뮬레이션 종료 시각 (`t == duration_ms`까지 처리) | ≥ 0 |
| `seed` | int \| null | 아니오 (기본 null) | 난수 시드 | **v1에서 무시** (결정성 — 난수 미사용) |
| `messages` | list[Message] | 아니오 (기본 []) | 메시지 주입 목록 | 주입은 tx 이벤트로 기록됨 |
| `assertions` | list[Assertion] | 아니오 (기본 []) | 선언형 검증 목록 | — |

### A.2.2 Message (주입)

| 필드 | 타입 | 필수 | 설명 | 제약 |
|------|------|------|------|------|
| `t_ms` | int | 예 | 주입 시각 | ≥ 0 |
| `link` | str | 예 | 대상 링크 이름 | 정의된 링크 |
| `frame` | str | 예 | 대상 프레임 이름 | 해당 링크에 정의된 프레임 |
| `data` | dict \| null | 아니오 (기본 null) | 페이로드 데이터 (객체) | Ethernet 전송 시간 계산과 무관 (payload = DLC 바이트) |

### A.2.3 Assertion (`expect`)

| 필드 | 타입 | 필수 | 설명 | 제약 |
|------|------|------|------|------|
| `name` | str \| null | 아니오 (기본 null) | assertion 이름 (리포트·실패 메시지에 표시) | — |
| `expect.event` | `tx` \| `rx` \| `task` | 예 | 매칭할 이벤트 타입 | `task`는 `task_start`+`task_end` **둘 다** 매칭 (U-4) |
| `expect.frame` | str \| null | 아니오 | 프레임 이름 | 지정 속성은 **모두 일치**해야 매칭 |
| `expect.message` | str \| null | 아니오 | 논리 메시지명 | — |
| `expect.node` | str \| null | 아니오 | 노드 이름 | — |
| `expect.link` | str \| null | 아니오 | 링크 이름 | — |
| `expect.task` | str \| null | 아니오 | 태스크 이름 | — |
| `expect.at_ms` | int \| null | 아니오 (기본 null) | 기대 시각 | ≥ 0. 명시 시 `\|t_ms - at_ms\| <= within_ms`, **생략 시 시간 무관** |
| `expect.within_ms` | int | 아니오 (기본 0) | 허용 오차 | ≥ 0 (0 = 정확 일치) |
| `expect.count` | int | 아니오 (기본 1) | 기대 개수 | ≥ 0. **최소 n건 이상(≥)** 통과 — 시간 조건과 독립 (U-5) |

## A.3 검증 규칙 상세

스키마 검증은 Pydantic으로 수행되며, 위반 시 오류 메시지에 **파일명·줄 번호·필드 경로**가 포함된다. 오류는 입력 오류로 분류되어 CLI 종료 코드 2를 반환한다.

### A.3.1 유일성

| 대상 | 범위 | 위반 예 |
|------|------|---------|
| 노드 이름 | 파일 전체 | `duplicate node name: 'body_ecu'` |
| 링크 이름 | 파일 전체 | `duplicate link name: 'can1'` |
| 게이트웨이 이름 | 파일 전체 | `duplicate gateway name: 'gw1'` |
| 프레임 이름 | 해당 링크 내 | `duplicate frame name on link 'can1': 'door_cmd'` |
| 컴포넌트 이름 | 해당 노드 내 | `duplicate component name on node 'body_ecu': 'door_ctrl'` |
| 링크의 노드 참조 | 해당 링크 내 | 링크 `nodes`에 같은 노드 2회 지정 |

### A.3.2 참조 무결성

| 규칙 | 위반 예 |
|------|---------|
| 링크 `nodes`의 모든 이름은 정의된 노드여야 함 | `link 'can1' references unknown node(s): ['hvac_ecu']` |
| 프레임 `source`는 해당 링크에 연결된 노드여야 함 | `frame 'door_cmd' on link 'can1': source 'hvac_ecu' is not connected to the link` |
| 라우트 `from.link`/`to.link`는 정의된 링크여야 함 | `gateway 'gw1' route #0: unknown from link 'can2'` |
| 라우트 `from.frame`는 소스 링크에 정의된 프레임이어야 함 | `gateway 'gw1' route #0: frame 'door_cmd' is not defined on link 'can1'` |
| 라우트 소스는 `frame` 또는 `(id_min, id_max)` 중 정확히 하나 | `from must specify either frame or (id_min, id_max)` |
| 컴포넌트 `sends`/`receives`의 메시지는 연결 링크 프레임에 매핑되어야 함 | `component 'door_ctrl' on node 'body_ecu': message 'hvac_cmd' does not map to a frame on any connected link` |

### A.3.3 메시지-프레임 매핑 규칙

- 컴포넌트의 `sends`/`receives`는 **논리 메시지** 이름을 참조한다.
- 프레임에 `message` 필드가 명시되면 그 메시지에 매핑된다.
- `message` 미명시 시 **프레임 이름 = 메시지 이름**으로 매핑된다.
- 컴포넌트가 속한 노드에 연결된 링크들의 프레임(매핑 메시지 집합)에 없는 메시지는 스키마 오류다.

## A.4 예시 — samples/basic (문 제어 시스템)

`report` 본문과 `samples/basic/`에 있는 축약 예제. 2 ECU + CAN 1링크, 주기 프레임 2종, 주입 메시지 1건, assertion 5건.

```yaml
# architecture.yaml
schema_version: 1
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
    bitrate: 500            # kbps → tx_ms = ceil((44 + 8*4) / 500) = 1ms
    nodes: [body_ecu, door_ecu]
    frames:
      - { name: door_cmd,   id: 0x100, dlc: 4, period_ms: 10, source: body_ecu }
      - { name: door_state, id: 0x101, dlc: 4, period_ms: 10, source: door_ecu }
```

```yaml
# scenario.yaml
schema_version: 1
duration_ms: 100

messages:
  - { t_ms: 5, link: can1, frame: door_cmd, data: { state: open } }

assertions:
  # door_cmd tx: 주기 11건(t=0,10,...,100) + 주입 1건(t=5) = 12건, 첫 전송 t=0
  - name: cmd_sent
    expect: { event: tx, frame: door_cmd, link: can1, at_ms: 0, count: 12 }
  # door_cmd rx: tx 완료(+1ms) 후 door_ecu 수신 — 11건
  - name: cmd_received
    expect: { event: rx, frame: door_cmd, link: can1, node: door_ecu, at_ms: 1, count: 11 }
  # door_state tx: 같은 tick에서 door_cmd에 밀려 1ms 지연 → CAN ID 중재 관찰
  - name: state_arbitrated
    expect: { event: tx, frame: door_state, link: can1, at_ms: 1, count: 10 }
  # door_state rx: body_ecu의 door_ctrl 수신 — 10건
  - name: state_received
    expect: { event: rx, frame: door_state, link: can1, node: body_ecu, at_ms: 2, count: 10 }
  # task 이벤트: task_start 11건 + task_end 10건 → 21건 ≥ 11
  - name: task_runs
    expect: { event: task, node: body_ecu, task: main, at_ms: 0, count: 11 }
```

실행: `uv run sdv-sim run samples/basic/architecture.yaml samples/basic/scenario.yaml` → `pass` (exit 0, assertions 5/5)
