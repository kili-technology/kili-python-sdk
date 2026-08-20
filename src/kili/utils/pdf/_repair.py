"""Repair of the Unicode maps of a single PDF file."""

# The PDF libraries are optional extras (`pip install kili[pdf]`), so they are imported
# where they are used rather than at module load time, and are not present at type-check
# time either.
# pyright: reportMissingImports=false
# pylint: disable=import-outside-toplevel

import io
import re
from pathlib import Path
from typing import Optional, Union

from kili.utils.pdf._cff import read_builtin_encoding
from kili.utils.pdf._encodings import base_encoding, base_encoding_glyph_names
from kili.utils.pdf._glyphs import (
    INVALID_TARGETS,
    first_code_point,
    is_synthesised_name,
    is_writable,
    known_fonts,
    to_utf16_be_hex,
    unicode_for_glyph_name,
)

_CMAP_HEADER = (
    "/CIDInit/ProcSet findresource begin\n12 dict begin begincmap\n"
    "/CMapName/Adobe-Identity-UCS def\n"
    "/CIDSystemInfo<</Registry(Adobe)/Ordering(UCS)/Supplement 0>>def\n"
    "/CMapType 2 def\n1 begincodespacerange\n<00><FF>endcodespacerange\n"
)
_CMAP_FOOTER = "endcmap\nCMapName currentdict /CMap defineresource pop end end\n"


def _decode_utf16_be_hex(hex_digits: str) -> int:
    """Decode a Unicode map target to its first character.

    Targets are UTF-16BE, so a character outside the basic plane is written as a pair of
    values that must be combined - reading only the first half yields half a character.
    """
    units = [int(hex_digits[i : i + 4], 16) for i in range(0, len(hex_digits) - 3, 4)]
    if not units:
        return 0
    if len(units) >= 2 and 0xD800 <= units[0] <= 0xDBFF and 0xDC00 <= units[1] <= 0xDFFF:
        return 0x10000 + ((units[0] - 0xD800) << 10) + (units[1] - 0xDC00)
    return units[0]


def _parse_existing_map(stream_text: str) -> dict[int, int]:
    """Read the character codes an existing Unicode map already covers.

    Only ``bfchar`` and ``bfrange`` blocks are inspected, so that the code space
    declaration is never mistaken for a mapping.
    """
    mapping: dict[int, int] = {}
    for block in re.findall(r"beginbfchar(.*?)endbfchar", stream_text, re.S):
        for code, target in re.findall(r"<([0-9A-Fa-f]{2})>\s*<([0-9A-Fa-f]+)>", block):
            mapping[int(code, 16)] = _decode_utf16_be_hex(target)
    for block in re.findall(r"beginbfrange(.*?)endbfrange", stream_text, re.S):
        for low, high, target in re.findall(
            r"<([0-9A-Fa-f]{2})>\s*<([0-9A-Fa-f]{2})>\s*<([0-9A-Fa-f]+)>", block
        ):
            start = _decode_utf16_be_hex(target)
            for offset, code in enumerate(range(int(low, 16), int(high, 16) + 1)):
                mapping[code] = start + offset
        for low, high, array in re.findall(
            r"<([0-9A-Fa-f]{2})>\s*<([0-9A-Fa-f]{2})>\s*\[(.*?)\]", block, re.S
        ):
            del high
            first = int(low, 16)
            for offset, target in enumerate(re.findall(r"<([0-9A-Fa-f]+)>", array)):
                mapping[first + offset] = _decode_utf16_be_hex(target)
    return mapping


def _render_cmap(mapping: dict[int, Union[int, list[int]]], existing_text: str = "") -> str:
    """Build a Unicode map, preserving any existing one and appending the new entries."""
    items = sorted(mapping.items())
    blocks = ""
    for start in range(0, len(items), 100):
        chunk = items[start : start + 100]
        blocks += (
            f"{len(chunk)} beginbfchar\n"
            + "\n".join(f"<{code:02X}> <{to_utf16_be_hex(value)}>" for code, value in chunk)
            + "\nendbfchar\n"
        )
    if existing_text and "endcmap" in existing_text:
        return existing_text.replace("endcmap", blocks + "endcmap", 1)
    return _CMAP_HEADER + blocks + _CMAP_FOOTER


