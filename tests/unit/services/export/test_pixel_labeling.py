from kili.services.export.format.pixel_labeling import (
    convert_to_pixel_coords,
    get_asset_pixel_dimensions,
    is_pixel_labeling_project,
)

WIDTH, HEIGHT = 11794, 11842


def _asset_with_label(json_response: dict) -> dict:
    return {
        "geospatialExportMetadata": [{"labelingCRS": "PIXEL", "width": WIDTH, "height": HEIGHT}],
        "latestLabel": {"jsonResponse": json_response},
    }


def test_is_pixel_labeling_project():
    assert is_pixel_labeling_project({"geospatialSettings": {"labelingCRSCode": "PIXEL"}})
    assert not is_pixel_labeling_project({"geospatialSettings": {"labelingCRSCode": "EPSG:4326"}})
    assert not is_pixel_labeling_project({})


def test_get_asset_pixel_dimensions():
    assert get_asset_pixel_dimensions(_asset_with_label({})) == (WIDTH, HEIGHT)
    assert get_asset_pixel_dimensions({}) is None


def test_convert_bounding_poly_to_pixels():
    asset = _asset_with_label(
        {
            "JOB": {
                "annotations": [
                    {
                        "boundingPoly": [
                            {"normalizedVertices": [{"x": 0.5, "y": 0.25}]},
                        ]
                    }
                ]
            }
        }
    )

    convert_to_pixel_coords(asset)

    assert asset["latestLabel"]["jsonResponse"]["JOB"]["annotations"][0]["boundingPoly"][0][
        "normalizedVertices"
    ] == [{"x": WIDTH * 0.5, "y": HEIGHT * 0.25}]


def test_convert_is_a_no_op_without_dimensions():
    """An asset imported before the dimensions were recorded keeps its coordinates."""
    asset = {
        "latestLabel": {"jsonResponse": {"JOB": {"annotations": [{"point": {"x": 0.1, "y": 0.2}}]}}}
    }

    convert_to_pixel_coords(asset)

    assert asset["latestLabel"]["jsonResponse"]["JOB"]["annotations"][0]["point"] == {
        "x": 0.1,
        "y": 0.2,
    }


def test_convert_pose_estimation_points_to_pixels():
    asset = _asset_with_label(
        {
            "JOB": {
                "annotations": [
                    {
                        "points": [
                            {"code": "HEAD", "jobName": "JOB", "point": {"x": 0.5, "y": 0.5}},
                            {"code": "TAIL", "jobName": "JOB"},
                        ]
                    }
                ]
            }
        }
    )

    convert_to_pixel_coords(asset)

    points = asset["latestLabel"]["jsonResponse"]["JOB"]["annotations"][0]["points"]
    assert points[0]["point"] == {"x": WIDTH * 0.5, "y": HEIGHT * 0.5}
    assert points[1] == {"code": "TAIL", "jobName": "JOB"}


def test_convert_nested_job_annotations_to_pixels():
    asset = _asset_with_label(
        {
            "JOB": {
                "annotations": [
                    {
                        "point": {"x": 0.1, "y": 0.2},
                        "children": {
                            "NESTED_JOB": {"annotations": [{"point": {"x": 0.4, "y": 0.8}}]}
                        },
                    }
                ]
            }
        }
    )

    convert_to_pixel_coords(asset)

    annotation = asset["latestLabel"]["jsonResponse"]["JOB"]["annotations"][0]
    assert annotation["children"]["NESTED_JOB"]["annotations"][0]["point"] == {
        "x": WIDTH * 0.4,
        "y": HEIGHT * 0.8,
    }
