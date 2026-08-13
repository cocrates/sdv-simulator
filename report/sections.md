# Section Design: SDV Simulator 구조 설계서

> 문서 루트: `report/overview.md`, `report/outline.md` 참조
> 날짜: 2026-08-13
> 작성 순서(의존성): 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13 → 부록 A → B → C → D

---

## Section 1: 서론

- **제목**: 1. 서론
- **목적(Purpose)**: 평가자가 이 문서를 읽을 준비를 갖추게 한다 — 무엇을 설명하는 문서인지, 어떤 배경의 과제인지, 어떻게 구성되었는지.
- **핵심 메시지(Key message)**: 이 문서는 sdv-simulator의 "최종 구조"를 동작(flow)과 구조(모듈·확장성) 중심으로 설명하는 과제 제출용 구조 설계서이며, 결정의 근거는 부록에 있다.
- **내용 요소(Content elements)**:
  - 문서 목적·독자·범위 (overview.md 요약) + 본문/부록 역할 분담 안내
  - 과제 배경: SDV 개념(기능이 SW로 정의되는 차량), 하드웨어 없이 E/E 아키텍처를 정의→실행→검증할 필요성
  - 버전 체계: v1(코어+CLI) → v2(웹 대시보드) → v3(데스크톱, 예정), 제공 형태 3종이 단일 코어 공유
- **서브섹션**:
  - 1.1 문서 목적과 구성 — 문서 목적/독자/범위/구성 안내
  - 1.2 과제 배경: SDV와 차량 SW 시뮬레이션 — SDV 정의, 시뮬레이션 필요성, 과제 요구
  - 1.3 버전 체계와 제공 형태 — v1/v2/v3 로드맵, 단일 코어 원칙 예고
- **의존성**: 없음
- **예상 분량**: 1.5~2p
- **톤/스타일**: 공식적이고 간결한 보고서 톤, 과제 맥락에 익숙하지 않은 독자도 배경을 이해하도록 서술.

## Section 2: 시스템 개요

- **제목**: 2. 시스템 개요
- **목적**: 전체 시스템의 한눈 구조(지도) 제공 — 이후 모든 섹션이 이 그림의 부분으로 읽히게 한다.
- **핵심 메시지**: sdv-simulator는 "코어 엔진 1개 + 여러 제공 형태(CLI/대시보드) + 배포"로 구성되며, 모든 형태가 동일한 코어를 공유한다.
- **내용 요소**:
  - 시스템 목표(정의→실행→검증)와 주요 기능 표 (통신 시뮬레이션·앱 런타임·자동 검증)
  - **D1 전체 계층도 (Mermaid flowchart)** — 사용자 접점(CLI/브라우저) → 제공 계층(cli/server/frontend) → 코어(core/schema) → 실행 환경
  - 구성 요소와 기술 스택 표 (Python 3.11+, Pydantic, FastAPI, React/TS/Vite, hatchling, systemd)
  - 주요 설계 특성 4가지 — 최종 설계 사실로 서술, 근거는 부록 C/D 참조 표기: ① 결정성(이벤트 (t_ms, seq) 완전 순서) ② 단일 코어 공유 ③ 헤드리스/CI(종료 코드·JSON 로그) ④ 브라우저 파일 경계(서버 FS 비접촉)
- **서브섹션**:
  - 2.1 시스템 목표와 주요 기능
  - 2.2 전체 구조 (D1)
  - 2.3 구성 요소와 기술 스택
  - 2.4 주요 설계 특성
- **의존성**: 1
- **예상 분량**: 2.5~3p
- **톤/스타일**: 그림 중심의 개관. 표와 다이어그램으로 압축.

## Section 3: 정의 형식 개요 — 도메인 모델

