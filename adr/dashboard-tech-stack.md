# Dashboard Tech Stack (백엔드·프런트엔드)

## Concern
웹 대시보드의 백엔드·프런트엔드 기술 스택을 무엇으로 할 것인가?

## Status
approved

## Context
- v2 = 구조 뷰(토폴로지 다이어그램) 중심 로컬 웹 대시보드. 구조 뷰에서 시뮬레이션 리플레이(애니메이션), YAML 편집 + 실시간 동기화, 로컬 파일 저장을 제공 (PRD v2).
- v1은 Python 3.11+ 단일 패키지(`sdv-sim`) — 코어는 Pydantic 스키마 기반 (ASR-001, ASR-003, ASR-006).
- PRD 제약: v1 코어 무변경 재사용, ko/en UI, 로컬 실행 전용, 파일시스템 접근 = 프로젝트 루트 제한.
- 핵심 요구: (1) v1 Pydantic 스키마 재사용(검증 피드백), (2) 대용량 이벤트(≤100만) 리플레이 애니메이션, (3) 커스텀 토폴로지 캔버스.

## Decision
**Option A — FastAPI(백엔드) + React/TypeScript + Vite(프런트엔드)**
사용자 승인("A로 해줘"): v1 Pydantic 스키마 네이티브 재사용, 커스텀 캔버스·이벤트 스트리밍 자유도가 v2 핵심 요구에 가장 적합.

## Options
### Option A — FastAPI(백엔드) + React/TypeScript + Vite(프런트엔드)
- FastAPI: Python 3.11+ async 웹 프레임워크, **Pydantic 네이티브** (v1 스키마 그대로 재사용 — 검증 피드백 API 자동 생성), OpenAPI 문서 자동화, SSE/WebSocket 지원(이벤트 스트리밍).
- React + TypeScript: 성숙한 생태계(그래프/차트 라이브러리 풍부), 타입 안전, 커스텀 캔버스(SVG/Canvas) 제어 자유도 최고.
- Vite: 빠른 개발 서버·빌드.
- Pro: v1 스키마 재사용 최적 / 이벤트 스트리밍·커스텀 렌더링에 가장 유리 / 에코시스템 최대
- Con: Node.js 프런트엔드 빌드 파이프라인 필요(개발 복잡도 증가)

### Option B — FastAPI(백엔드) + Vue 3/TypeScript + Vite(프런트엔드)
- 백엔드 장점은 A와 동일. Vue 3 Composition API + TypeScript.
- Pro: 템플릿 직관성, 단일 파일 컴포넌트
- Con: React 대비 그래프/캔버스 레퍼런스·에코시스템이 상대적으로 적음 (기능상 A와 동급 — 선택은 팀 취향)

### Option C — Python 단일 (Streamlit 또는 Plotly Dash)
- 백엔드·프런트엔드 모두 Python. 빌드 없음, 설치 단순.
- Pro: 단일 언어, v1 패키지 통합 단순, 개발 속도 빠름
- Con: **커스텀 토폴로지 캔버스 + 대용량 이벤트 애니메이션 리플레이(구조 뷰 오버레이 — v2 핵심) 구현에 제약**, 프레임워크 제약에 갇힘, 성능 커스터마이즈 어려움

## Tradeoffs
| 차원 | A (FastAPI+React) | B (FastAPI+Vue) | C (Python 단일) |
|---|------|------|------|
| v1 Pydantic 재사용 | ★★★ (네이티브) | ★★★ | ★★ (직접 구현) |
| 커스텀 캔버스/리플레이 | ★★★ | ★★★ | ★ (프레임워크 제약) |
| 이벤트 스트리밍 | ★★★ (SSE/WebSocket) | ★★★ | ★★ |
| 개발 복잡도 | ★★ (Node 빌드) | ★★ (Node 빌드) | ★ (빌드 없음) |
| 에코시스템 | ★★★ | ★★ | ★★ |

## Recommendation
- **Option A (FastAPI + React/TypeScript + Vite)** 권장. v2 핵심(구조 뷰 오버레이 리플레이, 스키마 검증 피드백)을 최소 제약으로 구현할 수 있고 v1 Pydantic 재사용이 가장 자연스러움.

## Consequences
- 프런트엔드(TypeScript)는 별도 빌드 산출물 — 배포 시 정적 자산을 패키지에 포함 (ASR-019와 연결).
- 개발 의존성에 Node.js 추가 (프런트엔드 빌드 전용 — 런타임은 정적 자산 서빙).

## Related ASRs
- ASR-014 — 대시보드 기술 스택 — 본 ADR의 대상

## Downstream Concerns
- [ ] **이벤트 전달 프로토콜 (ASR-015)**: 실행 결과를 프런트엔드로 전달하는 방식 — SSE vs WebSocket vs 일괄 JSON
- [ ] **토폴로지 렌더링 라이브러리 (ASR-016)**: SVG vs Canvas, 그래프 라이브러리(예: Cytoscape.js/D3) vs 커스텀 렌더
- [ ] **정적 자산 패키징 (ASR-019)**: 프런트엔드 빌드 산출물을 `sdv-sim` wheel에 포함하는 방식

## Related
- `spec/PRD.md` — v2 범위 (동작 방식·구조 뷰·편집·시뮬레이션)
- `spec/ASR.md` — ASR-014

## Tags
`dashboard`, `tech-stack`, `frontend`, `backend`

## Approved
- 2026-08-12: Option A (FastAPI + React/TypeScript + Vite), user confirmed ("A로 해줘")
