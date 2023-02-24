"""
Test synchronize_data_connection
"""

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


def test_e2e_synchronize_data_connection(kili: Kili, src_project: Dict):
    project_id = src_project["id"]

    data_integrations = kili.data_integrations(status="CONNECTED")

    if len(data_integrations) == 0:
        raise ValueError("No data integration found. Cannot run test.")

    # We take the first one...
    data_integration_id = data_integrations[0]["id"]
    print(f"Using data integration {data_integrations[0]}")

    data_connection_id = kili.add_data_connection(
        project_id=project_id, data_integration_id=data_integration_id
    )["id"]

    data_connections = kili.data_connections(
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

    assets = kili.assets(project_id=project_id)
    assert len(assets) == 0, f"Expected no asset before sync. Got {assets}"

    kili.synchronize_data_connection(
        project_id=project_id, data_connection_id=data_connection_id, delete_extraneous_files=True
    )

    assets = kili.assets(project_id=project_id)

    assert len(assets) > 0, "Expected at least one asset after sync."
