import json
import os
import shutil
import tempfile

from kili_formats.format.geojson import geojson_feature_collection_to_kili_json_response


def create_mock_geojson_file(feature_collection, temp_dir):
    """Create a mock GeoJSON file for testing purposes."""
    file_path = os.path.join(temp_dir, "test.geojson")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(feature_collection, f)
    return file_path


def is_almost_equal(a, b, tolerance=1e-14):
    """Due to different versions of coordinate transformations, the coordinates may differ slightly.

    This function checks if two coordinates are almost equal within a given tolerance.
    """
    return abs(a - b) <= tolerance


def test_point_geojson():
    """Test converting GeoJSON Point features to Kili annotations."""
    temp_dir = tempfile.mkdtemp()

    # Create mock GeoJSON feature collection with Point geometries
    feature_collection = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [9.429123117729949, 54.68002984132896],
                },
                "properties": {
                    "kili": {
                        "job": "points_job",
                        "type": "marker",
                        "categories": [{"name": "point_category"}],
                    }
                },
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [9.772235200599381, 54.68970515271516],
                },
                "properties": {
                    "kili": {
                        "job": "points_job",
                        "type": "marker",
                        "categories": [{"name": "point_category"}],
                    }
                },
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [9.451439350762108, 54.318792605636354],
                },
                "properties": {
                    "kili": {
                        "job": "points_job",
                        "type": "marker",
                        "categories": [{"name": "point_category"}],
                    }
                },
            },
        ],
    }

    geojson_file_path = create_mock_geojson_file(feature_collection, temp_dir)

    response = geojson_feature_collection_to_kili_json_response(feature_collection)

    assert "points_job" in response
    assert "annotations" in response["points_job"]

    annotations = response["points_job"]["annotations"]
    assert len(annotations) == 3

    expected_coordinates = [
        {"x": 9.429123117729949, "y": 54.68002984132896},
        {"x": 9.772235200599381, "y": 54.68970515271516},
        {"x": 9.451439350762108, "y": 54.318792605636354},
    ]

    for index, annotation in enumerate(annotations):
        assert annotation["type"] == "marker"
        assert "point" in annotation

        assert is_almost_equal(annotation["point"]["x"], expected_coordinates[index]["x"])
        assert is_almost_equal(annotation["point"]["y"], expected_coordinates[index]["y"])

        assert "categories" in annotation
        assert len(annotation["categories"]) == 1
        assert annotation["categories"][0]["name"] == "point_category"

    shutil.rmtree(temp_dir)


def test_linestring_geojson():
    """Test converting GeoJSON LineString features to Kili annotations."""
    temp_dir = tempfile.mkdtemp()

    # Create mock GeoJSON feature collection with LineString geometries
    feature_collection = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [9.254598688594093, 54.8539201125262],
                        [9.254598688594093, 54.85101839240259],
                        [9.259639164462506, 54.84811646354571],
                        [9.262159402396708, 54.845214325948014],
                    ],
                },
                "properties": {
                    "kili": {
                        "job": "lines_job",
                        "type": "polyline",
                        "categories": [{"name": "line_category"}],
                    }
                },
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [9.69312008914582, 54.23407519827612],
                        [9.69312008914582, 54.23996684410168],
                        [9.698160565014232, 54.244385026482774],
                    ],
                },
                "properties": {
                    "kili": {
                        "job": "lines_job",
                        "type": "polyline",
                        "categories": [{"name": "line_category"}],
                    }
                },
            },
        ],
    }

    geojson_file_path = create_mock_geojson_file(feature_collection, temp_dir)

    response = geojson_feature_collection_to_kili_json_response(feature_collection)

    assert "lines_job" in response
    assert "annotations" in response["lines_job"]

    annotations = response["lines_job"]["annotations"]
    assert len(annotations) == 2

    expected_coordinates = [
        [
            {"x": 9.254598688594093, "y": 54.8539201125262},
            {"x": 9.254598688594093, "y": 54.85101839240259},
            {"x": 9.259639164462506, "y": 54.84811646354571},
            {"x": 9.262159402396708, "y": 54.845214325948014},
        ],
        [
            {"x": 9.69312008914582, "y": 54.23407519827612},
            {"x": 9.69312008914582, "y": 54.23996684410168},
            {"x": 9.698160565014232, "y": 54.244385026482774},
        ],
    ]

    for index, annotation in enumerate(annotations):
        assert annotation["type"] == "polyline"
        assert "polyline" in annotation

        for point_index, point in enumerate(annotation["polyline"]):
            assert is_almost_equal(point["x"], expected_coordinates[index][point_index]["x"])
            assert is_almost_equal(point["y"], expected_coordinates[index][point_index]["y"])

        assert "categories" in annotation
        assert len(annotation["categories"]) == 1
        assert annotation["categories"][0]["name"] == "line_category"

    shutil.rmtree(temp_dir)


