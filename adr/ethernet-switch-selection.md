# Ethernet 스위치 다중 정의 정책 (Ethernet Switch Selection)

## Concern
Ethernet 링크의 `switches`에 2개 이상의 스위치가 정의되면 시뮬레이터는 어떻게 처리해야 하는가?

## Status
approved

## Context
- 검증(1차)에서 **미문서화 ASR U-2**로 식별 — ethernet-fidelity-model ADR은 "다중 스위치 토폴로지는 명시적 정의는 허용하되, v1 기본은 단일 스위치"로 선언했으나 **2개 이상 정의 시 동작은 미정**이었음
- 스펙 인코딩(2026-08-12) 시 "첫 번째만 사용 (스키마 오류 없음)"으로 결정되었으나 ADR 검토 없이 직접 인코딩됨
- 구현: `LinkRuntime.__init__`에서 `defn.switches[0].queue_depth`만 사용 — 실행 확인 exit 0
- 상위 결정: ethernet-fidelity-model (스위치 FIFO + 테일 드롭), definition-schema-structure (switches 필드)

## Decision
**Option A — 첫 번째만 사용, 스키마 오류 없음**
User-approved: `switches` 첫 항목만 큐잉 파라미터로 사용, 나머지는 무시 — v1 단일 스위치 모델과 Out of Scope 정합, 정의 파일 거부 없음.

## Options
### Option A — 첫 번째만 사용, 스키마 오류 없음 (현재 스펙/구현)
- `switches`의 첫 항목만 큐잉 파라미터로 사용, 나머지는 무시. 오류·경고 없음
- Pro: v1 단일 스위치 모델 유지, 정의 파일 호환성 최대, 구현 단순
- Con: 사용자가 다중 스위치를 기대했다면 조용히 무시됨 — 검증 관점에서 오해 가능

### Option B — 2개 이상 정의 시 스키마 오류
- `switches` 배열 길이 1 초과 시 스키마 검증 오류 (파일명·필드 경로 포함)
- Pro: 잘못된 기대를 즉시 표면화, 정의 파일 품질 향상
- Con: v1 범위(단일 스위치)를 벗어나는 정의를 명시적으로 거부하므로, "향후 다중 스위치"를 염두에 둔 사용자 정의 파일이 깨짐 — 범위 확장 시 스키마 변경 필요

### Option C — 다중 스위치 모두 모델링
- 정의된 모든 스위치를 독립 큐로 모델링 (토폴로지 연결 규칙 필요)
- Pro: L2 충실도 최대
- Con: v1 범위 초과 (토폴로지·라우팅 복잡도 급증), 스펙 Out of Scope 위반

## Tradeoffs
| | A (첫 번째만) | B (스키마 오류) | C (다중 모델링) |
|---|------|------|------|
| v1 범위 정합 | ✓ | ✓ | ✗ |
| 오류 표면화 | ✗ (조용한 무시) | ✓ (즉시) | ✓ |
| 향후 확장 호환 | ★★★★★ | ★★★ | — |
| 구현 비용 | 최저 | 낮음 | 높음 |

## Recommendation (optional)
- **Option A**: v1 단일 스위치 모델에서 다중 정의는 "미지원의 명시적 표현"보다 "첫 항목 사용"이 스펙 Out of Scope(다중 스위치 미지원)와 정합하면서도 정의 파일을 거부하지 않는다. 단, 경고 없음은 문서화로 보완.

## Consequences
- `switches[1:]`은 무시됨 — 스펙에 "첫 번째만 사용 (스키마 오류 없음)"으로 명시
- 다중 스위치 지원은 v2+ 후보로 Out of Scope 유지

## Related ASRs
- ASR-009 — Ethernet 스위치 다중 정의 정책 — 본 ADR이 직접 해소
- ASR-004 — 통신 프로토콜 충실도 (CAN/Ethernet) — 상위 ASR

## Downstream Concerns
- [ ] **경고 출력 여부:** 다중 정의 시 `--quiet` 아닌 실행에서 경고(warning)를 낼지 — 조용한 무시의 오해 가능성 완화 수단

## Related
- {project-root}/adr/ethernet-fidelity-model.md — 상위 결정 (스위치 FIFO + 테일 드롭)
- {project-root}/adr/definition-schema-structure.md — switches 필드 스키마

## Tags
`ethernet`, `switch`, `schema`, `policy`

## Approved
- 2026-08-12: Option A (첫 번째만 사용, 스키마 오류 없음), user confirmed
