import pytest

from kili.services.label_helpers.bbox import bbox_points_to_normalized_vertices


@pytest.mark.parametrize(
    "test_name,inputs,output",
    [
        (
            "box full image pixels",
            {
                "bottom_left": {"x": 0, "y": 0},
                "bottom_right": {"x": 1920, "y": 0},
                "top_right": {"x": 1920, "y": 1080},
                "top_left": {"x": 0, "y": 1080},
                "img_width": 1920,
                "img_height": 1080,
            },
            [{"x": 0, "y": 0}, {"x": 0, "y": 1}, {"x": 1, "y": 1}, {"x": 1, "y": 0}],
        ),
        (
            "box full image normalized pixels",
            {
                "bottom_left": {"x": 0, "y": 0},
                "bottom_right": {"x": 1, "y": 0},
                "top_right": {"x": 1, "y": 1},
                "top_left": {"x": 0, "y": 1},
            },
            [{"x": 0, "y": 0}, {"x": 0, "y": 1}, {"x": 1, "y": 1}, {"x": 1, "y": 0}],
        ),
        (
            "box left half part of the image",
            {
                "bottom_left": {"x": 0, "y": 0},
                "bottom_right": {"x": 1920 / 2, "y": 0},
                "top_right": {"x": 1920 / 2, "y": 1080},
                "top_left": {"x": 0, "y": 1080},
                "img_width": 1920,
                "img_height": 1080,
            },
            [{"x": 0, "y": 0}, {"x": 0, "y": 1}, {"x": 0.5, "y": 1}, {"x": 0.5, "y": 0}],
        ),
        (
            "box left half part of the image already normalized",
            {
                "bottom_left": {"x": 0, "y": 0},
                "bottom_right": {"x": 0.5, "y": 0},
                "top_right": {"x": 0.5, "y": 1},
                "top_left": {"x": 0, "y": 1},
            },
            [{"x": 0, "y": 0}, {"x": 0, "y": 1}, {"x": 0.5, "y": 1}, {"x": 0.5, "y": 0}],
        ),
        (
            "box right half part of the image",
            {
                "bottom_left": {"x": 0.5, "y": 0},
                "bottom_right": {"x": 1, "y": 0},
                "top_right": {"x": 1, "y": 1},
                "top_left": {"x": 0.5, "y": 1},
            },
            [{"x": 0.5, "y": 0}, {"x": 0.5, "y": 1}, {"x": 1, "y": 1}, {"x": 1, "y": 0}],
        ),
        (
            "box horizontal center part of the image full width",
            {
                "bottom_left": {"x": 0.0, "y": 0.25},
                "bottom_right": {"x": 1, "y": 0.25},
                "top_right": {"x": 1, "y": 0.75},
                "top_left": {"x": 0.0, "y": 0.75},
            },
            [{"x": 0, "y": 0.25}, {"x": 0, "y": 0.75}, {"x": 1, "y": 0.75}, {"x": 1, "y": 0.25}],
        ),
        (
            "square small box bottom left corner",
            {
                "bottom_left": {"x": 0, "y": 0},
                "bottom_right": {"x": 10, "y": 0},
                "top_right": {"x": 10, "y": 10},
                "top_left": {"x": 0, "y": 10},
                "img_width": 1920,
                "img_height": 1080,
            },
            [
                {"x": 0, "y": 0.9907407407407407},
                {"x": 0, "y": 1},
                {"x": 0.005208333333333333, "y": 1},
                {"x": 0.005208333333333333, "y": 0.9907407407407407},
            ],
        ),
        (
            "square small box bottom right corner",
            {
                "bottom_left": {"x": 1910, "y": 0},
                "bottom_right": {"x": 1920, "y": 0},
                "top_right": {"x": 1920, "y": 10},
                "top_left": {"x": 1910, "y": 10},
                "img_width": 1920,
                "img_height": 1080,
            },
            [
                {"x": 0.9947916666666666, "y": 0.9907407407407407},
                {"x": 0.9947916666666666, "y": 1},
                {"x": 1, "y": 1},
                {"x": 1, "y": 0.9907407407407407},
            ],
        ),
        (
            "square small box top right corner",
            {
                "bottom_left": {"x": 1910, "y": 1070},
                "bottom_right": {"x": 1920, "y": 1070},
                "top_right": {"x": 1920, "y": 1080},
                "top_left": {"x": 1910, "y": 1080},
                "img_width": 1920,
                "img_height": 1080,
            },
            [
                {"x": 0.9947916666666666, "y": 0},
                {"x": 0.9947916666666666, "y": 0.0092592592592593},
                {"x": 1, "y": 0.0092592592592593},
                {"x": 1, "y": 0},
            ],
        ),
        (
            "square small box top left corner",
            {
                "bottom_left": {"x": 0, "y": 1070},
                "bottom_right": {"x": 10, "y": 1070},
                "top_right": {"x": 10, "y": 1080},
                "top_left": {"x": 0, "y": 1080},
                "img_width": 1920,
                "img_height": 1080,
            },
            [
                {"x": 0, "y": 0},
                {"x": 0, "y": 0.0092592592592593},
                {"x": 0.005208333333333333, "y": 0.0092592592592593},
                {"x": 0.005208333333333333, "y": 0},
            ],
        ),
        (
            "small box somewhere in the top right quarter of the image",
            {
                "bottom_left": {"x": 1000, "y": 700},
                "bottom_right": {"x": 1050, "y": 700},
                "top_right": {"x": 1050, "y": 750},
                "top_left": {"x": 1000, "y": 750},
                "img_width": 1920,
                "img_height": 1080,
            },
            [
                {"x": 0.5208333333333334, "y": 0.3055555555555556},
                {"x": 0.5208333333333334, "y": 0.35185185185185186},
                {"x": 0.546875, "y": 0.35185185185185186},
                {"x": 0.546875, "y": 0.3055555555555556},
            ],
        ),
    ],
)
def test_bbox_points_to_normalized_vertices(test_name, inputs, output):
    vertices = bbox_points_to_normalized_vertices(**inputs)
    assert vertices == output


