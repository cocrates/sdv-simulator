"""``sdv-sim serve`` — v2 dashboard server (ASR-019, spec/sdv-sim-v2.md).

Single process: the FastAPI app (API 5종) plus the packaged static assets.
``--dev`` keeps the API server for the Vite dev server to proxy (HMR, T-016);
the dashboard UI is then served by Vite, not by this process.

Exit codes (D-16/U-3):

- 2 = input/resource error — here: the requested port is already in use.
- Clean shutdown (Ctrl+C / SIGTERM) is a normal uvicorn shutdown, after which
  uvicorn re-raises the received signal. The process therefore exits with the
  standard signal status (shell 130 for Ctrl+C, 143 for SIGTERM) rather than
  with code 0 — this is the documented contract, not a bug.
"""

from __future__ import annotations

import copy
import socket
import sys
from typing import Any

import uvicorn
from uvicorn.config import LOGGING_CONFIG

from sdv_sim.i18n import tr
from sdv_sim.server.app import create_app

HOST = "127.0.0.1"

EXIT_OK = 0
EXIT_PORT_BUSY = 2  # v1 resource-error convention: log write failure -> 2 (D-16/U-3)


def _stdout_log_config() -> dict[str, Any]:
    """Uvicorn's default logging config with every handler on stdout.

    spec/sdv-sim-v2.md requires server logs on stdout; uvicorn's default
    routes startup/shutdown records (``uvicorn`` logger) to stderr and only
    access records (``uvicorn.access``) to stdout.
    """
    cfg = copy.deepcopy(LOGGING_CONFIG)
    for handler in cfg["handlers"].values():
        handler["stream"] = "ext://sys.stdout"
    return cfg


def run_serve(port: int, lang: str | None, dev: bool) -> int:
    """Run the dashboard server until Ctrl+C. Returns the process exit code."""
    from sdv_sim.cli.main import _resolve_lang  # lazy: cli.main imports this module

    app_lang = _resolve_lang(lang)
    app = create_app(lang=app_lang)

    sock = _bind(port)
    if sock is None:
        print(f"{tr(app_lang, 'serve_port_busy')}: {port}", file=sys.stderr)
        return EXIT_PORT_BUSY

    _print_startup(port, dev, app_lang)
    config = uvicorn.Config(
        app,
        host=HOST,
        port=port,
        fd=sock.fileno(),
        log_level="info",
        log_config=_stdout_log_config(),
    )
    server = uvicorn.Server(config)
    try:
        server.run()
    finally:
        sock.close()
    return EXIT_OK


def _bind(port: int) -> socket.socket | None:
    """Bind the listen socket so port conflicts fail before uvicorn starts."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, port))
        return sock
    except OSError:
        return None


def _print_startup(port: int, dev: bool, lang: str) -> None:
    if dev:
        print(tr(lang, "serve_dev_hint", port=port))
    else:
        print(tr(lang, "serve_started", port=port))
