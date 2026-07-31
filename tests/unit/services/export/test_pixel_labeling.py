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