def _glyph_names_of_font(font, descriptor) -> dict[int, str]:
    """Build the character-code to glyph-name table a font declares."""
    from pypdf.generic import (
        DictionaryObject,
        IndirectObject,
    )

    names: dict[int, str] = {}
    encoding = font.get("/Encoding")
    if isinstance(encoding, IndirectObject):
        encoding = encoding.get_object()

    # /Encoding is either a dictionary describing the encoding, or the plain name of one.
    encoding_dict = encoding if isinstance(encoding, DictionaryObject) else None
    base_name = encoding_dict.get("/BaseEncoding") if encoding_dict is not None else encoding

    # With no base encoding declared, the font program's own encoding is what applies.
    if base_name is None:
        font_file = descriptor.get("/FontFile3") if descriptor else None
        if font_file is not None:
            program = font_file.get_object().get_data()
            charset = _cff_charset(program)
            raw = read_builtin_encoding(program)
            if raw and charset:
                names.update(
                    {code: charset[gid] for code, gid in raw.items() if 0 <= gid < len(charset)}
                )

    differences = encoding_dict.get("/Differences") if encoding_dict is not None else None
    if differences:
        code = 0
        for item in differences:
            item = item.get_object() if isinstance(item, IndirectObject) else item
            if isinstance(item, (int, float)):
                code = int(item)
            else:
                names[code] = str(item).lstrip("/")
                code += 1
    return names


def _cff_charset(font_program: bytes) -> Optional[list[str]]:
    """Return the glyph names of an embedded CFF font program, in glyph order."""
    try:
        from fontTools.cffLib import (
            CFFFontSet,
        )

        font_set = CFFFontSet()
        font_set.decompile(io.BytesIO(font_program), None)
        return list(font_set[font_set.fontNames[0]].charset)
    except Exception:  # pylint: disable=broad-except  # a malformed font must not abort the run
        return None


def _known_font_overrides(font, names: dict[int, str]) -> tuple[dict[int, int], bool, bool]:
    """Look up corrections for fonts whose own declarations are known to be unreliable.

    Returns:
        ``(overrides, names_are_untrustworthy, describes_whole_font)``.

        ``names_are_untrustworthy`` is set when the font belongs to a family whose glyph
        names are known not to describe the glyphs, whether or not a correction was found
        for this particular font.

        ``describes_whole_font`` is set when the table was matched on a fingerprint of the
        entire font, so its codes describe the font's real layout and can be trusted even
        where the font itself does not declare them.
    """
    base_font = str(font.get("/BaseFont") or "")
    tables = known_fonts()
    overrides: dict[int, int] = {}

    cmsy = tables["tex_cmsy"]
    rule = cmsy["match"]
    if rule["base_font_contains"] in base_font:
        # Fingerprinted on the full code range, not just the name: several producers
        # re-subset this font into smaller, renumbered pieces that keep the same name but
        # not the layout, and the table would be wrong for those.
        if (
            font.get("/FirstChar") == rule["first_char"]
            and font.get("/LastChar") == rule["last_char"]
        ):
            # The fingerprint covers the whole layout, so the table knows this font
            # better than the font describes itself - including codes it draws but
            # leaves out of its own declared range.
            return {int(code): value for code, value in cmsy["codes"].items()}, True, True
        return {}, True, False

    symbols = tables["advanced_print_publisher_symbols"]
    if symbols["match"]["base_font_contains"] in base_font:
        family = base_font.rsplit("+", maxsplit=1)[-1]
        glyph_map = symbols["fonts"].get(family) or {}
        # Keyed by glyph name, so only meaningful where the font names a glyph itself.
        for code, glyph_name in names.items():
            if glyph_name in glyph_map:
                overrides[code] = glyph_map[glyph_name]
        return overrides, True, False

    return overrides, False, False


