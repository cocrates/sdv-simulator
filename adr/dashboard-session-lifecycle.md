# 대시보드 세션 수명주기 (session-lifecycle)

## Concern
대시보드의 "세션"(`GET /api/events`·`GET /api/report`가 참조하는 상태)을 무엇으로 정의하고, 편집·재실행·파일 전환·다중 탭에서 언제 유지·무효화하는가?

## Status
approved

## Context
- v2 spec API가 "현재 세션"을 참조하나 정의 없음: `POST /api/run` "결과 + 세션 설정", `POST /api/load-log` "세션 설정", `GET /api/events`·`GET /api/report` "현재 세션" (spec review M-4).
- 구조 뷰는 "현재 YAML"과 "리플레이 오버레이" 두 정보를 동시에 표시 — 정의가 바뀌면 오버레이와 불일치할 수 있음.
- 단일 사용자·단일 머신·메모리 전용(영속화 없음). 실행은 동기·수 초 내 완료.

## Options
### Option A — 스냅샷 세션 + 편집 시 무효화 (권장)
- 세션 = `{events, report, duration_ms, source: run|log, 아키텍처/시나리오 스냅샷}`. run/load-log가 세션을 교체.
- 열린 YAML의 편집이 시작되면(첫 변경) 세션 무효화 → 오버레이 해제 + "정의 변경으로 리플레이 무효" 표시. 파일 열기/새로 만들기 시 세션 리셋.
- 다중 탭: 단일 사용자 — 세션은 서버 전역 1개, last-write-wins 명시.
- Pro: 리플레이-정의 불일치 원천 차단 (검증 도구의 신뢰성) / 상태 모델 단순·명확
- Con: 편집 후 재실행 전까지 리플레이 재생 불가 (약간의 UX 제약)

### Option B — 세션 독립 유지
- 편집과 무관하게 세션 유지. 명시적 "결과 해제" 컨트롤만 제공.
- Pro: 편집 중에도 리플레이 참조 가능
- Con: 오버레이가 다른 정의의 데이터일 수 있음 — 오인 위험 / 상태 복잡

### Option C — 유지 + 불일치 표시 (하이브리드)
- B와 같되, 편집으로 YAML이 세션 스냅샷과 달라지면 "불일치" 배지 표시.
- Pro: 유연 + 오인 방지
- Con: 불일치 판정 로직(내용 비교) 추가, 상태 모델 복잡

## Tradeoffs
| 차원 | A (무효화) | B (독립) | C (유지+표시) |
|------|-----------|----------|---------------|
| 오인(불일치 재생) 방지 | ★★★ | ★ | ★★ |
| 편집 중 리플레이 참조 | ★ (불가) | ★★★ | ★★★ |
| 상태 모델 단순성 | ★★★ | ★★ | ★ |
| 구현 비용 | ★★★ | ★★ | ★ |

## Recommendation
- **Option A** 권장. 시뮬레이터의 핵심 가치는 "보이는 것이 실제 실행 결과"라는 신뢰성 — 리플레이-정의 불일치를 구조적으로 차단하는 것이 우선. 다중 탭은 last-write-wins로 명시(단일 사용자 수용).

## Consequences
- 세션 = `{events, report, duration_ms, source: run|log, 아키텍처/시나리오 스냅샷}` — run/load-log가 세션을 교체
- 열린 YAML 편집 시작(첫 변경) 시 세션 무효화 → 오버레이 해제 + "정의 변경으로 리플레이 무효" 표시
- 파일 열기/새로 만들기 시 세션 리셋
- 재실행/재로드 시 세션 교체 (명시)
- 다중 탭: 서버 전역 세션 1개, last-write-wins 명시

## Related ASRs
- ASR-015 — 데이터 흐름·리플레이 — 세션 상태 모델의 대상

## Downstream Concerns
- [ ] **무효화 시점 세부**: "첫 변경" 기준 vs 검증 통과 편집만 — UX 판단 (첫 keystroke가 단순·명확)
- [ ] **불일치 표시 문구**: ko/en 카탈로그 항목 (i18n, ASR-020 연계)
- [ ] **파일 열기/새로 만들기 시 세션 리셋** 확인 — spec 인코딩

## Related
- `spec/sdv-sim-v2.md` — API(세션)·편집·파일 관리 절 수정 대상

## Tags
`session`, `lifecycle`, `replay`, `dashboard`, `state`

## Approved
- 2026-08-12: Option A (스냅샷 세션 + 편집 시 무효화, last-write-wins), user confirmed ("오케이") — ADR 5건 일괄 승인
