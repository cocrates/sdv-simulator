# 컴포넌트 API (Component API)

## Concern
컴포넌트 작성자(라이브러리 사용자)에게 어떤 Python API를 제공할 것인가?

## Status
approved

## Decision
**Option A — Component 베이스 클래스 + 콜백 오버라이드 + registry 등록**
User-approved: on_periodic/on_message 콜백 + ctx.send/log. load(arch, scenario, components={...}) 등록. 미등록 시 스텁.

## Context
- ASR-005(RTE 스타일)/ASR-006(코어 API 경계) 후속 — 라이브러리 임베드의 품질 기준
- ADR(app-runtime-model)의 Downstream: 컴포넌트 API 정의
- ADR(package-structure)의 Downstream: 공개 API 계약 세부 시그니처

## Options
### Option A — Component 베이스 클래스 + 콜백 오버라이드 + registry 등록
- `Component` 베이스: `on_periodic(ctx)` / `on_message(ctx, message)` 콜백
- `ctx.send(name, data)` / `ctx.log(...)`
- 등록: `load(arch, scenario, components={"door-controller": DoorController})` + YAML `class` 필드(선택)
- Pro: 명시적·타입 힌트 친화, mypy 검증 용이, RTE 관행과 정합
- Con: 상속 기반 (작성자는 클래스 구조 이해 필요)

### Option B — 데코레이터 기반
- `@component("door-controller")` + `@periodic(10)` 스타일
- Pro: 선언적, YAML과 매핑 간결
- Con: 매직/리플렉션 의존, IDE·타입 검사 지원 약함

### Option C — 순수 함수 콜백
- `{"door-controller": {"periodic": fn, "on_message": fn}}` 형태
- Pro: 최단 작성
- Con: 상태 유지 불편, API 계약 문서화 부담

## Tradeoffs
| | A (베이스 클래스) | B (데코레이터) | C (순수 함수) |
|---|-------------------|---------------|----------------|
| 타입 안정성(mypy) | ★★★★★ | ★★★ | ★★★ |
| RTE 관행 정합 | ★★★★★ | ★★★★ | ★★ |
| 작성 단순성 | ★★★★ | ★★★★★ | ★★★★★ |
| API 명시성 | ★★★★★ | ★★★ | ★★★ |

## Recommendation (optional)
- **Option A** 추천: 라이브러리 임베드(테스트 하네스)가 v1의 1급 사용처이므로 타입 안정성·명시성이 우선

## Consequences
- YAML 미등록 컴포넌트는 스텁 — 통신 시뮬레이션만 실행 (YAML만으로 성공 기준 1·2 충족)
- 공개 API: `load()` / `load_scenario()` / `run()` / 이벤트 스트림 / 결과 리포트 (ASR-006과 정합)

## Related ASRs
- ASR-005 — 앱 런타임 모델 — 컴포넌트 작성 인터페이스 결정
- ASR-006 — 코어 API 경계 — 공개 API 계약에 포함

## Downstream Concerns
- [ ] **TaskContext API 세부:** send/log 외 필요한 메서드 (실행 시각 조회 등)

## Related
- {project-root}/adr/app-runtime-model.md — 상위 결정 (RTE 스타일)
- {project-root}/adr/package-structure.md — 상위 결정 (단일 패키지)

## Tags
`api`, `component`, `python`, `rte`

## Approved
- 2026-08-12: Option A (베이스 클래스 + 콜백 + registry), user confirmed
