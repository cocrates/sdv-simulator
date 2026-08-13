# 부록 B. sdv-simulator 사양 요약 (spec v1/v2)

- **범위**: 본문이 참조하는 Spec(`spec/sdv-sim-v1.md` v1, `spec/sdv-sim-v2.md` v2)의 핵심 요구사항 집합 요약 — 원문 재생산이 아닌 요약 표 중심
- **용도**: 본문의 D-번호/F-번호/M-번호 인용이 어느 spec의 어떤 절에 근거하는지 추적 (B.3)
- **SSOT**: `spec/`가 유일한 요구사항 원천 — 본 부록은 요약이며, 모순 발생 시 spec이 우선한다

## B.1 v1 요약 — D-번호별 핵심 요구

v1 상세 설계 ADR 10건(D-12~D-21, 2026-08-12 승인)의 결정이 인코딩된 요구사항 1줄 요약:

| 번호 | 주제 | 핵심 요구 (1줄) |
|------|------|-----------------|
| D-12 | 정의 필드-레벨 스키마 & 메시지 주입 | `architecture.yaml`(nodes/links/gateways)과 `scenario.yaml`(duration_ms/messages/assertions) 필드 트리를 정의하고, `messages` 주입 항목(`t_ms`/`link`/`frame`/`data?`)은 tx 이벤트로 기록 (필드 상세 = 부록 A) |
| D-13 | 통신 이벤트 기록 의미론 | tx는 주기 프레임·`ctx.send`·주입 3경로, rx는 `receives` 매핑된 노드에만, 게이트웨이는 인프라(규칙 체인, 홉 ≤ 8), Ethernet은 스위치 FIFO 방출 시각에 rx |
| D-14 | 스텁 컴포넌트 동작 | `class` 미등록 컴포넌트는 수신자 전용 — `sends` 무시, 자동 송신 없음 (tx 3경로만 존재) |
| D-15 | 공개 API 계약 | `load(경로)`/`loads(YAML 문자열)`/`load_scenario`/`load_scenario_yaml` → `Simulator`, `run()` → `SimulationResult`(events 리스트·report·assertions·duration_ms), `TaskContext`(send/log/now_ms) |
| D-16 | CLI 입출력 채널 | `--log <path>`(기본 `events.json`, `-`=stdout)/`--quiet`/`--lang` — 파일 쓰기 실패는 exit 2, 오류 카테고리·공통 메시지는 ko/en, 내부 예외 상세는 원문 유지 |
| D-17 | 태스크 오버런 정책 | 오버런 후 다음 인스턴스는 **절대 주기**(원래 t=0 기준) 유지, 놓친 주기는 스킵 — 밀림 없음 |
| D-18 | 프레임 큐 인스턴스 정책 | 큐 대기 중 동일 프레임의 새 주기 인스턴스 도착 시 **최신 교체**(supersede) — 교체는 큐 depth 비소모, 별도 이벤트 없음 |
| D-19 | 이벤트 순서·종료 경계 | 동일 시각 = 태스크 우선순위(작을수록) → 파일 선언 순서 → seq, 비-태스크는 모든 태스크 뒤(가상 우선순위 2^30), `t == duration_ms` 포함(inclusive) 종료 |
| D-20 | Assertion 평가 규칙 | event 타입 + 지정 속성 모두 일치, `event: task`는 start+end 둘 다, `at_ms` 명시 시 `\|t_ms-at_ms\| ≤ within_ms` / 생략 시 시간 무관, `count` = 최소 n건(≥), 실패 메시지 = 매칭 최대 3건 + 기대/실제 |
| D-21 | 결과 리포트 스키마 | `simulation` + `links`(tx/rx/drop/supersede/bus_load_percent) + `tasks`(run/overrun) + `assertions` + `warnings`, `bus_load_percent = tx_ms 합 / duration_ms` |

### v1 기본 결정 그룹 (1차 ADR 11건 — D-번호 없이 Decisions에 인코딩)

