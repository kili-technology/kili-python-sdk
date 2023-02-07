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
        "tests/e2e/create_project.ipynb",
        "tests/e2e/export_labels.ipynb",
        "tests/e2e/import_assets.ipynb",
        "tests/e2e/import_predictions.ipynb",
        "tests/e2e/paginated_calls_project_lifecycle.ipynb",
        "tests/e2e/plugin_workflow.ipynb",
        "recipes/import_text_assets.ipynb",
        "recipes/importing_assets_and_labels.ipynb",
        "recipes/importing_video_assets.ipynb",
        "recipes/inference_labels.ipynb",
        "recipes/medical_imaging.ipynb",
        "recipes/ocr_pre_annotations.ipynb",
        "recipes/pixel_level_masks.ipynb",
        # "recipes/plugins_example.ipynb",
        "recipes/set_up_workflows.ipynb",
        "recipes/export_a_kili_project.ipynb",
        "recipes/plugins_example.ipynb",
        "recipes/basic_project_setup.ipynb",
        "recipes/importing_assets_and_labels.ipynb",
        "recipes/importing_video_assets.ipynb",
    ],
)
def test_all_recipes(notebook_file):
    """
    Runs `process_notebook` on all notebooks in the git repository.
    """
    process_notebook(notebook_file)

    return
