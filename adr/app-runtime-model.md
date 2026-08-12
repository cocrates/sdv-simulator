# 앱 런타임 모델 (App Runtime Model)

## Concern
가상 노드에서 SW 컴포넌트(앱)를 어떤 실행 모델로 구동할 것인가?

## Status
approved

## Context
- "앱 런타임"의 의미를 정의: 컴포넌트 API, 수명주기, 통신 인터페이스
- ASR-002(DES 하이브리드: 주기 태스크를 이벤트로 스케줄링)와 정합 필수
- 결정성(determinism) 요구 — 스레드 기반 비결정성 허용 불가
- (대화에서 Direct Input으로 확정된 결정을 ADR로 사후 문서화한 기록)

## Decision
**Option C — 주기 태스크 + 이벤트 핸들러 (RTE 스타일)**
User-approved: 컴포넌트는 주기 태스크(주기·우선순위)와 메시지 수신 핸들러를 가짐. 스케줄러가 태스크 실행을 이벤트 큐에 넣어 결정적으로 실행. AUTOSAR RTE 관행과 정합.

## Options
### Option A — 메시지 구동 컴포넌트
- 컴포넌트는 메시지 수신 시 호출되는 핸들러만 가짐
- Pro: 단순, 결정적, DES 엔진과 자연 정합
- Con: 주기적 동작(센서 폴링, 주기 제어) 표현 불가

### Option B — 스레드/태스크 기반
- 각 컴포넌트가 실제 스레드로 실행
- Pro: 현실적인 동시성 표현
- Con: 스레드 스케줄링 비결정성 → 결정성 요구 위반, 복잡도 증가

### Option C — 주기 태스크 + 이벤트 핸들러 (RTE 스타일)
- 주기 태스크(고정 주기 실행) + 메시지 수신 핸들러, 스케줄러가 이벤트로 스케줄
- Pro: AUTOSAR RTE 관행과 일치, DES(ASR-002)와 정합, 결정적
- Con: 실제 OS 스레드 동작과는 차이 (시뮬레이션 수준)

## Tradeoffs
| | 메시지 구동 (A) | 스레드 기반 (B) | RTE 스타일 (C) |
|---|----------------|-----------------|----------------|
| 주기 태스크 표현 | ✗ | ✓ | ✓ |
| 결정성 | ✓ | ✗ | ✓ |
| 자동차 SW 관행 정합 | ★★★ | ★★★★ | ★★★★★ |
| DES 엔진 정합 | ★★★★★ | ★★ | ★★★★★ |

## Recommendation (optional)
- **RTE 스타일 (C)** — Direct Input으로 확정됨

## Consequences
- 컴포넌트 작성자는 주기 콜백 + 메시지 핸들러만 구현
- 스케줄링 정책(우선순위·오버런)과 실행 시간 모델은 후속 상세 설계

## Related ASRs
- ASR-005 — 앱 런타임 모델 — 이 ADR이 결정을 문서화

## Downstream Concerns
- [ ] **컴포넌트 실행 시간(execution time) 모델:** 태스크 실행 시간·오버런 재현
- [ ] **컴포넌트 API 정의:** 주기 콜백, 메시지 핸들러, 상태 저장 인터페이스
- [ ] **스케줄링 정책:** 우선순위, 오버런 처리

## Related
- {project-root}/spec/sdv-sim-v1.md — Spec 반영됨
- {project-root}/adr/simulation-engine-model.md — 엔진 모델 (DES) 결정

## Tags
`runtime`, `component`, `rte`, `task`, `direct-input`

## Approved
- 2026-08-12: Option C (RTE 스타일), user confirmed via Direct Input (retroactive ADR documentation)
