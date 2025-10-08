"""Unit tests for the AssetsNamespace domain API."""

from unittest.mock import MagicMock, patch

import pytest

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.client import Kili
from kili.domain_api.assets import (
    AssetsNamespace,
    ExternalIdsNamespace,
    MetadataNamespace,
    WorkflowNamespace,
    WorkflowStepNamespace,
)


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
        return client

    @pytest.fixture()
    def mock_gateway(self):
        """Create a mock KiliAPIGateway."""
        return MagicMock(spec=KiliAPIGateway)

    @pytest.fixture()
    def assets_namespace(self, mock_client, mock_gateway):
        """Create an AssetsNamespace instance."""
        return AssetsNamespace(mock_client, mock_gateway)

    def test_init(self, mock_client, mock_gateway):
        """Test AssetsNamespace initialization."""
        namespace = AssetsNamespace(mock_client, mock_gateway)
        assert namespace.domain_name == "assets"
        assert namespace.client == mock_client
        assert namespace.gateway == mock_gateway

    def test_workflow_property(self, assets_namespace):
        """Test workflow property returns WorkflowNamespace."""
        workflow = assets_namespace.workflow
        assert isinstance(workflow, WorkflowNamespace)
        # Test caching
        assert assets_namespace.workflow is workflow

    def test_external_ids_property(self, assets_namespace):
        """Test external_ids property returns ExternalIdsNamespace."""
        external_ids = assets_namespace.external_ids
        assert isinstance(external_ids, ExternalIdsNamespace)
        # Test caching
        assert assets_namespace.external_ids is external_ids

    def test_metadata_property(self, assets_namespace):
        """Test metadata property returns MetadataNamespace."""
        metadata = assets_namespace.metadata
        assert isinstance(metadata, MetadataNamespace)
        # Test caching
        assert assets_namespace.metadata is metadata


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
        with patch("kili.domain_api.assets.AssetUseCases") as mock_asset_use_cases, patch(
            "kili.domain_api.assets.ProjectUseCases"
        ) as mock_project_use_cases:
            mock_use_case_instance = MagicMock()
            mock_asset_use_cases.return_value = mock_use_case_instance
            mock_use_case_instance.list_assets.return_value = iter(
                [
                    {"id": "asset1", "externalId": "ext1"},
                    {"id": "asset2", "externalId": "ext2"},
                ]
            )
            mock_project_use_cases.return_value.get_project_steps_and_version.return_value = (
                [],
                "V2",
            )

            result = assets_namespace.list(project_id="project_123")

            # Should return a generator
            assert hasattr(result, "__iter__")
            assets_list = list(result)
            assert len(assets_list) == 2
            assert assets_list[0].id == "asset1"

            mock_asset_use_cases.assert_called_once_with(assets_namespace.gateway)
            mock_project_use_cases.assert_called_once_with(assets_namespace.gateway)
            mock_use_case_instance.list_assets.assert_called_once()

    def test_list_assets_as_list(self, assets_namespace):
        """Test list method returns list when as_generator=False."""
        with patch("kili.domain_api.assets.AssetUseCases") as mock_asset_use_cases, patch(
            "kili.domain_api.assets.ProjectUseCases"
        ) as mock_project_use_cases:
            mock_use_case_instance = MagicMock()
            mock_asset_use_cases.return_value = mock_use_case_instance
            mock_use_case_instance.list_assets.return_value = iter(
                [
                    {"id": "asset1", "externalId": "ext1"},
                    {"id": "asset2", "externalId": "ext2"},
                ]
            )
            mock_project_use_cases.return_value.get_project_steps_and_version.return_value = (
                [],
                "V2",
            )

            result = assets_namespace.list(project_id="project_123", as_generator=False)

            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0].id == "asset1"

    def test_count_assets(self, assets_namespace):
        """Test count method."""
        with patch("kili.domain_api.assets.AssetUseCases") as mock_asset_use_cases, patch(
            "kili.domain_api.assets.ProjectUseCases"
        ) as mock_project_use_cases:
            mock_use_case_instance = MagicMock()
            mock_asset_use_cases.return_value = mock_use_case_instance
            mock_use_case_instance.count_assets.return_value = 42
            mock_project_use_cases.return_value.get_project_steps_and_version.return_value = (
                [],
                "V2",
            )

            result = assets_namespace.count(project_id="project_123")

            assert result == 42
            mock_asset_use_cases.assert_called_once_with(assets_namespace.gateway)
            mock_use_case_instance.count_assets.assert_called_once()

    def test_list_assets_uses_project_workflow_defaults(self, assets_namespace):
        """Ensure default fields follow project workflow version."""
        with patch("kili.domain_api.assets.AssetUseCases") as mock_asset_use_cases, patch(
            "kili.domain_api.assets.ProjectUseCases"
        ) as mock_project_use_cases:
            mock_use_case_instance = MagicMock()
            mock_asset_use_cases.return_value = mock_use_case_instance
            mock_use_case_instance.list_assets.return_value = iter([])
            mock_project_use_cases.return_value.get_project_steps_and_version.return_value = (
                [],
                "V1",
            )

            assets_namespace.list(project_id="project_321")

            _, kwargs = mock_use_case_instance.list_assets.call_args
            fields = kwargs["fields"]
            assert "status" in fields
            assert all(not f.startswith("currentStep.") for f in fields)

    def test_list_assets_rejects_deprecated_filters(self, assets_namespace):
        """Ensure deprecated filter names now raise."""
        with patch("kili.domain_api.assets.ProjectUseCases") as mock_project_use_cases:
            mock_project_use_cases.return_value.get_project_steps_and_version.return_value = (
                [],
                "V2",
            )

            with pytest.raises(TypeError):
                assets_namespace.list(
                    project_id="project_ext",
                    external_id_contains=["assetA", "assetB"],
                    as_generator=False,
                )

            with pytest.raises(TypeError):
                assets_namespace.list(
                    project_id="project_ext",
                    consensus_mark_gt=0.5,
                )

    def test_list_assets_resolves_step_name_filters(self, assets_namespace):
        """Ensure step_name_in resolves to step IDs in V2 workflow."""
        with patch("kili.domain_api.assets.AssetUseCases") as mock_asset_use_cases, patch(
            "kili.domain_api.assets.ProjectUseCases"
        ) as mock_project_use_cases:
            mock_use_case_instance = MagicMock()
            mock_asset_use_cases.return_value = mock_use_case_instance
            mock_use_case_instance.list_assets.return_value = iter([])
            mock_project_use_cases.return_value.get_project_steps_and_version.return_value = (
                [{"id": "step-1", "name": "Review"}],
                "V2",
            )

            assets_namespace.list(
                project_id="project_steps",
                step_name_in=["Review"],
                as_generator=False,
            )

            _, kwargs = mock_use_case_instance.list_assets.call_args
            filters = kwargs["filters"]
            assert filters.step_id_in == ["step-1"]

    def test_count_assets_rejects_deprecated_filters(self, assets_namespace):
        """Ensure deprecated count filters raise."""
        with patch("kili.domain_api.assets.ProjectUseCases") as mock_project_use_cases:
            mock_project_use_cases.return_value.get_project_steps_and_version.return_value = (
                [],
                "V2",
            )

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
        with patch("kili.domain_api.assets.AssetUseCases") as mock_asset_use_cases, patch(
            "kili.domain_api.assets.ProjectUseCases"
        ) as mock_project_use_cases:
            mock_use_case_instance = MagicMock()
            mock_asset_use_cases.return_value = mock_use_case_instance
            mock_use_case_instance.list_assets.return_value = iter([])
            mock_project_use_cases.return_value.get_project_steps_and_version.return_value = (
                [],
                "V2",
            )

            with pytest.raises(TypeError):
                assets_namespace.list(project_id="project_unknown", unexpected="value")

    def test_create_assets(self, assets_namespace, mock_client):
        """Test create method delegates to client."""
        expected_result = {"id": "project_123", "asset_ids": ["asset1", "asset2"]}
        mock_client.append_many_to_dataset.return_value = expected_result

        result = assets_namespace.create(
            project_id="project_123",
            content_array=["https://example.com/image.png"],
            external_id_array=["ext1"],
        )

        assert result.id == "project_123"
        assert result.asset_ids == ["asset1", "asset2"]
        mock_client.append_many_to_dataset.assert_called_once_with(
            project_id="project_123",
            content_array=["https://example.com/image.png"],
            multi_layer_content_array=None,
            external_id_array=["ext1"],
            is_honeypot_array=None,
            json_content_array=None,
            json_metadata_array=None,
            disable_tqdm=None,
            wait_until_availability=True,
            from_csv=None,
            csv_separator=",",
        )

    def test_delete_assets(self, assets_namespace, mock_client):
        """Test delete method delegates to client."""
        expected_result = {"id": "project_123"}
        mock_client.delete_many_from_dataset.return_value = expected_result

        result = assets_namespace.delete(asset_ids=["asset1", "asset2"])

        assert result.id == "project_123"
        mock_client.delete_many_from_dataset.assert_called_once_with(
            asset_ids=["asset1", "asset2"], external_ids=None, project_id=None
        )

    def test_update_assets(self, assets_namespace, mock_client):
        """Test update method delegates to client."""
        expected_result = [{"id": "asset1"}, {"id": "asset2"}]
        mock_client.update_properties_in_assets.return_value = expected_result

        result = assets_namespace.update(
            asset_ids=["asset1", "asset2"],
            priorities=[1, 2],
            json_metadatas=[{"key": "value1"}, {"key": "value2"}],
        )

        assert result.ids == ["asset1", "asset2"]
        mock_client.update_properties_in_assets.assert_called_once_with(
            asset_ids=["asset1", "asset2"],
            external_ids=None,
            project_id=None,
            priorities=[1, 2],
            json_metadatas=[{"key": "value1"}, {"key": "value2"}],
            consensus_marks=None,
            honeypot_marks=None,
            contents=None,
            json_contents=None,
            is_used_for_consensus_array=None,
            is_honeypot_array=None,
        )


