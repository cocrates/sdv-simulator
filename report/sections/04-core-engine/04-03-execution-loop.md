# 4.3 실행 루프

`Simulator.run()`은 초기 스케줄 → 이벤트 루프 → 정리(검증·리포트)의 세 단계로 진행된다.

```mermaid
sequenceDiagram
    participant Caller as 호출자 (CLI/서버)
    participant Sim as Simulator
    participant Heap as 이벤트 큐 (heap)
    participant Link as LinkRuntime

    Caller->>Sim: run()
    Note over Sim, Heap: ① 초기 스케줄 (t=0 기준)
    Sim->>Heap: 주기 프레임 tx_attempt (t=0, 이후 period_ms마다)
    Sim->>Heap: 주기 태스크 task_start (t=0, 이후 period_ms마다)
    Sim->>Heap: 시나리오 주입 tx_attempt (t=t_ms)

    Note over Sim, Heap: ② 이벤트 루프 (t <= duration_ms)
    loop 큐에 이벤트가 있고 t <= duration_ms
        Heap-->>Sim: (t, priority, decl, seq) 순으로 pop
        alt task_start
            Sim->>Sim: on_periodic 실행, task_end 스케줄
        else task_end
            Sim->>Sim: 오버런 검사·기록
        else tx_attempt
            Link->>Link: pending에 추가 (arrival_t, arrival_seq)
        else rx
            Sim->>Sim: 수신자 on_message 전달
        else link_service
            Sim->>Link: 웨이크 (큐 후속 전송 기회)
        end
        Sim->>Link: tick 종료 후 drain(t) — 버스/스위치 배치 해소
    end

    Note over Sim: ③ 정리
    Sim->>Sim: 이벤트 (t_ms, seq) 오름차순 정렬
    Sim->>Sim: assertion 평가 + 리포트 생성
    Sim-->>Caller: SimulationResult
```

## ① 초기 스케줄

- 각 링크의 **주기 프레임**: 첫 전송 시도 `t=0`, 이후 `period_ms` 간격으로 반복 스케줄된다.
  (`frame.period_ms == 0`이면 1회만 전송)
- 각 컴포넌트의 **주기 태스크**: 첫 `task_start`가 `t=0`, 이후 `period_ms` 간격으로 반복된다.
- **시나리오 주입**: `scenario.messages`의 각 항목이 해당 `t_ms`에 `tx_attempt`로 스케줄된다.

## ② 이벤트 루프

시각 `t`의 이벤트들을 큐 순서대로 꺼내 처리한 뒤, 같은 시각의 통신 동작을 **일괄 해소(drain)**한다.

- **task_start** — 태스크 실행을 시작한다 (4.6절). `on_periodic()` 호출과 `task_end` 스케줄.
- **task_end** — 태스크 완료 시각에 오버런을 판정·기록한다 (4.6절).
- **tx_attempt** — 전송 시도를 해당 링크의 `pending`에 추가한다. 실제 버스 동작은 drain에서 처리된다.
- **rx** — 링크의 수신 완료 시각에, 해당 메시지를 `receives`하는 컴포넌트들의 `on_message()`를 호출한다.
- **link_service** — 동작 없는 웨이크-업 이벤트. 버스가 비는 시각에 큐에 대기 중인 프레임이
  전송될 기회를 얻도록 한다.
- **drain(t)** — tick의 마지막에 각 링크가 대기 중인 시도들을 버스/스위치 규칙(4.4절)대로 배치하고
  `tx`/`rx`/`drop`/`supersede` 이벤트를 스케줄한다. 같은 시각의 전송들이 버스 경쟁(중재/큐잉)을
  동시에 놓고 결정되는 지점이다.

## ③ 정리

- 모든 이벤트는 `(t_ms, seq)` 오름차순으로 정렬되어 결과에 담긴다.
- assertion을 평가하고(4.7절) 리포트를 생성한 뒤 `SimulationResult`를 반환한다.
