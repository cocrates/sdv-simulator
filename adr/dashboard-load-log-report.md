# 로그 리플레이 리포트 파생 (load-log-report)

## Concern
`POST /api/load-log`로 로드한 v1 이벤트 로그에서 `GET /api/report`는 무엇을 반환하는가? — v1 로그에는 링크/태스크 통계가 없어 Report의 일부 항목을 이벤트만으로 파생할 수 없다.

## Status
approved

## Context
- v1 Report는 **정의(arch YAML) + 이벤트**에서 파생 (v1 D-21). v1 로그 JSON에는 `simulation{duration_ms, result}` + `events[]` + `assertions[]`만 포함 — 링크/태스크 통계 없음.
- 이벤트에서 파생 가능: links(tx/rx/drop_count), tasks(run/overrun_count), simulation, assertions. **파생 불가**: `bus_load_percent`(tx_ms에 DLC·bitrate 필요), `supersede_count`(D-18: 교체 이벤트 미기록), `tasks[].period_ms`.
- run 경로는 `SimulationResult.report`로 전체 표시 가능. load-log 경로만 문제 (spec review M-1).
- 타임라인 duration 소스: run = scenario.duration_ms, load-log = 로그 `simulation.duration_ms` (m-5 동시 해소).

## Options
### Option A — 파생 가능 항목만 표시 + arch 연동 시 전체 (권장)
- load-log 리포트 = 이벤트에서 파생 가능한 항목만 표시. 파생 불가 항목은 미표시(또는 "—") + "아키텍처 정의 로드 시 전체 리포트" 안내.
- 사용자가 대응 아키텍처 YAML을 열면(또는 세션에 arch 스냅샷이 있으면) 전체 Report 계산.
- Pro: 허위 통계 없음 (신뢰성) / 구현 단순 / v1 의미론 정합 ("리포트는 정의+이벤트에서 파생")
- Con: 로그 단독 리플레이에서 일부 지표 누락

### Option B — 로그 포맷 확장 (report 포함, schema v2)
- v2가 생성한 로그에 report 필드를 추가해 전체 표시.
- Pro: v2 생성 로그는 전체 리포트
- Con: v1 로그(schema_version 1)와 호환 문제·스키마 분기 / "v1 로그 스키마 그대로 전달"(ASR-015)과 충돌 / 대시보드는 로그를 쓰지 않으므로 실익 제한 (run 경로는 메모리 결과 직접 사용)

### Option C — load-log에서 리포트 탭 제한
- 로그 재생 시 리포트 탭 비활성, assertion 결과만 표시.
- Pro: 명확·최소 구현
- Con: PRD 성공 기준 4(리포트 확인)를 로그 겸용 경로에서 충족하지 못함 — PRD가 "기존 JSON 이벤트 로그 파일 로드도 겸용"을 명시한 점과 어긋남

## Tradeoffs
| 차원 | A (파생 가능만) | B (로그 확장) | C (제한) |
|------|-----------------|---------------|----------|
| 표시 충실도 | ★★ (일부 누락 명시) | ★★★ | ★ |
| 허위/과잉 표시 | ★★★ (없음) | ★★★ | ★★★ |
| 구현 비용 | ★★ | ★★★ (스키마·호환) | ★ |
| v1 로그 호환 | ★★★ | ★★ | ★★★ |

## Recommendation
- **Option A** 권장. 로그 단독 경로에서는 사실만 표시하고, 정의가 있을 때 전체 리포트를 제공 — "리포트는 정의+이벤트에서 파생"이라는 v1 의미론과 정합. 로그 검증 규칙(스키마 버전·type enum·정렬)도 함께 명시.

## Consequences
- load-log 리포트 = 이벤트에서 파생 가능한 항목만 표시: `simulation{duration_ms, result}`, `links[](tx_count/rx_count/drop_count)`, `tasks[](run_count/overrun_count)`, `assertions[]`
- 파생 불가 항목(`bus_load_percent`, `supersede_count`, `tasks[].period_ms`)은 미표시(또는 "—") + "아키텍처 정의 로드 시 전체 리포트" 안내
- 세션에 아키텍처 스냅샷이 있으면(arch 연동) 전체 Report 계산 — v1 의미론("리포트는 정의+이벤트에서 파생") 정합
- 타임라인 duration 소스: run = scenario.duration_ms, load-log = 로그 `simulation.duration_ms` (m-5 동시 해소)
- 로그 검증 규칙 명시: schema_version 1, type enum 7종, (t_ms, seq) 오름차순 정렬 검증

## Related ASRs
- ASR-015 — 데이터 흐름·리플레이 — 파일 로드 겸용·세션 상태의 대상
- ASR-007 — 검증·자동화 — Report·assertion 구조의 원천 (컨텍스트)

## Downstream Concerns
- [ ] **"아키텍처 로드 시 전체 리포트"의 조건**: 대응 arch를 어떻게 식별하는가 (세션 스냅샷 유무 기준) — spec 인코딩
- [ ] **로그 검증 규칙**: schema_version·type enum·(t_ms, seq) 정렬 검증 — spec 인코딩
- [ ] **duration 소스 명시**: load-log = 로그 `simulation.duration_ms` (m-5 해소)

## Related
- `adr/dashboard-run-path.md` — 실행 경로 ADR (서버 검증 유틸 연계)
- `spec/sdv-sim-v2.md` — API(load-log/report)·리포트 표시 절 수정 대상

## Tags
`load-log`, `report`, `replay`, `dashboard`, `events`

## Approved
- 2026-08-12: Option A (파생 가능 항목만 표시 + arch 연동 시 전체), user confirmed ("오케이") — ADR 5건 일괄 승인
