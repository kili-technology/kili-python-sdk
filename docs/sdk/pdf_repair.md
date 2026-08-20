# Repairing PDF text layers

## Why you might need this

Every PDF contains two things: the page you see, and an invisible **text layer** that
records which character each mark on the page stands for. Kili uses that text layer when
you select text to annotate.

In some PDFs the text layer is wrong. The page displays perfectly, but the characters
recorded underneath do not match it. This is a flaw in the software that produced the
document, and it is common in scientific and technical publishing.

Two examples of what it looks like in practice:

| What the page shows | What the text layer says |
| ------------------- | ------------------------ |
| `offset −3.5 mm` | `offset  3.5 mm` — the minus sign is missing |
| `pressure ≥ 20 bar` | `pressure $ 20 bar` — a dollar sign instead |

The consequences when annotating such a document are:

- Annotations capture the wrong text, so your labelled data is wrong.
- Text you can see on the page cannot be selected, because it is not really there.
- In some cases the annotation cannot be saved at all.

The second example is the more dangerous one: nothing looks broken, so the mistake ends
up in your dataset unnoticed.

## How to repair

There are three practical ways to deal with this.

- **Repair the document with the Kili SDK** — described below, and currently in beta. It
  works from what the document says about its own characters, so it is exact and
  repeatable, and the corrected text stays attached to the right position on the page. It
  cannot help where a character is described nowhere in the file.
- **Run an OCR tool over the pages.** OCR reads the page as an image, so broken character
  tables do not affect it. In practice though it tends to introduce new errors while
  fixing others — mathematical symbols get approximated, superscripts and reference
  numbers are often lost — and it replaces the whole text layer instead of correcting it.
- **Use an LLM model with vision capabilities.** These are quite effective at this when
  used well, particularly when asked to identify individual characters from the document's
  fonts rather than to transcribe whole pages. The risk is hallucination: an LLM model can
  return a plausible character that is not the one on the page, so its answers are worth
  reviewing before you rely on them.

## Repairing with the Kili SDK

!!! warning "Beta feature"
    This utility is in beta and still being developed. It has been tested against a varied
    corpus of documents from many different publishing tools, but it does not yet fix
    every case: some documents will be only partly repaired.

    If you come across a document that is not repaired, or one whose text the repair makes
    worse, please contact Kili support and let us know. Every reported case is used to
    extend the reference tables — and because those tables are keyed on fonts rather than
    on documents, reporting one document improves the result for every document that uses
    the same fonts.

### Installation

This feature needs two extra libraries, which are not installed with Kili by default:

```bash
pip install kili[pdf]
```

### Usage

Run the repair before importing your documents:

```python
from kili.client import Kili

kili = Kili()

report = kili.repair_pdf(
    input_dir="documents",
    output_dir="documents_repaired",
)
```

If you use the domain client (`from kili.client_domain import Kili`), the same method is
available on the `assets` namespace:

```python
report = kili.assets.repair_pdf(
    input_dir="documents",
    output_dir="documents_repaired",
)
```

Every PDF in `documents` is read, corrected, and written to `documents_repaired` under the
same file name. Documents that need no correction are copied through unchanged, so the
output directory always holds a complete set ready to import.

**Your original files are never modified**, and repaired documents look exactly the same
as before — only the invisible text layer changes.

Then import the repaired documents as usual:

```python
from pathlib import Path

paths = sorted(Path("documents_repaired").glob("*.pdf"))
kili.append_many_to_dataset(
    project_id="<project_id>",
    content_array=[str(path) for path in paths],
    external_id_array=[path.stem for path in paths],
)
```

With the domain client, use `create_pdf`:

```python
from pathlib import Path

for path in Path("documents_repaired").glob("*.pdf"):
    kili.assets.create_pdf(
        project_id="<project_id>",
        path=str(path),
        external_id=path.stem,
    )
```

!!! tip "Repair before you annotate"
    Run the repair on your documents **before** anyone starts labelling them. Repairing a
    document that has already been annotated can shift the position of existing
    annotations.

### Reading the report

The report is printed when the run finishes, and is also returned so you can act on it:

```
PDF text layer repair
============================================================
Repaired files written to: /home/user/documents_repaired

PDFs found                          12
Repaired                             2
Already correct                     10
Wrong characters put right          14
Missing characters filled in       640

Repaired files:
------------------------------------------------------------
  file                                          put right  filled in   fonts
  specification.pdf                                    12        640      18
  appendix.pdf                                          2          0       1
```

- **Wrong characters put right** — characters the document described incorrectly. These
  are the ones that would have corrupted your annotations.
- **Missing characters filled in** — characters the document did not describe at all.
  Filling them in makes the text layer complete.

Both counts are per character *definition*, not per occurrence: correcting one definition
fixes every place that character appears in the document.

You can use the report in your own code, for example to review the affected documents:

```python
report = kili.repair_pdf(
    input_dir="documents",
    output_dir="documents_repaired",
    verbose=False,
)

for file in report.repaired_files:
    print(f"{file.file_name}: {file.characters_corrected} characters put right")

for file in report.failed_files:
    print(f"Could not process {file.file_name}: {file.error}")
```

### What this can and cannot fix

The repair works out what each character really is from the information inside the
document: the names its fonts give their characters, published character tables, and a set
of tables for fonts that are known to describe themselves incorrectly. **Nothing is
guessed** — where the document holds no usable information, the character is left alone
rather than replaced with something that might be wrong.

As a result some documents are only partly repaired. Known limitations:

- Documents with **no text layer at all** — a scan, for instance — cannot be repaired:
  there are no characters to correct.
- Some **mathematical and decorative symbols** may remain unresolved, where the document
  describes them nowhere.
- Documents written in **scripts other than the Latin alphabet** — Arabic, Hebrew,
  Chinese, Japanese, Korean, Thai and the Indic scripts among them — are left untouched.
  The repair currently targets Latin-alphabet text and mathematical symbols.

If a document is still not right after repair, please contact Kili support so the
reference tables can be extended. The drawings of the unresolved characters are usually
enough; you do not need to send the document itself.

## Reference

::: kili.utils.pdf.repair_pdf

::: kili.utils.pdf.PdfRepairReport

::: kili.utils.pdf.RepairedFile
