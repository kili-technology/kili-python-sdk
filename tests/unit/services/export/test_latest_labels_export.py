"""Integration tests for latest_from_last_step and latest_from_all_steps export types."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import pytest
import pytest_mock

from kili.services.export import AbstractExporter, export_labels
from tests.fakes.fake_kili import FakeKili, mocked_kili_api_gateway_get_project


def mocked_AssetQuery_with_latestLabels(filters, fields, options: dict):
    """Mock asset query that returns assets with latestLabels or labels based on fields requested."""
    # Check if we're requesting labels or latestLabels fields
    use_labels_field = any("labels." in field for field in fields)
    use_latest_labels_field = any("latestLabels." in field for field in fields)

    # Common label data for both labelers
    labels_data = [
        {
            "id": "label-labeler-1",
            "author": {
                "id": "user-1",
                "email": "labeler1@example.com",
                "firstname": "John",
                "lastname": "Doe",
            },
            "jsonResponse": {
                "JOB_0": {
                    "annotations": [
                        {
                            "boundingPoly": [
                                {
                                    "normalizedVertices": [
                                        {"x": 0.1, "y": 0.1},
                                        {"x": 0.1, "y": 0.3},
                                        {"x": 0.3, "y": 0.1},
                                        {"x": 0.3, "y": 0.3},
                                    ]
                                }
                            ],
                            "categories": [{"name": "OBJECT_A", "confidence": 100}],
                            "mid": "annotation-1",
                        }
                    ]
                }
            },
            "labelType": "DEFAULT",
            "isLastForStep": True,
            "isLatestLabelForUser": True,
            "isSentBackToQueue": False,
            "createdAt": "2024-01-01T10:00:00Z",
            "modelName": None,
        },
        {
            "id": "label-labeler-2",
            "author": {
                "id": "user-2",
                "email": "labeler2@example.com",
                "firstname": "Jane",
                "lastname": "Smith",
            },
            "jsonResponse": {
                "JOB_0": {
                    "annotations": [
                        {
                            "boundingPoly": [
                                {
                                    "normalizedVertices": [
                                        {"x": 0.2, "y": 0.2},
                                        {"x": 0.2, "y": 0.4},
                                        {"x": 0.4, "y": 0.2},
                                        {"x": 0.4, "y": 0.4},
                                    ]
                                }
                            ],
                            "categories": [{"name": "OBJECT_B", "confidence": 100}],
                            "mid": "annotation-2",
                        }
                    ]
                }
            },
            "labelType": "DEFAULT",
            "isLastForStep": True,
            "isLatestLabelForUser": True,
            "isSentBackToQueue": False,
            "createdAt": "2024-01-01T10:05:00Z",
            "modelName": None,
        },
    ]

    # Asset with multiple labels from different labelers (consensus scenario)
    asset_with_consensus = {
        "id": "asset-consensus-1",
        "externalId": "consensus_asset_1",
        "content": "https://example.com/consensus.jpg",
        "jsonMetadata": {},
        "status": "DONE",
    }

    # Add the appropriate field based on what's requested
    if use_labels_field:
        asset_with_consensus["labels"] = labels_data
    elif use_latest_labels_field:
        asset_with_consensus["latestLabels"] = labels_data

    return [asset_with_consensus]


def mocked_AssetQuery_count_with_latestLabels(where):
    """Mock asset count query."""
    return 1


@pytest.mark.parametrize(
    ("export_type", "test_name"),
    [
        (
            "latest_from_last_step",
            "Export with latest_from_last_step should include multiple labels (consensus)",
        ),
        ("latest_from_all_steps", "Export with latest_from_all_steps should include all labels"),
    ],
)
def test_export_with_latest_labels(mocker: pytest_mock.MockerFixture, export_type, test_name):
    """Integration test for exporting with new export types that use latestLabels."""
    mocker.patch.object(AbstractExporter, "_check_and_ensure_asset_access", return_value=None)

    with TemporaryDirectory() as export_folder, TemporaryDirectory() as extract_folder:
        path_zipfile = Path(export_folder) / "export.zip"
        path_zipfile.parent.mkdir(parents=True, exist_ok=True)

        fake_kili = FakeKili()
        fake_kili.kili_api_gateway.list_assets.side_effect = mocked_AssetQuery_with_latestLabels
        fake_kili.kili_api_gateway.count_assets.side_effect = (
            mocked_AssetQuery_count_with_latestLabels
        )
        fake_kili.kili_api_gateway.get_project.side_effect = mocked_kili_api_gateway_get_project

        export_labels(
            fake_kili,  # type: ignore
            asset_ids=[],
            project_id="object_detection",
            export_type=export_type,
            label_format="raw",
            split_option="merged",
            single_file=False,
            output_file=str(path_zipfile),
            disable_tqdm=True,
            log_level="INFO",
            with_assets=False,
            annotation_modifier=None,
            asset_filter_kwargs=None,
            normalized_coordinates=None,
            label_type_in=None,
            include_sent_back_labels=None,
        )

        # Extract and verify the export
        with ZipFile(path_zipfile, "r") as zip_file:
            zip_file.extractall(extract_folder)

        # Read the exported label file
        label_file = Path(extract_folder) / "labels" / "consensus_asset_1.json"
        assert label_file.exists(), f"Label file should exist for {export_type}"

        with open(label_file) as f:
            exported_data = json.load(f)

        # Determine which field to check based on export type
        labels_field = "labels" if export_type == "latest_from_all_steps" else "latestLabels"

        # Verify that we have both labels exported (from both labelers)
        assert labels_field in exported_data, f"Should have {labels_field} field for {export_type}"
        assert (
            len(exported_data[labels_field]) == 2
        ), f"Should have 2 labels from 2 labelers for {export_type}"

        # Verify author names were properly concatenated
        authors = [label["author"]["name"] for label in exported_data[labels_field]]
        assert "John Doe" in authors, f"Should have John Doe as author for {export_type}"
        assert "Jane Smith" in authors, f"Should have Jane Smith as author for {export_type}"

        # Verify both annotations are present
        label_1 = next(l for l in exported_data[labels_field] if l["author"]["firstname"] == "John")
        label_2 = next(l for l in exported_data[labels_field] if l["author"]["firstname"] == "Jane")

        assert (
            label_1["jsonResponse"]["JOB_0"]["annotations"][0]["categories"][0]["name"]
            == "OBJECT_A"
        )
        assert (
            label_2["jsonResponse"]["JOB_0"]["annotations"][0]["categories"][0]["name"]
            == "OBJECT_B"
        )

        # Verify README file exists
        readme_file = Path(extract_folder) / "README.kili.txt"
        assert readme_file.exists(), "README file should exist"


def test_export_fields_fetched_for_latest_labels(mocker: pytest_mock.MockerFixture):
    """Test that the correct fields are fetched when using new export types."""
    mocker.patch.object(AbstractExporter, "_check_and_ensure_asset_access", return_value=None)

    # Track which fields are requested
    fields_requested = []

    def capture_fields(filters, fields, options):
        fields_requested.append(fields)
        return mocked_AssetQuery_with_latestLabels(filters, fields, options)

    with TemporaryDirectory() as export_folder:
        path_zipfile = Path(export_folder) / "export.zip"

        fake_kili = FakeKili()
        fake_kili.kili_api_gateway.list_assets.side_effect = capture_fields
        fake_kili.kili_api_gateway.count_assets.side_effect = (
            mocked_AssetQuery_count_with_latestLabels
        )
        fake_kili.kili_api_gateway.get_project.side_effect = mocked_kili_api_gateway_get_project

        export_labels(
            fake_kili,  # type: ignore
            asset_ids=[],
            project_id="object_detection",
            export_type="latest_from_all_steps",
            label_format="raw",
            split_option="merged",
            single_file=False,
            output_file=str(path_zipfile),
            disable_tqdm=True,
            log_level="INFO",
            with_assets=False,
            annotation_modifier=None,
            asset_filter_kwargs=None,
            normalized_coordinates=None,
            label_type_in=None,
            include_sent_back_labels=None,
        )

        # Verify that labels fields were requested (not latestLabels)
        assert len(fields_requested) > 0, "Should have requested fields"
        requested = fields_requested[0]

        assert "labels.jsonResponse" in requested
        assert "labels.author.firstname" in requested
        assert "labels.author.lastname" in requested
        assert "labels.isLastForStep" in requested
