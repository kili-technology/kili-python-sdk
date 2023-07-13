from kili.utils.labels.geojson import (
    features_list_to_feature_collection,
    kili_bbox_annotation_to_geojson_feature_polygon,
    kili_bbox_to_geojson_polygon,
    kili_line_annotation_to_geojson_feature_linestring,
    kili_line_to_geojson_linestring,
    kili_point_annotation_to_geojson_feature_point,
    kili_point_to_geojson_point,
    kili_polygon_annotation_to_geojson_feature_polygon,
    kili_polygon_to_geojson_polygon,
    kili_segmentation_annotation_to_geojson_feature_polygon,
    kili_segmentation_to_geojson_polygon,
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
    output = kili_point_annotation_to_geojson_feature_point(
        kili_point_annotation, job_name="POINT_JOB"
    )
    assert output == {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [long, lat]},
        "id": "20230712140607850-1660",
        "properties": {
            "categories": [{"name": "A"}],
            "type": "marker",
            "children": {},
            "job": "POINT_JOB",
        },
    }


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

    output = kili_bbox_annotation_to_geojson_feature_polygon(kili_bbox_ann, job_name="BBOX_JOB")

    assert output == {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [bbox],
        },
        "id": "20230712152136805-42164",
        "properties": {
            "categories": [{"name": "CATEGORY_A"}],
            "type": "rectangle",
            "children": {},
            "job": "BBOX_JOB",
        },
    }


def test_kili_polygon_to_geojson_polygon():
    normalized_vertices = [
        {"x": 4.4310542897769665, "y": 52.19847958268726},
        {"x": 4.424421731366076, "y": 52.202545578240006},
        {"x": 4.416462661273006, "y": 52.20569646893471},
        {"x": 4.407840335338849, "y": 52.20864387409585},
        {"x": 4.40352917237179, "y": 52.21108295809601},
        {"x": 4.399052195444408, "y": 52.2142332434119},
        {"x": 4.393911962675979, "y": 52.213217046751694},
        {"x": 4.395404288318439, "y": 52.21037157242832},
        {"x": 4.406513823656671, "y": 52.20610301920179},
        {"x": 4.414970335630547, "y": 52.20376530436754},
        {"x": 4.421602894041437, "y": 52.201020873500795},
        {"x": 4.423095219683898, "y": 52.19898785247491},
        {"x": 4.427572196611239, "y": 52.19695473844905},
    ]

    output = kili_polygon_to_geojson_polygon(normalized_vertices)

    assert output == {
        "coordinates": [
            [
                [4.4310542897769665, 52.19847958268726],
                [4.424421731366076, 52.202545578240006],
                [4.416462661273006, 52.20569646893471],
                [4.407840335338849, 52.20864387409585],
                [4.40352917237179, 52.21108295809601],
                [4.399052195444408, 52.2142332434119],
                [4.393911962675979, 52.213217046751694],
                [4.395404288318439, 52.21037157242832],
                [4.406513823656671, 52.20610301920179],
                [4.414970335630547, 52.20376530436754],
                [4.421602894041437, 52.201020873500795],
                [4.423095219683898, 52.19898785247491],
                [4.427572196611239, 52.19695473844905],
                [4.4310542897769665, 52.19847958268726],
            ]
        ],
        "type": "Polygon",
    }


