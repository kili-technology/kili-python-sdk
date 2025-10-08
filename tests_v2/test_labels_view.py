"""Integration tests for LabelView objects returned by the labels namespace.

This test file validates that the labels.list() method correctly returns
LabelView objects instead of dictionaries, and that these objects provide
proper property access and backward compatibility.

Test Strategy:
    - Verify list() returns LabelView objects in all modes (list, generator)
    - Test LabelView property access for common properties
    - Validate backward compatibility with dictionary interface via to_dict()
    - Ensure ParsedLabel mode remains unchanged
    - Test nested namespaces (predictions, inferences)
"""

import pytest

from kili.domain_v2.label import LabelView
from kili.utils.labels.parsing import ParsedLabel
from tests_v2 import (
    assert_is_view,
    assert_view_has_dict_compatibility,
    assert_view_property_access,
)


@pytest.mark.integration()
def test_list_returns_label_views(kili_client):
    """Test that labels.list() in list mode returns LabelView objects."""
    # Get the first project to test with
    projects = list(kili_client.projects.list(first=1, as_generator=False))

    if not projects:
        pytest.skip("No projects available for testing")

    # Extract project ID from ProjectView object
    project_id = projects[0].id

    # Get labels in list mode
    labels = kili_client.labels.list(project_id=project_id, first=5, as_generator=False)

    # Verify we get a list
    assert isinstance(labels, list), "labels.list() with as_generator=False should return a list"

    # Skip if no labels
    if not labels:
        pytest.skip(f"No labels available in project {project_id}")

    # Verify each item is a LabelView
    for label in labels:
        assert_is_view(label, LabelView)

        # Verify we can access basic properties
        assert hasattr(label, "id")
        assert hasattr(label, "label_type")
        assert hasattr(label, "author")


@pytest.mark.integration()
def test_list_generator_returns_label_views(kili_client):
    """Test that labels.list() in generator mode returns LabelView objects."""
    # Get the first project to test with
    projects = list(kili_client.projects.list(first=1, as_generator=False))

    if not projects:
        pytest.skip("No projects available for testing")

    # Extract project ID from ProjectView object
    project_id = projects[0].id

    # Get labels in generator mode
    labels_gen = kili_client.labels.list(project_id=project_id, first=5, as_generator=True)

    # Take first 5 items from generator (or fewer if less available)
    labels_from_gen = []
    for i, label in enumerate(labels_gen):
        if i >= 5:
            break
        labels_from_gen.append(label)

    # Skip if no labels
    if not labels_from_gen:
        pytest.skip(f"No labels available in project {project_id}")

    # Verify each yielded item is a LabelView
    for label in labels_from_gen:
        assert_is_view(label, LabelView)

        # Verify we can access basic properties
        assert hasattr(label, "id")
        assert hasattr(label, "label_type")


@pytest.mark.integration()
def test_label_view_properties(kili_client):
    """Test that LabelView provides access to all expected properties."""
    # Get the first project to test with
    projects = list(kili_client.projects.list(first=1, as_generator=False))

    if not projects:
        pytest.skip("No projects available for testing")

    # Extract project ID from ProjectView object
    project_id = projects[0].id

    # Get first label
    labels = kili_client.labels.list(project_id=project_id, first=1, as_generator=False)

    if not labels:
        pytest.skip(f"No labels available in project {project_id}")

    label = labels[0]

    # Verify LabelView type
    assert_is_view(label, LabelView)

    # Test core properties exist and are accessible
    assert_view_property_access(label, "id")
    assert_view_property_access(label, "label_type")
    assert_view_property_access(label, "author")
    assert_view_property_access(label, "json_response")
    assert_view_property_access(label, "created_at")

    # Test that id is not empty
    assert label.id, "Label id should not be empty"

    # Test optional properties
    assert_view_property_access(label, "author_email")
    assert_view_property_access(label, "author_id")
    assert_view_property_access(label, "updated_at")
    assert_view_property_access(label, "model_name")
    assert_view_property_access(label, "seconds_to_label")
    assert_view_property_access(label, "is_latest")
    assert_view_property_access(label, "consensus_mark")
    assert_view_property_access(label, "honeypot_mark")

    # Test computed properties
    assert_view_property_access(label, "is_prediction")
    assert_view_property_access(label, "is_review")
    assert_view_property_access(label, "display_name")

    # Verify json_response is a dictionary
    assert isinstance(label.json_response, dict), "json_response property should return a dict"

    # Verify label_type is one of the expected values
    if label.label_type:
        assert label.label_type in (
            "DEFAULT",
            "AUTOSAVE",
            "PREDICTION",
            "INFERENCE",
            "REVIEW",
        ), f"Unexpected label_type: {label.label_type}"

    # Verify is_prediction logic
    if label.label_type in ("PREDICTION", "INFERENCE"):
        assert label.is_prediction, "is_prediction should be True for PREDICTION/INFERENCE labels"
    else:
        assert not label.is_prediction, "is_prediction should be False for non-PREDICTION labels"

    # Verify is_review logic
    if label.label_type == "REVIEW":
        assert label.is_review, "is_review should be True for REVIEW labels"
    else:
        assert not label.is_review, "is_review should be False for non-REVIEW labels"


