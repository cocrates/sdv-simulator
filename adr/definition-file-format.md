# 아키텍처/시나리오 정의 파일 형식 (Definition File Format)

## Concern
노드·토폴로지·시나리오를 기술하는 정의 파일 형식은 무엇으로 할 것인가?

## Status
approved

## Context
- ASR-002(이산 사건 엔진) 승인 후속 — 정의 형식은 엔진 입력의 1차 UX이자 검증 자동화의 입력
- 사용자가 직접 작성하는 문서이므로 가독성·주석·계층 표현이 핵심
- (대화에서 Direct Input으로 확정된 결정을 ADR로 사후 문서화한 기록)

## Decision
**Option A — YAML**
User-approved: 사람이 작성하는 정의 파일에 최적. PyYAML로 파싱, Pydantic 모델 기반 스키마 검증으로 타입 안정성 보완.

## Options
### Option A — YAML
- 사람이 작성하기 좋은 계층 구조 + 주석 지원
- Pro: 가독성·주석·계층 표현, Python(PyYAML) 생태계 성숙, 자동차 도구 관행과 일치
- Con: 타입 엄격성 낮음 (Pydantic 스키마로 보완)

### Option B — JSON
- 기계 친화적, 엄격한 파싱
- Pro: 스키마 검증 용이
- Con: 주석 불가, 사람이 손으로 작성하기 불편

### Option C — TOML
- 설정 파일에 적합한 단순 문법
- Pro: 단순함, 설정 중심
- Con: 깊은 계층/목록 표현 불편

### Option D — 전용 DSL
- 도메인 특화 표현력
- Pro: 도메인에 최적화된 문법
- Con: 개발 비용 큼 (v1에 과도)

## Tradeoffs
| | YAML (A) | JSON (B) | TOML (C) | DSL (D) |
|---|----------|----------|----------|---------|
| 인간 작성 가독성 | ★★★★★ | ★★ | ★★★★ | ★★★ |
| 주석 지원 | ✅ | ❌ | ✅ | ✅ |
| 계층 표현 | ★★★★★ | ★★★★ | ★★★ | ★★★★★ |
| 구현 비용 | 낮음 | 낮음 | 낮음 | 높음 |

## Recommendation (optional)
- **YAML** — Direct Input으로 확정됨

## Consequences
- Pydantic 스키마 검증 계층 필요
- 아키텍처 파일/시나리오 파일 분리 여부는 후속 결정으로 남음

## Related ASRs
- ASR-003 — 아키텍처/시나리오 정의 형식 — 이 ADR이 결정을 문서화

## Downstream Concerns
- [ ] **스키마 검증 방식:** Pydantic 모델 기반 검증 (Spec에 반영됨)
- [ ] **파일 구성:** 아키텍처 파일과 시나리오 파일 분리 여부

## Related
- {project-root}/spec/sdv-sim-v1.md — Spec 반영됨

## Tags
`format`, `yaml`, `definition`, `direct-input`

## Approved
- 2026-08-12: Option A (YAML), user confirmed via Direct Input (retroactive ADR documentation)
