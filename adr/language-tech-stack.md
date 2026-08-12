# 언어/기술 스택 (Language / Tech Stack)

## Concern
시뮬레이터 코어와 CLI를 어떤 프로그래밍 언어/런타임으로 구현할 것인가?

## Status
approved

## Context
- PRD 승인됨 (v1 = 라이브러리 코어 + CLI, 헤드리스 실행, CI/자동화 필수)
- v2에서 웹 대시보드가 같은 코어를 공유해야 함
- 대상 청중: 차량 SW 개발자/아키텍트 — 통합(임베드) 용이성이 중요
- 시뮬레이션 영역: E/E 아키텍처 + CAN/Ethernet 통신 + 앱 런타임 (이산 사건 시뮬레이션 가능성 높음 — ASR-002)

## Decision
**Option A — Python**
User-approved: 코어 라이브러리와 CLI를 Python(3.11+, 타입 힌트 + mypy)으로 구현. 배포는 pip 패키지 + CLI 진입점. 성능 병목 지점은 필요 시 확장 모듈로 이관 가능.

## Options
### Option A — Python
- 고수준 언어, 빠른 프로토타이핑과 개발 생산성. 타입 힌트 + mypy로 타입 안정성 보완 가능
- Pro: 개발 생산성 최고, 자동차 테스트 자동화 생태계(python-can 등)와 친화적, 라이브러리 임베드·테스트 하네스 작성이 자연스러움, 에코시스템(YAML/JSON, pytest, Typer CLI) 성숙
- Con: CPU 집약 시뮬레이션 성능 제한, 배포 시 Python 런타임 의존

### Option B — TypeScript/Node.js
- 타입 안정성을 갖춘 웹 생태계 언어. npm 패키지로 배포
- Pro: v2 웹 대시보드와 동일 언어로 개발 가능, 타입 안정성, CLI 도구 생태계 풍부
- Con: CPU 집약 시뮬레이션에 불리, 차량 SW 개발자와의 친화성 낮음, 런타임(Node) 의존

### Option C — Go
- 간결한 문법, 빠른 컴파일, 단일 바이너리 배포
- Pro: 성능과 생산성의 균형, CI/자동화 친화적(단일 바이너리), 동시성 지원
- Con: 시뮬레이션 도메인 에코시스템(CAN/Ethernet 모델링) 부족, 제네릭·표현력이 Rust 대비 약함

### Option D — Rust
- 시스템 언어, 최고 성능, 메모리 안전, 결정적 실행에 유리
- Pro: 성능 최고, 단일 바이너리, 엄격한 타입 시스템으로 시뮬레이션 정확성 유지에 유리
- Con: 개발 생산성 낮음(학습 곡선), 프로토타이핑 속도 저하, 에코시스템 상대적으로 부족

### Option E — C++ (참고)
- 차량 SW 산업 표준(AUTOSAR 등)과 동일 계열. 성능 우수
- Con: 개발 생산성 낮음, 메모리 안전 위험 — 이 프로젝트의 생산성 요구와 불일치

## Tradeoffs
| | Python (A) | TypeScript (B) | Go (C) | Rust (D) |
|---|------------|----------------|--------|----------|
| 개발 생산성 | ★★★★★ | ★★★★ | ★★★★ | ★★★ |
| 시뮬레이션 성능 | ★★ | ★★★ | ★★★★ | ★★★★★ |
| 임베드/라이브러리 용이성 | ★★★★★ | ★★★★ | ★★★★ | ★★★ |
| CI/자동화 친화성 | ★★★★★ | ★★★★ | ★★★★★ | ★★★★ |
| CAN/Ethernet 에코시스템 | ★★★★★ | ★★★ | ★★ | ★★ |
| 차량 SW 개발자 친화성 | ★★★★★ | ★★ | ★★★ | ★★★ |
| v2 대시보드 연계 | ★★★★ | ★★★★★ | ★★★ | ★★★ |

## Recommendation (optional)
- **Option A (Python)** 추천: 헤드리스 시뮬레이터 + 개발자 임베드 + CI 자동화라는 v1 목표에 개발 생산성이 가장 크게 기여. 자동차 테스트 자동화 영역에서 Python이 사실상 표준(python-can, vTESTstudio 계열)이라 대상 청중 친화성도 높음. 성능 병목은 후속 단계에서 병목 지점만 확장 모듈(Rust/C)로 이관 가능. v2 대시보드는 FastAPI 백엔드로 코어를 그대로 노출하고 프런트엔드만 JS로 분리하면 됨.

## Consequences
- Python 런타임(3.11+) 의존 발생 — 배포는 pip 패키지 + CLI 진입점으로 해결
- 성능 상한 존재 — 대규모 시나리오(수천 노드·수백만 메시지)에서는 병목 지점 확장 모듈 필요 가능
- 타입 안정성은 타입 힌트 + mypy로 관리
- C++/AUTOSAR 생태계와의 직접 통합은 v1에서 제외 (API 경계로 분리 — ASR-006)

## Related ASRs
- ASR-001 — 언어/기술 스택 — 이 ADR이 해결

## Downstream Concerns
- [ ] **시뮬레이션 성능 전략:** 순수 Python으로 v1 충분한지, 병목 시 어떤 확장 수단을 쓸지 (ASR-002 엔진 모델과 연계)
- [ ] **패키징/배포:** pip 패키지 구조, CLI 진입점, 버전 관리
- [ ] **정의 파일 형식:** YAML/JSON/TOML 중 선택 (ASR-003에서 별도 결정)

## Related
- 다음 검토: ASR-002 (시뮬레이션 엔진 모델)

## Tags
`tech-stack`, `language`, `simulator`

## Approved
- 2026-08-12: Option A (Python), user confirmed
