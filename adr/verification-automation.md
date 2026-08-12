# 검증·자동화 지원 (Verification & Automation)

## Concern
자동 검증(assertion)과 CI 자동화(결정적 로그, 종료 코드)를 어떻게 지원할 것인가?

## Status
approved

## Context
- 개발자 대상 검증 도구의 핵심 가치 = "무인 실행"
- CI에서 시뮬레이션 결과를 자동 판정할 수 있어야 함
- ASR-006: 공개 API 계약(이벤트 스트림)과 정합
- (대화에서 Direct Input으로 확정된 결정을 ADR로 사후 문서화한 기록)

## Decision
**Option C — 선언형 assertion + JSON 이벤트 스트림**
User-approved: 시나리오 YAML에 기대값 assertion 선언, 실행 후 자동 평가. 결정적 JSON 이벤트 로그 출력. CLI 종료 코드(0=pass, 1=fail)로 CI 판정. 고급 검증은 라이브러리 임베드로 이벤트 스트림 직접 소비.

## Options
### Option A — 선언형 assertion
- 시나리오 YAML에 기대값 선언 (예: "메시지 X가 10ms 내에 노드 Y 도달")
- Pro: CLI 사용자에게 직관적인 1차 검증 UX, CI 판정 자동화 용이
- Con: 복잡한 조건의 유연성 제한

### Option B — 이벤트 스트림 외부 검증
- 엔진이 결정적 JSON 이벤트 로그 출력, 검증 로직은 사용자 도구가 작성
- Pro: 최대 유연성
- Con: 사용자 부담, 1차 검증 경험 부재

### Option C — A + B 결합
- 선언형 assertion(기본) + JSON 이벤트 스트림(고급 검증)
- Pro: 엔진이 어차피 이벤트를 생성하므로 추가 비용 낮음, 유연성 최대
- Con: assertion 문법·로그 스키마 정의 필요

## Tradeoffs
| | 선언형 (A) | 스트림 (B) | A+B (C) |
|---|-----------|------------|---------|
| CLI 1차 검증 UX | ★★★★★ | ★★ | ★★★★★ |
| 고급 검증 유연성 | ★★ | ★★★★★ | ★★★★★ |
| 구현 비용 | 낮음 | 낮음 | 중간 |
| CI 자동 판정 | ★★★★★ | ★★★ | ★★★★★ |

## Recommendation (optional)
- **A + B 결합 (C)** — Direct Input으로 확정됨

## Consequences
- assertion 문법과 JSON 로그 스키마 정의가 필요 (후속 상세 설계)
- 종료 코드 규약(0=pass, 1=fail)이 CI 파이프라인 계약

## Related ASRs
- ASR-007 — 검증·자동화 지원 — 이 ADR이 결정을 문서화

## Downstream Concerns
- [ ] **assertion 문법 정의:** 시간 제약, 메시지 속성 매칭, 이벤트 개수 표현
- [ ] **로그 스키마 정의:** 이벤트 타입(송신/수신/태스크/결과), 타임스탬프 포맷

## Related
- {project-root}/spec/sdv-sim-v1.md — Spec 반영됨

## Tags
`verification`, `assertion`, `ci`, `json`, `direct-input`

## Approved
- 2026-08-12: Option C (선언형 assertion + JSON 이벤트 스트림), user confirmed via Direct Input (retroactive ADR documentation)
