# SDV Simulator v2 — 웹 대시보드 (sdv-sim serve)

## Requirement
브라우저 기반 **로컬 웹 대시보드** — 아키텍처·시나리오 YAML을 구조 다이어그램으로 확인·편집·저장하고, v1 코어 시뮬레이션 결과를 **구조 뷰 위에서 리플레이**로 시각화·인터랙션하는 도구. v1 코어에 **YAML 문자열 입력 API(`loads()`)**를 추가해 백엔드로 재사용한다 (F-11: 브라우저가 로컬 파일을 직접 관리, 서버는 파일 내용만 수신).

## Context
- 상위 문서: `{project-root}/spec/PRD.md` (v2 스테이지 승인, 2026-08-12)
- v1 = 라이브러리 코어 + CLI (spec/sdv-sim-v1.md). v2는 동일 패키지에 대시보드 서버를 추가
- 로컬 실행 전용(단일 사용자·단일 머신, 브라우저 접속), ko/en UI
- v2 결정 근거: ADR 13건 (기술 스택 / serve / 데이터 흐름 / 렌더링·성능 / 편집·검증 / 실행 경로(문자열 입력) / 리플레이 시간 / 시크 / 세션 수명주기 / load-log 리포트 / 레이아웃 결정성 / 레이아웃 배치 규칙 / 브라우저 파일 접근) + direct-input 1건 (ASR-020) — 참고용, 생성에 필수 아님

## Decisions

### 기술 스택 (ASR-014)
- **백엔드**: FastAPI (Python 3.11+, 동일 환경) — Pydantic 네이티브, v1 스키마 재사용
- **프런트엔드**: React + TypeScript + Vite
- **모듈 경계**: 신규 `sdv_sim/server/` 모듈. `sdv_sim/core`·`sdv_sim/cli`는 **YAML 문자열 입력 API 추가만 허용** (core-yaml-string-input 승인) — 기존 경로 기반 `load()`/`load_scenario()` 시그니처·동작은 **하위 호환으로 유지**, `sdv_sim/schema`는 수정하지 않는다
- v1 코어 공개 API 계약(`load`/`loads`/`run`/`SimulationResult.events|report|assertions`) 유지·확장

### 제공 형태·서버 (ASR-019)
- `sdv-sim serve` CLI 명령 추가 — **단일 프로세스**: FastAPI 앱 + 정적 자산을 함께 서빙
- 프런트엔드 빌드 산출물은 패키지 내부(`sdv_sim/server/static/`)에 포함 — 별도 dist 경로 불필요
- 옵션: `--port <int>`(기본 8000), `--lang ko|en`, `--dev`(Vite dev server 프록시 — HMR). **`--root` 옵션 없음** (F-11: 파일 접근은 브라우저 측 — dashboard-browser-file-access)
- 포트 점유 시 명확한 오류 메시지와 함께 **종료 코드 2** (v1 리소스 오류 분류 선례 — 로그 쓰기 실패 → 2, v1 D-16·U-3에 따른 결정)
- 시작 시 접속 URL(`http://127.0.0.1:{port}`) 출력, Ctrl+C로 종료, 서버 로그는 stdout
- 실행 전용 데이터는 메모리 유지 — 별도 DB·영속화 없음

