"""FastAPI app for the v2 dashboard (spec/sdv-sim-v2.md, API section).

Endpoints (API 5종):

- ``POST /api/validate`` — schema validation of architecture/scenario YAML.
  Pure validation: it does **not** invalidate the session. Edit-time session
  invalidation is a frontend-local state (``SessionMeta.invalidated``, M-4 —
  T-024; the API surface no longer needs a dedicated invalidation signal).
- ``POST /api/run`` — v1 ``loads(arch, scenario)`` + ``Simulator.run()``,
  replaces the session (source="run"), returns a lightweight result plus the
  full Report (events are fetched via ``GET /api/events``).
- ``POST /api/load-log`` — validates a browser-provided v1 events.json, replaces
  the session (source="log"); ``arch_content`` enables the full Report (M-1).
- ``GET /api/events`` — current session events, sorted by ``(t_ms, seq)``.
- ``GET /api/report`` — current session Report (M-1 rules for log sessions).

Errors follow F-8: every error is ``{error: {code, message, detail?}}`` with
machine-readable ``code`` (``validation_error``/``log_invalid``/``session_invalid``/
``not_found``/``internal``), localized ``message``, and optional validation
``detail`` items ``{path, line, message}``. 409 ``session_invalid`` answers
events/report when the session is absent (F-7).

The server never touches the filesystem for user files (F-11): all YAML/JSON
content arrives as strings and the browser manages local files itself.
"""

from __future__ import annotations

import re
from dataclasses import asdict
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from sdv_sim.core.engine import _parse_yaml_text, loads
from sdv_sim.core.errors import SdvSimError, SdvSimInputError
from sdv_sim.core.events import Event
from sdv_sim.i18n import tr
from sdv_sim.schema.arch import Architecture
from sdv_sim.schema.scenario import Scenario
from sdv_sim.server.log_loader import LogValidationError, derive_report, parse_log
from sdv_sim.server.session import Session, SessionStore

_STATIC_DIR = Path(__file__).parent / "static"


# ------------------------------------------------------------------- request models


class ValidateRequest(BaseModel):
    kind: Literal["architecture", "scenario"]
    content: str
    arch: str | None = None


class RunRequest(BaseModel):
    architecture: str
    scenario: str


class LoadLogRequest(BaseModel):
    name: str | None = None
    content: str
    arch_content: str | None = None


class ErrorItem(BaseModel):
    path: str | None = None
    line: int | None = None
    message: str


class ValidateResponse(BaseModel):
    valid: bool
    errors: list[ErrorItem]


# --------------------------------------------------------------------------- helpers


def _error(
    code: str,
    message: str,
    *,
    status: int = 422,
    detail: list[dict[str, Any]] | None = None,
) -> JSONResponse:
    body: dict[str, Any] = {"error": {"code": code, "message": message}}
    if detail is not None:
        body["error"]["detail"] = detail
    return JSONResponse(status_code=status, content=body)


def _event_to_dict(event: Event) -> dict[str, Any]:
    """Serialize an event like the v1 log writer (None fields omitted)."""
    out = asdict(event)
    return {k: v for k, v in out.items() if v is not None}


def _input_error_items(exc: SdvSimInputError, lang: str) -> list[dict[str, Any]]:
    path = exc.filename or ""
    if exc.field:
        path = f"{path}.{exc.field}" if path else exc.field
    return [
        {
            "path": path or None,
            "line": exc.line,
            "message": exc.format(lang),
        }
    ]


def _parse_arch_yaml(content: str, lang: str) -> Architecture:
    return _parse_yaml_text(content, Architecture, "arch")


def _inject_lang(html: str, lang: str) -> str:
    """Inject the server-resolved UI language into the built index.html
    (ASR-020: serve --lang > SDV_SIM_LANG > locale; the frontend i18n reads
    ``window.__SDV_SIM_LANG__`` before falling back to the browser locale)."""
    html = re.sub(
        r'(<html\b[^>]*\blang=)["\'][^"\']*["\']',
        lambda m: f'{m.group(1)}"{lang}"',
        html,
        count=1,
    )
    script = f'<script>window.__SDV_SIM_LANG__ = "{lang}";</script>'
    if "</head>" in html:
        return html.replace("</head>", script + "</head>", 1)
    return html + script


# ----------------------------------------------------------------------------- app


