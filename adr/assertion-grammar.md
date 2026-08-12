# Assertion 문법 (Assertion Grammar)

## Concern
시나리오의 자동 검증 assertion을 어떤 문법으로 표현할 것인가?

## Status
approved

## Decision
**Option A — YAML 선언형 expect 블록**
User-approved: expect {event, 속성, at_ms, within_ms, count} 구조. 종료 후 첫 매칭 이벤트 기준 시간 검증 + count 개수 검증.

## Context
- ASR-007(선언형 assertion) 후속 — 검증 UX의 1차 인터페이스
- PRD 제약: 시뮬레이션 결과는 자동화 검증(assertion)에 사용 가능해야 함
- ADR(verification-automation)의 Downstream: assertion 문법 정의(시간 제약, 메시지 속성, 이벤트 개수)

## Options
### Option A — YAML 선언형 expect 블록
- `assertions: [{name?, expect: {event, frame/message/node/link/task, at_ms, within_ms, count}}]`
- 평가: 종료 후 로그에서 첫 매칭 이벤트 기준 시간 검증 + count 개수 검증
- Pro: 시나리오 YAML과 동일 문법(일관성), 파싱 간단, CI에서 검토 용이
- Con: 복잡한 논리 표현 제한 (v1에는 충분)

### Option B — 내장 DSL 문자열
- `assert: "rx door-state-frame at 10ms within 5ms count 1"` 형태의 문자열 식
- Pro: 표현력·간결성
- Con: 파서 구현 필요, YAML 스키마 검증에서 벗어남, 오타 위험

### Option C — Python 콜백 검증
- 시나리오에 파이썬 검증 함수 참조, 이벤트 스트림 소비
- Pro: 최대 유연성, 복잡 검증 가능
- Con: 선언성 상실, YAML-only 검증 불가 (CI 무인 실행 UX 저하)

## Tradeoffs
| | A (선언형) | B (DSL) | C (콜백) |
|---|-----------|---------|----------|
| 선언성 | ★★★★★ | ★★★★ | ★★ |
| 구현 비용 | 낮음 | 중간 | 중간 |
| CI/무인 실행 UX | ★★★★★ | ★★★★ | ★★★ |
| 복잡 검증 표현 | ★★ | ★★★★ | ★★★★★ |

## Recommendation (optional)
- **Option A** 추천: PRD 성공 기준 2(시간 제약·메시지 속성·이벤트 개수)를 충족하는 최소 선언형 문법. 복잡 검증은 이벤트 스트림 라이브러리 소비로 보완 (ASR-007의 C 결정과 정합)

## Consequences
- 논리 결합(and/or)과 이벤트 순서(sequence) 검증은 v1 제외 (Spec Out of Scope에 기록)
- `within_ms` 기본 0 = 정확 일치, `at_ms` 생략 시 시간 무관

## Related ASRs
- ASR-007 — 검증·자동화 지원 — assertion 문법 세부 결정

## Downstream Concerns
- [ ] **assertion 실패 메시지 형식:** 매칭 실패 사유를 리포트에 어떻게 표기할지

## Related
- {project-root}/adr/verification-automation.md — 상위 결정 (선언형 assertion + JSON 스트림)

## Tags
`assertion`, `verification`, `scenario`, `yaml`

## Approved
- 2026-08-12: Option A (YAML 선언형 expect 블록), user confirmed