- **제목**: 3. 정의 형식 개요
- **목적**: 시스템 입력 언어(architecture.yaml/scenario.yaml)의 개념 지도를 제공해 이후 동작 설명의 어휘를 확보한다.
- **핵심 메시지**: 입력은 "구조(architecture) + 시나리오(scenario)" 2개 YAML로 분리되며, 도메인은 노드/컴포넌트/태스크, 링크/프레임, 게이트웨이, 주입/assertion으로 구성된다.
- **내용 요소**:
  - 도메인 개념 설명: 노드(ECU/HPC)와 컴포넌트(메시지 송수신·주기 태스크), 링크(CAN/Ethernet)와 프레임(L2, ID/DLC/period/source), 게이트웨이(라우트), 시나리오(주입·assertion)
  - **D2 도메인 모델 (Mermaid classDiagram)** — Architecture → nodes/links/gateways, Scenario → messages/assertions
  - 메시지-프레임 매핑 규칙 (message 필드 또는 동일 이름)
  - 스키마 검증이 하는 일: Pydantic 모델 + 유일성/참조 무결성(링크 노드 존재, 프레임 source 연결, 라우트 참조, sends/receives 매핑)
  - 필드 단위 상세는 **부록 A** 참조 명시
- **서브섹션**:
  - 3.1 아키텍처 정의 (architecture.yaml) — 도메인 모델 중심
  - 3.2 시나리오 정의 (scenario.yaml) — duration/messages/assertions
  - 3.3 스키마 검증 규칙 — Pydantic, 유일성, 참조 무결성
- **의존성**: 2
- **예상 분량**: 2.5~3p
- **톤/스타일**: 사전/어휘집 스타일 — 정의 위주, 필드 표는 최소화(부록 참조).

## Section 4: 코어 시뮬레이션 엔진 ★

- **제목**: 4. 코어 시뮬레이션 엔진
- **목적**: 프로젝트 심장부의 **동작**을 가장 깊이 있게 설명 — 시뮬레이션이 어떻게 진행되는지.
- **핵심 메시지**: 코어는 "결정적 이산 사건(DES) 엔진"이다 — 정수 ms 시간 위에서 이벤트를 `(t_ms, priority, decl, seq)` 완전 순서로 처리하며, 같은 시각의 통신·태스크·게이트웨이 동작이 모두 이 순서 규칙으로 재현된다.
- **내용 요소**:
  - 4.1 엔진 동작 모델: 이벤트 큐(heap) 기반 DES, tick별 일괄 처리, 종료 경계(duration_ms 포함), 이벤트 순서 규칙(D-19: priority → decl → seq; 비-태스크는 가상 우선순위 2^30), 결정성(난수 없음)
  - 4.2 런타임 구조: **D3 (Mermaid classDiagram)** — Simulator(엔진 루트)가 소유: NodeRuntime/ComponentRuntime/LinkRuntime/TaskRuntime/Attempt; 공개 팩토리 `load()`/`loads()`, `SimulationResult`
  - 4.3 실행 루프: **D4 (Mermaid sequenceDiagram)** — run() 초기화(스케줄) → tick 이벤트 처리(task_start/task_end/tx_attempt/rx/link_service) → tick 후 link.drain() 배치 해소 → duration 도달 시 정렬·assertion·리포트
  - 4.4 통신 동작: **D5 (Mermaid flowchart/stateDiagram)** — CAN: tx_ms=ceil((44+8·DLC)/bitrate), ID 작을수록 중재 우선, 버스 점유 시 큐 대기; Ethernet: bytes=dlc+42, tx_ms 공식, 단일 스위치 FIFO, queue_depth 테일 드롭, 동일 프레임 supersede(D-18)
  - 4.5 게이트웨이 라우팅: **D6 (Mermaid flowchart)** — 매칭 우선순위(명시 frame > ID 범위), remap_id·delay_ms, 홉 제한(MAX_HOPS=8) 초과 시 drop
  - 4.6 앱 런타임: 주기 태스크(절대 주기) 비선점 실행, wcet_ms, 오버런 감지·다음 인스턴스 스킵(D-17), 컴포넌트 API(Component.on_periodic/on_message, TaskContext.send/log), 미등록 시 수신 전용 스텁(D-14)
  - 4.7 검증·자동화: assertion 매칭(이벤트 7종, count ≥ n, at_ms ± within_ms, event:task는 start+end), 이벤트 로그 스키마(schema_version/events/assertions), 리포트 생성(Report/LinkReport/TaskReport)
- **서브섹션**: 4.1~4.7 (위 참조)
- **의존성**: 3 (도메인 개념 전제)
- **예상 분량**: 6~8p — 문서에서 가장 김
- **톤/스타일**: 동작 중심 서술 — "어떻게 실행되는가"의 순서와 규칙. 다이어그램(D3~D6) 4개. 코드 식별자는 코드 폰트로 유지.

