"""Test notebooks with pytest."""
import os

import nbformat
import pytest
from nbconvert.preprocessors.execute import ExecutePreprocessor


def process_notebook(notebook_filename: str) -> None:
    """Check if an IPython notebook runs without error from start to finish."""
    with open(notebook_filename, encoding="utf-8") as n_f:
        notebook = nbformat.read(n_f, as_version=4)

    execute_preprocessor = ExecutePreprocessor(timeout=1000, kernel_name="python3")
    execute_preprocessor.preprocess(notebook, {"metadata": {"path": ""}})


@pytest.mark.parametrize(
    ("notebook_file", "requires_admin_rights"),
    [
        ("tests/e2e/create_project.ipynb", False),
        ("tests/e2e/export_labels.ipynb", False),
        ("tests/e2e/import_assets.ipynb", False),
        ("tests/e2e/import_predictions.ipynb", False),
        pytest.param(
            "tests/e2e/plugin_workflow.ipynb",
            False,
            marks=pytest.mark.skipif(
                "lts.cloud" in os.environ["KILI_API_ENDPOINT"],
                reason="Feature not available on premise",
            ),
        ),
        ("recipes/basic_project_setup.ipynb", False),
        ("recipes/export_a_kili_project.ipynb", True),
        ("recipes/frame_dicom_data.ipynb", False),
        # "recipes/finetuning_dinov2.ipynb",  # not testable because requires GPU
        ("recipes/geojson.ipynb", False),
        ("recipes/importing_coco.ipynb", False),
        ("recipes/importing_pascalvoc.ipynb", False),
        ("recipes/import_text_assets.ipynb", False),
        ("recipes/importing_assets_and_metadata.ipynb", False),
        ("recipes/importing_pdf_assets.ipynb", False),
        ("recipes/importing_labels.ipynb", False),
        ("recipes/importing_video_assets.ipynb", False),
        ("recipes/inference_labels.ipynb", False),
        ("recipes/label_parsing.ipynb", False),
        ("recipes/medical_imaging.ipynb", False),
        ("recipes/ner_pre_annotations_openai.ipynb", False),
        ("recipes/ocr_pre_annotations.ipynb", False),
        ("recipes/pixel_level_masks.ipynb", False),
        pytest.param(
            "recipes/plugins_example.ipynb",
            False,
            marks=pytest.mark.skipif(
                "lts.cloud" in os.environ["KILI_API_ENDPOINT"],
                reason="Feature not available on premise",
            ),
        ),
        # "recipes/plugins_development.ipynb", False
        ("recipes/set_up_workflows.ipynb", False),
        # "recipes/tagtog_to_kili.ipynb",  # not testable because data is private
        ("recipes/webhooks_example.ipynb", False),
    ],
)
def test_all_recipes(
    notebook_file: str,
    requires_admin_rights: bool,  # noqa: FBT001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Runs `process_notebook` on all notebooks in the git repository."""
    initial_api_key = os.environ["KILI_API_KEY"]
    try:
        if requires_admin_rights:
            monkeypatch.setenv("KILI_API_KEY", os.environ["KILI_API_KEY_ADMIN"])
        process_notebook(notebook_file)
    finally:
        monkeypatch.setenv("KILI_API_KEY", initial_api_key)