### 데이터 흐름·리플레이 (ASR-015)
- **실행 경로**: 서버가 v1 코어를 동일 프로세스에 임베드(import). `POST /api/run`의 YAML 문자열은 v1 공개 **문자열 입력 API** `loads(arch_yaml: str, scenario_yaml: str)`로 파싱·검증한 뒤 `Simulator.run()`으로 실행 (core-yaml-string-input Option A — v1 `load()`의 파일 경로 시그니처는 사용하지 않는다). 파싱·검증 오류는 v1 `SdvSimInputError` 형식(파일명 대신 의사 식별자 `arch`/`scenario`)을 줄 번호 매핑과 함께 반환. `components` 등록 없이 실행 → **스텁 컴포넌트 동작** (v1 D-14)
- **파일 로드 겸용**: **브라우저가 로컬 v1 이벤트 로그 JSON(`events.json`, schema_version 1)을 직접 읽어** 내용을 `POST /api/load-log`로 전송 (dashboard-browser-file-access). **로그 검증 규칙**: `schema_version == 1`, `events[].type`는 7종 enum(`tx|rx|task_start|task_end|drop|overrun|log`), `(t_ms, seq)` 오름차순 정렬 — 실패 시 422 + 오류 목록
- **전달**: 이벤트는 타임스탬프 `(t_ms, seq)` 오름차순 **전체 목록**을 일괄 JSON으로 반환 (`GET /api/events`)
- **리플레이**: 프런트엔드가 전체 이벤트 보유 → **로컬 재생/일시정지/탐색(시크)**. SSE/WebSocket 스트리밍은 비목표
- **시크 (M-3 — dashboard-seek-state-indexing)**: 위치 결정은 `(t_ms, seq)` 배열 이진 탐색 + **주기적 상태 스냅샷**(이벤트 K개마다 노드 태스크·오버런, 링크 in-flight 프레임, 큐 신호 상태 캡처) + 잔여 ≤ K개 이벤트 재적용. 시크 비용 상한 **O(K)** 보장 — "시크 후 상태 반영 ≤ 100ms" 기준의 달성 전략. K·스냅샷 상세는 생성 시 결정하되 스냅샷 구축은 로드·정렬 2s 예산에 포함. **load-log 경로 (F-5): in-flight 프레임 판정에 tx_ms(DLC/bitrate)가 필요하므로 시크 상태는 고정 펄스 근사로 표시하거나 in-flight를 미표시한다** — 아키텍처가 없는 경로에서는 물리 in-flight 계산 불가
- **세션 수명주기 (M-4 — dashboard-session-lifecycle)**: 세션 = `{events, report, duration_ms, source: run|log, 아키텍처/시나리오 스냅샷}`. `POST /api/run`·`POST /api/load-log`가 세션을 **교체**. 열린 YAML의 **편집 시작(첫 변경) 시 세션 무효화** → 오버레이 해제 + "정의 변경으로 리플레이 무효" 표시. **편집기에서 파일 열기/새로 만들기(브라우저 파일 선택) 시 세션 리셋**. **load-log 전체 Report (M-1·F-2 해소)**: `POST /api/load-log` 요청에 **대응 아키텍처 YAML(`arch_content`)을 함께 포함하면** 해당 세션은 아키텍처 스냅샷을 보유해 **전체 Report** 계산 — 포함하지 않으면 파생 가능 항목만. (파일 열기 = 세션 교체 규칙과 별개로, load-log 요청 하나에 arch를 포함하는 **단일 액션**으로 모순 해소). 다중 탭: 서버 전역 세션 1개, **last-write-wins**
- 이벤트는 v1 로그 스키마의 `events` 배열을 그대로 전달 (축약 포맷 없음 — type: `tx|rx|task_start|task_end|drop|overrun|log`, 필드: `t_ms, seq, node?, link?, frame?, task?, data?`)

### 구조 뷰 렌더링·성능 (ASR-016)
- **렌더링**: SVG + React 커스텀 컴포넌트. D3는 레이아웃 계산(자동 배치)에만 사용
- **자동 레이아웃 — 타입 밴드 (M-5 + dashboard-layout-placement-rule Option A, F-6 해소)**:
  - 노드를 **타입별 수평 밴드**로 배치: HPC 밴드(상단) / 게이트웨이 밴드(중앙) / ECU 밴드(하단). 게이트웨이는 라우팅 인프라 엔티티이므로 중앙 배치 (v1 의미론)
  - **밴드 내 노드 순서 = 결정적 규칙**: 연결 링크 수 내림차순 → 이름 사전순 (동률 시). 게이트웨이가 없는 토폴로지는 게이트웨이 밴드를 생략하고 HPC/ECU 밴드 유지
  - 링크 종류(CAN/Ethernet)는 **시각적 속성**(색·굵기·대시)으로 구분 — 위치와 무관
  - **결정성**: 동일 입력(동일 YAML) → 동일 좌표. 비결정적 D3 포스 사용 금지. YAML 좌표 필드 추가 없음
  - 검증 가능 항목: "같은 타입 노드는 같은 밴드", "게이트웨이는 중앙 밴드", "동일 입력 → 동일 좌표", "CAN/Ethernet 시각 구분"