def test_kili_polygon_annotation_to_geojson_polygon():
    polygon_ann = {
        "children": {},
        "boundingPoly": [
            {
                "normalizedVertices": [
                    {"x": 4.4310542897769665, "y": 52.19847958268726},
                    {"x": 4.424421731366076, "y": 52.202545578240006},
                    {"x": 4.416462661273006, "y": 52.20569646893471},
                    {"x": 4.407840335338849, "y": 52.20864387409585},
                    {"x": 4.40352917237179, "y": 52.21108295809601},
                    {"x": 4.399052195444408, "y": 52.2142332434119},
                    {"x": 4.393911962675979, "y": 52.213217046751694},
                    {"x": 4.395404288318439, "y": 52.21037157242832},
                    {"x": 4.406513823656671, "y": 52.20610301920179},
                    {"x": 4.414970335630547, "y": 52.20376530436754},
                    {"x": 4.421602894041437, "y": 52.201020873500795},
                    {"x": 4.423095219683898, "y": 52.19898785247491},
                    {"x": 4.427572196611239, "y": 52.19695473844905},
                ]
            }
        ],
        "categories": [{"name": "A"}],
        "mid": "20230712154012841-65343",
        "type": "polygon",
    }

    output = kili_polygon_annotation_to_geojson_feature_polygon(polygon_ann, job_name="POLYGON_JOB")

    assert output == {
        "geometry": {
            "coordinates": [
                [
                    [4.4310542897769665, 52.19847958268726],
                    [4.424421731366076, 52.202545578240006],
                    [4.416462661273006, 52.20569646893471],
                    [4.407840335338849, 52.20864387409585],
                    [4.40352917237179, 52.21108295809601],
                    [4.399052195444408, 52.2142332434119],
                    [4.393911962675979, 52.213217046751694],
                    [4.395404288318439, 52.21037157242832],
                    [4.406513823656671, 52.20610301920179],
                    [4.414970335630547, 52.20376530436754],
                    [4.421602894041437, 52.201020873500795],
                    [4.423095219683898, 52.19898785247491],
                    [4.427572196611239, 52.19695473844905],
                    [4.4310542897769665, 52.19847958268726],
                ]
            ],
            "type": "Polygon",
        },
        "properties": {
            "categories": [{"name": "A"}],
            "type": "polygon",
            "children": {},
            "job": "POLYGON_JOB",
        },
        "type": "Feature",
        "id": "20230712154012841-65343",
    }


def test_kili_line_to_geojson_linestring():
    polyline = [
        {"x": 4.46935731459989, "y": 52.19176987673034},
        {"x": 4.457252895500004, "y": 52.194109686268},
        {"x": 4.442495453035762, "y": 52.195939610198685},
        {"x": 4.43138591769753, "y": 52.19634624973076},
        {"x": 4.423592661564704, "y": 52.201225633952504},
        {"x": 4.4123173122661905, "y": 52.20518973920337},
        {"x": 4.4017052188087655, "y": 52.20864533731555},
        {"x": 4.396564986040335, "y": 52.211795795488335},
    ]

    output = kili_line_to_geojson_linestring(polyline)

    assert output == {
        "type": "LineString",
        "coordinates": [
            [4.46935731459989, 52.19176987673034],
            [4.457252895500004, 52.194109686268],
            [4.442495453035762, 52.195939610198685],
            [4.43138591769753, 52.19634624973076],
            [4.423592661564704, 52.201225633952504],
            [4.4123173122661905, 52.20518973920337],
            [4.4017052188087655, 52.20864533731555],
            [4.396564986040335, 52.211795795488335],
        ],
    }


def test_kili_line_annotation_to_geojson_linestring():
    ann = {
        "children": {},
        "polyline": [
            {"x": 4.46935731459989, "y": 52.19176987673034},
            {"x": 4.457252895500004, "y": 52.194109686268},
            {"x": 4.442495453035762, "y": 52.195939610198685},
            {"x": 4.43138591769753, "y": 52.19634624973076},
            {"x": 4.423592661564704, "y": 52.201225633952504},
            {"x": 4.4123173122661905, "y": 52.20518973920337},
            {"x": 4.4017052188087655, "y": 52.20864533731555},
            {"x": 4.396564986040335, "y": 52.211795795488335},
        ],
        "categories": [{"name": "A"}],
        "mid": "20230712161027535-42230",
        "type": "polyline",
    }

    output = kili_line_annotation_to_geojson_feature_linestring(ann, job_name="LINE_JOB")

    assert output == {
        "type": "Feature",
        "id": "20230712161027535-42230",
        "properties": {
            "categories": [{"name": "A"}],
            "type": "polyline",
            "children": {},
            "job": "LINE_JOB",
        },
        "geometry": {
            "coordinates": [
                [4.46935731459989, 52.19176987673034],
                [4.457252895500004, 52.194109686268],
                [4.442495453035762, 52.195939610198685],
                [4.43138591769753, 52.19634624973076],
                [4.423592661564704, 52.201225633952504],
                [4.4123173122661905, 52.20518973920337],
                [4.4017052188087655, 52.20864533731555],
                [4.396564986040335, 52.211795795488335],
            ],
            "type": "LineString",
        },
    }


