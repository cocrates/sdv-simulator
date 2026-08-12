# SDV Simulator 개발 대화 기록

> **프로젝트**: sdv-simulator (Software Defined Vehicle Simulator)
> **날짜**: 2026-08-12
> **목적**: SDV(소프트웨어 정의 차량) 시뮬레이터 구축 — spec-driven-generation 워크플로우 적용
> **워크플로우 위치**: Step 5 (시뮬레이터 생성) — T-008 진행 중, T-009(검증) 대기

---

## 대화 기록

### 1. 프로젝트 시작

**[user]** sdv(software defined vehicle) simulator를 만들려고 해.

**[cocrates]**
- 프로젝트 루트를 기존 폴더 `examples/sdv-simulator/`로 확정 (워크스페이스 Type 2: peer projects)
- spec-driven-generation 스킬 로드, Step 0(Spec Readiness Gate) 진입 → Gate 1 실패(PRD 미존재) → Step 1(PRD 작성)로 이동
- `examples/sdv-simulator/TODO.md` 초기화 — T-001(Step 1: PRD 작성)을 현재 진행 중으로 설정
- SDV 시뮬레이터의 "핵심 목적"을 묻는 첫 질문 제시 (한 번에 한 질문, 추천안 포함):
  - (A) 차량 소프트웨어 플랫폼 시뮬레이션 (E/E 아키텍처, HPC/ECU, 차량 내 통신, OTA, 앱 런타임) ← 추천
  - (B) ADAS/자율주행 시나리오·센서 시뮬레이션 (CARLA/SUMO 유형)
  - (C) 차량 동역학·물리 시뮬레이션
  - (D) 클라우드-차량 연동(OTA 배포, 원격 진단, 데이터 수집) 시뮬레이션
  - 추천 근거: SDV는 차량 기능이 소프트웨어로 정의되는 것을 핵심으로 하므로, 하드웨어 없이 차량 소프트웨어를 개발·검증하는 환경(A)이 가장 일반적인 용도. 목적에 따라 구조가 완전히 달라지므로 실제 의도 확인 필요.

---

### 2. 시뮬레이션 대상 확정 (A 선택)

**[user]** A로 하자.

**[cocrates]**
- 시뮬레이션 대상 = **차량 소프트웨어 플랫폼**으로 확정 (E/E 아키텍처, HPC/ECU, 차량 내 통신, OTA, 앱 런타임)
- Step 1(PRD 작성) 계속 — PRD의 두 번째 요소인 **대상 청중** 질문 제시 (추천안 포함):
  - (a) 차량 SW 개발자/아키텍트 — 개발·검증 도구 용도 ← 추천
  - (b) 연구자/학생 — 교육·연구 용도
  - (c) 데모/프레젠테이션 — 개념 소개용
  - (d) 개인 학습/포트폴리오 — 범위 대폭 축소 가능
  - 추천 근거: A(전체 차량 SW 플랫폼 시뮬레이터)는 규모가 있는 엔지니어링 프로젝트이므로, 사용자가 누구인지에 따라 충실도(fidelity)와 확장성 기준이 달라짐. 대상 청중 확정 후 아티팩트 형태(CLI/웹/라이브러리)와 범위 경계를 정하고 PRD 초안 작성 예정.

---

### 3. 대상 청중 확정 (a 선택)

**[user]** a

**[cocrates]**
- 대상 청중 = **차량 SW 개발자/아키텍트** (개발·검증 도구) 확정
- Step 1(PRD 작성) 계속 — 세 번째 요소인 **아티팩트 형태** 질문 제시 (추천안 포함):
  - (a) CLI — 자동화·CI 연동, 시나리오 스크립트 ← 추천
  - (b) 라이브러리/API — 테스트 하네스에 임베드
  - (c) 웹 대시보드 — 시각화·인터랙션
  - (d) 데스크톱 앱 — 로컬 GUI
  - 추천 근거: 개발자 대상 검증 도구는 무인 실행(자동화/CI)이 핵심이므로 CLI + 코어 라이브러리 조합이 적합. 시각화 대시보드는 이후 확장 단계로 연기 가능.

---

### 4. 아티팩트 형태 확정 (모두 선택)

**[user]** 모두

**[cocrates]**
- 아티팩트 형태 = **CLI + 라이브러리/API + 웹 대시보드 + 데스크톱 앱 모두 포함** 확정
- 범위 위험(모두 한 번에 = 과도한 엔지니어링)을 관리하기 위해 **단계별 스테이징(staging)** 제안:
  - 1차: 라이브러리 코어(헤드리스 시뮬레이션 엔진) + CLI — 무인 실행·자동화 기반
  - 2차: 웹 대시보드 — E/E 아키텍처·메시지 흐름 시각화, 인터랙션
  - 3차: 데스크톱 앱 — 웹 대시보드로 대체 가능성이 높아 연기 또는 씬 셸(shell)로 권장
- 스테이징 확정 후 A 내부 세부 범위(통신/OTA/앱 런타임 중 v1 포함 범위) 확인 예정

---

### 5. 스테이징 구도 승인

**[user]** 좋아

**[cocrates]**
- 스테이징 구도 승인 확정: 1차(라이브러리 코어 + CLI) → 2차(웹 대시보드) → 3차(데스크톱, 연기 가능). 모든 형태가 동일한 코어 엔진을 공유하는 원칙 확립
- 마지막 PRD 질문 제시 — A 내부 세부 범위 (v1 포함 범위):
  - (권장) v1 = E/E 아키텍처 모델링 + 차량 내 통신(CAN/Ethernet) + 앱 런타임(가상 ECU/HPC에서 SW 실행) / v2 = OTA
  - (확장) v1에 OTA까지 포함
  - 추천 근거: OTA는 별도 서브시스템(업데이트 캠페인, 버전 관리)으로 분리가 용이하고, v1의 핵심 검증 루프(정의→실행→검증)를 방해하지 않도록 뒤로 미루는 것이 안전.
  - 답변 확정 후 PRD 초안(`examples/sdv-simulator/spec/PRD.md`) 작성 및 승인 요청 예정.

---

### 6. v1 범위 확정 + PRD 초안 작성

**[user]** 오케이

**[cocrates]**
- v1 범위 확정: **E/E 아키텍처 + 차량 내 통신(CAN/Ethernet) + 앱 런타임**, OTA는 v2로 연기
- PRD 초안 작성: `examples/sdv-simulator/spec/PRD.md`
  - 배경·문제 정의, 목표(정의→실행→검증, 헤드리스 CLI, 라이브러리 코어, 단일 코어 공유), 대상 청중(차량 SW 개발자/아키텍트), v1/v2/v3 범위, 비목표(동역학, ADAS, OTA, HIL, 대시보드·데스크톱), 제약, v1 성공 기준 4가지
