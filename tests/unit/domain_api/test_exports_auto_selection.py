"""Unit tests for automatic export type selection based on project workflow version."""

from unittest.mock import MagicMock

import pytest

from kili.domain_api.exports import ExportNamespace


@pytest.fixture()
def mock_client():
    """Create a mock Kili client."""
    client = MagicMock()
    client.export_labels = MagicMock(return_value=[])
    return client


@pytest.fixture()
def mock_gateway():
    """Create a mock KiliAPIGateway."""
    return MagicMock()


@pytest.fixture()
def export_namespace(mock_client, mock_gateway):
    """Create an ExportNamespace instance with mocked dependencies."""
    return ExportNamespace(mock_client, mock_gateway)


class TestGetOptimalExportType:
    """Test the _get_optimal_export_type method."""

    def test_workflow_v1_returns_latest(self, export_namespace):
        """Test that Workflow V1 projects return 'latest' export type."""
        result = export_namespace._get_optimal_export_type("V1")
        assert result == "latest"

    def test_workflow_v2_returns_latest_from_last_step(self, export_namespace):
        """Test that Workflow V2 projects return 'latest_from_last_step' export type."""
        result = export_namespace._get_optimal_export_type("V2")
        assert result == "latest_from_last_step"

    def test_project_not_found_returns_latest(self, export_namespace):
        """Test that when project is not found, it defaults to 'latest'."""
        result = export_namespace._get_optimal_export_type(None)
        assert result == "latest"

    def test_project_without_workflow_version_returns_latest(self, export_namespace):
        """Test that projects without workflowVersion field default to 'latest'."""
        result = export_namespace._get_optimal_export_type(None)
        assert result == "latest"


class TestKiliExport:
    """Test the kili() export method with auto-selection."""

    @pytest.mark.parametrize(
        "workflow_version,expected_export_type",
        [
            ("V1", "latest"),
            ("V2", "latest_from_last_step"),
        ],
    )
    def test_auto_selects_export_type_based_on_workflow(
        self, export_namespace, mock_client, mock_gateway, workflow_version, expected_export_type
    ):
        """Test that export type is auto-selected based on project workflow version."""
        # Mock project
        mock_gateway.get_project.return_value = {
            "id": "test-project",
            "workflowVersion": workflow_version,
        }

        # Call export without specifying export_type
        export_namespace.kili(
            project_id="test-project",
            output_path="/tmp/export.zip",
        )

        # Verify the client was called with the correct export_type
        mock_client.export_labels.assert_called_once()
        call_args = mock_client.export_labels.call_args
        assert call_args.kwargs["export_type"] == expected_export_type

    def test_explicit_export_type_overrides_auto_selection(
        self, export_namespace, mock_client, mock_gateway
    ):
        """Test that explicitly provided export_type overrides auto-selection."""
        # Mock V2 project (would normally use latest_from_last_step)
        mock_gateway.get_project.return_value = {
            "id": "test-project",
            "workflowVersion": "V2",
        }

        # Call export with explicit export_type
        export_namespace.kili(
            project_id="test-project",
            output_path="/tmp/export.zip",
            export_type="normal",  # Override auto-selection
        )

        # Verify the explicit type was used
        mock_client.export_labels.assert_called_once()
        call_args = mock_client.export_labels.call_args
        assert call_args.kwargs["export_type"] == "normal"

        # Verify get_project was called only once (for validation, not for auto-selection)
        mock_gateway.get_project.assert_called_once()


class TestAllExportFormats:
    """Test auto-selection for all export formats."""

    @pytest.mark.parametrize(
        "workflow_version,expected_export_type",
        [
            ("V1", "latest"),
            ("V2", "latest_from_last_step"),
        ],
    )
    @pytest.mark.parametrize(
        "export_method,format_name",
        [
            ("kili", "kili"),
            ("coco", "coco"),
            ("yolo_v4", "yolo_v4"),
            ("yolo_v5", "yolo_v5"),
            ("yolo_v7", "yolo_v7"),
            ("yolo_v8", "yolo_v8"),
            ("pascal_voc", "pascal_voc"),
            ("geojson", "geojson"),
        ],
    )
    def test_all_formats_auto_select_export_type(
        self,
        export_namespace,
        mock_client,
        mock_gateway,
        workflow_version,
        expected_export_type,
        export_method,
        format_name,
    ):
        """Test that all export formats correctly auto-select export type."""
        # Mock project
        mock_gateway.get_project.return_value = {
            "id": "test-project",
            "workflowVersion": workflow_version,
        }

        # Get the export method
        method = getattr(export_namespace, export_method)

        # Call the method without explicit export_type
        method(
            project_id="test-project",
            output_path="/tmp/export.zip",
        )

        # Verify the client was called with correct export_type and format
        mock_client.export_labels.assert_called_once()
        call_args = mock_client.export_labels.call_args
        assert call_args.kwargs["export_type"] == expected_export_type
        assert call_args.kwargs["fmt"] == format_name


class TestExportTypeFieldSelection:
    """Test that the correct GraphQL fields are selected based on export type."""

    def test_v1_project_uses_latest_label_field(self, export_namespace, mock_client, mock_gateway):
        """Test that V1 projects query the latestLabel (singular) field."""
        # Mock V1 project
        mock_gateway.get_project.return_value = {
            "id": "v1-project",
            "workflowVersion": "V1",
        }

        export_namespace.kili(
            project_id="v1-project",
            output_path="/tmp/export.zip",
        )

        # The export should use "latest" type which queries latestLabel field
        call_args = mock_client.export_labels.call_args
        assert call_args.kwargs["export_type"] == "latest"

    def test_v2_project_uses_latest_labels_field(self, export_namespace, mock_client, mock_gateway):
        """Test that V2 projects query the latestLabels (plural) field."""
        # Mock V2 project
        mock_gateway.get_project.return_value = {
            "id": "v2-project",
            "workflowVersion": "V2",
        }

        export_namespace.kili(
            project_id="v2-project",
            output_path="/tmp/export.zip",
        )

        # The export should use "latest_from_last_step" type which queries latestLabels field
        call_args = mock_client.export_labels.call_args
        assert call_args.kwargs["export_type"] == "latest_from_last_step"


