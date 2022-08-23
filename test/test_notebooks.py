"""
Test notebooks with pytest
"""

import os
import subprocess

import nbformat
from nbconvert.preprocessors import CellExecutionError, ExecutePreprocessor


def process_notebook(notebook_filename):
    """
    Checks if an IPython notebook runs without error from start to finish.
    """
    with open(notebook_filename) as f:
        nb = nbformat.read(f, as_version=4)

    ep = ExecutePreprocessor(timeout=1000, kernel_name="python3")

    try:
        # Check that the notebook runs
        ep.preprocess(nb, {"metadata": {"path": ""}})
    except CellExecutionError:
        raise

    print(f"Successfully executed {notebook_filename}")
    return


def test_all_recipes():
    """
    Runs `process_notebook` on all notebooks in the git repository.
    """
    for notebook in [
        "test/integration/create_project.ipynb",
        "test/integration/export_labels.ipynb",
        "recipes/frame_dicom_data.ipynb",
        "test/integration/import_assets.ipynb",
        "test/integration/import_predictions.ipynb",
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
    ]:
        print("Testing", notebook)
        process_notebook(notebook)

    return


if __name__ == "__main__":
    test_all_recipes()
