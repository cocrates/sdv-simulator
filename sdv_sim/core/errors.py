"""Error types for sdv-sim."""

from __future__ import annotations

from typing import Any

from sdv_sim.i18n import tr


class SdvSimError(Exception):
    """Base class for sdv-sim errors."""


class SdvSimInputError(SdvSimError):
    """User input problem: missing file, YAML parse error, or schema violation.

    Carries a **message code** plus structured context (file, line, field
    path, params) so the CLI can render the message in the requested language
    (D-16)::

        SdvSimInputError("injection_unknown_link", params={"link": "nope"})

    The :meth:`format` method renders the localized message; ``str(exc)``
    keeps the English rendering as a stable default for library users.
    """

    def __init__(
        self,
        code: str,
        *,
        params: dict[str, Any] | None = None,
        filename: str | None = None,
        line: int | None = None,
        field: str | None = None,
    ) -> None:
        super().__init__(code)
        self.code = code
        self.params = params or {}
        self.filename = filename
        self.line = line
        self.field = field

    def format(self, lang: str = "en") -> str:
        parts: list[str] = []
        if self.filename is not None:
            loc = self.filename
            if self.line is not None:
                loc += f":{self.line}"
            parts.append(loc)
        parts.append(tr(lang, self.code, **self.params))
        if self.field is not None:
            parts.append(tr(lang, "field_suffix", field=self.field))
        return " ".join(parts)

    def __str__(self) -> str:
        return self.format("en")