- ASR 레지스트리 초기화: `examples/sdv-simulator/spec/ASR.md` (템플릿)
- TODO.md 업데이트: T-001(PRD 작성) done, T-002(PRD 승인 gate) in_progress
- **PRD 승인 요청** — 승인 시 Step 2(ASR 식별)로 진행

---

### 7. PRD 승인 + Step 2 (ASR 식별) + Step 3 시작 (ASR-001)

**[user]** 좋아

**[cocrates]**
- **PRD 승인 확정** (Gate 1 통과) → Step 2(ASR 식별) 진행
- **ASR 7개 식별·등록** (`examples/sdv-simulator/spec/ASR.md`):
  - ASR-001 언어/기술 스택 / ASR-002 시뮬레이션 엔진 모델 / ASR-003 정의 형식 / ASR-004 통신 충실도 / ASR-005 앱 런타임 모델 / ASR-006 코어 API 경계 / ASR-007 검증·자동화
- **의존성 순서 제시**: 001 → 002 → 003 → 004 → 005 → 006 → 007
- **Step 3 시작**: ASR-001(언어/기술 스택) → `reviewing` 전환, ADR 초안 작성 (`examples/sdv-simulator/adr/language-tech-stack.md`)
  - Python / TypeScript / Go / Rust / C++(참고) 비교, **Python 추천**
  - 추천 근거: 헤드리스 시뮬레이터 + 임베드 + CI 자동화라는 v1 목표에 생산성이 최대 기여, 자동차 테스트 자동화 생태계 친화적, 성능 병목은 확장 모듈로 이관 가능
  - Downstream Concerns: 성능 전략, 패키징/배포, 정의 파일 형식(ASR-003)
- TODO 업데이트: T-002, T-003 done, T-004(Step 3) in_progress

---

### 8. ASR-001 승인 (Python) + ASR-002 ADR 작성

**[user]** 좋아 python으로 하자.

**[cocrates]**
- **ADR-001(`adr/language-tech-stack.md`) → approved**: Python 3.11+ 선택 (타입 힌트 + mypy, pip 패키지 + CLI 진입점, 병목 시 확장 모듈)
- **ASR-001 → designed** (Resolution: Python 채택)
- Downstream Concerns 제시: 성능 전략(ASR-002 연계), 패키징/배포, 정의 파일 형식(ASR-003)
- **ASR-002(시뮬레이션 엔진 모델) ADR 작성** (`adr/simulation-engine-model.md`):
  - DES / Time-step / Continuous 비교, **이산 사건(DES) + 주기 태스크 하이브리드** 추천
  - 추천 근거: 통신 지연·라우팅·대역폭(v1 핵심 검증 대상)의 정확한 재현 + 자동차 SW 주기 태스크 특성 반영 + 단일 스레드 결정성
  - Downstream Concerns: 시간 해상도(ASR-004 연계), 결정성 보장 수단, 앱 태스크 스케줄링 정책(ASR-005 연계)
- ASR-002 → reviewing 전환, 승인 요청 대기

---

### 9. ASR-002 승인 (DES) + ASR-003 검토 시작

**[user]** DES 기반으로 하자

**[cocrates]**
- **ADR-002(`adr/simulation-engine-model.md`) → approved**: 이산 사건(DES) + 주기 태스크 하이브리드 선택. 단일 스레드 + 고정 이벤트 순서로 결정성 보장
- **ASR-002 → designed** (Resolution: DES 기반 엔진, 앱 주기 태스크는 스케줄러가 이벤트로 생성·실행)
- **ASR-003(정의 형식) 검토 시작** — Direct Input 경로:
  - YAML / JSON / TOML / 전용 DSL 비교
  - 추천: YAML (인간 작성·가독성·주석·계층 표현, Python 생태계 PyYAML, 차량 도구 관행)
  - 승인 대기

---

### 10. ASR-003 확정 (YAML) + ASR-004 검토 시작

**[user]** YAML 좋아

**[cocrates]**
- **ASR-003 → designed** (Direct Input): YAML 채택. Downstream: 스키마 검증(Pydantic 추천), 아키텍처/시나리오 파일 분리 여부
- **ASR-004(통신 프로토콜 충실도) 검토 시작**:
  - L1 신호/메시지 수준 / L2 프레임·버스 수준(지연·대역폭·큐잉·게이트웨이 라우팅) / L3 물리·프로토콜 스택 수준
  - 추천: L2 — PRD 성공 기준 2(라우팅·지연·대역폭 결과 확인) 충족을 위해 대역폭·큐잉 모델 필요, L3(비트 타이밍 등)는 v1 과도
  - 승인 대기

---

### 11. ASR-004 확정 (L2 통신 충실도) + ASR-005 검토 시작

**[user]** 오케이

**[cocrates]**
- **ASR-004 → designed** (Direct Input): L2(프레임/버스 수준) 채택 — CAN 프레임 ID·주기·DLC 기반 우선순위/버스 부하, Ethernet 링크 대역폭·스위치 큐잉, 게이트웨이 라우팅. L3는 v1 제외
- Downstream: 지연 모델 파라미터, Ethernet 스위치 수준 범위
- **ASR-005(앱 런타임 모델) 검토 시작**:
  - (A) 메시지 구동 컴포넌트 / (B) 스레드·태스크 기반 / (C) 주기 태스크 + 이벤트 핸들러(RTE 스타일)
  - 추천: (C) — AUTOSAR RTE 관행과 일치, ASR-002(DES 하이브리드)와 정합, (B)는 결정성 위반
  - 승인 대기

---

### 12. ASR-005 확정 (RTE 스타일) + ASR-006 검토 시작

**[user]** 좋아

**[cocrates]**
- **ASR-005 → designed** (Direct Input): C(주기 태스크 + 이벤트 핸들러, RTE 스타일) 채택
- Downstream: 컴포넌트 실행 시간 모델, 컴포넌트 API 정의, 스케줄링 정책
- **ASR-006(코어 API 경계 & 다중 아티팩트 구조) 검토 시작**:
  - (A) 단일 패키지 + 모듈 경계(`sdvsim/core`, `sdvsim/cli`) / (B) 멀티 패키지 워크스페이스(`sdvsim-core`, `sdvsim-cli`) / (C) 단일 모듈
  - 추천: (A) — v1 오버헤드 최소화하면서 core/cli 경계 유지, 공개 API 계약(load/run/events/results)으로 임베드 지원, v2 대시보드는 같은 코어 백엔드 + 별도 프런트엔드
  - 승인 대기

