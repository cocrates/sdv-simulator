# 태스크 오버런 정책 (Task Overrun Policy)

## Concern
주기 태스크가 오버런(주기 시작 시각 초과) 발생 시 **다음 인스턴스를 어떻게 스케줄링**하는가?

## Status
approved

## Decision
**Option A — 절대 주기 유지 + 인스턴스 스킵**
User-approved: 오버런은 overrun 이벤트로 기록, 다음 실행은 원래 절대 주기(t=0 기준) 기준, 놓친 주기 인스턴스는 스킵.

## Context
- ASR-005 후속 — task-scheduling-policy(비선점 + wcet_ms + overrun 기록)는 결정됐으나 오버런 후속 처리 미정
- Gate 5 재검토 그룹 B-6
- 결정성(DES)과 정수 ms 시간 모델 전제

## Options
### Option A — 절대 주기 유지 + 인스턴스 스킵
- 다음 실행은 원래 주기(절대 t=0 기준). 오버런으로 밀리지 않음 — 놓친 주기는 스킵(실행 안 함)
- Pro: 결정적·단순, AUTOSAR 주기 의미(절대 주기)와 정합, 오버런 누적 없음
- Con: 오버런 직후 실행 기회 손실(현실 RTOS와 상이 — v1 허용)

### Option B — 상대 주기(밀림)
- 오버런 완료 시각 + period에 다음 실행
- Pro: 실행 기회 보존
- Con: 오버런 연쇄(주기 어긋남), 로그 해석 복잡, 예측 어려움

### Option C — 오버런 시 시뮬레이션 실패
- 오버런 발생 시 결과를 실패 처리
- Pro: 오버런을 하드 에러로 취급
- Con: PRD 목적(오버런 관찰·검증)과 상충 — 오버런 자체를 assertion 대상으로 보는 용도 차단

## Tradeoffs
| | A (절대+스킵) | B (상대 밀림) | C (실패) |
|---|------|------|------|
| 결정성·단순성 | ★★★★★ | ★★★ | ★★★★★ |
| AUTOSAR 정합 | ★★★★★ | ★★ | — |
| 오버런 검증 용도 | ★★★★★ | ★★★ | ✗ |

## Recommendation (optional)
- **Option A**: overrun 이벤트로 관찰하되 주기는 절대 기준 유지 — 검증 도구 목적에 최적.

## Consequences
- 오버런 판정 기준: `wcet_ms` 종료 시각 > 원래 주기 시작 시각
- 스킵된 인스턴스는 별도 이벤트 없음 (overrun 이벤트만 기록)

## Related ASRs
- ASR-005 — 앱 런타임 모델 — 오버런 후속 스케줄링

## Downstream Concerns
- [ ] **메시지 핸들러 오버런:** on_message 실행이 wcet를 넘을 때도 동일 정책 적용 여부

## Related
- {project-root}/adr/task-scheduling-policy.md — 상위 결정 (비선점 + wcet + overrun)

## Tags
`scheduling`, `overrun`, `task`, `periodic`

## Approved
- 2026-08-12: Option A (절대 주기 유지 + 인스턴스 스킵), user confirmed
