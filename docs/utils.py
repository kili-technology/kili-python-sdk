"""
Utils for inserting notebooks in Python SDK doc.

Notebooks are stored in recipes/ and are converted to markdown using this script.

Run 'python -m docs.utils convert <notebook_file>' at the root of repository to convert a notebook
to markdown.

Markdown files are stored in docs/sdk/tutorials/ and are inserted in the doc with mkdocs.yml.

Please run 'mkdocs serve' to check the result before committing your changes.
"""

import base64
import re
import shutil
from binascii import a2b_base64
from itertools import groupby
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, Optional, Sequence

import click
from nbconvert import MarkdownExporter
from nbconvert.preprocessors.base import Preprocessor
from nbconvert.preprocessors.tagremove import TagRemovePreprocessor

IGNORED_NOTEBOOKS = [
    "recipes/plugins_development.ipynb",
]

IGNORED_TUTORIALS = [
    "plugins_library",
]


class ExtractAttachmentsPreprocessor(Preprocessor):
    """
    Extract attachments in markdown cells.

    This preprocessor aims at adding image data
    to `metadata["outputs"]` for images copy-pasted in the notebook.
    """

    def preprocess_cell(self, cell, resources, cell_index):  # pylint: disable=arguments-renamed
        """Extract attachments in a markdown cell."""

        if "attachments" not in cell or not cell["attachments"]:
            return cell, resources

        resources["outputs"] = resources["outputs"] or {}

        for img_name, attachment in cell["attachments"].items():
            for mime, img_data in attachment.items():
                if mime in {"image/png", "image/jpeg"}:
                    img_data = a2b_base64(img_data)  # base64 to binary
                elif mime in {"image/svg+xml"}:
                    img_data = img_data.encode("UTF-8")  # SVG and XML already binary
                else:
                    raise ValueError(f"Unexpected mime type {mime}")

                new_img_name = f"attach_{cell_index}_{img_name}"

                if img_name.endswith(".gif") and mime == "image/png":
                    new_img_name = new_img_name.replace(".gif", ".png")

                resources["outputs"][new_img_name] = img_data

                if "source" in cell:
                    cell["source"] = cell["source"].replace("attachment:" + img_name, new_img_name)

        return cell, resources


class RemoveTqdmOutputPreprocessor(Preprocessor):
    """
    Remove tqdm progress bar output.
    """

    TQDM_PATTERNS = ("%|█", "█|", "/", " [", ":", "<", "it", "]")

    def is_tqdm_line(self, line):
        """Check if a line is a tqdm progress bar."""
        return all(pattern in line for pattern in self.TQDM_PATTERNS)

    def preprocess_cell(self, cell, resources, index):
        """Remove tqdm progress bar in a cell."""

        if "outputs" not in cell or not cell["outputs"]:
            return cell, resources

        for output in cell["outputs"]:
            if "text" in output:
                text = "\n".join(
                    [line for line in output["text"].splitlines() if not self.is_tqdm_line(line)]
                )
                if len(text) > 0 and output["text"].endswith("\n") and not text.endswith("\n"):
                    text += "\n"
                output["text"] = text

        return cell, resources


def embed_images_in_markdown(markdown: str, images: Dict[str, bytes], notebook_dir: Path) -> str:
    """Embed images in markdown in base64."""
    md_img_pattern = r"!\[(.*?)\]\((.*?)\)"  # matches ![]()
    matched_images = re.findall(md_img_pattern, markdown)
    for img_text, img_content in matched_images:
        if img_content in images:
            img_bytes = images[img_content]
        elif Path(notebook_dir / img_content).is_file():
            with open(Path(notebook_dir / img_content), "rb") as file:
                img_bytes = file.read()
        else:
            raise ValueError(f"Image {img_content} not found.")

        extension = img_content.split(".")[-1]
        encoded_img = base64.b64encode(img_bytes).decode("utf-8")
        after = f"![{img_text}](data:image/{extension};base64,{encoded_img})"
        markdown = markdown.replace(f"![{img_text}]({img_content})", after)
    return markdown


DEFAULT_REMOVE_CELL_TAGS = ("remove", "remove_cell", "test", "test_cell", "skip", "skip_cell")


