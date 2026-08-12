# Spec Review: SDV Simulator v2 (Gate T-007)

**대상 Spec:** `{project-root}/spec/sdv-sim-v2.md` (상위: `{project-root}/spec/PRD.md`)
**교차 검증 대상:**
- v1 구현: `sdv_sim/core/engine.py`, `sdv_sim/schema/arch.py`, `sdv_sim/schema/scenario.py`, `sdv_sim/core/events.py`, `sdv_sim/core/report.py`, `sdv_sim/cli/main.py`
- v1 Spec: `spec/sdv-sim-v1.md` (계약 원천)
- ADR 11건 (v2) + `spec/ASR.md` (ASR-014~020)
**검토일:** 2026-08-12
**요약:** 계약·사실 정확성 pass (14/14) / PRD 정합 pass (7/7) / ADR 인코딩 partial (4건 미인코딩 downstream concern 잔존) / 내부 일관성 fail (모순 3건) / SSOT 충분성 **partial — 잔존 미해소 사항으로 승인 전 해소 권장**

---

## 1. 검증 인벤토리 및 결과

### 1-1. PRD 정합성 (v2 Spec ↔ PRD v2)

| # | Spec 항목 | 상태 | 근거 / 비고 |
|---|-----------|------|-------------|
| 1 | 구조 뷰 중심 — YAML → 자동 렌더링 | pass | Decisions(구조 뷰 렌더링), Requirements(구조 뷰) |
| 2 | 편집·파일 관리 (목록/열기/새로 만들기/편집/저장) | pass | Decisions(편집·파일 관리, API) |
| 3 | 시뮬레이션 오버레이 리플레이 | pass | Decisions(오버레이 렌더 규칙) |
| 4 | 인터랙션 (컨트롤·패널·필터) | pass | Decisions(컨트롤·보조 패널·필터) |
| 5 | assertion·리포트 확인 (성공 기준 4) | pass | Decisions(리포트·assertion 표시) |
| 6 | v1 코어 무변경 (성공 기준 5) | pass | Constraints·Decisions(모듈 경계, C-1 해소) |
| 7 | 검증 피드백 + 로컬 저장 (성공 기준 6) | pass | Decisions(편집·파일 관리) |

### 1-2. v1 계약·사실 정확성 (v2 Spec ↔ v1 구현 코드)

| # | Spec 주장 | 상태 | 근거 (구현) | 비고 |
|---|-----------|------|-------------|------|
| 8 | `Simulator(arch_model, scenario_model).run()` 생성자 사용 | pass | `engine.py` L206-211 — `__init__(arch: Architecture, scenario: Scenario, components=None)` | ✅ |
| 9 | v1 `load()`의 `str` = 파일 경로 (미사용 선언) | pass | `engine.py` L836-844 — `Path(path).read_text()` | ✅ C-1 해소 정확 |
| 10 | Report 구조 `simulation{...}/links[]/tasks[]/assertions[]/warnings[]` | pass | `core/report.py` L42-48 | ✅ |
| 11 | 이벤트 7종 enum + 필드 `(t_ms, seq, node?, link?, frame?, task?, data?)` | pass | `core/events.py` L8, L11-26; `cli/main.py` L112-114 | ✅ |
| 12 | tx→rx 정합 — `[tx, tx+tx_ms)` 재생, rx = 시작 + tx_ms (전파 지연 0) | pass | `engine.py` L587-611 — `completion = start + tx` | ✅ CAN 큐잉 후 시작 시각도 tx 이벤트 시각과 일치 |
| 13 | 게이트웨이 라우팅 = 소스 링크 **전송 완료** 시각 기준 | pass | `engine.py` L617-650 — `_route_frame` at `completion + delay_ms` | ✅ |
| 14 | load-log 파생 불가 판단: `bus_load_percent`(DLC·bitrate 필요), `supersede_count`(미기록), `tasks[].period_ms` | pass | 이벤트에 dlc/bitrate 없음; supersede는 `_enqueue`에서 count만 증가(이벤트 미기록) `engine.py` L185-197 | ✅ L56 판단 정확 |
| 15 | load-log 파생 가능 판단: links(tx/rx/drop), tasks(run/overrun), simulation, assertions | pass | tx/rx/drop/task_start/overrun 이벤트에서 집계 가능; 로그에 `simulation`, `assertions` 포함 (`cli/main.py` L117-130) | ✅ |
| 16 | 로그 검증 규칙 (`schema_version==1`, type enum, `(t_ms, seq)` 정렬) | pass | v1 로그 스키마와 일치 | ✅ |
| 17 | 동기 실행 — 수 초 내 완료 (진행률 UI 비목표) | pass | v1 성능 목표(≤100만 이벤트)와 정합 | ✅ |

