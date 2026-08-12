# Dashboard 실행 경로 (run-path): YAML 문자열 → Simulator

## Concern
v2 서버가 `POST /api/run`으로 받은 **YAML 문자열**로 v1 코어 `Simulator`를 생성·실행하는 경로를 무엇으로 할 것인가? v1 공개 API `load()`의 `str` 인자는 **파일 경로만** 수용하므로 "YAML 문자열 직접 전달"은 불가능(C-1). v1 코어를 수정해 문자열 입력 API를 추가할 것인가, 기존 공개 요소(스키마 모델 + Simulator 생성자)로 구현할 것인가?

## Status
superseded

> **2026-08-12:** 사용자 F-11 방향 전환("서버에 저장한다는 개념은 부적절" + v1 core/CLI에 YAML 문자열 입력 API 추가 지시)으로 이 ADR의 **Option A (v1 무변경)** 결정은 폐기된다. 교체: `adr/core-yaml-string-input.md` (proposed — 사용자 리뷰 대기).

## Context
- v2 spec "데이터 흐름·리플레이"는 `load(arch_str, scenario_str)` 사용을 명시했으나, v1 `load()`는 `Path(path).read_text()`를 수행 — 문자열을 경로로 취급해 항상 실패 (spec review C-1, 2026-08-12).
- v1 공개 계약 (D-15): `load(arch: str|Path, scenario: str|Path, ...)`. 그러나 `Simulator(Architecture, Scenario)` 생성자와 `Architecture`/`Scenario` Pydantic 모델은 공개 코드이며, v1 spec은 이 스키마 모델을 "구현 SSOT"(Pydantic 1:1)로 명시.
- PRD 제약·성공 기준 5: "대시보드는 **v1 코어를 변경하지 않고** 백엔드로 재사용 (코어 공개 API 계약 유지)" — 사용자 확정 사항.
- ASR-006: "v2/v3(대시보드, OTA)가 코어 변경 없이 추가될 수 있는 모듈 경계 유지" — v1 완료 스테이지의 경계.
- ASR-018 / editor-validation-feedback: 서버가 v1 Pydantic 스키마로 검증 — `sdv_sim/server/`에 YAML 파싱·검증·줄 번호 매핑 유틸이 **이미 필요** (오류는 줄 단위 인라인 표시).

## Decision
**Option A — v1 무변경: 스키마 모델 직접 파싱 + Simulator 생성자** (2026-08-12 사용자 승인 "오케이 Option A로 하자"): 서버가 v1 공개 스키마 모델(`Architecture`/`Scenario`)로 YAML 문자열을 파싱·검증한 뒤 `Simulator(arch_model, scenario_model)` 생성자로 실행한다. `load()`의 파일 경로 시그니처는 사용하지 않는다.

## Options
### Option A — v1 무변경: 스키마 모델 직접 파싱 + Simulator 생성자
- 서버가 YAML 문자열 → `yaml.safe_load` → `Architecture.model_validate` / `Scenario.model_validate` (v1 공개 스키마) → `Simulator(arch_model, scenario_model).run()`.
- `POST /api/validate`와 `POST /api/run`이 동일한 서버측 파싱·검증 유틸을 공유 (`sdv_sim/server/` 내 신규 코드 — v1 모듈 무변경).
- Pro: PRD "v1 코어 무변경"·성공 기준 5 완전 준수 / v1 재검증·재승인 불필요 / 검증 API와 실행 경로의 파싱 로직 단일화 / 임시 파일 불필요
- Con: v1 private 헬퍼(`_load_yaml_model`·`_locate_line`)의 기능(줄 번호 매핑·오류 포맷)을 서버 모듈에서 재구현 — 단, ASR-018로 이미 서버측 구현이 예정된 기능이므로 추가 부담은 미미

### Option B — v1 수정: 문자열 입력 공개 API 추가 (`load_str`)
- v1 코어에 `load_str(arch_yaml: str, scenario_yaml: str, components: dict | None = None) -> Simulator` 공개 API 추가 (파일 경로 대신 내용 문자열).
- Pro: "문자열 입력"이 v1 계약에 정식화 — v3(데스크톱)·테스트 하네스도 동일 진입점 재사용 / 파싱·오류 포맷 로직이 v1 단일 진실 소스로 유지 / 서버 코드 최소화
- Con: **PRD "v1 코어 무변경" 제약·성공 기준 5 위반** — v1 스펙(D-15)·ASR-006 Resolution·테스트·검증 보고서 갱신과 재승인 필요 (v1 "완료" 스테이지 재개) / "형태별 요구가 코어를 변경하지 않는다"는 경계의 의미 약화 — v2/v3 요구가 v1을 계속 확장하는 슬라이딩 스코프 위험

