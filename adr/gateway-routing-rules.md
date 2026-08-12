# 게이트웨이 라우팅 규칙 (Gateway Routing Rules)

## Concern
게이트웨이 라우팅 규칙을 어떤 형식/의미로 정의할 것인가?

## Status
approved

## Decision
**Option A — from/to 명시 규칙 + 선택적 변환**
User-approved: routes = from(link + frame|id 범위) → to(link + remap_id 선택). 매칭 우선순위: 명시 frame > ID 범위. delay_ms 기본 0.

## Context
- ASR-004(L2 통신) 후속 — PRD 성공 기준 2(라우팅)의 대상
- 게이트웨이는 링크 간 프레임 전달의 핵심

## Options
### Option A — from/to 명시 규칙 + 선택적 변환
- `routes: [{from: {link, frame|id_min/id_max}, to: {link, remap_id?}}]`
- 매칭 우선순위: 명시 frame 이름 > ID 범위. 게이트웨이 처리 지연 `delay_ms`(기본 0)
- Pro: 라우팅 의도를 명시적으로 검증 가능, ID 변환(remap) 지원
- Con: 규칙 작성 필요 (자동 라우팅 대비 작성량)

### Option B — 자동 라우팅
- 두 링크에 모두 연결된 노드 = 자동 전달 (규칙 없음)
- Pro: 작성 부담 없음
- Con: 라우팅 의도가 코드에 숨음, 제어력 없음, 검증 가치 저하

### Option C — 신호 변환 포함
- DBC 스타일 신호 매핑·데이터 변환 규칙
- Pro: 실제 게이트웨이 데이터 변환 재현
- Con: v1 범위 초과 (L2는 프레임 단위)

## Tradeoffs
| | A (명시 규칙) | B (자동) | C (신호 변환) |
|---|---------------|----------|---------------|
| 라우팅 검증 | ★★★★★ | ★★ | ★★★★★ |
| 제어력 | ★★★★★ | ★★ | ★★★★★ |
| 작성 부담 | 중간 | 없음 | 높음 |
| v1 적합성 | ✓ | △ | ✗ |

## Recommendation (optional)
- **Option A** 추천: v1의 라우팅 검증 목표(PRD 성공 기준 2)를 직접 지원

## Consequences
- 매칭 기준: 프레임 이름 또는 ID 범위 (선택 remap_id)
- 데이터 변환(신호 레벨)은 v1 제외

## Related ASRs
- ASR-004 — 통신 프로토콜 충실도 — 라우팅 규칙 형식 결정

## Downstream Concerns
- [ ] **다중 홉 라우팅:** 규칙 체인을 통한 2홉 이상 전달 의미 확정

## Related
- {project-root}/adr/communication-fidelity-level.md — 상위 결정 (L2)

## Tags
`gateway`, `routing`, `can`, `ethernet`

## Approved
- 2026-08-12: Option A (from/to 명시 규칙 + remap_id), user confirmed