| 주제 | 핵심 결정 |
|------|-----------|
| 언어/런타임 | Python 3.11+ (타입 힌트 + mypy strict), pip 패키지 + CLI 진입점, 난수 미사용(결정성) |
| 성능 목표 | v1 순수 Python — 노드 ≤ 50, 링크 ≤ 20, 프레임 ≤ 200, duration ≤ 60s, 이벤트 ≤ 100만 건 → 수 초 내 실행 |
| 패키지 구조 | 배포명 `sdv-sim` / 임포트명 `sdv_sim`, 단일 패키지 + `sdv_sim/core`·`sdv_sim/cli` 모듈 경계 |
| 시뮬레이션 엔진 | DES(이벤트 큐 + 단일 스레드 + fast-forward), 모든 시간은 정수 ms, 이벤트 `(t_ms, seq)` 완전 순서 |
| 정의 형식 | YAML (PyYAML + Pydantic), 메시지-프레임 2계층 + 매핑 규칙, architecture/scenario 파일 분리 |
| 통신 충실도 | L2 — CAN `ceil((44+8·DLC)/bitrate)` + ID 우선 중재 + 우선순위 큐, Ethernet `ceil((dlc+42)·8/(bitrate·1000))` + FIFO + 테일 드롭, 게이트웨이 `from/to` 명시 규칙 |
| 앱 런타임 | RTE 스타일(주기 태스크 + 이벤트 핸들러), 비선점 + `wcet_ms` + overrun 기록, `Component` 베이스 클래스 + `ctx.send/log/now_ms` |
| 검증·자동화 | YAML 선언형 assertion + 결정적 JSON 이벤트 로그(단일 문서, type enum 7종) + CLI 종료 코드 0/1/2/3 |

### v1 검증 발굴 항목 (U-1~U-6 — spec-driven-verification에서 식별 → 스펙 인코딩)

| # | 결정 내용 | 스펙 인코딩 위치 |
|---|-----------|------------------|
| U-1 | 같은 tick 비-태스크 이벤트는 모든 태스크 뒤 (가상 우선순위 2^30) | D-19 |
| U-2 | Ethernet `switches` 2개 이상 정의 시 첫 번째만 사용 | 통신 충실도 (L2) |
| U-3 | 로그 파일 쓰기 실패 시 종료 코드 2 (입력 오류 분류) | D-16 |
| U-4 | assertion `event: task`는 task_start + task_end 둘 다 매칭 | D-20 |
| U-5 | `count` = 최소 n건 이상(≥), 초과는 실패 아님 | D-20 |
| U-6 | Ethernet payload = 프레임 DLC 바이트 (`bytes = dlc + 42`) | 통신 충실도 (L2) |

## B.2 v2 요약 — F/M/T 번호별 핵심 요구

### B.2.1 spec-review 발굴 항목 (F-1~F-11)

v2 스펙 작성·검토 중 식별된 미정의/모순 항목 — 전부 `spec/sdv-sim-v2.md`에 인코딩·해소:

| 번호 | 핵심 요구 (1줄) | 해소 위치 |
|------|-----------------|-----------|
| F-1 | supersede 관련 문구 명확화 | v1 Report 파생 규칙 |
| F-2 | load-log에서 전체 Report 계산 — `POST /api/load-log`에 `arch_content` 포함 시 전체, 미포함 시 파생 가능 항목만 | 데이터 흐름·리플레이 (ASR-015) |
| F-3 | 설계 결정 근거를 스펙에 명시 | Context·Decisions 절 |
| F-4 | 검증 범위 — 시나리오 단독 = 구조 검증만, `arch` 페어링 시 참조 검증까지 | 편집·파일 관리 (ASR-018) |
| F-5 | load-log 경로 시크 상태 — 고정 펄스 근사 또는 in-flight 미표시 (tx_ms 계산 불가) | 데이터 흐름·리플레이 (ASR-015) |
| F-6 | 구조 뷰 자동 레이아웃 = 타입 밴드 (HPC 상단/게이트웨이 중앙/ECU 하단, 밴드 내 링크 수 내림차순 → 이름 사전순) | 구조 뷰 렌더링·성능 (ASR-016) |
| F-7 | 세션 없음 시 events/report 조회 = 409 + `{error: {code: session_invalid}}` | API (REST, JSON) |
| F-8 | 오류 응답 스키마 = `{error: {code, message, detail?}}` (code: validation_error/log_invalid/session_invalid/not_found/internal) | API (REST, JSON) |
| F-9 | 서버 파일 API(`/api/files*`)·`--root` 샌드박스 제거 — 서버는 파일 내용만 수신 | 파일 접근·보안 경계 (ASR-017) |
| F-10 | SPA 라우팅 = 해시 라우팅 (비-API GET 서빙 정책 불필요) | Constraints |
| F-11 | **방향 전환** — 브라우저가 로컬 파일 직접 관리(FS Access API + 업로드/다운로드 폴백) + v1 코어 `loads()` 문자열 입력 API 추가 | 파일 접근·보안 경계 (ASR-017) + v1 Spec D-15 |