def test_polygon_geojson():
    """Test converting GeoJSON Polygon features to Kili annotations."""
    temp_dir = tempfile.mkdtemp()

    # Create mock GeoJSON feature collection with Polygon geometries
    feature_collection = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [9.504102244080421, 54.51885219373373],
                            [9.50914271994883, 54.52031500197589],
                            [9.514183195817239, 54.52324046127452],
                            [9.519223671685653, 54.52470311233283],
                            [9.504102244080421, 54.51885219373373],  # Close the polygon
                        ]
                    ],
                },
                "properties": {
                    "kili": {
                        "job": "polygons_job",
                        "type": "semantic",
                        "categories": [{"name": "polygon_category"}],
                    }
                },
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [10.05351411373718, 54.316481719000855],
                            [10.063595065473999, 54.316481719000855],
                            [10.068635541342411, 54.316481719000855],
                            [10.076196255145028, 54.31501161884114],
                            [10.05351411373718, 54.316481719000855],  # Close the polygon
                        ]
                    ],
                },
                "properties": {
                    "kili": {
                        "job": "polygons_job",
                        "type": "semantic",
                        "categories": [{"name": "polygon_category"}],
                    }
                },
            },
        ],
    }

    geojson_file_path = create_mock_geojson_file(feature_collection, temp_dir)

    response = geojson_feature_collection_to_kili_json_response(feature_collection)

    assert "polygons_job" in response
    assert "annotations" in response["polygons_job"]

    annotations = response["polygons_job"]["annotations"]
    assert len(annotations) == 2

    # Test the first polygon
    first_annotation = annotations[0]
    assert first_annotation["type"] == "semantic"
    assert "boundingPoly" in first_annotation
    assert len(first_annotation["boundingPoly"]) == 1  # Only exterior ring

    expected_first_polygon = [
        {"x": 9.504102244080421, "y": 54.51885219373373},
        {"x": 9.50914271994883, "y": 54.52031500197589},
        {"x": 9.514183195817239, "y": 54.52324046127452},
        {"x": 9.519223671685653, "y": 54.52470311233283},
    ]

    first_polygon_vertices = first_annotation["boundingPoly"][0]["normalizedVertices"]
    assert len(first_polygon_vertices) == len(expected_first_polygon)

    for i, point in enumerate(first_polygon_vertices):
        assert is_almost_equal(point["x"], expected_first_polygon[i]["x"])
        assert is_almost_equal(point["y"], expected_first_polygon[i]["y"])

    assert "categories" in first_annotation
    assert len(first_annotation["categories"]) == 1
    assert first_annotation["categories"][0]["name"] == "polygon_category"

    shutil.rmtree(temp_dir)


def test_multipolygon_geojson():
    """Test converting GeoJSON MultiPolygon features to Kili annotations."""
    temp_dir = tempfile.mkdtemp()

    # Create mock GeoJSON feature collection with MultiPolygon geometry
    feature_collection = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "MultiPolygon",
                    "coordinates": [
                        # First polygon
                        [
                            [
                                [9.504102244080421, 54.51885219373373],
                                [9.50914271994883, 54.52031500197589],
                                [9.514183195817239, 54.52324046127452],
                                [9.504102244080421, 54.51885219373373],
                            ]
                        ],
                        # Second polygon
                        [
                            [
                                [10.05351411373718, 54.316481719000855],
                                [10.063595065473999, 54.316481719000855],
                                [10.068635541342411, 54.316481719000855],
                                [10.05351411373718, 54.316481719000855],
                            ]
                        ],
                    ],
                },
                "properties": {
                    "kili": {
                        "job": "multipolygons_job",
                        "type": "semantic",
                        "categories": [{"name": "multipolygon_category"}],
                    }
                },
            }
        ],
    }

    geojson_file_path = create_mock_geojson_file(feature_collection, temp_dir)

    response = geojson_feature_collection_to_kili_json_response(feature_collection)

    assert "multipolygons_job" in response
    assert "annotations" in response["multipolygons_job"]

    annotations = response["multipolygons_job"]["annotations"]
    # MultiPolygon should create multiple annotations with the same mid
    assert len(annotations) == 2

    # Check that both annotations have the same mid (indicating they're parts of the same multipolygon)
    mids = [ann.get("mid") for ann in annotations]
    assert len(set(mids)) == 1  # All should have the same mid

    for annotation in annotations:
        assert annotation["type"] == "semantic"
        assert "boundingPoly" in annotation
        assert "categories" in annotation
        assert len(annotation["categories"]) == 1
        assert annotation["categories"][0]["name"] == "multipolygon_category"

    shutil.rmtree(temp_dir)


