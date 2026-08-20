"""Resolution of PDF glyph names to Unicode characters.

Every rule in this module is deterministic: a glyph name either resolves through a
published table or through a documented naming convention, or it does not resolve at
all. Nothing is guessed.
"""

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Optional, Union

_DATA_DIR = Path(__file__).parent / "data"

# Character codes a /ToUnicode map must never point at. A font claiming that one of its
# glyphs is a control character or the replacement character is always a producer bug,
# never an intention, so such entries are treated as missing rather than trusted.
INVALID_TARGETS = frozenset({0x0000, 0xFFFD} | set(range(0x01, 0x20)) | set(range(0x7F, 0xA0)))

_BASE36 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


@lru_cache(maxsize=1)
def _glyph_table() -> dict[str, int]:
    """Load the packaged glyph-name table (Adobe Glyph List plus the TeX extensions)."""
    with (_DATA_DIR / "glyph_to_unicode.json").open(encoding="utf-8") as file:
        return json.load(file)


@lru_cache(maxsize=1)
def known_fonts() -> dict:
    """Load the packaged table of fonts whose glyph names are known to be unreliable."""
    with (_DATA_DIR / "known_fonts.json").open(encoding="utf-8") as file:
        return json.load(file)


def is_synthesised_name(name: str, char_code: int) -> bool:
    """Tell whether a glyph name is a machine-generated placeholder carrying no meaning.

    Some PDF producers replace real glyph names with short tokens that simply re-encode
    the character code in base 36 (so the glyph at code 99 is called ``CR``). Such a name
    describes nothing, and must not be looked up in a glyph table: a few of them collide
    with genuine names.

    The test is self-validating - the token is only accepted when the value it decodes to
    is the very code it is attached to.

    Args:
        name: The glyph name as found in the font's ``/Differences`` array.
        char_code: The character code that the name is attached to.

    Returns:
        True when the name is a placeholder that should be ignored.
    """
    if not re.fullmatch(r"[A-Z][0-9A-Z]", name or ""):
        return False
    return (ord(name[0]) - ord("A")) * 36 + _BASE36.index(name[1]) == char_code


def unicode_for_glyph_name(  # pylint: disable=too-many-return-statements
    name: str,
) -> Optional[Union[int, list[int]]]:
    """Resolve a glyph name to the character (or characters) it represents.

    Args:
        name: A glyph name, such as ``"summationdisplay"``, ``"uni2212"`` or ``"T_h"``.

    Returns:
        A character code, a list of character codes when the name denotes a sequence,
        or None when the name cannot be resolved.
    """
    if not name or name == ".notdef":
        return None

    table = _glyph_table()
    if name in table:
        return table[name]

    # A suffix after a full stop marks a stylistic variant of the base glyph.
    base = name.split(".")[0]
    if base in table:
        return table[base]

    # Names built from a character code.
    match = re.fullmatch(r"uni([0-9A-Fa-f]{4,6})", base) or re.fullmatch(
        r"u([0-9A-Fa-f]{4,6})", base
    )
    if match:
        return int(match.group(1), 16)

    # An underscore joins several glyphs into one: the name denotes the whole sequence.
    if "_" in base:
        parts = [unicode_for_glyph_name(part) for part in base.split("_")]
        if all(part is not None for part in parts):
            sequence: list[int] = []
            for part in parts:
                sequence.extend(part if isinstance(part, list) else [part])  # type: ignore[arg-type]
            return sequence
        return None

    # A trailing digit marks a variant of the base name, e.g. a second form of a letter.
    match = re.fullmatch(r"([A-Za-z]{3,})\d", base)
    if match and match.group(1) in table:
        return table[match.group(1)]

    return None


def first_code_point(value: Union[int, list[int]]) -> int:
    """Return the first character code of a resolved glyph value."""
    return value[0] if isinstance(value, list) else value


def is_writable(value: Union[int, list[int]]) -> bool:
    """Tell whether a resolved value may be written into a Unicode map.

    Rejects control characters and half of a surrogate pair. A lone surrogate is not a
    character at all: it cannot be encoded as UTF-8, and a reader that meets one shows a
    replacement mark. Writing one would turn "no character" into a broken character.
    """
    sequence = value if isinstance(value, list) else [value]
    if not sequence:
        return False
    return all(
        code_point not in INVALID_TARGETS and not 0xD800 <= code_point <= 0xDFFF
        for code_point in sequence
    )


def to_utf16_be_hex(value: Union[int, list[int]]) -> str:
    """Render a resolved glyph value as the hexadecimal string a CMap expects."""
    sequence = value if isinstance(value, list) else [value]
    out = ""
    for code_point in sequence:
        if code_point > 0xFFFF:
            shifted = code_point - 0x10000
            out += f"{0xD800 + (shifted >> 10):04X}{0xDC00 + (shifted & 0x3FF):04X}"
        else:
            out += f"{code_point:04X}"
    return out