class TestWorkflowNamespace:
    """Test cases for WorkflowNamespace."""

    @pytest.fixture()
    def mock_client(self):
        """Create a mock Kili client."""
        client = MagicMock(spec=Kili)
        client.assign_assets_to_labelers = MagicMock()
        return client

    @pytest.fixture()
    def mock_gateway(self):
        """Create a mock KiliAPIGateway."""
        return MagicMock(spec=KiliAPIGateway)

    @pytest.fixture()
    def assets_namespace(self, mock_client, mock_gateway):
        """Create an AssetsNamespace instance."""
        return AssetsNamespace(mock_client, mock_gateway)

    @pytest.fixture()
    def workflow_namespace(self, assets_namespace):
        """Create a WorkflowNamespace instance."""
        return WorkflowNamespace(assets_namespace)

    def test_init(self, assets_namespace):
        """Test WorkflowNamespace initialization."""
        workflow = WorkflowNamespace(assets_namespace)
        assert workflow._assets_namespace == assets_namespace

    def test_step_property(self, workflow_namespace):
        """Test step property returns WorkflowStepNamespace."""
        step = workflow_namespace.step
        assert isinstance(step, WorkflowStepNamespace)
        # Test caching
        assert workflow_namespace.step is step

    def test_assign_delegates_to_client(self, workflow_namespace, mock_client):
        """Test assign method delegates to client."""
        expected_result = [{"id": "asset1"}, {"id": "asset2"}]
        mock_client.assign_assets_to_labelers.return_value = expected_result

        result = workflow_namespace.assign(
            asset_ids=["asset1", "asset2"], to_be_labeled_by_array=[["user1"], ["user2"]]
        )

        assert result.ids == ["asset1", "asset2"]
        mock_client.assign_assets_to_labelers.assert_called_once_with(
            asset_ids=["asset1", "asset2"],
            external_ids=None,
            project_id=None,
            to_be_labeled_by_array=[["user1"], ["user2"]],
        )


