"""
Test cloud storage methods
"""

import json
import os
from typing import Dict, List, Tuple

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
        title="test_e2e_synchronize_cloud_storage_connection",
        description="test_e2e_synchronize_cloud_storage_connection",
    )

    yield project

    kili.delete_project(project["id"])


def get_test_cases() -> List[Tuple[str]]:
    """
    KILI_TEST_DATA_INTEGRATION_ID is a json string of the form:
    {
        "LTS": {
            "AWS": ["data_integration_id_1", "data_integration_id_2"],
            "GCP": ["data_integration_id_1", "data_integration_id_2"],
            "Azure": ["data_integration_id_1", "data_integration_id_2"],
        },
        "STAGING": {
            "AWS": ["data_integration_id_1", "data_integration_id_2"],
            ...
        },
        ...
    }
    """
    test_cases = []

    integrations_ids = os.environ.get("KILI_TEST_DATA_INTEGRATION_ID")
    if integrations_ids is None:
        return test_cases

    integrations_ids = json.loads(integrations_ids)

    for endpoint_short_name, platform_to_data_integration_ids in integrations_ids.items():
        for platform_name, data_integration_ids in platform_to_data_integration_ids.items():
            for data_integration_id in data_integration_ids:
                test_cases.append((endpoint_short_name, platform_name, data_integration_id))

    return test_cases


def is_same_endpoint(endpoint_short_name: str, endpoint_url: str) -> bool:
    if endpoint_short_name == "LTS":
        return "lts" in endpoint_url
    elif endpoint_short_name == "STAGING":
        return "staging" in endpoint_url
    elif endpoint_short_name == "PREPROD":
        return "preprod" in endpoint_url
    elif endpoint_short_name == "PROD":
        return "https://cloud" in endpoint_url
    else:
        raise ValueError(f"Unknown endpoint short name: {endpoint_short_name}")


@pytest.mark.parametrize("endpoint_short_name,platform_name,data_integration_id", get_test_cases())
def test_e2e_synchronize_cloud_storage_connection(
    kili: Kili,
    src_project: Dict,
    endpoint_short_name: str,
    platform_name: str,
    data_integration_id: str,
):
    if not is_same_endpoint(endpoint_short_name, kili.auth.api_endpoint):
        pytest.skip("Skipping test because it is not the right endpoint.")

    project_id = src_project["id"]

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
