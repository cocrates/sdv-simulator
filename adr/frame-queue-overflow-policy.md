# 프레임 큐 오버플로 정책 (Frame Queue Overflow Policy)

## Concern
주기 프레임이 링크 큐(CAN 우선순위 큐 / Ethernet FIFO)에서 **대기 중 다음 주기 인스턴스가 도착**하면 어떻게 처리하는가?

## Status
approved

## Decision
**Option A — 최신 교체 (supersede)**
User-approved: 큐 대기 중 동일 프레임 신규 인스턴스 도착 시 기존 제거·교체. CAN/Ethernet 동일 적용, 교체는 depth 소모 없음.

## Context
- ASR-004 후속 — 큐잉 모델(CAN 우선순위 큐, Ethernet FIFO+테일 드롭)은 결정됐으나 주기 인스턴스 겹침 처리 미정
- Gate 5 재검토 그룹 B-7 — 버스 부하 시나리오에서 실제 발생
- 정수 ms 시간 모델 — tx_ms 동안 큐에 남는 프레임 발생 가능

## Options
### Option A — 최신 교체 (supersede)
- 큐에 대기 중인 동일 프레임 인스턴스가 있으면 기존을 제거하고 신규 인스턴스로 교체
- Pro: 오래된 데이터 폐기 = CAN 현실과 정합, 큐 폭주 방지, 로그 명확
- Con: 폐기 사실이 별도 이벤트 없음(교체로만 표현)

### Option B — 복수 인스턴스 큐잉
- 모든 인스턴스를 큐에 쌓음
- Pro: 큐 동작 단순(일반 큐)
- Con: 폭주 시 오래된 프레임이 뒤늦게 전송(시점 왜곡), 테일 드롭까지 이어질 수 있음

### Option C — 신규 인스턴스 폐기
- 큐에 기존 인스턴스가 있으면 신규 도착 프레임 폐기(drop 이벤트)
- Pro: 대기열 안정
- Con: 신규 데이터 손실 — 주기 데이터는 최신이 중요한데 역방향

## Tradeoffs
| | A (최신 교체) | B (복수 큐잉) | C (신규 폐기) |
|---|------|------|------|
| CAN 현실 정합 | ★★★★★ | ★★ | ★★ |
| 큐 폭주 방지 | ★★★★★ | ★ | ★★★★ |
| 로그 명확성 | ★★★★ | ★★★ | ★★★ |

## Recommendation (optional)
- **Option A**: 주기 데이터의 "최신 우선" 성격과 CAN 현실을 반영. CAN/Ethernet 모두 동일 적용.

## Consequences
- Ethernet 테일 드롭(queue_depth 초과)과는 별개 정책 — 교체는 depth 소모 없음
- 교체 시 별도 이벤트 없음 (로그는 최종 전송된 인스턴스만)

## Related ASRs
- ASR-004 — 통신 프로토콜 충실도 — 큐 인스턴스 정책

## Downstream Concerns
- [ ] **교체 발생 통계:** 리포트에 supersede 횟수 집계 여부 (D-21과 연계)

## Related
- {project-root}/adr/can-fidelity-model.md, ethernet-fidelity-model.md — 큐잉 모델

## Tags
`queue`, `frame`, `can`, `ethernet`, `overflow`

## Approved
- 2026-08-12: Option A (최신 교체/supersede), user confirmed