class TestBackwardCompatibility:
    """Test backward compatibility with existing code."""

    def test_existing_code_with_explicit_export_type_still_works(
        self, export_namespace, mock_client, mock_gateway
    ):
        """Test that existing code explicitly specifying export_type still works."""
        # Mock V1 project to allow "normal" export type
        mock_gateway.get_project.return_value = {
            "id": "any-project",
            "workflowVersion": "V1",
        }

        # Existing code that explicitly specifies export_type
        export_namespace.kili(
            project_id="any-project",
            output_path="/tmp/export.zip",
            export_type="normal",
        )

        # Should work
        mock_client.export_labels.assert_called_once()
        call_args = mock_client.export_labels.call_args
        assert call_args.kwargs["export_type"] == "normal"

    @pytest.mark.parametrize(
        "explicit_export_type",
        [
            "latest",
            "normal",
        ],
    )
    def test_compatible_export_types_work_with_v1(
        self, export_namespace, mock_client, mock_gateway, explicit_export_type
    ):
        """Test that compatible export types work with V1 projects."""
        mock_gateway.get_project.return_value = {
            "id": "v1-project",
            "workflowVersion": "V1",
        }

        export_namespace.kili(
            project_id="v1-project",
            output_path="/tmp/export.zip",
            export_type=explicit_export_type,
        )

        mock_client.export_labels.assert_called_once()
        call_args = mock_client.export_labels.call_args
        assert call_args.kwargs["export_type"] == explicit_export_type


class TestExportTypeValidation:
    """Test validation of export type compatibility with workflow versions."""

    @pytest.mark.parametrize(
        "incompatible_export_type",
        [
            "latest_from_last_step",
            "latest_from_all_steps",
        ],
    )
    def test_v1_project_rejects_incompatible_export_types(
        self, export_namespace, mock_client, mock_gateway, incompatible_export_type
    ):
        """Test that V1 projects reject export types designed for V2."""
        # Mock V1 project
        mock_gateway.get_project.return_value = {
            "id": "v1-project",
            "workflowVersion": "V1",
        }

        # Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            export_namespace.kili(
                project_id="v1-project",
                output_path="/tmp/export.zip",
                export_type=incompatible_export_type,
            )

        # Verify error message is helpful
        error_message = str(exc_info.value)
        assert incompatible_export_type in error_message
        assert "Workflow V1" in error_message
        assert "not compatible" in error_message
        assert "Workflow V2" in error_message

        # Should not have called export_labels
        mock_client.export_labels.assert_not_called()

        # Should have fetched workflow version only once
        mock_gateway.get_project.assert_called_once()

    @pytest.mark.parametrize(
        "export_type",
        [
            "latest_from_last_step",
            "latest_from_all_steps",
        ],
    )
    def test_v2_project_allows_all_export_types(
        self, export_namespace, mock_client, mock_gateway, export_type
    ):
        """Test that V2 projects can use any export type."""
        # Mock V2 project
        mock_gateway.get_project.return_value = {
            "id": "v2-project",
            "workflowVersion": "V2",
        }

        # Should work fine
        export_namespace.kili(
            project_id="v2-project",
            output_path="/tmp/export.zip",
            export_type=export_type,
        )

        # Should have called export_labels
        mock_client.export_labels.assert_called_once()
        call_args = mock_client.export_labels.call_args
        assert call_args.kwargs["export_type"] == export_type

        # Should have fetched workflow version only once
        mock_gateway.get_project.assert_called_once()

    def test_validation_with_project_not_found(self, export_namespace, mock_client, mock_gateway):
        """Test that validation fails open when project is not found."""
        # Mock project not found
        mock_gateway.get_project.return_value = None

        # Should not raise error (fail open)
        export_namespace.kili(
            project_id="non-existent-project",
            output_path="/tmp/export.zip",
            export_type="latest_from_last_step",
        )

        # Should have proceeded with the export
        mock_client.export_labels.assert_called_once()

        # Should have fetched workflow version only once
        mock_gateway.get_project.assert_called_once()

    @pytest.mark.parametrize(
        "export_method",
        [
            "coco",
            "yolo_v4",
            "yolo_v5",
            "pascal_voc",
            "geojson",
        ],
    )
    def test_all_formats_validate_export_type(
        self, export_namespace, mock_client, mock_gateway, export_method
    ):
        """Test that all export formats validate export type compatibility."""
        # Mock V1 project
        mock_gateway.get_project.return_value = {
            "id": "v1-project",
            "workflowVersion": "V1",
        }

        method = getattr(export_namespace, export_method)

        # Should raise ValueError for incompatible export type
        with pytest.raises(ValueError) as exc_info:
            method(
                project_id="v1-project",
                output_path="/tmp/export.zip",
                export_type="latest_from_last_step",
            )

        # Verify error message
        assert "latest_from_last_step" in str(exc_info.value)
        assert "Workflow V1" in str(exc_info.value)

        # Should have fetched workflow version only once
        mock_gateway.get_project.assert_called_once()
