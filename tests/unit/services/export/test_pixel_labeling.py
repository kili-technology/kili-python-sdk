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


def test_get_asset_pixel_dimensions_ignores_the_other_layers():
    """A reference layer of another size must never unnormalize the annotations."""
    asset = {
        "geospatialExportMetadata": [
            {"width": WIDTH, "height": HEIGHT},
            {"width": 640, "height": 480},
        ]
    }
    assert get_asset_pixel_dimensions(asset) == (WIDTH, HEIGHT)


def test_get_asset_pixel_dimensions_without_a_dimensioned_first_layer():
    """Sliding to the next layer would silently use the wrong grid."""
    asset = {"geospatialExportMetadata": [{"labelingCRS": "PIXEL"}, {"width": 640, "height": 480}]}
    assert get_asset_pixel_dimensions(asset) is None


def test_bounding_poly_carries_both_normalized_and_pixel_vertices():
    """As for an image asset: `vertices` is added, `normalizedVertices` stays normalized."""
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

    bounding_poly = asset["latestLabel"]["jsonResponse"]["JOB"]["annotations"][0]["boundingPoly"][0]
    assert bounding_poly["normalizedVertices"] == [{"x": 0.5, "y": 0.25}]
    assert bounding_poly["vertices"] == [{"x": WIDTH * 0.5, "y": HEIGHT * 0.25}]


def test_point_and_polyline_carry_both():
    asset = _asset_with_label(
        {
            "JOB": {
                "annotations": [
                    {"point": {"x": 0.1, "y": 0.2}},
                    {"polyline": [{"x": 0.25, "y": 0.5}]},
                ]
            }
        }
    )

    convert_to_pixel_coords(asset)

    annotations = asset["latestLabel"]["jsonResponse"]["JOB"]["annotations"]
    assert annotations[0]["point"] == {"x": 0.1, "y": 0.2}
    assert annotations[0]["pointPixels"] == {"x": WIDTH * 0.1, "y": HEIGHT * 0.2}
    assert annotations[1]["polylinePixels"] == [{"x": WIDTH * 0.25, "y": HEIGHT * 0.5}]


def test_no_pixel_coordinates_are_added_without_dimensions():
    """An asset imported before the dimensions were recorded keeps only its fractions."""
    asset = {
        "latestLabel": {"jsonResponse": {"JOB": {"annotations": [{"point": {"x": 0.1, "y": 0.2}}]}}}
    }

    convert_to_pixel_coords(asset)

    annotation = asset["latestLabel"]["jsonResponse"]["JOB"]["annotations"][0]
    assert annotation["point"] == {"x": 0.1, "y": 0.2}
    assert "pointPixels" not in annotation