## Section 5: CLI

- **제목**: 5. CLI (Command-Line Interface)
- **목적**: 코어를 감싸는 1차 제공 형태의 동작(사용법·계약) 설명.
- **핵심 메시지**: `sdv-sim run`은 파일 입력 → 코어 실행 → JSON 로그 + 요약 → 종료 코드 0/1/2/3의 자동화 계약을 제공한다.
- **내용 요소**:
  - 명령 구조: `run`/`serve` 하위 명령, 옵션(--log, --quiet, --lang, --port, --host, --dev)
  - 실행 흐름: load() → run() → _write_json_log → 요약 출력 → 종료 코드
  - 입출력 계약: 로그는 --log 경로(기본 events.json) 또는 stdout(-), --quiet로 요약 생략
  - 종료 코드 의미: 0 pass / 1 assertion fail / 2 입력·리소스 오류 / 3 내부 오류
  - i18n: --lang > SDV_SIM_LANG env > 시스템 로케일(→ko), 메시지 코드 체계(SdvSimInputError.code + tr())
- **서브섹션**:
  - 5.1 명령 구조와 옵션
  - 5.2 실행 흐름과 입출력 계약
  - 5.3 종료 코드와 오류 처리
  - 5.4 i18n 체계
- **의존성**: 4 (코어 공개 API 사용)
- **예상 분량**: 1.5~2p
- **톤/스타일**: 실용적 레퍼런스 톤 — 명령·표 중심.

## Section 6: 대시보드 서버

- **제목**: 6. 대시보드 서버
- **목적**: v2 백엔드(FastAPI)의 구조와 API 동작을 설명 — 브라우저와 코어 사이의 계약.
- **핵심 메시지**: 서버는 "검증·실행·세션"을 담당하는 얇은 API 계층이다 — 파일 시스템에 닿지 않고(YAML/JSON 문자열 수신), 단일 세션(last-write-wins)을 유지하며, F-8 오류 계약으로 모든 오류를 일관되게 반환한다.
- **내용 요소**:
  - 서버 구조: create_app() 팩토리, Session/SessionStore(단일 전역 세션), 정적 자산 마운트, --dev 프록시
  - **D7 API 5종 동작 (Mermaid flowchart)** + 명세표: validate(순수 검증, 세션 무효화 없음 — T-024), run(loads()+run, 세션 교체), load-log(파싱·검증·리포트 파생, 세션 교체), events(정렬된 이벤트), report(현재 리포트); GET 계열은 세션 없으면 409
  - 오류 계약: {error: {code, message, detail?}} — codes: validation_error/log_invalid/session_invalid/not_found/internal
  - 세션 수명주기: run/load-log 교체, 편집 시 프런트 로컬 무효화(invalidated), 409 응답
  - 로그 로드·리포트 파생 규칙(M-1): 이벤트만으로 파생 가능(링크 tx/rx/drop, 태스크 run/overrun, assertion) / arch 필요(kind·bus_load·period_ms) / 불가(supersede_count·warnings)
- **서브섹션**:
  - 6.1 서버 구조
  - 6.2 API 5종 (D7)
  - 6.3 오류 계약
  - 6.4 세션 수명주기
  - 6.5 로그 로드·리포트 파생 (M-1)
- **의존성**: 4, 5
- **예상 분량**: 3~4p
- **톤/스타일**: API 레퍼런스 + 동작 흐름 혼합. 엔드포인트 표와 오류 코드 표 활용.

## Section 7: 프런트엔드

