# 시뮬레이션 시간 모델 (Simulation Time Model)

## Concern
시뮬레이션 시간을 어떤 단위/정밀도로 표현·진행하고, 종료 조건과 난수 정책은 무엇으로 할 것인가?

## Status
approved

## Decision
**Option A — 정수 ms + (t_ms, seq) + duration_ms 종료 + 난수 없음**
User-approved: 결정성 최우선 — 모든 시간을 정수 ms로 표현, (t_ms, seq)로 완전 순서 보장, duration_ms 도달 시 종료, v1 난수 미사용.

## Context
- ASR-002(DES 엔진) 후속 — 시간 표현은 결정성(determinism)의 기반
- v1 검증 대상(L2 통신)은 ms 단위 충실도로 충분
- ADR(simulation-engine-model)의 Downstream: 시간 해상도/단위, 결정성 보장 수단

## Options
### Option A — 정수 ms + (t_ms, seq) + duration_ms 종료 + 난수 없음
- 모든 시간 값(주기·지연·타임아웃·타임스탬프)을 정수 ms로 표현. 이벤트는 (t_ms, seq) 쌍으로 완전 순서 보장
- 시나리오 `duration_ms` 도달 시 종료. v1은 난수 미사용 (seed 필드는 스키마에만 유지)
- Pro: 결정성 최대, 구현·디버깅 단순, 로그가 정수라 비교 용이
- Con: ms 미만 정밀도 표현 불가 (v1 L2 충실도에는 충분)

### Option B — float ms (us/ns 정밀도)
- 시간을 float로 표현해 서브-ms 정밀도 허용
- Pro: 실행 시간·지연 세부 표현 가능
- Con: 부동소수점 비교의 결정성 리스크, 로그 가독성 저하, fast-forward 로직 복잡

### Option C — 설정 가능 단위 (ms/us)
- 전역 `time_unit` 설정으로 정수 ms 또는 정수 us 선택
- Pro: 사용자 필요에 따라 정밀도 조정
- Con: 스키마·엔진·로그가 단위 의존 → 복잡도 증가, 결정성 확인 부담

## Tradeoffs
| | A (정수 ms) | B (float) | C (설정 단위) |
|---|-------------|-----------|---------------|
| 결정성 | ★★★★★ | ★★★ | ★★★★ |
| 구현 단순성 | ★★★★★ | ★★★ | ★★ |
| 충실도 | ★★★ (v1 충분) | ★★★★★ | ★★★★★ |
| 로그 가독성 | ★★★★★ | ★★★ | ★★★★ |

## Recommendation (optional)
- **Option A** 추천: v1의 검증 대상(L2 통신·라우팅)은 정수 ms로 충분하고 결정성이 최우선. 실행 시간 모델은 wcet를 ms 정수로 표현(기본 0)

## Consequences
- 주기 프레임/태스크는 t=0에서 첫 발생 후 매 period (정수 ms)
- 전파 지연은 0 — 지연은 큐잉/버스 점유로만 발생
- 동시 이벤트는 seq로 순서 결정 (정의/생성 순서)

## Related ASRs
- ASR-002 — 시뮬레이션 엔진 모델 — 시간 표현·진행 세부 결정

## Downstream Concerns
- [ ] **종료 후 평가:** duration_ms 도달 후 assertion 평가 순서 확정
- [ ] **태스크 실행 시간 정합:** wcet_ms 정수 표현 (task-scheduling-policy와 연계)

## Related
- {project-root}/adr/simulation-engine-model.md — 상위 결정 (DES + 주기 태스크 하이브리드)

## Tags
`simulation`, `time-model`, `determinism`

## Approved
- 2026-08-12: Option A (정수 ms + (t_ms, seq) + duration_ms 종료 + 난수 없음), user confirmed