@pytest.mark.integration()
def test_label_view_dict_compatibility(kili_client):
    """Test that LabelView maintains backward compatibility via to_dict()."""
    # Get the first project to test with
    projects = list(kili_client.projects.list(first=1, as_generator=False))

    if not projects:
        pytest.skip("No projects available for testing")

    # Extract project ID from ProjectView object
    project_id = projects[0].id

    # Get first label
    labels = kili_client.labels.list(project_id=project_id, first=1, as_generator=False)

    if not labels:
        pytest.skip(f"No labels available in project {project_id}")

    label = labels[0]

    # Verify LabelView type
    assert_is_view(label, LabelView)

    # Test dictionary compatibility
    assert_view_has_dict_compatibility(label)

    # Get dictionary representation
    label_dict = label.to_dict()

    # Verify it's a dictionary
    assert isinstance(label_dict, dict), "to_dict() should return a dictionary"

    # Verify dictionary has expected keys
    assert "id" in label_dict, "Dictionary should have 'id' key"

    # Verify dictionary values match property values
    if "labelType" in label_dict:
        assert (
            label_dict["labelType"] == label.label_type
        ), "Dictionary labelType should match property"

    if "jsonResponse" in label_dict:
        assert (
            label_dict["jsonResponse"] == label.json_response
        ), "Dictionary jsonResponse should match property"

    if "createdAt" in label_dict:
        assert (
            label_dict["createdAt"] == label.created_at
        ), "Dictionary createdAt should match property"

    # Verify to_dict() returns the same reference (zero-copy)
    assert label_dict is label._data, "to_dict() should return the same reference as _data"


@pytest.mark.integration()
def test_label_view_with_parsed_label(kili_client):
    """Test that ParsedLabel mode still returns ParsedLabel objects (unchanged behavior)."""
    # Get the first project to test with
    projects = list(kili_client.projects.list(first=1, as_generator=False))

    if not projects:
        pytest.skip("No projects available for testing")

    # Extract project ID from ProjectView object
    project_id = projects[0].id

    # Get labels in parsed_label mode
    labels = kili_client.labels.list(
        project_id=project_id, first=5, output_format="parsed_label", as_generator=False
    )

    # Skip if no labels
    if not labels:
        pytest.skip(f"No labels available in project {project_id}")

    # Verify each item is a ParsedLabel (not LabelView)
    for label in labels:
        assert isinstance(
            label, ParsedLabel
        ), f"Expected ParsedLabel with output_format='parsed_label', got {type(label).__name__}"
        # ParsedLabel should NOT be a LabelView
        assert not isinstance(label, LabelView), "ParsedLabel should not be wrapped in LabelView"


@pytest.mark.integration()
def test_predictions_list_returns_label_views(kili_client):
    """Test that labels.predictions.list() returns LabelView objects."""
    # Get the first project to test with
    projects = list(kili_client.projects.list(first=1, as_generator=False))

    if not projects:
        pytest.skip("No projects available for testing")

    # Extract project ID from ProjectView object
    project_id = projects[0].id

    # Get predictions in list mode
    predictions = kili_client.labels.predictions.list(
        project_id=project_id, first=5, as_generator=False
    )

    # Verify we get a list
    assert isinstance(
        predictions, list
    ), "labels.predictions.list() with as_generator=False should return a list"

    # Skip if no predictions
    if not predictions:
        pytest.skip(f"No prediction labels available in project {project_id}")

    # Verify each item is a LabelView
    for prediction in predictions:
        assert_is_view(prediction, LabelView)

        # Verify we can access basic properties
        assert hasattr(prediction, "id")
        assert hasattr(prediction, "label_type")

        # Verify it's actually a PREDICTION label
        assert (
            prediction.label_type == "PREDICTION"
        ), f"Expected PREDICTION label, got {prediction.label_type}"


