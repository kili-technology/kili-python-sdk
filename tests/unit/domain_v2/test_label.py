"""Unit tests for Label domain contracts."""

from typing import cast

from kili.domain_v2.label import (
    LabelContract,
    LabelView,
    filter_labels_by_type,
    sort_labels_by_created_at,
    validate_label,
)


class TestLabelContract:
    """Test suite for LabelContract."""

    def test_validate_label_with_valid_data(self):
        """Test validating a valid label contract."""
        label_data = {
            "id": "label-123",
            "author": {"id": "user-1", "email": "user@example.com", "name": "John Doe"},
            "jsonResponse": {"job1": {"categories": [{"name": "CAT_A"}]}},
            "createdAt": "2024-01-01T00:00:00Z",
            "labelType": "DEFAULT",
            "isLatestLabelForUser": True,
        }

        result = validate_label(label_data)
        assert result == label_data

    def test_validate_label_with_partial_data(self):
        """Test validating a label with only some fields."""
        label_data = {
            "id": "label-123",
            "jsonResponse": {},
        }

        result = validate_label(label_data)
        assert result == label_data

    def test_validate_label_with_prediction_data(self):
        """Test validating a prediction label."""
        label_data = {
            "id": "label-123",
            "labelType": "PREDICTION",
            "modelName": "model-v1",
            "jsonResponse": {"predictions": []},
        }

        result = validate_label(label_data)
        assert result == label_data
        assert result.get("labelType") == "PREDICTION"


class TestLabelView:
    """Test suite for LabelView wrapper."""

    def test_label_view_basic_properties(self):
        """Test basic property access on LabelView."""
        label_data = cast(
            LabelContract,
            {
                "id": "label-123",
                "author": {"id": "user-1", "email": "user@example.com"},
                "jsonResponse": {"job": "value"},
                "createdAt": "2024-01-01T00:00:00Z",
                "labelType": "DEFAULT",
            },
        )

        view = LabelView(label_data)

        assert view.id == "label-123"
        assert view.author_email == "user@example.com"
        assert view.author_id == "user-1"
        assert view.created_at == "2024-01-01T00:00:00Z"
        assert view.label_type == "DEFAULT"

    def test_label_view_author_properties(self):
        """Test author-related properties."""
        label_data = cast(
            LabelContract,
            {
                "id": "label-123",
                "author": {
                    "id": "user-1",
                    "email": "user@example.com",
                    "name": "John Doe",
                },
            },
        )

        view = LabelView(label_data)

        assert view.author is not None
        assert view.author.get("email") == "user@example.com"
        assert view.author.get("name") == "John Doe"
        assert view.author_email == "user@example.com"
        assert view.author_id == "user-1"

    def test_label_view_missing_author(self):
        """Test label view with no author."""
        label_data = cast(LabelContract, {"id": "label-123"})
        view = LabelView(label_data)

        assert view.author is None
        assert view.author_email == ""
        assert view.author_id == ""

    def test_label_view_display_name(self):
        """Test display name property."""
        # With author email
        label_data = cast(
            LabelContract,
            {
                "id": "label-123",
                "author": {"email": "user@example.com"},
            },
        )
        view = LabelView(label_data)
        assert view.display_name == "user@example.com"

        # Without author
        label_data = cast(LabelContract, {"id": "label-123"})
        view = LabelView(label_data)
        assert view.display_name == "label-123"

    def test_label_view_is_prediction(self):
        """Test is_prediction property."""
        # Prediction type
        label_data = cast(LabelContract, {"id": "label-123", "labelType": "PREDICTION"})
        view = LabelView(label_data)
        assert view.is_prediction is True

        # Inference type
        label_data = cast(LabelContract, {"id": "label-123", "labelType": "INFERENCE"})
        view = LabelView(label_data)
        assert view.is_prediction is True

        # Default type
        label_data = cast(LabelContract, {"id": "label-123", "labelType": "DEFAULT"})
        view = LabelView(label_data)
        assert view.is_prediction is False

    def test_label_view_is_review(self):
        """Test is_review property."""
        # Review type
        label_data = cast(LabelContract, {"id": "label-123", "labelType": "REVIEW"})
        view = LabelView(label_data)
        assert view.is_review is True

        # Default type
        label_data = cast(LabelContract, {"id": "label-123", "labelType": "DEFAULT"})
        view = LabelView(label_data)
        assert view.is_review is False

    def test_label_view_quality_marks(self):
        """Test quality mark properties."""
        label_data = cast(
            LabelContract,
            {
                "id": "label-123",
                "consensusMark": 0.95,
                "honeypotMark": 0.87,
            },
        )

        view = LabelView(label_data)

        assert view.consensus_mark == 0.95
        assert view.honeypot_mark == 0.87

    def test_label_view_timing_properties(self):
        """Test timing-related properties."""
        label_data = cast(
            LabelContract,
            {
                "id": "label-123",
                "secondsToLabel": 120,
                "createdAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-01T00:05:00Z",
            },
        )

        view = LabelView(label_data)

        assert view.seconds_to_label == 120
        assert view.created_at == "2024-01-01T00:00:00Z"
        assert view.updated_at == "2024-01-01T00:05:00Z"

    def test_label_view_json_response(self):
        """Test JSON response property."""
        label_data = cast(
            LabelContract,
            {
                "id": "label-123",
                "jsonResponse": {
                    "JOB_1": {"categories": [{"name": "CAT_A"}]},
                    "JOB_2": {"text": "Some text"},
                },
            },
        )

        view = LabelView(label_data)

        assert "JOB_1" in view.json_response
        assert "JOB_2" in view.json_response
        assert view.json_response["JOB_1"]["categories"][0]["name"] == "CAT_A"

    def test_label_view_to_dict(self):
        """Test converting view back to dictionary."""
        label_data = cast(
            LabelContract,
            {
                "id": "label-123",
                "jsonResponse": {},
                "labelType": "DEFAULT",
            },
        )

        view = LabelView(label_data)
        result = view.to_dict()

        assert result == label_data
        assert result is label_data


