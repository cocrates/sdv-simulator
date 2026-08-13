# Verification: SDV Simulator v2 — 웹 대시보드 (sdv-sim serve)

**Spec:** `/home/ubuntu/workspace/softwares/sdv-simulator/spec/sdv-sim-v2.md` (Aligned with `/home/ubuntu/workspace/softwares/sdv-simulator/spec/PRD.md`)
**Artifact(s):**
- 서버: `sdv_sim/server/{app,session,log_loader}.py`, `sdv_sim/cli/{main,serve}.py`
- v1 코어 확장: `sdv_sim/core/engine.py` (`loads`/`load_scenario_yaml`), `sdv_sim/__init__.py`
- 프런트엔드: `frontend/src/` (App, EditorPane, StructureView, layout, useValidation, fileManager, api, i18n, replay/, ReportView/ReportPanel, EventPanel, router, yaml, types)
- 정적 자산: `sdv_sim/server/static/` (T-020 wheel 포함 확인)
- 테스트: `tests/test_server.py`(23건) 외 111 passed / mypy strict 18 files clean / `frontend/scripts/check-*.ts` 3종 통과
**Verified:** 2026-08-13
**Summary:** 43 pass, 0 fail, 1 partial, 3 not-verifiable

---

## Inventory & Results

### A. PRD 수준 (성공 기준 6)

| # | Spec 항목 | Status | Evidence / Notes |
|---|-----------|--------|------------------|
| A1 | [PRD-1] 브라우저에서 구조 다이어그램 확인 + 정의 편집·저장·실행 | pass | `frontend/src/App.tsx` — EditorPane(2탭) + StructureView(구조 뷰) + 저장/실행 툴바. 통합 serve 스모크: run → event_count 64 |
| A2 | [PRD-2] 실행 결과가 구조 뷰 위에서 리플레이 | pass | `ReplayView.tsx` + `ReplayOverlay.tsx` — 동일 SVG 좌표계 `<g>` 오버레이. run → #/replay 흐름 |
| A3 | [PRD-3] 필터·상세 조회·재실행 인터랙션 | pass | `ReplayView.tsx` 타입 필터 6종 + 엔티티 필터(구조 클릭), `EventPanel.tsx` 상세 패널(시크 연동), 툴바 재실행 |
| A4 | [PRD-4] assertion 결과와 drop/overrun/버스 부하 리포트 | pass | `ReportView/ReportPanel.tsx` — run 전체 Report(links bus_load 포함), load-log 파생 모드("—"). 통합: run 리포트 확인 |
| A5 | [PRD-5] v1 공개 API 계약 유지 (`loads()` 추가만) | pass | `engine.py` L852-883 — `load()` 시그니처·동작 유지 + `loads()` 추가. pytest v1 회귀 전체 통과 |
| A6 | [PRD-6] 스키마 검증 피드백 + 브라우저 로컬 파일 저장 | pass | `useValidation.ts`(500ms 디바운스 + forceValidate), `fileManager.ts`(FS Access API + 폴백). EditorPane 줄 마커 |

### B. 서버 (serve)

| # | Spec 항목 | Status | Evidence / Notes |
|---|-----------|--------|------------------|
| B1 | `sdv-sim serve` 존재, 기본 포트 8888 | pass | `cli/main.py` L177-187 (`--port` default 8888), serve 스모크 8888/8899 실행 확인 |
| B2 | `--port`/`--lang`/`--dev` 동작, `--root` 없음 | pass | `main.py` L181-186. `--root` 옵션·코드 부재 확인. serve 통합: `--lang en` → index.html `"en"` 주입 |
| B3 | 정적 자산 패키지 내부 서빙 | pass | `app.py` L304-318 `StaticFiles(directory=_STATIC_DIR)`. T-020 wheel 검증: static 3건 1회 포함, fail-fast(누락 시 FileNotFoundError) |
| B4 | 포트 점유 시 명확한 오류 + exit 2 | pass | `serve.py` L55-58 `_bind` → `EXIT_PORT_BUSY=2`. `tests/test_cli.py` serve 포트 점유 → exit 2 |
| B5 | 시작 시 접속 URL 출력 | pass | `serve.py` L60, L88-92 `serve_started`/`serve_dev_hint`. 서버 실행 로그 확인 |
| B6 | v1 코어 문자열 입력 API만 추가, 하위 호환 | pass | `engine.py` L863-895 — `loads()`/`_tagged_scenario_error`. 기존 경로 기반 API 변경 없음 (pytest v1 스위트 회귀 없음) |

