# 스텁 컴포넌트 동작 (Stub Component Behavior)

## Concern
YAML에 `class` 미등록 컴포넌트(스텁)는 통신상 어떻게 동작하는가? — 스텁이 sends 메시지를 자동 송신하는가?

## Status
approved

## Decision
**Option A — 스텁은 수신자로만 동작 (sends 무시)**
User-approved: tx는 주기 프레임·시나리오 주입·실제 컴포넌트 ctx.send 3경로로만 발생, 스텁은 rx 기록만 수행.

## Context
- ASR-005(앱 런타임) 후속 — "미등록 시 스텁(통신 시뮬레이션만 수행)"은 결정됐으나 동작 의미론 미정
- Gate 5 재검토 그룹 A-3: YAML만으로 성공 기준 1·2를 충족시키는 핵심 경로
- 주기 프레임은 링크에서 정의됨(definition-schema-structure) — tx 발생 경로와의 정합 필요

## Options
### Option A — 스텁은 수신자로만 동작 (sends 무시)
- tx는 3경로로만: (1) 주기 프레임(source 노드) (2) 시나리오 주입 (3) 실제 컴포넌트 `ctx.send`
- 스텁은 receives 매핑에 따라 rx 기록만 수행
- Pro: 스텁이 "통신 시뮬레이션"의 관찰자로 단순·결정적, YAML-only 시나리오는 프레임 주기로 충분
- Con: 컴포넌트 없이 sends 기반 메시지 흐름은 생성 불가

### Option B — 스텁 자동 송신
- 스텁의 sends 메시지를 해당 프레임(매핑)의 period에 맞춰 자동 tx
- Pro: YAML만으로 컴포넌트 송신 흐름 재현
- Con: "스텁" 의미 모호(실제 로직 없이 송신), 주기·우선순위 파생 결정 필요, 예상 밖 tx 발생 위험

### Option C — class 미지정 시 스키마 오류
- 모든 컴포넌트에 class 필수
- Pro: 의미 명확
- Con: YAML-only 검증 경로(성공 기준 1·2) 차단 — v1 목표와 상충

## Tradeoffs
| | A (수신자 전용) | B (자동 송신) | C (오류) |
|---|------|------|------|
| YAML-only 검증 | ✓ (프레임 기반) | ✓ | ✗ |
| 예측 가능성 | ★★★★★ | ★★★ | ★★★★★ |
| 스텁 개념 단순성 | ★★★★★ | ★★ | — |

## Recommendation (optional)
- **Option A**: 주기 프레임이 이미 tx 경로를 제공하므로 스텁을 수신자로 한정 — 동작 예측 가능, 성공 기준 1·2 유지.

## Consequences
- sends가 있는 스텁 컴포넌트도 tx 미발생 — 스텁 송신을 기대하는 assertion은 실패
- 시나리오 주입(messages)이 YAML-only 시나리오의 송신 수단

## Related ASRs
- ASR-005 — 앱 런타임 모델 — 스텁 동작 의미론

## Downstream Concerns
- [ ] **경고 여부:** sends가 있는데 class 미등록 시 로드 경고를 줄지

## Related
- {project-root}/adr/app-runtime-model.md — 상위 결정 (RTE 스타일)
- {project-root}/adr/component-api.md — 컴포넌트 등록 API

## Tags
`stub`, `component`, `runtime`, `yaml`

## Approved
- 2026-08-12: Option A (스텁 수신자 전용), user confirmed