@click.command(name="convert")
@click.argument(
    "ipynb_filepath",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
)
@click.option(
    "--md-output-filepath",
    type=click.Path(exists=False, path_type=Path),
    required=False,
    help="Output markdown.",
)
def notebook_to_markdown_cmd(
    ipynb_filepath: Path,
    md_output_filepath: Optional[Path] = None,
):
    """Command to generate markdown from a notebook.

    Args:
        ipynb_filepath: Path to notebook.
        md_output_filepath: Output path for markdown file.
    """
    md_output_filepath = notebook_to_markdown(
        ipynb_filepath=ipynb_filepath,
        md_output_filepath=md_output_filepath,
        remove_cell_tags=DEFAULT_REMOVE_CELL_TAGS,
    )
    print(f"Wrote {md_output_filepath}")


def notebook_to_markdown(
    ipynb_filepath: Path,
    md_output_filepath: Optional[Path],
    remove_cell_tags: Sequence,
) -> Path:
    """Generate markdown from a notebook."""
    if not md_output_filepath:
        md_output_filepath = Path(f"docs/sdk/tutorials/{ipynb_filepath.stem}.md")

    if md_output_filepath.suffix != ".md":
        raise ValueError(f"md_output_filepath must end with .md, got: {md_output_filepath}")

    ipynb_filepath = ipynb_filepath.resolve()
    md_output_filepath = md_output_filepath.resolve()

    md_exporter = MarkdownExporter()

    if remove_cell_tags is not None:
        tag_removal_preprocessor = TagRemovePreprocessor(
            remove_cell_tags=remove_cell_tags, enabled=True
        )
        md_exporter.register_preprocessor(tag_removal_preprocessor, enabled=True)

    md_exporter.register_preprocessor(ExtractAttachmentsPreprocessor(enable=True), enabled=True)
    md_exporter.register_preprocessor(RemoveTqdmOutputPreprocessor(enable=True), enabled=True)

    output = md_exporter.from_filename(str(ipynb_filepath))

    markdown_str, metadata = output
    markdown_str = embed_images_in_markdown(
        markdown_str, metadata["outputs"], Path(metadata["metadata"]["path"])
    )

    markdown_split_str = ["<!-- FILE AUTO GENERATED BY docs/utils.py DO NOT EDIT DIRECTLY -->"]
    # remove trailing spaces so that markdown file can pass trailing-whitespace precommit hook
    markdown_split_str.extend([line.rstrip() for line in markdown_str.splitlines()])
    # remove last empty lines so that markdown file can pass end-of-file-fixer precommit hook
    while markdown_split_str[-1] == "":
        markdown_split_str.pop()
    markdown_split_str.append("")  # add last empty line
    markdown_str = "\n".join(markdown_split_str)

    with open(md_output_filepath, "w", encoding="utf-8") as file:
        file.write(markdown_str)

    return md_output_filepath


class OutdatedMarkdownError(Exception):
    """Raised when markdown is not up to date with notebook."""


def check_markdown_up_to_date(ipynb_filepath: Path, md_filepath: Path, remove_cell_tags: Sequence):
    """
    Check if markdown file is up to date with its associated notebook.

    Overwrites the markdown file if it is not up to date.
    """
    assert ipynb_filepath.is_file(), f"{ipynb_filepath} does not exist."
    assert md_filepath.is_file(), f"{md_filepath} does not exist."

    with NamedTemporaryFile(suffix=".md") as temp_file:
        notebook_to_markdown(
            ipynb_filepath=ipynb_filepath,
            md_output_filepath=Path(temp_file.name),
            remove_cell_tags=remove_cell_tags,
        )
        with open(temp_file.name, "r", encoding="utf-8") as file:
            temp_markdown = file.read()

        with open(md_filepath, "r", encoding="utf-8") as file:
            markdown = file.read()

        if temp_markdown != markdown:
            shutil.copy(temp_file.name, md_filepath)
            raise OutdatedMarkdownError(
                f"{ipynb_filepath} is not up to date with {md_filepath}. {md_filepath.name} has"
                " been updated. Please run 'mkdocs serve' to check the result before committing."
            )


class OutdatedMkDocs(Exception):
    """Raised when mkdocs.yml is not up to date."""


def check_mkdocs_yml_up_to_date(md_filepath: Path):
    """Check if mkdocs.yml contains the tutorial markdown file."""
    with open("mkdocs.yml", encoding="utf-8") as file:
        mkdocs_config = file.read()

    if f"sdk/tutorials/{md_filepath.name}" not in mkdocs_config:
        raise OutdatedMkDocs(f"sdk/tutorials/{md_filepath.name} is not in mkdocs.yml.")


