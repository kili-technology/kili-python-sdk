"""Tests for the PDF text layer repair utility.

The PDFs used here are built from scratch by `_build_pdf` so that each test states
exactly which defect it covers.
"""

import re
import warnings
from pathlib import Path
from typing import Optional

import pytest

from kili.utils.pdf import _repair, repair_pdf
from kili.utils.pdf._glyphs import (
    is_synthesised_name,
    to_utf16_be_hex,
    unicode_for_glyph_name,
)

pypdf = pytest.importorskip("pypdf")


def _build_pdf(
    to_unicode: Optional[str],
    differences: str = "[97 /a]",
    base_font: str = "TestFont",
    flags: int = 32,
    first_char: int = 97,
    last_char: int = 97,
    widths: str = "[500]",
    in_xobject: bool = False,
) -> bytes:
    """Build a one page PDF holding a single Type 3 font.

    Args:
        to_unicode: The body of the font's Unicode map, or None for no map at all.
        differences: The font's /Differences array.
        base_font: The font's /BaseFont name.
        flags: The font descriptor flags (4 marks a symbol font).
        first_char: The font's /FirstChar.
        last_char: The font's /LastChar.
        widths: The font's /Widths array.
        in_xobject: Whether the text is drawn inside a form object with its own fonts.

    Returns:
        The bytes of a syntactically valid PDF.
    """
    cmap = (
        "/CIDInit/ProcSet findresource begin\n12 dict begin begincmap\n"
        "/CMapName/Test def\n/CMapType 2 def\n"
        "1 begincodespacerange\n<00><FF>\nendcodespacerange\n"
        f"{to_unicode}\nendcmap\nend end\n"
    )
    objects: list[bytes] = [
        b"<</Type/Catalog/Pages 2 0 R>>",
        b"<</Type/Pages/Kids[3 0 R]/Count 1>>",
        b"<</Type/Page/Parent 2 0 R/MediaBox[0 0 200 100]"
        b"/Resources<</Font<</F1 4 0 R>>>>/Contents 7 0 R>>",
        (
            f"<</Type/Font/Subtype/Type3/BaseFont/{base_font}/FontBBox[0 0 10 10]"
            "/FontMatrix[0.001 0 0 0.001 0 0]/CharProcs 5 0 R"
            f"/Encoding<</Type/Encoding/Differences{differences}>>"
            f"/FirstChar {first_char}/LastChar {last_char}/Widths{widths}"
            "/FontDescriptor 9 0 R" + ("/ToUnicode 6 0 R" if to_unicode is not None else "") + ">>"
        ).encode(),
        b"<</a 8 0 R>>",
        f"<</Length {len(cmap)}>>\nstream\n{cmap}\nendstream".encode(),
        b"<</Length 40>>\nstream\nBT /F1 12 Tf 10 50 Td (a) Tj ET\nendstream",
        b"<</Length 12>>\nstream\n500 0 d0\nendstream",
        (
            f"<</Type/FontDescriptor/FontName/{base_font}/Flags {flags}/ItalicAngle 0"
            "/Ascent 10/Descent 0/CapHeight 10/StemV 1/FontBBox[0 0 10 10]>>"
        ).encode(),
    ]
    if in_xobject:
        # the text is drawn inside a form object that carries its own font resources
        objects[2] = (
            b"<</Type/Page/Parent 2 0 R/MediaBox[0 0 200 100]"
            b"/Resources<</XObject<</X1 10 0 R>>>>/Contents 7 0 R>>"
        )
        objects[6] = b"<</Length 8>>\nstream\n/X1 Do\nendstream"
        objects.append(
            b"<</Type/XObject/Subtype/Form/BBox[0 0 200 100]"
            b"/Resources<</Font<</F1 4 0 R>>>>/Length 40>>"
            b"\nstream\nBT /F1 12 Tf 10 50 Td (a) Tj ET\nendstream"
        )

    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{number} 0 obj\n".encode() + body + b"\nendobj\n"
    xref_at = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode()
    out += (
        f"trailer\n<</Size {len(objects) + 1}/Root 1 0 R>>\nstartxref\n{xref_at}\n%%EOF\n".encode()
    )
    return bytes(out)


