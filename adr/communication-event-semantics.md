# 통신 이벤트 의미론 (Communication Event Semantics)

## Concern
통신 이벤트(tx/rx/drop)가 **정확히 언제, 누구에게 기록**되는가? — CAN 수신 범위, Ethernet 스위치 흐름, 게이트웨이 라우팅 이벤트·다중 홉, 주입 메시지의 tx 발생 여부

## Status
approved

## Decision
**Option A — 수신자 매핑 기반 rx + 게이트웨이 link rx + 규칙 체인 다중 홉**
User-approved: rx는 receives 매핑된 노드에만 기록, 게이트웨이는 인프라로 동작, 다중 홉은 규칙 체인(홉 최대 8).

## Context
- ASR-002(DES)·ASR-004(L2) 후속 — 모델(CAN/Ethernet/게이트웨이)은 결정됐으나 이벤트 기록 의미론 미정
- Gate 5 재검토 그룹 A-2: PRD 성공 기준 2(라우팅·지연·대역폭 결과 확인)에 직결
- 이벤트 로그 스키마(event-log-schema)의 tx/rx/drop 이벤트에 node/link/frame 필드가 있음 — "누가 기록하는가"가 이 ADR의 결정 대상

## Options
### Option A — 수신자 매핑 기반 rx + 게이트웨이 link rx + 규칙 체인 다중 홉
- **tx 발생 경로 3가지**: (1) 주기 프레임(source 노드, t=0 첫 발생) (2) 컴포넌트 `ctx.send` (3) 시나리오 주입 — 모두 송신 노드·프레임으로 tx 기록
- **rx**: 해당 링크에서 `receives`에 매핑된 컴포넌트가 있는 **노드에만** 기록 (브로드캐스트 이벤트를 모든 노드에 남기지 않음)
- **게이트웨이**: 명시적 노드로 기록하지 않고, 매칭 시 소스 링크 기준 rx → 라우팅 → 대상 링크에서 tx(remap_id 적용) → 대상 수신자 rx. 원본 프레임은 소스 링크에서 정상 전파 유지
- **다중 홉**: 라우팅된 프레임이 다시 게이트웨이 규칙에 매칭될 수 있음(규칙 체인). 무한 루프 방지: 프레임당 라우팅 홉 최대치(기본 8) 초과 시 drop 이벤트
- **Ethernet 흐름**: tx(송신 노드) → 스위치 FIFO 입장 → 방출 완료 시각에 수신자 rx. 스위치 큐 초과는 테일 드롭(기존 결정)
- Pro: 로그가 "누가 받았는가" 기준으로 검증 가치 높음, 게이트웨이 별도 노드 불필요(스키마 변경 없음)
- Con: CAN 브로드캐스트 현실과 달라 버스 전체 수신 관찰 불가

### Option B — 브로드캐스트 rx (수신자 무관)
- 링크의 모든 노드에 rx 기록
- Pro: 버스 현실(브로드캐스트) 재현
- Con: 로그 폭증(프레임 × 노드), assertion의 node 매칭이 과잉 매칭

### Option C — 게이트웨이를 노드로 취급
- 게이트웨이도 node처럼 rx/tx 기록 (node 필드에 게이트웨이 이름)
- Pro: 흐름 추적이 명시적
- Con: 게이트웨이를 노드로 승격 — architecture 스키마 변경, 노드 수 규모 목표에 영향

## Tradeoffs
| | A (수신자 매핑) | B (브로드캐스트) | C (게이트웨이 노드화) |
|---|------|------|------|
| 검증 가치 | ★★★★★ | ★★ | ★★★★ |
| 로그 크기 | 적음 | 큼 | 중간 |
| 구현 복잡도 | 낮음 | 낮음 | 중간 |
| 스키마 영향 | 없음 | 없음 | 있음 |

## Recommendation (optional)
- **Option A**: assertion/지연 검증 목적에 최적. 게이트웨이는 인프라로 두고 link rx/tx로 표현 — 스키마 변경 없이 다중 홉 지원.

## Consequences
- 라우팅된 프레임의 tx node는 게이트웨이(인프라)가 아닌 대상 링크 기준 — rx/tx의 node 필드 규칙 확정
- CAN/Ethernet 모두 동일 rx 규칙 적용
- 주입 메시지도 tx 이벤트로 기록 → 지연·라우팅 검증에 주입 시나리오 사용 가능

## Related ASRs
- ASR-002 — 시뮬레이션 엔진 모델 — 이벤트 처리 의미론
- ASR-004 — 통신 프로토콜 충실도 — 이벤트 기록 규칙

## Downstream Concerns
- [ ] **라우팅 홉 최대치:** 기본 8의 근거·설정 가능 여부
- [ ] **주입 메시지와 프레임 매핑:** 주입 시 frame 지정이 필수인지 message로 유추할지 (D-12와 연계)

## Related
- {project-root}/adr/can-fidelity-model.md, ethernet-fidelity-model.md, gateway-routing-rules.md — 상위 모델
- {project-root}/adr/event-log-schema.md — 이벤트 필드 규칙

## Tags
`event`, `semantics`, `rx`, `gateway`, `routing`

## Approved
- 2026-08-12: Option A (수신자 매핑 rx + 게이트웨이 link rx + 규칙 체인), user confirmed
