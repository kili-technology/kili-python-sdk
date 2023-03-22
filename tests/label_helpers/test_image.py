import cv2
import matplotlib.pyplot as plt
import numpy as np
import pytest
from PIL import Image

from kili.label_helpers import mask_to_vertices


def test_mask_to_vertices_simple_image():
    # create grayscale image
    im = Image.new(mode="L", size=(5, 5), color=0)

    # create a 3x3 empty box in the middle of the image
    im.putpixel((1, 1), 255)
    im.putpixel((1, 2), 255)
    im.putpixel((1, 3), 255)
    im.putpixel((2, 1), 255)
    im.putpixel((2, 3), 255)
    im.putpixel((3, 1), 255)
    im.putpixel((3, 2), 255)
    im.putpixel((3, 3), 255)

    normalized_vertices = mask_to_vertices(im)
    assert normalized_vertices == [
        {"x": 0.2, "y": 0.2},
        {"x": 0.2, "y": 0.8},
        {"x": 0.8, "y": 0.8},
        {"x": 0.8, "y": 0.2},
    ]


# DO NOT DELETE. USED FOR DEBUGGING
def debug_using_kili_project():
    kili = Kili()
    project = kili.create_project(
        input_type="IMAGE",
        json_interface={
            "jobs": {
                "OBJECT_DETECTION_JOB": {
                    "content": {
                        "categories": {"A": {"children": [], "color": "#472CED", "name": "A"}},
                        "input": "radio",
                    },
                    "instruction": "Box",
                    "mlTask": "OBJECT_DETECTION",
                    "required": 1,
                    "tools": ["semantic"],
                    "isChild": False,
                }
            }
        },
        title="test bbox",
    )

    kili.append_many_to_dataset(
        project["id"],
        content_array=[
            "https://farm7.staticflickr.com/6153/6181981748_6a225c275d_z.jpg"  # 426x640
        ],
        external_id_array=["moto"],
    )

    im = cv2.imread("../../recipes/img/HUMAN.mask.png")
    im = im[:, :, 0]
    normalizedVertices = mask_to_vertices(im)

    kili.append_labels(
        json_response_array=[
            {
                "OBJECT_DETECTION_JOB": {
                    "annotations": [
                        {
                            "boundingPoly": [{"normalizedVertices": normalizedVertices}],
                            "categories": [{"name": "A"}],
                            "type": "semantic",
                        }
                    ]
                }
            }
        ],
        asset_external_id_array=["moto"],
        project_id=project["id"],
    )


if __name__ == "__main__":
    from kili.client import Kili

    # test_mask_to_vertices_simple_image()
    debug_using_kili_project()
