# CAN 버스 모델 (CAN Fidelity Model)

## Concern
CAN 버스의 지연·중재·부하를 어떤 모델로 재현할 것인가?

## Status
approved

## Decision
**Option A — 표준 프레임 비트 수식 + ID 우선 중재 + 우선순위 큐 대기**
User-approved: tx_ms = ceil((44 + 8·DLC) / bitrate_kbps), CAN ID 작을수록 중재 우선, 버스 점유 시 우선순위 큐 대기.

## Context
- ASR-004(L2 통신) 후속 — PRD 성공 기준 2(지연·대역폭)의 핵심
- ADR(communication-fidelity-level)의 Downstream: 지연 모델 파라미터(전파 지연 vs 큐잉)
- 결정성 요구 (ASR-002)

## Options
### Option A — 표준 프레임 비트 수식 + ID 우선 중재 + 우선순위 큐 대기
- 전송 시간: `tx_ms = ceil((44 + 8·DLC) / bitrate_kbps)` (CAN 표준 프레임 비트 수)
- 중재: 동시 전송 시 CAN ID 작을수록 우선. 버스 점유 중이면 우선순위 큐에서 대기 → 지연
- 버스 부하(점유율 %)를 리포트에 포함
- Pro: 현실적·결정적, 버스 부하 검증 가능, 구현 합리적
- Con: 비트 레벨 상세(비트 스터핑 등) 미포함

### Option B — 고정 지연 상수
- 프레임마다 고정 지연값 사용
- Pro: 구현 최단
- Con: 부하·경합에 따른 지연 변화 재현 불가 (PRD 기준 미충족)

### Option C — 오류 프레임/재전송/버스 오프 포함
- 프로토콜 오류까지 모델링
- Pro: 오류 시나리오 검증 가능
- Con: v1 범위 초과, 복잡도 급증

## Tradeoffs
| | A (비트 수식+중재) | B (고정 지연) | C (오류 포함) |
|---|---------------------|---------------|---------------|
| 버스 부하·경합 재현 | ✓ | ✗ | ✓ |
| 결정성 | ✓ | ✓ | △ |
| 구현 비용 | 중간 | 낮음 | 높음 |

## Recommendation (optional)
- **Option A** 추천: PRD 성공 기준 2를 충족하는 최소 현실적 모델

## Consequences
- 전파 지연은 0 — 지연은 큐잉/버스 점유로만 발생 (simulation-time-model과 정합)
- 중재 실패/재전송/오류 프레임은 v1 제외

## Related ASRs
- ASR-004 — 통신 프로토콜 충실도 — CAN 세부 모델 결정

## Downstream Concerns
- [ ] **버스 부하 리포트 형식:** 점유율·프레임 수·드롭 수 집계 항목

## Related
- {project-root}/adr/communication-fidelity-level.md — 상위 결정 (L2)

## Tags
`can`, `bus`, `fidelity`, `arbitration`

## Approved
- 2026-08-12: Option A (비트 수식 + ID 우선 중재 + 큐 대기), user confirmed