- **제목**: 7. 프런트엔드
- **목적**: v2 UI(React/TS/Vite)의 구조와 핵심 동작(구조 뷰·리플레이·파일 접근·검증 피드백) 설명.
- **핵심 메시지**: 프런트엔드는 "서버는 검증·실행 권위, 브라우저는 파일 소유자"라는 경계 위에서, 결정적 레이아웃과 스냅샷 시크 인덱싱으로 구조 뷰·리플레이를 구현한다.
- **내용 요소**:
  - 7.1 모듈 구조: src/ 파일 맵과 역할(api/client, fileManager, layout, replay/, i18n/, useValidation, StructureView, EditorPane, EventPanel, ReportView/Panel, App)
  - 7.2 상태 관리·라우팅: App.tsx 소유 상태(EditorFile 2개, SessionMeta, 최근 파일), hash 라우팅(#/editor, #/replay, #/report)
  - 7.3 구조 뷰: SVG 렌더링, 타입 밴드 레이아웃(HPC→Gateway→ECU, 링크 수 desc→이름 asc), 결정성(같은 입력=같은 좌표), CAN/Ethernet 시각 구분
  - 7.4 리플레이 ★: **D8 (Mermaid sequenceDiagram)** — 이벤트 로드→스냅샷 인덱스(K=2000)→seekToTime(이분 탐색+잔여 재적용)→advanceToTime(증분)→오버레이(비행 프레임·노드 하이라이트·드롭/오버런 신호); 물리 모드(tx_ms 재현) vs 펄스 모드(근사, 300ms 고정); useReplayClock(rAF, 배속)
  - 7.5 파일 접근: FS Access API(같은 파일 저장) + input file/Blob 다운로드 폴백, IndexedDB 최근 파일(20개), 서버 FS 미접촉
  - 7.6 검증 피드백: useValidation(500ms 디바운스, stale 응답 가드, forceValidate), 줄 단위 오류 표시, 유효할 때만 다이어그램 동기화
  - 7.7 i18n: window.__SDV_SIM_LANG__ 주입 > localStorage 선택 > 브라우저 로케일 > ko
- **서브섹션**: 7.1~7.7 (위 참조)
- **의존성**: 6
- **예상 분량**: 5~7p
- **톤/스타일**: 컴포넌트 동작 중심. 7.4는 시퀀스 다이어그램과 함께 상세 서술.

## Section 8: 핵심 데이터 흐름 ★

- **제목**: 8. 핵심 데이터 흐름
- **목적**: 4·6·7장의 구성 요소를 하나로 묶어 "전체 시스템이 어떻게 움직이는지" 통합 시퀀스로 제시.
- **핵심 메시지**: 편집→검증→실행→세션 교체→조회→리플레이라는 단일 흐름과, 로그 파일 로드라는 두 번째 진입 흐름이 존재하며, 모든 데이터는 문자열/JSON으로 서버를 통과한다.
- **내용 요소**:
  - 8.1 run 경로: **D9 (Mermaid sequenceDiagram)** — 브라우저 파일 열기 → 편집(자동 검증) → run 클릭(forceValidate) → POST /api/run(loads+run) → 세션 교체 → GET /api/events·/api/report → 리플레이/리포트 뷰
  - 8.2 load-log 경로: **D10 (Mermaid sequenceDiagram)** — 브라우저 events.json 선택 → POST /api/load-log(+arch_content 선택) → 파싱·검증 → 세션 교체 → 리포트 파생 → 리플레이
  - 8.3 재생·시크 흐름: 이벤트 정렬 → 인덱스 → 시크/재생 → 오버레이 갱신 (7.4와 연결)
- **서브섹션**: 8.1~8.3
- **의존성**: 4, 6, 7
- **예상 분량**: 2~3p
- **톤/스타일**: 통합 내러티브 — 다이어그램 위주, 각 단계가 "어느 모듈의 어떤 동작"인지 교차 참조.

## Section 9: 모듈 의존성과 확장·변경 반영 ★

- **제목**: 9. 모듈 의존성과 확장·변경 반영
- **목적**: "개발 측면" 초점 — 모듈 간 의존성 방향과, 확장/변경 요구가 구조에 어떻게 반영되는지 설명.
- **핵심 메시지**: 의존성은 "core ← (cli, server) ← frontend(API 계약)"의 단방향이며, 확장은 코어 변경 없이 계층 추가(컴포넌트 등록·새 아티팩트)로 이루어진다.
- **내용 요소**:
  - 9.1 모듈 의존성: **D11 (Mermaid flowchart)** — sdv_sim.core(무의존, schema 타입만 사용), schema(외부 의존: pydantic), cli→core, server→core+schema, frontend→서버 API 계약(HTTP), tests→core, deploy→cli; core가 cli/server에 역의존하지 않는 규칙과 이유(재사용 경계)
  - 9.2 확장 지점: ① 커스텀 컴포넌트(components= 등록, 클래스 키 매칭) ② 새 링크 종류/라우트/assertion(스키마+엔진 확장 지점) ③ v2 추가(v1 코어 무변경: loads() 문자열 API 추가만으로 대시보드 재사용) ④ v3 데스크톱 예정 경계(같은 코어+API)
  - 9.3 변경 요구 반영 사례: F-11 방향 전환(--root 서버 샌드박스 제거 → 브라우저 파일 접근; core-yaml-string-input loads() 추가 — 기존 load() 계약 하위 호환 유지), serve-network-binding(--host 추가, 기본 127.0.0.1), T-024(세션 무효화를 서버 API에서 프런트 로컬 상태로 이동 — validate 순수화) — 요구가 "코어 계약 보존 + 계층 추가"로 흡수된 방식
- **서브섹션**: 9.1~9.3
- **의존성**: 1~8 (전체 종합)
- **예상 분량**: 3~4p
- **톤/스타일**: 개발자 관점 — 의존성 방향·계약·변경 사례 중심.

## Section 10: 배포

- **제목**: 10. 배포
- **목적**: 실제 실행 환경 구조 설명.
- **핵심 메시지**: 단일 패키지(sdv-sim wheel, 프런트 정적 자산 포함)가 단일 프로세스 서버(sd-sim serve)와 systemd 서비스로 배포된다.
- **내용 요소**:
  - 10.1 패키징: hatchling, wheel에 sdv_sim/server/static 강제 포함(빌드 오류로 누락 방지), dist 생성
  - 10.2 serve 실행 모델: 단일 프로세스(FastAPI+정적 자산), --dev Vite 프록시, 포트 사전 바인딩(점유 시 exit 2), --host 바인딩(기본 127.0.0.1, 0.0.0.0 경고)
  - 10.3 systemd: deploy/sdv-simulator.service(Restart=always, %h 경로, --host 0.0.0.0, SDV_SIM_LANG=ko), install.sh/uninstall.sh, 실제 설치는 보류 상태
- **서브섹션**: 10.1~10.3
- **의존성**: 4, 6
- **예상 분량**: 1.5~2p
- **톤/스타일**: 사실 중심 — 파일/명령 예시 포함.

## Section 11: 검증과 품질

- **제목**: 11. 검증과 품질
- **목적**: 구조가 품질을 어떻게 보장하는지 — 테스트/타입/검증 스크립트 체계.
- **핵심 메시지**: 백엔드는 pytest(78건)+mypy strict, 프런트엔드는 순수 로직(Node 실행 가능) 검증 스크립트, 샘플 2종이 실행 검증을 담당한다.
- **내용 요소**:
  - 11.1 백엔드: pytest 단위 테스트(78 passed), mypy strict(13개 소스), uvicorn/httpx 테스트
  - 11.2 프런트: scripts/check-layout.ts(좌표 결정성), check-replay.ts(시크==전체 재스캔), check-files.ts(파일 존재)
  - 11.3 샘플: samples/basic(assertion 5건), samples/vehicle(assertion 9건 — drop/overrun/supersede 관찰), components.py(커스텀 컴포넌트 API)
- **서브섹션**: 11.1~11.3
- **의존성**: 4, 7
- **예상 분량**: 1~2p
- **톤/스타일**: 표/명령 중심의 간결한 레퍼런스.

## Section 12: 향후 방향

- **제목**: 12. 향후 방향
- **목적**: 현재 구조가 어디로 확장될 수 있는지 표시 (상세 제외).
- **핵심 메시지**: 코어 계약을 유지한 채 v3 데스크톱·OTA·다중 스위치 등이 계층 추가로 확장 가능하다.
- **내용 요소**: v3 데스크톱 셸, OTA(캠페인·버전·배포), Ethernet 다중 스위치, 구조화 폼/드래그 편집 후보 — 각각 9.2의 확장 지점과 연결.
- **서브섹션**: 없음 (단일 흐름)
- **의존성**: 9
- **예상 분량**: 0.5~1p
- **톤/스타일**: 짧고 전망적인 서술.

## Section 13: 결론

- **제목**: 13. 결론
- **목적**: 문서 요약 + 검증 기준(overview.md 4가지) 관점의 자체 점검.
- **핵심 메시지**: 결정적 코어 + 계층형 제공 형태 구조가 "정의→실행→검증" 목표를 단일 코어 공유로 달성한다.
- **내용 요소**: 구조 요약(코어/CLI/서버/프런트/배포), 설계 특성 4가지 재확인, 검증 기준 4가지(구조 파악·핵심 설계 설명력·정합성·설계 근거)에 대한 충족 근거 — 각 항목이 문서 어느 장에서 충족되는지 교차 참조.
- **서브섹션**: 없음
- **의존성**: 전체
- **예상 분량**: 1~1.5p
- **톤/스타일**: 정리·확언 — 새로운 내용 없음.

## 부록 A: SDV 정의 — SDV를 위한 YAML 사양

- **제목**: 부록 A. SDV 정의 — YAML 사양
- **목적**: 입력 언어의 완전한 필드 사양 제공 (본문 3장의 상세판).
- **핵심 메시지**: architecture.yaml/scenario.yaml의 모든 필드·제약·예시가 이 부록에 정의된다.
- **내용 요소**:
  - A.1 architecture.yaml: 최상위(schema_version/nodes/links/gateways), 노드(ECU/HPC, components), 컴포넌트(sends/receives/tasks/class), 태스크(period_ms/priority/wcet_ms), 링크(kind/bitrate/nodes/frames/switches), 프레임(name/id/dlc/period_ms/source/message), 게이트웨이(routes: from/to/delay_ms, id_min/id_max/remap_id) — 필드 표(이름·타입·필수·설명·제약)
  - A.2 scenario.yaml: duration_ms, messages(주입: t_ms/link/frame/data), assertions(expect: event/속성/at_ms/within_ms/count) — 필드 표 + 예시
  - A.3 검증 규칙 상세: 유일성(노드·링크·게이트웨이·프레임·컴포넌트), 참조 무결성(링크 노드, 프레임 source, 라우트, sends/receives 매핑), 메시지-프레임 매핑
  - A.4 예시: samples/basic 축약 예제
- **서브섹션**: A.1~A.4
- **의존성**: 3 (개념), 코드(schema/arch.py, scenario.py), spec/sdv-sim-v1.md 정의 절
- **예상 분량**: 5~8p
- **톤/스타일**: 사양서 — 필드 표 중심, 코드·YAML 예시 블록.

## 부록 B: sdv-simulator 사양 요약 (spec v1/v2)

- **제목**: 부록 B. sdv-simulator 사양 요약
- **목적**: 본문이 인용하는 Spec(D-번호/F-번호 등)의 집합을 요약해 근거를 확인할 수 있게 한다.
- **핵심 메시지**: v1(코어·통신·런타임·검증·API·CLI)과 v2(대시보드 기능·API·리플레이·파일 접근)의 핵심 요구사항이 각각 spec/sdv-sim-v1.md, spec/sdv-sim-v2.md에 정의되어 있다.
- **내용 요소**:
  - B.1 v1 요약: 엔진·시간 모델·통신 충실도(CAN/Ethernet)·앱 런타임·정의 형식·검증·공개 API·CLI — D-번호별 핵심 요구 1줄 요약
  - B.2 v2 요약: 대시보드 동작 방식·API 5종·리플레이·파일 접근·편집 검증 — F-번호/M-번호별 핵심 요구 1줄 요약
  - B.3 인용 매핑 표: 본문 장 ↔ 참조 D/F/M 번호 ↔ spec 파일/절
- **서브섹션**: B.1~B.3
- **의존성**: 4~8 (본문), spec/sdv-sim-v1.md, spec/sdv-sim-v2.md
- **예상 분량**: 3~5p
- **톤/스타일**: 요약 표 중심 — 원문 재생산 아님.

## 부록 C: 설계 및 개발 과정

- **제목**: 부록 C. 설계 및 개발 과정 (PRD → ASR → ADR → Spec → 구현 → 검증)
- **목적**: 프로젝트가 어떤 과정으로 설계·개발되었는지, 산출물(PRD/ASR/ADR/Spec)이 무엇인지 설명 — 본문의 "최종 설계" 도출 배경.
- **핵심 메시지**: 이 프로젝트는 spec-driven 개발로, PRD → ASR 식별 → ADR 검토·결정 → Spec 인코딩 → 구현 → 검증이 반복 루프로 진행되었고, 검증에서 발견된 미문서화 요구가 다시 ASR/ADR/Spec으로 정식화되었다.
- **내용 요소**:
  - C.1 단계 파이프라인 개요: PRD → ASR → ADR → Spec → 구현 → 검증 (흐름도, 피드백 루프)
  - C.2 산출물 개념: PRD(제품 요구사항·목표/범위/성공 기준), ASR(아키텍처 중요 요구사항 등록부), ADR(결정 레코드 — 대안·트레이드오프·결정·결과), Spec(결정 통합 실행 사양) — 각각의 역할·내용·상태
  - C.3 단계별 활동: v1 진행(ASR 1~13, 3차 ADR 배치, 검증 발굴 ADR U-1~U-6), v2 진행(PRD v2 → ASR 14~20 → F-11 방향 전환 → T-024 재설계), 검증 반복(verification/) — 실제 활동 요약 (prompts.md/TODO 기준 요약·개념화)
  - C.4 사용자 개입 지점: 승인 게이트, 방향 전환 결정(F-11), 실제 설치 보류 등
- **서브섹션**: C.1~C.4
- **의존성**: 2 (구조 이해 전제), 자료: prompts.md, TODO-v1/v2.md, spec/, adr/, verification/
- **예상 분량**: 3~5p
- **톤/스타일**: 과정 설명 — 진행 로그 재생산이 아닌 단계·개념·사례 중심.

## 부록 D: ASR & ADR — ASR별 ADR 검토 및 결정 내역

- **제목**: 부록 D. ASR & ADR — 옵션 비교와 결정 근거
- **목적**: "왜 이렇게 설계했는가"의 근거 저장소 — 본문의 설계 사실을 결정 기록과 연결
- **핵심 메시지**: 21개 ASR 각각에 대해 **옵션 간 장/단점 분석 테이블**과 **결정된 option·결정 근거**를 명확히 제시한다. 상세 서술은 지양하고 표 중심으로 작성한다.
- **내용 요소**:
  - D.1 ASR-ADR 요약표: ASR ID·제목·카테고리·상태·관련 ADR 수·**결정 요약**
  - D.2 ASR별 상세 소절(001~021): 각 소절은 ADR별로 다음 순서로만 구성
    1. **옵션 비교 테이블**: `옵션 | 개요 | 장점 | 단점` 4열 — 관련 ADR의 옵션들을 표로 제시
    2. **결정(Decision)**: 표 **하단**에 기술 — 선택된 option과 결정 내용 1~3줄
    3. **결정 근거(Rationale)**: 표 하단에 결정 아래 기술 — 선택 이유 1~2줄 (트레이드오프의 승리 차원 명시)
    - **결정 옵션 색상 표시**: 채택된 옵션 행은 옵션명을 초록색(`#1a7f37`)+굵게 표시 — 표에서 즉시 식별
    - 공유 ADR(communication-event-semantics, result-report-schema, component-api, public-api-contract, cli-output-policy, cli-io-contract, core-yaml-string-input, dashboard-browser-file-access 등)은 최초 소절에 전체 테이블을 두고, 이후 소절에서는 "결정 옵션 + 근거"만 표 하단 형식으로 기술하고 원 테이블을 참조
    - superseded ADR(dashboard-run-path)은 표 안에 "⚠ superseded — 대체 ADR" 표기
  - D.3 의존성 경로: ASR 의존 순서 요약 (ASR.md의 Dependency Order 재인용)
- **서브섹션**: D.1~D.3 (D.2는 ASR별 ## 소절)
- **의존성**: 3~10 (본문), spec/ASR.md, adr/*.md (49건)
- **예상 분량**: 5~8p
- **톤/스타일**: 결정 레지스트리 — 표 중심, 서술 최소화. 각 표에서 결정 옵션이 즉시 식별되도록 강조.

---

## 공통 작성 규칙

- 언어: 한국어 본문, 코드 식별자·타입·파일명·명령은 원어(코드 폰트) 유지
- 다이어그램: 전부 Mermaid 코드 블록 (D1~D11 — outline의 표 참조)
- ADR/ASR/스펙 참조 형식: `(ADR: <파일명>)`, `(spec/sdv-sim-v1.md D-15)` 등으로 본문 내 인용, 상세는 부록 참조
- 본문에서 "왜"의 서술은 피하고 "어떻게/무엇" 중심 — 근거는 부록 C/D 참조 표기만
- 모든 D-번호/F-번호/M-번호는 부록 B의 인용 매핑과 일치해야 함
