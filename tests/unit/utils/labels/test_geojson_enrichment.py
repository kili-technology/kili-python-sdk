import pytest

from kili.utils.labels.geojson import (
    enrich_geojson_with_kili_properties,
    enrich_geojson_with_specific_mapping,
)


@pytest.fixture()
def mock_json_interface():
    """Mock JSON interface with various job types for testing."""
    return {
        "jobs": {
            "MARKER_JOB": {
                "mlTask": "OBJECT_DETECTION",
                "tools": ["marker"],
                "content": {
                    "categories": {"POINT_CATEGORY": {"name": "Point Category", "color": "#ff0000"}}
                },
            },
            "POLYLINE_JOB": {
                "mlTask": "OBJECT_DETECTION",
                "tools": ["polyline"],
                "content": {
                    "categories": {"LINE_CATEGORY": {"name": "Line Category", "color": "#00ff00"}}
                },
            },
            "POLYGON_JOB": {
                "mlTask": "OBJECT_DETECTION",
                "tools": ["polygon"],
                "content": {
                    "categories": {
                        "POLYGON_CATEGORY": {"name": "Polygon Category", "color": "#0000ff"}
                    }
                },
            },
            "SEMANTIC_JOB": {
                "mlTask": "OBJECT_DETECTION",
                "tools": ["semantic"],
                "content": {
                    "categories": {
                        "SEMANTIC_CATEGORY": {"name": "Semantic Category", "color": "#ffff00"}
                    }
                },
            },
            "MULTI_TOOL_JOB": {
                "mlTask": "OBJECT_DETECTION",
                "tools": ["marker", "polyline", "polygon", "semantic"],
                "content": {
                    "categories": {"MULTI_CATEGORY": {"name": "Multi Category", "color": "#ff00ff"}}
                },
            },
            "CLASSIFICATION_JOB": {
                "mlTask": "CLASSIFICATION",
                "tools": [],
                "content": {
                    "categories": {
                        "CLASS_CATEGORY": {"name": "Classification Category", "color": "#00ffff"}
                    }
                },
            },
        }
    }


