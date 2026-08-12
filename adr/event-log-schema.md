# 이벤트 로그 스키마 (Event Log Schema)

## Concern
결정적 이벤트 로그를 어떤 구조/형식으로 출력할 것인가?

## Status
approved

## Decision
**Option A — 단일 JSON 파일 (events 배열 + type enum)**
User-approved: {schema_version, simulation, events[], assertions[]} 구조. type enum 7종, (t_ms, seq) 오름차순.

## Context
- ASR-007(JSON 이벤트 스트림) 후속 — CI 재사용의 핵심 산출물
- ADR(verification-automation)의 Downstream: 로그 스키마 정의(이벤트 타입, 타임스탬프)
- 결정성: 동일 입력 → 동일 로그

## Options
### Option A — 단일 JSON 파일 (events 배열 + type enum)
- `{schema_version, simulation{duration_ms, result}, events:[{t_ms, seq, type, node?, link?, frame?, task?, data?}], assertions:[{name, status, detail}]}`
- type enum: tx | rx | task_start | task_end | drop | overrun | log
- (t_ms, seq) 오름차순 저장, 누락 필드는 생략
- Pro: 단일 산출물(CI 아티팩트), 스키마 검증 용이, 결정성 표현 명확
- Con: 대규모 시나리오에서 파일 크기 증가 (v1 목표 규모에서는 무시 가능)

### Option B — NDJSON 스트림
- 이벤트 1건 = 1라인
- Pro: 파일 크기 효율, 스트리밍 처리
- Con: 단일 JSON 문서가 아니어서 스키마 검증·시각화 불편

### Option C — 타입별 분리 배열
- `{tx: [...], rx: [...], task: [...]}` 구조
- Pro: 타입별 조회 용이
- Con: 순서 복원에 추가 정보 필요 (결정성 표현 약화)

## Tradeoffs
| | A (단일 배열) | B (NDJSON) | C (분리 배열) |
|---|---------------|------------|---------------|
| 결정성 표현 | ★★★★★ | ★★★★★ | ★★★ |
| CI 산출물 적합성 | ★★★★★ | ★★★★ | ★★★★ |
| 스키마 검증 | ★★★★★ | ★★★ | ★★★★★ |
| 구현 단순성 | ★★★★★ | ★★★ | ★★★ |

## Recommendation (optional)
- **Option A** 추천: v1 목표 규모(이벤트 ≤ 1M)에서는 단일 JSON 파일이 가장 단순하고 CI 친화적

## Consequences
- 이벤트 타입 7종: tx/rx/task_start/task_end/drop/overrun/log
- 타임스탬프는 정수 ms (simulation-time-model 결정과 정합)

## Related ASRs
- ASR-007 — 검증·자동화 지원 — 로그 스키마 세부 결정

## Downstream Concerns
- [ ] **버전 관리:** schema_version 정책 (v1 고정 1)
- [ ] **대용량 스트리밍:** v2에서 NDJSON 전환 가능성 여부

## Related
- {project-root}/adr/verification-automation.md — 상위 결정

## Tags
`log`, `json`, `schema`, `verification`, `ci`

## Approved
- 2026-08-12: Option A (단일 JSON 파일 + events 배열 + type enum), user confirmed
