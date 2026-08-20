"""Repair the text layer of PDF files whose characters are mis-encoded.

Some PDFs describe their characters incorrectly. The page looks perfect on screen, but
the text stored underneath is wrong: a minus sign may be missing entirely, or a "greater
than or equal" sign may be recorded as a dollar sign. When such a file is annotated, the
text captured in the labels is wrong too.

This module rewrites the character tables so the stored text matches what the page shows.
"""

# The PDF libraries are optional extras (`pip install kili[pdf]`), so they are imported
# where they are used rather than at module load time, and are not present at type-check
# time either.
# pyright: reportMissingImports=false
# pylint: disable=import-outside-toplevel

import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union

BETA_WARNING = (
    "The PDF repair utility is in beta and still being developed. It has been tested "
    "against a varied corpus of documents, but it does not yet fix every case. If you "
    "find a document that is not repaired, or one whose text the repair makes worse, "
    "please report it to Kili support so the reference tables can be extended."
)

_MISSING_DEPENDENCY = (
    "Repairing PDFs requires extra libraries. Install them with:\n\n    pip install kili[pdf]\n"
)


@dataclass
class RepairedFile:
    """The outcome of repairing a single PDF."""

    file_name: str
    """Name of the PDF file."""

    fonts_repaired: int = 0
    """How many of the file's fonts had their character table corrected."""

    characters_corrected: int = 0
    """How many character definitions were wrong in the file and have been put right.

    This counts distinct definitions, not occurrences: one corrected definition fixes
    every place that character appears in the document.
    """

    characters_completed: int = 0
    """How many character definitions were missing from the file and have been filled in."""

    error: Optional[str] = None
    """The reason the file could not be processed, when applicable."""

    @property
    def was_repaired(self) -> bool:
        """Whether anything was changed in this file."""
        return self.error is None and (self.characters_corrected + self.characters_completed) > 0


@dataclass
class PdfRepairReport:
    """A summary of a `repair_pdf` run."""

    files: list[RepairedFile] = field(default_factory=list)
    """One entry per PDF found in the input directory."""

    output_dir: Optional[str] = None
    """Directory the repaired files were written to."""

    @property
    def total_files(self) -> int:
        """How many PDFs were found."""
        return len(self.files)

    @property
    def repaired_files(self) -> list[RepairedFile]:
        """The files in which something was corrected."""
        return [file for file in self.files if file.was_repaired]

    @property
    def unchanged_files(self) -> list[RepairedFile]:
        """The files that needed no correction.

        They are copied through unmodified.
        """
        return [file for file in self.files if file.error is None and not file.was_repaired]

    @property
    def failed_files(self) -> list[RepairedFile]:
        """The files that could not be processed."""
        return [file for file in self.files if file.error is not None]

    @property
    def total_characters_corrected(self) -> int:
        """How many wrong character definitions were put right across every file."""
        return sum(file.characters_corrected for file in self.files)

    @property
    def total_characters_completed(self) -> int:
        """How many missing character definitions were filled in across every file."""
        return sum(file.characters_completed for file in self.files)

    def __str__(self) -> str:
        """Render the report as a readable summary."""
        lines = ["", "PDF text layer repair", "=" * 60]
        if self.output_dir:
            lines.append(f"Repaired files written to: {self.output_dir}")
        lines.append("")
        lines.append(f"{'PDFs found':<30}{self.total_files:>8}")
        lines.append(f"{'Repaired':<30}{len(self.repaired_files):>8}")
        lines.append(f"{'Already correct':<30}{len(self.unchanged_files):>8}")
        if self.failed_files:
            lines.append(f"{'Could not be processed':<30}{len(self.failed_files):>8}")
        lines.append(f"{'Wrong characters put right':<30}{self.total_characters_corrected:>8}")
        lines.append(f"{'Missing characters filled in':<30}{self.total_characters_completed:>8}")

        if self.repaired_files:
            lines += ["", "Repaired files:", "-" * 60]
            lines.append(f"  {'file':<44}{'put right':>11}{'filled in':>11}{'fonts':>8}")
            for file in sorted(
                self.repaired_files,
                key=lambda item: (-item.characters_corrected, -item.characters_completed),
            ):
                lines.append(
                    f"  {file.file_name[:42]:<44}"
                    f"{file.characters_corrected:>11}"
                    f"{file.characters_completed:>11}"
                    f"{file.fonts_repaired:>8}"
                )
        if self.failed_files:
            lines += ["", "Could not be processed:", "-" * 60]
            for file in self.failed_files:
                lines.append(f"  {file.file_name[:44]:<46}{file.error}")
        lines.append("")
        return "\n".join(lines)


