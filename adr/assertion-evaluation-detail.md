# Assertion 평가 세부 (Assertion Evaluation Detail)

## Concern
assertion 평가의 세부 규칙 — **count의 대상 범위, at_ms 생략 의미, 실패 메시지 형식**은 무엇인가?

## Status
approved

## Decision
**Option A — count=전체 로그 총수 + 시간 무관 기본 + 실패 상세**
User-approved: at_ms 생략 시 시간 무관, count는 전체 로그 매칭 총수(시간 조건과 독립), 실패 메시지에 매칭 이벤트 최대 3건.

## Context
- ASR-007 후속 — expect{event, 속성, at_ms, within_ms, count} 문법은 결정됐으나 평가 규칙 미정
- Gate 5 재검토 그룹 B-9 — `at_ms` 생략 의미(시간 무관)가 ADR(assertion-grammar)에만 있고 스펙 미인코딩(SSOT 위반)
- assertion-grammar Downstream open: 실패 메시지 형식

## Options
### Option A — count=전체 로그 총수 + 시간 무관 기본 + 실패 상세
- 매칭: event 타입 + 지정 속성(frame/message/node/link/task) 모두 일치
- 시간: `at_ms` 명시 시 `|t_ms - at_ms| <= within_ms`(기본 0 = 정확 일치), `at_ms` 생략 시 시간 무관
- count: 매칭 이벤트의 **전체 로그 총수** 검증 (시간 조건과 독립)
- 실패 메시지: 매칭 이벤트 최대 3건(t_ms, seq, 속성) + 기대/실제 시각 + 기대/실제 count
- Pro: 예측 단순, SSOT 갭 해소, CI 디버깅 UX
- Con: count와 at_ms가 독립(같은 윈도우 count 아님) — 의도 설명 필요

### Option B — count=within_ms 윈도우 내
- count는 시간 조건(윈도우) 내 매칭 수
- Pro: "지정 시간대에 n건"이라는 직관
- Con: at_ms 생략 시 윈도우 의미 모호, 시간 조건 중첩 해석 복잡

### Option C — at_ms 필수
- at_ms 생략 시 스키마 오류
- Pro: 모호성 제거
- Con: "이벤트 존재 여부만" 검증 케이스 표현 불가 — 표현력 저하

## Tradeoffs
| | A (전체 count+시간 무관) | B (윈도우 count) | C (at_ms 필수) |
|---|------|------|------|
| 예측 단순성 | ★★★★★ | ★★★ | ★★★★ |
| 표현력 | ★★★★★ | ★★★★ | ★★★ |
| SSOT(스펙 인코딩) | ✓ | ✓ | ✓ |

## Recommendation (optional)
- **Option A**: 시간 검증과 개수 검증을 직교(독립)로 — 해석이 단순하고 assertion-grammar의 "첫 매칭 이벤트 시간 검증 + count 개수 검증"과 정확히 일치.

## Consequences
- "count + at_ms" 조합은 "시간대 관계없이 총 n건" 의미
- `at_ms` 생략 시 시간 무관 — Spec에 인코딩 필요 (SSOT 갭 해소)

## Related ASRs
- ASR-007 — 검증·자동화 지원 — 평가 규칙

## Downstream Concerns
- [ ] **다중 매칭 속성의 조합 규칙:** frame+message 동시 지정 시 AND인지 오류인지

## Related
- {project-root}/adr/assertion-grammar.md — 상위 결정 (문법)

## Tags
`assertion`, `evaluation`, `verification`, `count`

## Approved
- 2026-08-12: Option A (전체 count + 시간 무관 + 실패 상세), user confirmed
