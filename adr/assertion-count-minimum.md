# Assertion count 비교 연산 (Assertion Count Minimum)

## Concern
assertion의 `count: n` 검증은 매칭 이벤트 수가 **정확히 n**이어야 하는가, **최소 n건 이상**이어야 하는가?

## Status
approved

## Context
- 검증(1차)에서 **미문서화 ASR U-5**로 식별 — assertion-evaluation-detail ADR은 "count = 매칭 이벤트의 전체 로그 총수 검증"을 정했으나 **비교 연산(== vs ≥)은 미정**이었음
- 스펙 인코딩(2026-08-12) 시 "최소 n건 이상 (≥, 초과는 실패 아님)"으로 결정 — 생성 시 해석 ③(≥)과 정합
- 구현: `len(matched) >= exp.count`
- 상위 결정: assertion-evaluation-detail (D-20), assertion-grammar (count 필드)

## Decision
**Option A — 최소 n건 이상 (≥)**
User-approved: `count: n`은 매칭 이벤트 ≥ n이면 통과 — "최소 발생 보장"이 assertion의 기본 의도, 종료 경계(inclusive) 내성, 공식 예시(12건) 정합.

## Options
### Option A — 최소 n건 이상 (≥) (현재 스펙/구현)
- 매칭 이벤트 수가 `count` 이상이면 통과. 초과는 실패 아님
- Pro: 주기 이벤트 수가 duration 경계(마지막 인스턴스 포함 여부)로 미세하게 달라질 수 있어도 통과 — 공식 예시(주기 11건 + 주입 1건 = 12건)와 정합, 검증 의도("최소한 n건 발생")에 직관적
- Con: "정확히 n건 발생"을 검증할 수 없음 — 과잉 발생(원치 않는 추가 전송)을 잡아내지 못함

### Option B — 정확히 n건 (==)
- 매칭 이벤트 수가 `count`와 정확히 일치해야 통과
- Pro: 결정적 시뮬레이션에서 정밀 검증 가능 — 원치 않는 추가 이벤트도 실패로 검출
- Con: 종료 경계(inclusive t==duration)나 부수 이벤트(예: 주입+주기 중복)로 수가 어긋나면 의도와 무관하게 실패 — 공식 예시 검증 시 "12건"이 정확히 맞아야 함

### Option C — 최대 n건 이하 (≤)
- 매칭 이벤트 수가 `count` 이하이면 통과
- Pro: "n건 이하로만 발생" 상한 검증 가능
- Con: 최소 보장이 없어 "이벤트가 아예 없어도 통과" — 대부분 검증 의도와 반대

## Tradeoffs
| | A (≥ 최소) | B (== 정확) | C (≤ 최대) |
|---|------|------|------|
| 최소 보장 검증 | ✓ | ✓ | ✗ |
| 과잉 발생 검출 | ✗ | ✓ | ✓ |
| 경계·부수 이벤트 내성 | ★★★★★ | ★★ | ★★★★★ |
| D-20/공식 예시 정합 | ✓ | △ | ✗ |

## Recommendation (optional)
- **Option A**: "최소 n건 발생"이 assertion의 기본 의도(검증하려는 동작이 n번 일어남을 보장)와 일치하고, 종료 경계에서의 인스턴스 수 변동(inclusive 종료)에 강건하다. 정확한 개수 검증이 필요한 사용자는 향후 `count_exact` 등 별도 필드로 확장 가능.

## Consequences
- `count: n` = 매칭 이벤트 ≥ n — 스펙 문구 "최소 n건 이상"으로 인코딩됨
- 공식 예시 `count: 12`(주기 11 + 주입 1)는 ≥ 의미에서 통과

## Related ASRs
- ASR-012 — Assertion count 비교 연산 — 본 ADR이 직접 해소
- ASR-007 — 검증·자동화 지원 — 상위 ASR

## Downstream Concerns
- [ ] **정확 개수 검증 수단:** == 검증 use case(과잉 전송 차단)가 필요하면 `count_exact` 필드 도입 여부 — v1 범위 결정

## Related
- {project-root}/adr/assertion-evaluation-detail.md — 상위 결정 (D-20, count 대상·평가 규칙)
- {project-root}/adr/assertion-grammar.md — assertion 문법 (count 필드)

## Tags
`assertion`, `count`, `evaluation`, `semantics`

## Approved
- 2026-08-12: Option A (최소 n건 이상, ≥), user confirmed
