# 로그 쓰기 실패 종료 코드 (Log Write Failure Exit Code)

## Concern
`--log <path>`로 JSON 로그를 파일에 쓸 때 I/O 오류(권한 없음, 디스크 꽉 참 등)가 발생하면 CLI 종료 코드는 무엇이어야 하는가?

## Status
approved

## Context
- 검증(1차)에서 **미문서화 ASR U-3**로 식별 — cli-output-policy는 종료 코드 0/1/2/3을 정했으나 "파일 쓰기 실패"의 분류는 미정이었음
- 스펙 인코딩(2026-08-12) 시 "파일 쓰기 실패는 종료 코드 2(입력 오류)"로 결정되었으나 ADR 검토 없이 직접 인코딩됨
- 구현: `_write_json_log`에서 OSError → `tr('error_write')` + `EXIT_INPUT_ERROR` — 실행 확인 exit 2
- 상위 결정: cli-output-policy (0=pass / 1=assertion fail / 2=입력 오류 / 3=내부 오류), cli-io-contract (--log 채널)

## Decision
**Option A — 종료 코드 2 (입력 오류로 분류)**
User-approved: 로그 파일 쓰기 실패는 "파일" 범주 오류로 분류해 exit 2 — 종료 코드 계약(0/1/2/3) 유지, 오류 메시지(카테고리 ko/en + OS 상세 원문)가 원인 전달.

## Options
### Option A — 종료 코드 2 (입력 오류로 분류) (현재 스펙/구현)
- 로그 파일 쓰기 실패 = 입력 오류(파일 관련)로 분류 → exit 2
- Pro: "파일" 범주의 오류를 하나로 묶어 단순, CI에서 파일 문제와 assertion 실패(1)를 구분 가능
- Con: 의미상 쓰기 실패는 "입력"이 아니라 출력 I/O 오류 — 3(내부 오류)과의 경계가 모호

### Option B — 종료 코드 3 (내부 오류로 분류)
- 쓰기 실패를 내부/환경 오류로 분류 → exit 3
- Pro: "입력 오류"는 정의 파일 문제만을 가리키게 되어 의미 명확
- Con: 사용자 환경 문제(권한·디스크)를 "내부 오류"로 오인할 수 있음 — 3의 정의("시뮬레이터 내부 오류")와도 정확히 일치하지 않음

### Option C — 별도 종료 코드 4 (I/O 오류)
- 파일 쓰기 실패 전용 코드 4 추가
- Pro: 입력 오류(2)·내부 오류(3)·I/O 오류(4) 삼분화 — CI에서 원인 구분 최대
- Con: 기존 종료 코드 계약(0/1/2/3) 변경 필요, cli-output-policy와 스펙 수정 부담

## Tradeoffs
| | A (2, 입력 오류) | B (3, 내부 오류) | C (4, I/O 오류) |
|---|------|------|------|
| 의미 명확성 | ★★ | ★★★ | ★★★★★ |
| CI 원인 구분 | ★★★ (파일 문제) | ★★ | ★★★★★ |
| 기존 계약 유지 | ✓ | ✓ | ✗ (코드 추가) |
| 구현 비용 | 최저 | 최저 | 낮음 |

## Recommendation (optional)
- **Option A**: v1에서 "파일 관련 오류 = 2"라는 단순한 분류를 유지하고, 오류 메시지(카테고리 ko/en + OS 상세 원문)가 실제 원인을 전달하도록 한다. 별도 코드 4는 v2+에서 CI 요구가 생기면 도입 가능.

## Consequences
- 로그 파일 쓰기 실패는 exit 2 — 오류 메시지에는 `error_write` 카테고리 + OS 상세(원문) 포함
- 종료 코드 계약(0/1/2/3)은 변경 없음

## Related ASRs
- ASR-010 — 로그 쓰기 실패 종료 코드 — 본 ADR이 직접 해소
- ASR-006 — 코어 API 경계 & CLI — CLI 경계
- ASR-007 — 검증·자동화 지원 — CI 판정·종료 코드

## Downstream Concerns
- [ ] **오류 메시지 상세 수준:** 로그 쓰기 실패 시 파일 경로를 메시지에 포함할지 — 현재 코드는 OS 상세만 포함

## Related
- {project-root}/adr/cli-output-policy.md — 상위 결정 (종료 코드 0/1/2/3)
- {project-root}/adr/cli-io-contract.md — 상위 결정 (--log 채널)

## Tags
`cli`, `exit-code`, `error`, `log`, `io`

## Approved
- 2026-08-12: Option A (종료 코드 2, 입력 오류로 분류), user confirmed
