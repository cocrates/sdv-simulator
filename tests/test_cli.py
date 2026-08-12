"""CLI contract tests (cli-output-policy / cli-io-contract D-16)."""

from __future__ import annotations

import json
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest

from sdv_sim.cli.main import (
    EXIT_ASSERTION_FAIL,
    EXIT_INPUT_ERROR,
    EXIT_INTERNAL_ERROR,
    EXIT_PASS,
    main,
)

ARCH = """\
schema_version: 1
nodes:
  - name: ecu1
    type: ECU
    components:
      - name: sensor
        sends: [temp]
        tasks:
          - name: sense
            period_ms: 10
            priority: 1
            wcet_ms: 0
  - name: hpc1
    type: HPC
    components:
      - name: display
        receives: [temp]
links:
  - name: can1
    kind: can
    bitrate: 500
    nodes: [ecu1, hpc1]
    frames:
      - name: temp_frame
        id: 100
        dlc: 8
        period_ms: 10
        source: ecu1
        message: temp
gateways: []
"""

SCEN_PASS = """\
schema_version: 1
duration_ms: 10
messages: []
assertions:
  - name: tx_ok
    expect: {event: tx, frame: temp_frame, link: can1, count: 2}
"""

SCEN_FAIL = """\
schema_version: 1
duration_ms: 10
messages: []
assertions:
  - name: never_enough
    expect: {event: rx, frame: temp_frame, link: can1, node: hpc1, count: 99}
"""

SCEN_BAD_SCHEMA = """\
schema_version: 1
duration_ms: -5
"""


@pytest.fixture
def files(tmp_path):
    arch = tmp_path / "arch.yaml"
    arch.write_text(ARCH, encoding="utf-8")
    return tmp_path


def _write(files, name: str, text: str):
    p = files / name
    p.write_text(text, encoding="utf-8")
    return str(p)


class TestCliExitCodes:
    def test_pass(self, files, capsys) -> None:
        code = main(["run", _write(files, "a.yaml", ARCH), _write(files, "s.yaml", SCEN_PASS), "--quiet", "--log", "-"])
        assert code == EXIT_PASS
        assert "시뮬레이션" not in capsys.readouterr().out  # quiet: no summary

    def test_assertion_fail(self, files) -> None:
        code = main(["run", _write(files, "a.yaml", ARCH), _write(files, "s.yaml", SCEN_FAIL), "--quiet", "--log", "-"])
        assert code == EXIT_ASSERTION_FAIL

    def test_input_error_schema(self, files, capsys) -> None:
        code = main(["run", _write(files, "a.yaml", ARCH), _write(files, "s.yaml", SCEN_BAD_SCHEMA), "--quiet", "--log", "-"])
        assert code == EXIT_INPUT_ERROR
        err = capsys.readouterr().err
        assert "입력 오류" in err
        assert "스키마 오류" in err

    def test_input_error_missing_file(self, files, capsys) -> None:
        code = main(["run", str(files / "missing.yaml"), str(files / "s.yaml"), "--quiet", "--log", "-"])
        assert code == EXIT_INPUT_ERROR
        assert "파일을 읽을 수 없음" in capsys.readouterr().err

    def test_internal_error(self, files, capsys, monkeypatch) -> None:
        import sdv_sim.cli.main as cli_module

        def boom(*args, **kwargs):
            raise RuntimeError("engine blew up")

        # cli.main imported `load` by name; patch the module attribute.
        # (sdv_sim.cli.__init__ re-exports `main`, which shadows the submodule
        # attribute, so reach the real module via sys.modules.)
        monkeypatch.setattr(sys.modules["sdv_sim.cli.main"], "load", boom)
        code = main(["run", _write(files, "a.yaml", ARCH), _write(files, "s.yaml", SCEN_PASS), "--quiet", "--log", "-"])
        assert code == EXIT_INTERNAL_ERROR
        assert "내부 오류" in capsys.readouterr().err