class TestEnrichGeojsonWithKiliProperties:
    """Test cases for enrich_geojson_with_kili_properties function."""

    def test_features_with_existing_kili_properties_remain_unchanged(self, mock_json_interface):
        """Test that features with existing kili properties are not modified."""
        feature_collection = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "properties": {
                        "kili": {
                            "job": "CUSTOM_JOB",
                            "type": "marker",
                            "categories": [{"name": "CUSTOM_CATEGORY"}],
                        }
                    },
                }
            ],
        }

        result = enrich_geojson_with_kili_properties(feature_collection, mock_json_interface)

        assert len(result["features"]) == 1
        assert result["features"][0]["properties"]["kili"]["job"] == "CUSTOM_JOB"
        assert (
            result["features"][0]["properties"]["kili"]["categories"][0]["name"]
            == "CUSTOM_CATEGORY"
        )

    def test_point_geometry_gets_marker_annotation(self, mock_json_interface):
        """Test that Point geometries get mapped to marker annotations."""
        feature_collection = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "properties": {},
                }
            ],
        }

        result = enrich_geojson_with_kili_properties(feature_collection, mock_json_interface)

        assert len(result["features"]) == 1
        kili_props = result["features"][0]["properties"]["kili"]
        assert kili_props["job"] == "MARKER_JOB"
        assert kili_props["type"] == "marker"
        assert kili_props["categories"][0]["name"] == "POINT_CATEGORY"

    def test_linestring_geometry_gets_polyline_annotation(self, mock_json_interface):
        """Test that LineString geometries get mapped to polyline annotations."""
        feature_collection = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "LineString", "coordinates": [[0, 0], [1, 1]]},
                    "properties": {},
                }
            ],
        }

        result = enrich_geojson_with_kili_properties(feature_collection, mock_json_interface)

        assert len(result["features"]) == 1
        kili_props = result["features"][0]["properties"]["kili"]
        assert kili_props["job"] == "POLYLINE_JOB"
        assert kili_props["type"] == "polyline"
        assert kili_props["categories"][0]["name"] == "LINE_CATEGORY"

    def test_polygon_geometry_prefers_polygon_over_semantic(self, mock_json_interface):
        """Test that Polygon geometries prefer polygon jobs over semantic jobs."""
        feature_collection = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
                    },
                    "properties": {},
                }
            ],
        }

        result = enrich_geojson_with_kili_properties(feature_collection, mock_json_interface)

        assert len(result["features"]) == 1
        kili_props = result["features"][0]["properties"]["kili"]
        assert kili_props["job"] == "POLYGON_JOB"
        assert kili_props["type"] == "polygon"
        assert kili_props["categories"][0]["name"] == "POLYGON_CATEGORY"

    def test_multipolygon_geometry_gets_semantic_annotation(self, mock_json_interface):
        """Test that MultiPolygon geometries get mapped to semantic annotations."""
        feature_collection = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "MultiPolygon",
                        "coordinates": [
                            [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
                            [[[2, 2], [3, 2], [3, 3], [2, 3], [2, 2]]],
                        ],
                    },
                    "properties": {},
                }
            ],
        }

        result = enrich_geojson_with_kili_properties(feature_collection, mock_json_interface)

        assert len(result["features"]) == 1
        kili_props = result["features"][0]["properties"]["kili"]
        assert kili_props["job"] == "SEMANTIC_JOB"
        assert kili_props["type"] == "semantic"
        assert kili_props["categories"][0]["name"] == "SEMANTIC_CATEGORY"

    def test_features_with_null_geometry_are_skipped(self, mock_json_interface):
        """Test that features with null geometry are skipped."""
        feature_collection = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": None,
                    "properties": {"some_attribute": "value"},
                },
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "properties": {},
                },
            ],
        }

        result = enrich_geojson_with_kili_properties(feature_collection, mock_json_interface)

        # Only the feature with valid geometry should remain
        assert len(result["features"]) == 1
        assert result["features"][0]["geometry"]["type"] == "Point"

    def test_features_without_compatible_job_are_skipped(self, mock_json_interface):
        """Test that features without compatible jobs are skipped."""
        # Create interface with only classification job
        classification_only_interface = {
            "jobs": {
                "CLASSIFICATION_JOB": {
                    "mlTask": "CLASSIFICATION",
                    "tools": [],
                    "content": {"categories": {"CLASS_CATEGORY": {"name": "Class"}}},
                }
            }
        }

        feature_collection = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "properties": {},
                }
            ],
        }

        result = enrich_geojson_with_kili_properties(
            feature_collection, classification_only_interface
        )

        # No features should remain as there's no compatible job
        assert len(result["features"]) == 0

    def test_empty_feature_collection(self, mock_json_interface):
        """Test handling of empty feature collection."""
        feature_collection = {"type": "FeatureCollection", "features": []}

        result = enrich_geojson_with_kili_properties(feature_collection, mock_json_interface)

        assert result["type"] == "FeatureCollection"
        assert len(result["features"]) == 0

    def test_json_interface_without_jobs(self):
        """Test handling when JSON interface has no jobs."""
        json_interface = {"jobs": {}}
        feature_collection = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "properties": {},
                }
            ],
        }

        result = enrich_geojson_with_kili_properties(feature_collection, json_interface)

        assert len(result["features"]) == 0

    def test_job_without_categories(self, mock_json_interface):
        """Test handling of jobs without categories."""
        json_interface_no_categories = {
            "jobs": {
                "MARKER_JOB": {
                    "mlTask": "OBJECT_DETECTION",
                    "tools": ["marker"],
                    "content": {"categories": {}},
                }
            }
        }

        feature_collection = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "properties": {},
                }
            ],
        }

        result = enrich_geojson_with_kili_properties(
            feature_collection, json_interface_no_categories
        )

        # Feature should be skipped as job has no categories
        assert len(result["features"]) == 0