---

### 13. ASR-006 확정 (단일 패키지 + `sdv-sim`) + ASR-007 검토 시작

**[user]** A로 하고, 패키지 이름은 sdv-sim으로 하자

**[cocrates]**
- **ASR-006 → designed** (Direct Input): A(단일 패키지 + 모듈 경계) 채택
  - 배포(distribution) 이름: `sdv-sim`, 임포트 이름: `sdv_sim` (Python 관례)
  - 내부 모듈: `sdv_sim/core`, `sdv_sim/cli`, 공개 API 계약(load/run/events/results)
- Downstream: 공개 API 계약 세부, 패키징 도구(src 레이아웃, hatch/setuptools/pdm)
- **ASR-007(검증·자동화 지원) 검토 시작** — 마지막 ASR:
  - (A) 선언형 assertion(YAML에 기대값) / (B) 이벤트 스트림 외부 검증 / (C) 둘 다
  - 추천: (C) — 엔진이 이벤트를 생성하므로 JSON 스트림 출력 비용 낮음, 선언형 assertion은 CLI의 1차 검증 UX
  - 승인 대기

---

### 14. ASR-007 확정 + Step 3 완료 → Step 4 (Spec 작성)

**[user]** 오케이

**[cocrates]**
- **ASR-007 → designed** (Direct Input): C(선언형 assertion + JSON 이벤트 스트림) 채택. CLI 종료 코드(0=pass/1=fail)로 CI 판정
- **Step 3 완료**: ASR-001~007 전부 designed. ADR 2건 승인(언어/엔진), Direct Input 5건(형식/통신/런타임/API 경계/검증)
- Downstream: assertion 문법 정의, 로그 스키마 정의
- **Step 4(Spec 작성) 진입**: spec-writing 스킬 로드, ASR resolution을 요구사항 Spec에 인코딩 예정
- TODO: T-004, T-005 done, T-006(Spec 작성) in_progress

---

### 15. 사양 구현 충분성 검토 (Gate 5)

**[user]** 작성된 사양이 구현에 충분한지를 검토해줘. 미진한 설계 검토가 무엇인지 확인해줘.