### 1-3. ADR 인코딩 충실도

| # | ADR (해소 항목) | 상태 | 비고 |
|---|-----------------|------|------|
| 18 | C-1 dashboard-run-path (생성자 경로) | pass | L29, L87 인코딩 완료 — 시그니처 정확 |
| 19 | M-1 dashboard-load-log-report (파생 규칙) | **partial** | 파생/불가 목록 인코딩 ✅. 단 "세션에 아키텍처 스냅샷이 있으면 전체 Report"의 **스냅샷 획득 메커니즘 미인코딩 + M-4와 규칙 충돌** (아래 F-2) |
| 20 | M-2 dashboard-replay-animation-timing | **partial** | 물리 재생 + 고정 펄스 폴백 ✅. 단 "drop/**supersede** 이벤트로부터 도출" 문구 — **supersede 이벤트는 v1에 존재하지 않음** (아래 F-1) |
| 21 | M-3 dashboard-seek-state-indexing | **partial** | O(K) 상한·스냅샷·2s 예산 ✅. 단 **load-log 경로의 시크 상태 의미론 미정의** (아래 F-5) |
| 22 | M-4 dashboard-session-lifecycle | **partial** | 세션 정의·무효화·last-write-wins ✅. 단 **무효화 후 events/report API 동작 미정의** (아래 F-7) |
| 23 | M-5 dashboard-layout-determinism | **partial** | 결정성 요구 ✅. 단 "노드 타입·링크 종류 기준 배치"가 **검증 불가능할 정도로 추상적** (아래 F-6) |
| 24 | ASR-014 (기술 스택) / ASR-017 (보안) / ASR-019 (serve) / ASR-020 (i18n) | pass | 인코딩 일치 |
| 25 | ASR-018 downstream "검증 응답 형태" | **partial** | `{path, line, message}`는 명시 ✅. 전체 오류 응답 스키마 미정의 (아래 F-8) |
| 26 | dashboard-run-path downstream "시나리오 단독 검증 범위" | **fail** | **미인코딩** — 참조 검증(unknown link/frame)은 arch 없이 불가 (아래 F-4) |

### 1-4. 내부 일관성

| # | 항목 | 상태 | 비고 |
|---|------|------|------|
| 27 | L43 "drop/**supersede** 이벤트로부터 도출" vs L56 "supersede는 **이벤트 미기록**" | **fail** | 내부 모순 (아래 F-1) |
| 28 | M-1 "세션에 아키텍처 스냅샷이 있으면 전체 Report" vs M-4 "파일 열기/새로 만들기 시 세션 리셋" | **fail** | 규칙 충돌 (아래 F-2) |
| 29 | Related "adr/dashboard-tech-stack.md 외 **ADR 4건**" (L166) | **fail** | 실제 v2 ADR은 11건 (Context L10과도 불일치) |
| 30 | Open Questions "(없음)" (L160) | **fail** | 잔존 미해소 downstream concern 존재 (F-4~F-8) |
| 31 | TODO.md "verification/sdv-sim-v2-spec-review.md Part 6" 존재 언급 | **fail** | 해당 파일 없음 (T-007 노트와 실제 파일 불일치) |

---

## 2. 주요 발견 (Findings)

### F-1 (오류 — 수정 필요): "drop/supersede 이벤트" 문구 — supersede는 이벤트가 아님

- **위치:** v2 spec L43 "큐 깊이는 v1 이벤트에 없으므로 drop/**supersede** 이벤트로부터 도출되는 근사 표시"; M-2 ADR consequence에도 동일 문구 전파됨.
- **사실 확인:** v1은 supersede를 **이벤트로 기록하지 않는다** (v1 D-18: "교체는 별도 이벤트로 기록하지 않음"; 이벤트 enum 7종에 supersede 없음 — `events.py` L8; 구현도 `_enqueue`에서 count만 증가). 같은 spec L56이 정확히 이 점을 인정("supersede는 이벤트 미기록 — v1 D-18") — **내부 모순**.
- **영향:** 큐 상태 근사 표시가 어떤 신호로부터 도출되는지 오도. 생성자가 supersede 이벤트를 기다리는 로직을 만들 위험.
- **조치:** "drop 이벤트로부터 도출되는 근사 표시"로 수정 (supersede 신호는 로그에서 얻을 수 없음). ADR consequence 문구도 함께 정정.

