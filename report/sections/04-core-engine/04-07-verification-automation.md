# 4.7 검증과 자동화 (assertion · 이벤트 로그 · 리포트)

시뮬레이션의 결과는 **이벤트 로그**로 남고, **assertion 평가**와 **리포트 생성**으로
검증·자동화에 연결된다.

## 이벤트 로그

실행 중 모든 사건은 단일 `Event`로 기록된다: `(t_ms, seq, type, node, link, frame, task, data)`.
이벤트 종류는 7가지다.

| type | 의미 |
|------|------|
| `tx` | 프레임 전송 시작 |
| `rx` | 프레임 수신 완료 |
| `task_start` | 주기 태스크 실행 시작 |
| `task_end` | 주기 태스크 실행 완료 |
| `drop` | 프레임 드롭 (Ethernet 큐 초과, 홉 제한 초과) |
| `overrun` | 태스크 오버런 (4.6절) |
| `log` | 컴포넌트가 기록한 로그 (`TaskContext.log`) |

데이터 페이로드는 있으면 포함되고, 없으면 `null`로 생략된다. 로그는 이벤트 생성 순서가 아니라
`(t_ms, seq)` 정렬로 저장되어 재생(replay)이 결정적이다 (7.4절).

## Assertion 평가

시나리오의 `assertions` 각 항목은 다음 조건을 모두 만족하면 통과한다.

1. **매칭**: `expect.event`와 일치하는 이벤트가 존재한다. 이벤트별 추가 속성(`frame`, `link`,
   `node`, `task`, `message`)이 지정되면 그 속성도 일치해야 한다. `event: task`는
   `task_start`와 `task_end` **둘 모두**와 매칭한다.
2. **최소 개수**: 매칭된 이벤트 수가 `count` 이상이다 (D-20: "이상" 의미).
   `count`는 기본 1.
3. **시간**: `at_ms`가 지정되면, 첫 매칭 이벤트의 시각이 `at_ms ± within_ms` 안에 있다.
   (`within_ms` 기본 0)

모든 assertion이 통과하면 결과는 `pass`, 하나라도 실패하면 `fail`이다.

## 리포트

리포트는 이벤트 로그에서 집계된다. 구조는 4가지 파트로 나뉜다.

| 파트 | 내용 |
|------|------|
| **Summary** | `duration_ms`, 결과(`pass`/`fail`), 이벤트 총 개수 |
| **LinkReport** | 링크별 `kind`, tx/rx/drop/supersede 횟수, 버스 점유율(`bus_load_percent`) |
| **TaskReport** | 태스크별 노드·주기, `run_count`, `overrun_count` |
| **AssertionResult** | assertion별 이름·상태·상세(첫 매칭 시각, 실패 사유) |

리포트는 CLI 출력(5장), 서버 `/api/report`(6장)을 통해 사용자에게 제공되며, 이벤트 로그만으로
재구성 가능한 부분과 아키텍처 정보가 필요한 부분은 M-1 규칙(6.5절)으로 구분된다.

## CI 계약

자동 검증의 최종 인터페이스는 **종료 코드**이다. `run` 명령은 assertion 결과에 따라
0(pass) / 1(fail)을 반환하므로, CI 파이프라인은 로그·리포트를 파싱하지 않고도 성공 여부를
판정할 수 있다 (5장).
