"""
Test notebooks with pytest
"""
import nbformat
import pytest
from nbconvert.preprocessors.execute import ExecutePreprocessor


def process_notebook(notebook_filename):
    """
    Checks if an IPython notebook runs without error from start to finish.
    """
    with open(notebook_filename, encoding="utf-8") as n_f:
        notebook = nbformat.read(n_f, as_version=4)

    execute_preprocessor = ExecutePreprocessor(timeout=1000, kernel_name="python3")
    execute_preprocessor.preprocess(notebook, {"metadata": {"path": ""}})


@pytest.mark.parametrize(
    "notebook_file",
    [
        "tests/integration/create_project.ipynb",
        "tests/integration/export_labels.ipynb",
        "recipes/frame_dicom_data.ipynb",
        "tests/integration/import_assets.ipynb",
        "tests/integration/import_predictions.ipynb",
        "recipes/import_text_assets.ipynb",
        "recipes/inference_labels.ipynb",
        "recipes/medical_imaging.ipynb",
        "recipes/ocr_pre_annotations.ipynb",
        "recipes/pixel_level_masks.ipynb",
        "recipes/query_methods.ipynb",
        "recipes/webhooks.ipynb",
        "recipes/getting-started/getting_started-image_bounding_box_detection.ipynb",
        "recipes/getting-started/getting_started-image_classification.ipynb",
        "recipes/getting-started/getting_started-image_semantic_segmentation.ipynb",
        "recipes/getting-started/getting_started-named-entity-recognition.ipynb",
    ],
)
def test_all_recipes(notebook_file):
    """
    Runs `process_notebook` on all notebooks in the git repository.
    """
    process_notebook(notebook_file)

    return
