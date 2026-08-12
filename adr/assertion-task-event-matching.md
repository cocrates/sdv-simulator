# Assertion `event: task` 매칭 범위 (Assertion Task Event Matching)

## Concern
assertion에서 `expect: {event: task, ...}`를 선언하면 `task_start`와 `task_end` 중 어떤 이벤트를 매칭해야 하는가?

## Status
approved

## Context
- 검증(1차)에서 **미문서화 ASR U-4**로 식별 — assertion-evaluation-detail ADR은 "event 타입 + 지정 속성 모두 일치"를 정했으나, `event: task`가 start/end 중 무엇을 가리키는지는 미정이었음
- 스펙 인코딩(2026-08-12) 시 "task_start와 task_end 둘 다 매칭"으로 결정되었으나 ADR 검토 없이 직접 인코딩됨
- 구현: `_match_assertion`에서 `e.type not in ("task_start", "task_end")`로 양쪽 매칭 — 실행 확인 count 21 (11 start + 10 end)
- 상위 결정: assertion-evaluation-detail (D-20), assertion-grammar (event enum)

## Decision
**Option A — task_start와 task_end 둘 다 매칭**
User-approved: `event: task`는 태스크 생명주기 이벤트군(task_start+task_end)을 가리키고 `task` 속성으로 특정 태스크 한정 — D-20 "타입+속성 모두 일치"와 정합.

## Options
### Option A — task_start와 task_end 둘 다 매칭 (현재 스펙/구현)
- `event: task`는 두 이벤트 타입 모두를 매칭 대상으로 함. `task` 속성으로 특정 태스크 한정
- Pro: "이 태스크가 (시작하거나 끝나는) 실행 이벤트를 n건 가짐"이라는 종합 검증 가능, count로 시작+종료 총수 검증 가능
- Con: 시작과 종료를 구분해 검증하려면 count 산정에 의도치 않은 혼합 발생 가능

### Option B — task_start만 매칭
- `event: task`는 시작 이벤트만 매칭
- Pro: "태스크가 실행되기 시작했다"의 단일 의미 — 실행 횟수 검증에 직관적
- Con: 종료(완료) 여부를 `event: task`로는 검증 불가 — 종료 검증 수단 부재

### Option C — task_end만 매칭
- `event: task`는 종료 이벤트만 매칭
- Pro: "태스크가 완료되었다"의 단일 의미 — 완료 검증에 직관적
- Con: 시작 이벤트로는 검증 불가, 오버런 등 시작만 기록되는 사례 누락

## Tradeoffs
| | A (둘 다) | B (start만) | C (end만) |
|---|------|------|------|
| 검증 표현력 | ★★★★★ | ★★★ | ★★★ |
| 의미 단일성 | ★★ | ★★★★★ | ★★★★★ |
| count 해석 단순성 | ★★ | ★★★★★ | ★★★★★ |
| D-20 정합성 | ✓ (타입+속성 모두 일치) | △ | △ |

## Recommendation (optional)
- **Option A**: "event 타입 + 속성 모두 일치"라는 D-20 매칭 규칙과 정합 — `event: task`는 태스크 생명주기 이벤트군을 가리키고 `task` 속성으로 특정 태스크를 한정한다. 시작/종료를 분리 검증하려면 이후 assertion 확장(예: `task_phase`)에서 다룰 수 있다.

## Consequences
- `event: task` count는 task_start+task_end 합산 — 실행 확인 사례: 11 start + 10 end = 21
- 로그 스키마의 `task_start`/`task_end` 타입은 유지, assertion 문법 변경 없음

## Related ASRs
- ASR-011 — Assertion `event: task` 매칭 범위 — 본 ADR이 직접 해소
- ASR-007 — 검증·자동화 지원 — 상위 ASR

## Downstream Concerns
- [ ] **시작/종료 분리 검증 수단:** task_start만 검증하는 use case가 생기면 별도 event 값(`task_start` 직접 선언) 또는 `task_phase` 필드 도입 여부

## Related
- {project-root}/adr/assertion-evaluation-detail.md — 상위 결정 (D-20, 매칭·평가 규칙)
- {project-root}/adr/assertion-grammar.md — assertion 문법 (event enum)

## Tags
`assertion`, `task`, `matching`, `event`

## Approved
- 2026-08-12: Option A (task_start + task_end 둘 다 매칭), user confirmed
