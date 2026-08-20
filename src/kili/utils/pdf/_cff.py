"""Minimal reader for the built-in encoding of an embedded CFF (Type 1C) font program.

A PDF font may omit its ``/Encoding`` entry, in which case the character-code to
glyph mapping lives inside the embedded font program itself. ``fontTools`` does not
expose that table in the form we need, so this module reads it directly.
"""

import struct
from typing import Optional


def _read_index(data: bytes, pos: int) -> tuple[list[bytes], int]:
    """Read a CFF INDEX structure, returning its entries and the next offset."""
    (count,) = struct.unpack(">H", data[pos : pos + 2])
    if count == 0:
        return [], pos + 2
    off_size = data[pos + 2]
    cursor = pos + 3
    offsets = []
    for _ in range(count + 1):
        value = 0
        for byte in data[cursor : cursor + off_size]:
            value = (value << 8) | byte
        offsets.append(value)
        cursor += off_size
    data_start = cursor - 1
    entries = [data[data_start + offsets[i] : data_start + offsets[i + 1]] for i in range(count)]
    return entries, data_start + offsets[-1]


def _parse_dict(raw: bytes) -> dict[int, list]:
    """Parse a CFF DICT into ``{operator: operands}``."""
    result: dict[int, list] = {}
    operands: list = []
    i = 0
    while i < len(raw):
        b0 = raw[i]
        if b0 <= 21:
            operator = b0
            i += 1
            if b0 == 12:
                operator = 1200 + raw[i]
                i += 1
            result[operator] = operands
            operands = []
        elif b0 == 28:
            operands.append(struct.unpack(">h", raw[i + 1 : i + 3])[0])
            i += 3
        elif b0 == 29:
            operands.append(struct.unpack(">i", raw[i + 1 : i + 5])[0])
            i += 5
        elif b0 == 30:  # real number, we never need the value
            i += 1
            while i < len(raw) and (raw[i] & 0x0F) != 0x0F and (raw[i] >> 4) != 0x0F:
                i += 1
            i += 1
            operands.append(0.0)
        elif 32 <= b0 <= 246:
            operands.append(b0 - 139)
            i += 1
        elif 247 <= b0 <= 250:
            operands.append((b0 - 247) * 256 + raw[i + 1] + 108)
            i += 2
        elif 251 <= b0 <= 254:
            operands.append(-(b0 - 251) * 256 - raw[i + 1] - 108)
            i += 2
        else:
            i += 1
    return result


def read_builtin_encoding(font_program: bytes) -> Optional[dict[int, int]]:
    """Read the built-in encoding of a CFF font program.

    Args:
        font_program: The raw bytes of an embedded CFF (Type 1C) font program.

    Returns:
        A mapping of character code to glyph index, or None when the font uses one of
        the predefined encodings (in which case there is nothing font-specific to read).
    """
    try:
        pos = font_program[2]  # header size
        _, pos = _read_index(font_program, pos)  # Name INDEX
        top_dicts, pos = _read_index(font_program, pos)  # Top DICT INDEX
        if not top_dicts:
            return None
        top_dict = _parse_dict(top_dicts[0])
        if 16 not in top_dict:  # no Encoding operator: standard encoding
            return None
        offset = int(top_dict[16][0])
        if offset in (0, 1):  # predefined Standard / Expert encoding
            return None

        fmt = font_program[offset]
        encoding: dict[int, int] = {}
        base_format = fmt & 0x7F
        if base_format == 0:
            n_codes = font_program[offset + 1]
            for glyph_index in range(1, n_codes + 1):
                encoding[font_program[offset + 1 + glyph_index]] = glyph_index
        elif base_format == 1:
            n_ranges = font_program[offset + 1]
            glyph_index, cursor = 1, offset + 2
            for _ in range(n_ranges):
                first, n_left = font_program[cursor], font_program[cursor + 1]
                for step in range(n_left + 1):
                    encoding[first + step] = glyph_index
                    glyph_index += 1
                cursor += 2
        return encoding
    except (IndexError, struct.error, ValueError):
        return None