### C. 파일 관리 (브라우저)

| # | Spec 항목 | Status | Evidence / Notes |
|---|-----------|--------|------------------|
| C1 | Chrome/Edge FS Access API — 같은 파일 열기/저장 | pass | `fileManager.ts` L156-166(`showOpenFilePicker`), L276-303(handle createWritable 같은 파일 저장) |
| C2 | Firefox/Safari 폴백 — 업로드 + Blob 다운로드 | pass | `fileManager.ts` L171-206(`<input type=file>`), L305-316(`downloadBlob`) |
| C3 | 서버 파일 API(`/api/files*`)·`--root` 샌드박스 없음 | pass | `app.py` — 파일 API 없음, `--root` 옵션 없음. 코드·테스트 부재 확인 |
| C4 | 파일 삭제·이름 변경 미지원 | pass | `fileManager.ts`에 삭제/rename 기능 부재 (최근 파일 항목 제거만 존재 — 목록 관리, 파일시스템 아님) |
| C5 | 최근 파일 목록(IndexedDB) | pass | `fileManager.ts` L318-379 — `sdv-sim` DB, `recent-files` store, MAX_RECENT=20. `check:files` 23 checks passed |

### D. 편집·검증

| # | Spec 항목 | Status | Evidence / Notes |
|---|-----------|--------|------------------|
| D1 | YAML 텍스트 편집 → 유효 시 다이어그램 실시간 반영, 오류 시 마지막 유효 상태 유지 | pass | `App.tsx` L117-125 (`archValidation.status === "valid"`일 때만 structureArch 갱신) |
| D2 | 검증 오류 줄 단위 인라인 표시 | pass | `EditorPane.tsx` L256-284 — gutter 줄 마커 + 오류 목록 클릭 시 해당 줄 이동 |
| D3 | 저장·실행 시 강제 검증, 실패 시 거부 | pass | `App.tsx` handleSave/handleRun → `forceValidate()`; `useValidation.ts` L80-86. 실패 시 `editor.saveBlocked`/`runBlocked` flash |
| D4 | v1 Pydantic 스키마 재사용 (프런트 포팅 없음) | pass | `app.py` L120-121, L169 — `_parse_yaml_text(content, Architecture/Scenario)`가 v1 스키마 사용. `useValidation.ts`는 서버 검증만 호출 |
| D5 | 시나리오 단독 = 구조 검증만, arch 페어링 시 참조 검증 (F-4) | pass | `app.py` L164-169 — `arch` 유무 분기. `App.tsx` L94-99 — `archValidation.status === "valid"`일 때만 `validArchContent` 전달 |

### E. 구조 뷰·리플레이

