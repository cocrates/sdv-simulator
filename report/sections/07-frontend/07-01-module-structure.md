# 7.1 프런트엔드 모듈 구조

프런트엔드(`frontend/`)는 React 19 + TypeScript + Vite 6 기반의 SPA이다.
백엔드(6장)와 달리 **파일을 소유하는 계층**이며(7.5절), 서버 API를 통해 코어에 접근한다.

주요 소스 모듈과 역할:

```
frontend/src/
├── App.tsx                 # 전역 상태·라우팅 소유 (7.2)
├── main.tsx                # 진입점, 언어 주입 (7.7)
├── api/
│   └── client.ts           # API 5종 호출 클라이언트 (6.2절 계약)
├── components/
│   ├── StructureView.tsx   # 구조 뷰 (SVG) (7.3)
│   ├── EditorPane.tsx      # YAML 편집기 (줄 단위 오류 표시)
│   ├── EventPanel.tsx      # 이벤트 로그 패널
│   └── ReportView.tsx      # 리포트 패널
├── replay/
│   ├── ReplayView.tsx      # 리플레이 뷰 (7.4)
│   ├── ReplayOverlay.tsx   # 구조 뷰 위 오버레이 렌더링
│   ├── replayIndex.ts      # 스냅샷 인덱스·시크 로직
│   └── useReplayClock.ts   # 재생 시계 (rAF, 배속)
├── fileManager.ts          # 파일 열기/저장·최근 파일 (7.5)
├── layout.ts               # 구조 뷰 결정적 레이아웃 계산 (7.3)
├── useValidation.ts        # 편집 검증 훅 (7.6)
├── i18n/                   # 번역 사전·언어 결정 (7.7)
├── types/
│   ├── schema.ts           # 서버 계약 타입
│   └── ...
└── yaml.ts                 # YAML 파싱·직렬화 헬퍼
```

계층 규칙: **컴포넌트(뷰) → 훅/모듈(로직) → api/client(계약)** 방향으로만 의존한다.
`replayIndex`·`layout`·`fileManager`는 React에 의존하지 않는 **순수 로직 모듈**로 분리되어
Node에서 직접 테스트된다 (11.2절).
