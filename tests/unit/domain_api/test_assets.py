"""Unit tests for the AssetsNamespace domain API."""

from unittest.mock import MagicMock

import pytest

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.client import Kili
from kili.domain_api.assets import AssetsNamespace


class TestAssetsNamespace:
    """Test cases for AssetsNamespace domain API."""

    @pytest.fixture()
    def mock_client(self):
        """Create a mock Kili client."""
        client = MagicMock(spec=Kili)
        # Mock all the legacy methods that AssetsNamespace delegates to
        client.assets = MagicMock()
        client.count_assets = MagicMock()
        client.append_many_to_dataset = MagicMock()
        client.delete_many_from_dataset = MagicMock()
        client.update_properties_in_assets = MagicMock()
        client.assign_assets_to_labelers = MagicMock()
        client.send_back_to_queue = MagicMock()
        client.add_to_review = MagicMock()
        client.change_asset_external_ids = MagicMock()
        client.add_metadata = MagicMock()
        client.set_metadata = MagicMock()
        client.skip_or_unskip = MagicMock()
        client.update_asset_consensus = MagicMock()
        return client

    @pytest.fixture()
    def mock_gateway(self):
        """Create a mock KiliAPIGateway."""
        return MagicMock(spec=KiliAPIGateway)

    @pytest.fixture()
    def assets_namespace(self, mock_client, mock_gateway):
        """Create an AssetsNamespace instance."""
        return AssetsNamespace(mock_client, mock_gateway)