class TestWorkflowStepNamespace:
    """Test cases for WorkflowStepNamespace."""

    @pytest.fixture()
    def mock_client(self):
        """Create a mock Kili client."""
        client = MagicMock(spec=Kili)
        client.send_back_to_queue = MagicMock()
        client.add_to_review = MagicMock()
        return client

    @pytest.fixture()
    def mock_gateway(self):
        """Create a mock KiliAPIGateway."""
        return MagicMock(spec=KiliAPIGateway)

    @pytest.fixture()
    def assets_namespace(self, mock_client, mock_gateway):
        """Create an AssetsNamespace instance."""
        return AssetsNamespace(mock_client, mock_gateway)

    @pytest.fixture()
    def workflow_step_namespace(self, assets_namespace):
        """Create a WorkflowStepNamespace instance."""
        return WorkflowStepNamespace(assets_namespace)

    def test_init(self, assets_namespace):
        """Test WorkflowStepNamespace initialization."""
        step = WorkflowStepNamespace(assets_namespace)
        assert step._assets_namespace == assets_namespace

    def test_invalidate_delegates_to_client(self, workflow_step_namespace, mock_client):
        """Test invalidate method delegates to client send_back_to_queue."""
        expected_result = {"id": "project_123", "asset_ids": ["asset1", "asset2"]}
        mock_client.send_back_to_queue.return_value = expected_result

        result = workflow_step_namespace.invalidate(asset_ids=["asset1", "asset2"])

        assert result.id == "project_123"
        assert result.asset_ids == ["asset1", "asset2"]
        mock_client.send_back_to_queue.assert_called_once_with(
            asset_ids=["asset1", "asset2"], external_ids=None, project_id=None
        )

    def test_next_delegates_to_client(self, workflow_step_namespace, mock_client):
        """Test next method delegates to client add_to_review."""
        expected_result = {"id": "project_123", "asset_ids": ["asset1", "asset2"]}
        mock_client.add_to_review.return_value = expected_result

        result = workflow_step_namespace.next(asset_ids=["asset1", "asset2"])

        assert result.id == "project_123"
        assert result.asset_ids == ["asset1", "asset2"]
        mock_client.add_to_review.assert_called_once_with(
            asset_ids=["asset1", "asset2"], external_ids=None, project_id=None
        )


