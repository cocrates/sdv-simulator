# 8. 핵심 데이터 흐름

4·5·6·7장에서 설명한 구성 요소가 하나로 묶여 움직이는 **통합 흐름**을 보여준다.
시스템에는 두 개의 진입 흐름이 있다: ① 대시보드에서 정의를 편집·실행하는 **run 경로**,
② 기존 로그 파일을 불러와 재현하는 **load-log 경로**. CLI의 `run`은 ①의 서버 없이 코어를
직접 호출하는 변형이다. 모든 데이터는 문자열/YAML/JSON으로 서버를 통과한다.

## 8.1 run 경로 (대시보드 실행)

```mermaid
sequenceDiagram
    participant U as 사용자
    participant F as 프런트엔드
    participant S as 서버 (FastAPI)
    participant C as 코어 (loads/run)

    U->>F: 파일 열기 (FS Access API / 폴백)
    F->>F: EditorFile 상태 (arch, scenario)

    loop 편집 중
        U->>F: YAML 편집
        F->>S: POST /api/validate (500ms 디바운스)
        S->>C: 스키마 검증 (3.3절)
        S-->>F: {ok} / {ok:false, errors}
        F->>F: 줄 단위 오류 표시 / 구조 뷰 동기화
    end

    U->>F: 실행 클릭
    F->>F: forceValidate — 즉시 검증
    F->>S: POST /api/run (YAML 문자열 2개)
    S->>C: loads() + run()
    C-->>S: SimulationResult
    S->>S: 세션 교체 (last-write-wins)
    S-->>F: {events_count, duration_ms, result}
    F->>F: invalidated = false

    F->>S: GET /api/events · /api/report
    S-->>F: 이벤트(정렬) · 리포트
    F->>F: 리플레이 뷰 / 리포트 뷰 렌더링
```

- 편집은 서버와 독립적으로 진행되며, 검증만 서버를 거친다.
- 실행은 **YAML 문자열**로 서버에 전달되고, 결과 이벤트·리포트는 **JSON**으로 돌아온다 —
  어느 단계에서도 파일 경로가 오가지 않는다 (2.4절 ④).
- 세션이 교체되면 프런트의 `invalidated`가 꺼져, 현재 편집 내용과 실행 결과가 일치함을
  보장한다 (7.6절).

## 8.2 load-log 경로 (로그 파일 재현)

```mermaid
sequenceDiagram
    participant U as 사용자
    participant F as 프런트엔드
    participant S as 서버 (FastAPI)
    participant L as log_loader

    U->>F: events.json 파일 선택 (+arch 선택적)
    F->>S: POST /api/load-log (내용 문자열)
    S->>L: 파싱·구조 검증

    alt 검증 실패
        S-->>F: 400 log_invalid (F-8 계약)
    else 성공
        L->>L: M-1 리포트 파생 (6.5절)
        S->>S: 세션 교체
        S-->>F: {events_count, duration_ms, result}
        F->>F: invalidated = false
        F->>S: GET /api/events · /api/report
        S-->>F: 이벤트 · 리포트
        F->>F: 리플레이 뷰 렌더링
    end
```

- CLI가 남긴 `events.json`(5.2절)이 이 경로의 대표 입력이다. 실행 없이 같은 리플레이·
  리포트를 웹에서 재현한다.
- 아키텍처를 함께 주면 버스 점유율 등 M-1 보강 항목이 리포트에 포함된다 (6.5절).

## 8.3 재생·시크 흐름

리플레이 뷰 내부의 시간 축 이동은 7.4절의 설계를 따른다:

```
이벤트 로드 (이미 (t_ms, seq) 정렬) → 스냅샷 인덱스 생성 (K=2000)
→ seekToTime(시크) = 이분 탐색 + 잔여 증분 재적용
→ advanceToTime(재생) = 증분 적용 (rAF 루프)
→ ReplayOverlay가 구조 뷰 위에 상태 렌더링
```

run 경로와 load-log 경로 중 어느 쪽으로 세션이 만들어졌든, 이벤트는 같은 정렬 계약을
따르므로 리플레이 로직은 하나로 재사용된다.