def create_app(lang: str = "ko", store: SessionStore | None = None) -> FastAPI:
    """Build the dashboard FastAPI app.

    ``lang`` selects the server-side error language (ko/en). ``store`` allows
    tests to inject an isolated session store (defaults to a fresh one).
    """

    def t(key: str, **params: Any) -> str:
        return tr(lang, key, **params)

    sessions = store or SessionStore()
    app = FastAPI(title="sdv-sim dashboard", version="0.1.0")

    # -------------------------------------------------------------- API 5종

    @app.post("/api/validate", response_model=ValidateResponse)
    def validate(req: ValidateRequest) -> ValidateResponse | JSONResponse:
        # Pure validation (T-024): no session side effects. Edit-time session
        # invalidation is frontend-local (SessionMeta.invalidated, M-4).
        try:
            if req.kind == "scenario" and req.arch is not None:
                # structure + reference validation (F-4: arch pairing)
                loads(req.arch, req.content)
            elif req.kind == "scenario":
                # structure validation only — references need an architecture
                _parse_yaml_text(req.content, Scenario, "scenario")
            else:
                _parse_arch_yaml(req.content, lang)
        except SdvSimInputError as exc:
            return ValidateResponse(
                valid=False,
                errors=[ErrorItem(**item) for item in _input_error_items(exc, lang)],
            )
        return ValidateResponse(valid=True, errors=[])

    @app.post("/api/run")
    def run(req: RunRequest) -> JSONResponse:
        try:
            sim = loads(req.architecture, req.scenario)
            result = sim.run()
        except SdvSimError as exc:
            if isinstance(exc, SdvSimInputError):
                detail = _input_error_items(exc, lang)
            else:
                detail = [{"path": None, "line": None, "message": str(exc)}]
            return _error(
                "validation_error", t("error_input"), detail=detail, status=422
            )
        except Exception as exc:  # pragma: no cover - engine invariant
            return _error("internal", f"{t('error_internal')}: {exc}", status=500)
        sessions.replace(
            Session(
                source="run",
                events=[_event_to_dict(e) for e in result.events],
                report=asdict(result.report),
                duration_ms=result.duration_ms,
                arch_content=req.architecture,
                scenario_content=req.scenario,
            )
        )
        return JSONResponse(
            {
                "duration_ms": result.duration_ms,
                "event_count": len(result.events),
                "report": asdict(result.report),
            }
        )

    @app.post("/api/load-log")
    def load_log(req: LoadLogRequest) -> JSONResponse:
        arch: Architecture | None = None
        if req.arch_content is not None:
            try:
                arch = _parse_arch_yaml(req.arch_content, lang)
            except SdvSimInputError as exc:
                return _error(
                    "validation_error",
                    t("error_input"),
                    detail=_input_error_items(exc, lang),
                    status=422,
                )
        try:
            doc = parse_log(req.content, lang)
        except LogValidationError as exc:
            return _error(
                "log_invalid", t("log_invalid"), detail=exc.items, status=422
            )
        sessions.replace(
            Session(
                source="log",
                events=doc.events,
                report=derive_report(doc, arch),
                duration_ms=doc.simulation["duration_ms"],
                arch_content=req.arch_content,
            )
        )
        return JSONResponse(
            {
                "name": req.name,
                "duration_ms": doc.simulation["duration_ms"],
                "event_count": len(doc.events),
                "report": derive_report(doc, arch),
            }
        )

    @app.get("/api/events")
    def events() -> JSONResponse:
        current = sessions.current
        if current is None:
            return _error("session_invalid", t("session_invalid"), status=409)
        return JSONResponse(current.events)

    @app.get("/api/report")
    def report() -> JSONResponse:
        current = sessions.current
        if current is None:
            return _error("session_invalid", t("session_invalid"), status=409)
        return JSONResponse(current.report)

    # unknown /api/* routes answer the F-8 not_found envelope (before static)
    @app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    def api_not_found(path: str) -> JSONResponse:  # noqa: ARG001 - route shape
        return _error("not_found", t("not_found"), status=404)

    # ---------------------------------------------------------- error handlers

    @app.exception_handler(RequestValidationError)
    async def _request_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        items = [
            {
                "path": ".".join(str(p) for p in err.get("loc", ())),
                "line": None,
                "message": str(err.get("msg", "")),
            }
            for err in exc.errors()
        ]
        return _error("validation_error", t("error_input"), detail=items, status=422)

    @app.exception_handler(StarletteHTTPException)
    async def _http_exception(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        if exc.status_code == 404:
            return _error("not_found", t("not_found"), status=404)
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": "internal", "message": t("error_internal")}},
        )

    @app.exception_handler(Exception)
    async def _unhandled_exception(
        request: Request, exc: Exception
    ) -> JSONResponse:  # pragma: no cover - defensive
        return _error("internal", f"{t('error_internal')}: {exc}", status=500)

    # ------------------------------------------------------------- static assets

    index_html: str | None = None
    if _STATIC_DIR.is_dir():
        index_file = _STATIC_DIR / "index.html"
        if index_file.is_file():
            index_html = index_file.read_text(encoding="utf-8")

    if index_html is not None:
        # SPA: hash routing (F-10) — only "/" needs index.html; the language is
        # injected here so the served page matches `serve --lang` (ASR-020).
        # Registered before the catch-all mount, so "/" hits this route and
        # /assets/* still falls through to the static mount.
        @app.get("/", include_in_schema=False)
        def root() -> HTMLResponse:
            return HTMLResponse(_inject_lang(index_html, lang))

        app.mount("/", StaticFiles(directory=_STATIC_DIR), name="static")
    else:
        @app.get("/")
        def _root_no_static() -> JSONResponse:
            return JSONResponse({"message": t("static_not_built")})

    return app
