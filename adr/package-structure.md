# 코어 API 경계 & 패키지 구조 (Core API Boundary & Package Structure)

## Concern
코어 라이브러리와 CLI의 패키지 구조와 경계를 어떻게 설계할 것인가? (v2/v3가 코어를 재사용하는 구조 포함)

## Status
approved

## Context
- PRD 목표: "모든 형태(CLI/대시보드/데스크톱)가 단일 코어 엔진을 공유"
- 라이브러리 임베드(테스트 하네스)를 위한 공개 API 계약의 품질 기준
- ASR-001 결정: Python. 배포는 pip 패키지 + CLI 진입점
- (대화에서 Direct Input으로 확정된 결정을 ADR로 사후 문서화한 기록)

## Decision
**Option A — 단일 패키지 + 모듈 경계**
User-approved: 배포(distribution) 이름 `sdv-sim`, 임포트(import) 이름 `sdv_sim` (Python 관례: 하이픈→언더스코어). 내부 모듈 `sdv_sim/core`(엔진·모델)와 `sdv_sim/cli`. 공개 API 계약(load/run/events/results)으로 임베드 지원. v2 대시보드는 같은 코어 백엔드 + 별도 프런트엔드.

## Options
### Option A — 단일 패키지 + 모듈 경계
- 하나의 pip 패키지 `sdv-sim`(임포트 `sdv_sim`), 내부에 core/cli 모듈 분리
- Pro: v1 오버헤드 최소 + 경계 유지, 공개 API 계약으로 임베드 지원
- Con: 물리적 패키지 분리보다는 약한 경계

### Option B — 멀티 패키지 워크스페이스
- `sdvsim-core`, `sdvsim-cli` 별도 설치 가능한 패키지 (워크스페이스 도구 필요)
- Pro: 의존성 방향이 가장 명확
- Con: v1 패키징 오버헤드

### Option C — 단일 모듈
- 모든 코드를 한 모듈에
- Pro: 가장 단순
- Con: 경계 없음 → 성장 시 재구성 비용 큼

## Tradeoffs
| | 단일 패키지 (A) | 멀티 패키지 (B) | 단일 모듈 (C) |
|---|----------------|-----------------|---------------|
| core/cli 경계 | ★★★★ | ★★★★★ | ✗ |
| v1 패키징 복잡도 | 낮음 | 높음 | 최저 |
| v2/v3 확장성 | ★★★★ | ★★★★★ | ★★ |

## Recommendation (optional)
- **단일 패키지 + 모듈 경계 (A)** — Direct Input으로 확정됨

## Consequences
- 공개 API 계약(load/load_scenario/run/이벤트 스트림/결과)이 라이브러리 임베드의 품질 기준
- v2 대시보드 추가 시 패키지 구조 변경 불필요 (코어 백엔드 노출)

## Related ASRs
- ASR-006 — 코어 API 경계 & 다중 아티팩트 구조 — 이 ADR이 결정을 문서화

## Downstream Concerns
- [ ] **공개 API 계약 세부:** load/run/이벤트 스트림/결과 리포트의 시그니처
- [ ] **패키징 도구:** src 레이아웃, hatch/setuptools/pdm 선택

## Related
- {project-root}/spec/sdv-sim-v1.md — Spec 반영됨

## Tags
`package`, `api`, `structure`, `cli`, `direct-input`

## Approved
- 2026-08-12: Option A (단일 패키지, 배포명 `sdv-sim`), user confirmed via Direct Input (retroactive ADR documentation)