@pytest.mark.integration()
def test_inferences_list_returns_label_views(kili_client):
    """Test that labels.inferences.list() returns LabelView objects."""
    # Get the first project to test with
    projects = list(kili_client.projects.list(first=1, as_generator=False))

    if not projects:
        pytest.skip("No projects available for testing")

    # Extract project ID from ProjectView object
    project_id = projects[0].id

    # Get inferences in list mode
    inferences = kili_client.labels.inferences.list(
        project_id=project_id, first=5, as_generator=False
    )

    # Verify we get a list
    assert isinstance(
        inferences, list
    ), "labels.inferences.list() with as_generator=False should return a list"

    # Skip if no inferences
    if not inferences:
        pytest.skip(f"No inference labels available in project {project_id}")

    # Verify each item is a LabelView
    for inference in inferences:
        assert_is_view(inference, LabelView)

        # Verify we can access basic properties
        assert hasattr(inference, "id")
        assert hasattr(inference, "label_type")

        # Verify it's actually an INFERENCE label
        assert (
            inference.label_type == "INFERENCE"
        ), f"Expected INFERENCE label, got {inference.label_type}"


@pytest.mark.integration()
def test_label_view_filtering(kili_client):
    """Test that LabelView objects work correctly with filtering."""
    # Get the first project to test with
    projects = list(kili_client.projects.list(first=1, as_generator=False))

    if not projects:
        pytest.skip("No projects available for testing")

    # Extract project ID from ProjectView object
    project_id = projects[0].id

    # Get all labels
    all_labels = kili_client.labels.list(project_id=project_id, first=10, as_generator=False)

    if not all_labels:
        pytest.skip(f"No labels available in project {project_id}")

    # Get the first label's ID
    first_label_id = all_labels[0].id

    # Query for specific label by ID
    filtered_labels = kili_client.labels.list(
        project_id=project_id, label_id=first_label_id, as_generator=False
    )

    # Verify we got results
    assert len(filtered_labels) > 0, "Should get at least one label with specific label_id"

    # Verify each result is a LabelView
    for label in filtered_labels:
        assert_is_view(label, LabelView)

        # Verify it's the correct label
        assert label.id == first_label_id, "Filtered label should have the requested ID"


@pytest.mark.integration()
def test_label_view_empty_results(kili_client):
    """Test that empty results are handled correctly."""
    # Get the first project to test with
    projects = list(kili_client.projects.list(first=1, as_generator=False))

    if not projects:
        pytest.skip("No projects available for testing")

    # Extract project ID from ProjectView object
    project_id = projects[0].id

    # Query with a filter that should return no results
    # Using a non-existent label ID
    empty_labels = kili_client.labels.list(
        project_id=project_id, label_id="non-existent-label-id-12345", as_generator=False
    )

    # Verify we get an empty list
    assert isinstance(empty_labels, list), "Should return a list even when no results"
    assert len(empty_labels) == 0, "Should return empty list for non-existent label"


@pytest.mark.integration()
def test_label_view_with_fields_parameter(kili_client):
    """Test that LabelView works correctly with custom fields parameter."""
    # Get the first project to test with
    projects = list(kili_client.projects.list(first=1, as_generator=False))

    if not projects:
        pytest.skip("No projects available for testing")

    # Extract project ID from ProjectView object
    project_id = projects[0].id

    # Query with specific fields
    labels = kili_client.labels.list(
        project_id=project_id,
        first=1,
        fields=["id", "labelType", "createdAt", "jsonResponse"],
        as_generator=False,
    )

    if not labels:
        pytest.skip(f"No labels available in project {project_id}")

    label = labels[0]

    # Verify it's still a LabelView
    assert_is_view(label, LabelView)

    # Verify requested fields are accessible
    assert_view_property_access(label, "id")
    assert_view_property_access(label, "label_type")
    assert_view_property_access(label, "created_at")
    assert_view_property_access(label, "json_response")
