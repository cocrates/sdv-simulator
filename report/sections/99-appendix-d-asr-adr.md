# 부록 D. ASR & ADR — 옵션 비교와 결정 근거

- **범위**: 21개 ASR × 관련 ADR 49건의 결정 내역
- **표기 규칙**: 각 표에서 <b style="color:#1a7f37;">초록색 굵은 옵션명</b> = 채택된 옵션. **결정(Decision)**과 **결정 근거(Rationale)**는 해당 표 **하단**에 기술.
- **공유 ADR**은 최초 소절에 전체 표, 이후 소절에는 결정·근거만 기술하고 원 표를 참조.

## D.1 ASR-ADR 요약표

| ID | 제목 | 카테고리 | 상태 | 관련 ADR | 결정 요약 |
|----|------|----------|------|----------|-----------|
| ASR-001 | 언어/기술 스택 | Constraints & Integration | approved | 2 | Python 3.11+ (mypy strict), v1 순수 Python + 명시적 목표 규모 |
| ASR-002 | 시뮬레이션 엔진 모델 | Structure & Organization | approved | 5 | DES + 주기 태스크 하이브리드, 정수 ms + (t_ms, seq), 수신자 매핑 rx, 전체 로그 count, 구조화 리포트 |
| ASR-003 | 아키텍처/시나리오 정의 형식 | Structure & Organization | approved | 3 | YAML, 메시지-프레임 2계층 + 매핑 규칙, 명시적 완전 스키마 + 공식 예시 |
| ASR-004 | 통신 프로토콜 충실도 | Structure & Organization | approved | 7 | L2(프레임/버스), CAN 비트 수식+ID 중재, Ethernet 스위치 FIFO, 명시 라우팅, 최신 교체 |
| ASR-005 | 앱 런타임 모델 | Structure & Organization | approved | 6 | RTE 스타일(주기 태스크+이벤트 핸들러), 비선점+wcet, 베이스 클래스 API, 스텁 수신자 전용, 절대 주기+스킵 |
| ASR-006 | 코어 API 경계 & 다중 아티팩트 구조 | Deliverable form & Structure | designed | 6 | 단일 패키지+모듈 경계, 4채널 IO, --lang+0/1/2/3, loads() 계열 추가(F-11) |
| ASR-007 | 검증·자동화 지원 | Quality bar | approved | 7 | 선언형 assertion+JSON 스트림, 전체 count+시간 무관, 단일 JSON 로그 |
| ASR-008 | 동일 시각 비-태스크 이벤트 순서 | Structure & Organization | designed | 1 | 비-태스크는 모든 태스크 뒤 (가상 우선순위 2^30) |
| ASR-009 | Ethernet 스위치 다중 정의 정책 | Structure & Organization | designed | 1 | 첫 항목만 사용, 스키마 오류 없음 |
| ASR-010 | 로그 쓰기 실패 종료 코드 | Quality bar | designed | 1 | exit 2 (입력/파일 오류로 분류) |
| ASR-011 | Assertion `event: task` 매칭 범위 | Quality bar | designed | 1 | task_start+task_end 둘 다 매칭 |
| ASR-012 | Assertion count 비교 연산 | Quality bar | designed | 1 | 최소 n건 이상 (≥) |
| ASR-013 | Ethernet payload 크기 기준 | Structure & Organization | designed | 1 | 프레임 DLC 기준 (bytes = dlc + 42) |
| ASR-014 | 대시보드 기술 스택 | Constraints & Integration | approved | 1 | FastAPI + React/TS + Vite |
| ASR-015 | 데이터 흐름·리플레이 모델 | Structure & Organization | approved | 6 | 코어 임베드+일괄 JSON, F-11 후 loads() 경로, 스냅샷 세션+무효화, 파생 가능 리포트만 |
| ASR-016 | 구조 뷰 렌더링·성능 | Structure & Organization | approved | 5 | SVG+React(D3 보조), 물리 재생+폴백, 스냅샷+재적용, 결정성, 타입 밴드 배치 |
| ASR-017 | 파일시스템 접근·보안 경계 | Constraints | approved | 1 | 브라우저 권한 경계 — 하이브리드(FS Access + 업로드/다운로드), 서버 파일 API 제거 |
| ASR-018 | 편집·검증 피드백 | Quality bar | approved | 1 | 서버 Pydantic 검증(v1 스키마 재사용) + 500ms 디바운스 |
| ASR-019 | 패키지 통합·서버 명령 (serve) | Deliverable form | designed | 3 | 단일 프로세스+패키지 내부 정적 자산, --root 제거, --host 옵션(기본 127.0.0.1) |
| ASR-020 | UI 언어 지원 (ko/en) | Constraints | approved | 0 (direct-input) | 프런트 i18n 카탈로그, v1 우선순위 패턴 대응 |
| ASR-021 | 상시 실행 서비스 등록 (deploy) | Integration & dependencies | approved | 0 (direct-input) | systemd user unit + install/uninstall (설치 보류) |

## D.2 ASR별 상세

### ASR-001 — 언어/기술 스택

