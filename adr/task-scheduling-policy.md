# 태스크 스케줄링 정책 (Task Scheduling Policy)

## Concern
가상 노드의 주기 태스크를 어떤 정책으로 실행·스케줄링할 것인가?

## Status
approved

## Decision
**Option A — 비선점 + wcet_ms(기본 0) + overrun 기록**
User-approved: 태스크는 이벤트 큐에서 순차 실행(비선점). wcet_ms만큼 시간 경과, 주기 초과 시 overrun 이벤트 + 경고.

## Context
- ASR-005(RTE 스타일) 후속 — 앱 런타임의 실행 의미론 결정
- ADR(simulation-engine-model)의 Downstream: 앱 태스크 스케줄링 정책(주기·우선순위·오버런)
- 결정성 (ASR-002)과 단일 스레드 실행이 전제

## Options
### Option A — 비선점 + wcet_ms(기본 0) + overrun 기록
- 태스크 실행은 이벤트 큐에서 순차 처리(비선점). 실행 시간 `wcet_ms`(기본 0=즉시)만큼 시뮬레이션 시간 경과
- 주기 시작 시각을 넘기면 `overrun` 이벤트 기록 + 리포트 경고
- Pro: DES 엔진과 정합, 결정성 보장, 오버런 관찰 가능
- Con: 실제 RTOS 선점 동작과 상이 (v1 목적상 허용)

### Option B — 선점형 스케줄링
- 높은 우선순위 태스크가 실행 중인 낮은 우선순위 태스크를 선점
- Pro: RTOS 동작에 더 근접
- Con: 실행 중단/재개 상태 모델 필요, 결정성 검증 복잡도 증가

### Option C — 라운드로빈 (우선순위 무시)
- 정의 순서대로 순환 실행
- Pro: 구현 최단
- Con: 우선순위 의미 상실 (ASR-005 RTE 스타일과 불일치)

## Tradeoffs
| | A (비선점) | B (선점) | C (RR) |
|---|-----------|----------|--------|
| 결정성 | ★★★★★ | ★★★ | ★★★★★ |
| DES 정합성 | ★★★★★ | ★★★ | ★★★ |
| RTOS 근접성 | ★★ | ★★★★ | ★ |
| 구현 비용 | 낮음 | 높음 | 최저 |

## Recommendation (optional)
- **Option A** 추천: RTE 주기 태스크의 기본 의미(주기·우선순위·오버런 관찰)를 결정적으로 제공

## Consequences
- 수신 메시지 핸들러도 동일 이벤트 큐에서 실행 (컴포넌트 priority 반영)
- 우선순위 역전/데드라인 미스 메커니즘은 v1 제외 (overrun 관찰까지만)

## Related ASRs
- ASR-005 — 앱 런타임 모델 — 스케줄링 정책 세부 결정

## Downstream Concerns
- [ ] **동일 시각·동일 우선순위 순서:** 컴포넌트 정의 순서 반영 여부 확정

## Related
- {project-root}/adr/simulation-engine-model.md — 상위 결정 (DES)
- {project-root}/adr/app-runtime-model.md — 상위 결정 (RTE 스타일)

## Tags
`scheduling`, `task`, `rte`, `priority`, `overrun`

## Approved
- 2026-08-12: Option A (비선점 + wcet_ms + overrun 기록), user confirmed