- **오버레이 렌더 규칙**:
  - 링크 위 프레임 전송 애니메이션 (M-2 — dashboard-replay-animation-timing): `tx` 이벤트 시각(전송 시작)에 송신 노드 → 링크 → 수신 노드 이동 표시, **지속시간 = tx_ms(DLC/bitrate 기반)로 [tx, tx+tx_ms) 구간 재생** — rx 이벤트 시각과 정확히 일치 (전파 지연 0 — v1 의미론). run 경로는 프런트가 보유한 아키텍처로 tx_ms 계산. **load-log 경로(아키텍처 없음): 고정 지속시간 펄스 폴백 + "근사 표시" 라벨** — 정확한 타임스탬프 대응은 run 경로 전용. **load-log + `arch_content` 포함 시에는 아키텍처가 있으므로 run 경로와 동일하게 tx_ms 물리 재생** (L61 Report 규칙과 정합)
  - 노드 상태 하이라이트: `task_start`/`task_end`(태스크 실행), `overrun`(오버런) — 노드 레벨
  - 링크/스위치 상태 하이라이트: `drop` 연관 (큐 상태) — **큐 깊이는 v1 이벤트에 없으므로 drop 이벤트로부터 도출되는 근사 표시, 깊이 수치 추정 금지** (supersede는 이벤트 미기록 — v1 D-18, 근사 신호로 사용 불가)
  - 게이트웨이 라우팅 표시: 소스 링크 **전송 완료** → 대상 링크 `tx` 체인 표시 (v1 라우팅은 전송 완료 시각에 동작 — rx 이벤트 기준 아님. 다중 홉 포함, 홉 ≤ 8 — v1)
  - 스위치 드롭 표시: `drop` 이벤트를 해당 스위치/링크 위치에 표시
- **컨트롤**: 재생/일시정지/탐색(시크) + 타임라인 + 배속(0.5x/1x/2x/4x). 타임라인 duration: run 경로 = `scenario.duration_ms`, load-log 경로 = 로그 `simulation.duration_ms`
- **보조 패널**: 타임라인·이벤트 상세 패널 — 구조 뷰와 클릭 연동 (노드/링크 클릭 → 해당 엔티티 이벤트 필터)
- **필터**: 이벤트 타입(tx/rx/task/drop/overrun/log) 및 엔티티(노드/링크) 필터. **task = `task_start`+`task_end` 그룹** (v1 D-20·U-4 정합)
- **성능 기준**:
  - 노드 ≤ 200 / 링크 ≤ 500 토폴로지에서 렌더·인터랙션 60fps 목표
  - ≤ 100만 이벤트 로드·정렬(시크 스냅샷 구축 포함) ≤ 2s
  - 시크(탐색) 후 노드·링크 상태 반영 ≤ 100ms — 주기적 스냅샷 + 잔여 ≤ K 재적용으로 시크 비용 상한 O(K) 보장 (M-3)

### 리포트·assertion 표시 (PRD 성공 기준 4)
- **run 경로**: 실행 결과로 v1 `Report` 구조 **전체**를 표시: `simulation{duration_ms, result, event_count}`, `links[]`(tx_count/rx_count/drop_count/supersede_count/bus_load_percent), `tasks[]`(run_count/overrun_count), `assertions[]`(name/status/detail), `warnings[]`
- **load-log 경로 (M-1 — dashboard-load-log-report, F-2 해소)**: 이벤트에서 **파생 가능한 항목만** 표시 — `simulation{duration_ms, result}`, `links[](tx_count/rx_count/drop_count)`, `tasks[](run_count/overrun_count)`, `assertions[]`. **파생 불가 항목(`links[].bus_load_percent`, `links[].supersede_count`, `tasks[].period_ms`, `warnings[]`)은 미표시(또는 "—")** (tx_ms는 DLC·bitrate 필요 — 정의 요구; supersede는 이벤트 미기록 — v1 D-18). **`POST /api/load-log`에 `arch_content`를 포함해 로드하면 전체 Report 계산** (v1 의미론 "리포트는 정의+이벤트에서 파생" 정합)
- 링크별 버스 부하(`bus_load_percent`)를 링크 표시에 반영 (run 경로 또는 arch_content 포함 load-log)
- assertion 실패 시 상세 메시지(매칭 이벤트 최대 3건 + 기대/실제 시각·count — v1 D-20) 표시

### 편집·파일 관리 (ASR-018)
- **편집 방식**: YAML 텍스트 편집기 — 탭/선택기로 열린 파일 전환, 새로 만들기, 저장
- **파일 열기/새로 만들기/저장 — 브라우저 로컬 파일 (F-11, dashboard-browser-file-access Option C)**:
  - Chrome/Edge: **File System Access API** — `showOpenFilePicker`(읽기)/`showSaveFilePicker`(같은 파일에 저장)로 실제 로컬 파일 직접 관리. 사용자 권한 프롬프트
  - Firefox/Safari: `<input type="file">`(읽기) + **Blob 다운로드**(저장) 폴백 — 저장은 새 다운로드 파일 생성
  - 서버 파일 API(`/api/files*`)·`--root` 샌드박스 **없음** — 서버는 파일 내용(문자열)만 수신
  - 파일 목록: 브라우저 측 **최근 파일**(IndexedDB)로 제공 (디렉터리 목록 대체)
