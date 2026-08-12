# 리플레이 애니메이션 시간 모델 (replay-animation-timing)

## Concern
구조 뷰 위 프레임 전송 애니메이션의 **시간**을 어떻게 결정하는가? v1 이벤트는 tx(전송 시작)와 rx(시작 + tx_ms 완료)만 기록하는데, tx_ms(전송 시간)는 이벤트에 없고 rx는 `receives` 매핑 노드에만 기록된다.

## Status
approved

## Context
- v1 의미론: tx = 전송 시작 시각, rx = 시작 + tx_ms (tx_ms = DLC/bitrate 기반, 이벤트에 미포함). 전파 지연 0. 큐잉 지연은 tx 시작 전에 소화.
- v2 spec: "tx 이벤트 시각에 송신 노드 → 링크 → 수신 노드 이동 표시 (전파 지연 0 — v1 의미론)" — 애니메이션 지속시간·완료 시각 미정의 (spec review M-2).
- run 경로: 프런트가 아키텍처 YAML 보유 → tx_ms 계산 가능. load-log 경로: 아키텍처 없음.
- 연계: 시크 상태 계산(시크 중 in-flight 프레임 판정)과 상호 의존 — 별도 ADR(dashboard-seek-state-indexing).

## Options
### Option A — 물리 시간 재생 (tx_ms 기반) + load-log 고정 폴백 (권장)
- 프런트가 아키텍처로 tx_ms를 계산해 [tx, tx+tx_ms) 구간 동안 프레임이 링크 위를 이동하도록 재생. rx 이벤트 시각과 정확히 일치.
- load-log 경로(아키텍처 없음): 고정 지속시간 펄스로 폴백 + 화면에 "근사 표시" 라벨.
- Pro: v1 의미론·rx 타임스탬프와 시각적 정합 / 버스 부하·연속 전송 직관 일치 / 리포트(버스 부하)와 시각 일관
- Con: run 경로는 arch 필요(이미 보유) / load-log는 폴백 필요

### Option B — 고정 펄스 단일 모델
- 모든 tx에서 배속 기준 고정 지속시간(예: 1x에서 ~300ms) 펄스를 재생 — 전 경로 동일.
- Pro: 구현 단순, arch 불필요, 경로 간 동작 일관
- Con: rx 타임스탬프와 시각 불일치 — 프레임이 rx 이벤트보다 늦거나 빠르게 "도착"해 보임 / 고부하 링크의 연속 프레임이 겹쳐 보이는 오해

### Option C — rx 구간 기반 완료 추정
- 완료를 동일 (frame, link)의 다음 rx 이벤트 시각으로 추정 (tx→rx 구간 = tx_ms).
- Pro: 이벤트만으로 완료 시각 추정 가능 (rx 존재 시) — arch 불필요
- Con: rx 미발생 프레임(receives 매핑 없음)은 추정 불가 → 폴백 필요 / 다중 수신자·게이트웨이 재전송 시 매칭 모호 / 부분적 해법

## Tradeoffs
| 차원 | A (물리+폴백) | B (고정 펄스) | C (rx 구간) |
|------|---------------|---------------|-------------|
| rx 타임스탬프와 시각 정합 | ★★★ | ★ (불일치) | ★★★ (rx 존재 시) |
| arch 의존성 | run: 있음 / load-log: 폴백 | 없음 | 없음 |
| 구현 단순성 | ★★ | ★★★ | ★★ |
| no-rx 프레임 처리 | 폴백 명시 | 일관 | 모호·폴백 필요 |

## Recommendation
- **Option A** 권장. "동일 리플레이 파이프라인"의 의미가 "동일 이벤트 데이터의 정확한 재생"임을 보장하는 방안. load-log은 근사 표시를 명시해 정확성 기대를 관리. (m-2·m-3 문구 보정 포함: 큐 상태는 drop/supersede 이벤트 신호로만 표시, 게이트웨이 체인은 소스 링크 전송 완료 → 대상 링크 tx 기준)

## Consequences
- run 경로: 프런트가 보유한 아키텍처로 tx_ms(DLC/bitrate 기반)를 계산해 [tx, tx+tx_ms) 구간 동안 프레임 이동 애니메이션 재생 — rx 이벤트 시각과 정확히 일치
- load-log 경로(아키텍처 없음): 고정 지속시간 펄스로 폴백 + "근사 표시" 라벨 — 정확한 타임스탬프 대응은 run 경로 전용임을 명시
- 큐 상태 표시: 이벤트에 큐 깊이 없음 — drop/supersede 이벤트를 신호로 표시, 깊이 수치 추정 금지 (m-2 인코딩)
- 게이트웨이 체인 표시: 소스 링크 전송 완료 → 대상 링크 tx 순 (rx 이벤트 기준 아님 — v1 라우팅은 전송 완료 시각에 동작, m-3 인코딩)

## Related ASRs
- ASR-016 — 구조 뷰 렌더링·성능 — 애니메이션·오버레이 표시 규칙의 대상
- ASR-015 — 데이터 흐름·리플레이 — 이벤트 의미론의 원천 (컨텍스트)

## Downstream Concerns
- [ ] **시크 중 in-flight 프레임 판정**: 물리 재생 채택 시 시크 상태 계산에 tx_ms가 필요 — dashboard-seek-state-indexing ADR과 연계
- [ ] **큐 상태 표시 규칙**: 이벤트에 큐 깊이 없음 — drop/supersede 이벤트를 큐 상태 신호로 표시, 깊이 수치는 추정 금지 (m-2, spec 인코딩)
- [ ] **게이트웨이 체인 표시 기준**: 소스 링크 전송 완료 → 대상 링크 tx 순 (rx 이벤트 기준 아님 — v1 라우팅은 전송 완료 시각에 동작) (m-3, spec 인코딩)

## Related
- `adr/dashboard-seek-state-indexing.md` — 연계 ADR (시크 상태 계산)
- `spec/sdv-sim-v2.md` — 오버레이 렌더 규칙 수정 대상

## Tags
`replay`, `animation`, `timing`, `dashboard`, `overlay`

## Approved
- 2026-08-12: Option A (물리 시간 재생 + load-log 고정 폴백), user confirmed ("오케이") — ADR 5건 일괄 승인