### B.2.2 v2 설계 결정 (M-1~M-5)

| 번호 | 주제 | 핵심 요구 (1줄) |
|------|------|-----------------|
| M-1 | load-log 리포트 파생 규칙 | `simulation{duration_ms, result}`·`links[](tx/rx/drop)`·`tasks[](run/overrun)`·`assertions[]` 표시, 파생 불가 항목(bus_load/supersede/period_ms/warnings)은 미표시 — `arch_content` 포함 시 전체 Report |
| M-2 | 리플레이 애니메이션 타이밍 | run 경로: 지속시간 = `tx_ms`(DLC/bitrate)로 `[tx, tx+tx_ms)` 재생 — rx 시각과 정합. load-log 경로: 고정 펄스 + "근사 표시" 라벨 |
| M-3 | 시크 상태 인덱싱 | `(t_ms, seq)` 이진 탐색 + 주기적 상태 스냅샷(K개마다) + 잔여 ≤ K 재적용 — 시크 비용 상한 O(K), 반영 ≤ 100ms |
| M-4 | 세션 수명주기 | 세션 = events/report/duration_ms/source/스냅샷, run·load-log가 교체, 편집 시작 시 무효화 — **무효화는 프런트 로컬 상태(`SessionMeta.invalidated`)** (T-024) |
| M-5 | 레이아웃 결정성 | 동일 YAML → 동일 좌표. 비결정적 D3 포스 사용 금지, YAML 좌표 필드 없음 |

### B.2.3 후속 버그 수정·추가 요구 (T-023, T-024)

| 번호 | 주제 | 핵심 요구 (1줄) |
|------|------|-----------------|
| T-023 | 기본 샘플 시드 | 새 세션(기본 실행) 시 아키텍처·시나리오 슬롯이 `samples/basic` 미러 템플릿으로 시드 — 파일 생성 없이 [실행]으로 리플레이 확인 가능 |
| T-024 | 리포트 409 재설계 | `POST /api/validate`는 **순수 검증**(세션 부작용 없음) — 세션 무효화는 프런트 로컬 `SessionMeta.invalidated`로 이동 (기존 "무효화 신호 = validate 호출" 설계 폐기) |

### B.2.4 v2 ASR 요약

| ASR | 제목 | 핵심 결정 |
|-----|------|-----------|
| ASR-014 | 대시보드 기술 스택 | FastAPI + React/TypeScript + Vite, 신규 `sdv_sim/server/` 모듈 |
| ASR-015 | 데이터 흐름·리플레이 모델 | 서버 임베드 + 문자열 입력 API(`loads`), 일괄 JSON 전달, 로컬 재생/시크, 세션 수명주기 |
| ASR-016 | 구조 뷰 렌더링·성능 | SVG + React, 타입 밴드 결정적 레이아웃, 60fps/2s/100ms 성능 기준 |
| ASR-017 | 파일시스템 접근·보안 경계 | 서버 FS 비접촉, 브라우저 권한 경계 (FS Access API + 폴백) |
| ASR-018 | 편집·검증 피드백 | YAML 편집기 + 500ms 디바운스 검증 (v1 스키마 재사용) + 강제 검증 |
| ASR-019 | 패키지 통합·서버 명령 | `sdv-sim serve` 단일 프로세스, 정적 자산 패키지 내부, `--host` 옵션(기본 127.0.0.1) |
| ASR-020 | UI 언어 지원 | 프런트 i18n 카탈로그 ko/en, 언어 결정 `--lang` > env > 브라우저 로케일 |
| ASR-021 | 상시 실행 서비스 등록 | systemd user unit + install/uninstall (deploy/ — 실제 설치는 보류) |