**[cocrates]**
- **Gate 5(Spec 충분성) 검토 수행** — `spec/sdv-sim-v1.md`를 PRD·ASR·ADR의 downstream 관점에서 갭 스캔
- **판정**: 아키텍처 수준 **충분** (ASR-001~007 resolution이 Decisions/Requirements/Constraints로 모두 인코딩, Out of Scope 명확, Open Questions 2건 명시) / 구현 상세 수준 **미흡**
- 핵심 지적: Open Questions가 "Step 5 상세 설계에서 확정(차단 아님)"이라 했으나, spec-driven-generation 워크플로우의 Step 5는 Spec에서 직접 생성하며 별도 상세 설계 게이트가 없음 → 이 갭들은 생성 시 조용한 기본값(발명)으로 처리될 위험
- **미진한 설계 검토 14건**:
  - **그룹 A (차단성 — 생성 시 발명 필연)**: ① 정의 파일 스키마 상세(architecture/scenario YAML 필드 구조, ASR-003 downstream) ② assertion 문법(시간 제약·메시지 속성·이벤트 조건 표현식, ASR-007 downstream, Open Q #1) ③ 이벤트 로그 JSON 스키마(이벤트 타입·필드·타임스탬프, ASR-007 downstream) ④ 시간 모델·단위(시간 단위, 타임스탬프 표현, 주기 메시지 첫 송신 규칙, ADR-002 downstream)
  - **그룹 B (정책·파라미터 — 모델 동작을 좌우)**: ⑤ CAN 버스 모델 파라미터(bitrate, 중재 규칙, 지연 계산식, 재전송/드롭 정책) ⑥ Ethernet 스위치 모델 파라미터(스위치 토폴로지, 포트 속도, 큐·드롭 정책) ⑦ 게이트웨이 라우팅 규칙 형식(매칭 기준, 신호/ID 변환) ⑧ 앱 스케줄링 정책(선점 여부, 오버런 처리; 실행 시간 모델은 Open Q #2로 인지) ⑨ 컴포넌트 API 시그니처(컴포넌트 작성자용 Python API 형태, ASR-005/006) ⑩ 시나리오 종료 조건(고정 시간·큐 소진·assertion 타임아웃)
  - **그룹 C (경미)**: ⑪ 난수/시드 사용처(v1에서 실제 난수 필요 여부) ⑫ i18n 언어 결정 방식(플래그/환경변수/locale) ⑬ 성능 목표(노드·메시지 규모, ADR-001 downstream) ⑭ 에러 분류·종료 코드 확장(스키마 오류 vs assertion 실패 vs 내부 오류)
- **ASR.md 레지스트리 문제 발견**: ASR-003~007이 Summary/Detail에 designed+identified 중복 행, 모든 ASR의 Spec 컬럼 "—" (T-007 승인 시 `spec/sdv-sim-v1.md` 기재 + approved 전환 필요)
- **후속 선택지 제시** (T-007 Spec 승인 전 결정 권장): ① 갭 전부 상세화(spec-writing으로 스키마·문법·로그 스키마·시간 모델을 Spec에 추가) ② 최소 기본값을 명시적으로 확정(예: 시간 단위=정수 ms, 큐=FIFO, assertion=단순 비교식 — silent default를 명시적 결정으로 승격) ③ 범위 축소로 갭 축소(예: 컴포넌트 API 제한, 단일 스위치 제한)
- TODO: T-006 유지(in_progress), Notes에 Gate 5 검토 결과 기록. Recommended next = 갭 해소 결정 후 Spec 반영 → T-007

---

### 16. 갭 해소 방식 선택 (① 전부 상세화) + 상세 설계 제안

**[user]** 1

**[cocrates]**
- **① 전부 상세화 선택 확인** — spec-writing 스킬 로드, 그룹 A/B/C 갭 14건에 대한 상세 설계 제안 작성 (승인 대기)
- **제안 요약 (상세 설계)**: 
  - **시간 모델(A4)**: 모든 시간은 정수 ms. 이벤트 = (t_ms, seq) 완전 순서로 결정성 보장. 주기 프레임/태스크는 t=0 첫 발생 후 매 period. 전파 지연 0 (지연은 큐잉/버스 점유만)
  - **정의 파일 스키마(A1)**: `architecture.yaml`(nodes: type/links없음·components/tasks(period·priority·wcet)·sends/receives, links: kind can|ethernet·bitrate·frames(name/id/dlc/period/source/message)·switches, gateways: routes) / `scenario.yaml`(duration_ms 필수, seed 선택, messages 주입, assertions)
  - **assertion 문법(A2)**: `expect { event: tx|rx|task, frame/message/node/link/task, at_ms, within_ms, count }`. 첫 매칭 이벤트 기준 시간 검증. 논리 결합·시퀀스는 v1 제외
  - **로그 스키마(A3)**: JSON — `events[] { t_ms, seq, type(tx|rx|task_start|task_end|drop|overrun|log), node/link/frame/task/data }` + `assertions[] { name, status, detail }`. (t_ms, seq) 오름차순
  - **CAN(B5)**: tx_ms = ceil((44+8·DLC)/bitrate_kbps). CAN ID 작을수록 우선, 버스 점유 시 큐 대기. 오류 프레임/재전송 v1 제외
  - **Ethernet(B6)**: frame_bytes = data+42, tx_ms = ceil(bytes·8/(Mbps·1000)). 스위치 FIFO 큐 + queue_depth(기본 1000) 초과 시 테일 드롭 → drop 이벤트
  - **게이트웨이(B7)**: routes = from(link + frame|id 범위) → to(link + remap_id 선택). 매칭 우선순위: 명시 frame > ID 범위. 처리 지연 delay_ms 기본 0. 신호 변환 v1 제외
  - **스케줄링(B8)**: 비선점, wcet_ms(기본 0=즉시), period 초과 시 overrun 이벤트+경고(우선순위 역전 미모델). 같은 시각: 우선순위(작을수록 우선) → seq
  - **컴포넌트 API(B9)**: `Component` 베이스(on_periodic/on_message) + `ctx.send(name, data)`. YAML class 필드 + `load(..., components={name: 클래스})` 등록. 미등록 시 스텁(통신 시뮬레이션만)
  - **종료(B10)**: duration_ms 도달 시 종료 후 assertion 평가
  - **기타(C11~C14)**: v1 난수 없음(seed는 스키마 유지·미사용), i18n = `--lang` 플래그 > `SDV_SIM_LANG` env > 시스템 로케일, 성능 목표 = 노드≤50·링크≤20·프레임≤200·이벤트≤1M·duration≤60s, 종료 코드 = 0 pass / 1 assertion fail / 2 입력 오류 / 3 내부 오류
- 승인 시 `spec/sdv-sim-v1.md`에 상세 설계 인코딩 + Open Questions 해소(assertion 문법·실행 시간 모델) + ASR.md 정리 예정
- TODO: Notes 갱신 (갭 해소 방식 = ① 전부 상세화 확정)

---

### 17. 설계 결정 사항 ADR 작성 (11건, proposed)

**[user]** 설계 결정이 필요한 사항을 ADR로 작성해줘.

**[cocrates]**
- adr-writing 스킬 로드, 병렬 세션에서 완료된 사후 ADR 5건(ASR-003~007)과 갱신된 ASR.md 확인
- **상세 설계 갭 14건을 설계 결정 concern 11건으로 분해해 ADR 전부 작성** (`adr/` 아래 11개, 전부 `proposed`):
  | ADR | Concern | 관련 ASR | 추천 옵션 |
  |-----|---------|---------|---------|
  | simulation-time-model | 시간 단위·진행·종료·난수 | ASR-002 | A: 정수 ms + (t_ms,seq) + duration_ms 종료 + 난수 없음 |
  | definition-schema-structure | YAML 스키마 구조 | ASR-003 | A: 메시지-프레임 2계층 분리 + 매핑 규칙 |
  | assertion-grammar | assertion 문법 | ASR-007 | A: YAML 선언형 expect 블록 |
  | event-log-schema | 이벤트 로그 JSON 스키마 | ASR-007 | A: 단일 events 배열 + type enum 7종 |
  | can-fidelity-model | CAN 지연·중재·부하 | ASR-004 | A: 비트 수식 + ID 우선 중재 + 큐 대기 |
  | ethernet-fidelity-model | Ethernet 스위치·큐잉 | ASR-004 | A: 프레임 크기 수식 + FIFO + 테일 드롭 |
  | gateway-routing-rules | 라우팅 규칙 형식 | ASR-004 | A: from/to 명시 규칙 + remap_id |
  | task-scheduling-policy | 스케줄링·오버런 | ASR-005 | A: 비선점 + wcet_ms + overrun 기록 |
  | component-api | 컴포넌트 Python API | ASR-005/006 | A: 베이스 클래스 + 콜백 + registry |
  | cli-output-policy | i18n·오류·종료 코드 | ASR-006/007 | A: --lang/env/로케일 + 0/1/2/3 |
  | performance-targets | 성능 목표·확장 전략 | ASR-001 | A: v1 순수 Python + 목표 규모 명시 |
- 각 ADR에 ≥2 viable options + tradeoffs + recommendation 포함, 기존 ADR 스타일 준수
- **ASR.md 동기화**: 관련 ASR-001~007 → `reviewing` 전환, 신규 ADR을 Related ADRs에 연결 (Resolution 유지)
- TODO: T-007 → pending (T-011 의존), T-011(상세 설계 ADR 작성·승인) in_progress
- **승인 게이트 제시**: 11건 전체 일괄 승인 또는 항목별 조정 후 승인 — 승인 시 Spec 보강 → T-007

---

### 18. 상세 설계 ADR 11건 승인 + Spec 인코딩 (T-011, T-012 완료)

**[user]** 전부 A 옵션으로 승인. (요약)

**[cocrates]**
- **ADR 11건 Status → `approved`** — Decision(선택 근거) 및 Approved(2026-08-12, 옵션 A, user confirmed) 기록
- **ASR.md 동기화**: ASR-001~007 상태 `designed` 유지 (Spec 동기화·사용자 확인 후 `approved` 전환 예정), Related ADRs에 승인 상태 반영
- **Spec 인코딩** (`spec/sdv-sim-v1.md` 보강, spec-writing 규칙: deep-copy + 자급자족):
  - Decisions 13개 그룹: 시간 모델(정수 ms + (t_ms,seq) + duration_ms 종료 + 난수 없음), 스키마 2계층(메시지-프레임 + 매핑 규칙), assertion 문법(expect 블록), 이벤트 로그 스키마(단일 JSON + type enum 7종), CAN 모델(ceil((44+8·DLC)/bitrate) + ID 우선 중재 + 큐 대기), Ethernet 모델(data+42 + FIFO + queue_depth 테일 드롭), 게이트웨이(from/to + remap_id + delay_ms), 스케줄링(비선점 + wcet_ms + overrun), 컴포넌트 API(on_periodic/on_message + load(components)), CLI 정책(--lang/env/로케일 + 종료 코드 0/1/2/3), 성능 목표(v1 순수 Python + 목표 규모)
  - Requirements 그룹별 검증 가능한 항목 추가, Out of Scope 7건 추가, Open Questions 해소(삭제), Constraints에 정수 ms·순수 Python 명시
- **TODO 갱신**: T-011·T-012 done (Done 9, In progress 1, Pending 2), T-007(Spec 승인 Gate) in_progress
- **승인 게이트 제시**: 보강된 Spec 요약 + T-007 승인 요청 — 승인 시 ASR-001~007 → `approved`, T-008(Step 5 생성) 시작

---

### 19. 사양 구현 충분성 재검토 (Gate 5 재검토 — SSOT 충분성 확인)

**[user]** 작성된 사양이 구현에 충분한지를 검토해줘. 미진한 설계 검토가 무엇인지 확인해줘. 스펙이 SSOT로 충분한지.

**[cocrates]**
- spec-driven-verification 스킬 로드 — `spec/sdv-sim-v1.md`를 PRD·ASR.md·상세 설계 ADR 11건과 대비해 항목별 갭 스캔 (T-012 인코딩 후 재검토)
- **판정**:
  - **아키텍처 SSOT: 충분** — ASR-001~007 resolution과 상세 설계 ADR 11건 결정이 Decisions/Requirements/Constraints로 인코딩, Out of Scope 13건이 ADR과 정합, 내부 모순 없음
  - **구현 SSOT: 아직 불충분** — 스펙만으로 구현 시 조용한 발명(기본값 임의 결정)이 필연인 지점 존재. ADR 참조 없이는 구현 불가
- **미진한 설계 검토 — 그룹 A (차단성, 구현 시 발명 필연 5건)**:
  1. **정의 파일 필드-레벨 스키마** — architecture/scenario YAML의 전체 필드 트리 + scenario `messages` 주입 형식(시각·링크·프레임·데이터 표현)이 스펙·ADR 모두에 미정 (definition-schema-structure Downstream open)
  2. **통신 이벤트 의미론** — CAN rx 범위(브로드캐스트 vs receives 매핑), Ethernet 노드↔스위치 흐름(tx→큐→rx 시점), 게이트웨이 라우팅의 이벤트 기록(누가 rx인지·원본 소멸 여부·다중 홉), 주입 메시지가 tx를 유발하는지 (gateway-routing-rules Downstream open)
  3. **스텁 컴포넌트 동작 의미론** — 미등록 컴포넌트가 sends 메시지를 주기 송신하는지, 주입에만 반응하는지 (YAML만으로 성공 기준 1·2를 충족시키는 핵심 경로인데 미정)
  4. **공개 API 시그니처** — load/load_scenario/run의 구체 인자·반환, "이벤트 스트림"의 형태(이터레이터·콜백·전체 버퍼), TaskContext 메서드 (component-api Downstream open)
  5. **CLI 출력 채널·플래그** — JSON 로그 출력 위치(stdout/파일/--output), 사람용 요약 포맷, 플래그 세트 (cli-output-policy Downstream open — CI 재사용 목표에 직결)
- **그룹 B (정책·엣지, Major 6건)**: ⑥ overrun 후 주기 처리(절대 주기 유지+스킵 vs 밀림) ⑦ CAN 큐 대기 중 period 초과 처리(최신 교체 vs 복수 큐잉) ⑧ 같은 시각·같은 우선순위 순서(컴포넌트 정의 순서, task-scheduling Downstream open) ⑨ assertion 평가 세부(count 대상=전체 로그?·`at_ms` 생략 의미가 ADR에만 있고 스펙 미인코딩·실패 메시지 형식) ⑩ 종료 경계(t==duration_ms 이벤트 포함 여부) ⑪ 버스 부하 리포트 항목·drop 집계 형식
- **그룹 C (경미 3건)**: ⑫ 성능 "수 초 내" 판정용 벤치마크 시나리오 ⑬ schema_version 정책(v1 고정 1로 사실상 충분) ⑭ i18n 오류 메시지 적용 범위
- **근거 요약**: ADR 11건 각각의 Downstream open 체크박스 ~11개 중 v1 관련 ~8건이 미해소 상태. 스펙 Related가 ADR을 "생성에 필수 아님"이라 선언했으나, 실제로는 `at_ms` 생략 의미처럼 ADR에만 있는 결정이 존재 → SSOT(자급자족) 위반 사례 확인
- **권고**: T-007(Spec 승인)를 지금 진행하지 말 것 — 그룹 A 최소 해소 후 승인 권장. 스펙에 스키마 예시(필드 트리) + 이벤트 의미론 + API/CLI 계약을 인코딩하면 구현 SSOT 확보 가능
- **후속 선택지**: ① 그룹 A+B를 spec-writing으로 스펙 상세화(권장) ② 결정 근거가 필요한 항목만 신규 ADR 5~6건 작성 ③ 범위 축소로 갭 축소(예: 스텁 송신 제거→주입 전용, 게이트웨이 rx 기록 단순화) ④ 그룹 C는 명시적 기본값으로 승격
- TODO: T-007 유지(in_progress), Notes + T-007에 재검토 결과 기록. 다음 액션 = 미진 항목 해소 방식 결정 → Spec 반영 → T-007 승인

---

### 20. 미진 설계 항목 ADR 생성·검토 (2차 상세 설계 ADR 배치, D-12~D-21)

**[user]** 미진한 내용에 대해 ADR를 생성해서 검토해줘.

**[cocrates]**
- adr-writing 스킬 로드 — Gate 5 재검토의 미진 항목(그룹 A 5건 + 그룹 B 6건 + C-14)을 **1 ADR = 1 concern** 규칙으로 **ADR 10건(D-12~D-21)** 재구성·작성 (전부 `proposed`)
- **ADR 세트**: D-12 definition-field-schema(필드-레벨 스키마+주입 형식) / D-13 communication-event-semantics(CAN rx·Eth 흐름·게이트웨이·다중 홉·주입→tx) / D-14 stub-component-behavior(스텁 송신 여부) / D-15 public-api-contract(시그니처·TaskContext) / D-16 cli-io-contract(출력 채널·플래그·i18n 오류) / D-17 task-overrun-policy(오버런 후속) / D-18 frame-queue-overflow-policy(큐 인스턴스 겹침) / D-19 event-ordering-boundary(동일 시각 순서·종료 경계) / D-20 assertion-evaluation-detail(count·at_ms 생략·실패 메시지) / D-21 result-report-schema(리포트 항목)
- **ADR 비대상(Direct Input)**: C-12 벤치마크 시나리오(구현 태스크), C-13 schema_version(스펙에 이미 `schema_version: 1`)
- **각 ADR 구조**: Concern + Context + Options ≥3(비-스rawman) + Tradeoffs 표 + Recommendation(전부 Option A 추천) + Downstream Concerns + Related ASRs
- **추천 요약 (전부 A)**: ① 완전 스키마+공식 예시 ② 수신자 매핑 기반 rx + 게이트웨이 link rx + 규칙 체인 다중 홉(홉 최대 8) ③ 스텁은 수신자 전용(sends 무시, tx는 주기 프레임·주입·실제 컴포넌트만) ④ 경로 기반 load/run→SimulationResult(events 리스트) ⑤ --log 파일(기본 events.json)+요약 stdout+--quiet ⑥ 절대 주기 유지+인스턴스 스킵 ⑦ 최신 교체(supersede) ⑧ 우선순위→정의 순서→seq + inclusive 종료 ⑨ count=전체 로그 총수, at_ms 생략=시간 무관 ⑩ 구조화 리포트(links·tasks·assertions·warnings)
- **ASR.md 동기화**: ASR-002~007 → `reviewing` 전환, Related ADRs에 신규 10건(proposed) 연결, Dependency Order에 2차 배치(3번) 추가. ASR-001은 변경 없음(designed 유지)
- **TODO 갱신**: T-007 → `pending`(T-015 의존 추가), 신규 T-013(ADR 작성·검토, `in_progress`)·T-014(ADR 승인 gate)·T-015(Spec 재인코딩) 추가. Snapshot: Done 9 / In progress 1 / Pending 5
- **승인 게이트 제시**: 10건 전체 일괄 승인 또는 항목별 조정 후 승인 — 승인 시 Status→approved + ASR.md 동기화 → T-015(Spec 인코딩) → T-007(Spec 승인) → T-008(생성)
- **실제 상태 점검**: 이전 기록과 달리 실제 파일시스템 기준으로는 ADR 10건이 전부 `approved`로 확정되어 있었으나(Approved: 2026-08-12, user confirmed) ASR.md·TODO.md·Spec 인코딩은 미반영 상태였음. 실제 파일을 SSOT로 삼아 동기화 진행.
- **T-014 완료 확인**: D-12~D-21 10건 전부 approved (파일 검증) → TODO Completed 이동
- **ASR.md 동기화**: 2차 ADR 10건 `(proposed)` → `(approved)` (Summary + Detail), ASR-002~007 Summary `reviewing` → `designed`, Dependency Order "전부 proposed" → "전부 approved"
- **T-015 (Spec 인코딩) 완료** — spec/sdv-sim-v1.md에 deep-copy 반영:
  - Context: 상세 설계 ADR 21건(1차 11 + 2차 10)으로 갱신
  - Decisions 신규 하위 섹션 9개: 필드-레벨 스키마 & 메시지 주입(D-12, 공식 YAML 예시 포함) / 통신 이벤트 기록 의미론(D-13, rx 수신자 매핑·게이트웨이 인프라·홉 최대 8) / 프레임 큐 인스턴스 정책(D-18, 최신 교체) / 스텁 컴포넌트 동작(D-14, 수신자 전용) / 태스크 오버런 정책(D-17, 절대 주기+스킵) / 공개 API 시그니처(D-15, load/run→SimulationResult/TaskContext) / CLI 입출력 채널(D-16, --log 기본 events.json, --quiet) / Assertion 평가 규칙(D-20, at_ms 생략=시간 무관, count=전체 로그) / 결과 리포트(D-21, links/tasks/assertions/warnings, bus_load_percent = tx_ms 합/duration_ms)
  - 시뮬레이션 엔진 & 시간 모델에 D-19 추가(같은 시각 순서: 우선순위→정의 순서→seq, 종료 inclusive)
  - Requirements +14건, Out of Scope +7건(스텁 자동 송신·브로드캐스트 rx·게이트웨이 노드화·상대 주기·큐 복수 큐잉·콜백/이터레이터 API·홉 8 초과), Related 갱신
- **TODO**: T-013·T-014·T-015 done (Done 12), T-007 in_progress — Snapshot: Done 12 / In progress 1 / Pending 2 (T-008·T-009)
- **T-007 승인 게이트 제시**: 인코딩 반영 후 Spec 재검토·승인 요청 — 승인 시 ASR-001~007 → approved, T-008(Step 5 생성) 시작

---

### 21. Spec 승인 (T-007) + Step 5 생성 시작 (T-008)

**[user]** uv로 venv를 생성하고 개발해줘.

**[cocrates]**
- 사용자 지시("uv venv 개발")를 **Spec 승인 신호로 간주** — Gate 5 재검토 2회 통과(아키텍처/구현 SSOT 충분성) 확인 후 T-007 done 처리
- **ASR-001~007 → `approved` 전환** (designed → approved)
- **T-008 (Step 5: 시뮬레이터 생성) 시작** — 워크플로우 위치 Step 5 진입
- 환경: uv 0.11.3 + Python 3.12.3 (Spec 요구 3.11+ 충족). 생성 후 spec-driven-verification(T-009) 권장
- **패키지 구조** (src 레이아웃, hatchling 빌드, 배포명 `sdv-sim` / 임포트명 `sdv_sim`):
  - `sdv_sim/core/` — `engine.py`(DES 이벤트 큐, 고정 순서 `(t_ms, priority, decl, seq)` 결정성, CAN ID 우선 중재 + 우선순위 큐, Ethernet 스위치 FIFO + `queue_depth` 테일 드롭, 게이트웨이 규칙 체인(홉 최대 8), 비선점 태스크 스케줄링 + 오버런 감지), `component.py`(Component 베이스 + TaskContext), `events.py`, `report.py`, `errors.py`(i18n 오류 분류)
  - `sdv_sim/schema/` — `arch.py`, `scenario.py` (Pydantic 검증, YAML 줄번호·필드 경로 매핑 오류 메시지)
  - `sdv_sim/cli/main.py` — `sdv-sim run <architecture.yaml> <scenario.yaml> [--log events.json] [--quiet] [--lang ko|en]`, 종료 코드 **0=pass / 1=assertion fail / 2=입력 오류 / 3=내부 오류**, 언어 결정 `--lang > SDV_SIM_LANG > 로케일`
- `pyproject.toml`: sdv-sim 0.1.0, requires-python ≥3.11, 의존성 pyyaml+pydantic, dev = mypy(strict)+pytest+types-PyYAML
- **테스트 9개 파일 작성**: test_api / test_assertions / test_can / test_cli / test_ethernet / test_gateway / test_schema / test_tasks + conftest
- **생성 시 해석 결정 5건 명시** (조용한 발명 방지 — TODO.md Notes 기록, T-009에서 재확인 예정):
  1. tx 이벤트 시각 = 실제 전송 시작 시각 (D-18 "최종 전송된 인스턴스만" 정합)
  2. Ethernet payload = 프레임 dlc 바이트 (bytes = dlc + 42)
  3. assertion count = "최소 n건" (≥, 공식 예시 정합)
  4. 태스크 스케줄링 = 자체 오버런에 덮인 인스턴스만 스킵 (노드 자원 경쟁 미모델 — v1 제외 정합)
  5. on_message 핸들러 = 시간 진행 없음 (D-17 downstream open 기본값 명시화)
- pytest 실행 → **실패 5건** 원인 분석 후 수정 (3건은 테스트 버그, 1건은 엔진 버그, 1건은 기대값 정정):
  1. **test_api.py (테스트 버그)**: 종료 경계 inclusive(D-19) — t=100 송신의 rx는 t=101 > duration로 미처리 → `rx_count` 12→11, "got temp" 로그 12→11
  2. **test_gateway.py (테스트 버그)**: 주기 f도 라우팅되어 can2에 tx 2건 발생 → `tx2[0]` 고정 인덱스 대신 `any(e.data == {"v": 7})`로 주입 데이터 검사
  3. **test_can supersede (엔진 버그)**: D-18 "동일 프레임의 새 인스턴스 도착 시 최신 교체" 위반 — slow bus(tx=11ms, period=1ms)에서 t=11에 버스가 비는 순간 도착한 인스턴스가 supersede해야 하는데, 기존 `drain()`은 pending+queue를 병합 후 arrival_seq 정렬로 **오래된 큐 인스턴스가 전송 우선** → `drain()` 시작 시 pending 도착분이 이전 tick 큐의 동일 프레임을 supersede하도록 엔진 수정 (supersede_count 9→10)
  4. **test_assertions first_match (테스트 버그)**: 주석은 "rx at t=1, 11, 21" 의도(period 10)였으나 `_arch()`가 period_ms=100 → 공용 `_arch()`는 100 유지(다른 테스트 의존), period 10 전용 아키텍처로 테스트 수정
  5. **test_ethernet tail_drop (기대값 정정)**: 주기 b/c도 t=0에 발생(D-13 경로 1) → queue_depth=2에서 periodic c·injected c **2건** 드롭, injected b→periodic b supersede 1건. 시뮬레이터는 충실하므로 기대값을 실제 의미론에 맞게 수정 (drop 1→2, supersede 1 추가 검증)
- **최종 상태**: 63 passed / mypy strict 통과 (12개 소스 파일, Success)
- **다음 권장**: T-009 — spec-driven-verification으로 스펙 대비 검증 (TODO.md에 대기 등록됨)

---

### 22. 사양 대비 구현 검증 (T-009)

**[user]** 사양 대로 구현되었는지를 확인해줘.

**[cocrates]**
- spec-driven-verification 스킬 로드 — `spec/sdv-sim-v1.md`(+PRD.md)를 기준으로 구현 산출물을 항목별 검증
- **오리엔테이션**: 프로젝트 루트 `workspace/softwares/sdv-simulator/` 확인. `.venv`이 gitignore 대상이라 소실됨 → `uv venv --python 3.12` + `uv sync --extra dev`로 재생성
- **실행 확인**: `uv run pytest` → **63 passed** / `uv run mypy` → **Success (12 source files, strict)**
- **검증 리포트 작성**: `verification/sdv-sim-v1.md` — 인벤토리 81건 (78 pass / 1 fail / 2 partial)
- **Deviation 1 (Major — 스펙 결함, 코드 아님)**: D-12 **공식 예시가 자기 의미론과 비정합**
  - 그대로 실행 → exit 2: 링크 `can1`이 `door_ecu` 참조하나 예시의 `nodes`에 정의 없음 (스펙 자체 규칙 "미정의 참조 = 스키마 오류"에 걸림)
  - `door_ecu` 추가 후 재실행 → exit 1: assertion `cmd_sent`의 `at_ms: 5`가 주기 프레임 `door_cmd`의 **t=0 첫 tx**에 먼저 매칭되어 실패 (D-8 주기 t=0 + D-20 첫 매칭 기준 — 엔진은 충실, 예시만 부정합)
  - 권고: spec-writing으로 예시 수정 (door_ecu 노드 추가 + assertion 시맨틱 정합)
- **Deviation 2 (Minor)**: D-16 "오류 메시지도 --lang" — 카테고리 라벨만 로컬라이즈, Pydantic/YAML 상세 메시지는 영어 유지 (partial)
- **Undocumented ASR 6건 식별 (U-1~U-6)**:
  - U-1: 같은 tick에서 비-태스크 이벤트는 태스크 뒤에 처리 (`MAX_PRIO=2^30`) — D-19가 태스크↔비-태스크 상대 순서 미정의
  - U-2: 스위치 2개 이상 정의 시 첫 번째만 사용, 검증 없음 (스펙 "단일 스위치")
  - U-3: 로그 쓰기 실패 시 종료 코드 2 (스펙 미분류)
  - U-4: `event: task` = task_start+task_end 둘 다 매칭 (스펙 미정의)
  - U-5: count = "최소 n건(≥)" — 생성 시 해석 #3과 정합, 스펙 문구 "총수" 명확화 권장
  - U-6: Ethernet payload = DLC 바이트 (bytes = dlc+42) — 생성 시 해석 #2와 정합
- **TODO 갱신**: T-008 done (생성 완료), T-009 in_progress (리포트 초안 완료 → 리뷰 게이트)
- **판정 요약**: 구현 코드는 스펙 시맨틱을 충실히 구현 (81건 중 78 pass). 수정 대상은 **스펙의 예시·문구**이지 코드가 아님. 다음 액션 = 사용자 리뷰 후 spec-writing으로 스펙 수정 → 재검증 루프

---

### 23. 스펙 수정 + i18n 로컬라이즈 (T-016, Deviation 1·2 해소)

**[user]** 잘못된 스펙의 공식 예시를 수정해줘. 오류 메시지도 ko/en 출력으로 수정해줘.

**[cocrates]**
- **승인 게이트**: 수정 계획 2건 제시 → 사용자 "1" = 권장안 승인 (① assertion `at_ms: 0, count: 12` ② 로컬라이즈 경계: 카테고리·공통 메시지 ko/en, 내부 예외 상세 원문 유지)
- **스펙 수정 (spec-writing)** — `spec/sdv-sim-v1.md`:
  - 공식 예시: `door_ecu` 노드 정의 추가 (door_act 컴포넌트, receives: [door_cmd]), assertion `{event: tx, frame: door_cmd, link: can1, at_ms: 5}` → `{at_ms: 0, count: 12}` (주기 t=0~100 11건 + 주입 t=5 1건, D-19/D-20 정합)
  - **U-1~U-6 전부 스펙 인코딩**: D-19 비-태스크 이벤트는 태스크 뒤(MAX_PRIO) / L2 `bytes = dlc + 42` + switches 첫 번째만 사용 / CLI 로그 쓰기 실패 = exit 2 / D-20 `event: task` = start+end 둘 다, count = "최소 n건 이상(≥), 초과는 실패 아님" / D-16 오류 로컬라이즈 경계 명시
- **i18n 구현**:
  - `sdv_sim/i18n.py` 신설 — ko/en 메시지 카탈로그 + `tr(lang, key, **params)` (폴백: ko → 키)
  - `SdvSimInputError` 재구성 — `code + params + filename/line/field`, `.format(lang)` 렌더, `str()`은 영어 유지 (라이브러리 기본)
  - `engine.py` `_validate_scenario_model`/`_load_yaml_model` 오류 → code+params 전환, `cli/main.py` `_KO`/`_EN`/`_msg` → `tr()` 통합, `SdvSimError` 분기도 로컬라이즈
- **검증**: pytest **63→78 passed** (신규 `test_i18n.py` 15건: 카탈로그 일관성, format ko/en, CLI 로컬라이즈, 내부 상세 원문 유지), mypy **13 source files** strict 통과
- **실행 확인**: 공식 예시 exit 0 (`cmd_sent: matched 12 event(s); first at t=0`), `--lang ko` → `입력 오류: ... 스키마 오류: ... (필드: ...)`, `--lang en` → `input error: ... schema error: ... (field: ...)`, 로그 쓰기 실패 exit 2, U-4 task=start+end 21건 매칭, U-1 t=0 task_start(seq 3)→tx(seq 10)
- **재검증 리포트 갱신**: `verification/sdv-sim-v1.md` — **86 pass / 0 fail / 0 partial** (인벤토리 #82~#85 신규: U-1~U-4, U-5·U-6은 기존 #76·#38 갱신)
- **TODO 갱신**: T-016 in_progress (재검증 게이트), T-009 done 처리, T-017 pending (v2 스테이징 대기)
- **다음**: T-016 사용자 리뷰 승인 → v1 완료 / v2 대시보드 스테이징 논의

---

### 24. Undocumented ASR(U-1~U-6) ADR 설계 검토 정식화 (T-018)

**[user]** Undocumented ASR에 대해서 설계 검토가 필요한 내용을 ADR로 작성해줘.

**[cocrates]**
- adr-writing 스킬 로드 — 검증(T-009)에서 식별된 U-1~U-6이 스펙에는 인코딩됐으나 ADR 설계 검토 없이 직접 인코딩된 상태임을 확인. 6건 모두 독립 설계 결정 포인트(≥2 유효 대안 존재)로 판단
- **작성 방식 승인 게이트**: 신규 ADR 6건 + ASR-008~013 등록(권장) vs 기존 ADR 병합 vs 일부 항목만 → 사용자 권장안 승인
- **ADR 6건 작성** (`adr/`, 전부 `proposed` → Option A 추천):
  | ADR | Concern | Option A (스펙 인코딩 내용과 정합) | 대안 |
  |-----|---------|-----------------------------------|------|
  | event-ordering-non-task.md (ASR-008) | 같은 tick 비-태스크 이벤트 위치 | 모든 태스크 뒤 (가상 우선순위 2^30, 원인→결과 보장) | 선언 순서 통합 / 태스크 앞 |
  | ethernet-switch-selection.md (ASR-009) | switches 2개 이상 정의 시 | 첫 번째만 사용, 스키마 오류 없음 | 스키마 오류 / 다중 모델링 |
  | log-write-failure-exit-code.md (ASR-010) | 로그 쓰기 실패 시 종료 코드 | 2 (입력 오류로 분류) | 3(내부 오류) / 4(I/O 전용) |
  | assertion-task-event-matching.md (ASR-011) | `event: task` 매칭 범위 | task_start + task_end 둘 다 | start만 / end만 |
  | assertion-count-minimum.md (ASR-012) | count: n 비교 연산 | 최소 n건(≥), 초과는 통과 | 정확히 n(==) / 최대 n(≤) |
  | ethernet-payload-basis.md (ASR-013) | Ethernet payload 크기 기준 | 프레임 DLC 바이트 (bytes = dlc + 42) | data 객체 크기 / max·설정 |
- **ASR.md 동기화**: ASR-008~013 신규 등록(`reviewing`), Related ADRs(proposed) 연결, Dependency Order에 3차 배치 추가
- **TODO**: T-018 추가(pending), Snapshot 16/1/2
- **리뷰 게이트**: 6건 전체 승인 / 항목별 승인 / 옵션 변경 / 수정 요청 중 선택 요청
- **승인 후 (사용자 전체 Option A 승인)**:
  - ADR 6건 Status → `approved`, Decision + Approved(2026-08-12, user confirmed) 기록
  - ASR-008~013 → `designed` 전환 + Resolution 기록 (스펙 인코딩 완료 상태 반영)
  - TODO: T-018 done, T-016 done(재검증 게이트 마감), T-017 pending — Snapshot 17/0/1
  - 스펙 변경 불필요: 결정 6건은 이미 `sdv-sim-v1.md`에 인코딩 + 재검증 86 pass 통과 — ADR은 감사 추적(사후 설계 검토) 완성 목적
  - **Downstream Concerns 기록**: ① U-1 관련 — 같은 tick 컴포넌트 tx vs 주기 프레임 tx 공존 시 원인-결과 순서 문서화 ② U-2 관련 — 다중 스위치 정의 시 경고 출력 여부 ③ U-5 관련 — 정확 개수(==) 검증 `count_exact` 도입 여부 (v1 범위 결정)
- **다음**: v1 마무리 확인 / Downstream Concern ADR 검토 / v2 대시보드 스테이징(T-017) 논의


