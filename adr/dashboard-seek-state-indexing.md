# 시크 상태 계산 전략 (seek-state-indexing)

## Concern
최대 100만 이벤트에서 시크(탐색) 후 노드·링크 상태 반영 **≤ 100ms**(spec 성능 기준)를 어떤 방식으로 달성하는가?

## Status
approved

## Context
- v2 spec 성능 기준: "시크(탐색) 후 노드·링크 상태 반영 ≤ 100ms". "시크 위치 결정은 (t_ms, seq) 배열 이진 탐색"만 명시 — **위치**는 찾지만 해당 시점 **상태**의 계산 전략은 없음 (spec review M-3).
- ADR topology-rendering-performance의 downstream concern "시크 시 노드 상태 계산 — O(1) 근사 이벤트 인덱싱"이 미해소 상태로 spec에 전달됨.
- 100만 이벤트의 O(N) 상태 재적용은 JS에서 100ms 초과 위험.
- 연계: 상태 정의(특히 in-flight 프레임)는 애니메이션 시간 모델에 의존 — dashboard-replay-animation-timing ADR.

## Options
### Option A — 주기적 상태 스냅샷 + 잔여 재적용 (권장)
- 이벤트 K개마다 노드/링크 상태 스냅샷을 구축. 시크 = 스냅샷 오프셋 이진 탐색 + 잔여 ≤ K개 이벤트 재적용.
- Pro: 시크 비용 상한(K) 보장 — 100ms 달성 예측 가능 / 메모리 제어 가능(스냅샷 크기 × 개수) / 로드·정렬 2s 예산에 구축 포함
- Con: 스냅샷 구축 비용·메모리 (사전 계산)

### Option B — O(N) 순차 재적용 (스냅샷 없음)
- 매 시크마다 이벤트 처음부터 시크 위치까지 재적용.
- Pro: 구현 단순, 추가 메모리 없음
- Con: 최악 100만 이벤트 재적용 — 100ms 초과 위험, 비용 비예측 (스펙 성능 기준 위반 가능)

### Option C — 전 이벤트 상태 시퀀스 사전 계산
- 이벤트별 결과 상태를 배열로 저장해 O(1) 시크.
- Pro: 시크 즉시
- Con: 상태 복사가 O(N) 메모리 — 100만 건에서 비현실 (구조 공유 없이)

## Tradeoffs
| 차원 | A (스냅샷) | B (O(N)) | C (전 시퀀스) |
|------|-----------|----------|---------------|
| 시크 비용 상한 | ★★★ (O(K)) | ★ (O(N)) | ★★★ (O(1)) |
| 메모리 | ★★ (스냅샷 수 × 크기) | ★★★ (없음) | ★ (O(N) 복사) |
| 구현 복잡도 | ★★ | ★★★ | ★ |
| 100ms 보장성 | ★★★ | ★★ | ★★★ |

## Recommendation
- **Option A** 권장. 상한 보장 + 메모리 제어의 균형. 구체 파라미터(K·스냅샷 내용)는 생성 시 결정하되 "시크 비용 상한 O(K)"를 요구사항으로 명시. 스냅샷 구축은 로드·정렬 2s 예산에 포함.

## Consequences
- 주기적 상태 스냅샷 채택: 이벤트 K개마다 노드/링크 상태 스냅샷 구축 (K와 스냅샷 내용은 생성 시 결정, spec에 시크 비용 상한 O(K) 명시)
- 시크 = 스냅샷 오프셋 이진 탐색 + 잔여 ≤ K개 이벤트 재적용 — 시크 비용 상한 보장으로 100ms 달성 예측 가능
- 스냅샷 구축은 로드·정렬 2s 예산에 포함
- in-flight 프레임 상태: 물리 재생(animation-timing ADR)에 따라 스냅샷·재적용에 tx_ms 필요 — 연계 명시

## Related ASRs
- ASR-016 — 구조 뷰 렌더링·성능 — 성능 기준(100ms)의 대상

## Downstream Concerns
- [ ] **스냅샷 내용·간격**: 상태 정의(노드 태스크·오버런, 링크 in-flight 프레임, 큐 신호)와 K 선택 — 생성 시 파라미터 (spec 상한 명시)
- [ ] **in-flight 프레임 상태**: 물리 재생(animation-timing ADR) 채택 시 스냅샷·재적용에 tx_ms 필요 — 연계

## Related
- `adr/dashboard-replay-animation-timing.md` — 연계 ADR (애니메이션 시간 모델)
- `adr/topology-rendering-performance.md` — 상위 ADR (성능 기준 원천)
- `spec/sdv-sim-v2.md` — 성능 기준·시크 절 수정 대상

## Tags
`seek`, `indexing`, `performance`, `replay`, `dashboard`

## Approved
- 2026-08-12: Option A (주기적 상태 스냅샷 + 잔여 재적용), user confirmed ("오케이") — ADR 5건 일괄 승인