| # | Spec 항목 | Status | Evidence / Notes |
|---|-----------|--------|------------------|
| E1 | 아키텍처 노드/링크/게이트웨이/프레임 자동 렌더링 | pass | `StructureView.tsx`(SVG 노드/링크/프레임 라벨) + `layout.ts`(기하). 샘플 YAML 데모 확인 |
| E2 | 타입 밴드 레이아웃 — HPC 상단/게이트웨이 중앙/ECU 하단, 밴드 내 링크 수↓→이름↑ (F-6) | pass | `layout.ts` L99-147, L127-132(`sortBand`). `check:layout` 9 checks passed |
| E3 | 결정적 레이아웃 — 동일 YAML → 동일 좌표 (M-5) | pass | `layout.ts` — 순수 함수, 비결정 요소 없음(byName 코드 유닛 순). `check:layout` 결정성 검증 |
| E4 | CAN/Ethernet 시각 구분 (색·굵기·대시) | pass | `StructureView.tsx` L60-63 — `.link-can`(실선 두꺼움)/`.link-eth`(대시). `check:layout` kind 시각 전용 검증 |
| E5 | 링크 프레임 애니메이션 — run: tx_ms 물리 재생, load-log: 고정 펄스 + "근사 표시" (M-2/F-5) | pass | `replayIndex.ts` `computeTxMs`(v1 공식 복제, L62-65), `ReplayOverlay.tsx` pulse 모드 근사 라벨 L211-216 |
| E6 | 노드 상태 하이라이트 (task_start/end 실행, overrun) | pass | `ReplayOverlay.tsx` L159-171 — running 테두리 + overrun SIGNAL_MS 500ms 플래시 |
| E7 | 링크/스위치 drop 하이라이트 — 큐 근사, 깊이 수치 추정 없음 | pass | `ReplayOverlay.tsx` L175-180 drop 신호만; `replayIndex.ts` L17-18 주석 "no depth figures" |
| E8 | 게이트웨이 라우팅(소스 전송 완료 → 대상 tx)·스위치 드롭 표시 | pass | `ReplayOverlay.tsx` L61-82 `travelEndpoints`(게이트웨이 엔드포인트 우선), drop 표시 L229-239. v1 의미론(홉 ≤ 8) |
| E9 | 재생/일시정지/탐색 컨트롤 + 타임라인 + 배속(0.5/1/2/4x) | pass | `ReplayView.tsx` L227-258, `useReplayClock.ts`(rAF 클록) |
| E10 | load-log 시크 상태 — 고정 펄스 근사 또는 in-flight 미표시 (F-5) | pass | pulse 모드 `PULSE_MS=300` 고정 + "근사" 라벨 선택 |
| E11 | 이벤트 상세 패널, 구조 뷰와 클릭 연동 | pass | `EventPanel.tsx`(클릭 시크) + `ReplayView.tsx` 구조 노드/링크 클릭 → 엔티티 필터 |
| E12 | 이벤트 타입·엔티티 필터 (task = start+end 그룹) | pass | `ReplayView.tsx` L50-52 `typeGroup`, 필터 6종 체크박스 + 엔티티 필터 |
| E13 | 리포트 — run 전체 / load-log 파생 항목만 (M-1) | pass | `ReportPanel.tsx` `derived` prop → 비파생 셀 "—". 통합: no-arch → links 4키, arch → 6키(bus_load/kind 포함) |
| E14 | 브라우저 v1 로그 JSON 로드 리플레이 (`arch_content` 포함 시 전체 Report) (F-2) | pass | `ReplayView.tsx` handleLoadLog → `apiLoadLog(content, name, archContent)`. 통합: no-arch vs with-arch Report 차이 확인 |
| E15 | 편집 시작(첫 변경) 시 세션 무효화 — 오버레이 해제 + 안내 (M-4) | partial | 세션 무효화 + "invalid" 안내 표시는 확인(`ReplayView.tsx` L215-217). 무효화 신호 = **`/api/validate` 호출**(디바운스 500ms 후 서버 도달 시점) — 스펙의 "첫 변경 시"와 시점 차이(500ms). **2026-08-13 사용자 수용 → U-1로 스펙 인코딩 완료 (현재는 스펙 계약과 일치)** |
| E16 | 무효화/부재 세션 events/report → 409 + `session_invalid` (F-7) | pass | `app.py` L252-261. 통합: 편집 후 GET /api/events·report → 409 `session_invalid` |
| E17 | 세션 교체 — run/load-log → replace, 파일 열기/새로 만들기 → reset (M-4) | pass | `app.py` L194-203/L231-239(`sessions.replace`), `App.tsx` handleNewFile/handleOpenFile(`setSessionMeta(null)`) |
| E18 | 세션 데이터 — run `{events, report, arch/scenario 스냅샷}`, load-log arch_content | pass | `session.py` Session dataclass(L22-32). run: arch_content+scenario_content 저장, log: arch_content 저장 |

### F. 성능

| # | Spec 항목 | Status | Evidence / Notes |
|---|-----------|--------|------------------|
| F1 | 노드 ≤ 200 / 링크 ≤ 500 — 60fps 인터랙션 | not-verifiable | SVG + React 구조(렌더링 경로 단순), 이벤트 패널 고정 행고 22px 가상화(`EventPanel.tsx`). **실측 벤치마크(브라우저 DevTools)는 수동 확인 필요** — 성능 기준 측정 방법이 스펙에 명시되지 않음 (spec-review F-10 경미 항목으로 기록됨) |
| F2 | ≤ 100만 이벤트 로드·정렬 ≤ 2s | not-verifiable | `buildReplayIndex` O(n) 정렬 검증 + 스냅샷 K=2000. `check:replay`는 10만 이벤트 블록 경계로 구조 검증. **100만 실측은 수동 필요** |
| F3 | 시크 후 상태 반영 ≤ 100ms — O(K) 상한 (M-3) | pass | `replayIndex.ts` L253-266 `seekToTime` — 스냅샷 + 잔여 ≤ K 재적용, 비용 O(K) 구조. `check:replay` — 시크 24개 타겟 = 전역 재스캔 동등 + O(K) 구조 상한 검증. advance==seek 불변식 확인 |

