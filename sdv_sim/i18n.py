"""ko/en message catalog for sdv-sim (D-16 localization).

Localization boundary (approved 2026-08-12):

- Error **category labels and common messages** (``입력 오류`` / ``input
  error``, ``스키마 오류`` / ``schema error``, ``파일을 읽을 수 없음`` /
  ``cannot read file``, ...) are localized through :func:`tr`.
- **Internal exception details** (component exception originals, OS-level
  detail) stay in their original language so debugging information is not
  obscured by translation.
"""

from __future__ import annotations

from typing import Any

MESSAGES: dict[str, dict[str, str]] = {
    "ko": {
        # CLI summary labels
        "simulation": "시뮬레이션",
        "result_pass": "통과",
        "result_fail": "실패",
        "links": "링크",
        "tasks": "태스크",
        "assertions": "Assertion",
        "warnings": "경고",
        "none": "없음",
        "link_cols": "링크  종류      tx    rx  drop  supersede  부하(%)",
        "task_cols": "노드  태스크  주기(ms)  실행  오버런",
        # Error categories
        "error_input": "입력 오류",
        "error_internal": "내부 오류",
        "error_write": "로그를 쓸 수 없음",
        # Structured diagnostics (SdvSimInputError codes)
        "file_read_error": "파일을 읽을 수 없음",
        "yaml_parse_error": "YAML 구문 오류: {detail}",
        "schema_error": "스키마 오류: {detail}",
        "field_suffix": "(필드: {field})",
        "injection_unknown_link": "주입이 알 수 없는 링크 {link!r}를 참조합니다",
        "injection_unknown_frame": (
            "주입이 링크 {link!r}에 정의되지 않은 프레임 {frame!r}을 참조합니다"
        ),
        "assertion_unknown_link": "assertion #{num}이(가) 알 수 없는 링크 {link!r}을 참조합니다",
        "assertion_unknown_frame": "assertion #{num}이(가) 알 수 없는 프레임 {frame!r}을 참조합니다",
        "assertion_unknown_message": "assertion #{num}이(가) 알 수 없는 메시지 {message!r}을 참조합니다",
        "assertion_unknown_node": "assertion #{num}이(가) 알 수 없는 노드 {node!r}을 참조합니다",
        "assertion_unknown_task": "assertion #{num}이(가) 알 수 없는 태스크 {task!r}을 참조합니다",
        # Server (v2 dashboard) messages
        "log_parse_error": "로그 JSON 파싱 오류: {detail}",
        "log_not_object": "로그 최상위가 JSON 객체가 아님",
        "log_schema_version": "지원하지 않는 로그 스키마 버전 {version!r} (필요: 1)",
        "log_simulation_invalid": "로그 simulation 필드 오류: {detail}",
        "log_events_not_list": "로그 events가 목록이 아님",
        "log_bad_event": "잘못된 이벤트 events[{index}]: {detail}",
        "log_unsorted": "events[{index}]가 (t_ms, seq) 오름차순 위반: (t_ms={t_ms}, seq={seq})",
        "log_bad_assertion": "잘못된 assertion assertions[{index}]",
        "log_assertions_invalid": "로그 assertions 필드 오류: {detail}",
        "log_invalid": "로그 검증 실패",
        "session_invalid": "세션이 없거나 무효화됨 — 실행 또는 로그 로드를 다시 시도하세요",
        "not_found": "요청한 리소스를 찾을 수 없음",
        "static_not_built": "대시보드 정적 자산이 아직 빌드되지 않음 (npm run build 실행 필요)",
        # Serve (CLI) messages
        "serve_started": "대시보드 실행 중: http://127.0.0.1:{port}",
        "serve_dev_hint": "개발 모드 — 대시보드 UI는 Vite dev server가 제공합니다 (frontend/ 에서 npm run dev; /api 프록시 대상: http://127.0.0.1:{port})",
        "serve_port_busy": "포트를 사용할 수 없음 (이미 사용 중)",
    },
    "en": {
        # CLI summary labels
        "simulation": "Simulation",
        "result_pass": "pass",
        "result_fail": "fail",
        "links": "Links",
        "tasks": "Tasks",
        "assertions": "Assertions",
        "warnings": "Warnings",
        "none": "none",
        "link_cols": "link  kind        tx    rx  drop  supersede  load(%)",
        "task_cols": "node  task  period(ms)  runs  overruns",
        # Error categories
        "error_input": "input error",
        "error_internal": "internal error",
        "error_write": "cannot write log",
        # Structured diagnostics (SdvSimInputError codes)
        "file_read_error": "cannot read file",
        "yaml_parse_error": "YAML parse error: {detail}",
        "schema_error": "schema error: {detail}",
        "field_suffix": "(field: {field})",
        "injection_unknown_link": "injection references unknown link {link!r}",
        "injection_unknown_frame": (
            "injection references frame {frame!r} not defined on link {link!r}"
        ),
        "assertion_unknown_link": "assertion #{num} references unknown link {link!r}",
        "assertion_unknown_frame": "assertion #{num} references unknown frame {frame!r}",
        "assertion_unknown_message": "assertion #{num} references unknown message {message!r}",
        "assertion_unknown_node": "assertion #{num} references unknown node {node!r}",
        "assertion_unknown_task": "assertion #{num} references unknown task {task!r}",
        # Server (v2 dashboard) messages
        "log_parse_error": "log JSON parse error: {detail}",
        "log_not_object": "log top-level is not a JSON object",
        "log_schema_version": "unsupported log schema version {version!r} (need: 1)",
        "log_simulation_invalid": "invalid log simulation field: {detail}",
        "log_events_not_list": "log events is not a list",
        "log_bad_event": "invalid event events[{index}]: {detail}",
        "log_unsorted": "events[{index}] violates (t_ms, seq) ascending order: (t_ms={t_ms}, seq={seq})",
        "log_bad_assertion": "invalid assertion assertions[{index}]",
        "log_assertions_invalid": "invalid log assertions field: {detail}",
        "log_invalid": "log validation failed",
        "session_invalid": "session missing or invalidated — run or load a log again",
        "not_found": "requested resource not found",
        "static_not_built": "dashboard static assets not built yet (run npm run build)",
        # Serve (CLI) messages
        "serve_started": "Dashboard running at http://127.0.0.1:{port}",
        "serve_dev_hint": "dev mode — dashboard UI is served by the Vite dev server (npm run dev in frontend/; /api proxied to http://127.0.0.1:{port})",
        "serve_port_busy": "port unavailable (already in use)",
    },
}


def tr(lang: str, key: str, **params: Any) -> str:
    """Look up a localized template and format it with ``params``.

    Falls back to Korean, then to the key itself when a language or key is
    missing (never raises for catalog gaps).
    """
    table = MESSAGES.get(lang) or MESSAGES["ko"]
    template = table.get(key, key)
    try:
        return template.format(**params)
    except (KeyError, IndexError, ValueError):
        return template