class NotebookTestMissingError(Exception):
    """Raised when notebook is not tested in test_notebooks.py."""


def check_notebook_tested(ipynb_filepath: Path):
    """Check if notebook is tested."""
    if f"recipes/{ipynb_filepath.name}" in IGNORED_NOTEBOOKS:
        return

    with open("tests/test_notebooks.py", encoding="utf-8") as file:
        test_notebooks_module_str = file.read()

    if f"recipes/{ipynb_filepath.name}" not in test_notebooks_module_str:
        raise NotebookTestMissingError(
            f"recipes/{ipynb_filepath.name} not found in test_notebooks.py."
        )


class ColabLinkMissingError(Exception):
    """Raised when notebook does not have a colab link."""


def check_colab_link_in_notebook(ipynb_filepath: Path):
    """Check if notebook has a colab link."""
    with open(ipynb_filepath, encoding="utf-8") as file:
        notebook_str = file.read()
    # pylint: disable=line-too-long
    if (
        f"https://colab.research.google.com/github/kili-technology/kili-python-sdk/blob/master/recipes/{ipynb_filepath.name}"
        not in notebook_str
    ):
        raise ColabLinkMissingError(f"Colab link not found in {ipynb_filepath.name}.")


@click.command(name="notebook_tutorials_commit_hook")
@click.argument(
    "modified_files",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    nargs=-1,
)
def notebook_tutorials_commit_hook(modified_files: Sequence[Path]):
    """
    Check if all notebooks in commit are up-to-date with their markdown files.

    `modified_files` are the files in commit that match:
        - markdown files in docs/sdk/tutorials/
        - notebooks in recipes/

    Also checks:
        - markdown files are in mkdocs.yml.
        - notebooks are tested in test_notebooks.py.
    """
    # get existing tutorials names
    existing_tutorials = list(Path("docs/sdk/tutorials").glob("*.md"))
    existing_tutorials = [
        tutorial.stem for tutorial in existing_tutorials if tutorial.stem not in IGNORED_TUTORIALS
    ]

    # group files by tutorial name (filename or notebooks and markdowns without extension)
    modified_files = sorted(modified_files, key=lambda path: path.stem)  # sort before grouping
    groupby_iter = groupby(modified_files, key=lambda path: path.stem)  # group by filename

    for tutorial_name, group in groupby_iter:
        group = list(group)

        # skip files that are not tutorials
        if tutorial_name not in existing_tutorials:
            continue

        # case when notebook is modified but not markdown
        if len(group) == 1 and group[0].suffix == ".ipynb":
            ipynb_filepath = group[0]
            md_filepath = Path("docs/sdk/tutorials") / f"{tutorial_name}.md"

        # case when markdown is modified but not notebook
        elif len(group) == 1 and group[0].suffix == ".md":
            md_filepath = group[0]
            ipynb_filepath = Path("recipes") / f"{tutorial_name}.ipynb"

        # both notebook and markdown got modified
        elif len(group) == 2:
            ipynb_filepath, md_filepath = sorted(group, key=lambda path: path.suffix)

        # group must have two files, one .md and one .ipynb
        else:
            raise ValueError(
                f"Expected two files (.md and .ipynb) in staging for tutorial '{tutorial_name}',"
                f" got {group}. Run 'python -m docs.utils convert <notebook_file>' at the root of"
                " repository to convert a notebook to markdown. Please run 'mkdocs serve' to check"
                " the result before committing your changes."
            )

        assert ipynb_filepath.suffix == ".ipynb", ipynb_filepath
        assert md_filepath.suffix == ".md", md_filepath
        ipynb_filepath = ipynb_filepath.resolve()
        md_filepath = md_filepath.resolve()

        check_mkdocs_yml_up_to_date(md_filepath)
        check_notebook_tested(ipynb_filepath)
        check_colab_link_in_notebook(ipynb_filepath)
        check_markdown_up_to_date(ipynb_filepath, md_filepath, DEFAULT_REMOVE_CELL_TAGS)


@click.group()
def main():
    """Main"""


if __name__ == "__main__":
    main.add_command(notebook_to_markdown_cmd)
    main.add_command(notebook_tutorials_commit_hook)
    main()