# DO NOT DELETE. USED FOR DEBUGGING
# def debug_using_kili_project():
#     kili = Kili()
#     project = kili.create_project(
#         input_type="IMAGE",
#         json_interface={
#             "jobs": {
#                 "OBJECT_DETECTION_JOB": {
#                     "content": {
#                         "categories": {"A": {"children": [], "color": "#472CED", "name": "A"}},
#                         "input": "radio",
#                     },
#                     "instruction": "Box",
#                     "mlTask": "OBJECT_DETECTION",
#                     "required": 1,
#                     "tools": ["rectangle"],
#                     "isChild": False,
#                 }
#             }
#         },
#         title="test bbox",
#     )

#     kili.append_many_to_dataset(
#         project["id"],
#         content_array=[
#             "https://storage.googleapis.com/label-public-staging/car/car_1.jpg"  # 1920 1080
#         ],
#         external_id_array=["car_1"],
#     )

#     points = {
#         "bottom_left": {"x": 1000, "y": 700},
#         "bottom_right": {"x": 1050, "y": 700},
#         "top_right": {"x": 1050, "y": 750},
#         "top_left": {"x": 1000, "y": 750},
#         "img_width": 1920,
#         "img_height": 1080,
#     }
#     normalizedVertices = bbox_points_to_normalized_vertices(**points)
#     kili.append_labels(
#         json_response_array=[
#             {
#                 "OBJECT_DETECTION_JOB": {
#                     "annotations": [
#                         {
#                             "boundingPoly": [{"normalizedVertices": normalizedVertices}],
#                             "categories": [{"name": "A"}],
#                             "type": "rectangle",
#                         }
#                     ]
#                 }
#             }
#         ],
#         asset_external_id_array=["car_1"],
#         project_id=project["id"],
#     )


# if __name__ == "__main__":
#     from kili.client import Kili

#     debug_using_kili_project()
