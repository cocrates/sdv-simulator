"""Localization tests (D-16: error messages follow CLI language).

Coverage:
- :func:`sdv_sim.i18n.tr` catalog lookups and fallbacks.
- :class:`SdvSimInputError` rendering per language (code + params).
- CLI error output: category labels and common messages localized,
  internal exception detail stays in its original language.
"""

from __future__ import annotations

import sys

import pytest

from sdv_sim.core.errors import SdvSimInputError
from sdv_sim.i18n import MESSAGES, tr
from sdv_sim.cli.main import EXIT_INPUT_ERROR, EXIT_INTERNAL_ERROR, main

from conftest import inject, make_arch, make_frame, make_link, make_scenario


class TestCatalog:
    def test_both_languages_have_same_keys(self) -> None:
        assert set(MESSAGES["ko"]) == set(MESSAGES["en"])

    def test_tr_renders_params(self) -> None:
        msg = tr("en", "injection_unknown_link", link="can9")
        assert msg == "injection references unknown link 'can9'"

    def test_tr_korean(self) -> None:
        msg = tr("ko", "schema_error", detail="Input should be an integer")
        assert msg == "스키마 오류: Input should be an integer"

    def test_tr_unknown_lang_falls_back_to_ko(self) -> None:
        assert tr("fr", "error_input") == tr("ko", "error_input")

    def test_tr_unknown_key_returns_key(self) -> None:
        assert tr("ko", "no_such_key") == "no_such_key"

    def test_tr_missing_param_does_not_raise(self) -> None:
        # A missing param must not crash CLI output for catalog gaps.
        assert tr("ko", "injection_unknown_link") == "주입이 알 수 없는 링크 {link!r}를 참조합니다"


class TestInputErrorFormat:
    def test_english_default_str(self) -> None:
        exc = SdvSimInputError("injection_unknown_link", params={"link": "can9"})
        assert str(exc) == "injection references unknown link 'can9'"

    def test_format_korean(self) -> None:
        exc = SdvSimInputError("injection_unknown_link", params={"link": "can9"})
        assert exc.format("ko") == "주입이 알 수 없는 링크 'can9'를 참조합니다"

    def test_format_with_location(self) -> None:
        exc = SdvSimInputError(
            "schema_error",
            params={"detail": "bad"},
            filename="scenario.yaml",
            line=3,
            field="duration_ms",
        )
        out = exc.format("ko")
        assert out.startswith("scenario.yaml:3")
        assert "스키마 오류: bad" in out
        assert "(필드: duration_ms)" in out


# -------------------------------------------------------------------- CLI


ARCH = """\
schema_version: 1
nodes:
  - name: ecu1
    type: ECU
links:
  - name: can1
    kind: can
    bitrate: 500
    nodes: [ecu1]
    frames:
      - name: temp_frame
        id: 100
        dlc: 8
        period_ms: 10
        source: ecu1
gateways: []
"""

SCEN_BAD = """\
schema_version: 1
duration_ms: -5
"""

SCEN_OK = """\
schema_version: 1
duration_ms: 10
messages: []
assertions: []
"""


@pytest.fixture
def files(tmp_path):
    arch = tmp_path / "arch.yaml"
    arch.write_text(ARCH, encoding="utf-8")
    return tmp_path


def _write(files, name: str, text: str) -> str:
    p = files / name
    p.write_text(text, encoding="utf-8")
    return str(p)


class TestCliLocalization:
    def test_schema_error_korean_by_default(self, files, capsys) -> None:
        main(["run", _write(files, "a.yaml", ARCH), _write(files, "s.yaml", SCEN_BAD), "--quiet", "--log", "-"])
        err = capsys.readouterr().err
        assert "입력 오류" in err
        assert "스키마 오류" in err

    def test_schema_error_english_with_lang_flag(self, files, capsys) -> None:
        main(["run", _write(files, "a.yaml", ARCH), _write(files, "s.yaml", SCEN_BAD), "--quiet", "--log", "-", "--lang", "en"])
        err = capsys.readouterr().err
        assert "input error" in err
        assert "schema error" in err

    def test_yaml_parse_error_korean(self, files, capsys) -> None:
        bad = ": not: [valid"
        main(["run", _write(files, "a.yaml", ARCH), _write(files, "s.yaml", bad), "--quiet", "--log", "-"])
        err = capsys.readouterr().err
        assert "YAML 구문 오류" in err

    def test_missing_file_korean(self, files, capsys) -> None:
        main(["run", str(files / "missing.yaml"), _write(files, "s.yaml", SCEN_OK), "--quiet", "--log", "-"])
        err = capsys.readouterr().err
        assert "입력 오류" in err
        assert "파일을 읽을 수 없음" in err

    def test_internal_error_keeps_original_detail(self, files, capsys, monkeypatch) -> None:
        """The category label is localized; the exception detail is unchanged."""
        import sdv_sim.cli.main as cli_module

        def boom(*args, **kwargs):
            raise RuntimeError("engine blew up")

        monkeypatch.setattr(sys.modules["sdv_sim.cli.main"], "load", boom)
        main(["run", _write(files, "a.yaml", ARCH), _write(files, "s.yaml", SCEN_OK), "--quiet", "--log", "-", "--lang", "en"])
        err = capsys.readouterr().err
        assert "internal error" in err
        assert "engine blew up" in err  # original detail kept verbatim

    def test_input_error_korean_validation(self, capsys, files, monkeypatch) -> None:
        """Scenario cross-validation message renders in ko via the catalog."""
        from sdv_sim.core.engine import Simulator
        import sdv_sim.cli.main as cli_module

        def patched_load(a, s, components=None):
            arch = make_arch(
                [{"name": "n1"}, {"name": "n2"}],
                [make_link("l1", "can", 500, ["n1", "n2"], frames=[make_frame("f1", 10, 8, 100, "n1")])],
            )
            scen = make_scenario(messages=[inject(0, "nope", "f1")])
            return Simulator(arch, scen)

        monkeypatch.setattr(sys.modules["sdv_sim.cli.main"], "load", patched_load)
        main(["run", _write(files, "a.yaml", ARCH), _write(files, "s.yaml", SCEN_OK), "--quiet", "--log", "-"])
        err = capsys.readouterr().err
        assert "입력 오류" in err
        assert "알 수 없는 링크" in err