def _resolve_code(
    code: int,
    glyph_name: Optional[str],
    fallback: dict[int, int],
    *,
    symbolic: bool,
) -> Optional[Union[int, list[int]]]:
    """Work out which character a font's code stands for, or None if it cannot be known.

    Args:
        code: The character code.
        glyph_name: The name the font gives that code, if it gives one.
        fallback: The character table of the font's base encoding.
        symbolic: Whether the font is flagged as a symbol font.

    Returns:
        The character (or characters) the code stands for, or None.
    """
    placeholder = is_synthesised_name(glyph_name or "", code)
    value = None if placeholder else unicode_for_glyph_name(glyph_name or "")

    if value is not None and first_code_point(value) not in INVALID_TARGETS:
        return value

    # The name told us nothing usable. The encoding slot is only a safe fallback for a
    # text font: in a symbol font the slot number says nothing about the character drawn.
    if symbolic or code not in fallback:
        return None
    if placeholder or glyph_name is None:
        return fallback[code]
    return None


def _descriptor_if_repairable(font, empty_dict_factory):
    """Return the font's descriptor if this font can be repaired, else None.

    Only single-byte fonts whose glyphs travel with the document are handled. Type 3
    fonts carry their glyphs as page content and have no descriptor of their own.
    """
    if str(font.get("/Subtype")) == "/Type0":
        return None
    is_type3 = str(font.get("/Subtype")) == "/Type3" or "/CharProcs" in font

    descriptor = font.get("/FontDescriptor")
    if descriptor is None:
        return empty_dict_factory() if is_type3 else None

    descriptor = descriptor.get_object()
    embedded = any(key in descriptor for key in ("/FontFile", "/FontFile2", "/FontFile3"))
    return descriptor if (is_type3 or embedded) else None


def _defined_codes(font, names, whole_font_overrides=()) -> set[int]:
    """Return the character codes a font actually defines.

    Writing entries for codes a font never uses would add noise and claim knowledge we do
    not have, so the repair stays inside what the font declares: the codes it names, and
    the range it gives. A correction from a reference table is not a licence to step
    outside that range - the table is keyed by glyph name, and for a symbol font the name
    attached to an undeclared slot comes from the base encoding, which says nothing about
    what that font actually draws there. A table matched on a fingerprint of the whole
    font is the exception: it describes the real layout, so its codes count as declared.
    """
    declared: set[int] = set(names) | set(whole_font_overrides)
    first_char, last_char = font.get("/FirstChar"), font.get("/LastChar")
    if isinstance(first_char, int) and isinstance(last_char, int) and first_char <= last_char:
        declared |= set(range(first_char, last_char + 1))
    return {code for code in declared if 0 <= code <= 255}