### F-2 (모순 — 해소 필요): load-log 전체 Report의 "아키텍처 스냅샷" 획득 메커니즘 미정의 + M-4와 충돌

- **위치:** v2 spec L56 (M-1) vs L34 (M-4).
- **문제:** M-1은 "세션에 아키텍처 스냅샷이 있으면 전체 Report 계산"이라 하지만, M-4는 "파일 열기/새로 만들기 시 세션 리셋"이라 규정. load-log 세션에는 arch 스냅샷이 없고, arch 파일을 열면 세션이 리셋되므로 **두 규칙을 동시에 만족하는 경로가 없다**. load-log-report ADR의 downstream concern("대응 arch를 어떻게 식별하는가 — spec 인코딩")이 실제로는 미인코딩된 채로 남음.
- **영향:** "로그 로드 후 대응 아키텍처 열면 전체 리포트"라는 UX 약속이 구현 불가능할 수 있음. 생성자가 임의로 동작을 정해야 하는 공백.
- **조치:** 아래 중 하나를 spec에 명시 — (a) 세션에 arch 스냅샷을 붙이는 별도 API/액션 (예: "리포트에 아키텍처 연결" 액션이 arch 열기를 세션 교체가 아닌 세션 보강으로 처리), (b) "파일 열기 = 세션 리셋"을 "로그 세션 + 열린 arch와의 페어링"으로 재정의, 또는 (c) M-1의 arch 연동 약속을 load-log에서 제거(파생 가능 항목만 표시로 단순화).

### F-3 (오류/오해 — 확인 필요): 포트 충돌 exit code 2의 "v1 체계 정합" 주장

- **위치:** v2 spec L24.
- **문제:** v1 종료 코드 2 = "**입력 오류**(스키마·파일)" (v1 D-16). 포트 점유는 입력 오류가 아니라 **환경 오류**. v1 선례(log-write-failure → 2)가 "파일/리소스 오류"를 2로 분류한 근거가 되므로 정당화는 가능하나, "정합"이라는 표현은 의미론적으로 약함. 3(내부 오류) 또는 별도 코드가 더 적절할 수 있음.
- **조치:** "v1 리소스 오류 분류 선례(로그 쓰기 실패 → 2)에 따른 결정"으로 근거를 명시하거나, 코드를 재검토. 사용자 확정 필요.

### F-4 (미인코딩 downstream — Major): `/api/validate` 시나리오 단독 검증 범위 미정의

- **위치:** v2 spec L86, L90 (저장 강제 검증 포함).
- **문제:** run-path ADR downstream concern #2가 **그대로 미해소**: 시나리오의 참조 검증(unknown link/frame, assertion 참조)은 아키텍처 없이 불가능. 그런데 편집·저장은 arch/scenario 개별 파일 단위로 일어남. "저장·실행 시 강제 검증"에서 시나리오 단독 저장 시 (1) 무엇을 검증하는지(구조만? 참조 포함?), (2) 어떤 arch와 페어링하는지(마지막으로 연 arch? 요청에 arch 내용 포함?)가 미정의.
- **영향:** 검증 강제(Requirements)의 의미가 파일 종류에 따라 달라져 테스트 불가. 생성 시 임의 구현 위험.
- **조치:** spec에 (a) validate 요청에 `arch` 페어링 정보를 선택적으로 포함, (b) 시나리오 단독 검증은 구조 검증만 + 참조 검증은 "페어링된 arch가 있을 때만" 명시.

### F-5 (미인코딩 downstream — Major): 시크 상태의 load-log 경로 의미론 미정의

- **위치:** v2 spec L33, L52.
- **문제:** 스냅샷이 캡처하는 "링크 in-flight 프레임" 상태는 tx_ms(DLC/bitrate) 계산이 필요 — 아키텍처가 없는 load-log 경로에서는 계산 불가. M-2가 애니메이션에는 "고정 펄스 폴백"을 정의했지만, **시크 상태 계산(특히 in-flight 판정)의 load-log 동작은 미정의**.
- **영향:** 100ms 시크 요구가 load-log 경로에서 의미하는 바가 불명확. "근사 표시"가 시크 상태에도 적용되는지, in-flight 상태를 생략하는지 불명.
- **조치:** "load-log 경로의 시크 상태는 고정 펄스 근사(또는 in-flight 미표시)"를 명시.

### F-6 (추상적 요구 — Major): 레이아웃 "노드 타입·링크 종류 기준 배치"가 검증 불가