### G. 언어

| # | Spec 항목 | Status | Evidence / Notes |
|---|-----------|--------|------------------|
| G1 | UI 문자열 ko/en 카탈로그 (하드코딩 없음) | pass | `i18n/messages.ts` — ko/en **각 90키 완전 동일 세트**(parity 스크립트 확인). `index.tsx` `t()` |
| G2 | 언어 우선순위: `--lang` > `SDV_SIM_LANG` > 브라우저 로케일 > ko | pass | 서버: `_inject_lang`(app.py L124-137) + `_resolve_lang`(cli/main.py L45-62). 프런트: `resolveInitialLang`(messages.ts L301) — localStorage 선택 > `window.__SDV_SIM_LANG__` > 로케일 > ko. T-020 serve 통합 확인(ko/en/env) |

### H. Out of Scope (비목표 침범 검사)

| # | Spec 항목 | Status | Evidence / Notes |
|---|-----------|--------|------------------|
| H1 | OTA — 미포함 | pass | 구현 부재 |
| H2 | 구조화 폼/드래그 앤 드롭 편집 — 미포함 | pass | YAML 텍스트 편집기만 |
| H3 | 서버 측 파일시스템 접근·파일 API·`--root` — 없음 | pass | `app.py`/`serve.py` 확인 — 파일시스템 접근 없음 |
| H4 | SSE/WebSocket 스트리밍 — 비목표 | pass | REST 일괄 JSON만 |
| H5 | Canvas 렌더링 — 미사용 (SVG) | pass | `StructureView.tsx` — SVG 전용 |
| H6 | 컴포넌트 Python 등록 UI — 미포함 (스텁 실행) | pass | v1 스텁 동작 유지, 등록 UI 부재 |
| H7 | 이벤트 축약 포맷 — 미사용 | pass | v1 로그 스키마 전체 이벤트 전달(`_event_to_dict` 전체 필드) |
| H8 | 데스크톱 앱 — 미포함 | pass | 구현 부재 |
| H9 | 실시간 실행 진행률 UI — 비목표 (동기 실행) | pass | `POST /api/run` 동기 처리 |

---

## Deviations (Non-compliance)

**1건 partial (E15) — minor:**

| Spec item | 실제 동작 | Severity |
|-----------|-----------|----------|
| E15: "편집 시작(첫 변경) 시 세션 무효화" | 무효화 신호 = `/api/validate` 호출 (디바운스 500ms 후 서버 도달 시점). 스펙의 "첫 변경 시"보다 500ms 늦게 무효화됨. 프런트는 편집 직후 세션Meta를 유지하므로 그 사이 이벤트 조회는 여전히 유효한 세션을 반환 | Minor (의도·결과는 스펙과 정합 — T-014에서 이미 구현 결정으로 기록, 테스트 23건이 무효화 동작 검증) |

fail 0건. Out of Scope 침범 0건.

---

## Undocumented ASRs (Specification Gaps)

ASR gap scan protocol (의미 있는 구조 결정만 기록):

| # | 결정된 사항 | 위치 | ASR 카테고리 | 스펙 갭 | Risk | 권장 조치 |
|---|------------|------|--------------|---------|------|-----------|
| U-1 | **세션 무효화 신호를 `/api/validate` 호출로 매핑** — API 5종에 전용 무효화 엔드포인트가 없으므로, 편집 파이프라인에서 서버에 도달하는 유일한 신호(validate)가 M-4의 "편집 시작"을 대신한다 | `app.py` L160-162 (주석), T-014 노트 | Scope boundary / Integration | 스펙 M-4는 "첫 변경 시"만 규정, API 계약에 무효화 신호가 명시되지 않음 | 무효화 시점 500ms 지연. 프런트가 validate를 생략하면(빈 파일 등) 무효화 누락 가능 | **✅ 해소 (2026-08-13, 사용자 수용)** — `spec/sdv-sim-v2.md` M-4 절·`POST /api/validate` 절·Requirements 절에 "무효화 신호 = validate 호출" 인코딩 완료. ASR-015 Notes 기록 |
| U-2 | **이벤트 패널 고정 행고 22px + 가상화** — 100만 이벤트 목록을 DOM에 직접 렌더링하지 않는 구조 선택 | `EventPanel.tsx` (T-019) | Quality bar / 성능 | 스펙 성능 절에 이벤트 패널 처리 정책 없음 (spec-review F-10에서 "경미"로 기록) | 대용량 로그에서 UI 프리즈 위험 방지 (실측 미검증) | 선택 사항 — 스펙 성능 절에 1줄 명시하거나 F-1 수동 벤치마크와 함께 확인 |
| U-3 | **프런트엔드 방어적 YAML 파서(`yaml.ts`) 별도 존재** — 렌더링용 경량 파서. 서버는 여전히 검증 권위자 (ASR-018) | `frontend/src/yaml.ts` (T-017) | Integration / Structure | 스펙에 "렌더링용 파서" 언급 없음 — "서버 검증 권위"만 규정 | 프런트 파서와 서버 검증 결과가 다른 입력에서 어긋날 수 있음 (렌더링만 담당하므로 영향 제한적) | ASR-018 하위 구현 결정으로 문서화 완료(T-017 노트) — 스펙 반영은 선택 사항 |