class TestEnrichGeojsonWithSpecificMapping:
    """Test cases for enrich_geojson_with_specific_mapping function."""

    def test_successful_mapping_with_point_geometry(self, mock_json_interface):
        """Test successful mapping of Point geometry to marker job."""
        feature_collection = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "properties": {},
                }
            ],
        }

        result = enrich_geojson_with_specific_mapping(
            feature_collection, mock_json_interface, "MARKER_JOB", "POINT_CATEGORY"
        )

        assert len(result["features"]) == 1
        kili_props = result["features"][0]["properties"]["kili"]
        assert kili_props["job"] == "MARKER_JOB"
        assert kili_props["type"] == "marker"
        assert kili_props["categories"][0]["name"] == "POINT_CATEGORY"

    def test_successful_mapping_with_linestring_geometry(self, mock_json_interface):
        """Test successful mapping of LineString geometry to polyline job."""
        feature_collection = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "LineString", "coordinates": [[0, 0], [1, 1]]},
                    "properties": {},
                }
            ],
        }

        result = enrich_geojson_with_specific_mapping(
            feature_collection, mock_json_interface, "POLYLINE_JOB", "LINE_CATEGORY"
        )

        assert len(result["features"]) == 1
        kili_props = result["features"][0]["properties"]["kili"]
        assert kili_props["job"] == "POLYLINE_JOB"
        assert kili_props["type"] == "polyline"
        assert kili_props["categories"][0]["name"] == "LINE_CATEGORY"

    def test_polygon_geometry_with_polygon_tool(self, mock_json_interface):
        """Test Polygon geometry mapping to polygon tool."""
        feature_collection = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
                    },
                    "properties": {},
                }
            ],
        }

        result = enrich_geojson_with_specific_mapping(
            feature_collection, mock_json_interface, "POLYGON_JOB", "POLYGON_CATEGORY"
        )

        assert len(result["features"]) == 1
        kili_props = result["features"][0]["properties"]["kili"]
        assert kili_props["job"] == "POLYGON_JOB"
        assert kili_props["type"] == "polygon"

    def test_polygon_geometry_with_semantic_tool(self, mock_json_interface):
        """Test Polygon geometry mapping to semantic tool when polygon tool not available."""
        feature_collection = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
                    },
                    "properties": {},
                }
            ],
        }

        result = enrich_geojson_with_specific_mapping(
            feature_collection, mock_json_interface, "SEMANTIC_JOB", "SEMANTIC_CATEGORY"
        )

        assert len(result["features"]) == 1
        kili_props = result["features"][0]["properties"]["kili"]
        assert kili_props["job"] == "SEMANTIC_JOB"
        assert kili_props["type"] == "semantic"

    def test_multipolygon_geometry_with_semantic_tool(self, mock_json_interface):
        """Test MultiPolygon geometry mapping to semantic tool."""
        feature_collection = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "MultiPolygon",
                        "coordinates": [
                            [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
                            [[[2, 2], [3, 2], [3, 3], [2, 3], [2, 2]]],
                        ],
                    },
                    "properties": {},
                }
            ],
        }

        result = enrich_geojson_with_specific_mapping(
            feature_collection, mock_json_interface, "SEMANTIC_JOB", "SEMANTIC_CATEGORY"
        )

        assert len(result["features"]) == 1
        kili_props = result["features"][0]["properties"]["kili"]
        assert kili_props["job"] == "SEMANTIC_JOB"
        assert kili_props["type"] == "semantic"

    def test_multi_tool_job_with_different_geometries(self, mock_json_interface):
        """Test job with multiple tools handles different geometry types correctly."""
        feature_collection = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "properties": {},
                },
                {
                    "type": "Feature",
                    "geometry": {"type": "LineString", "coordinates": [[0, 0], [1, 1]]},
                    "properties": {},
                },
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
                    },
                    "properties": {},
                },
            ],
        }

        result = enrich_geojson_with_specific_mapping(
            feature_collection, mock_json_interface, "MULTI_TOOL_JOB", "MULTI_CATEGORY"
        )

        assert len(result["features"]) == 3

        # Check Point mapping
        point_kili = result["features"][0]["properties"]["kili"]
        assert point_kili["type"] == "marker"
        assert point_kili["job"] == "MULTI_TOOL_JOB"

        # Check LineString mapping
        line_kili = result["features"][1]["properties"]["kili"]
        assert line_kili["type"] == "polyline"
        assert line_kili["job"] == "MULTI_TOOL_JOB"

        # Check Polygon mapping (should prefer polygon over semantic)
        polygon_kili = result["features"][2]["properties"]["kili"]
        assert polygon_kili["type"] == "polygon"
        assert polygon_kili["job"] == "MULTI_TOOL_JOB"

    def test_nonexistent_job_raises_error(self, mock_json_interface):
        """Test that specifying a non-existent job raises ValueError."""
        feature_collection = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "properties": {},
                }
            ],
        }

        with pytest.raises(ValueError, match="Job 'NONEXISTENT_JOB' not found in project"):
            enrich_geojson_with_specific_mapping(
                feature_collection, mock_json_interface, "NONEXISTENT_JOB", "SOME_CATEGORY"
            )

    def test_non_object_detection_job_raises_error(self, mock_json_interface):
        """Test that specifying a non-OBJECT_DETECTION job raises ValueError."""
        feature_collection = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "properties": {},
                }
            ],
        }

        with pytest.raises(
            ValueError, match="Job 'CLASSIFICATION_JOB' is not an OBJECT_DETECTION job"
        ):
            enrich_geojson_with_specific_mapping(
                feature_collection, mock_json_interface, "CLASSIFICATION_JOB", "CLASS_CATEGORY"
            )

    def test_nonexistent_category_raises_error(self, mock_json_interface):
        """Test that specifying a non-existent category raises ValueError."""
        feature_collection = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "properties": {},
                }
            ],
        }

        with pytest.raises(
            ValueError, match="Category 'NONEXISTENT_CATEGORY' not found in job 'MARKER_JOB'"
        ):
            enrich_geojson_with_specific_mapping(
                feature_collection, mock_json_interface, "MARKER_JOB", "NONEXISTENT_CATEGORY"
            )

    def test_incompatible_geometry_tool_combination_skipped(self, mock_json_interface):
        """Test that incompatible geometry-tool combinations are skipped."""
        feature_collection = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "properties": {},
                },
                {
                    "type": "Feature",
                    "geometry": {"type": "LineString", "coordinates": [[0, 0], [1, 1]]},
                    "properties": {},
                },
            ],
        }

        # Try to map to a job that only has polygon tool
        result = enrich_geojson_with_specific_mapping(
            feature_collection, mock_json_interface, "POLYGON_JOB", "POLYGON_CATEGORY"
        )

        # Both features should be skipped as they're incompatible with polygon tool
        assert len(result["features"]) == 0

    def test_features_with_null_geometry_are_skipped(self, mock_json_interface):
        """Test that features with null geometry are skipped."""
        feature_collection = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": None,
                    "properties": {"some_attribute": "value"},
                },
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "properties": {},
                },
            ],
        }

        result = enrich_geojson_with_specific_mapping(
            feature_collection, mock_json_interface, "MARKER_JOB", "POINT_CATEGORY"
        )

        # Only the feature with valid geometry should remain
        assert len(result["features"]) == 1
        assert result["features"][0]["geometry"]["type"] == "Point"

    def test_existing_properties_are_preserved(self, mock_json_interface):
        """Test that existing properties are preserved when adding kili properties."""
        feature_collection = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "properties": {"existing_prop": "existing_value", "another_prop": 123},
                }
            ],
        }

        result = enrich_geojson_with_specific_mapping(
            feature_collection, mock_json_interface, "MARKER_JOB", "POINT_CATEGORY"
        )

        assert len(result["features"]) == 1
        properties = result["features"][0]["properties"]

        # Check that kili properties were added
        assert "kili" in properties
        assert properties["kili"]["job"] == "MARKER_JOB"

        # Check that existing properties were preserved
        assert properties["existing_prop"] == "existing_value"
        assert properties["another_prop"] == 123

    def test_empty_feature_collection(self, mock_json_interface):
        """Test handling of empty feature collection."""
        feature_collection = {"type": "FeatureCollection", "features": []}

        result = enrich_geojson_with_specific_mapping(
            feature_collection, mock_json_interface, "MARKER_JOB", "POINT_CATEGORY"
        )

        assert result["type"] == "FeatureCollection"
        assert len(result["features"]) == 0
