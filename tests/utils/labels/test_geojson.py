from kili.utils.labels.geojson import (
    kili_bbox_annotation_to_geojson_polygon,
    kili_bbox_to_geojson_polygon,
    kili_point_annotation_to_geojson_feature_point,
    kili_point_to_geojson_point,
)


def test_kili_point_to_geojson_point():
    lat = 1.0
    long = 2.0
    kili_point = {"x": long, "y": lat}
    expected = {"type": "Point", "coordinates": [long, lat]}
    assert kili_point_to_geojson_point(kili_point) == expected


def test_kili_point_to_geojson_feature_point():
    lat = 1.0
    long = 2.0
    kili_point_annotation = {
        "children": {},
        "point": {"x": long, "y": lat},
        "categories": [{"name": "A"}],
        "mid": "20230712140607850-1660",
        "type": "marker",
    }
    expected = {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [long, lat]},
        "id": "20230712140607850-1660",
        "properties": {"categories": [{"name": "A"}]},
    }
    assert kili_point_annotation_to_geojson_feature_point(kili_point_annotation) == expected


def test_kili_bbox_to_geojson_polygon():
    normalized_vertices = [
        {"x": 4.426411498889343, "y": 52.195226518404574},
        {"x": 4.426411498889343, "y": 52.19969942041263},
        {"x": 4.433707313141323, "y": 52.19969942041263},
        {"x": 4.433707313141323, "y": 52.195226518404574},
    ]
    bbox = [
        [4.426411498889343, 52.195226518404574],
        [4.433707313141323, 52.195226518404574],
        [4.433707313141323, 52.19969942041263],
        [4.426411498889343, 52.19969942041263],
        [4.426411498889343, 52.195226518404574],
    ]
    expected = {
        "type": "Polygon",
        "coordinates": [bbox],
    }

    assert kili_bbox_to_geojson_polygon(normalized_vertices) == expected


def test_kili_bbox_annotation_to_geojson_polygon():
    kili_bbox_ann = {
        "children": {},
        "boundingPoly": [
            {
                "normalizedVertices": [
                    {"x": 4.426411498889343, "y": 52.195226518404574},
                    {"x": 4.426411498889343, "y": 52.19969942041263},
                    {"x": 4.433707313141323, "y": 52.19969942041263},
                    {"x": 4.433707313141323, "y": 52.195226518404574},
                ]
            }
        ],
        "categories": [{"name": "CATEGORY_A"}],
        "mid": "20230712152136805-42164",
        "type": "rectangle",
    }
    bbox = [
        [4.426411498889343, 52.195226518404574],
        [4.433707313141323, 52.195226518404574],
        [4.433707313141323, 52.19969942041263],
        [4.426411498889343, 52.19969942041263],
        [4.426411498889343, 52.195226518404574],
    ]
    expected = {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [bbox],
        },
        "id": "20230712152136805-42164",
        "properties": {"categories": [{"name": "CATEGORY_A"}]},
    }

    output = kili_bbox_annotation_to_geojson_polygon(kili_bbox_ann)
    assert output == expected