- **위치:** v2 spec L39, L117.
- **문제:** 결정성("동일 YAML → 동일 좌표")은 테스트 가능하지만, "노드 타입(ECU/HPC)·링크 종류(CAN/Ethernet) 기준 배치"는 **무엇을 배치 규칙으로 삼는지 명시가 없어** 검증 불가. layout-determinism ADR downstream concern("레이아웃 기준 구체화 — spec 인코딩") 미인코딩.
- **영향:** 검증 단계에서 "타입 기준 배치"를 확인할 방법 없음. 생성자가 타입 기준을 무시해도 fail 판정 불가.
- **조치:** 최소한 검증 가능한 규칙으로 구체화 (예: "ECU/HPC 타입별 그룹(클러스터) 배치 + 링크 종류별 시각적 구분(색/굵기) + 결정적 좌표", 또는 "같은 타입 노드는 근접 배치" 등).

### F-7 (미정의 — Medium): 세션 무효화 후 `GET /api/events`·`GET /api/report` 동작

- **위치:** v2 spec L88-89, L127.
- **문제:** 편집 시작 시 세션 무효화 규칙은 있으나, 무효화된 세션에 대해 events/report API가 무엇을 반환하는지(404? 빈 목록? "무효" 표시 응답?) 미정의. 프런트가 오버레이를 해제한 후 재조회 시 동작이 API 계약에 없음.
- **조치:** "무효화된 세션 조회 시 409 (또는 204/빈 응답) + 사유" 명시.

### F-8 (미정의 — Medium): API 오류 응답 스키마 미정의

- **위치:** v2 spec API 절 전반 (400/422 사용).
- **문제:** 400(traversal)·422(검증) 등 상태 코드는 있으나 **응답 바디 형태**(예: `{error: {code, message, detail}}`)가 없어, 검증 오류 목록(`{path, line, message}`)과 일반 오류의 형식 구분이 불명확.
- **조치:** API 오류 응답 스키마 1줄 정의로 자체-포함·테스트 가능하게.

### F-9 (미정의 — Medium): 새 파일 생성·목록 응답 형태

- **위치:** v2 spec L82-85.
- **문제:** `POST /api/files {name, kind}` — `name`에 하위 경로 허용 여부, `.yaml/.yml` 확장자 강제 여부, 기존 파일 충돌 시 동작(409 vs 덮어쓰기) 미정의. `GET /api/files`의 응답 형태(경로 목록? kind 포함 객체?) 미정의.
- **조치:** 각 1줄 명시.

### F-10 (미정의 — Medium): SPA fallback / dot-dir 직접 접근 / 상세 사항

- **SPA fallback:** 클라이언트 라우팅 사용 시 비-API GET 경로에 `index.html` 서빙 정책 미언급 (해시 라우팅 사용 시 불필요 — 사용 여부 명시 권장).
- **dot-dir 제외 범위:** 목록 제외는 명시되어 있으나(L74) **직접 경로 접근** (`GET /api/files/.venv/x.yaml`) 정책 미정의 — 목록 제외를 우회 가능.
- **load-log 경로 warnings[]:** 파생 가능 목록에 없음 — 빈 배열로 표시인지 미표시인지 미정의 (경미).
- **`--root` 상대 경로:** 상대 경로 해석 기준(CWD) 미정의 (경미).
- **이벤트 상세 패널 100만 건:** 필터/가상화 처리 정책 미언급 (성능 구현 디테일, 경미).

### F-11 (재확인 권장 — 설계 검토): CWD 기본 `--root`의 보안 노출

- L23: 기본 `--root` = CWD. 명시된 결정이므로 모호하진 않으나, `$HOME`에서 실행 시 홈 전체가 샌드박스가 됨. 로컬 단일 사용자 도구로 수용 가능한지 사용자 확정 권장 (문서화 또는 기본값 재검토).

---

## 3. SSOT 충분성 평가

**결론: 대체로 충분하지만, "승인 전 해소"가 필요한 잔존 항목이 있다.**

- ✅ **강점:** 자체-포함·테스트 가능한 불릿 구조. v1 계약에 대한 14개 사실 주장이 구현과 **전부 일치** (생성자 시그니처, load() 의미, Report/이벤트 스키마, tx→rx 정합, 게이트웨이 타이밍, 파생/불가 판단). ADR을 "생성에 필수 아님"으로 명시한 것도 SSOT 정신에 부합. 생성 시 결정 위임(K·스냅샷, 레이아웃 알고리즘)도 상한(O(K))·결정성으로 테스트 가능하게 봉인됨.
- ❌ **잔존 미해소:** ADR downstream concern 중 4건이 spec에 인코딩되지 않음 (F-2, F-4, F-5, F-6) — 이 4건은 **생성자가 임의로 정해야 하는 설계 결정**이므로 SSOT로 승인하면 생성 품질이 사용자 의도와 어긋날 위험. 사실 오류(F-1)와 내부 모순(F-2)도 수정 필요.
- ⚠️ **검증 방법 미정의:** 성능 기준(60fps/2s/100ms)의 측정·검증 방법이 spec에 없음 — 검증 스테이지(T-009)에서의 기준이 필요하면 명시.