class TestAssetsNamespaceCoreOperations:
    """Test core operations of AssetsNamespace."""

    @pytest.fixture()
    def mock_client(self):
        """Create a mock Kili client."""
        client = MagicMock(spec=Kili)
        client.assets = MagicMock()
        client.count_assets = MagicMock()
        client.append_many_to_dataset = MagicMock()
        client.delete_many_from_dataset = MagicMock()
        client.update_properties_in_assets = MagicMock()
        return client

    @pytest.fixture()
    def mock_gateway(self):
        """Create a mock KiliAPIGateway."""
        return MagicMock(spec=KiliAPIGateway)

    @pytest.fixture()
    def assets_namespace(self, mock_client, mock_gateway):
        """Create an AssetsNamespace instance."""
        return AssetsNamespace(mock_client, mock_gateway)

    def test_list_assets_generator(self, assets_namespace):
        """Test list method returns generator by default."""

        # Mock the legacy client method to return a generator
        def mock_generator():
            yield {"id": "asset1", "externalId": "ext1"}
            yield {"id": "asset2", "externalId": "ext2"}

        assets_namespace._client.assets.return_value = mock_generator()

        result = assets_namespace.list_as_generator(project_id="project_123")

        # Should return a generator
        assert hasattr(result, "__iter__")
        assets_list = list(result)
        assert len(assets_list) == 2
        assert assets_list[0]["id"] == "asset1"

        # Verify the legacy method was called with correct parameters
        assets_namespace._client.assets.assert_called_once()
        call_kwargs = assets_namespace._client.assets.call_args[1]
        assert call_kwargs["project_id"] == "project_123"
        assert call_kwargs["as_generator"] is True

    def test_list_assets_as_list(self, assets_namespace):
        """Test list method returns list when as_generator=False."""
        # Mock the legacy client method
        assets_namespace._client.assets.return_value = [
            {"id": "asset1", "externalId": "ext1"},
            {"id": "asset2", "externalId": "ext2"},
        ]

        result = assets_namespace.list(project_id="project_123")

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["id"] == "asset1"

        # Verify the legacy method was called with correct parameters
        assets_namespace._client.assets.assert_called_once()
        call_kwargs = assets_namespace._client.assets.call_args[1]
        assert call_kwargs["project_id"] == "project_123"
        assert call_kwargs["as_generator"] is False

    def test_list_assets_with_step_status_not_in_filter(self, assets_namespace):
        """Test list method with step_status_not_in filter."""
        # Mock the legacy client method
        assets_namespace._client.assets.return_value = [
            {"id": "asset1", "externalId": "ext1"},
        ]

        result = assets_namespace.list(
            project_id="project_123", filter={"step_status_not_in": ["DONE", "SKIPPED"]}
        )

        # Verify the legacy method was called with the filter
        assets_namespace._client.assets.assert_called_once()
        call_kwargs = assets_namespace._client.assets.call_args[1]
        assert call_kwargs["step_status_not_in"] == ["DONE", "SKIPPED"]

    def test_list_assets_with_step_name_not_in_filter(self, assets_namespace):
        """Test list method with step_name_not_in filter."""
        # Mock the legacy client method
        assets_namespace._client.assets.return_value = [
            {"id": "asset1", "externalId": "ext1"},
        ]

        result = assets_namespace.list(
            project_id="project_123", filter={"step_name_not_in": ["Review", "QA"]}
        )

        # Verify the legacy method was called with the filter
        assets_namespace._client.assets.assert_called_once()
        call_kwargs = assets_namespace._client.assets.call_args[1]
        assert call_kwargs["step_name_not_in"] == ["Review", "QA"]

    def test_count_assets_with_step_filters_not_in(self, assets_namespace):
        """Test count method with step_status_not_in and step_name_not_in filters."""
        # Mock the legacy client method
        assets_namespace._client.count_assets.return_value = 15

        result = assets_namespace.count(
            project_id="project_123",
            filter={"step_status_not_in": ["DONE"], "step_name_not_in": ["Final Review"]},
        )

        # Verify the result
        assert result == 15

        # Verify the legacy method was called with both filters
        assets_namespace._client.count_assets.assert_called_once()
        call_kwargs = assets_namespace._client.count_assets.call_args[1]
        assert call_kwargs["step_status_not_in"] == ["DONE"]
        assert call_kwargs["step_name_not_in"] == ["Final Review"]

    def test_count_assets(self, assets_namespace):
        """Test count method."""
        # Mock the legacy client method
        assets_namespace._client.count_assets.return_value = 42

        result = assets_namespace.count(project_id="project_123")

        assert result == 42
        # Verify the legacy method was called with correct parameters
        assets_namespace._client.count_assets.assert_called_once()
        call_kwargs = assets_namespace._client.count_assets.call_args[1]
        assert call_kwargs["project_id"] == "project_123"

    def test_list_assets_uses_project_workflow_defaults(self, assets_namespace):
        """Ensure default fields follow project workflow version."""
        # Mock the legacy client method
        assets_namespace._client.assets.return_value = []

        assets_namespace.list(project_id="project_321")

        # Verify the legacy method was called
        assets_namespace._client.assets.assert_called_once()
        call_kwargs = assets_namespace._client.assets.call_args[1]
        # Check that fields were passed (could be None for defaults)
        assert "project_id" in call_kwargs
        assert call_kwargs["project_id"] == "project_321"

    def test_list_assets_rejects_deprecated_filters(self, assets_namespace):
        """Ensure deprecated filter names now raise."""
        # Mock the legacy client method
        assets_namespace._client.assets.return_value = []

        # The namespace API doesn't accept these deprecated parameters
        # They should raise TypeError if passed as **kwargs
        with pytest.raises(TypeError):
            assets_namespace.list(
                project_id="project_ext",
                external_id_contains=["assetA", "assetB"],
            )

        with pytest.raises(TypeError):
            assets_namespace.list(
                project_id="project_ext",
                consensus_mark_gt=0.5,
            )

    def test_list_assets_resolves_step_name_filters(self, assets_namespace):
        """Ensure step_name_in filter is supported."""
        # Mock the legacy client method
        assets_namespace._client.assets.return_value = []

        # The namespace API accepts filters as a dict
        assets_namespace.list(
            project_id="project_steps",
            filter={"step_name_in": ["Review"]},
        )

        # Verify the legacy method was called
        assets_namespace._client.assets.assert_called_once()
        call_kwargs = assets_namespace._client.assets.call_args[1]
        # step_name_in should be passed as a kwarg
        assert call_kwargs.get("step_name_in") == ["Review"]

    def test_count_assets_rejects_deprecated_filters(self, assets_namespace):
        """Ensure deprecated count filters raise."""
        # Mock the legacy client method
        assets_namespace._client.count_assets.return_value = 0

        # The namespace API doesn't accept these deprecated parameters
        with pytest.raises(TypeError):
            assets_namespace.count(
                project_id="project_ext_count",
                external_id_contains=["legacy"],
            )

        with pytest.raises(TypeError):
            assets_namespace.count(
                project_id="project_ext_count",
                honeypot_mark_gt=0.2,
            )

    def test_list_assets_unknown_filter_raises(self, assets_namespace):
        """Ensure unexpected filter names raise a helpful error."""
        # Mock the legacy client method
        assets_namespace._client.assets.return_value = []

        # Unknown kwargs should raise TypeError
        with pytest.raises(TypeError):
            assets_namespace.list(project_id="project_unknown", unexpected="value")

    def test_create_image_assets(self, assets_namespace, mock_client):
        """Test create_image method delegates to client."""
        expected_result = {"id": "project_123", "asset_ids": ["asset1", "asset2"]}
        mock_client.append_many_to_dataset.return_value = expected_result

        result = assets_namespace.create_image(
            project_id="project_123",
            content_array=["https://example.com/image.png"],
            external_id_array=["ext1"],
        )

        assert result == expected_result
        mock_client.append_many_to_dataset.assert_called_once_with(
            project_id="project_123",
            content_array=["https://example.com/image.png"],
            external_id_array=["ext1"],
            json_metadata_array=None,
            disable_tqdm=None,
            wait_until_availability=True,
        )

    def test_delete_assets(self, assets_namespace, mock_client):
        """Test delete method delegates to client."""
        expected_result = {"id": "project_123"}
        mock_client.delete_many_from_dataset.return_value = expected_result

        result = assets_namespace.delete(asset_ids=["asset1", "asset2"])

        assert result == expected_result
        mock_client.delete_many_from_dataset.assert_called_once_with(
            asset_ids=["asset1", "asset2"], external_ids=None, project_id=""
        )

    def test_update_consensus_with_asset_id(self, assets_namespace, mock_client):
        """Test update_consensus method with asset_id."""
        mock_client.update_asset_consensus.return_value = True

        result = assets_namespace.update_consensus(
            project_id="project_123",
            asset_id="asset1",
            is_consensus=True,
        )

        assert result is True
        mock_client.update_asset_consensus.assert_called_once_with(
            project_id="project_123",
            is_consensus=True,
            asset_id="asset1",
            external_id=None,
        )

    def test_update_consensus_with_external_id(self, assets_namespace, mock_client):
        """Test update_consensus method with external_id."""
        mock_client.update_asset_consensus.return_value = True

        result = assets_namespace.update_consensus(
            project_id="project_123",
            external_id="ext_asset1",
            is_consensus=True,
        )

        assert result is True
        mock_client.update_asset_consensus.assert_called_once_with(
            project_id="project_123",
            is_consensus=True,
            asset_id=None,
            external_id="ext_asset1",
        )

    def test_update_consensus_deactivate(self, assets_namespace, mock_client):
        """Test update_consensus method to deactivate consensus."""
        mock_client.update_asset_consensus.return_value = False

        result = assets_namespace.update_consensus(
            project_id="project_123",
            asset_id="asset1",
            is_consensus=False,
        )

        assert result is False
        mock_client.update_asset_consensus.assert_called_once_with(
            project_id="project_123",
            is_consensus=False,
            asset_id="asset1",
            external_id=None,
        )