def _check_dependencies() -> None:
    """Raise a helpful error when the optional PDF libraries are not installed."""
    try:
        import fontTools  # noqa: F401  # pylint: disable=unused-import,import-outside-toplevel
        import pypdf  # noqa: F401  # pylint: disable=unused-import,import-outside-toplevel
    except ImportError as err:
        raise ImportError(_MISSING_DEPENDENCY) from err


def repair_pdf(
    input_dir: Union[str, Path],
    output_dir: Union[str, Path],
    *,
    verbose: bool = True,
) -> PdfRepairReport:
    """Repair the text layer of every PDF in a directory.

    Read every PDF in `input_dir`, correct the character tables that describe its text,
    and write the result to `output_dir` under the same file name. PDFs that need no
    correction are copied through unchanged, so `output_dir` always holds a complete set.

    Your original files are never modified. The repaired files render exactly as before -
    only the invisible text layer changes.

    !!! warning "Beta feature"
        This feature is in beta and still being developed. It does not yet fix every case;
        please report documents that are not repaired, or that it makes worse, to Kili
        support so the reference tables can be extended.

    Args:
        input_dir: Directory containing the PDFs to repair.
        output_dir: Directory the repaired PDFs are written to. Created if missing.
        verbose: Whether to print the report once the run finishes.

    Returns:
        A report describing what was corrected, in total and per file.

    Raises:
        ImportError: If the optional PDF dependencies are not installed.
        FileNotFoundError: If `input_dir` does not exist.
        NotADirectoryError: If `input_dir` is not a directory.
        ValueError: If `input_dir` and `output_dir` are the same directory.

    Examples:
        >>> from kili.client import Kili
        >>> kili = Kili()
        >>> report = kili.repair_pdf(
        ...     input_dir="my_documents",
        ...     output_dir="my_documents_repaired",
        ... )
        >>> report.total_characters_corrected
        12

        Then import the repaired files as you normally would:

        >>> paths = sorted(Path("my_documents_repaired").glob("*.pdf"))
        >>> kili.append_many_to_dataset(
        ...     project_id="...",
        ...     content_array=[str(path) for path in paths],
        ...     external_id_array=[path.stem for path in paths],
        ... )
    """
    warnings.warn(BETA_WARNING, UserWarning, stacklevel=2)
    _check_dependencies()

    from kili.utils.pdf._repair import repair_file

    source_dir = Path(input_dir)
    if not source_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {source_dir}")
    if not source_dir.is_dir():
        raise NotADirectoryError(f"Not a directory: {source_dir}")

    target_dir = Path(output_dir)
    if target_dir.resolve() == source_dir.resolve():
        raise ValueError(
            "input_dir and output_dir must be different directories: this function never "
            "modifies your original files, so it cannot write the repaired ones over them."
        )
    target_dir.mkdir(parents=True, exist_ok=True)

    report = PdfRepairReport(output_dir=str(target_dir.resolve()))
    pdf_paths = sorted(
        path for path in source_dir.iterdir() if path.is_file() and path.suffix.lower() == ".pdf"
    )

    for path in pdf_paths:
        destination = target_dir / path.name
        result = RepairedFile(file_name=path.name)
        try:
            fonts, corrected, completed = repair_file(path, destination)
            result.fonts_repaired = fonts
            result.characters_corrected = corrected
            result.characters_completed = completed
        except Exception as err:  # pylint: disable=broad-except
            # One unreadable document must not stop the batch. Copy it through untouched
            # so the output directory still mirrors the input.
            result.error = f"{type(err).__name__}: {err}"[:80]
            try:
                destination.write_bytes(path.read_bytes())
            except OSError as copy_err:
                # The output directory is meant to hold a complete set; say so when it does not.
                result.error = f"{result.error} (and could not be copied: {copy_err})"[:160]
        report.files.append(result)

    if verbose:
        print(report)
    return report