class TestCliChannels:
    def test_log_to_stdout_with_dash(self, files, capsys) -> None:
        code = main(["run", _write(files, "a.yaml", ARCH), _write(files, "s.yaml", SCEN_PASS), "--quiet", "--log", "-"])
        out = capsys.readouterr().out
        doc = json.loads(out)
        assert doc["schema_version"] == 1
        assert doc["simulation"]["result"] == "pass"
        assert doc["events"] and all("t_ms" in e and "seq" in e for e in doc["events"])
        assert any(a["status"] == "pass" for a in doc["assertions"])
        assert code == EXIT_PASS

    def test_default_log_file(self, files, capsys, monkeypatch) -> None:
        monkeypatch.chdir(files)
        code = main(["run", "arch.yaml", _write(files, "s.yaml", SCEN_PASS), "--quiet"])
        assert code == EXIT_PASS
        doc = json.loads((files / "events.json").read_text(encoding="utf-8"))
        assert doc["simulation"]["duration_ms"] == 10

    def test_custom_log_path(self, files) -> None:
        out_path = files / "out.json"
        code = main(["run", _write(files, "a.yaml", ARCH), _write(files, "s.yaml", SCEN_PASS), "--quiet", "--log", str(out_path)])
        assert code == EXIT_PASS
        assert out_path.exists()

    def test_summary_printed_unless_quiet(self, files, capsys) -> None:
        main(["run", _write(files, "a.yaml", ARCH), _write(files, "s.yaml", SCEN_PASS), "--log", "-"])
        out = capsys.readouterr().out
        assert "시뮬레이션" in out
        assert "can1" in out and "부하" in out

    def test_lang_flag(self, files, capsys) -> None:
        main(["run", _write(files, "a.yaml", ARCH), _write(files, "s.yaml", SCEN_PASS), "--log", "-", "--lang", "en"])
        assert "Simulation" in capsys.readouterr().out

    def test_lang_env_fallback(self, files, capsys, monkeypatch) -> None:
        monkeypatch.setenv("SDV_SIM_LANG", "en")
        main(["run", _write(files, "a.yaml", ARCH), _write(files, "s.yaml", SCEN_PASS), "--log", "-"])
        assert "Simulation" in capsys.readouterr().out

    def test_invalid_lang_rejected(self, files) -> None:
        with pytest.raises(SystemExit) as exc:
            main(["run", _write(files, "a.yaml", ARCH), _write(files, "s.yaml", SCEN_PASS), "--lang", "fr"])
        assert exc.value.code == 2  # argparse invalid choice


class TestCliEventLog:
    def test_events_omit_none_fields(self, files, capsys) -> None:
        main(["run", _write(files, "a.yaml", ARCH), _write(files, "s.yaml", SCEN_PASS), "--quiet", "--log", "-"])
        doc = json.loads(capsys.readouterr().out)
        tx = next(e for e in doc["events"] if e["type"] == "tx")
        # tx has no data (None) and no task -> omitted, not null
        assert "data" not in tx
        assert "task" not in tx
        assert "node" in tx

    def test_events_sorted(self, files, capsys) -> None:
        main(["run", _write(files, "a.yaml", ARCH), _write(files, "s.yaml", SCEN_PASS), "--quiet", "--log", "-"])
        doc = json.loads(capsys.readouterr().out)
        pairs = [(e["t_ms"], e["seq"]) for e in doc["events"]]
        assert pairs == sorted(pairs)


class TestCliServe:
    """`sdv-sim serve` — v2 dashboard server (ASR-019)."""

    @staticmethod
    def _free_port() -> int:
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]

    def test_serve_help_lists_options(self, capsys) -> None:
        with pytest.raises(SystemExit) as exc:
            main(["serve", "--help"])
        assert exc.value.code == 0
        out = capsys.readouterr().out
        assert "--port" in out and "--lang" in out and "--dev" in out

    def test_serve_port_in_use_returns_input_error(self, capsys) -> None:
        """Port occupied -> clear error + exit code 2 (D-16/U-3 convention)."""
        port = self._free_port()
        with socket.socket() as s:
            s.bind(("127.0.0.1", port))
            code = main(["serve", "--port", str(port)])
        assert code == EXIT_INPUT_ERROR
        assert "포트" in capsys.readouterr().err

    def test_serve_live_smoke(self) -> None:
        """Real uvicorn subprocess: startup URL printed, API answers, Ctrl+C-like
        SIGTERM exits cleanly with code 0."""
        port = self._free_port()
        root = Path(__file__).resolve().parents[1]
        proc = subprocess.Popen(
            [sys.executable, "-m", "sdv_sim.cli.main", "serve",
             "--port", str(port), "--lang", "en"],
            cwd=str(root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            deadline = time.monotonic() + 10
            url = f"http://127.0.0.1:{port}/api/events"
            last: httpx.Response | None = None
            while time.monotonic() < deadline:
                if proc.poll() is not None:
                    out, err = proc.communicate()
                    pytest.fail(
                        f"serve exited early rc={proc.returncode}\nstdout={out}\nstderr={err}"
                    )
                try:
                    last = httpx.get(url, timeout=1)
                    if last.status_code == 409:
                        break
                except httpx.HTTPError:
                    time.sleep(0.1)
            assert last is not None, "server did not start in time"
            assert last.status_code == 409
            assert last.json()["error"]["code"] == "session_invalid"
        finally:
            proc.terminate()
            try:
                out, _ = proc.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                out, _ = proc.communicate()
        assert proc.returncode in (0, -signal.SIGTERM)  # uvicorn re-raises the received signal after graceful shutdown
        assert f"127.0.0.1:{port}" in out  # startup URL printed to stdout

