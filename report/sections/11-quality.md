# 11. 검증과 품질

구조가 의도대로 동작함을 보장하는 검증 체계는 **백엔드 테스트 + 프런트 로직 검증 스크립트 +
샘플 실행**의 세 축으로 구성된다.

## 11.1 백엔드: pytest + mypy strict

- **pytest**: `tests/`에 **113개 테스트**가 있으며 전부 통과한다. 엔진 동작별로 분리되어 있다.

  | 파일 | 대상 |
  |------|------|
  | `test_can.py` / `test_ethernet.py` | 통신 동작 — 전송 시간·중재·큐잉·supersede·테일 드롭 (4.4절) |
  | `test_gateway.py` | 게이트웨이 라우팅·홉 제한 (4.5절) |
  | `test_tasks.py` | 태스크 스케줄링·오버런 (4.6절) |
  | `test_assertions.py` | assertion 평가 규칙 (4.7절) |
  | `test_schema.py` | 스키마 검증 — 필드 제약·유일성·참조 무결성 (3.3절) |
  | `test_cli.py` | CLI 명령·종료 코드·로그 계약 (5장) |
  | `test_api.py` / `test_server.py` | 서버 API 5종·세션·오류 계약 (6장) — FastAPI TestClient 사용 |
  | `test_string_input.py` | `loads()` 문자열 입력 계약 (4.2절) |
  | `test_i18n.py` | 메시지 번역·언어 결정 (5.4절) |

- **mypy strict**: `[tool.mypy] strict = true, files = ["sdv_sim"]` — 코어·CLI·서버 전체가
  strict 타입 검사를 통과해야 한다. 이벤트/리포트/API 응답 타입이 계약으로 강제된다.
- 결정성(2.4절 ①) 덕분에 테스트는 시간·순서에 대해 **결정적인 기대값**을 assert할 수 있다.

## 11.2 프런트: 순수 로직 검증 스크립트

프런트의 뷰 로직은 브라우저 테스트 러너 없이 **Node로 실행되는 검증 스크립트**로 검증한다
(React에 의존하지 않는 순수 모듈 분리 — 7.1절).

| 스크립트 | 검증 내용 |
|----------|-----------|
| `check-layout.ts` | 구조 뷰 레이아웃 **결정성** — 같은 아키텍처 입력이 항상 같은 좌표를 만든다 (7.3절) |
| `check-replay.ts` | 리플레이 **시크 정확성** — 스냅샷 인덱스 기반 시크 결과가 전체 이벤트 재스캔 결과와 일치한다 (7.4절) |
| `check-files.ts` | 배포 필수 파일 존재 — `frontend/dist/`와 `sdv_sim/server/static/` 동기화 상태 (10.1절) |

이 구조 덕분에 리플레이 시크(대형 로그 성능의 핵심)와 레이아웃 결정성을 브라우저 없이
CI에서 회귀 검증할 수 있다.

## 11.3 샘플 실행 검증

`sample/`에 포함된 두 예제가 실행 검증(integration) 역할을 한다.

| 샘플 | 내용 |
|------|------|
| `samples/basic` | 소형 아키텍처 — **assertion 5건**: CAN 프레임 주기 전송·수신, 중재 우선순위, 태스크 실행 |
| `samples/vehicle` | 차량형 아키텍처 — **assertion 9건**: CAN 중재(door/seat), Ethernet 전송·수신, **드롭·오버런·supersede 관찰**, 사용자 정의 컴포넌트(`components.py`) 포함 |

- `components.py`는 4.6절의 Component API(`on_periodic`/`on_message`/`TaskContext.send`)의
  실제 사용 예이다.
- 두 샘플 모두 `sdv-sim run`이 종료 코드 0(pass)으로 끝나는 것이 수동 검증 경로이며,
  각 assertion은 drop/overrun/supersede 같은 고급 동작까지 예상 시각·횟수로 명시한다.
