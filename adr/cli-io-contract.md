# CLI 입출력 계약 (CLI I/O Contract)

## Concern
CLI의 출력 채널(JSON 로그 위치, 사람용 요약), 플래그 세트, 오류 메시지 i18n 범위는 무엇인가?

## Status
approved

## Decision
**Option A — 로그는 파일(--log), 요약은 stdout**
User-approved: --log 기본 events.json, --log -는 stdout, --quiet 지원, 오류 메시지도 CLI 언어 적용.

## Context
- ASR-006/007 후속 — --lang/종료 코드 0/1/2/3은 결정됐으나 출력 채널·플래그 미정
- Gate 5 재검토 그룹 A-5: CI 재사용(성공 기준)에 직결 — "이벤트 로그를 출력한다"의 정확한 의미 미정
- cli-output-policy Downstream open: 플래그 세트(--lang/--output 외), 이벤트 로그·assertion은 구조화 데이터(언어 무관)

## Options
### Option A — 로그는 파일(--log), 요약은 stdout
- `sdv-sim run <arch> <scenario> [--log <path>] [--quiet] [--lang ko|en]`
- JSON 로그: `--log <path>`(기본 `events.json`), `--log -`는 stdout
- 사람용 요약(결과·통계·assertion)은 stdout — `--quiet` 시 요약 생략(종료 코드로만 판정)
- 오류 메시지도 CLI 언어(--lang) 적용
- Pro: CI에서 로그 파일 아티팩트 분리, 요약/로그 섞임 없음, 기본값 안전
- Con: 기본 파일 생성(작업 디렉터리 오염) — `--log -`/`--quiet`로 회피 가능

### Option B — 로그는 stdout(--json 플래그)
- `--json` 시 JSON만 stdout 출력, 그 외 요약
- Pro: 파이프 친화
- Con: 요약+JSON 동시 확인 불가, CI 파이프 처리 부담

### Option C — 로그 파일 필수(--log 없으면 오류)
- Pro: 명시성
- Con: 기본 실행 UX 저하(성공 기준 4 헤드리스 단순성)

## Tradeoffs
| | A (--log+요약 stdout) | B (--json stdout) | C (--log 필수) |
|---|------|------|------|
| CI 아티팩트 | ★★★★★ | ★★★ | ★★★★★ |
| 사람 UX | ★★★★★ | ★★ | ★★ |
| 파이프 친화성 | ★★★ | ★★★★★ | ★★★ |

## Recommendation (optional)
- **Option A**: "요약 stdout + 로그 파일"이 CI·사람 UX를 동시에 만족. `--log -`로 파이프도 지원.

## Consequences
- JSON 로그 파일명 기본값 `events.json` — 문서화 필요
- 종료 코드 0/1/2/3은 기존 결정 유지 — 오류 메시지의 언어만 i18n 적용

## Related ASRs
- ASR-006 — 코어 API 경계 — CLI 경계
- ASR-007 — 검증·자동화 지원 — CI 판정·로그 산출물

## Downstream Concerns
- [ ] **요약 포맷 상세:** 통계 표(링크·태스크·assertion) 항목 — D-21(result-report-schema)과 정합

## Related
- {project-root}/adr/cli-output-policy.md — 상위 결정 (--lang, 종료 코드)
- {project-root}/adr/event-log-schema.md — 로그 구조

## Tags
`cli`, `output`, `json`, `log`, `ci`

## Approved
- 2026-08-12: Option A (--log 파일 + 요약 stdout), user confirmed
