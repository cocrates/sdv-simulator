"""sdv-sim CLI (cli-io-contract D-16, cli-output-policy).

Usage::

    sdv-sim run <architecture.yaml> <scenario.yaml> [--log <path>] [--quiet] [--lang ko|en]
    sdv-sim serve [--port <port>] [--host <ip>] [--lang ko|en] [--dev]

Channels (D-16):

- JSON event log goes to ``--log <path>`` (default ``events.json``) or to
  stdout with ``--log -``.
- The human-readable summary goes to stdout; ``--quiet`` suppresses it so the
  exit code alone judges the run.

Exit codes (cli-output-policy):

- 0 = pass
- 1 = assertion fail
- 2 = input error (missing file, YAML parse, schema violation)
- 3 = internal error (component bug, engine invariant)
"""

from __future__ import annotations

import argparse
import json
import locale
import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

from sdv_sim.core.engine import SimulationResult, load
from sdv_sim.core.errors import SdvSimError, SdvSimInputError
from sdv_sim.core.events import Event
from sdv_sim.i18n import tr

EXIT_PASS = 0
EXIT_ASSERTION_FAIL = 1
EXIT_INPUT_ERROR = 2
EXIT_INTERNAL_ERROR = 3


def _resolve_lang(lang_arg: str | None) -> str:
    """Language resolution: --lang > SDV_SIM_LANG > system locale (else ko)."""
    if lang_arg is not None:
        return lang_arg
    env = os.environ.get("SDV_SIM_LANG")
    if env in ("ko", "en"):
        return env
    try:
        code, _ = locale.getlocale()
    except Exception:
        code = None
    if code is not None:
        low = code.lower()
        if low.startswith("ko"):
            return "ko"
        if low.startswith("en"):
            return "en"
    return "ko"


# ------------------------------------------------------------------- summary


def _format_summary(lang: str, result: SimulationResult) -> str:
    def m(key: str) -> str:
        return tr(lang, key)

    report = result.report
    lines: list[str] = []
    lines.append(
        f"{m('simulation')}: "
        f"{m('result_pass') if report.simulation.result == 'pass' else m('result_fail')} "
        f"(duration_ms={result.duration_ms}, events={report.simulation.event_count})"
    )
    lines.append("")
    lines.append(m("links"))
    lines.append(m("link_cols"))
    for link in report.links:
        lines.append(
            f"{link.name}  {link.kind:<8}  {link.tx_count:>3}  {link.rx_count:>3}  "
            f"{link.drop_count:>3}  {link.supersede_count:>5}  {link.bus_load_percent:.2f}"
        )
    lines.append("")
    lines.append(m("tasks"))
    lines.append(m("task_cols"))
    for task in report.tasks:
        lines.append(
            f"{task.node}  {task.task}  {task.period_ms:>7}  {task.run_count:>3}  "
            f"{task.overrun_count:>3}"
        )
    lines.append("")
    lines.append(m("assertions"))
    if report.assertions:
        for a in report.assertions:
            lines.append(f"  [{a.status}] {a.name}: {a.detail}")
    else:
        lines.append(f"  ({m('none')})")
    if report.warnings:
        lines.append("")
        lines.append(m("warnings"))
        for w in report.warnings:
            lines.append(f"  - {w}")
    return "\n".join(lines)


# -------------------------------------------------------------------- json log


def _event_to_dict(event: Event) -> dict[str, Any]:
    out = asdict(event)
    return {k: v for k, v in out.items() if v is not None}


def _log_document(result: SimulationResult) -> dict[str, Any]:
    report = result.report
    return {
        "schema_version": 1,
        "simulation": {
            "duration_ms": result.duration_ms,
            "result": report.simulation.result,
        },
        "events": [_event_to_dict(e) for e in result.events],
        "assertions": [
            {"name": a.name, "status": a.status, "detail": a.detail}
            for a in report.assertions
        ],
    }


def _write_json_log(dest: str, result: SimulationResult) -> None:
    doc = _log_document(result)
    text = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    if dest == "-":
        sys.stdout.write(text)
    else:
        Path(dest).write_text(text, encoding="utf-8")


# ---------------------------------------------------------------------- errors


def _format_input_error(exc: SdvSimInputError, lang: str) -> str:
    # Category label and structured message follow the CLI language (D-16);
    # internal exception detail stays in its original language.
    return f"{tr(lang, 'error_input')}: {exc.format(lang)}"


def _format_internal_error(exc: Exception, lang: str) -> str:
    return f"{tr(lang, 'error_internal')}: {exc}"


# ------------------------------------------------------------------------ main


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sdv-sim",
        description="SDV (Software Defined Vehicle) simulator CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser(
        "run",
        help="run a simulation from architecture + scenario YAML files",
    )
    run.add_argument("architecture", metavar="<architecture.yaml>")
    run.add_argument("scenario", metavar="<scenario.yaml>")
    run.add_argument("--log", default="events.json", metavar="<path>",
                     help="JSON event log path ('-' = stdout; default events.json)")
    run.add_argument("--quiet", action="store_true",
                     help="suppress the human-readable summary (exit code only)")
    run.add_argument("--lang", choices=("ko", "en"), default=None,
                     help="output language (default: SDV_SIM_LANG env, then system locale)")
    serve = sub.add_parser(
        "serve",
        help="run the v2 web dashboard (single process: API + static assets)",
    )
    serve.add_argument("--port", type=int, default=8888, metavar="<port>",
                       help="listen port (default 8888)")
    serve.add_argument("--host", default="127.0.0.1", metavar="<ip>",
                       help="bind address (default 127.0.0.1; use 0.0.0.0 to allow external access)")
    serve.add_argument("--lang", choices=("ko", "en"), default=None,
                       help="server language (default: SDV_SIM_LANG env, then system locale)")
    serve.add_argument("--dev", action="store_true",
                       help="dev mode: UI served by the Vite dev server (HMR proxy)")
    return parser


def _run_command(args: argparse.Namespace) -> int:
    lang = _resolve_lang(args.lang)
    try:
        sim = load(args.architecture, args.scenario)
        result = sim.run()
    except SdvSimInputError as exc:
        print(_format_input_error(exc, lang), file=sys.stderr)
        return EXIT_INPUT_ERROR
    except SdvSimError as exc:
        print(f"{tr(lang, 'error_input')}: {exc}", file=sys.stderr)
        return EXIT_INPUT_ERROR
    except Exception as exc:  # component bugs / engine invariants
        print(_format_internal_error(exc, lang), file=sys.stderr)
        return EXIT_INTERNAL_ERROR

    try:
        _write_json_log(args.log, result)
    except OSError as exc:
        print(f"{tr(lang, 'error_write')}: {exc}", file=sys.stderr)
        return EXIT_INPUT_ERROR

    if not args.quiet:
        print(_format_summary(lang, result))

    passed = all(a.status == "pass" for a in result.report.assertions)
    return EXIT_PASS if passed else EXIT_ASSERTION_FAIL


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "run":
        return _run_command(args)
    if args.command == "serve":
        from sdv_sim.cli.serve import run_serve

        return run_serve(port=args.port, lang=args.lang, dev=args.dev, host=args.host)
    parser.error(f"unknown command {args.command!r}")  # pragma: no cover
    return EXIT_INTERNAL_ERROR  # pragma: no cover


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
