# Ethernet 모델 (Ethernet Fidelity Model)

## Concern
Ethernet 링크와 스위치를 어떤 수준으로 재현할 것인가?

## Status
approved

## Decision
**Option A — 프레임 크기 수식 + 단일 스위치 FIFO 큐 + 테일 드롭**
User-approved: bytes = data + 42, tx_ms = ceil(bytes·8 / (Mbps·1000)). 스위치 FIFO 큐, queue_depth 초과 시 테일 드롭 → drop 이벤트.

## Context
- ASR-004(L2 통신) 후속 — PRD 성공 기준 2(대역폭)의 대상
- ADR(communication-fidelity-level)의 Downstream: Ethernet 수준 범위(단순 링크 vs 스위치 포트·큐잉)

## Options
### Option A — 프레임 크기 수식 + 단일 스위치 FIFO 큐 + 테일 드롭
- 프레임 크기: `bytes = data + 42` (Ethernet 오버헤드), 전송 시간: `tx_ms = ceil(bytes·8 / (bitrate_mbps·1000))`
- 링크에 스위치 명시(기본 1개), FIFO 큐, `queue_depth`(기본 1000) 초과 시 테일 드롭 → drop 이벤트
- Pro: 대역폭·큐잉·드롭 검증 가능, 결정적, 구현 합리적
- Con: 우선순위 큐/VLAN 미지원

### Option B — 링크 대역폭만 (스위치 없음)
- 대역폭에 따른 전송 지연만, 큐잉 없음
- Pro: 구현 단순
- Con: 스위치 큐잉·드롭 검증 불가 (L2 충실도 목표 미달)

### Option C — 우선순위 큐(802.1p)/VLAN 포함
- 실제 스위치 QoS 동작 모델링
- Pro: QoS 시나리오 검증 가능
- Con: v1 범위 초과, 복잡도 급증

## Tradeoffs
| | A (스위치+FIFO+드롭) | B (대역폭만) | C (QoS/VLAN) |
|---|---------------------|-------------|--------------|
| 큐잉·드롭 재현 | ✓ | ✗ | ✓ |
| 구현 비용 | 중간 | 낮음 | 높음 |
| 결정성 | ✓ | ✓ | △ |

## Recommendation (optional)
- **Option A** 추천: L2 충실도(큐잉·드롭)와 구현 비용의 균형

## Consequences
- 다중 스위치 토폴로지는 명시적 정의는 허용하되, v1 기본은 단일 스위치
- VLAN/802.1p는 v1 제외

## Related ASRs
- ASR-004 — 통신 프로토콜 충실도 — Ethernet 세부 모델 결정

## Downstream Concerns
- [ ] **drop 이벤트 집계:** 드롭 발생 시각·프레임 집계 (event-log-schema와 연계)

## Related
- {project-root}/adr/communication-fidelity-level.md — 상위 결정 (L2)

## Tags
`ethernet`, `switch`, `queueing`, `fidelity`

## Approved
- 2026-08-12: Option A (프레임 크기 수식 + FIFO 큐 + 테일 드롭), user confirmed