def test_mixed_geometries_geojson():
    """Test converting GeoJSON with mixed geometry types to Kili annotations."""
    temp_dir = tempfile.mkdtemp()

    # Create mock GeoJSON feature collection with mixed geometries
    feature_collection = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [9.429123117729949, 54.68002984132896],
                },
                "properties": {
                    "kili": {
                        "job": "detection_job",
                        "type": "marker",
                        "categories": [{"name": "point_category"}],
                    }
                },
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [9.254598688594093, 54.8539201125262],
                        [9.254598688594093, 54.85101839240259],
                        [9.259639164462506, 54.84811646354571],
                    ],
                },
                "properties": {
                    "kili": {
                        "job": "tracking_job",
                        "type": "polyline",
                        "categories": [{"name": "line_category"}],
                    }
                },
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [9.504102244080421, 54.51885219373373],
                            [9.50914271994883, 54.52031500197589],
                            [9.514183195817239, 54.52324046127452],
                            [9.504102244080421, 54.51885219373373],
                        ]
                    ],
                },
                "properties": {
                    "kili": {
                        "job": "segmentation_job",
                        "type": "semantic",
                        "categories": [{"name": "polygon_category"}],
                    }
                },
            },
        ],
    }

    geojson_file_path = create_mock_geojson_file(feature_collection, temp_dir)

    response = geojson_feature_collection_to_kili_json_response(feature_collection)

    # Should have three different jobs
    assert len(response) == 3
    assert "detection_job" in response
    assert "tracking_job" in response
    assert "segmentation_job" in response

    # Check point annotation
    assert "annotations" in response["detection_job"]
    point_annotations = response["detection_job"]["annotations"]
    assert len(point_annotations) == 1
    assert point_annotations[0]["type"] == "marker"
    assert "point" in point_annotations[0]

    # Check line annotation
    assert "annotations" in response["tracking_job"]
    line_annotations = response["tracking_job"]["annotations"]
    assert len(line_annotations) == 1
    assert line_annotations[0]["type"] == "polyline"
    assert "polyline" in line_annotations[0]

    # Check polygon annotation
    assert "annotations" in response["segmentation_job"]
    polygon_annotations = response["segmentation_job"]["annotations"]
    assert len(polygon_annotations) == 1
    assert polygon_annotations[0]["type"] == "semantic"
    assert "boundingPoly" in polygon_annotations[0]

    shutil.rmtree(temp_dir)


def test_multiple_geojson_files():
    """Test merging annotations from multiple GeoJSON files."""
    temp_dir = tempfile.mkdtemp()

    # Create first GeoJSON file with points
    feature_collection_1 = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [9.429123117729949, 54.68002984132896],
                },
                "properties": {
                    "kili": {
                        "job": "detection_job",
                        "type": "marker",
                        "categories": [{"name": "point_category"}],
                    }
                },
            }
        ],
    }

    # Create second GeoJSON file with more points for the same job
    feature_collection_2 = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [9.772235200599381, 54.68970515271516],
                },
                "properties": {
                    "kili": {
                        "job": "detection_job",
                        "type": "marker",
                        "categories": [{"name": "point_category"}],
                    }
                },
            }
        ],
    }

    file_path_1 = create_mock_geojson_file(feature_collection_1, temp_dir)
    file_path_2 = create_mock_geojson_file(feature_collection_2, temp_dir)

    # Test merging logic by manually processing both files
    merged_json_response = {}

    for feature_collection in [feature_collection_1, feature_collection_2]:
        json_response = geojson_feature_collection_to_kili_json_response(feature_collection)

        for job_name, job_data in json_response.items():
            if job_name not in merged_json_response:
                merged_json_response[job_name] = job_data
            else:
                # Merge job data
                for key, value in job_data.items():
                    if key == "annotations":
                        merged_json_response[job_name].setdefault("annotations", []).extend(value)
                    else:
                        merged_json_response[job_name][key] = value

    # Should have merged the annotations from both files
    assert "detection_job" in merged_json_response
    assert "annotations" in merged_json_response["detection_job"]
    annotations = merged_json_response["detection_job"]["annotations"]
    assert len(annotations) == 2  # One from each file

    shutil.rmtree(temp_dir)


def test_non_localised_features_geojson():
    """Test converting non-localised GeoJSON features (transcription and classification)."""
    temp_dir = tempfile.mkdtemp()

    # Create mock GeoJSON feature collection with non-localised features
    feature_collection = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": None,  # Non-localised features have no geometry
                "properties": {
                    "kili": {"job": "transcription_job", "text": "This is a transcription"}
                },
            },
            {
                "type": "Feature",
                "geometry": None,
                "properties": {
                    "kili": {
                        "job": "classification_job",
                        "categories": [{"name": "category_a"}, {"name": "category_b"}],
                    }
                },
            },
        ],
    }

    geojson_file_path = create_mock_geojson_file(feature_collection, temp_dir)

    response = geojson_feature_collection_to_kili_json_response(feature_collection)

    # Should have two jobs
    assert len(response) == 2
    assert "transcription_job" in response
    assert "classification_job" in response

    # Check transcription job
    assert "text" in response["transcription_job"]
    assert response["transcription_job"]["text"] == "This is a transcription"

    # Check classification job
    assert "categories" in response["classification_job"]
    categories = response["classification_job"]["categories"]
    assert len(categories) == 2
    assert categories[0]["name"] == "category_a"
    assert categories[1]["name"] == "category_b"

    shutil.rmtree(temp_dir)
