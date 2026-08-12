# 공개 API 계약 (Public API Contract)

## Concern
라이브러리 공개 API(load/load_scenario/run/이벤트 스트림/TaskContext/결과)의 **정확한 시그니처**는 무엇인가?

## Status
approved

## Decision
**Option A — 경로 기반 + 결과 객체**
User-approved: load/run → SimulationResult(events 리스트), TaskContext(send/log/now_ms), 이벤트 스트림 = 결과 리스트.

## Context
- ASR-005/006 후속 — "load/run/events/results" 계약은 결정됐으나 시그니처 미정
- Gate 5 재검토 그룹 A-4: 테스트 하네스 임베드(PRD 목표)의 품질 기준
- component-api Downstream open: TaskContext API 세부(실행 시각 조회 등)

## Options
### Option A — 경로 기반 + 결과 객체
- `load(arch: str|Path, scenario: str|Path, components: dict[str, type[Component]] | None = None) -> Simulator`
- `Simulator.run() -> SimulationResult` — `events: list[Event]`(결정적, 전체 버퍼), `report: Report`, `assertions: list[AssertionResult]`, `duration_ms: int`
- `TaskContext`: `send(name: str, data: Any)`, `log(message: str)`, `now_ms() -> int` (실행 시각 조회)
- 이벤트 스트림 = `SimulationResult.events` 리스트 (소비자가 직접 순회)
- Pro: 단순·타입 명시·임베드 직관, 1M 이벤트 버퍼 메모리 수용(성능 목표 내), 결정성 보존
- Con: 실시간 스트리밍 소비 불가(전체 실행 후 반환)

### Option B — 파일 객체/딕셔너리 수용 + 콜백
- `load(arch: str|Path|dict, ...)`, `run(on_event: Callable[[Event], None])` 콜백
- Pro: 메모리 효율, 유연한 입력
- Con: 콜백 순서·예외 처리 부담, 타입 힌트 약화

### Option C — 이터레이터 스트리밍
- `run()`이 이벤트 이터레이터(generator) 반환
- Pro: 실시간 소비 가능
- Con: assertion/리포트가 전체 로그 필요 → 내부 버퍼 유지 필수, API 복잡도 증가

## Tradeoffs
| | A (경로+결과 객체) | B (딕셔너리+콜백) | C (이터레이터) |
|---|------|------|------|
| 임베드 용이성 | ★★★★★ | ★★★★ | ★★★ |
| 타입 안정성(mypy) | ★★★★★ | ★★★ | ★★★★ |
| 메모리 | 중간(1M 허용) | 낮음 | 낮음 |
| 구현 단순성 | ★★★★★ | ★★★ | ★★ |

## Recommendation (optional)
- **Option A**: v1 목표 규모(이벤트 ≤ 1M)에서 리스트 반환이 가장 단순·안전. 콜백/이터레이터는 v2 대시보드 시점에 추가 가능.

## Consequences
- 이벤트 스트림 = 로그 스키마의 events와 동일 구조 — JSON 직렬화와 1:1
- Report 구조는 D-21(result-report-schema)에서 확정

## Related ASRs
- ASR-005 — 앱 런타임 모델 — TaskContext·컴포넌트 작성 인터페이스
- ASR-006 — 코어 API 경계 — 공개 API 계약

## Downstream Concerns
- [ ] **Event/Report/AssertionResult 타입 정의:** dataclass vs pydantic 모델 (로그 스키마와 정합)
- [ ] **예외 타입:** 입력 오류·내부 오류 예외 클래스 분류 (cli-output-policy와 연계)

## Related
- {project-root}/adr/component-api.md, package-structure.md — 상위 결정
- {project-root}/adr/event-log-schema.md — 이벤트 구조

## Tags
`api`, `library`, `contract`, `signature`

## Approved
- 2026-08-12: Option A (경로 기반 + 결과 객체), user confirmed
