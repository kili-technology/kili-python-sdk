"""Unit tests for Asset domain contracts."""

from typing import cast

from kili.domain_v2.asset import AssetContract, AssetView, validate_asset


class TestAssetContract:
    """Test suite for AssetContract."""

    def test_validate_asset_with_valid_data(self):
        """Test validating a valid asset contract."""
        asset_data = {
            "id": "asset-123",
            "externalId": "ext-123",
            "content": "https://example.com/image.jpg",
            "jsonMetadata": {"key": "value"},
            "labels": [],
            "status": "TODO",
            "isHoneypot": False,
            "skipped": False,
            "createdAt": "2024-01-01T00:00:00Z",
        }

        # Should not raise
        result = validate_asset(asset_data)
        assert result == asset_data

    def test_validate_asset_with_partial_data(self):
        """Test validating an asset with only some fields."""
        asset_data = {
            "id": "asset-123",
            "externalId": "ext-123",
        }

        # Should not raise since TypedDict has total=False
        result = validate_asset(asset_data)
        assert result == asset_data

    def test_validate_asset_with_nested_labels(self):
        """Test validating an asset with nested label data."""
        asset_data = {
            "id": "asset-123",
            "externalId": "ext-123",
            "labels": [
                {
                    "id": "label-1",
                    "author": {"id": "user-1", "email": "user@example.com"},
                    "jsonResponse": {"job": "value"},
                    "createdAt": "2024-01-01T00:00:00Z",
                }
            ],
            "latestLabel": {
                "id": "label-1",
                "author": {"id": "user-1", "email": "user@example.com"},
                "jsonResponse": {"job": "value"},
            },
        }

        result = validate_asset(asset_data)
        assert result == asset_data
        assert len(result.get("labels", [])) == 1

    def test_validate_asset_with_current_step(self):
        """Test validating an asset with workflow v2 current step."""
        asset_data = {
            "id": "asset-123",
            "currentStep": {
                "name": "Labeling",
                "status": "TO_DO",
            },
        }

        result = validate_asset(asset_data)
        assert result == asset_data
        current_step = result.get("currentStep")
        assert current_step is not None
        assert current_step.get("name") == "Labeling"


class TestAssetView:
    """Test suite for AssetView wrapper."""

    def test_asset_view_basic_properties(self):
        """Test basic property access on AssetView."""
        asset_data = cast(
            AssetContract,
            {
                "id": "asset-123",
                "externalId": "ext-123",
                "content": "https://example.com/image.jpg",
                "isHoneypot": True,
                "skipped": False,
            },
        )

        view = AssetView(asset_data)

        assert view.id == "asset-123"
        assert view.external_id == "ext-123"
        assert view.content == "https://example.com/image.jpg"
        assert view.is_honeypot is True
        assert view.skipped is False

    def test_asset_view_display_name(self):
        """Test display name property."""
        # With external ID
        asset_data = cast(AssetContract, {"id": "asset-123", "externalId": "ext-123"})
        view = AssetView(asset_data)
        assert view.display_name == "ext-123"

        # Without external ID
        asset_data = cast(AssetContract, {"id": "asset-123"})
        view = AssetView(asset_data)
        assert view.display_name == "asset-123"

    def test_asset_view_labels(self):
        """Test label-related properties."""
        asset_data = cast(
            AssetContract,
            {
                "id": "asset-123",
                "labels": [
                    {"id": "label-1", "jsonResponse": {}},
                    {"id": "label-2", "jsonResponse": {}},
                ],
            },
        )

        view = AssetView(asset_data)

        assert view.has_labels is True
        assert view.label_count == 2
        assert len(view.labels) == 2

    def test_asset_view_no_labels(self):
        """Test asset view with no labels."""
        asset_data = cast(AssetContract, {"id": "asset-123"})
        view = AssetView(asset_data)

        assert view.has_labels is False
        assert view.label_count == 0
        assert view.labels == []

    def test_asset_view_metadata(self):
        """Test metadata property access."""
        asset_data = cast(
            AssetContract,
            {
                "id": "asset-123",
                "jsonMetadata": {"custom_field": "custom_value", "priority": 1},
            },
        )

        view = AssetView(asset_data)

        assert view.metadata is not None
        assert view.metadata["custom_field"] == "custom_value"
        assert view.metadata["priority"] == 1

    def test_asset_view_current_step(self):
        """Test current step property for workflow v2."""
        asset_data = cast(
            AssetContract,
            {
                "id": "asset-123",
                "currentStep": {
                    "name": "Review",
                    "status": "DONE",
                },
            },
        )

        view = AssetView(asset_data)

        assert view.current_step is not None
        assert view.current_step.get("name") == "Review"
        assert view.current_step.get("status") == "DONE"

    def test_asset_view_status(self):
        """Test status property for workflow v1."""
        asset_data = cast(
            AssetContract,
            {
                "id": "asset-123",
                "status": "LABELED",
            },
        )

        view = AssetView(asset_data)
        assert view.status == "LABELED"

    def test_asset_view_to_dict(self):
        """Test converting view back to dictionary."""
        asset_data = cast(
            AssetContract,
            {
                "id": "asset-123",
                "externalId": "ext-123",
                "content": "test",
            },
        )

        view = AssetView(asset_data)
        result = view.to_dict()

        assert result == asset_data
        assert result is asset_data  # Should be the same object

    def test_asset_view_missing_fields(self):
        """Test accessing missing fields returns appropriate defaults."""
        asset_data = cast(AssetContract, {"id": "asset-123"})
        view = AssetView(asset_data)

        assert view.external_id == ""
        assert view.content == ""
        assert view.metadata is None
        assert view.latest_label is None
        assert view.status is None
        assert view.current_step is None
        assert view.created_at is None
