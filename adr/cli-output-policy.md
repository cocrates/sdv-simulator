# CLI 출력·오류 정책 (CLI Output & Error Policy)

## Concern
CLI 출력 언어(i18n)와 오류 분류·종료 코드를 어떻게 정할 것인가?

## Status
approved

## Decision
**Option A — --lang 플래그 + 환경변수 + 로케일 폴백 + 종료 코드 0/1/2/3**
User-approved: --lang ko|en > SDV_SIM_LANG env > 시스템 로케일(외 → ko). 종료 코드 0=pass/1=assertion fail/2=입력 오류/3=내부 오류.

## Context
- PRD 제약: 문서·CLI 출력은 한국어/영어 지원 가능 구조 (1차는 사용자 언어)
- ASR-007: CLI 종료 코드로 CI 판정
- ADR(package-structure)의 Downstream: 공개 API 계약 세부

## Options
### Option A — --lang 플래그 + 환경변수 + 로케일 폴백 + 종료 코드 0/1/2/3
- 언어 결정: `--lang ko|en` > `SDV_SIM_LANG` env > 시스템 로케일(ko/en 외 → ko)
- 종료 코드: 0=pass, 1=assertion fail, 2=입력 오류(스키마/파일), 3=내부 오류
- Pro: 사용자 제어 명확, CI에서 오류 종류 구분 가능, 구현 단순
- Con: 코드 분류 세분화 필요(경미)

### Option B — 언어 고정 (ko) + 종료 코드 0/1
- Pro: 구현 최단
- Con: PRD "한국어/영어 지원 가능 구조" 제약 위반, 오류 구분 불가

### Option C — i18n 카탈로그 프레임워크(gettext 등)
- Pro: 표준 국제화
- Con: v1에 과도, 메시지 카탈로그 관리 부담

## Tradeoffs
| | A (플래그+env+코드 분류) | B (고정 ko) | C (gettext) |
|---|--------------------------|-------------|-------------|
| PRD i18n 제약 충족 | ✓ | ✗ | ✓ |
| CI 오류 구분 | ✓ (0/1/2/3) | ✗ (0/1) | ✓ |
| 구현 비용 | 중간 | 최저 | 높음 |

## Recommendation (optional)
- **Option A** 추천: PRD 제약 충족 + CI 판정 개선을 최소 비용으로 달성

## Consequences
- 이벤트 로그·assertion은 구조화 데이터 — 언어 무관 (CLI 요약 텍스트만 언어 적용)
- 오류 메시지에 파일명·줄 번호·필드 경로 포함

## Related ASRs
- ASR-006 — 코어 API 경계 — CLI 경계 설계에 포함
- ASR-007 — 검증·자동화 지원 — 종료 코드·CI 판정 세부 결정

## Downstream Concerns
- [ ] **CLI 플래그 세트 확정:** --lang/--output 외 필요한 옵션

## Related
- {project-root}/adr/package-structure.md — 상위 결정 (CLI 모듈 경계)

## Tags
`cli`, `i18n`, `exit-code`, `error`

## Approved
- 2026-08-12: Option A (--lang/env/로케일 + 종료 코드 0/1/2/3), user confirmed
