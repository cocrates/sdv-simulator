# 정의 파일 필드-레벨 스키마 (Definition Field-Level Schema)

## Concern
architecture.yaml / scenario.yaml의 **필드-레벨 스키마**(전체 필드 트리)와 시나리오의 **메시지 주입 형식**을 어떻게 확정할 것인가?

## Status
approved

## Decision
**Option A — 명시적 완전 스키마 + 공식 예시**
User-approved: 필드-레벨 스키마와 시나리오 메시지 주입 형식을 문서화하고 Pydantic 모델 1:1로 구현 SSOT 확보.

## Context
- ASR-003(YAML) 후속 — 2계층 구조(메시지-프레임)와 파일 분리는 결정됐으나 실제 필드 트리와 주입 문법은 미정 (구현 SSOT 갭)
- Gate 5 재검토(2026-08-12) 그룹 A-1: 스펙·ADR 모두 개념 수준 — 구현 시 필드 발명 필연
- Pydantic 모델 기반 스키마 검증(결정됨) — 필드 트리 = Pydantic 모델 정의 그 자체

## Options
### Option A — 명시적 완전 스키마 + 공식 예시
- 전체 필드 트리를 ADR에 문서화하고, Spec에 예시 YAML 포함:
  - `architecture.yaml`:
    - `nodes: [{name, type: ECU|HPC, components: [{name, sends: [msg], receives: [msg], tasks: [{name, period_ms, priority, wcet_ms}]}]}]`
    - `links: [{name, kind: can|ethernet, bitrate, nodes: [node], frames: [{name, id, dlc, period_ms, source, message?}], switches: [{name?, queue_depth}]}]`
    - `gateways: [{name, routes: [{from: {link, frame|id_min, id_max}, to: {link, remap_id?}, delay_ms?}]}]`
  - `scenario.yaml`: `duration_ms`, `seed?`, `messages: [{t_ms, link, frame, data?}]`, `assertions: [{name?, expect: {...}}]`
- Pro: 구현 SSOT 확보, 예시가 테스트·문서 역할, Pydantic 모델 1:1
- Con: ADR·Spec 분량 증가

### Option B — 최소 스키마 (필수 필드만)
- 블록 레벨만 정의, 세부 필드는 구현 시 Pydantic으로 확정
- Pro: 문서 부담 최소
- Con: 구현 발명 잔존 — 이번 ADR의 목적(SSOT) 미달

### Option C — 외부 JSON Schema 파일로 관리
- 스키마를 YAML 문서가 아닌 JSON Schema 파일로 두고 참조
- Pro: 코드 검증과 단일 소스
- Con: 관리 포인트 추가, YAML 작성자 관점에서 문서 분산

## Tradeoffs
| | A (완전 스키마+예시) | B (최소) | C (JSON Schema) |
|---|------|------|------|
| 구현 SSOT | ★★★★★ | ★★ | ★★★★ |
| 사람 가독성 | ★★★★★ | ★★★ | ★★ |
| 문서 부담 | 중간 | 최저 | 중간 |
| Pydantic 정합 | ★★★★★ | ★★★ | ★★★★ |

## Recommendation (optional)
- **Option A**: Gate 5의 핵심 갭(그룹 A-1)을 직접 해소. Spec에 예시 YAML을 포함해 구현·테스트·문서 3역할을 한 번에.

## Consequences
- Pydantic 모델은 ADR의 필드 트리와 1:1 — `sdv_sim/schema/arch.py`, `sdv_sim/schema/scenario.py` 분리 (definition-schema-structure Downstream과 정합)
- 스키마 오류 메시지는 필드 경로 포함 (cli-output-policy와 정합)

## Related ASRs
- ASR-003 — 아키텍처/시나리오 정의 형식 — 필드-레벨 스키마 확정

## Downstream Concerns
- [ ] **주입 메시지의 data 표현:** data 유형(스칼라/맵/바이너리?)과 DLC와의 관계
- [ ] **프레임 source 검증:** source 노드가 해당 링크에 연결되어 있는지 스키마 검증에서 확인할지

## Related
- {project-root}/adr/definition-schema-structure.md — 상위 결정 (2계층 + 매핑)
- {project-root}/adr/definition-file-format.md — 상위 결정 (YAML)

## Tags
`schema`, `yaml`, `definition`, `field-level`

## Approved
- 2026-08-12: Option A (명시적 완전 스키마 + 공식 예시), user confirmed