class TestExternalIdsNamespace:
    """Test cases for ExternalIdsNamespace."""

    @pytest.fixture()
    def mock_client(self):
        """Create a mock Kili client."""
        client = MagicMock(spec=Kili)
        client.change_asset_external_ids = MagicMock()
        return client

    @pytest.fixture()
    def mock_gateway(self):
        """Create a mock KiliAPIGateway."""
        return MagicMock(spec=KiliAPIGateway)

    @pytest.fixture()
    def assets_namespace(self, mock_client, mock_gateway):
        """Create an AssetsNamespace instance."""
        return AssetsNamespace(mock_client, mock_gateway)

    @pytest.fixture()
    def external_ids_namespace(self, assets_namespace):
        """Create an ExternalIdsNamespace instance."""
        return ExternalIdsNamespace(assets_namespace)

    def test_init(self, assets_namespace):
        """Test ExternalIdsNamespace initialization."""
        external_ids = ExternalIdsNamespace(assets_namespace)
        assert external_ids._assets_namespace == assets_namespace

    def test_update_delegates_to_client(self, external_ids_namespace, mock_client):
        """Test update method delegates to client."""
        expected_result = [{"id": "asset1"}, {"id": "asset2"}]
        mock_client.change_asset_external_ids.return_value = expected_result

        result = external_ids_namespace.update(
            new_external_ids=["new_ext1", "new_ext2"], asset_ids=["asset1", "asset2"]
        )

        assert result.ids == ["asset1", "asset2"]
        mock_client.change_asset_external_ids.assert_called_once_with(
            new_external_ids=["new_ext1", "new_ext2"],
            asset_ids=["asset1", "asset2"],
            external_ids=None,
            project_id=None,
        )


