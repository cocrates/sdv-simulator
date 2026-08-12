# 이벤트 순서·종료 경계 (Event Ordering & Termination Boundary)

## Concern
동일 시각(t_ms 동일) 이벤트를 **어떤 순서로 처리**하며, `duration_ms` 경계에서 **t == duration_ms 이벤트를 처리**하는가?

## Status
approved

## Decision
**Option A — 우선순위 → 정의 순서 → seq + inclusive 종료**
User-approved: 동일 시각은 우선순위(작을수록 우선)→파일 선언 순서→seq, t == duration_ms 이벤트까지 처리 후 종료.

## Context
- ASR-002 후속 — (t_ms, seq) 완전 순서와 duration_ms 종료는 결정됐으나, seq의 배정 근거와 경계 포함 여부 미정
- Gate 5 재검토 그룹 B-8, B-10
- task-scheduling-policy Downstream open: 동일 시각·동일 우선순위 순서

## Options
### Option A — 우선순위 → 정의 순서 → seq + inclusive 종료
- 처리 순서: 태스크 우선순위(작을수록 우선) → 파일 선언 순서(노드/컴포넌트/프레임 정의 순) → seq(생성 순서)
- 종료: `t == duration_ms`의 이벤트까지 처리 후 종료 (inclusive)
- Pro: 정의 순서가 결정적이고 사용자 제어 가능, duration 경계 이벤트 검증 직관
- Con: "선언 순서" 개념을 문서화 필요

### Option B — seq만 + inclusive 종료
- 순서: (t_ms, seq)만 사용 — seq는 이벤트 생성 순서
- Pro: 단순
- Con: 같은 시각 이벤트 간 순서를 사용자가 제어 불가(엔진 내부 생성 순서에 의존)

### Option C — 정의 순서 + exclusive 종료
- 순서는 A와 동일, 종료는 `t == duration_ms` 미처리
- Pro: "duration까지" 경계가 깔끔
- Con: duration 직전에 스케줄된 이벤트 검증 불가 — assertion at_ms=duration 실패

## Tradeoffs
| | A (우선순위→정의→seq, inclusive) | B (seq만, inclusive) | C (정의 순서, exclusive) |
|---|------|------|------|
| 사용자 제어 | ★★★★★ | ★★ | ★★★★★ |
| 단순성 | ★★★ | ★★★★★ | ★★★ |
| 경계 검증 UX | ★★★★★ | ★★★★★ | ★★ |

## Recommendation (optional)
- **Option A**: 선언 순서를 결정적 순서의 주 근거로 사용 — 사용자가 정의 파일로 순서를 제어할 수 있어야 검증 도구로 유용.

## Consequences
- seq는 여전히 로그에 기록 — 동률 시 최종 순서는 seq
- exclusive 종료는 assertion at_ms == duration_ms를 불가능하게 하므로 배제

## Related ASRs
- ASR-002 — 시뮬레이션 엔진 모델 — 이벤트 순서·종료 경계

## Downstream Concerns
- [ ] **선언 순서의 범위:** 같은 노드 내 컴포넌트 vs 전역 정의 순서 중 어떤 기준인지 구체화

## Related
- {project-root}/adr/simulation-time-model.md, task-scheduling-policy.md — 상위 결정

## Tags
`ordering`, `determinism`, `termination`, `boundary`

## Approved
- 2026-08-12: Option A (정의 순서 + inclusive 종료), user confirmed