def _repair_simple_font(font, writer) -> tuple[int, int]:
    """Repair one simple (single-byte) font.

    Returns:
        ``(corrected, completed)`` - how many characters had a wrong meaning that was put
        right, and how many had no meaning recorded at all and were filled in.
    """
    from pypdf.generic import (
        DecodedStreamObject,
        DictionaryObject,
        IndirectObject,
        NameObject,
    )

    descriptor = _descriptor_if_repairable(font, DictionaryObject)
    if descriptor is None:
        return 0, 0

    names = _glyph_names_of_font(font, descriptor)
    symbolic = bool(int(descriptor.get("/Flags", 0) or 0) & 4)

    encoding = font.get("/Encoding")
    if isinstance(encoding, IndirectObject):
        encoding = encoding.get_object()
    encoding_dict = encoding if isinstance(encoding, DictionaryObject) else None
    base_name = encoding_dict.get("/BaseEncoding") if encoding_dict is not None else encoding
    base_name = str(base_name) if base_name is not None else None
    fallback = base_encoding(base_name)

    # The known-font tables are keyed by glyph name, so they need the names implied by the
    # base encoding too. Those names are deliberately kept out of `names`: for a symbol
    # font they describe the slot, not the glyph, and must not drive the generic path.
    override_names = {**base_encoding_glyph_names(base_name), **names}

    unicode_map = font.get("/ToUnicode")
    existing_text, existing = "", {}
    if unicode_map is not None:
        try:
            existing_text = unicode_map.get_object().get_data().decode("latin-1", "replace")
            existing = _parse_existing_map(existing_text)
        except Exception:  # pylint: disable=broad-except
            existing_text, existing = "", {}
    trusted: set[int] = {code for code, value in existing.items() if value not in INVALID_TARGETS}

    overrides, names_are_untrustworthy, describes_whole_font = _known_font_overrides(
        font, override_names
    )

    additions: dict[int, Union[int, list[int]]] = {}
    for code in sorted(_defined_codes(font, names, overrides if describes_whole_font else ())):
        if code in overrides:
            if existing.get(code) != overrides[code]:
                additions[code] = overrides[code]
            continue
        if code in trusted:
            continue
        if names_are_untrustworthy:
            # This font belongs to a family whose glyph names are known not to describe
            # the glyphs. Where the table has no entry we know nothing at all, so leaving
            # the character alone is the only safe option: a name-derived guess here would
            # replace "no character" with a confident, wrong one.
            continue
        value = _resolve_code(code, names.get(code), fallback, symbolic=symbolic)
        if value is not None and is_writable(value):
            additions[code] = value

    if not additions:
        return 0, 0

    stream = DecodedStreamObject()
    stream.set_data(_render_cmap(additions, existing_text).encode("latin-1", "replace"))
    font[NameObject("/ToUnicode")] = writer._add_object(stream)  # noqa: SLF001  # pylint: disable=protected-access
    # A character counts as "put right" only when the file already described it and
    # described it wrongly. A character the file never described was missing, not wrong,
    # even when the value came from a reference table.
    corrected = sum(1 for code in additions if code in existing)
    return corrected, len(additions) - corrected


def _all_resources(writer) -> list:
    """Yield every resource dictionary in a document, including nested ones.

    Text is not always drawn straight onto the page: figures, headers and placed artwork
    are often wrapped in form objects that carry their own fonts. Those fonts would
    otherwise be missed, and the document reported as needing no repair.
    """
    found, visited = [], set()

    def walk(resources, depth: int) -> None:
        if resources is None or depth > 8:  # a malformed file could nest for ever
            return
        key = id(resources)
        if key in visited:
            return
        visited.add(key)
        found.append(resources)
        xobjects = resources.get("/XObject")
        if not xobjects:
            return
        for reference in xobjects.values():
            try:
                xobject = reference.get_object()
                if str(xobject.get("/Subtype")) == "/Form":
                    walk(xobject.get("/Resources"), depth + 1)
            except Exception:  # pylint: disable=broad-except  # a broken object must not stop the walk
                continue

    for page in writer.pages:
        walk(page.get("/Resources"), 0)
    return found


def repair_file(source: Path, destination: Path) -> tuple[int, int, int]:
    """Repair the Unicode maps of one PDF.

    The page content is never modified: the repaired file is written as an incremental
    update, so the original bytes are preserved and the document renders identically.

    Args:
        source: The PDF to read.
        destination: Where to write the repaired PDF.

    Returns:
        A tuple ``(fonts_repaired, characters_corrected, characters_completed)``.
    """
    from pypdf import (
        PdfWriter,
    )
    from pypdf.generic import (
        IndirectObject,
    )

    writer = PdfWriter(str(source), incremental=True)
    seen: set[int] = set()
    fonts_repaired = characters_corrected = characters_completed = 0

    for resources in _all_resources(writer):
        fonts = resources.get("/Font")
        if not fonts:
            continue
        for reference in fonts.values():
            key = reference.idnum if isinstance(reference, IndirectObject) else id(reference)
            if key in seen:
                continue
            seen.add(key)
            corrected, completed = _repair_simple_font(reference.get_object(), writer)
            if corrected or completed:
                fonts_repaired += 1
                characters_corrected += corrected
                characters_completed += completed

    writer.write(str(destination))
    return fonts_repaired, characters_corrected, characters_completed
