# 같은 시각 비-태스크 이벤트 순서 (Same-Tick Non-Task Event Ordering)

## Concern
동일 `t_ms`에서 태스크 이벤트(`task_start`/`task_end`)와 비-태스크 이벤트(`tx`/`rx`/`drop` 등)가 공존할 때, 비-태스크 이벤트는 어떤 위치에서 처리되는가?

## Status
approved

## Context
- 검증(1차)에서 **미문서화 ASR U-1**로 식별 — 기존 D-19(event-ordering-boundary)는 "태스크 우선순위 → 파일 선언 순서 → seq"만 결정, 태스크↔비-태스크 상대 순서는 미정이었음
- 스펙 인코딩(2026-08-12) 시 "비-태스크 이벤트는 모든 태스크 이벤트 뒤"로 결정되었으나 ADR 검토 없이 직접 인코딩됨
- 구현: `MAX_PRIO = 1<<30` (태스크 최대 우선순위보다 큰 가상 우선순위) — 실행 확인: t=0에서 `task_start`(seq 3) → `tx`(seq 10)
- 상위 결정: event-ordering-boundary (D-19), task-scheduling-policy

## Decision
**Option A — 비-태스크는 모든 태스크 뒤**
User-approved: 같은 시각 비-태스크 이벤트는 가상 우선순위 2^30으로 모든 태스크 이벤트 뒤에 처리 — 태스크 실행의 부수효과(전송)가 관측(tx)보다 먼저 처리되어 원인→결과 순서 보장.

## Options
### Option A — 비-태스크는 모든 태스크 뒤 (현재 스펙/구현)
- 비-태스크 이벤트에 가상 우선순위 `2^30` 부여 → 모든 태스크 이벤트 후 처리, 비-태스크 간에는 파일 선언 순서 → seq
- Pro: 태스크 실행의 부수효과(컴포넌트 `ctx.send` → tx)가 같은 tick의 tx보다 먼저 처리되어 "원인 → 결과" 관측 순서가 자연스러움
- Con: 태스크가 없는 구간의 tx를 기대하는 assertion은 영향 없으나, 태스크와 tx 순서에 의존하는 검증은 문서화된 규칙에 의존

### Option B — 파일 선언 순서로 통합 (우선순위 무시)
- 태스크·비-태스크를 구분하지 않고 동일 시각 이벤트를 전부 파일 선언 순서로 처리
- Pro: 규칙 단일화
- Con: 컴포넌트 `ctx.send` 결과 tx가 같은 tick의 이전 태스크 tx보다 뒤에 오는지 보장 불가 — 관측 순서가 정의 순서에 민감

### Option C — 비-태스크를 모든 태스크 앞에
- 비-태스크에 최소 우선순위 부여
- Pro: 구현 대칭
- Con: 태스크가 생성한 tx가 관측될 때까지 같은 tick에서 다음 이벤트들이 이미 처리됨 — 원인-결과 순서가 역전될 수 있음

## Tradeoffs
| | A (비-태스크 뒤) | B (선언 순서 통합) | C (비-태스크 앞) |
|---|------|------|------|
| 원인→결과 관측 순서 | ★★★★★ | ★★★ | ★ |
| 규칙 단순성 | ★★★ | ★★★★★ | ★★★ |
| 결정성 | ★★★★★ | ★★★★★ | ★★★★★ |
| D-19 정합성 | ✓ (상위 규칙 확장) | △ (재정의) | △ (역전) |

## Recommendation (optional)
- **Option A**: 태스크 실행의 부수효과(전송)를 같은 tick의 관측(tx)보다 앞서 처리하는 것이 "원인 → 결과" 검증 UX에 가장 자연스럽고, 기존 D-19의 우선순위 체계를 확장하므로 정합성도 유지된다.

## Consequences
- `tx`/`rx`/`drop` 등 비-태스크 이벤트의 순서는 모든 태스크 이벤트 뒤 → 태스크 없음 구간에서는 선언 순서 → seq
- 가상 우선순위 `2^30`은 태스크 우선순위 범위(사용자 정의 가능)와 충돌하지 않음 (v1 우선순위는 작은 정수 가정)

## Related ASRs
- ASR-008 — 동일 시각 비-태스크 이벤트 순서 — 본 ADR이 직접 해소
- ASR-002 — 시뮬레이션 엔진 모델 — 상위 ASR (이벤트 순서·종료 경계)

## Downstream Concerns
- [ ] **컴포넌트 tx vs 주기 프레임 tx 순서:** 같은 tick에서 컴포넌트 `ctx.send`로 생성된 tx와 주기 프레임 tx가 동시에 있으면 파일 선언 순서 → seq로 정렬되는데, "원인-결과"가 깨지는 사례가 있는지 문서화 필요

## Related
- {project-root}/adr/event-ordering-boundary.md — 상위 결정 (D-19, 동일 시각 순서·종료 경계)
- {project-root}/adr/task-scheduling-policy.md — 태스크 우선순위 체계

## Tags
`ordering`, `event`, `task`, `determinism`

## Approved
- 2026-08-12: Option A (비-태스크는 모든 태스크 뒤), user confirmed