def _to_unicode_of_first_font(pdf_path: Path) -> str:
    """Read back the Unicode map of the first font in a PDF."""
    reader = pypdf.PdfReader(str(pdf_path))
    font = reader.pages[0]["/Resources"]["/Font"]["/F1"].get_object()
    return font["/ToUnicode"].get_object().get_data().decode("latin-1")


@pytest.fixture()
def dirs(tmp_path: Path):
    """Provide an empty input and output directory."""
    source, target = tmp_path / "in", tmp_path / "out"
    source.mkdir()
    return source, target


def test_glyph_name_resolution():
    assert unicode_for_glyph_name("summationdisplay") == 0x2211
    assert unicode_for_glyph_name("uni2212") == 0x2212
    assert unicode_for_glyph_name("uni2264.alt") == 0x2264  # stylistic suffix
    assert unicode_for_glyph_name("epsilon1") == 0x03F5
    assert unicode_for_glyph_name("T_h") == [0x0054, 0x0068]  # a sequence, not just "T"
    assert unicode_for_glyph_name("notaglyphname") is None


def test_machine_generated_names_are_only_accepted_at_their_own_code():
    # These tokens encode the character code itself, so they describe nothing.
    assert is_synthesised_name("CR", 99) is True
    assert is_synthesised_name("D6", 114) is True
    # The same token at a different code is a real name that happens to look alike.
    assert is_synthesised_name("CR", 50) is False
    # Genuine ligature names must never be mistaken for placeholders.
    assert is_synthesised_name("OE", 140) is False
    assert is_synthesised_name("AE", 198) is False


def test_sequences_are_encoded_as_utf16():
    assert to_utf16_be_hex(0x2212) == "2212"
    assert to_utf16_be_hex([0x54, 0x68]) == "00540068"
    assert to_utf16_be_hex(0x1D400) == "D835DC00"  # outside the basic plane


def test_character_mapped_to_a_control_code_is_corrected(dirs):
    source, target = dirs
    # The letter "a" is declared as a carriage return, which is never a real intention.
    (source / "doc.pdf").write_bytes(_build_pdf("1 beginbfchar\n<61> <000D>\nendbfchar"))

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        report = repair_pdf(source, target, verbose=False)

    assert report.total_characters_corrected == 1
    assert report.files[0].was_repaired
    assert "<61> <0061>" in _to_unicode_of_first_font(target / "doc.pdf")


def test_character_with_no_mapping_is_filled_in(dirs):
    source, target = dirs
    (source / "doc.pdf").write_bytes(_build_pdf(None))

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        report = repair_pdf(source, target, verbose=False)

    assert report.total_characters_completed >= 1
    assert "<61> <0061>" in _to_unicode_of_first_font(target / "doc.pdf")


def test_a_correct_mapping_is_left_alone(dirs):
    source, target = dirs
    (source / "doc.pdf").write_bytes(_build_pdf("1 beginbfchar\n<61> <0061>\nendbfchar"))

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        report = repair_pdf(source, target, verbose=False)

    assert report.total_characters_corrected == 0
    assert len(report.unchanged_files) == 1


