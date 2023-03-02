"""
Test synchronize_data_connection
"""

import os
from typing import Dict

import pytest

from kili.client import Kili


@pytest.fixture
def kili() -> Kili:
    return Kili()


@pytest.fixture()
def src_project(kili: Kili):
    interface = {
        "jobs": {
            "JOB_0": {
                "content": {
                    "categories": {
                        "OBJECT_A": {"children": [], "name": "Object A"},
                        "OBJECT_B": {"children": [], "name": "Object B"},
                    },
                    "input": "radio",
                },
                "instruction": "Categories",
                "isChild": False,
                "mlTask": "CLASSIFICATION",
                "models": {},
                "isVisible": True,
                "required": 1,
            }
        }
    }

    project = kili.create_project(
        input_type="IMAGE",
        json_interface=interface,
        title="test_e2e_synchronize_data_connection.py",
        description="test_e2e_synchronize_data_connection.py",
    )

    yield project

    kili.delete_project(project["id"])


@pytest.mark.skip(reason="cannot test this for now. requires data integrations to be set up")
def test_e2e_synchronize_data_connection(kili: Kili, src_project: Dict):
    project_id = src_project["id"]

    data_integration_id = os.environ.get("KILI_TEST_DATA_INTEGRATION_ID")
    if data_integration_id is None:
        raise ValueError("KILI_TEST_DATA_INTEGRATION_ID env var not found. Cannot run test.")

    print("Data integration used:", data_integration_id)

    data_integrations = kili.cloud_storage_integrations(
        status="CONNECTED", cloud_storage_integration_id=data_integration_id
    )
    if len(data_integrations) != 1:
        raise ValueError("No data integration found. Cannot run test.", data_integrations)

    data_connection_id = kili.add_cloud_storage_connection(
        project_id=project_id, cloud_storage_integration_id=data_integration_id
    )["id"]

    data_connections = kili.cloud_storage_connections(
        project_id=project_id,
        fields=[
            "id",
            "dataDifferencesSummary.added",
            "dataDifferencesSummary.removed",
            "dataDifferencesSummary.total",
            "isChecking",
            "isApplyingDataDifferences",
            "lastChecked",
            "numberOfAssets",
            "selectedFolders",
            "dataIntegrationId",
        ],
    )
    assert len(data_connections) == 1, data_connections
    data_connection = data_connections[0]
    assert data_connection["id"] == data_connection_id, data_connection
    assert data_connection["dataIntegrationId"] == data_integration_id, data_connection
    print("Data connection:", data_connection)

    nb_assets = kili.count_assets(project_id=project_id)
    assert nb_assets == 0, f"Expected no asset before sync. Got {nb_assets}"

    kili.synchronize_cloud_storage_connection(
        cloud_storage_connection_id=data_connection_id,
        delete_extraneous_files=True,
    )

    nb_assets = kili.count_assets(project_id=project_id)
    assert nb_assets > 0, "Expected at least one asset after sync."
