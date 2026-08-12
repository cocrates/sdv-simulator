# 편집·검증 피드백 모델

## Concern
YAML 텍스트 편집에서 스키마 검증 피드백을 어디서 어떻게 제공할 것인가? (검증 시점, 오류 표시 위치, v1 Pydantic 스키마 재사용 전략)

## Status
approved

## Context
- v2 편집 방식 = YAML 텍스트 편집 + 실시간 다이어그램 동기화 + 스키마 검증 피드백 (PRD v2, 편집 Option A 확정).
- v1은 정의 형식을 Pydantic 스키마(`sdv_sim/schema/`)로 검증 (ASR-003). 이 스키마가 단일 진실 소스.
- 기술 스택 = FastAPI + React/TS (ASR-014). 로컬 단일 사용자 — 서버 왕복 지연 미미.

## Decision
**Option A — 서버 검증 (v1 Pydantic 스키마 그대로) + 디바운스 자동 검증**
사용자 위임 계속 진행 (2026-08-12 auto-continue): 편집 시 서버가 v1 Pydantic 스키마로 검증, 오류를 편집기 인라인 표시. 다이어그램 동기화는 유효한 파싱에서만 반영.

## Options
### Option A — 서버 검증 (v1 Pydantic 스키마 그대로)
- 편집 중 디바운스(예: 500ms) 서버 검증 API 호출 + 저장/실행 시 최종 검증. 오류는 줄 단위 인라인 표시.
- Pro: v1 스키마 100% 재사용 — 검증 진실 소스 단일화, 이중 관리 없음, 커스텀 검증 규칙 포함 그대로 동작
- Con: 타이핑 중 피드백이 서버 왕복에 의존 (로컬이라 지연 미미)

### Option B — 프런트엔드 검증 (Pydantic → JSON Schema 포팅)
- v1 스키마를 JSON Schema로 변환해 프런트엔드에서 입력 중 즉시 검증.
- Pro: 즉시 피드백, 저장 불필요
- Con: 스키마 파생·동기화 유지보수 필요, 커스텀 규칙(예: 참조 검증)은 별도 구현, 이중 진실 소스 리스크

### Option C — 하이브리드 (프런트엔드 경량 + 서버 정확)
- 프런트엔드 JSON Schema로 구조·타입 오류 즉시 표시 + 서버 Pydantic으로 최종 정확 검증.
- Pro: UX 최고 (즉시 + 정확)
- Con: 구현량 최대 — B의 동기화 문제 + A의 구현을 모두 부담

## Tradeoffs
| 차원 | A (서버 Pydantic) | B (프런트 JSON Schema) | C (하이브리드) |
|---|------|------|------|
| v1 스키마 단일 진실 소스 | ★★★ | ★★ | ★★ |
| 피드백 지연 | ★★ (로컬 — 미미) | ★★★ | ★★★ |
| 구현 비용 | ★★★ | ★★ | ★ |
| 커스텀 규칙 검증 | ★★★ (그대로) | ★★ | ★★ |

## Recommendation
- **Option A** 권장. 로컬 전용이라 지연 우려가 없고, v1 Pydantic 스키마를 그대로 진실 소스로 유지해 "코어 무변경" 제약과도 정합. 실시간 다이어그램 동기화는 유효 파싱 시에만 반영(오류 시 마지막 유효 상태 유지 + 인라인 오류 표시)으로 충분.

## Consequences
- 검증 API(`POST /api/validate`) 추가 — v1 스키마 로드 후 YAML 파싱·검증 결과(오류 위치·메시지) 반환.
- 편집기에는 오류 마커(줄 번호·메시지) 표시, 검증 통과 시에만 다이어그램 갱신.
- 프런트엔드 스키마 포팅은 비목표.

## Related ASRs
- ASR-018 — 편집·검증 피드백 — 본 ADR의 대상
- ASR-003 — v1 정의 형식 — Pydantic 스키마 재사용의 원천
- ASR-017 — 파일시스템 보안 — 저장 검증 흐름의 전제

## Downstream Concerns
- [ ] **검증 응답 형태**: 오류 메시지 구조(경로/줄 번호/메시지/레벨) — Spec 인코딩
- [ ] **디바운스 정책**: 자동 검증 주기(500ms), 저장 시 강제 검증 — Spec 인코딩

## Related
- `spec/PRD.md` — v2 편집·파일 관리
- `spec/ASR.md` — ASR-018, ASR-003, ASR-017

## Tags
`editor`, `validation`, `pydantic`, `dashboard`

## Approved
- 2026-08-12: Option A (서버 Pydantic 검증 + 디바운스), user delegated continuation ("계속 진행해 주세요")