class TestLabelHelpers:
    """Test suite for label helper functions."""

    def test_sort_labels_by_created_at_ascending(self):
        """Test sorting labels by creation time in ascending order."""
        labels = [
            cast(LabelContract, {"id": "label-3", "createdAt": "2024-01-03T00:00:00Z"}),
            cast(LabelContract, {"id": "label-1", "createdAt": "2024-01-01T00:00:00Z"}),
            cast(LabelContract, {"id": "label-2", "createdAt": "2024-01-02T00:00:00Z"}),
        ]

        sorted_labels = sort_labels_by_created_at(labels, reverse=False)

        assert sorted_labels[0].get("id") == "label-1"
        assert sorted_labels[1].get("id") == "label-2"
        assert sorted_labels[2].get("id") == "label-3"

    def test_sort_labels_by_created_at_descending(self):
        """Test sorting labels by creation time in descending order."""
        labels = [
            cast(LabelContract, {"id": "label-1", "createdAt": "2024-01-01T00:00:00Z"}),
            cast(LabelContract, {"id": "label-3", "createdAt": "2024-01-03T00:00:00Z"}),
            cast(LabelContract, {"id": "label-2", "createdAt": "2024-01-02T00:00:00Z"}),
        ]

        sorted_labels = sort_labels_by_created_at(labels, reverse=True)

        assert sorted_labels[0].get("id") == "label-3"
        assert sorted_labels[1].get("id") == "label-2"
        assert sorted_labels[2].get("id") == "label-1"

    def test_sort_labels_with_missing_created_at(self):
        """Test sorting labels when some lack createdAt."""
        labels = [
            cast(LabelContract, {"id": "label-2", "createdAt": "2024-01-02T00:00:00Z"}),
            cast(LabelContract, {"id": "label-no-date"}),
            cast(LabelContract, {"id": "label-1", "createdAt": "2024-01-01T00:00:00Z"}),
        ]

        sorted_labels = sort_labels_by_created_at(labels)

        # Label without date should come first (empty string sorts first)
        assert sorted_labels[0].get("id") == "label-no-date"

    def test_filter_labels_by_type_default(self):
        """Test filtering labels by DEFAULT type."""
        labels = [
            cast(LabelContract, {"id": "label-1", "labelType": "DEFAULT"}),
            cast(LabelContract, {"id": "label-2", "labelType": "REVIEW"}),
            cast(LabelContract, {"id": "label-3", "labelType": "DEFAULT"}),
            cast(LabelContract, {"id": "label-4", "labelType": "PREDICTION"}),
        ]

        filtered = filter_labels_by_type(labels, "DEFAULT")

        assert len(filtered) == 2
        assert filtered[0].get("id") == "label-1"
        assert filtered[1].get("id") == "label-3"

    def test_filter_labels_by_type_review(self):
        """Test filtering labels by REVIEW type."""
        labels = [
            cast(LabelContract, {"id": "label-1", "labelType": "DEFAULT"}),
            cast(LabelContract, {"id": "label-2", "labelType": "REVIEW"}),
            cast(LabelContract, {"id": "label-3", "labelType": "REVIEW"}),
        ]

        filtered = filter_labels_by_type(labels, "REVIEW")

        assert len(filtered) == 2
        assert filtered[0].get("id") == "label-2"
        assert filtered[1].get("id") == "label-3"

    def test_filter_labels_by_type_no_matches(self):
        """Test filtering when no labels match the type."""
        labels = [
            cast(LabelContract, {"id": "label-1", "labelType": "DEFAULT"}),
            cast(LabelContract, {"id": "label-2", "labelType": "DEFAULT"}),
        ]

        filtered = filter_labels_by_type(labels, "REVIEW")

        assert len(filtered) == 0
