"""Test cloud storage methods."""

import hashlib
import json
import os
from typing import Dict, List, Optional

import pytest

from kili.client import Kili
from kili.domain.organization import OrganizationId


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


def is_same_endpoint(endpoint_short_name: str, endpoint_url: str) -> bool:
    """Check if the endpoint url matches the endpoint short name."""
    if endpoint_short_name == "LTS":
        return "lts" in endpoint_url

    if endpoint_short_name == "STAGING":
        return "staging" in endpoint_url

    if endpoint_short_name == "PREPROD":
        return "preprod" in endpoint_url

    if endpoint_short_name == "PROD":
        return "https://cloud" in endpoint_url

    raise ValueError(f"Unknown endpoint short name: {endpoint_short_name}")


# pylint: disable=line-too-long
@pytest.mark.parametrize(
    (
        "endpoint_short_name",
        "platform_name",
        "data_integration_id_hash",
        "selected_folders",
        "expected_nb_assets_after_sync",
    ),
    [
        ("STAGING", "AWS", "e39a035e575dd2f41b9e722caf4e18c5", None, 41),
        ("STAGING", "AWS", "e39a035e575dd2f41b9e722caf4e18c5", ["chickens"], 41),
        ("STAGING", "AWS", "e39a035e575dd2f41b9e722caf4e18c5", [], 41),
        ("STAGING", "Azure", "5512237816bd1dde391368ed93332b75", None, 10),
        ("STAGING", "Azure", "3e7e98e2ab4af2d614d97acb7b970c2b", None, 10),
        ("STAGING", "Azure", "3e7e98e2ab4af2d614d97acb7b970c2b", ["bears"], 10),
        ("STAGING", "Azure", "3e7e98e2ab4af2d614d97acb7b970c2b", [], 0),
        ("STAGING", "GCP", "f474c0170c8daa09ec2e368ce4720c73", None, 5),
    ],
)
def test_e2e_synchronize_cloud_storage_connection(
    kili: Kili,
    src_project: Dict,
    endpoint_short_name: str,
    platform_name: str,
    data_integration_id_hash: str,
    selected_folders: Optional[List[str]],
    expected_nb_assets_after_sync: int,
) -> None:
    """E2e test for cloud storage methods."""
    if not is_same_endpoint(endpoint_short_name, kili.api_endpoint):
        pytest.skip(
            f"Skipping test because endpoint {kili.api_endpoint} does not match"
            f" {endpoint_short_name}"
        )

    integrations_ids_str = os.getenv("KILI_TEST_DATA_INTEGRATION_ID", "{}")
    integrations_ids = json.loads(integrations_ids_str)

    data_integration_id = None
    for integration_id in integrations_ids.get(endpoint_short_name, {}).get(platform_name, []):
        if hashlib.md5(integration_id.encode()).hexdigest() == data_integration_id_hash:
            data_integration_id = integration_id
            break

    if data_integration_id is None:
        raise ValueError(f"Data integration with hash {data_integration_id_hash} not found.")

    project_id = src_project["id"]

    # Check that the data integration exists
    print("Data integration used:", data_integration_id)
    data_integrations = kili.cloud_storage_integrations(
        status="CONNECTED", cloud_storage_integration_id=data_integration_id
    )
    count_data_integrations = kili.count_cloud_storage_integrations(
        cloud_storage_integration_id=data_integration_id
    )
    if not len(data_integrations) == count_data_integrations == 1:
        raise ValueError(f"Data integration {data_integration_id} not found. Cannot run test.")

    # Create a data connection
    data_connection_id = kili.add_cloud_storage_connection(
        project_id=project_id,
        cloud_storage_integration_id=data_integration_id,
        selected_folders=selected_folders,
    )["id"]

    # Check that the data connection has been created
    data_connections = kili.cloud_storage_connections(
        cloud_storage_connection_id=data_connection_id,
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
    assert nb_assets == 0, f"Expected no asset before sync. Got {nb_assets} assets."

    kili.synchronize_cloud_storage_connection(
        cloud_storage_connection_id=data_connection_id,
        delete_extraneous_files=True,
    )

    nb_assets = kili.count_assets(project_id=project_id)
    assert (
        nb_assets == expected_nb_assets_after_sync
    ), f"Expected {expected_nb_assets_after_sync} assets after sync. Got {nb_assets} assets."


def test_e2e_update_data_integration(kili: Kili) -> None:
    """E2e test for data integration update method."""
    data_integration_id = "clhizyvxq00040j2ucmpuecw4"
    # Create data integration
    data_integration = kili.cloud_storage_integrations(
        status="CONNECTED", cloud_storage_integration_id=data_integration_id
    )[0]
    data_integration_name = data_integration["name"]
    # Update data integration
    data_integration_updated = kili.update_data_integration(
        data_integration_id=data_integration_id,
        name=f"{data_integration_name}_updated_name",
        platform=data_integration["platform"],
        status=data_integration["status"],
        organization_id=OrganizationId("feat1-organization"),
    )

    assert data_integration_updated["name"] == f"{data_integration_name}_updated_name"

    kili.update_data_integration(
        data_integration_id=data_integration_id,
        name=data_integration_name,
        platform=data_integration["platform"],
        status=data_integration["status"],
        organization_id=OrganizationId("feat1-organization"),
    )


def test_e2e_create_and_delete_data_integration(kili: Kili) -> None:
    """E2e test for data integration create and delete methods."""
    # Create data integration
    created_data_integration = kili.create_cloud_storage_integration(
        aws_access_point_arn=os.getenv("KILI_TEST_AWS_ACCESS_POINT_ARN", ""),
        aws_role_arn=os.getenv("KILI_TEST_AWS_ROLE_ARN", ""),
        aws_role_external_id=os.getenv("KILI_TEST_AWS_ROLE_EXTERNAL_ID", ""),
        name="E2E create data integration",
        platform="AWS",
    )
    assert created_data_integration["name"] == "E2E create data integration"

    count_data_integrations_before = kili.count_cloud_storage_integrations(
        cloud_storage_integration_id=created_data_integration["id"]
    )
    # Delete data integration
    deleted_data_integration = kili.delete_cloud_storage_integration(
        cloud_storage_integration_id=created_data_integration["id"]
    )

    assert deleted_data_integration == created_data_integration["id"]

    count_data_integrations_after = kili.count_cloud_storage_integrations(
        cloud_storage_integration_id=created_data_integration["id"]
    )

    assert count_data_integrations_after == count_data_integrations_before - 1