- **실시간 동기화**: 편집 내용이 유효(YAML 파싱 + 스키마 검증 통과) 시 다이어그램이 즉시 갱신. 오류 시 **마지막 유효 상태를 유지**하고 오류만 표시
- **검증**: 서버가 **v1 Pydantic 스키마**(`sdv_sim/schema/arch.py`, `scenario.py`)를 그대로 재사용. 프런트엔드 스키마 포팅 없음
- **검증 시점**: 편집 중 디바운스 500ms 자동 검증 + **저장/실행 시 강제 검증** (실패 시 저장·실행 거부)
- **검증 범위 (F-4 — run-path downstream 해소)**: `POST /api/validate` 요청은 `arch` 필드를 **선택적으로** 포함할 수 있다. 아키텍처 단독 검증 = 스키마 검증 전체. **시나리오 단독 검증 = 구조 검증만** (unknown link/frame 등 참조 검증은 아키텍처가 없으면 불가) — `arch`가 포함되면 참조 검증까지 수행
- **오류 표시**: 줄 단위 인라인 마커 + 오류 메시지(파일명·줄 번호·필드 경로 — v1 스키마 오류 형식 정합)
- **새로 만들기**: 아키텍처/시나리오 기본 템플릿(skeleton)으로 신규 파일 생성 — v1 정의 스키마(spec/sdv-sim-v1.md) 기준 최소 필수 필드를 갖춘 템플릿
- **저장**: 검증 통과 시 브라우저 로컬 파일로 저장 (Chrome/Edge = 같은 파일, 기타 = 다운로드)

### 파일 접근·보안 경계 (ASR-017, F-11 재정의)
- **서버는 파일시스템에 접근하지 않는다** — 파일 API·`--root` 샌드박스 없음 (dashboard-browser-file-access)
- 파일 읽기/쓰기는 **브라우저 권한**이 경계 — FS Access API는 사용자 권한 프롬프트, 업로드/다운로드는 브라우저 표준 동작
- 허용 확장자 안내: `.yaml`/`.yml`(정의), `.json`(이벤트 로그) — 브라우저 파일 선택 UI에서 안내 (강제는 아님)
- 파일 삭제·이름 변경은 브라우저에서 미지원 (PRD 비목표 — 로컬 파일 관리 도구 사용)

### UI 언어 (ASR-020)
- 프런트엔드 **i18n 메시지 카탈로그(ko/en)** — UI 문자열 하드코딩 금지
- 언어 우선순위: `serve --lang` > `SDV_SIM_LANG` env > 브라우저 로케일 (ko/en 외 → ko) — v1 패턴 대응
- UI에 언어 선택 스위치(ko/en) 제공

### API (REST, JSON)
- **오류 응답 스키마 (F-8)**: 모든 오류는 `{error: {code, message, detail?}}` 형태. `code`는 기계 판독용 카테고리(`validation_error`/`log_invalid`/`session_invalid`/`not_found`/`internal`), `message`는 서버 언어(ko/en) 로컬라이즈, `detail`는 선택 — 검증 오류 목록일 경우 `{path, line, message}` 배열 (v1 스키마 오류 형식 정합)
- `POST /api/validate` — 검증 (`{kind: architecture|scenario, content, arch?: string}` → `{valid, errors: [{path, line, message}]}`). **시나리오 단독 시 arch 없으면 구조 검증만, arch 포함 시 참조 검증까지 (F-4)**. 오류 메시지는 서버 언어(ko/en)로 로컬라이즈
- `POST /api/run` — 실행 (`{architecture, scenario}` YAML 문자열 → v1 `loads(arch_yaml, scenario_yaml)` → `Simulator.run()` → 결과 + **세션 교체**). 검증 실패 시 422 + 오류 목록. (v1 `load()` 파일 경로 시그니처 미사용 — core-yaml-string-input)
- `POST /api/load-log` — 브라우저가 읽은 v1 이벤트 로그 JSON 로드 (`{name?, content, arch_content?: string}` → 로그 검증(`schema_version == 1`, type enum, `(t_ms, seq)` 정렬) → **세션 교체**). `arch_content` 포함 시 전체 Report 계산 (M-1, F-2 해소). 검증 실패 시 422 + 오류 목록
- `GET /api/events` — **현재 세션**의 전체 이벤트 목록 (`(t_ms, seq)` 오름차순). **세션 없음/무효화 시 409 + `{error: {code: session_invalid}}` (F-7)**
- `GET /api/report` — **현재 세션**의 `Report` + assertions 반환 (load-log 경로는 M-1 파생 규칙 적용). **세션 없음/무효화 시 409 + `{error: {code: session_invalid}}` (F-7)**
- 서버 오류 응답은 ko/en 중 서버 언어로 로컬라이즈 (내부 예외 상세는 원문 유지 — v1 D-16 정합)

