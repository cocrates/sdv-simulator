# 결과 리포트 스키마 (Result Report Schema)

## Concern
실행 결과 리포트(라이브러리 `run()` 반환 + CLI 요약)의 **항목과 형식**은 무엇인가? — 버스 부하·드롭·오버런 집계 포함

## Status
approved

## Decision
**Option A — 구조화 리포트 (링크·태스크·assertion·경고)**
User-approved: Report에 simulation/links/tasks/assertions/warnings 포함, CLI 요약은 요약판. 버스 부하 = tx_ms 합 / duration_ms.

## Context
- ASR-002/004/007 후속 — "버스 부하(점유율 %)를 리포트에 포함"(CAN), "리포트에 경고 표시"(앱 런타임), "검증 결과(pass/fail) 출력"(CLI)은 결정됐으나 리포트 항목 미정
- Gate 5 재검토 그룹 B-11 — PRD 성공 기준 2(지연·대역폭 결과 확인)의 "확인" 수단
- can-fidelity-model Downstream open: 버스 부하 리포트 형식, ethernet Downstream open: drop 집계

## Options
### Option A — 구조화 리포트 (링크·태스크·assertion·경고)
- `Report`: `simulation{duration_ms, result: pass|fail, event_count}` + `links[{name, kind, tx_count, rx_count, drop_count, supersede_count?, bus_load_percent}]` + `tasks[{node, task, period_ms, run_count, overrun_count}]` + `assertions[{name, status: pass|fail, detail}]` + `warnings[]`
- CLI 요약 = 이 표의 요약판(링크 부하·오버런·assertion 결과)
- Pro: PRD 성공 기준 2 직접 지원, 구조화(라이브러리 소비 가능), 결정적
- Con: 항목 확정·문서화 부담

### Option B — 최소 리포트
- duration_ms + result + assertion 결과만
- Pro: 최소 구현
- Con: 버스 부하·오버런 "확인" 수단 부재 — 성공 기준 2 미달 위험

### Option C — 로그 통합(리포트 없음)
- 리포트 없이 이벤트 로그에서 사용자가 집계
- Pro: API 단순
- Con: "결과 확인" UX 저하, CLI 요약도 불가

## Tradeoffs
| | A (구조화) | B (최소) | C (로그 통합) |
|---|------|------|------|
| 성공 기준 2 지원 | ★★★★★ | ★★ | ★★ |
| CLI 요약 UX | ★★★★★ | ★★★ | ★ |
| 구현 비용 | 중간 | 낮음 | 낮음 |

## Recommendation (optional)
- **Option A**: PRD 성공 기준 2(대역폭·지연 결과 확인)를 리포트로 직접 충족. 항목은 로그 집계와 1:1이라 구현 비용 낮음.

## Consequences
- 리포트는 이벤트 로그로부터 파생(결정적) — 별도 저장 형식이 아닌 API/CLI 표시 계약
- JSON 로그(schema)와 리포트(구조체)는 별개 산출물

## Related ASRs
- ASR-002 — 시뮬레이션 엔진 모델 — 실행 요약
- ASR-004 — 통신 프로토콜 충실도 — 버스 부하·드롭 집계
- ASR-007 — 검증·자동화 지원 — assertion 요약

## Downstream Concerns
- [ ] **bus_load_percent 계산식:** 점유 시간/실행 시간 비율 정의 (tx_ms 합 / duration_ms)

## Related
- {project-root}/adr/can-fidelity-model.md, ethernet-fidelity-model.md, task-scheduling-policy.md, event-log-schema.md

## Tags
`report`, `summary`, `bus-load`, `cli`

## Approved
- 2026-08-12: Option A (구조화 리포트), user confirmed
