# Serve 패키징·통합 (sdv-sim serve)

## Concern
대시보드를 `sdv-sim` 패키지에 통합할 때, `sdv-sim serve`가 프런트엔드(정적 자산)와 백엔드(FastAPI)를 어떻게 제공할 것인가?

## Status
approved

## Context
- v2 제공 형태 = `sdv-sim serve` 명령으로 로컬 웹 대시보드 실행 (PRD v2 "제공 형태").
- v1은 Python 3.11+ 단일 패키지(`sdv-sim`) — ASR-006. 기술 스택 = FastAPI + React/TS + Vite (ASR-014 승인).
- 프런트엔드는 Vite 빌드 산출물(정적 파일)이므로, 이 자산을 어디에 두고 어떻게 서빙할지 결정 필요.
- 로컬 실행 전용, 브라우저에서 localhost로 접속하는 단일 사용자 시나리오.

## Decision
**Option A — 단일 프로세스 + 패키지 내부 정적 자산**
사용자 승인("A 오케이"): `sdv-sim serve`가 FastAPI 앱 + 패키지 내부(dist 포함) 정적 자산을 단일 프로세스로 서빙. 개발 중 `--dev` 모드로 Vite dev server 프록시.

## Options
### Option A — 단일 프로세스 + 패키지 내부 정적 자산 (권장)
- 빌드된 프런트엔드 자산(dist)을 `sdv-sim` 패키지 내부(`sdv_sim/server/static/`)에 포함. `sdv-sim serve`가 FastAPI 앱을 띄우고 정적 자산을 자동 서빙.
- 개발 중에는 `--dev` 플래그로 Vite dev server(HMR)에 프록시 — 소스 변경 실시간 반영.
- Pro: `pip install → sdv-sim serve` 한 줄로 완결 (v1 UX 유지), 단일 프로세스, 배포 산출물 단순
- Con: 프런트엔드 수정 시 빌드 단계 필요(개발 사이클에 포함), wheel 크기 증가

### Option B — 패키지 외부 dist 참조
- `sdv-sim serve`가 정적 자산 경로를 인자/환경변수로 받음(예: `--static-dir ./frontend/dist`). 패키지에는 자산 미포함.
- Pro: 빌드·패키징 분리, 배포 시점 유연
- Con: 설치 후 즉시 실행 불가(자산 별도 준비 필요), 서버가 실행 환경 경로에 의존 — v1 "단일 명령" UX 약화

### Option C — serve 미제공 (직접 실행 안내)
- `sdv-sim serve` 없이, 문서로 uvicorn 실행법 안내 (`uvicorn sdv_sim.server.app:app`).
- Pro: 구현 최소화
- Con: PRD의 제공 형태("예: `sdv-sim serve`")와 불일치, 사용자 부담 증가, 포트·자산 경로 수동 관리

## Tradeoffs
| 차원 | A (패키지 내부) | B (외부 dist) | C (직접 실행) |
|---|------|------|------|
| 설치→실행 UX | ★★★ (명령 하나) | ★★ (자산 별도) | ★ (수동) |
| 개발 편의(HMR) | ★★★ (--dev) | ★★ | ★ |
| 배포 산출물 단순성 | ★★★ | ★★ | ★★★ |
| 구현 비용 | ★★ | ★★ | ★ |

## Recommendation
- **Option A** 권장. v1 단일 패키지 정신(ASR-006)과 PRD 제공 형태("`sdv-sim serve`")를 그대로 만족하고, `--dev` 모드로 개발 편의도 확보. 로컬 전용이므로 패키징 비용은 경미.

## Consequences
- 프런트엔드 빌드는 배포 전 필수 단계로 CI/개발 절차에 포함 (wheel 빌드 시 dist 복사).
- 서버는 단일 프로세스 — 포트(기본값) 정책과 수명주기(Ctrl+C)는 Spec에서 구체화.

## Related ASRs
- ASR-019 — 패키지 통합·서버 명령 (serve) — 본 ADR의 대상
- ASR-006 — v1 단일 패키지 구조 — 확장 방식의 기반

## Downstream Concerns
- [ ] **포트 정책**: `sdv-sim serve` 기본 포트, 충돌 시 처리(자동 증가 vs 오류) — Spec 세부 항목
- [ ] **서버 수명주기·로그**: 시작/종료 메시지, 로그 출력 수준 — Spec 세부 항목
- [ ] **`--dev` 모드 범위**: Vite dev server 프록시의 구성과 플래그 설계 — Spec 세부 항목

## Related
- `spec/PRD.md` — v2 제공 형태
- `spec/ASR.md` — ASR-019, ASR-006

## Tags
`packaging`, `serve`, `deliverable-form`, `fastapi`

## Approved
- 2026-08-12: Option A (단일 프로세스 + 패키지 내부 정적 자산), user confirmed ("A 오케이")