class TestMetadataNamespace:
    """Test cases for MetadataNamespace."""

    @pytest.fixture()
    def mock_client(self):
        """Create a mock Kili client."""
        client = MagicMock(spec=Kili)
        client.add_metadata = MagicMock()
        client.set_metadata = MagicMock()
        return client

    @pytest.fixture()
    def mock_gateway(self):
        """Create a mock KiliAPIGateway."""
        return MagicMock(spec=KiliAPIGateway)

    @pytest.fixture()
    def assets_namespace(self, mock_client, mock_gateway):
        """Create an AssetsNamespace instance."""
        return AssetsNamespace(mock_client, mock_gateway)

    @pytest.fixture()
    def metadata_namespace(self, assets_namespace):
        """Create a MetadataNamespace instance."""
        return MetadataNamespace(assets_namespace)

    def test_init(self, assets_namespace):
        """Test MetadataNamespace initialization."""
        metadata = MetadataNamespace(assets_namespace)
        assert metadata._assets_namespace == assets_namespace

    def test_add_delegates_to_client(self, metadata_namespace, mock_client):
        """Test add method delegates to client."""
        expected_result = [{"id": "asset1"}, {"id": "asset2"}]
        mock_client.add_metadata.return_value = expected_result

        result = metadata_namespace.add(
            json_metadata=[{"key1": "value1"}, {"key2": "value2"}],
            project_id="project_123",
            asset_ids=["asset1", "asset2"],
        )

        assert result.ids == ["asset1", "asset2"]
        mock_client.add_metadata.assert_called_once_with(
            json_metadata=[{"key1": "value1"}, {"key2": "value2"}],
            project_id="project_123",
            asset_ids=["asset1", "asset2"],
            external_ids=None,
        )

    def test_set_delegates_to_client(self, metadata_namespace, mock_client):
        """Test set method delegates to client."""
        expected_result = [{"id": "asset1"}, {"id": "asset2"}]
        mock_client.set_metadata.return_value = expected_result

        result = metadata_namespace.set(
            json_metadata=[{"key1": "value1"}, {"key2": "value2"}],
            project_id="project_123",
            asset_ids=["asset1", "asset2"],
        )

        assert result.ids == ["asset1", "asset2"]
        mock_client.set_metadata.assert_called_once_with(
            json_metadata=[{"key1": "value1"}, {"key2": "value2"}],
            project_id="project_123",
            asset_ids=["asset1", "asset2"],
            external_ids=None,
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

    def test_api_parity_create_vs_append_many(self, assets_namespace, mock_client):
        """Test that create() calls have same signature as append_many_to_dataset()."""
        # This test ensures that the domain API maintains the same interface
        # as the legacy API for compatibility
        mock_client.append_many_to_dataset.return_value = {"id": "project", "asset_ids": []}

        # Test that all parameters are correctly passed through
        assets_namespace.create(
            project_id="test_project",
            content_array=["content"],
            multi_layer_content_array=None,
            external_id_array=["ext1"],
            is_honeypot_array=[False],
            json_content_array=None,
            json_metadata_array=[{"meta": "data"}],
            disable_tqdm=True,
            wait_until_availability=False,
            from_csv=None,
            csv_separator=";",
        )

        # Verify that the legacy method was called with exact same parameters
        mock_client.append_many_to_dataset.assert_called_once_with(
            project_id="test_project",
            content_array=["content"],
            multi_layer_content_array=None,
            external_id_array=["ext1"],
            is_honeypot_array=[False],
            json_content_array=None,
            json_metadata_array=[{"meta": "data"}],
            disable_tqdm=True,
            wait_until_availability=False,
            from_csv=None,
            csv_separator=";",
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

    def test_api_parity_update_vs_update_properties(self, assets_namespace, mock_client):
        """Test that update() calls have same signature as update_properties_in_assets()."""
        mock_client.update_properties_in_assets.return_value = [{"id": "asset1"}]

        assets_namespace.update(
            asset_ids=["asset1"],
            external_ids=None,
            project_id="test_project",
            priorities=[1],
            json_metadatas=[{"key": "value"}],
            consensus_marks=[0.8],
            honeypot_marks=[0.9],
            contents=["new_content"],
            json_contents=["new_json"],
            is_used_for_consensus_array=[True],
            is_honeypot_array=[False],
        )

        mock_client.update_properties_in_assets.assert_called_once_with(
            asset_ids=["asset1"],
            external_ids=None,
            project_id="test_project",
            priorities=[1],
            json_metadatas=[{"key": "value"}],
            consensus_marks=[0.8],
            honeypot_marks=[0.9],
            contents=["new_content"],
            json_contents=["new_json"],
            is_used_for_consensus_array=[True],
            is_honeypot_array=[False],
        )


if __name__ == "__main__":
    pytest.main([__file__])