참고 — 미문서화 ASR 아님 (이미 결정·인코딩 확인):
- K=2000 스냅샷, PULSE_MS=300, SIGNAL_MS=500, ARC_RISE — 스펙이 "생성 시 결정"으로 위임 (M-3/M-2, L33/L46)
- `arch_content` 단일 액션 F-2 — 스펙 L34/L61/L95 인코딩 완료
- last-write-wins 단일 세션 — 스펙 M-4 인코딩 완료
- 툴바/2탭 고정 슬롯 편집기 모델 — T-018 구현 결정으로 기록, 스펙 편집 방식과 정합

---

## Recommended Next Steps

1. **E15 partial (minor)** — 수용 여부 확인. 수용 시 U-1을 스펙 API 절에 1줄 추가해 인코딩 (다음 스펙 갱신 주기에). 비수용 시 전용 무효화 엔드포인트 또는 프런트 시점 즉시 무효화 방안 논의.
2. **F1/F2 not-verifiable** — 성능 수동 벤치마크(100만 이벤트 로드, 200노드/500링크 토폴로지, 브라우저 DevTools)를 희망하면 별도 세션에서 진행. 스펙에 측정 방법 명시 여부는 선택.
3. **U-2/U-3** — 경미. 스펙 반영은 사용자 재량 (수용 시 spec-writing).
4. 위 사항 리뷰 후 **T-010 (v2 완료 승인 게이트)** 진행 — 승인 시 v3(데스크톱) 논의 가능. ✅ **완료 (2026-08-13, 사용자 승인)** — v2 완료 확정.

## User Review

- **E15 partial — 수용 (2026-08-13, 사용자):** 무효화 신호 = `/api/validate` 호출을 스펙에 인코딩 — `spec/sdv-sim-v2.md` M-4 절·`POST /api/validate` API 절·Requirements 절 3곳 반영 완료. ASR-015 Notes에 기록. (T-009 검증 U-1 해소) ⚠️ **2026-08-13 T-024로 재설계·폐기:** 이 인코딩은 편집 없이도 validate가 불리는 경로(마운트/재마운트 디바운스)에서 run 후 세션이 죽는 버그(리포트 409)를 유발 → validate는 순수 검증으로 전환, 세션 무효화는 프런트 로컬 상태(`SessionMeta.invalidated`)로 이동 (스펙 M-4/API/Requirements 재인코딩 완료, 신규 테스트 `test_validate_does_not_invalidate_session` 포함 pytest 113 passed).
- **F1/F2 실측 벤치마크 — 추후 진행 (2026-08-13, 사용자):** 100만 이벤트 로드·200노드/500링크 60fps 실측은 별도 세션에서 진행. 현재 스펙의 성능 기준은 구조 검증(check-replay O(K))으로만 보증.
- **T-010 — v2 완료 승인 (2026-08-13, 사용자):** 검증 결과 + 외부 접근(T-022) + 기본 샘플(T-023) + 리포트 409 버그 수정(T-024) + deploy 산출물(T-025~T-028) 반영 후 최종 승인. v3(데스크톱)는 별도 논의.

---

*검증 방법: 서버 코드 전문 독해 + TestClient 통합 스모크(9개 시나리오: GET /, validate, run, events/report, 편집→409, load-log no-arch/with-arch, log_invalid, not_found) + pytest 111 passed + mypy strict 18 files clean + `npm run check:{layout,files,replay}` + typecheck + wheel 내용 확인(T-020).*
