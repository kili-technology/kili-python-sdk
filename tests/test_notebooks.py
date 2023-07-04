"""Test notebooks with pytest."""
import os

import nbformat
import pytest
from nbconvert.preprocessors.execute import ExecutePreprocessor


def process_notebook(notebook_filename):
    """Checks if an IPython notebook runs without error from start to finish."""
    with open(notebook_filename, encoding="utf-8") as n_f:
        notebook = nbformat.read(n_f, as_version=4)

    execute_preprocessor = ExecutePreprocessor(timeout=1000, kernel_name="python3")
    execute_preprocessor.preprocess(notebook, {"metadata": {"path": ""}})


@pytest.mark.parametrize(
    "notebook_file",
    [
        "tests/e2e/create_project.ipynb",
        "tests/e2e/export_labels.ipynb",
        "tests/e2e/import_assets.ipynb",
        "tests/e2e/import_predictions.ipynb",
        "tests/e2e/paginated_calls_project_lifecycle.ipynb",
        pytest.param(
            "tests/e2e/plugin_workflow.ipynb",
            marks=pytest.mark.skipif(
                "lts.cloud" in os.environ["KILI_API_ENDPOINT"],
                reason="Feature not available on premise",
            ),
        ),
        "recipes/basic_project_setup.ipynb",
        "recipes/export_a_kili_project.ipynb",
        "recipes/frame_dicom_data.ipynb",
        # "recipes/finetuning_dinov2.ipynb",  # not testable because requires GPU
        "recipes/import_text_assets.ipynb",
        "recipes/importing_assets_and_metadata.ipynb",
        "recipes/importing_pdf_assets.ipynb",
        "recipes/importing_labels.ipynb",
        "recipes/importing_video_assets.ipynb",
        "recipes/inference_labels.ipynb",
        "recipes/label_parsing.ipynb",
        "recipes/medical_imaging.ipynb",
        # "recipes/ner_pre_annotations_openai.ipynb",
        "recipes/ocr_pre_annotations.ipynb",
        "recipes/pixel_level_masks.ipynb",
        pytest.param(
            "recipes/plugins_example.ipynb",
            marks=pytest.mark.skipif(
                "lts.cloud" in os.environ["KILI_API_ENDPOINT"],
                reason="Feature not available on premise",
            ),
        ),
        # "recipes/plugins_development.ipynb"
        "recipes/set_up_workflows.ipynb",
        # "recipes/tagtog_to_kili.ipynb",  # not testable because data is private
        "recipes/webhooks_example.ipynb",
    ],
)
def test_all_recipes(notebook_file):
    """Runs `process_notebook` on all notebooks in the git repository."""
    process_notebook(notebook_file)
