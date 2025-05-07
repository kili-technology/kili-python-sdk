import math
from pathlib import Path
from typing import Dict, List, Optional, Union

from kili_formats.types import Job


def get_asset(
    content_path: Path,
    with_annotation: Optional[List[Dict]],
    negative_polygons: Union[List[List[Dict]], None] = None,
) -> Dict:
    # without annotation means that: there is a label for the asset
    # but there is no labeling data for the job.
    # `annotations=[]` should not exist.
    json_response = {"author": {"firstname": "Jean-Pierre", "lastname": "Dupont"}}

    if with_annotation:
        json_response = {
            **json_response,
            "JOB_0": {
                "annotations": [
                    {
                        "categories": [{"confidence": 100, "name": "OBJECT_A"}],
                        "jobName": "JOB_0",
                        "mid": "2022040515434712-7532",
                        "mlTask": "OBJECT_DETECTION",
                        "boundingPoly": [{"normalizedVertices": with_annotation}],
                        "type": "semantic",
                        "children": {},
                    }
                ]
            },
        }
        if negative_polygons:
            json_response["JOB_0"]["annotations"][0]["boundingPoly"] += map(
                lambda negative_polygon: {"normalizedVertices": negative_polygon}, negative_polygons
            )

    return {
        "latestLabel": {"jsonResponse": json_response},
        "externalId": "ca/r_1",
        "jsonContent": "",
        "content": str(content_path),
    }


def estimate_rotated_bb_from_kili_poly(
    coco_annotation: Dict, coco_image: Dict, kili_annotation: Dict
):
    """estimate_rotated_bb_from_kili_poly.

    Convert a rotated bounding box encoded into normalized vertices in Kili, into a rotated bounding
    box, which is encoded by an unnormalized horizontal bounding box
    (top_left_x, top_left_y, width, height).
    """

    def _is_rectangle(vertices: List[Dict]) -> bool:
        """Check that the polygon has 4 vertices and at least 3 right angles."""
        if len(vertices) != 4:
            return False
        vector_1 = (vertices[1]["x"] - vertices[0]["x"], vertices[1]["y"] - vertices[0]["y"])
        vector_2 = (vertices[2]["x"] - vertices[1]["x"], vertices[2]["y"] - vertices[1]["y"])
        vector_3 = (vertices[3]["x"] - vertices[2]["x"], vertices[3]["y"] - vertices[2]["y"])
        vector_4 = (vertices[0]["x"] - vertices[3]["x"], vertices[0]["y"] - vertices[3]["y"])

        inner_product_1 = vector_1[0] * vector_2[0] + vector_1[1] * vector_2[1]
        inner_product_2 = vector_2[0] * vector_3[0] + vector_2[1] * vector_3[1]
        inner_product_3 = vector_3[0] * vector_4[0] + vector_3[1] * vector_4[1]

        eps = 1e-10

        return inner_product_1 < eps and inner_product_2 < eps and inner_product_3 < eps

    def distance(point1: Dict, point2: Dict) -> float:
        return math.sqrt(
            math.pow(point1["x"] - point2["x"], 2) + math.pow(point1["y"] - point2["y"], 2)
        )

    def angle_to_horizontal(point1: Dict, point2: Dict):
        return math.degrees(math.acos((point2["x"] - point1["x"]) / distance(point1, point2)))

    normalized_polygon = kili_annotation["boundingPoly"][0]["normalizedVertices"]
    image_width = coco_image["width"]
    image_height = coco_image["height"]
    pixel_polygon = [
        {"x": p["x"] * image_width, "y": p["y"] * image_height} for p in normalized_polygon
    ]

    if not _is_rectangle(pixel_polygon):
        return coco_annotation

    # takes the top point, and the one on the left if there are ex-aequos
    _, _, top_left_ind, top_left_point = min(
        (p["y"], p["x"], ind, p) for ind, p in enumerate(pixel_polygon)
    )
    del pixel_polygon[top_left_ind]

    # takes the next point in the bottom-right quadrant and take the
    # minimum angle in the bottom-right quadrant is the right one
    # by convention, the width is the side with the minimum angle to the horizontal
    angle, width, bottom_right_ind = min(
        (angle_to_horizontal(top_left_point, p), distance(top_left_point, p), ind)
        for ind, p in enumerate(pixel_polygon)
        if p["x"] > top_left_point["x"]
    )
    del pixel_polygon[bottom_right_ind]

    # The height is given by the point at the minimal distance from top_point
    # (the other remaining one is the diagonal)
    height = min(distance(top_left_point, p) for p in pixel_polygon)

    attributes = {**coco_annotation.get("attributes", {}), "rotation": angle}
    bbox = [
        top_left_point["x"],
        top_left_point["y"],
        width,
        height,
    ]

    return {**coco_annotation, "attributes": attributes, "bbox": bbox}


DESSERT_JOB = Job(
    content={
        "categories": {"APPLE_PIE": {"name": "apple_pie"}, "TIRAMISU": {"name": "tiramisu"}},
    },
    instruction="dessert",
    isChild=False,
    tools=["rectangle"],
    mlTask="OBJECT_DETECTION",
    models=None,
    isVisible=True,
    required=0,
    isNew=False,
)

MAIN_JOB = Job(
    content={
        "categories": {"PIZZA": {"name": "pizza"}, "SPAGHETTIS": {"name": "spaghettis"}},
    },
    instruction="main course",
    isChild=False,
    tools=["rectangle"],
    mlTask="OBJECT_DETECTION",
    models=None,
    isVisible=True,
    required=0,
    isNew=False,
)

TASTY_JOB = Job(
    content={
        "categories": {"TASTY": {"name": "tasty"}, "NOT_TASTY": {"name": "not tasty"}},
    },
    instruction="is it tasty",
    isChild=False,
    tools=[],
    mlTask="CLASSIFICATION",
    models=None,
    isVisible=True,
    required=0,
    isNew=False,
)


# DO NOT DELETE: to use for debugging
# def display_kili_and_coco_bbox(
#     path: Path, expected_segmentation: List[Dict], coco_annotation: Dict
# ):
#     import matplotlib.patches as patches
#     import matplotlib.pyplot as plt
#     import numpy as np
#     from PIL import Image

#     im = Image.open(path)
#     _, ax = plt.subplots()
#     ax.imshow(im) # type: ignore
#     seg1 = patches.Polygon(
#         xy=np.reshape(expected_segmentation, [-1, 2]), # type: ignore
#         fill=False,
#         edgecolor="g",
#         linewidth=2,
#     )
#     ax.add_patch(seg1)

#     x, y, w, h = coco_annotation["annotations"][0]["bbox"]
#     angle = coco_annotation["annotations"][0]["attributes"]["rotation"]
#     seg2 = patches.Rectangle(xy=[x, y], width=w, height=h, angle=angle, fill=False, edgecolor="r")
#     ax.add_patch(seg2)
#     plt.show()