> 참고: 임시 파일 경유 방안(temp 파일 기록 후 기존 `load()` 호출)은 spec review 단계에서 배제 — temp 파일 관리·임의 파일명 오류 메시지·불필요한 I/O, 비권장.

## Tradeoffs
| 차원 | A (v1 무변경) | B (v1 수정) |
|------|---------------|-------------|
| PRD "v1 코어 무변경" (제약·성공 기준 5) | ✅ 준수 | ❌ 위반 (계약·스펙·검증 재개) |
| v1 재검증·재승인 비용 | 없음 | 필요 (D-15/ASR-006/테스트/검증 보고서) |
| 문자열 입력의 정식 계약화 (v3·테스트 하네스 재사용) | 없음 — 서버 내부 패턴 | v1 계약에 포함 |
| 파싱·오류 포맷 단일 소스 | 서버 모듈에 재구현 (ASR-018로 이미 예정된 기능) | v1 단일 소스 |
| 서버 구현량 | 중간 (파싱·줄 매핑 유틸 1회 작성 후 공유) | 작음 (load_str 호출) |
| 모듈 경계·스코프 안정성 | 경계 유지, v1 완료 상태 유지 | 경계 약화, 슬라이딩 스코프 위험 |

## Recommendation
- **Option A** 권장. PRD가 사용자 확정으로 명시한 "v1 코어 무변경"을 지키면서, 서버측 파싱·검증 유틸은 ASR-018(편집·검증)에서 이미 필요로 하는 기능이라 추가 비용이 거의 없음. v1의 승인·검증 상태를 훼손하지 않는 것이 이번 스테이지의 핵심 제약. Option B의 장점(단일 소스)은 서버 모듈 내 유틸 1회 작성으로 대부분 흡수됨.

## Consequences
- v1 코어·스펙·검증 상태 무변경 — v1 계약(`load`/`run`/`events`) 그대로 유지, 재검증 불필요
- `sdv_sim/server/`에 파싱·검증 유틸 신규 작성 — `POST /api/validate`·`POST /api/run`이 공유 (줄 번호 매핑 포함)
- `POST /api/run`은 Simulator 생성자 사용 — v2 spec의 `load(arch_str, scenario_str)` 문구 수정 필요 (spec-writing 단계 반영)
- 명시적 배제: v1 코어 수정, `load()` 계약 변경, temp 파일 경유

## Related ASRs
- ASR-015 — 데이터 흐름·리플레이 — 코어 임베드 실행 메커니즘을 확정하는 본 ADR의 대상
- ASR-006 — 코어 API 경계 — "v1 무변경" 경계의 원천 (컨텍스트)
- ASR-014 — 기술 스택 — FastAPI 서버 구현의 전제 (컨텍스트)

## Downstream Concerns
- [ ] **서버 검증 유틸 오류 포맷**: `POST /api/validate`·`/api/run` 오류 응답 구조 `{path, line, message}` — v1 `SdvSimInputError.format()`(파일명·줄·필드 경로, ko/en)와 정합 방식 (spec 인코딩)
- [ ] **/api/validate의 시나리오 단독 검증 범위**: 참조 검증(unknown link/frame 등)은 아키텍처 없이 불가 — 구조 검증만 가능함을 spec에 명시
- [ ] **M-1 연계**: load-log 경로의 Report 파생 규칙 — `adr/dashboard-load-log-report.md`에서 처리

## Related
- `adr/dashboard-data-flow-replay.md` — 상위 ADR (코어 임베드 + 일괄 JSON 전달)
- `spec/sdv-sim-v2.md` — C-1 수정 대상 (spec-writing으로 반영)

## Tags
`dashboard`, `run-path`, `api`, `public-api`, `core-boundary`

## Approved
- 2026-08-12: Option A (v1 무변경 — 스키마 모델 직접 파싱 + Simulator 생성자), user confirmed ("오케이 Option A로 하자")