def test_kili_segmentation_to_geojson_polygon():
    bounding_poly = [
        {
            "normalizedVertices": [
                {"x": 4.439649, "y": 52.201064},
                {"x": 4.439694, "y": 52.200955},
                {"x": 4.439827, "y": 52.200846},
            ]
        },
        {
            "normalizedVertices": [
                {"x": 4.441604, "y": 52.200982},
                {"x": 4.441604, "y": 52.201254},
                {"x": 4.441648, "y": 52.2009},
            ]
        },
        {
            "normalizedVertices": [
                {"x": 4.446402, "y": 52.200192},
                {"x": 4.446402, "y": 52.200274},
                {"x": 4.446491, "y": 52.200083},
            ]
        },
    ]

    output = kili_segmentation_to_geojson_polygon(bounding_poly)

    assert output == {
        "type": "Polygon",
        "coordinates": [
            [
                [4.439649, 52.201064],
                [4.439694, 52.200955],
                [4.439827, 52.200846],
                [4.439649, 52.201064],
            ],
            [
                [4.441604, 52.200982],
                [4.441604, 52.201254],
                [4.441648, 52.2009],
                [4.441604, 52.200982],
            ],
            [
                [4.446402, 52.200192],
                [4.446402, 52.200274],
                [4.446491, 52.200083],
                [4.446402, 52.200192],
            ],
        ],
    }


def test_kili_segmentation_annotation_to_geojson_polygon():
    ann = {
        "children": {},
        "boundingPoly": [
            {
                "normalizedVertices": [
                    {"x": 4.439649, "y": 52.201064},
                    {"x": 4.439694, "y": 52.200955},
                    {"x": 4.439694, "y": 52.201853},
                    {"x": 4.439649, "y": 52.201853},
                ]
            },
            {
                "normalizedVertices": [
                    {"x": 4.441604, "y": 52.200982},
                    {"x": 4.441782, "y": 52.200655},
                    {"x": 4.441737, "y": 52.200764},
                    {"x": 4.441648, "y": 52.2009},
                ]
            },
            {
                "normalizedVertices": [
                    {"x": 4.446402, "y": 52.200192},
                    {"x": 4.446402, "y": 52.200274},
                    {"x": 4.44658, "y": 52.199838},
                    {"x": 4.44658, "y": 52.199947},
                    {"x": 4.446491, "y": 52.200083},
                ]
            },
        ],
        "categories": [{"name": "A"}],
        "mid": "20230712163555037-91494",
        "type": "semantic",
    }

    output = kili_segmentation_annotation_to_geojson_feature_polygon(
        ann, job_name="SEGMENTATION_JOB"
    )

    assert output == {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [4.439649, 52.201064],
                    [4.439694, 52.200955],
                    [4.439694, 52.201853],
                    [4.439649, 52.201853],
                    [4.439649, 52.201064],
                ],
                [
                    [4.441604, 52.200982],
                    [4.441782, 52.200655],
                    [4.441737, 52.200764],
                    [4.441648, 52.2009],
                    [4.441604, 52.200982],
                ],
                [
                    [4.446402, 52.200192],
                    [4.446402, 52.200274],
                    [4.44658, 52.199838],
                    [4.44658, 52.199947],
                    [4.446491, 52.200083],
                    [4.446402, 52.200192],
                ],
            ],
        },
        "id": "20230712163555037-91494",
        "properties": {
            "categories": [{"name": "A"}],
            "type": "semantic",
            "children": {},
            "job": "SEGMENTATION_JOB",
        },
    }


def test_features_list_to_feature_collection():
    feat1 = {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [102.0, 0.5]},
        "properties": {"prop0": "value0"},
    }
    feat2 = {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": [[102.0, 0.0], [103.0, 1.0], [104.0, 0.0], [105.0, 1.0]],
        },
        "properties": {"prop0": "value0", "prop1": 0.0},
    }
    features = [feat1, feat2]

    output = features_list_to_feature_collection(features)

    assert output == {
        "type": "FeatureCollection",
        "features": features,
    }
