# v1 코어 YAML 문자열 입력 API (core-yaml-string-input)

## Concern
v1 코어/CLI가 **파일 경로 대신 YAML 문자열**을 입력받는 공개 API를 어떤 형태로 제공할 것인가? (F-11 방향 전환 — 브라우저 로컬 파일 사용 → 서버는 파일 경로가 아닌 YAML **내용**을 수신)

## Status
approved

## Context
- **F-11 사용자 방향 전환 (2026-08-12):** "서버에 저장한다는 개념은 부적절" — 브라우저가 로컬 파일을 직접 읽고 쓰고, 검증·실행을 위해 파일 **내용(문자열)**만 서버로 전달. 기존 서버-FS 샌드박스(`--root`) 설계 대체.
- v1 현재 API: `load(arch: str|Path, scenario: str|Path, components=None) -> Simulator` — `str`은 **파일 경로** (`engine.py` L836-844: `Path(path).read_text()`). `load_scenario(scenario: str|Path)`도 경로 전용 (L287-293). `Simulator.__init__(arch: Architecture, scenario: Scenario)` 생성자는 모델 객체만 수용 (L206-211).
- `dashboard-run-path` ADR (approved 2026-08-12): **Option A — v1 무변경** (서버가 스키마 모델 직접 파싱 + 생성자). 이번 사용자 지시("v1 core/cli를 수정해 YAML 문자열 입력 API를 밀어넣고")로 **방향 전환** — supersede 필요.
- PRD 제약·성공 기준 5: "대시보드는 **v1 코어를 변경하지 않고** 백엔드로 재사용" — 사용자 방향 전환으로 **갱신 필요** (PRD 개정).
- Python 관례: `json.load`(경로/파일) ↔ `json.loads`(문자열) — 명명 패턴 선례.
- v1 에러 체계: `SdvSimInputError`(파일명·줄 번호·필드 경로, ko/en) — 문자열 입력에서 "파일명" 대신 어떤 식별자를 쓸지가 파생 질문.

## Decision
**Option A — 전용 `loads`/`load_str` 계열 함수 추가 (json.loads 관례)** (2026-08-12 사용자 승인 "오케이"): 기존 경로 기반 `load()`·`load_scenario()`를 보존하고, `loads(arch_yaml: str, scenario_yaml: str, components=None) -> Simulator`와 `Simulator.load_scenario_yaml(scenario_yaml: str)`을 공개 API로 추가한다. v1 계약(D-15)의 하위 호환을 지키면서 브라우저 문자열 전달 경로를 명시적으로 제공.

## Options
### Option A — 전용 `loads`/`load_str` 계열 함수 추가 (json.loads 관례)
- `loads(arch_yaml: str, scenario_yaml: str, components=None) -> Simulator` + `Simulator.load_scenario_yaml(scenario_yaml: str)` 추가. 기존 `load()`·`load_scenario()`는 경로 전용으로 **유지**.
- Pro: Python 표준 관례와 일치, 기존 계약 불변(하위 호환), 명시적·타입 안전, 에러 포맷 로직 재사용
- Con: API 표면 2배(경로 + 문자열), 동의어 API로 혼동 가능성

### Option B — `load()` 단일 함수에 감지 로직 통합
- `str` 인자가 "존재하는 파일 경로"인지 "YAML 내용"인지 판별(존재 체크/확장자/`---` prefix)해 자동 분기.
- Pro: API 단일, 호출 측 단순
- Con: **모호성 위험** — 존재하지 않는 경로 문자열 vs 파싱 실패 내용을 구분 불가, 오류 진단 혼란, 타입 안전성 약화 (mypy에서 str|Path 유지하나 의미론적 혼재)

### Option C — Simulator 클래스메서드/생성자 오버로드
- `Simulator.from_yaml(arch_yaml, scenario_yaml, components=None)` 클래스메서드 추가 (모델 파싱 포함). `__init__`은 모델 객체 전용 유지.
- Pro: "Simulator 생성" 진입점에 통합, 생성자 계약 유지
- Con: v1의 `load()`-함수 패턴과 이원화, 문서/임포트 경로가 2곳으로 분산

## Tradeoffs
| 차원 | A (loads 함수) | B (감지 통합) | C (from_yaml) |
|------|----------------|---------------|----------------|
| 하위 호환 (v1 계약) | ★★★★★ | ★★ (의미 혼재) | ★★★★★ |
| 명시성·타입 안전 | ★★★★★ | ★★ | ★★★★ |
| Python 관례 정합 | ★★★★★ | ★★ | ★★★ |
| 오류 진단 명확성 | ★★★★ (별도 함수) | ★ (경로/내용 구분 모호) | ★★★★ |
| API 표면 단순성 | ★★★ | ★★★★★ | ★★★★ |

## Recommendation
- **Option A** 권장. Python `json.load`/`json.loads` 관례를 따라 기존 경로 기반 `load()`를 보존하고 `loads()`를 추가 — v1 계약(D-15)의 하위 호환을 지키면서 브라우저 문자열 전달 경로를 명시적으로 제공. B의 감지 로직은 오류 진단 모호성이 커 배제.

## Consequences
- v1 공개 API 계약(D-15)에 `loads()`·`load_scenario_yaml()` 추가 — **v1 스펙·검증 보고서 갱신 필요** (v1 "완료" 상태 재개 → 재승인)
- `dashboard-run-path` ADR의 Option A(v1 무변경)는 **superseded** — run 경로는 서버 파싱 유틸 대신 v1 `loads()` 사용
- PRD 제약 "v1 코어 무변경"(제약·성공 기준 5) **삭제/개정** — "v1 코어 확장(문자열 입력 API 추가)"으로 변경
- ASR-006 Resolution 갱신 ("v1 무변경" → "문자열 입력 API 추가 허용")
- 명시적 배제: 경로/내용 자동 감지, 임시 파일 경유

## Related ASRs
- ASR-006 — 코어 API 경계 — 공개 API 계약(D-15)을 확장하는 본 ADR의 대상
- ASR-015 — 데이터 흐름·리플레이 — run 경로가 v1 `loads()` 사용으로 변경

## Downstream Concerns
- [ ] **CLI 문자열 입력 플래그**: `sdv-sim run`에 `--arch-yaml`/`--scenario-yaml`(stdin 포함) 지원 여부 — 사용자가 "v1 core/**cli** 수정"이라 지시했으므로 CLI 스코프 확정 필요
- [ ] **오류 식별자**: 문자열 입력에서 `SdvSimInputError.filename` 대체 — `<yaml-string>`/`arch`/`scenario` 같은 의사 파일명 규칙
- [ ] **v1 재검증 범위**: 추가된 API의 v1 테스트·검증 보고서·승인 재개 범위

## Related
- `adr/dashboard-run-path.md` — **superseded** (v1 무변경 → v1 확장으로 방향 전환)
- `adr/public-api-contract.md` — 기존 D-15 시그니처의 원천 (보존 + 확장)
- `adr/dashboard-browser-file-access.md` — 동반 ADR (F-11의 브라우저 측)
- `spec/sdv-sim-v1.md` — D-15 갱신 대상
- `spec/sdv-sim-v2.md` — run 경로 문구 수정 대상 (spec-writing)

## Tags
`v1-core`, `api`, `string-input`, `yaml`, `dashboard`, `f-11`

## Approved
- 2026-08-12: Option A (loads() 전용 함수 추가 — json.loads 관례, 기존 load() 보존), user confirmed ("오케이")
