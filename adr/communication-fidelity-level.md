# 통신 프로토콜 충실도 (Communication Fidelity Level)

## Concern
CAN/Ethernet 통신을 어느 수준(신호/메시지/프레임, 지연·대역폭 모델)까지 재현할 것인가?

## Status
approved

## Context
- v1의 핵심 검증 대상은 메시지 라우팅·지연·대역폭 (PRD 성공 기준 2)
- ASR-002(이산 사건 엔진)와 정합: 이벤트 기반으로 지연·큐잉을 재현
- (대화에서 Direct Input으로 확정된 결정을 ADR로 사후 문서화한 기록)

## Decision
**Option B — L2 (프레임/버스 수준)**
User-approved: CAN 프레임(ID·주기·DLC) 기반 우선순위/버스 부하 모델, Ethernet 링크 대역폭·스위치 큐잉 모델, 게이트웨이 라우팅 규칙. L3(비트 타이밍, 프로토콜 스택)는 v1 제외.

## Options
### Option A — L1 (신호/메시지 수준)
- 정의된 메시지·신호만 전달, 지연은 단순화
- Pro: 구현 단순, 앱 로직 검증에 충분
- Con: 대역폭·버스 부하·라우팅 검증 불가 (PRD 기준 미충족)

### Option B — L2 (프레임/버스 수준)
- CAN 프레임(ID·주기·DLC), 버스 부하·지연·큐잉, 게이트웨이 라우팅, Ethernet 링크 대역폭·스위치 큐잉
- Pro: 라우팅·지연·대역폭 검증 가능 (PRD 기준 충족), 구현 비용 합리적
- Con: 비트 레벨 타이밍·프로토콜 스택 세부는 제외

### Option C — L3 (프로토콜 스택/물리 수준)
- 비트 타이밍, 오류 프레임, Ethernet QoS, Some/IP 등
- Pro: 실제 프로토콜 스택 수준 검증
- Con: 구현 비용 급증 (v1 범위 초과)

## Tradeoffs
| | L1 (A) | L2 (B) | L3 (C) |
|---|--------|--------|--------|
| 대역폭·큐잉 재현 | ✗ | ✓ | ✓ |
| 게이트웨이 라우팅 | ✗ | ✓ | ✓ |
| PRD 성공 기준 2 충족 | ✗ | ✓ | ✓ |
| 구현 비용 | 낮음 | 중간 | 높음 |

## Recommendation (optional)
- **L2** — Direct Input으로 확정됨

## Consequences
- 지연 모델은 우선순위 기반 큐잉 중심 (전파 지연 파라미터는 후속 상세 설계)
- Ethernet 스위치 수준 범위는 후속 상세 설계에서 확정

## Related ASRs
- ASR-004 — 통신 프로토콜 충실도 (CAN/Ethernet) — 이 ADR이 결정을 문서화

## Downstream Concerns
- [ ] **지연 모델 파라미터:** 전파 지연 vs 버스 부하 기반 큐잉
- [ ] **Ethernet 수준 범위:** 단순 링크 대역폭 vs 스위치 포트·큐잉 포함

## Related
- {project-root}/spec/sdv-sim-v1.md — Spec 반영됨
- {project-root}/adr/simulation-engine-model.md — 엔진 모델 (DES) 결정

## Tags
`communication`, `can`, `ethernet`, `fidelity`, `direct-input`

## Approved
- 2026-08-12: Option B (L2 프레임/버스 수준), user confirmed via Direct Input (retroactive ADR documentation)
