"""The standard PDF base encodings, as character-code to Unicode tables."""

# The PDF libraries are optional extras (`pip install kili[pdf]`), so they are imported
# where they are used rather than at module load time, and are not present at type-check
# time either.
# pyright: reportMissingImports=false
# pylint: disable=import-outside-toplevel

import json
from functools import lru_cache
from pathlib import Path
from typing import Optional

from kili.utils.pdf._glyphs import INVALID_TARGETS, unicode_for_glyph_name

_DATA_DIR = Path(__file__).parent / "data"


@lru_cache(maxsize=1)
def _name_tables() -> dict[str, dict[str, str]]:
    with (_DATA_DIR / "base_encodings.json").open(encoding="utf-8") as file:
        return json.load(file)


def base_encoding_glyph_names(name: Optional[str]) -> dict[int, str]:
    """Return the character-code to glyph-name table of a PDF base encoding.

    Args:
        name: The encoding name as written in the PDF. When None, StandardEncoding.

    Returns:
        A mapping of character code to glyph name.
    """
    table = _name_tables().get(name or "/StandardEncoding", {})
    return {int(code): glyph_name for code, glyph_name in table.items()}


_CODECS = {
    "/WinAnsiEncoding": "cp1252",
    "/MacRomanEncoding": "mac_roman",
    "/MacExpertEncoding": None,  # not a text encoding; no sensible Unicode fallback
}


@lru_cache(maxsize=8)
def base_encoding(name: Optional[str]) -> dict[int, int]:
    """Return the character-code to Unicode table of a PDF base encoding.

    Args:
        name: The encoding name as written in the PDF, for instance
            ``"/WinAnsiEncoding"``. When None, Adobe's StandardEncoding is used.

    Returns:
        A mapping of character code to Unicode character code. Codes the encoding
        leaves undefined are absent from the mapping.
    """
    if name in _CODECS:
        codec = _CODECS[name]
        if codec is None:
            return {}
        table = {}
        for code in range(32, 256):
            try:
                char = bytes([code]).decode(codec)
            except UnicodeDecodeError:
                continue
            if ord(char) not in INVALID_TARGETS:
                table[code] = ord(char)
        return table

    # Adobe StandardEncoding, resolved through the glyph table.
    try:
        from fontTools.encodings.StandardEncoding import (
            StandardEncoding,
        )
    except ImportError:  # pragma: no cover - guarded by the caller's dependency check
        return {}

    table = {}
    for code, glyph_name in enumerate(StandardEncoding):
        if not glyph_name or glyph_name == ".notdef":
            continue
        value = unicode_for_glyph_name(glyph_name)
        if isinstance(value, int) and value not in INVALID_TARGETS:
            table[code] = value
    return table