**언어/기술 스택 (adr/language-tech-stack.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. Python</b> | 고수준 언어, 타입 힌트+mypy로 안전성 보완 | 생산성 최고, 자동차 테스트 에코(python-can) 친화, 임베드·테스트 하네스 자연스러움 | CPU 집약 시뮬레이션 성능 제한, 런타임 의존 |
| B. TypeScript/Node | 타입 안정성 갖춘 웹 생태계 | v2 대시보드와 동일 언어, 타입 안정, npm 생태계 | 시뮬레이션 성능 불리, 차량 SW 청중 친화성 낮음, Node 의존 |
| C. Go | 간결·단일 바이너리 | 성능·생산성 균형, CI/자동화 친화 | CAN/Ethernet 도메인 에코 부족 |
| D. Rust | 시스템 언어, 최고 성능 | 결정적 실행·정확성 유지에 유리 | 생산성 낮음, 에코 상대적으로 부족 |
| E. C++ (참고) | 차량 SW 산업 표준 계열 | 성능 우수 | 생산성 낮음, 메모리 안전 위험 |

**결정 (Decision):** Option A — Python 3.11+ (타입 힌트 + mypy strict, pip 패키지 + CLI 진입점)<br>
**결정 근거 (Rationale):** v1 목표(헤드리스 CLI + 라이브러리 임베드 + CI)에 개발 생산성·차량 SW 청중 친화성(python-can 등)이 최우선. v2는 FastAPI 백엔드로 코어를 노출하므로 프런트만 JS를 써도 정합.

**성능 목표 (adr/performance-targets.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 순수 Python + 목표 규모</b> | v1은 Python 유지, 목표 규모 명시, 병목 시 후속 확장 | 구현 단순·일관, 성능 검증 기준 제공, ADR-001과 정합 | 대규모(수천 노드) 미지원 |
| B. 확장 모듈 선제 | 이벤트 큐 등 핫 경로를 Rust/C 확장으로 설계 | 성능 여유 | v1 범위 초과, 개발 비용↑, 결정성 검증 부담 |
| C. 목표 미설정 | — | 없음 | 성능 회귀 판정 불가, 확장 근거 부재 |

**결정 (Decision):** Option A — v1 순수 Python + 명시적 목표 규모 (노드 ≤ 50, 링크 ≤ 20, 프레임 ≤ 200, duration ≤ 60s, 이벤트 ≤ 100만)<br>
**결정 근거 (Rationale):** 목표 규모를 명시해 성능 회귀 판정 기준을 확보. 확장 모듈은 병목이 실제 확인된 후에만 도입(선제 도입은 v1 범위 초과).

### ASR-002 — 시뮬레이션 엔진 모델

**엔진 모델 (adr/simulation-engine-model.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. DES</b> | 이벤트 큐 기반, 지연·도착·태스크 실행을 이벤트로 모델링 (ns-3/OMNeT++ 방식) | 지연·대역폭·큐잉·라우팅 정확, fast-forward로 대규모에 효율, 결정적 | 주기적 태스크(CAN 주기 메시지, RTE)를 이벤트로 변환하는 추상화 필요 |
| B. Time-step | 고정 간격마다 전 컴포넌트 순차 실행 (AUTOSAR RTE에 가까움) | 주기 태스크 모델과 자연 일치, 구현 단순 | 지연·경합 정확 모델링 어려움, 간격이 작을수록 느림 |
| C. Continuous | 미분방정식 기반 연속 시간 | 물리적 정확성 | 차량 SW 플랫폼 검증엔 과도, 결정성·구현 불리 |

**결정 (Decision):** Option A — 이산 사건 시뮬레이션(DES) + 주기 태스크 하이브리드. 코어는 이벤트 큐, 앱 주기 태스크는 스케줄러가 이벤트로 생성·실행. 단일 스레드 + 고정 이벤트 순서로 결정성 보장.<br>
**결정 근거 (Rationale):** "결정성"이 검증 도구의 생명. 지연·대역폭·큐잉·게이트웨이를 정확히 재현하며 이벤트 없이 시간을 도약하는 DES가 목표 규모에서 효율적.

**시간 모델 (adr/simulation-time-model.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 정수 ms + (t_ms, seq)</b> | 모든 시간을 정수 ms, (t_ms, seq) 완전 순서, duration_ms 도달 시 종료, 난수 없음 | 결정성 최대, 구현·디버깅 단순, 로그 비교 용이 | ms 미만 정밀도 표현 불가 (v1 L2 충실도엔 충분) |
| B. float ms | 서브-ms 정밀도 허용 | 실행 시간·지연 세부 표현 | 부동소수점 결정성 리스크, 로그 가독성 저하 |
| C. 설정 단위 (ms/us) | 전역 time_unit 설정 | 필요에 따라 정밀도 조정 | 스키마·엔진·로그가 단위 의존 → 복잡·결정성 확인 부담 |

**결정 (Decision):** Option A — 정수 ms + (t_ms, seq) 완전 순서 + duration_ms 종료 + 난수 없음<br>
**결정 근거 (Rationale):** 부동소수점 비교의 결정성 리스크를 원천 제거. 정수 로그는 비교·디버깅이 용이하고, v1 L2 충실도에 ms 정밀도는 충분.

**통신 이벤트 의미론 (adr/communication-event-semantics.md)** — ASR-004에도 적용되는 공유 ADR

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 수신자 매핑 기반 rx</b> | tx 경로 3가지(주기 프레임·ctx.send·주입), rx는 receives 매핑된 노드에만, 게이트웨이는 규칙 체인으로 표현(홉 최대 8 초과 시 drop), Ethernet은 스위치 FIFO 방출 시각에 rx | 로그가 "누가 받았는가" 기준으로 검증 가치 높음, 게이트웨이 별도 노드 불필요(스키마 변경 없음) | 게이트웨이 흐름이 노드 로그가 아닌 규칙으로만 추적됨 |
| B. 브로드캐스트 rx | 링크의 모든 노드에 rx 기록 | 버스 현실(브로드캐스트) 재현 | 로그 폭증(프레임×노드), node 매칭 과잉 |
| C. 게이트웨이 노드화 | 게이트웨이도 node처럼 rx/tx 기록 | 흐름 추적이 명시적 | architecture 스키마 변경, 노드 수 목표에 영향 |

**결정 (Decision):** Option A — 수신자 매핑 기반 rx + 게이트웨이 link rx + 규칙 체인 다중 홉 (홉 최대 8 초과 시 drop)<br>
**결정 근거 (Rationale):** rx는 "누가 받았는가" 기준으로 기록해야 assertion 검증 가치가 있음. 게이트웨이를 노드로 승격하면 스키마가 바뀌므로 규칙 체인으로 표현.

**동일 시각 순서·종료 경계 (adr/event-ordering-boundary.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 우선순위→정의 순서→seq + inclusive</b> | 태스크 우선순위(작을수록 우선) → 파일 선언 순서 → seq. `t == duration_ms`까지 처리 후 종료 | 정의 순서가 결정적·사용자 제어 가능, duration 경계 이벤트 검증 직관 | "선언 순서" 개념 문서화 필요 |
| B. seq만 + inclusive | (t_ms, seq)만 사용 | 단순 | 같은 시각 이벤트 순서를 사용자 제어 불가 |
| C. 정의 순서 + exclusive | A와 동일하되 t==duration_ms 미처리 | "duration까지" 경계가 깔끔 | duration 직전 스케줄 이벤트 검증 불가 — at_ms=duration assertion 실패 |

**결정 (Decision):** Option A — 우선순위 → 정의 순서 → seq + inclusive 종료 (`t == duration_ms`의 이벤트까지 처리)<br>
**결정 근거 (Rationale):** 동일 시각 이벤트의 순서를 사용자가 제어할 수 있어야 검증이 가능. inclusive는 경계 시각 assertion 검증을 가능하게 함.

**결과 리포트 (adr/result-report-schema.md)** — ASR-004·ASR-007에도 적용되는 공유 ADR

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 구조화 리포트</b> | simulation + links(링크 부하·드롭·supersede) + tasks(오버런) + assertions + warnings | PRD 성공 기준 2 직접 지원, 라이브러리 소비 가능, 결정적 | 항목 확정·문서화 부담 |
| B. 최소 리포트 | duration_ms + result + assertion 결과만 | 최소 구현 | 버스 부하·오버런 "확인" 수단 부재 — 성공 기준 2 미달 위험 |
| C. 로그 통합(리포트 없음) | 리포트 없이 이벤트 로그에서 사용자가 집계 | API 단순 | 결과 확인 UX 저하, CLI 요약 불가 |

**결정 (Decision):** Option A — 구조화 리포트 (simulation + links + tasks + assertions + warnings), CLI 요약은 이 표의 요약판<br>
**결정 근거 (Rationale):** PRD 성공 기준 2(버스 부하·오버런 확인)를 직접 지원하면서 라이브러리 소비도 가능. 결정적 출력이라 CI 비교가 용이.

### ASR-003 — 아키텍처/시나리오 정의 형식

**정의 파일 형식 (adr/definition-file-format.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. YAML</b> | 계층 구조 + 주석 | 가독성·주석·계층, Python 에코 성숙, 자동차 도구 관행과 일치 | 타입 엄격성 낮음 (Pydantic으로 보완) |
| B. JSON | 기계 친화적, 엄격 파싱 | 스키마 검증 용이 | 주석 불가, 수기 작성 불편 |
| C. TOML | 설정 중심 단순 문법 | 단순함 | 깊은 계층/목록 표현 불편 |
| D. 전용 DSL | 도메인 특화 문법 | 도메인 최적화 | 개발 비용 큼 (v1에 과도) |

**결정 (Decision):** Option A — YAML (PyYAML 파싱 + Pydantic 모델 기반 스키마 검증, architecture.yaml/scenario.yaml 분리)<br>
**결정 근거 (Rationale):** 정의 파일 = CLI의 1차 UX. 사람이 작성·주석·계층 표현이 우선이며, 자동차 도구 관행과 일치. 타입 엄격성은 Pydantic으로 보완.

**스키마 구조 (adr/definition-schema-structure.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 메시지-프레임 2계층</b> | 컴포넌트는 논리 메시지, 링크는 L2 프레임(id/dlc/period/source/message). 매핑: message 필드 또는 동일 이름. architecture.yaml/scenario.yaml 분리 | L2/L7 분리 명확, 프레임 독립 시뮬레이션 가능, 스키마 검증 명확 | 매핑 개념 1개 추가 (학습 비용 소폭 증가) |
| B. 단일 프레임 레벨 | 컴포넌트가 프레임 직접 송수신 | 스키마 단순 | 앱 로직과 L2 충실도 혼재, 컴포넌트 재사용·신호 표현 불편 |
| C. 신호 레벨 포함 | DBC 스타일 신호 정의 추가 | 실제 신호 의미 표현 | v1 범위 초과, 스키마 복잡도 급증 |

**결정 (Decision):** Option A — 메시지-프레임 2계층 분리 + 매핑 규칙 (프레임 `message` 필드 명시 또는 프레임명=메시지명 기본 규칙)<br>
**결정 근거 (Rationale):** L2/L7 계층을 분리해야 프레임 독립 시뮬레이션(YAML만)이 가능하고 스키마 검증이 명확. 신호 레벨은 v1 범위 초과.

**필드 스키마 (adr/definition-field-schema.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 명시적 완전 스키마 + 공식 예시</b> | 전체 필드 트리를 ADR에 문서화 + Spec 예시 YAML 포함 | SSOT 달성, 구현 발명 제거 | 문서 부담 |
| B. 최소 스키마 | 블록 레벨만, 세부는 구현 시 확정 | 문서 부담 최소 | 구현 발명 잔존 — SSOT 미달 |
| C. 외부 JSON Schema 파일 | 별도 파일로 관리 | 코드 검증과 단일 소스 | 관리 포인트 추가, YAML 작성자 관점 문서 분산 |

**결정 (Decision):** Option A — 명시적 완전 스키마 + 공식 예시 (architecture.yaml/scenario.yaml 필드 트리를 ADR·Spec에 문서화)<br>
**결정 근거 (Rationale):** 이 ADR의 목적이 SSOT — 최소 스키마나 외부 파일 관리는 문서 분산·구현 발명을 남김.

### ASR-004 — 통신 프로토콜 충실도 (CAN/Ethernet)

**충실도 수준 (adr/communication-fidelity-level.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| A. L1 (신호/메시지) | 메시지·신호만 전달, 지연 단순화 | 구현 단순, 앱 로직 검증에 충분 | 대역폭·부하·라우팅 검증 불가 (PRD 미충족) |
| <b style="color:#1a7f37;">B. L2 (프레임/버스)</b> | CAN 프레임·버스 부하·지연·큐잉, 게이트웨이 라우팅, Ethernet 대역폭·스위치 큐잉 | 라우팅·지연·대역폭 검증 가능 (PRD 충족), 비용 합리적 | 비트 레벨 타이밍·프로토콜 스택 세부 제외 |
| C. L3 (프로토콜 스택/물리) | 비트 타이밍·오류 프레임·QoS·Some/IP | 실제 스택 수준 검증 | 구현 비용 급증 (v1 범위 초과) |

**결정 (Decision):** Option B — L2 (프레임/버스 수준). CAN: 비트 수식+ID 중재+큐, Ethernet: 스위치 FIFO+테일 드롭, 게이트웨이: 명시 라우팅. L3(비트 타이밍·QoS·Some/IP)는 v1 제외.<br>
**결정 근거 (Rationale):** PRD가 요구하는 "라우팅·지연·대역폭 검증"을 충족하는 최소 수준이 L2. L3는 구현 비용 급증이라 v1 범위 초과.

**CAN 모델 (adr/can-fidelity-model.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 비트 수식 + 중재 + 큐</b> | `tx_ms = ceil((44 + 8·DLC) / bitrate)`, 동시 전송 시 ID 작을수록 우선, 버스 점유 중이면 우선순위 큐 대기, 버스 부하 % 리포트 | 현실적·결정적, 버스 부하 검증 가능, 구현 합리적 | 비트 스터핑 등 비트 레벨 상세 미포함 |
| B. 고정 지연 상수 | 프레임별 고정 지연 | 구현 최단 | 부하·경합 지연 변화 재현 불가 (PRD 미충족) |
| C. 오류 프레임/재전송/버스 오프 | 프로토콜 오류까지 모델링 | 오류 시나리오 검증 가능 | v1 범위 초과, 복잡도 급증 |

**결정 (Decision):** Option A — 표준 프레임 비트 수식 + ID 우선 중재 + 우선순위 큐 대기 (버스 부하 % 리포트 포함)<br>
**결정 근거 (Rationale):** L2 목표(부하·경합 검증)를 충족하면서 결정적이고 구현이 합리적. 오류 프레임 모델링은 v1 범위 초과.

**Ethernet 모델 (adr/ethernet-fidelity-model.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 스위치 + FIFO + 테일 드롭</b> | `bytes = data + 42`, `tx_ms = ceil(bytes·8 / (bitrate·1000))`, 단일 스위치 FIFO, queue_depth(기본 1000) 초과 시 테일 드롭→drop 이벤트 | 대역폭·큐잉·드롭 검증 가능, 결정적, 구현 합리적 | 우선순위 큐/VLAN 미지원 |
| B. 대역폭만 | 전송 지연만, 큐잉 없음 | 구현 단순 | 스위치 큐잉·드롭 검증 불가 (L2 목표 미달) |
| C. QoS/VLAN 포함 | 802.1p 우선순위 큐 모델링 | QoS 시나리오 검증 | v1 범위 초과, 복잡도 급증 |

**결정 (Decision):** Option A — 프레임 크기 수식 + 단일 스위치 FIFO 큐 + 테일 드롭 (queue_depth 기본 1000)<br>
**결정 근거 (Rationale):** 대역폭·큐잉·드롭 검증이라는 L2 목표를 충족. 우선순위 큐/VLAN은 v1 범위 초과.

**게이트웨이 라우팅 (adr/gateway-routing-rules.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 명시 규칙 + 변환</b> | `routes: [{from: {link, frame|id_min/id_max}, to: {link, remap_id?}}]`, 매칭 우선순위 명시 frame > ID 범위, delay_ms 기본 0 | 라우팅 의도를 명시적으로 검증 가능, ID 변환(remap) 지원 | 규칙 작성 필요 (자동 대비 작성량) |
| B. 자동 라우팅 | 양쪽 링크에 연결된 노드 = 자동 전달 | 작성 부담 없음 | 의도가 코드에 숨음, 제어력 없음, 검증 가치 저하 |
| C. 신호 변환 포함 | DBC 스타일 신호 매핑·데이터 변환 | 실제 게이트웨이 데이터 변환 재현 | v1 범위 초과 (L2는 프레임 단위) |

**결정 (Decision):** Option A — from/to 명시 규칙 + 선택적 변환 (명시 frame > ID 범위 우선순위, delay_ms 기본 0)<br>
**결정 근거 (Rationale):** 라우팅 의도를 명시적으로 검증 가능해야 검증 도구로서 가치가 있음. 신호 변환은 L2 범위 밖.

**큐 오버플로 정책 (adr/frame-queue-overflow-policy.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 최신 교체 (supersede)</b> | 대기 중 동일 프레임 인스턴스가 있으면 기존 제거·신규 교체 | 오래된 데이터 폐기 = CAN 현실과 정합, 큐 폭주 방지, 로그 명확 | 폐기 사실이 별도 이벤트 없음(교체로만 표현) |
| B. 복수 인스턴스 큐잉 | 모든 인스턴스 적재 | 큐 동작 단순 | 폭주 시 오래된 프레임이 뒤늦게 전송(시점 왜곡), 테일 드롭까지 |
| C. 신규 인스턴스 폐기 | 기존 있으면 신규 폐기(drop 이벤트) | 대기열 안정 | 신규 데이터 손실 — 주기 데이터는 최신이 중요한데 역방향 |

**결정 (Decision):** Option A — 최신 교체 (supersede) — 대기 중 동일 프레임은 신규 인스턴스로 교체<br>
**결정 근거 (Rationale):** 주기 데이터는 최신이 중요 — 오래된 인스턴스 폐기가 CAN 현실과 정합하고 큐 폭주를 방지.

> 참고: 이벤트 의미론·결과 리포트는 공유 ADR — 전체 표는 ASR-002 소절 참조 (결정: 각각 A).

### ASR-005 — 앱 런타임 모델

**런타임 모델 (adr/app-runtime-model.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| A. 메시지 구동 | 메시지 수신 핸들러만 보유 | 단순, 결정적, DES와 자연 정합 | 주기적 동작(센서 폴링, 주기 제어) 표현 불가 |
| B. 스레드/태스크 | 실제 스레드로 실행 | 현실적 동시성 표현 | 스케줄링 비결정성 → 결정성 위반, 복잡도↑ |
| <b style="color:#1a7f37;">C. RTE 스타일</b> | 주기 태스크 + 메시지 수신 핸들러, 스케줄러가 이벤트로 스케줄 | AUTOSAR RTE 관행 일치, DES와 정합, 결정적 | 실제 OS 스레드 동작과는 차이 (시뮬레이션 수준) |

**결정 (Decision):** Option C — 주기 태스크 + 이벤트 핸들러 (RTE 스타일) — 주기 태스크와 메시지 수신 핸들러, 스케줄러가 이벤트로 스케줄<br>
**결정 근거 (Rationale):** 자동차 SW의 주기성이 핵심 — RTE 스타일이 AUTOSAR 관행과 정합하면서 DES 엔진(ASR-002)과 자연스럽게 결합. 스레드 기반은 결정성을 깨뜨림.

**스케줄링 정책 (adr/task-scheduling-policy.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 비선점 + wcet + overrun 기록</b> | 이벤트 큐 순차 처리, wcet_ms(기본 0)만큼 시간 경과, 주기 초과 시 overrun 이벤트 + 리포트 경고 | DES와 정합, 결정성 보장, 오버런 관찰 가능 | 실제 RTOS 선점과 상이 (v1 목적상 허용) |
| B. 선점형 | 높은 우선순위가 낮은 것을 선점 | RTOS에 더 근접 | 중단/재개 상태 모델 필요, 결정성 검증 복잡 |
| C. 라운드로빈 | 정의 순서 순환 | 구현 최단 | 우선순위 의미 상실 (ASR-005 불일치) |

**결정 (Decision):** Option A — 비선점 + wcet_ms(기본 0) + overrun 기록<br>
**결정 근거 (Rationale):** 결정성을 지키되 오버런은 관찰 대상으로 남김(실패가 아니라 기록·경고) — PRD 목적(오버런 관찰·검증)과 정합.

**컴포넌트 API (adr/component-api.md)** — ASR-006에도 적용되는 공유 ADR

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 베이스 클래스 + 콜백 + registry</b> | `on_periodic(ctx)`/`on_message(ctx, msg)` 오버라이드, `ctx.send`/`ctx.log`, `load(..., components={...})` + YAML class 필드 | 명시적·타입 힌트 친화, mypy 검증 용이, RTE 관행 정합 | 상속 기반 — 클래스 구조 이해 필요 |
| B. 데코레이터 기반 | `@component`/`@periodic` 스타일 | 선언적, YAML 매핑 간결 | 매직/리플렉션 의존, IDE·타입 검사 지원 약함 |
| C. 순수 함수 콜백 | dict에 함수 매핑 | 최단 작성 | 상태 유지 불편, API 계약 문서화 부담 |

**결정 (Decision):** Option A — Component 베이스 클래스 + 콜백 오버라이드 + registry 등록 (`on_periodic`/`on_message`/`ctx.send`/`ctx.log`, `load(..., components={...})`)<br>
**결정 근거 (Rationale):** 명시적이고 타입 힌트 친화적이라 mypy 검증이 용이하며 RTE 관행과 정합. 데코레이터 매직은 IDE·타입 검사 지원이 약함.

**스텁 동작 (adr/stub-component-behavior.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 수신자 전용</b> | tx는 주기 프레임·시나리오 주입·ctx.send 3경로만, 스텁은 rx 기록만 | 단순·결정적, YAML-only 시나리오는 프레임 주기로 충분 | 컴포넌트 없이 sends 기반 메시지 흐름 생성 불가 |
| B. 스텁 자동 송신 | sends 메시지를 period에 맞춰 자동 tx | YAML만으로 송신 흐름 재현 | "스텁" 의미 모호, 주기·우선순위 파생 결정 필요, 예상 밖 tx 위험 |
| C. class 미지정 시 오류 | 모든 컴포넌트에 class 필수 | 의미 명확 | YAML-only 검증 경로 차단 — v1 목표와 상충 |

**결정 (Decision):** Option A — 스텁은 수신자로만 동작 (sends 무시, tx는 주기 프레임·시나리오 주입·ctx.send 3경로만)<br>
**결정 근거 (Rationale):** 스텁을 "통신 시뮬레이션의 관찰자"로 단순·결정적 유지. YAML-only 시나리오는 프레임 주기로 충분(성공 기준 1·2 보존).

**공개 API 계약 (adr/public-api-contract.md)** — ASR-006에도 적용되는 공유 ADR

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 경로 기반 + 결과 객체</b> | `load(arch, scenario, components?) -> Simulator`, `run() -> SimulationResult` (events 전체 버퍼·report·assertions·duration_ms), `TaskContext.send/log/now_ms` | 단순·타입 명시·임베드 직관, 1M 이벤트 메모리 수용(성능 목표 내), 결정성 보존 | 실시간 스트리밍 소비 불가(전체 실행 후 반환) |
| B. 파일 객체/딕셔너리 + 콜백 | load가 dict 수용, run(on_event=...) | 메모리 효율, 유연한 입력 | 콜백 순서·예외 처리 부담, 타입 힌트 약화 |
| C. 이터레이터 스트리밍 | run()이 generator 반환 | 실시간 소비 가능 | assertion/리포트가 전체 로그 필요 → 내부 버퍼 필수, API 복잡↑ |

**결정 (Decision):** Option A — 경로 기반 + 결과 객체 (전체 이벤트 버퍼 + 리포트 + assertion 결과)<br>
**결정 근거 (Rationale):** v1 성능 목표(≤100만 이벤트)에서 전체 버퍼를 메모리에 수용 가능 — 단순·타입 명시·임베드 직관을 얻고 결정성을 보존. 실시간 스트리밍은 v1 요구가 아님.

**오버런 정책 (adr/task-overrun-policy.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 절대 주기 + 스킵</b> | 다음 실행은 원래 주기(t=0 기준), 놓친 주기는 스킵 | 결정적·단순, AUTOSAR 주기 의미 정합, 오버런 누적 없음 | 오버런 직후 실행 기회 손실 (현실 RTOS와 상이 — v1 허용) |
| B. 상대 주기(밀림) | 완료 시각 + period에 다음 실행 | 실행 기회 보존 | 오버런 연쇄(주기 어긋남), 로그 해석 복잡, 예측 어려움 |
| C. 오버런 시 실패 | 오버런 = 결과 실패 | 하드 에러로 취급 | PRD 목적(오버런 관찰·검증)과 상충 — assertion 대상으로 쓰는 용도 차단 |

**결정 (Decision):** Option A — 절대 주기 유지 + 인스턴스 스킵 (놓친 주기는 실행 안 함)<br>
**결정 근거 (Rationale):** AUTOSAR 주기 의미(절대 주기)와 정합, 오버런 누적이 없어 결정적·단순. 오버런 자체는 기록되어 검증 대상이 됨.

### ASR-006 — 코어 API 경계 & 다중 아티팩트 구조

**패키지 구조 (adr/package-structure.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 단일 패키지 + 모듈 경계</b> | `sdv-sim`(임포트 `sdv_sim`) 하나, 내부 core/cli 분리 | v1 오버헤드 최소 + 경계 유지, 공개 API 계약으로 임베드 지원 | 물리적 분리보다는 약한 경계 |
| B. 멀티 패키지 워크스페이스 | core/cli 별도 설치 가능 (워크스페이스 도구 필요) | 의존성 방향이 가장 명확 | v1 패키징 오버헤드 |
| C. 단일 모듈 | 전 코드 한 모듈 | 가장 단순 | 경계 없음 → 성장 시 재구성 비용 큼 |

**결정 (Decision):** Option A — 단일 패키지 + 모듈 경계 (배포 `sdv-sim`, 임포트 `sdv_sim`, 내부 `sdv_sim/core`·`sdv_sim/cli`)<br>
**결정 근거 (Rationale):** "모든 형태가 단일 코어 공유"의 실현 수단 — v1에서 물리적 분리는 오버헤드, 모듈 경계 + 공개 API 계약으로 임베드를 지원.

**CLI I/O 계약 (adr/cli-io-contract.md)** — ASR-007에도 적용되는 공유 ADR

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. --log 파일 + 요약 stdout</b> | `run <arch> <scenario> [--log <path>] [--quiet] [--lang]`, JSON 로그는 파일(기본 events.json, `-`=stdout), 사람용 요약은 stdout, --quiet 시 요약 생략 | CI에서 로그 아티팩트 분리, 요약/로그 섞임 없음, 기본값 안전 | 기본 파일 생성(작업 디렉터리 오염) — `--log -`/`--quiet`로 회피 |
| B. --json 플래그 | --json 시 JSON만 stdout | 파이프 친화 | 요약+JSON 동시 확인 불가, CI 파이프 처리 부담 |
| C. --log 필수 | --log 없으면 오류 | 명시성 | 기본 실행 UX 저하 (성공 기준 4 헤드리스 단순성) |

**결정 (Decision):** Option A — 로그는 파일(--log), 요약은 stdout (--quiet 시 요약 생략, 오류 메시지도 --lang 적용)<br>
**결정 근거 (Rationale):** CI에서 로그 파일 아티팩트를 분리하고 요약·로그가 섞이지 않음. 기본값 안전성(파일 생성)은 `--log -`/`--quiet`로 회피.

**CLI 출력 정책 (adr/cli-output-policy.md)** — ASR-007에도 적용되는 공유 ADR

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. --lang + env + 로케일 + 0/1/2/3</b> | 언어: `--lang` > `SDV_SIM_LANG` > 로케일(기타→ko). 종료: 0=pass / 1=assertion fail / 2=입력 오류 / 3=내부 오류 | 사용자 제어 명확, CI에서 오류 종류 구분, 구현 단순 | 코드 분류 세분화 필요(경미) |
| B. 언어 고정 ko + 0/1 | — | 구현 최단 | PRD "ko/en 지원 구조" 제약 위반, 오류 구분 불가 |
| C. gettext 프레임워크 | 표준 국제화 | 표준화 | v1에 과도, 카탈로그 관리 부담 |

**결정 (Decision):** Option A — --lang 플래그 + SDV_SIM_LANG env + 로케일 폴백 + 종료 코드 0/1/2/3<br>
**결정 근거 (Rationale):** PRD "ko/en 지원 구조" 제약 충족 + CI에서 오류 종류를 코드로 구분. gettext는 v1에 과도.

**YAML 문자열 입력 (adr/core-yaml-string-input.md)** — ASR-015에도 적용되는 공유 ADR (F-11, 2026-08-12)

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 전용 loads() 계열</b> | `loads(arch_yaml, scenario_yaml, components?)` + `load_scenario_yaml(str)` 추가, 기존 경로 API 유지 | Python 표준 관례(json.loads) 일치, 기존 계약 불변(하위 호환), 명시적·타입 안전, 에러 포맷 로직 재사용 | API 표면 2배(경로+문자열), 동의어 API 혼동 가능성 |
| B. load() 감지 통합 | str 인자가 경로인지 YAML 내용인지 자동 판별 | API 단일, 호출 측 단순 | **모호성 위험** — 없는 경로 vs 파싱 실패 내용 구분 불가, 오류 진단 혼란, 타입 안전성 약화 |
| C. from_yaml 클래스메서드 | `Simulator.from_yaml(...)` 추가 | "Simulator 생성" 진입점 통합 | v1 load()-함수 패턴과 이원화, 문서/임포트 경로 2곳 분산 |

**결정 (Decision):** Option A — 전용 `loads()`/`load_scenario_yaml()` 계열 함수 추가 (기존 `load()`·`load_scenario()` 경로 계약은 하위 호환으로 유지) — F-11 방향 전환(2026-08-12)으로 v1 Spec D-15에 기록 완료<br>
**결정 근거 (Rationale):** 브라우저가 보낸 YAML 문자열을 서버가 그대로 v1 API로 전달하는 F-11 경로의 근간. json.loads 관례를 따르고 기존 계약을 깨지 않으며, 감지 통합(B)의 모호성 리스크를 배제.

> 참고: 컴포넌트 API·공개 API는 공유 ADR — 전체 표는 ASR-005 소절 참조 (결정: 각각 A).

### ASR-007 — 검증·자동화 지원

**검증 방식 (adr/verification-automation.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| A. 선언형 assertion | 시나리오 YAML에 기대값 선언 | CLI 사용자 직관, CI 판정 자동화 용이 | 복잡 조건 유연성 제한 |
| B. 이벤트 스트림 외부 검증 | 엔진이 결정적 JSON 로그 출력, 검증은 사용자 도구 | 최대 유연성 | 사용자 부담, 1차 검증 경험 부재 |
| <b style="color:#1a7f37;">C. A+B 결합</b> | 선언형(기본) + JSON 스트림(고급) | 추가 비용 낮음, 유연성 최대 | assertion 문법·로그 스키마 정의 필요 |

**결정 (Decision):** Option C — 선언형 assertion(기본) + JSON 이벤트 스트림(고급 검증) 결합<br>
**결정 근거 (Rationale):** 엔진이 어차피 이벤트를 생성하므로 스트림 노출 비용이 낮고, 선언형 assertion으로 CLI 1차 검증 UX를 지킴.

**Assertion 문법 (adr/assertion-grammar.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. YAML 선언형 expect</b> | `assertions: [{name?, expect: {event, frame/message/node/link/task, at_ms, within_ms, count}}]` | 시나리오 YAML과 동일 문법(일관성), 파싱 간단, CI 검토 용이 | 복잡 논리 제한 (v1엔 충분) |
| B. 내장 DSL 문자열 | `"rx door-state-frame at 10ms within 5ms count 1"` | 표현력·간결성 | 파서 구현 필요, 스키마 검증 밖, 오타 위험 |
| C. Python 콜백 검증 | 검증 함수 참조, 이벤트 스트림 소비 | 최대 유연성 | 선언성 상실, YAML-only 검증 불가 |

**결정 (Decision):** Option A — YAML 선언형 expect 블록 (평가: 종료 후 로그에서 첫 매칭 이벤트 기준 시간 검증 + count 개수 검증)<br>
**결정 근거 (Rationale):** 시나리오 YAML과 동일 문법으로 일관성 유지, 파싱 간단, CI에서 검토 용이. 복잡 논리는 스트림(옵션 C 방식)으로 보완.

**평가 규칙 (adr/assertion-evaluation-detail.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 전체 count + 시간 무관 기본 + 실패 상세</b> | 매칭: event 타입+속성 일치. 시간: at_ms 명시 시 `|t_ms-at_ms| ≤ within_ms`(기본 0), 생략 시 무관. count: 전체 로그 총수(시간과 독립). 실패 메시지: 매칭 3건 + 기대/실제 시각·count | 예측 단순, SSOT 갭 해소, CI 디버깅 UX | count와 at_ms 독립(같은 윈도우 count 아님) — 의도 설명 필요 |
| B. 윈도우 count | count = within_ms 내 매칭 수 | "지정 시간대 n건" 직관 | at_ms 생략 시 윈도우 모호, 시간 조건 중첩 해석 복잡 |
| C. at_ms 필수 | 생략 시 스키마 오류 | 모호성 제거 | "이벤트 존재 여부만" 검증 불가 — 표현력 저하 |

**결정 (Decision):** Option A — count=전체 로그 총수 + 시간 무관 기본(at_ms 명시 시에만 시간 검증) + 실패 상세(매칭 3건 + 기대/실제 시각·count)<br>
**결정 근거 (Rationale):** 예측이 단순하고 CI 디버깅 UX가 좋음. count와 at_ms를 독립시켜 "최소 발생" 검증 의도와 정합(ASR-012 결정과 일관).

**이벤트 로그 스키마 (adr/event-log-schema.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 단일 JSON 파일</b> | `{schema_version, simulation, events: [{t_ms, seq, type, ...}], assertions}`, type enum 7종(tx/rx/task_start/task_end/drop/overrun/log), (t_ms, seq) 오름차순 | 단일 산출물(CI 아티팩트), 스키마 검증 용이, 결정성 명확 | 대규모 시나리오에서 파일 크기 증가 (v1 목표 규모에선 무시 가능) |
| B. NDJSON 스트림 | 이벤트 1건 = 1라인 | 파일 크기 효율, 스트리밍 | 단일 JSON이 아님 — 검증·시각화 불편 |
| C. 타입별 분리 배열 | `{tx: [...], rx: [...], task: [...]}` | 타입별 조회 용이 | 순서 복원에 추가 정보 필요 — 결정성 표현 약화 |

**결정 (Decision):** Option A — 단일 JSON 파일 (events 배열 + type enum 7종, (t_ms, seq) 오름차순, 누락 필드 생략)<br>
**결정 근거 (Rationale):** 단일 산출물로 CI 아티팩트·스키마 검증·결정성 표현이 모두 명확. 파일 크기는 v1 목표 규모에서 무시 가능.

> 참고: CLI 출력·I/O 계약·결과 리포트는 공유 ADR — 전체 표는 ASR-006·ASR-002 소절 참조 (결정: 각각 A).

### ASR-008 — 동일 시각 비-태스크 이벤트 순서

**비-태스크 순서 (adr/event-ordering-non-task.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 비-태스크는 모든 태스크 뒤</b> | 가상 우선순위 2^30 → 태스크 이벤트 후 처리, 비-태스크 간 선언 순서 → seq | 부수효과 tx가 같은 tick tx보다 먼저 처리 → 관측 순서 자연스러움 | 태스크와 tx 순서에 의존하는 검증은 문서화된 규칙에 의존 |
| B. 선언 순서 통합 | 태스크·비-태스크 구분 없이 선언 순서 | 규칙 단일화 | ctx.send 결과 tx 순서 보장 불가 — 정의 순서에 민감 |
| C. 비-태스크를 앞에 | 최소 우선순위 부여 | 구현 대칭 | 태스크가 만든 tx가 뒤늦게 관측 — 원인-결과 역전 가능 |

**결정 (Decision):** Option A — 비-태스크는 모든 태스크 뒤 (가상 우선순위 2^30, 비-태스크 간에는 파일 선언 순서 → seq) — 스펙 D-19 인코딩 완료<br>
**결정 근거 (Rationale):** 태스크 실행의 부수효과(`ctx.send` → tx)가 같은 tick의 다른 tx보다 먼저 처리되어 "원인 → 결과" 관측 순서를 보장 — assertion 결과의 결정성에 직접 영향.

### ASR-009 — Ethernet 스위치 다중 정의 정책

**스위치 선택 (adr/ethernet-switch-selection.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 첫 번째만 사용</b> | switches 첫 항목만 큐잉 파라미터로 사용, 나머지 무시(오류·경고 없음) | 단일 스위치 모델 유지, 정의 파일 호환성 최대, 구현 단순 | 다중 스위치 기대 시 조용히 무시됨 — 검증 관점 오해 가능 |
| B. 2개 이상이면 스키마 오류 | 배열 길이 1 초과 시 오류(파일명·필드 경로 포함) | 잘못된 기대 즉시 표면화 | v1 범위 밖 정의를 거부 — 향후 다중 스위치 대비 파일이 깨짐 |
| C. 다중 스위치 모델링 | 모든 스위치를 독립 큐로 | L2 충실도 최대 | v1 범위 초과(토폴로지·라우팅 복잡), 스펙 Out of Scope 위반 |

**결정 (Decision):** Option A — switches 첫 항목만 큐잉 파라미터로 사용, 나머지 무시 (스키마 오류 없음). 다중 스위치는 v2+ 후보.<br>
**결정 근거 (Rationale):** v1은 단일 스위치 모델 — 오류 거부는 v1 범위 밖 정의 파일을 깨뜨리고, 다중 모델링은 범위 초과. "첫 항목 사용"을 스펙에 명시해 오해를 방지.

### ASR-010 — 로그 쓰기 실패 종료 코드

**종료 코드 분류 (adr/log-write-failure-exit-code.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. exit 2 (입력 오류)</b> | 쓰기 실패를 파일/입력 범주로 분류 | 파일 범주 단일화·단순, CI에서 파일 문제와 assertion(1) 구분 | 의미상 쓰기 실패는 출력 I/O 오류 — 3과 경계 모호 |
| B. exit 3 (내부 오류) | 쓰기 실패를 내부/환경 오류로 분류 | "입력 오류"가 정의 파일 문제만을 지칭 — 의미 명확 | 사용자 환경 문제(권한·디스크)를 "내부 오류"로 오인 가능 |
| C. 별도 exit 4 (I/O 오류) | 쓰기 실패 전용 코드 추가 | 2/3/4 삼분화 — CI 원인 구분 최대 | 기존 코드 계약 변경 필요, cli-output-policy·스펙 수정 부담 |

**결정 (Decision):** Option A — 종료 코드 2 (입력/파일 오류로 분류) — 스펙 D-16 인코딩 완료<br>
**결정 근거 (Rationale):** "파일" 범주의 오류를 하나로 묶어 종료 코드 계약(0/1/2/3)을 유지하고, CI에서 파일 문제와 assertion 실패(1)를 구분 가능. 3과의 경계 모호함은 스펙 D-16으로 의미를 명시해 해소.

### ASR-011 — Assertion `event: task` 매칭 범위

**task 매칭 (adr/assertion-task-event-matching.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 둘 다 매칭</b> | event: task = task_start+task_end 모두 대상, task 속성으로 한정 | 생명주기 종합 검증, count로 시작+종료 총수 검증 | 시작/종료 구분 검증 시 count에 의도치 않은 혼합 가능 |
| B. task_start만 | 시작 이벤트만 매칭 | "실행 시작" 단일 의미 — 실행 횟수 검증 직관 | 종료(완료) 여부 검증 수단 부재 |
| C. task_end만 | 종료 이벤트만 매칭 | "완료" 단일 의미 — 완료 검증 직관 | 시작 이벤트 검증 불가, 오버런 등 시작만 기록되는 사례 누락 |

**결정 (Decision):** Option A — task_start와 task_end 둘 다 매칭 (`task` 속성으로 특정 태스크 한정) — 스펙 D-20 인코딩 완료<br>
**결정 근거 (Rationale):** "이 태스크가 (시작하거나 끝나는) 실행 이벤트를 n건 가짐"이라는 종합 검증이 가능. 시작/종료 구분이 필요하면 count 산정에 유의해야 함을 스펙 D-20으로 명시.

### ASR-012 — Assertion count 비교 연산

**count 연산 (adr/assertion-count-minimum.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 최소 n건 이상 (≥)</b> | 매칭 수 ≥ n이면 통과, 초과는 실패 아님 | 경계·부수 이벤트 내성, 공식 예시(12건)와 정합, 의도 직관 | 과잉 발생(원치 않는 추가 전송)을 잡아내지 못함 |
| B. 정확히 n건 (==) | count와 정확히 일치해야 통과 | 결정적 시뮬레이션에서 정밀 검증 — 추가 이벤트도 실패로 검출 | 종료 경계·부수 이벤트로 수가 어긋나면 의도와 무관하게 실패 |
| C. 최대 n건 이하 (≤) | 매칭 수 ≤ n이면 통과 | 상한 검증 가능 | 최소 보장 없음 — "아예 없어도 통과" — 대부분 의도와 반대 |

> 참고: 원 ADR 파일에서는 최소 n건이 Option A로 표기되어 있으며, 채택 옵션은 동일(≥).

**결정 (Decision):** Option A — 최소 n건 이상 (≥) — 매칭 이벤트 ≥ n이면 통과, 초과는 실패 아님, 시간 조건과 독립. 스펙 D-20 인코딩 완료<br>
**결정 근거 (Rationale):** 주기 이벤트 수는 duration 경계(inclusive 종료)로 미세하게 달라질 수 있음 — "최소한 n건 발생"이라는 검증 의도에 직관적이고 경계 내성. "정확히 n건"이 필요하면 별도 수단으로 보완.

### ASR-013 — Ethernet payload 크기 기준

**payload 기준 (adr/ethernet-payload-basis.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 프레임 DLC 기준</b> | 전송 크기 = 정의된 dlc(고정), 주입 데이터 크기와 무관 | 결정적·예측 가능, CAN 모델과 일관, 구현 단순 | 실제 페이로드가 DLC와 달라도 전송 크기 동일 — 미세 충실도 손실 |
| B. data 객체 직렬화 크기 | 주입/전송 시 data 직렬화 크기를 payload로 | 실제 데이터 크기 반영 — 크기별 대역폭 검증 가능 | 직렬화 규칙에 따라 크기 변동 — 결정성 위험, CAN과 비대칭 |
| C. max(dlc, data) 또는 설정 | 큰 값 사용, 또는 payload_mode 설정 | 유연성 | 기본값 모호, v1 스키마·문서 변경 부담 |

**결정 (Decision):** Option A — payload = 프레임 DLC 바이트 (`bytes = dlc + 42`, 주입 data 객체 크기와 무관) — 스펙 인코딩 완료<br>
**결정 근거 (Rationale):** 전송 크기가 주입 내용과 무관해야 결정적·예측 가능하고, CAN 모델(전송 크기 = DLC)과 일관. 미세 충실도 손실은 v1 L2 수준에서 수용.

### ASR-014 — 대시보드 기술 스택 (백엔드·프런트엔드)

**대시보드 스택 (adr/dashboard-tech-stack.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. FastAPI + React/TS + Vite</b> | FastAPI: Pydantic 네이티브(스키마 재사용), OpenAPI 자동화, SSE/WS. React+TS: 커스텀 캔버스 제어. Vite: 빠른 빌드 | v1 스키마 재사용 최적, 이벤트 스트리밍·커스텀 렌더링 최적, 에코 최대 | Node 프런트 빌드 파이프라인 필요(개발 복잡도 증가) |
| B. FastAPI + Vue3/TS + Vite | 백엔드 동일, Vue Composition API | 템플릿 직관성, 단일 파일 컴포넌트 | React 대비 그래프·캔버스 레퍼런스 상대적 부족 (기능상 동급 — 취향 차이) |
| C. Python 단일 (Streamlit/Dash) | 전부 Python, 빌드 없음 | 단일 언어, 패키지 통합 단순, 개발 빠름 | **커스텀 토폴로지 캔버스 + 대용량 애니메이션 리플레이 구현 제약**, 프레임워크 제약·성능 커스터마이즈 어려움 |

**결정 (Decision):** Option A — FastAPI(백엔드) + React/TypeScript + Vite(프런트엔드) — 사용자 승인 (2026-08-12)<br>
**결정 근거 (Rationale):** FastAPI의 Pydantic 네이티브 재사용으로 v1 스키마(검증 피드백 API)를 그대로 활용. React+TS는 커스텀 캔버스(SVG/Canvas)·이벤트 스트리밍에 가장 자유도가 높음 — v2 핵심 UX(구조 뷰 오버레이 리플레이)에 필수.

### ASR-015 — 데이터 흐름·리플레이 모델

**데이터 흐름·리플레이 (adr/dashboard-data-flow-replay.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 임베드 실행 + 일괄 JSON</b> | 서버가 코어 import 후 load/run, 두 흐름(run·load-log) 모두 `GET /api/events`로 정렬 전체 목록 반환, 프런트 로컬 재생/시크 | 구현 단순, v1 공개 API 그대로, 단일 프로세스(ASR-019 일관), 시크 UX 최고, 두 흐름 동일 파이프라인 | 대용량(≤100만) 응답 JSON 크기·파싱 비용, 서버 메모리 전체 보유 |
| B. 임베드 + SSE 스트리밍 | 이벤트를 청크 단위 SSE로 push, 프런트 버퍼링 | 초기 응답 지연 감소, 실행-재생 연결 자연 | 시크 시 서버 왕복 필요, 커넥션 관리 복잡, 단일 사용자에 이점 제한 |
| C. CLI subprocess + 일괄 JSON | 서버가 `sdv-sim run`을 하위 프로세스로 실행 | 프로세스 격리(크래시 영향 없음), CLI 출력 재사용 | 프로세스 관리·로그 경로 처리 복잡, 상태 전달 추가, 인프로세스보다 간접적 |

**결정 (Decision):** Option A — 코어 임베드 실행 + 일괄 JSON 전달 (타임스탬프 정렬 전체 이벤트를 `GET /api/events`로 반환, 프런트 로컬 재생/시크, SSE/WebSocket 비목표)<br>
**결정 근거 (Rationale):** 단일 프로세스 + v1 공개 API 그대로(코어 무변경 보장) + 시크 UX 최고. 로그 파일 로드와 실행이 동일 파이프라인. SSE의 시크 시 왕복·커넥션 관리 복잡성은 로컬 단일 사용자 시나리오에서 이점 제한.

**run 경로 (adr/dashboard-run-path.md — ⚠ superseded, F-11로 폐기)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| A. v1 무변경 (모델 직접 파싱) | 서버가 yaml.safe_load → Pydantic model_validate → Simulator(...).run(), 검증/실행 유틸 공유 | PRD "v1 코어 무변경" 완전 준수, v1 재검증 불필요 | v1 private 헬퍼 기능을 서버 모듈에서 재구현 |
| B. v1 수정 (load_str 추가) | v1 코어에 문자열 입력 공개 API 추가 | 문자열 입력이 v1 계약에 정식화, 파싱·오류 포맷 단일 진실 소스 | PRD "v1 코어 무변경" 위반 — v1 재승인 필요, 슬라이딩 스코프 위험 |

**결정 (Decision):** ⚠ **superseded** — F-11 방향 전환(2026-08-12)으로 두 옵션 모두 폐기. `core-yaml-string-input` Option A(전용 `loads()` 추가)가 v1 API로 정식화되어 run 경로로 채택 — 서버는 모델 파싱 재구현 없이 v1 공개 함수만 호출.<br>
**결정 근거 (Rationale):** "v1 무변경" 대 "v1 수정"의 이분법을 넘어, F-11에서 문자열 입력 자체를 v1 공개 계약으로 정식화하는 방향이 선택됨 — 브라우저 YAML 문자열 → v1 `loads()` 직접 전달로 파싱 로직이 단일 진실 소스로 유지.

**세션 수명주기 (adr/dashboard-session-lifecycle.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 스냅샷 세션 + 무효화</b> | 세션 = {events, report, duration_ms, source, arch/scenario 스냅샷}, 편집 첫 변경 시 무효화 → 오버레이 해제+표시, 세션 전역 1개 last-write-wins | 리플레이-정의 불일치 원천 차단(검증 신뢰성), 상태 모델 단순 | 편집 후 재실행 전까지 리플레이 재생 불가 (약간의 UX 제약) |
| B. 세션 독립 유지 | 편집과 무관하게 유지, 명시적 해제 컨트롤 | 편집 중에도 참조 가능 | 오버레이가 다른 정의의 데이터일 수 있음 — 오인 위험, 상태 복잡 |
| C. 유지 + 불일치 표시 | B + 편집 시 "불일치" 배지 | 유연 + 오인 방지 | 내용 비교 로직 추가, 상태 모델 복잡 |

**결정 (Decision):** Option A — 스냅샷 세션 + 편집 시 무효화 (세션 = {events, report, duration_ms, source, 스냅샷}, 전역 1개, last-write-wins). 무효화 신호는 프런트 로컬 상태(`SessionMeta.invalidated`, 편집 시작 시 세팅) — validate는 순수 검증으로 전환.<br>
**결정 근거 (Rationale):** 리플레이-정의 불일치를 원천 차단하는 검증 도구의 신뢰성 기준. 2026-08-13 T-024 재설계로 무효화를 프런트 로컬 상태로 이동 — 편집 없이 validate가 불리는 경로에서 세션이 죽는 버그(리포트 409) 해소.

**load-log 리포트 (adr/dashboard-load-log-report.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 파생 가능 항목만 + arch 연동 시 전체</b> | 이벤트에서 파생 가능한 항목만 표시, 파생 불가 항목 미표시 + "아키텍처 로드 시 전체" 안내, arch 스냅샷 있으면 전체 계산 | 허위 통계 없음(신뢰성), 구현 단순, v1 의미론("리포트는 정의+이벤트에서 파생") 정합 | 로그 단독 리플레이에서 일부 지표 누락 |
| B. 로그 포맷 확장 (report 포함) | v2 로그에 report 필드 추가 | v2 생성 로그는 전체 리포트 | v1 로그 호환 문제·스키마 분기, "v1 로그 스키마 그대로"(ASR-015)와 충돌, 실익 제한 |
| C. load-log에서 리포트 탭 제한 | 로그 재생 시 리포트 비활성, assertion만 | 명확·최소 구현 | PRD 성공 기준 4를 로그 겸용 경로에서 미충족 |

**결정 (Decision):** Option A — 파생 가능 항목만 표시 + arch 연동 시 전체 리포트 (파생 불가 항목은 미표시 + 안내)<br>
**결정 근거 (Rationale):** 허위 통계 없음(신뢰성) + v1 의미론("리포트는 정의+이벤트에서 파생") 정합. 로그 포맷 확장은 v1 로그 스키마 계약과 충돌.

> 참고: YAML 문자열 입력(run 경로 재설계)은 공유 ADR — 전체 표는 ASR-006 소절 참조 (결정: A — loads() 계열). 브라우저 파일 접근(load-log 경로 입력)은 공유 ADR — 전체 표는 ASR-017 소절 참조 (결정: C — 하이브리드).

### ASR-016 — 구조 뷰 렌더링·성능

**렌더링 기술 (adr/topology-rendering-performance.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. SVG + React 커스텀</b> | React가 SVG 노드/링크 렌더, D3는 레이아웃 계산만, 애니메이션은 stroke-dashoffset/CSS, 상태는 클래스 토글 | DOM 기반 — React 상태·이벤트 자연 통합, 개발·디버깅 최고, 수백 요소에 성능 충분, 리플레이 갱신은 변화 요소만 | 요소 수천 개 넘으면 DOM 오버헤드 (현 요구에선 없음) |
| B. Canvas 2D 커스텀 | 단일 캔버스 직접 그리기 | 요소 수 무관 그리기 성능 | 히트 테스트·툴팁·인터랙션 직접 구현, React와 수동 동기화, 개발 비용 큼 — 과잉 |
| C. 그래프 라이브러리 | Cytoscape.js / vis-network 등 | 그래프 기능 기본 제공 | **커스텀 오버레이(프레임 애니메이션·라우팅·드롭)가 데이터 모델에 제약** — v2 핵심 UX를 라이브러리에 맞게 각색해야 함, React 이중 관리 |

**결정 (Decision):** Option A — SVG + React 커스텀 (D3는 레이아웃 계산만) — 성능 기준: 노드 ≤200/링크 ≤500 60fps, ≤100만 이벤트 로드·정렬 ≤2s, 시크 ≤100ms<br>
**결정 근거 (Rationale):** DOM 기반 SVG가 React 상태·이벤트(클릭/툴팁)와 자연 통합되고 수백 요소 규모에서 성능이 충분. 커스텀 오버레이(링크 프레임 애니메이션·라우팅·드롭)를 라이브러리 제약 없이 구현 가능.

**애니메이션 시간 모델 (adr/dashboard-replay-animation-timing.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 물리 재생 + 고정 폴백</b> | 프런트가 arch로 tx_ms 계산, [tx, tx+tx_ms) 동안 프레임 이동 — rx 시각과 정확 일치. load-log는 고정 펄스 + "근사 표시" 라벨 | v1 의미론·rx 타임스탬프와 시각 정합, 버스 부하·연속 전송 직관, 리포트(부하)와 시각 일관 | run 경로는 arch 필요(이미 보유), load-log 폴백 필요 |
| B. 고정 펄스 단일 | 모든 tx에서 배속 기준 고정 지속시간 펄스 | 구현 단순, arch 불필요, 경로 일관 | rx 타임스탬프와 시각 불일치 — 도착이 늦거나 빨라 보임, 연속 프레임 겹침 오해 |
| C. rx 구간 기반 추정 | 완료를 다음 rx 시각으로 추정 | rx 존재 시 arch 불필요 | rx 미발생 프레임 추정 불가 → 폴백 필요, 다중 수신자·재전송 시 매칭 모호 |

**결정 (Decision):** Option A — 물리 시간 재생 (tx_ms 기반) + load-log 고정 폴백 ("근사 표시" 라벨)<br>
**결정 근거 (Rationale):** v1 의미론(rx 타임스탬프)과 시각적으로 정합하고 리포트(버스 부하)와도 일관. run 경로는 arch를 이미 보유하므로 추가 부담이 없음.

**시크 인덱싱 (adr/dashboard-seek-state-indexing.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 스냅샷 + 잔여 재적용</b> | 이벤트 K개마다 노드/링크 상태 스냅샷, 시크 = 이진 탐색 + 잔여 ≤ K 재적용 | 시크 비용 상한(K) 보장 — 100ms 달성 예측 가능, 메모리 제어 가능, 로드·정렬 2s 예산에 구축 포함 | 스냅샷 구축 비용·메모리 (사전 계산) |
| B. O(N) 순차 재적용 | 매 시크마다 처음부터 재적용 | 구현 단순, 추가 메모리 없음 | 최악 100만 재적용 — 100ms 초과 위험, 비용 비예측 |
| C. 전 이벤트 상태 시퀀스 | 이벤트별 결과 상태를 배열로 O(1) 시크 | 시크 즉시 | 상태 복사 O(N) 메모리 — 100만 건에서 비현실 |

**결정 (Decision):** Option A — 주기적 상태 스냅샷 + 잔여 ≤ K 재적용 (이벤트 K개마다 스냅샷, 시크 = 이진 탐색 + 재적용)<br>
**결정 근거 (Rationale):** 시크 비용 상한(K)을 보장해 100ms 성능 기준 달성을 예측 가능. 메모리를 스냅샷 크기×개수로 제어.

**레이아웃 결정성 (adr/dashboard-layout-determinism.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 결정성 요구</b> | "동일 입력 → 동일 레이아웃"을 요구사항으로 명시, 구현은 자유(결정적 계층 또는 고정 시드+고정 반복 포스) | 리플레이 오버레이 안정, 클릭·선택 유지, 스크린샷·문서 재현성, 테스트 용이 | 비결정적 포스 대비 최적 배치에서 다소 열위 |
| B. 비결정적 포스 허용 | 표준 D3 force, 매 로드 재계산 | 유기적 배치, 구현 단순 | 재실행마다 위치 변경 — 오버레이·클릭 기억·스크린샷 불안정, v2 핵심 UX 손상 |
| C. 고정 규칙 배치 | 타입·링크 종류로 그리드/밴드 고정 | 완전 결정적·예측 가능 | 대형 그래프(200노드) 적응성 낮음, 미관 하락 가능 |

**결정 (Decision):** Option A — 결정성 요구 ("동일 입력 → 동일 레이아웃" 명시, 구현은 결정적 계층 레이아웃 또는 고정 시드+고정 반복 수의 포스 레이아웃)<br>
**결정 근거 (Rationale):** 리플레이 오버레이 안정·클릭/선택 유지·스크린샷/문서 재현성·테스트 용이 — v2 핵심 UX(구조 뷰 위 리플레이)를 지키는 전제.

**배치 규칙 (adr/dashboard-layout-placement-rule.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 타입 밴드</b> | 타입별 수평 밴드(HPC 상단/게이트웨이 중앙/ECU 하단), 밴드 내 결정적 순서(연결 수 내림차순 → 이름순), 링크 종류는 색·굵기·대시로 구분 | "타입 기준"이 직접 관찰 가능 — 검증 쉬움, 결정성이 구조적으로 보장, 구현 단순 | 대형 그래프에서 단일 밴드 내 밀집 가능, 유기적 배치 대비 미관 한계 |
| B. 결정적 포스 + 타입 클러스터 | 고정 시드 포스 + 타입 기반 인력/척력 + 링크별 스프링 길이 | 유기적 배치 품질, 200노드 적응성 | "타입 기준"이 결과적 특성 — 검증이 간접 지표에 의존, 결정성이 구현에 민감 |
| C. 커넥티비티 계층 | 게이트웨이 중심 홉 기반 계층 배치 | 라우팅 중심 토폴로지 반영, 결정적 | "타입 기준"이 주 규칙이 아님 — 스펙 문구와 약한 정합, 게이트웨이 없는 토폴로지에서 근거 상실 |

**결정 (Decision):** Option A — 타입 밴드 레이아웃 (HPC 상단/게이트웨이 중앙/ECU 하단, 밴드 내 연결 링크 수 내림차순 → 이름 사전순, 링크 종류는 시각적 속성으로 구분)<br>
**결정 근거 (Rationale):** "타입 기준"이 직접 관찰 가능해 스펙 문구("노드 타입 기준 배치")와 정합 검증이 쉬움. 결정성이 구조적으로 보장되어 레이아웃 결정성(위 ADR) 요구와 정합. 사용자 승인 (2026-08-12, spec review F-6 해소).

### ASR-017 — 파일시스템 접근·보안 경계

**브라우저 파일 접근 (adr/dashboard-browser-file-access.md)** — ASR-015·ASR-019에도 적용되는 공유 ADR (F-11, 2026-08-12)

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| A. FS Access API 전용 | showOpenFilePicker/showSaveFilePicker로 실제 로컬 파일 직접 읽기·같은 파일 저장, 파일 API 불필요 | 진짜 "로컬 저장" UX(덮어쓰기), 서버 API·샌드박스·--root 제거, 보안 문제 소멸 | **Chrome/Edge 전용** — Firefox/Safari 미동작, 파일 목록은 디렉터리 핸들 권한 의존 |
| B. 업로드/다운로드 (범용) | `<input type=file>` 읽기, 서버 텍스트를 Blob 다운로드로 저장 | 모든 주요 브라우저 동작, 구현 단순, 권한 프롬프트 없음 | "저장"이 원래 파일 덮어쓰기가 아니라 다운로드 생성 — "로컬 저장" 의미 퇴색, 파일 목록은 다운로드 폴더·로컬스토리지 의존 |
| <b style="color:#1a7f37;">C. 하이브리드</b> | 지원 브라우저(Chrome/Edge)는 A의 직접 읽기/같은 파일 저장, 미지원은 B의 업로드/다운로드 | 현대 브라우저 최상 UX + 범용 지원, 서버 파일 API 제거 가능 | 두 경로 구현·테스트(기능 분기), 파일 목록 UX가 브라우저별 상이 |

**결정 (Decision):** Option C — 하이브리드 (FS Access 우선 + 업로드/다운로드 폴백). 서버 파일 API·`--root` 샌드박스 제거 — 파일은 브라우저가 직접 관리, 서버는 파일 내용(문자열)만 수신. 파일 삭제·이름 변경 미지원 유지.<br>
**결정 근거 (Rationale):** F-11 방향 전환의 핵심 — 파일 경계가 서버 경로 검증에서 브라우저 권한으로 대체되어 traversal 문제가 소멸. 하이브리드는 현대 브라우저 UX와 범용 브라우저 지원을 동시에 확보(전용 A는 Firefox/Safari 미동작, 업로드 B는 "로컬 저장" 의미 퇴색).

### ASR-018 — 편집·검증 피드백

**검증 피드백 (adr/editor-validation-feedback.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 서버 검증 (v1 Pydantic)</b> | 디바운스 500ms 서버 검증 API + 저장/실행 시 최종 검증, 줄 단위 인라인 오류 | v1 스키마 100% 재사용 — 진실 소스 단일화, 커스텀 규칙 포함 동작 | 타이핑 중 피드백이 서버 왕복 의존 (로컬이라 지연 미미) |
| B. 프런트엔드 검증 (JSON Schema 포팅) | v1 스키마를 JSON Schema로 변환해 입력 중 즉시 검증 | 즉시 피드백, 저장 불필요 | 스키마 파생·동기화 유지보수, 커스텀 규칙 별도 구현, 이중 진실 소스 리스크 |
| C. 하이브리드 | 프런트 경량(구조·타입) + 서버 정확(최종) | UX 최고(즉시+정확) | 구현량 최대 — B의 동기화 문제 + A의 구현 모두 부담 |

**결정 (Decision):** Option A — 서버 검증 (v1 Pydantic 스키마 그대로) — 디바운스(500ms) 자동 검증 + 저장/실행 시 최종 검증, 오류는 줄 단위 인라인, 유효 파싱 시에만 다이어그램 동기화. 프런트엔드 스키마 포팅 비목표.<br>
**결정 근거 (Rationale):** v1 Pydantic 스키마를 100% 재사용해 검증 진실 소스를 단일화 — JSON Schema 포팅(B)의 이중 관리·동기화 유지보수가 없고, 커스텀 규칙(참조 검증 등)이 그대로 동작. 로컬 서버 왕복 지연은 디바운스로 무시 가능.

### ASR-019 — 패키지 통합·서버 명령 (serve)

**serve 패키징 (adr/serve-packaging.md)**

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| <b style="color:#1a7f37;">A. 단일 프로세스 + 패키지 내부 자산</b> | dist를 `sdv_sim/server/static/`에 포함, serve가 자동 서빙, 개발 중 `--dev`로 Vite HMR 프록시 | 설치→실행 1줄 완결, 단일 프로세스, 배포 산출물 단순 | 프런트 수정 시 빌드 단계 필요, wheel 크기 증가 |
| B. 패키지 외부 dist 참조 | 정적 자산 경로를 인자/env로 수신 | 빌드·패키징 분리, 배포 유연 | 설치 후 즉시 실행 불가, 실행 환경 경로 의존 — "단일 명령" UX 약화 |
| C. serve 미제공 | 문서로 uvicorn 실행 안내 | 구현 최소화 | PRD 제공 형태와 불일치, 사용자 부담·포트/자산 수동 관리 |

**결정 (Decision):** Option A — 단일 프로세스 + 패키지 내부 정적 자산 (`sdv_sim/server/static/`, wheel 포함, `--dev`로 Vite dev server 프록시). 옵션 세트: `--port`/`--lang`/`--dev` (+ `--host`, 아래 참조). **F-11로 `--root` 옵션 제거.**<br>
**결정 근거 (Rationale):** `pip install → sdv-sim serve` 한 줄 완결(v1 UX 유지) — 배포 산출물 단순화가 최우선. 외부 dist 참조는 설치 후 즉시 실행이 불가능하고, serve 미제공은 PRD 제공 형태와 불일치.

**네트워크 바인딩 (adr/serve-network-binding.md)** — 2026-08-13 추가 승인

| 옵션 | 개요 | 장점 | 단점 |
|---|---|---|---|
| A. SSH 터널 유지 | `ssh -L 8888:127.0.0.1:8888` → 로컬 접근 | 코드·스펙 무변경, 서버 미노출, 인증 문제 없음 | 브라우저 주소가 원하는 `161.33.194.12:8888` 아님(터널 설정 필요), SSH 권한자만 사용 |
| <b style="color:#1a7f37;">B. --host 옵션 (기본 루프백)</b> | `--host 0.0.0.0`으로 바인딩 확장, 기본 127.0.0.1 유지 | 원하는 주소 직접 접근, 기본 동작(안전) 유지 | 스펙 제약 수정 필요, **인증 없는 서버가 인터넷 노출** — 방화벽으로만 보호 (현재 8888 개방) |
| C. HOST 상수 하드코딩 | serve.py를 0.0.0.0으로 영구 변경 | 옵션 없이 즉시 외부 접근 | 모든 실행에서 노출, 기본값 안전성 상실, 비문서화 — 비권장 |

**결정 (Decision):** Option B — `--host` 옵션 추가 (기본 127.0.0.1 루프백, `--host 0.0.0.0`으로 외부 접근) — 사용자 승인 (2026-08-13)<br>
**결정 근거 (Rationale):** 외부 접근이 필요하되 기본값 안전성은 유지. SSH 터널(A)은 사용자가 원하는 직접 접근이 불가능하고, 하드코딩(C)은 모든 실행에서 노출되는 비문서화 변경. 옵션 도입 시 방화벽 보호가 전제(스펙에 명시).

> 참고: 브라우저 파일 접근(--root 제거 영향)은 공유 ADR — 전체 표는 ASR-017 소절 참조 (결정: C — 하이브리드).

### ASR-020 — UI 언어 지원 (ko/en)

**direct-input (별도 ADR 없음 — v1 i18n 패턴을 프런트엔드에 대응)**

| 고려 사항 | 개요 | 장점 | 단점 |
|---|---|---|---|
| v1 패턴 대응 (선택) | --lang/env/로케일 우선순위를 프런트에 반영, 브라우저 로케일이 폴백 | CLI·대시보드 언어 결정이 일관, PRD 제약 충족 | 언어 상태 동기화(서버 옵션 vs 브라우저) 관리 필요 |
| 카탈로그 외부화 (선택) | UI 문자열을 하드코딩하지 않고 카탈로그 파일로 분리 | 다국어 추가 용이, 리뷰 용이 | 초기 구성 파일 관리 부담 |
| 언어 선택 UI (선택) | 대시보드에 언어 전환 컨트롤 제공 | 사용자 제어 명확 | UI 추가 |

**결정 (Decision):** direct-input — 프런트엔드 i18n 메시지 카탈로그 (ko/en, React 대상), v1 우선순위 패턴(`--lang`/env/브라우저 로케일) 대응, UI 문자열 하드코딩 금지·카탈로그 외부화, 언어 선택 UI 포함.<br>
**결정 근거 (Rationale):** PRD 제약("문서·CLI·대시보드 UI 출력은 한국어/영어 지원 구조") — v1 Python `i18n.py` 패턴을 React 대상 카탈로그로 대응. 별도 ADR이 필요 없을 만큼 v1 패턴과 정합(direct-input 해소).

### ASR-021 — 상시 실행 서비스 등록 (deploy)

**direct-input (cocrates-server/deploy 패턴 참조)**

| 고려 사항 | 개요 | 장점 | 단점 |
|---|---|---|---|
| systemd user unit (선택) | `deploy/sdv-simulator.service`: WantedBy=default.target, Restart=always/RestartSec=5, `%h/work/sdv-simulator`, `.venv/bin/sdv-sim serve --port 8888 --host 0.0.0.0`, SDV_SIM_LANG=ko | sudo 불필요, 부팅·장애 자동 복구, 로컬 전용 제약과 정합 | 사용자 세션에 종속(linger로 보완) |
| install/uninstall 스크립트 (선택) | unit 복사 → daemon-reload → enable --now → linger 활성화 / 해제 | 재현 가능한 등록·해제 절차 | 실패 시 수동 개입 필요 |
| 설치 보류 (선택) | 스크립트 제공만, 실행은 사용자 몫 | 시스템 변경이 사용자 결정에 의해서만 발생 | 대시보드가 등록되기까지 수동 실행 필요 |

**결정 (Decision):** direct-input — cocrates-server/deploy 패턴 미러: systemd user unit (`deploy/sdv-simulator.service`) + `deploy/install.sh` + `deploy/uninstall.sh`. **실제 설치는 보류** — 사용자가 필요 시 직접 실행.<br>
**결정 근거 (Rationale):** "부팅·장애 후에도 계속 실행" 요구에 systemd가 표준이고, user unit은 로컬 실행 전용(PRD 제약)과 충돌하지 않음(sudo·시스템 전역 등록 없음). ASR-019의 `serve --port 8888 --host 0.0.0.0`를 그대로 재사용. 설치 보류는 사용자 지시("실제 설치는 하지 말아줘") 반영.

## D.3 의존성 경로

ASR.md의 Dependency Order 재인용:

1. **v1 코어**: ASR-001 → ASR-002 → ASR-003 → ASR-004 → ASR-005 → ASR-006 → ASR-007
2. **상세 설계 ADR** (2026-08-12 전부 승인): simulation-time-model → definition-schema-structure → assertion-grammar → event-log-schema → can-fidelity-model → ethernet-fidelity-model → gateway-routing-rules → task-scheduling-policy → component-api → cli-output-policy → performance-targets
3. **2차 상세 설계 ADR** (D-12~D-21 전부 approved): definition-field-schema → communication-event-semantics → stub-component-behavior → public-api-contract → cli-io-contract → task-overrun-policy → frame-queue-overflow-policy → event-ordering-boundary → assertion-evaluation-detail → result-report-schema
4. **3차 검증 발굴 ADR** (U-1~U-6 전부 approved): event-ordering-non-task → ethernet-switch-selection → log-write-failure-exit-code → assertion-task-event-matching → assertion-count-minimum → ethernet-payload-basis
5. **v2 대시보드**: ASR-014 → ASR-019 → ASR-015 → ASR-016 → ASR-017 → ASR-018 → ASR-020
6. **F-11 방향 전환 재검토** (2026-08-12): ASR-006 (core-yaml-string-input) → ASR-015 (loads() 경로 재설계, dashboard-run-path superseded) → ASR-017 (브라우저 파일 접근) → ASR-019 (--root 제거) → (2026-08-13) serve-network-binding (--host 옵션)

---

*작성: 2026-08-13 · 출처: spec/ASR.md, adr/ (49건)*
