# 성능 목표 (Performance Targets)

## Concern
v1의 성능/규모 목표는 무엇이며 순수 Python으로 충분한가?

## Status
approved

## Decision
**Option A — v1 순수 Python + 명시적 목표 규모**
User-approved: 노드 ≤ 50, 링크 ≤ 20, 프레임 ≤ 200, duration ≤ 60s, 이벤트 ≤ 100만 건에서 수 초 내 실행. 병목 시 후속 단계에서 확장 모듈 검토.

## Context
- ADR(language-tech-stack)의 Downstream: 시뮬레이션 성능 전략(순수 Python vs 확장 모듈)
- v1은 개발자 대상 검증 도구 — 대규모 실시간 시뮬레이션이 아니라 결정적 검증이 목적

## Options
### Option A — v1 순수 Python + 명시적 목표 규모
- 목표: 노드 ≤ 50, 링크 ≤ 20, 프레임 ≤ 200, 시나리오 duration ≤ 60s, 이벤트 ≤ 100만 건에서 수 초 내 실행
- 성능 병목 발생 시에만 후속 단계에서 병목 지점 확장 모듈 검토
- Pro: 구현 단순·일관, 목표 규모가 성능 검증 기준 제공, ADR-001과 정합
- Con: 대규모(수천 노드) 시나리오는 미지원

### Option B — 병목 지점 확장 모듈 선제 도입
- 이벤트 큐 등 핫 경로를 Rust/C 확장으로 설계
- Pro: 성능 여유
- Con: v1 범위 초과, 개발 비용 증가, 결정성 검증 부담

### Option C — 목표 미설정
- Pro: 없음
- Con: 성능 회귀 판정 불가, 확장 전략 결정 근거 부재

## Tradeoffs
| | A (순수 Python+목표) | B (확장 모듈) | C (미설정) |
|---|---------------------|---------------|-----------|
| 구현 비용 | 낮음 | 높음 | - |
| 성능 판정 기준 | ✓ | ✓ | ✗ |
| v1 적합성 | ✓ | ✗ | ✗ |

## Recommendation (optional)
- **Option A** 추천: v1은 "정의→실행→검증" 루프가 목적이므로 목표 규모 내 결정성이 우선

## Consequences
- 벤치마크/성능 회귀 테스트는 목표 규모 기준으로 작성
- 대규모 시나리오는 v2+ 이슈로 등록

## Related ASRs
- ASR-001 — 언어/기술 스택 — 성능 전략 세부 결정

## Downstream Concerns
- [ ] **벤치마크 시나리오:** 목표 규모를 검증하는 샘플 시나리오 작성 여부

## Related
- {project-root}/adr/language-tech-stack.md — 상위 결정 (Python)

## Tags
`performance`, `scale`, `python`

## Approved
- 2026-08-12: Option A (v1 순수 Python + 명시적 목표 규모), user confirmed