---

## 4. 권장 다음 단계

1. **필수 수정 (spec-writing):** F-1 (supersede 문구), F-2 (M-1×M-4 모순), F-4 (validate 범위), F-5 (시크 load-log), F-6 (레이아웃 규칙) — 5건 인코딩
2. **간단 명시 (spec-writing):** F-7~F-10 (무효화 후 API, 오류 스키마, 파일 API 형태, SPA/dot-dir)
3. **사용자 확정:** F-3 (포트 exit code), F-11 (CWD --root), F-6의 배치 규칙 방향
4. 이후 **T-007 승인** → ASR-014~020 approved → T-008 (생성) 진행

## User Review

- **F-3 (포트 충돌 exit code 2):** 사용자 확정 — 종료 코드 2 유지 (기본 결정). spec에 "v1 리소스 오류 분류 선례(로그 쓰기 실패 → 2)에 따른 결정"으로 근거 명시 필요. (2026-08-12)
- **F-6 (레이아웃 배치 규칙):** 사용자 확정 — **Option A (타입 밴드)**. `adr/dashboard-layout-placement-rule.md` approved 전환 + ASR-016 designed 전환 완료 (2026-08-12).
- **F-11 (파일 접근 방향):** 사용자 방향 전환 — "서버에 저장한다는 개념은 부적절". (1) v1 core/cli에 **YAML 문자열 입력 API** 추가 지시, (2) 브라우저가 **로컬 파일을 직접** 사용 (Server-FS 샌드박스 탈피). → 신규 ADR 2건 초안 작성: `adr/core-yaml-string-input.md`, `adr/dashboard-browser-file-access.md` (proposed, 리뷰 대기). `adr/dashboard-run-path.md` superseded. ASR-006/015/017 reviewing 복귀. (2026-08-12)

## Finding 해소 기록 (2026-08-12, T-012)

| Finding | 해소 방식 | 상태 |
|---------|-----------|------|
| F-1 (supersede 이벤트 오류) | L48 — "drop 이벤트로부터 도출" + "supersede는 이벤트 미기록(v1 D-18)" 명시 | ✅ 수정됨 |
| F-2 (M-1×M-4 모순) | `POST /api/load-log`의 `arch_content` 단일 액션 — 파일 열기와 별개로 세션에 arch 스냅샷 포함 (L34/L61/L95) | ✅ 해소 |
| F-3 (exit 2 근거) | L24 — "v1 리소스 오류 분류 선례(로그 쓰기 실패 → 2, D-16·U-3)" 명시 | ✅ 반영 |
| F-4 (validate 범위) | 시나리오 단독 = 구조 검증만, arch 페어링 시 참조 검증 (L75/L93/L122) | ✅ 인코딩 |
| F-5 (시크 load-log) | 고정 펄스 근사 또는 in-flight 미표시 (L33/L133) | ✅ 인코딩 |
| F-6 (레이아웃 규칙) | 타입 밴드(Option A) 규칙 전체 인코딩 (L39-44/L126) | ✅ 인코딩 |
| F-7 (무효화 후 API) | events/report 409 + `session_invalid` (L96-97/L139) | ✅ 인코딩 |
| F-8 (오류 스키마) | `{error: {code, message, detail?}}` (L92) | ✅ 인코딩 |
| F-9 (파일 API 형태) | 파일 API 제거로 소멸 — 최근 파일(IndexedDB) 대체 (L71/L115) | ✅ 해소 |
| F-10 (SPA 등) | 해시 라우팅(L158), warnings[] 파생 불가(L61), dot-dir·--root 문제는 파일 API 제거로 소멸 | ✅ 해소 |
| F-11 (CWD --root) | 방향 전환 — 브라우저 로컬 파일(하이브리드), 서버 파일 API·--root 제거 (L23/L67-71/L80-84) | ✅ 반영 |

- **T-012 완료 (2026-08-12):** v2 Spec·PRD·v1 Spec(D-15)·ASR.md 전면 갱신. **T-007 (v2 Spec 승인 게이트) 재개 대기.**