## Requirements

### 서버 (serve)
- `sdv-sim serve` 명령이 존재하고 기본 포트 8000에서 대시보드를 제공한다
- `--port`/`--lang`/`--dev` 옵션이 동작한다 (`--root` 옵션은 없다)
- serve는 정적 자산을 패키지 내부에서 서빙한다 (외부 dist 경로 불필요)
- 포트 점유 시 명확한 오류와 종료 코드 2로 종료한다 (v1 리소스 오류 선례 — D-16·U-3)
- 시작 시 접속 URL을 출력한다
- serve 실행은 v1 코어의 **문자열 입력 API(`loads`/`load_scenario_yaml`) 추가만** 허용하며, 기존 경로 기반 API의 시그니처·동작은 변경하지 않는다 (core-yaml-string-input)

### 파일 관리 (브라우저)
- Chrome/Edge에서 File System Access API로 로컬 파일을 열고 같은 파일에 저장할 수 있다 (권한 프롬프트 포함)
- Firefox/Safari에서 파일 업로드(`<input type=file>`)로 열고, Blob 다운로드로 저장할 수 있다
- 서버 파일 API(`/api/files*`)와 `--root` 샌드박스는 제공되지 않는다
- 브라우저에서 파일 삭제·이름 변경 기능은 제공되지 않는다
- 최근 파일 목록(IndexedDB)을 제공한다

### 편집·검증
- YAML 텍스트 편집이 가능하고, 유효한 편집 내용이 다이어그램에 실시간 반영된다
- 검증 오류가 줄 단위 인라인으로 표시된다
- 저장·실행 시 검증이 강제되며 실패 시 거부된다
- 검증은 v1 Pydantic 스키마를 재사용한다 (프런트엔드 포팅 없음)
- 시나리오 단독 검증은 구조 검증만 수행하고, arch 페어링 시 참조 검증까지 수행한다 (F-4)

### 구조 뷰·리플레이
- 아키텍처 YAML의 노드/링크/게이트웨이/프레임이 자동 렌더링된다
- 자동 레이아웃은 **타입 밴드**다 — HPC 상단 / 게이트웨이 중앙 / ECU 하단, 밴드 내 연결 링크 수 내림차순 → 이름 사전순 (F-6, Option A)
- 자동 레이아웃은 결정적이다 — 동일 YAML 입력 → 동일 좌표 (M-5)
- 실행 결과가 구조 뷰 위에서 링크 프레임 애니메이션으로 재생된다 — run 경로는 tx_ms 물리 재생(rx 시각 정합), load-log 경로는 고정 펄스 + "근사 표시" (M-2)
- 노드 상태(태스크 실행·오버런) 하이라이트가 표시된다
- 링크/스위치 상태(drop 연관, 큐 근사 — 깊이 수치 추정 없음) 하이라이트가 표시된다 (supersede 신호 없음 — v1 D-18)
- 게이트웨이 라우팅(소스 전송 완료 → 대상 tx)·스위치 드롭이 표시된다
- 재생/일시정지/탐색 컨트롤과 타임라인이 동작한다
- load-log 경로의 시크 상태는 고정 펄스 근사이거나 in-flight를 미표시한다 (F-5)
- 이벤트 상세 패널이 구조 뷰와 클릭 연동된다
- 이벤트 타입·엔티티 필터가 동작한다 (task = task_start+task_end 그룹)
- assertion 결과와 리포트를 확인할 수 있다 — run 경로는 전체, load-log 경로는 파생 가능 항목만 (M-1)
- 브라우저가 선택한 v1 이벤트 로그 JSON을 로드해 리플레이할 수 있다 (`arch_content` 포함 시 전체 Report)
- 편집 시작(첫 변경) 시 세션이 무효화되어 리플레이 오버레이가 해제되고 안내가 표시된다 (M-4)
- 무효화된 세션의 events/report 조회는 409 + `session_invalid` 오류를 반환한다 (F-7)