def test_the_code_space_range_is_not_mistaken_for_a_mapping(dirs):
    source, target = dirs
    # <00><FF> declares the code space. A naive parser reads that as "code 0x00 means
    # 0x00FF", which would mark code 0 as already described and leave it alone.
    (source / "doc.pdf").write_bytes(
        _build_pdf(
            "1 beginbfchar\n<61> <000D>\nendbfchar",
            differences="[0 /space 97 /a]",
            first_char=0,
            last_char=97,
            widths="[" + " 500" * 98 + "]",
        )
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        repair_pdf(source, target, verbose=False)

    written = _to_unicode_of_first_font(target / "doc.pdf")
    assert "<00> <0020>" in written  # code 0 was treated as undescribed, and resolved
    assert "<00> <00FF>" not in written


def test_every_pdf_is_present_in_the_output(dirs):
    source, target = dirs
    (source / "broken.pdf").write_bytes(_build_pdf("1 beginbfchar\n<61> <000D>\nendbfchar"))
    (source / "fine.pdf").write_bytes(_build_pdf("1 beginbfchar\n<61> <0061>\nendbfchar"))
    (source / "notes.txt").write_text("not a pdf")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        report = repair_pdf(source, target, verbose=False)

    assert report.total_files == 2  # the text file is ignored
    assert sorted(path.name for path in target.iterdir()) == ["broken.pdf", "fine.pdf"]


def test_an_unreadable_file_is_reported_and_does_not_stop_the_run(dirs):
    source, target = dirs
    (source / "damaged.pdf").write_bytes(b"%PDF-1.4\nthis is not a real pdf")
    (source / "good.pdf").write_bytes(_build_pdf("1 beginbfchar\n<61> <000D>\nendbfchar"))

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        report = repair_pdf(source, target, verbose=False)

    assert len(report.failed_files) == 1
    assert report.failed_files[0].file_name == "damaged.pdf"
    assert report.total_characters_corrected == 1  # the other file was still repaired
    assert (target / "damaged.pdf").exists()  # copied through so nothing is lost


def test_the_original_file_is_never_modified(dirs):
    source, target = dirs
    original = _build_pdf("1 beginbfchar\n<61> <000D>\nendbfchar")
    (source / "doc.pdf").write_bytes(original)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        repair_pdf(source, target, verbose=False)

    assert (source / "doc.pdf").read_bytes() == original


def test_the_page_content_is_untouched(dirs):
    source, target = dirs
    (source / "doc.pdf").write_bytes(_build_pdf("1 beginbfchar\n<61> <000D>\nendbfchar"))

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        repair_pdf(source, target, verbose=False)

    before = pypdf.PdfReader(str(source / "doc.pdf")).pages[0].get_contents().get_data()
    after = pypdf.PdfReader(str(target / "doc.pdf")).pages[0].get_contents().get_data()
    assert before == after


def test_a_beta_warning_is_shown(dirs):
    source, target = dirs
    (source / "doc.pdf").write_bytes(_build_pdf(None))

    with pytest.warns(UserWarning, match="beta"):
        repair_pdf(source, target, verbose=False)


def test_missing_input_directory_is_reported_clearly(tmp_path):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with pytest.raises(FileNotFoundError):
            repair_pdf(tmp_path / "nope", tmp_path / "out", verbose=False)


def test_the_output_directory_is_created(dirs):
    source, target = dirs
    (source / "doc.pdf").write_bytes(_build_pdf(None))
    assert not target.exists()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        repair_pdf(source, target, verbose=False)

    assert target.is_dir()


def test_the_report_reads_as_a_summary(dirs):
    source, target = dirs
    (source / "doc.pdf").write_bytes(_build_pdf("1 beginbfchar\n<61> <000D>\nendbfchar"))

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        report = repair_pdf(source, target, verbose=False)

    text = str(report)
    assert "PDFs found" in text
    assert "Wrong characters put right" in text
    assert "doc.pdf" in text


# --- Regressions found in review -------------------------------------------------


def test_no_half_character_is_ever_written(dirs):
    source, target = dirs
    # The maths symbols table covers characters outside the basic plane. Written as half
    # of a surrogate pair they cannot be encoded at all, and a reader shows a blank mark.
    (source / "doc.pdf").write_bytes(
        _build_pdf(
            None,
            differences="[1 /minus]",
            base_font="ABCDEF+CM_Maths_Symbols",
            flags=4,
            first_char=1,
            last_char=138,
            widths="[" + " 500" * 138 + "]",
        )
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        repair_pdf(source, target, verbose=False)

    written = _to_unicode_of_first_font(target / "doc.pdf")
    targets = re.findall(r"<[0-9A-Fa-f]{2}> <([0-9A-Fa-f]+)>", written)
    assert targets
    for value in targets:
        # Every target must decode, and a lone surrogate does not.
        text = bytes.fromhex(value).decode("utf-16-be")
        text.encode("utf-8")
    assert "<41> <D835DC9C>" in written  # a script capital, written as a full pair


def test_a_character_outside_the_basic_plane_survives_a_round_trip():
    assert _repair._decode_utf16_be_hex("D835DC9C") == 0x1D49C
    assert _repair._decode_utf16_be_hex("2212") == 0x2212
    assert to_utf16_be_hex(_repair._decode_utf16_be_hex("D835DC9C")) == "D835DC9C"


def test_a_font_known_to_misname_its_glyphs_is_not_guessed_at(dirs):
    source, target = dirs
    # This family is known to give its glyphs names that do not describe them. For a
    # variant we have no table for, we know nothing: the character must be left alone
    # rather than resolved from a name we have already established is untrue.
    (source / "doc.pdf").write_bytes(
        _build_pdf(
            None,
            differences="[36 /dollar]",
            base_font="ABCDEF+AdvPS9999",
            flags=4,
            first_char=36,
            last_char=36,
        )
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        report = repair_pdf(source, target, verbose=False)

    assert report.total_characters_completed == 0
    assert report.total_characters_corrected == 0


def test_a_correction_never_steps_outside_the_declared_range(dirs):
    source, target = dirs
    # The font declares one character. A reference table keyed by glyph name must not
    # reach codes the font never declared just because the base encoding names them.
    (source / "doc.pdf").write_bytes(
        _build_pdf(
            None,
            differences="[36 /dollar]",
            base_font="ABCDEF+AdvPS3D56D5",
            flags=4,
            first_char=36,
            last_char=36,
        )
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        repair_pdf(source, target, verbose=False)

    written = _to_unicode_of_first_font(target / "doc.pdf")
    assert "<24> <2265>" in written  # the declared character, corrected
    assert "<23>" not in written  # its neighbour, which the font never declared


def test_fonts_inside_a_form_object_are_repaired(dirs):
    source, target = dirs
    # Figures and headers are often drawn through a form object carrying its own fonts.
    (source / "doc.pdf").write_bytes(
        _build_pdf("1 beginbfchar\n<61> <000D>\nendbfchar", in_xobject=True)
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        report = repair_pdf(source, target, verbose=False)

    assert report.total_characters_corrected == 1
    assert report.files[0].was_repaired  # and so not reported as already correct


def test_a_missing_character_is_not_reported_as_a_wrong_one(dirs):
    source, target = dirs
    (source / "doc.pdf").write_bytes(_build_pdf(None))

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        report = repair_pdf(source, target, verbose=False)

    # The document described nothing, so nothing was wrong - only missing.
    assert report.total_characters_corrected == 0
    assert report.total_characters_completed >= 1


def test_writing_over_the_originals_is_refused(dirs):
    source, _ = dirs
    (source / "doc.pdf").write_bytes(_build_pdf(None))

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with pytest.raises(ValueError, match="different directories"):
            repair_pdf(source, source, verbose=False)


def test_a_whole_font_table_covers_codes_the_font_omits(dirs):
    source, target = dirs
    # This font draws a character at code 0 but starts its declared range at 1 - the
    # omission is part of the same producer fault the reference table exists to correct.
    # A table matched on a fingerprint of the whole font may fill that code in.
    (source / "doc.pdf").write_bytes(
        _build_pdf(
            None,
            differences="[1 /minus]",
            base_font="TeX_CM_Maths_Symbols",
            flags=4,
            first_char=1,
            last_char=138,
            widths="[" + " 500" * 138 + "]",
        )
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        repair_pdf(source, target, verbose=False)

    assert "<00> <2212>" in _to_unicode_of_first_font(target / "doc.pdf")