class TestAssetsNamespaceContractCompatibility:
    """Contract tests to ensure domain API matches legacy API behavior."""

    @pytest.fixture()
    def mock_client(self):
        """Create a mock Kili client."""
        client = MagicMock(spec=Kili)
        return client

    @pytest.fixture()
    def mock_gateway(self):
        """Create a mock KiliAPIGateway."""
        return MagicMock(spec=KiliAPIGateway)

    @pytest.fixture()
    def assets_namespace(self, mock_client, mock_gateway):
        """Create an AssetsNamespace instance."""
        return AssetsNamespace(mock_client, mock_gateway)

    def test_api_parity_create_image_vs_append_many(self, assets_namespace, mock_client):
        """Test that create_image() correctly delegates to append_many_to_dataset()."""
        # This test ensures that the domain API correctly passes parameters
        # to the underlying legacy API
        mock_client.append_many_to_dataset.return_value = {"id": "project", "asset_ids": []}

        # Test that image-relevant parameters are correctly passed through
        assets_namespace.create_image(
            project_id="test_project",
            content_array=["content"],
            external_id_array=["ext1"],
            json_metadata_array=[{"meta": "data"}],
            disable_tqdm=True,
            wait_until_availability=False,
            is_honeypot_array=[False],
        )

        # Verify that the legacy method was called with correct parameters
        mock_client.append_many_to_dataset.assert_called_once_with(
            project_id="test_project",
            content_array=["content"],
            external_id_array=["ext1"],
            json_metadata_array=[{"meta": "data"}],
            disable_tqdm=True,
            wait_until_availability=False,
            is_honeypot_array=[False],
        )

    def test_api_parity_delete_vs_delete_many(self, assets_namespace, mock_client):
        """Test that delete() calls have same signature as delete_many_from_dataset()."""
        mock_client.delete_many_from_dataset.return_value = {"id": "project"}

        assets_namespace.delete(
            asset_ids=["asset1", "asset2"], external_ids=None, project_id="test_project"
        )

        mock_client.delete_many_from_dataset.assert_called_once_with(
            asset_ids=["asset1", "asset2"], external_ids=None, project_id="test_project"
        )


if __name__ == "__main__":
    pytest.main([__file__])
