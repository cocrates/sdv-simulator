# Ethernet payload 크기 기준 (Ethernet Payload Basis)

## Concern
Ethernet 프레임 전송 시간 계산 `bytes = data + 42`에서 **payload(`data`)의 크기 기준**은 무엇인가 — 프레임 DLC 바이트인가, 시나리오 주입 데이터(`data` 객체)의 직렬화 크기인가?

## Status
approved

## Context
- 검증(1차)에서 **미문서화 ASR U-6**로 식별 — ethernet-fidelity-model ADR은 "bytes = data + 42"를 정했으나 `data`의 기준(DLC vs 메시지 객체)은 미정이었음
- 스펙 인코딩(2026-08-12) 시 "payload = 프레임 DLC 바이트, `data` 객체 크기와 무관"으로 결정 — 생성 시 해석 ②(프레임 dlc 바이트)와 정합
- 구현: `tx_ms()`에서 `dlc + 42` 사용
- 상위 결정: ethernet-fidelity-model (프레임 크기 수식), definition-field-schema (scenario `messages.data` 선택 필드)

## Decision
**Option A — payload = 프레임 DLC 바이트 (bytes = dlc + 42)**
User-approved: 전송 크기는 프레임 정의(DLC) 기준, 주입 `data` 객체 크기와 무관 — 결정성 + CAN 모델 일관성, 주입 데이터 내용은 크기가 아니라 라우팅에만 영향.

## Options
### Option A — payload = 프레임 DLC 바이트 (bytes = dlc + 42) (현재 스펙/구현)
- 전송 크기는 프레임 정의의 `dlc`(고정) 기준 — 주입 데이터 객체 크기와 무관
- Pro: 결정적·예측 가능 (주입 내용이 바뀌어도 전송 시간 불변), CAN 모델과 일관(전송 크기 = DLC), 구현 단순
- Con: 실제 페이로드가 DLC보다 작게/다르게 주입되어도 전송 크기가 같음 — 미세 충실도 손실

### Option B — payload = data 객체 직렬화 크기
- 주입/전송 시 `data` 객체의 직렬화(JSON 등) 크기를 payload로 사용
- Pro: 실제 데이터 크기 반영 — 페이로드 크기에 따른 대역폭 검증 가능
- Con: 직렬화 규칙(포맷·타입)에 따라 크기가 달라져 결정성 위험, 컴포넌트 `ctx.send` 데이터의 직렬화 비용 도입, CAN과 모델 비대칭

### Option C — payload = max(dlc, data 크기) 또는 구성 가능
- DLC와 데이터 크기 중 큰 값 사용, 또는 `payload_mode: dlc|data` 설정 제공
- Pro: 유연성
- Con: 기본값 모호, 설정 추가로 v1 스키마·문서 변경 부담

## Tradeoffs
| | A (DLC 기준) | B (data 크기) | C (max/설정) |
|---|------|------|------|
| 결정성 | ★★★★★ | ★★ (직렬화 의존) | ★★★ |
| CAN 모델 일관성 | ✓ | ✗ | △ |
| 실제 크기 반영 | ✗ | ✓ | △ |
| 구현 단순성 | ★★★★★ | ★★ | ★★★ |

## Recommendation (optional)
- **Option A**: L2 프레임 모델에서 전송 크기는 프레임 정의(DLC)가 기준 — CAN과 동일한 원칙. 주입 데이터 내용은 페이로드 크기(대역폭)가 아니라 내용 라우팅에만 영향. v1 결정성 요구(난수 없음)와도 정합.

## Consequences
- `bytes = dlc + 42`, `tx_ms = ceil(bytes·8 / (Mbps·1000))` — 주입 `data` 내용과 무관
- 스펙 문구 "payload = 프레임 DLC 바이트, `data` 객체 크기와 무관"으로 인코딩됨

## Related ASRs
- ASR-013 — Ethernet payload 크기 기준 — 본 ADR이 직접 해소
- ASR-004 — 통신 프로토콜 충실도 (CAN/Ethernet) — 상위 ASR

## Downstream Concerns
- [ ] **CAN payload 기준 명시:** CAN 모델도 전송 크기 = DLC로 이미 일관적이나, `data` 객체와 DLC 불일치 시 검증 의도 문서화 필요

## Related
- {project-root}/adr/ethernet-fidelity-model.md — 상위 결정 (bytes = data + 42 수식)
- {project-root}/adr/can-fidelity-model.md — CAN 대칭 모델 (전송 크기 = DLC)

## Tags
`ethernet`, `payload`, `fidelity`, `dlc`

## Approved
- 2026-08-12: Option A (payload = 프레임 DLC 바이트), user confirmed