### 성능
- 노드 ≤ 200 / 링크 ≤ 500 토폴로지에서 인터랙션이 60fps로 동작한다
- ≤ 100만 이벤트 로드·정렬(시크 스냅샷 구축 포함)이 2초 이내에 완료된다
- 시크 후 상태 반영이 100ms 이내에 완료된다 — 주기적 상태 스냅샷 + 잔여 ≤ K 재적용으로 시크 비용 상한 O(K) 보장 (M-3)

### 언어
- UI 문자열이 ko/en 카탈로그에서 제공된다 (하드코딩 없음)
- 언어 우선순위(`--lang` > `SDV_SIM_LANG` > 브라우저 로케일, 기본 ko)가 동작한다

## Constraints
- v1 코어 변경은 **문자열 입력 API(`loads`/`load_scenario_yaml`) 추가로 제한** — 기존 `load`/`run`/`events` 계약·동작 하위 호환 유지 (core-yaml-string-input)
- 로컬 실행 전용 (단일 사용자·단일 머신) — 클라우드·다중 사용자·인증 없음
- 파일 접근은 **브라우저 권한 경계** — 서버는 파일시스템에 접근하지 않는다 (F-11)
- 대시보드 실행은 컴포넌트 클래스 미등록(스텁 동작, v1 D-14) 기준 — 브라우저에서 Python 코드 등록 불가
- 시간·이벤트 의미론은 v1 그대로 (정수 ms, `(t_ms, seq)` 정렬, 전파 지연 0, 홉 ≤ 8)
- 시뮬레이션 스케일(노드 ≤ 50/링크 ≤ 20/이벤트 ≤ 100만 — v1 성능 목표)과 **렌더링 스케일(노드 ≤ 200/링크 ≤ 500 — v2 구조 뷰)은 다른 차원**: v2 뷰는 v1 산출물을 초과하는 규모의 토폴로지도 표시·리플레이할 수 있어야 함
- 프런트엔드 빌드(Node.js)는 개발·배포 절차에 포함 — 런타임은 빌드 산출물만 사용
- **SPA 라우팅 (F-10)**: 클라이언트 라우팅은 **해시 라우팅** 사용 — 비-API GET 경로 서빙 정책 불필요 (서버는 정적 자산만 서빙)

## Out of Scope
- OTA (업데이트 캠페인·버전 관리·배포 흐름) — 후속 후보
- 구조화 폼(폼 기반) 편집 / 시각적(드래그 앤 드롭) 아키텍처 편집
- 파일 삭제·이름 변경 (브라우저에서)
- **서버 측 파일시스템 접근·파일 API·`--root` 샌드박스 (F-11 제거)**
- 클라우드 배포·다중 사용자·계정 인증
- SSE/WebSocket 이벤트 스트리밍
- Canvas 렌더링 (SVG 사용)
- 컴포넌트 Python 클래스 등록 UI (스텁 실행만)
- 이벤트 축약(프로젝션) 포맷 — 원본 v1 로그 스키마 전달 (대용량 최적화는 후속)
- 데스크톱 앱 (v3로 연기)
- 실시간 실행 진행률 UI — v1 성능 목표로 실행이 수 초 내 완료 (동기 실행)

## Open Questions
- (없음 — 생성 차단 사항 없음. F-2는 `arch_content` 단일 액션으로 해소, F-4는 arch 페어링으로 해소, F-5는 고정 펄스 근사로 해소, F-7~F-10은 상기 인코딩으로 해소 완료)

## Related
- `{project-root}/spec/PRD.md` — 상위 제품 요구사항
- `{project-root}/spec/sdv-sim-v1.md` — v1 코어·CLI 스펙 (재사용 대상, 계약 원천 — D-15 `loads()` 추가로 갱신)
- `{project-root}/spec/ASR.md` — ASR-006·014~020
- `{project-root}/adr/` — ADR 13건 (core-yaml-string-input, dashboard-browser-file-access, dashboard-layout-placement-rule 포함) — 결정 근거 (참고용, 생성에 필수 아님)

## Tags
`sdv-simulator`, `dashboard`, `web`, `fastapi`, `react`, `replay`, `v2`
