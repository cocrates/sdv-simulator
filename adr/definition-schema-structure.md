# 정의 파일 스키마 구조 (Definition File Schema Structure)

## Concern
아키텍처/시나리오 YAML의 내부 구조를 어떻게 설계할 것인가? (노드·링크·프레임·컴포넌트 구성, 메시지-프레임 매핑, 파일 분리)

## Status
approved

## Decision
**Option A — 메시지-프레임 2계층 분리 + 매핑 규칙**
User-approved: 컴포넌트는 논리 메시지, 링크는 L2 프레임을 소유. 프레임 message 필드 또는 프레임명=메시지명 기본 규칙. architecture/scenario 파일 분리.

## Context
- ASR-003(YAML) 후속 — 형식은 결정됐으나 스키마 구조는 미정
- v1은 앱 로직 없이도(YAML만으로) 통신 검증이 가능해야 함 (PRD 성공 기준 1·2)
- ADR(definition-file-format)의 Downstream: 파일 구성 분리 여부

## Options
### Option A — 메시지-프레임 2계층 분리 + 매핑 규칙
- 컴포넌트는 논리 메시지(sends/receives), 링크는 L2 프레임(id/dlc/period/source/message)을 소유
- 매핑 규칙: 프레임 `message` 필드 명시 또는 프레임명=메시지명 기본 규칙
- architecture.yaml(노드/링크/프레임/게이트웨이) + scenario.yaml(duration/messages/assertions) 분리
- Pro: L2/L7 계층 분리 명확, 프레임 독립 시뮬레이션(YAML만) 가능, 스키마 검증 명확
- Con: 매핑 개념 1개 추가 (학습 비용 소폭 증가)

### Option B — 단일 프레임 레벨
- 컴포넌트가 프레임을 직접 송수신 (메시지 계층 없음)
- Pro: 스키마 단순
- Con: 앱 로직과 L2 충실도 혼재, 컴포넌트 재사용·신호 표현 불편

### Option C — 신호(signal) 레벨 포함
- DBC 스타일 신호 정의(시작 비트·길이·스케일) 추가
- Pro: 실제 신호 의미 표현 가능
- Con: v1 범위 초과 (L2는 프레임까지만), 스키마 복잡도 급증

## Tradeoffs
| | A (2계층) | B (단일) | C (신호) |
|---|-----------|----------|----------|
| 계층 명확성 | ★★★★★ | ★★★ | ★★★★★ |
| 구현 비용 | 중간 | 낮음 | 높음 |
| YAML만으로 통신 검증 | ✓ | ✓ | ✓ |
| v1 범위 적합성 | ✓ | △ | ✗ (과도) |

## Recommendation (optional)
- **Option A** 추천: v1의 "정의→실행→검증" 루프와 L2 충실도 목표를 동시에 만족

## Consequences
- scenario.yaml은 duration_ms 필수 + messages 주입 + assertions
- 컴포넌트 `class` 필드는 선택 — 미등록 시 스텁(통신만 시뮬레이션)

## Related ASRs
- ASR-003 — 아키텍처/시나리오 정의 형식 — 스키마 구조 세부 결정

## Downstream Concerns
- [ ] **Pydantic 모델 구성:** 스키마 모델 클래스 분리 (arch.py/scenario.py)
- [ ] **오류 메시지 형식:** 파일명·줄 번호·필드 경로 포함 여부 (cli-output-policy와 연계)

## Related
- {project-root}/adr/definition-file-format.md — 상위 결정 (YAML)

## Tags
`schema`, `yaml`, `definition`, `architecture`

## Approved
- 2026-08-12: Option A (메시지-프레임 2계층 분리 + 매핑 규칙), user confirmed
