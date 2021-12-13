"""
Test notebooks with pytest
"""

import os
import subprocess

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert.preprocessors import CellExecutionError

RECIPES_DIR = './recipes'
RECIPES_TESTED = [
    'create_project.ipynb',
    'export_labels.ipynb',
    'frame_dicom_data.ipynb',
    'import_assets.ipynb',
    'import_predictions.ipynb',
    'import_text_assets.ipynb',
    'inference_labels.ipynb',
    'medical_imaging.ipynb',
    'ocr_pre_annotations.ipynb',
    'pixel_level_masks.ipynb',
    'query_methods.ipynb',
    'webhooks.ipynb',
    'getting-started/getting_started-image_bounding_box_detection.ipynb',
    'getting-started/getting_started-image_classification.ipynb',
    'getting-started/getting_started-image_semantic_segmentation.ipynb',
    'getting-started/getting_started-named-entity-recognition.ipynb',
]

def process_notebook(notebook_filename):
    """
    Checks if an IPython notebook runs without error from start to finish.
    """
    with open(notebook_filename) as f:
        nb = nbformat.read(f, as_version=4)
    
    ep = ExecutePreprocessor(timeout=1000, kernel_name='python3')

    try:
        # Check that the notebook runs
        ep.preprocess(nb, {'metadata': {'path': ''}})
    except CellExecutionError:
        raise
         
    print(f"Successfully executed {notebook_filename}")
    return
    
def test_all_recipes():
    """
    Runs `process_notebook` on all notebooks in the git repository.
    """
    notebooks = [os.path.join(RECIPES_DIR, recipe) for recipe in RECIPES_TESTED]
    for notebook in notebooks:
        print("Testing", notebook)
        process_notebook(notebook)
        
    return

if __name__ == '__main__':
    test_all_recipes()
    