## B.3 인용 매핑 표 (본문 장 ↔ 참조 번호 ↔ spec 파일/절)

| 본문 장/절 | 참조 D/F/M/U/T | spec 파일·절 |
|-----------|----------------|--------------|
| 1. 서론 | — | PRD.md (목표·범위·성공 기준), sdv-sim-v1.md Requirement |
| 2. 시스템 개요 | — | sdv-sim-v1.md Context·Decisions, sdv-sim-v2.md Requirement |
| 3. 정의 형식 개요 | D-12 | sdv-sim-v1.md "정의 필드-레벨 스키마 & 메시지 주입" (+ 부록 A) |
| 4.1 엔진 동작 모델 | D-19 | sdv-sim-v1.md "시뮬레이션 엔진 & 시간 모델" (순서·종료 경계) |
| 4.2 런타임 구조 | D-15 | sdv-sim-v1.md "공개 API 계약" |
| 4.3 실행 루프 | D-19 | sdv-sim-v1.md "시뮬레이션 엔진 & 시간 모델" |
| 4.4 통신 동작 (CAN/Ethernet) | D-13, D-18, U-2, U-6 | sdv-sim-v1.md "통신 충실도 (L2)"·"통신 이벤트 기록 의미론"·"프레임 큐 인스턴스 정책" |
| 4.5 게이트웨이 라우팅 | D-13 | sdv-sim-v1.md "통신 이벤트 기록 의미론" (게이트웨이·홉 ≤ 8) |
| 4.6 앱 런타임 | D-14, D-17 | sdv-sim-v1.md "앱 런타임"·"스텁 컴포넌트 동작"·"태스크 오버런 정책" |
| 4.7 검증과 자동화 | D-20, D-21 | sdv-sim-v1.md "Assertion 평가 규칙"·"결과 리포트 스키마"·"검증·자동화 & CLI" |
| 5. CLI | D-16 | sdv-sim-v1.md "CLI 입출력 채널"·"검증·자동화 & CLI", U-3 |
| 6. 대시보드 서버 | F-7, F-8, ASR-014/019 | sdv-sim-v2.md "기술 스택"·"제공 형태·서버"·"API (REST, JSON)" |
| 7.1 프런트엔드 모듈 구조 | F-10, F-11 | sdv-sim-v2.md Constraints·"파일 접근·보안 경계" |
| 7.2 상태 관리·라우팅 | F-10, M-4, T-024 | sdv-sim-v2.md Constraints·"데이터 흐름·리플레이" (세션 수명주기) |
| 7.3 구조 뷰 | F-6, M-5 | sdv-sim-v2.md "구조 뷰 렌더링·성능" |
| 7.4 리플레이 | M-1, M-2, M-3, F-5 | sdv-sim-v2.md "구조 뷰 렌더링·성능"·"데이터 흐름·리플레이" |
| 7.5 파일 접근 | F-9, F-11, ASR-017 | sdv-sim-v2.md "파일 접근·보안 경계"·"편집·파일 관리" |
| 7.6 검증 피드백 | F-4, T-024, ASR-018 | sdv-sim-v2.md "편집·검증"·API `POST /api/validate` |
| 7.7 i18n | ASR-020 | sdv-sim-v2.md "UI 언어" |
| 8. 핵심 데이터 흐름 | M-1, M-4, F-2, F-7, F-8, T-024 | sdv-sim-v2.md "데이터 흐름·리플레이"·"API (REST, JSON)" |
| 9. 모듈 의존성·확장성 | F-11 | sdv-sim-v2.md Constraints·"파일 접근·보안 경계", v1 D-15 `loads()` |
| 10. 배포 | ASR-019/021, T-025~T-028 | sdv-sim-v2.md "제공 형태·서버", deploy/ 산출물 |
| 11. 검증과 품질 | U-1~U-6, F-1~F-11 | verification/sdv-sim-v1.md, verification/sdv-sim-v2.md |
| 12. 향후 방향 | — | PRD.md (v3 데스크톱·OTA 후속 후보) |
| 13. 결론 | — | 전체 |
