from copy import deepcopy

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


def test_semantic_bounding_poly_keeps_its_polygon_groups():
    """Geospatial semantic holds every part of one object, so its boundingPoly is nested."""
    asset = _asset_with_label(
        {
            "JOB": {
                "annotations": [
                    {
                        "type": "semantic",
                        "boundingPoly": [
                            [
                                {"normalizedVertices": [{"x": 0.1, "y": 0.2}]},
                                {"normalizedVertices": [{"x": 0.3, "y": 0.4}]},
                            ],
                            [{"normalizedVertices": [{"x": 0.5, "y": 0.6}]}],
                        ],
                    }
                ]
            }
        }
    )

    convert_to_pixel_coords(asset)

    bounding_poly = asset["latestLabel"]["jsonResponse"]["JOB"]["annotations"][0]["boundingPoly"]
    assert len(bounding_poly) == 2
    assert len(bounding_poly[0]) == 2
    # The exterior ring and its hole keep their grouping, and both carry pixel coordinates.
    assert bounding_poly[0][0]["normalizedVertices"] == [{"x": 0.1, "y": 0.2}]
    assert bounding_poly[0][0]["vertices"] == [{"x": WIDTH * 0.1, "y": HEIGHT * 0.2}]
    assert bounding_poly[0][1]["vertices"] == [{"x": WIDTH * 0.3, "y": HEIGHT * 0.4}]
    assert bounding_poly[1][0]["vertices"] == [{"x": WIDTH * 0.5, "y": HEIGHT * 0.6}]


def test_conversion_is_idempotent():
    """Labels are collected from three overlapping lists, so a label can be reached twice."""
    label = {
        "jsonResponse": {
            "JOB": {
                "annotations": [
                    {"boundingPoly": [{"normalizedVertices": [{"x": 0.1, "y": 0.2}]}]},
                    {"boundingPoly": [[{"normalizedVertices": [{"x": 0.3, "y": 0.4}]}]]},
                    {"point": {"x": 0.5, "y": 0.6}},
                    {"polyline": [{"x": 0.7, "y": 0.8}]},
                ]
            }
        }
    }
    asset = {
        "geospatialExportMetadata": [{"labelingCRS": "PIXEL", "width": WIDTH, "height": HEIGHT}],
        "latestLabel": label,
        "labels": [label],
        "latestLabels": [label],
    }

    convert_to_pixel_coords(asset)
    once = deepcopy(asset["latestLabel"]["jsonResponse"])
    convert_to_pixel_coords(asset)

    assert asset["latestLabel"]["jsonResponse"] == once
