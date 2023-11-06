import logging
from typing import Any, Dict, List, Optional

import pytest
import pytest_mock

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.mixin import KiliAPIGateway
from kili.domain.cloud_storage import (
    DataConnectionFilters,
    DataConnectionId,
    DataDifferenceType,
    DataIntegrationFilters,
)
from kili.use_cases.cloud_storage import (
    CloudStorageUseCases,
    _compute_differences,
    _validate_data_differences,
)


class MockerGetDataConnection:
    """Class to mock the get_data_connection function."""

    def __init__(
        self,
        added: int,
        removed: int,
        total: int,
        nb_of_assets: int,
        is_checking: bool,
        project_id: str,
        selected_folders: Optional[List[str]],
        data_integration: Optional[Dict] = None,
    ) -> None:
        if data_integration is None:
            data_integration = {
                "azureIsUsingServiceCredentials": False,
                "platform": "AWS",
                "azureSASToken": "fake_token",
                "azureConnectionURL": "fake_url",
                "id": "fake_data_integration_id",
            }
        self.added = added
        self.removed = removed
        self.total = total
        self.nb_of_assets = nb_of_assets
        self.is_checking = is_checking
        self.project_id = project_id
        self.selected_folders = selected_folders
        self.data_integration = data_integration

    def __call__(self, data_connection_id: str, fields: List[str]) -> Dict[str, Any]:
        ret: Dict[str, Any] = {"id": data_connection_id}

        ret["dataDifferencesSummary"] = {}

        if "dataDifferencesSummary.added" in fields:
            ret["dataDifferencesSummary"]["added"] = self.added
        if "dataDifferencesSummary.removed" in fields:
            ret["dataDifferencesSummary"]["removed"] = self.removed
        if "dataDifferencesSummary.total" in fields:
            ret["dataDifferencesSummary"]["total"] = self.total
        if "isChecking" in fields:
            ret["isChecking"] = self.is_checking
        if "numberOfAssets" in fields:
            ret["numberOfAssets"] = self.nb_of_assets
        if "projectId" in fields:
            ret["projectId"] = self.project_id
        if "selectedFolders" in fields:
            ret["selectedFolders"] = self.selected_folders
        if any(field.startswith("dataIntegration.") for field in fields):
            ret["dataIntegration"] = self.data_integration

        return ret


@pytest.mark.parametrize(
    ("delete_extraneous_files", "data_connection_ret_values", "log_messages"),
    [
        (
            False,
            {
                "added": 0,
                "removed": 0,
                "total": 0,
                "nb_of_assets": 100,
                "is_checking": False,
                "project_id": "fake_proj_id",
                "selected_folders": None,
            },
            (
                "Currently 100 asset(s) imported from the data connection.",
                "No differences found. Nothing to synchronize.",
            ),
        ),
        (
            False,
            {
                "added": 0,
                "removed": 12,
                "total": 42,
                "nb_of_assets": 50,
                "is_checking": False,
                "project_id": "fake_proj_id",
                "selected_folders": None,
            },
            (
                "Currently 50 asset(s) imported from the data connection.",
                "Found 42 difference(s)",
                "Use delete_extraneous_files=True to remove 12 extraneous file(s).",
            ),
        ),
        (
            True,
            {
                "added": 0,
                "removed": 12,
                "total": 42,
                "nb_of_assets": 50,
                "is_checking": False,
                "project_id": "fake_proj_id",
                "selected_folders": None,
            },
            (
                "Currently 50 asset(s) imported from the data connection.",
                "Found 42 difference(s)",
                "Removed 12 extraneous file(s).",
            ),
        ),
        (
            True,
            {
                "added": 444,
                "removed": 1,
                "total": 1000,
                "nb_of_assets": 2000,
                "is_checking": False,
                "project_id": "fake_proj_id",
                "selected_folders": None,
            },
            (
                "Currently 2000 asset(s) imported from the data connection.",
                "Found 1000 difference(s)",
                "Removed 1 extraneous file(s).",
                "Added 444 file(s).",
            ),
        ),
    ],
)
def test_given_kili_client_when_calling_synchronize_cloud_storage_connection_then_it_calls_proper_resolvers(
    delete_extraneous_files,
    data_connection_ret_values,
    log_messages,
    caplog,
    mocker,
    kili_api_gateway: KiliAPIGateway,
) -> None:
    # Given
    mocker.patch("kili.use_cases.cloud_storage._compute_differences")
    mocker.patch("kili.use_cases.cloud_storage.Retrying", return_value=[])

    kili_api_gateway.get_data_connection.side_effect = MockerGetDataConnection(
        **data_connection_ret_values
    )
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())

    # When
    CloudStorageUseCases(kili_api_gateway).synchronize_data_connection(
        data_connection_id=DataConnectionId("my_data_connection_id"),
        delete_extraneous_files=delete_extraneous_files,
        dry_run=False,
        logger=logger,
    )

    # Then
    assert "Synchronizing data connection: my_data_connection_id" in caplog.text
    for log_msg in log_messages:
        assert log_msg in caplog.text

    if delete_extraneous_files and data_connection_ret_values["removed"] > 0:
        kili_api_gateway.validate_data_connection_differences.assert_any_call(
            data_connection_id="my_data_connection_id",
            data_difference_type="REMOVE",
            fields=("id",),
        )

    if data_connection_ret_values["added"] > 0:
        kili_api_gateway.validate_data_connection_differences.assert_any_call(
            data_connection_id="my_data_connection_id",
            data_difference_type="ADD",
            fields=("id",),
        )


def test_given_data_connections_when_querying_presentation_method_then_it_works(
    kili_api_gateway: KiliAPIGateway,
):
    # Given
    kili_api_gateway.list_data_connections.return_value = [
        {"id": "data_connection_id_1"},
        {"id": "data_connection_id_2"},
    ]

    # When
    data_connections = CloudStorageUseCases(kili_api_gateway).list_data_connections(
        DataConnectionFilters(None, None), fields=("id",), options=QueryOptions(None)
    )

    # Then
    assert data_connections == [
        {"id": "data_connection_id_1"},
        {"id": "data_connection_id_2"},
    ]


def test_given_data_connection_when_querying_presentation_method_then_it_works(
    kili_api_gateway: KiliAPIGateway,
):
    # Given
    kili_api_gateway.get_data_connection.return_value = {"id": "fake_data_connection_id"}

    # When
    data_connections = CloudStorageUseCases(kili_api_gateway).get_data_connection(
        data_connection_id=DataConnectionId("fake_data_connection_id"), fields=("id",)
    )

    # Then
    assert data_connections == {"id": "fake_data_connection_id"}


def test_given_data_integrations_when_querying_count_then_it_returns_count(
    kili_api_gateway: KiliAPIGateway,
):
    # Given
    kili_api_gateway.count_data_integrations.return_value = 42

    # When
    count = CloudStorageUseCases(kili_api_gateway).count_data_integrations(
        DataIntegrationFilters(id=None)
    )

    # Then
    assert count == 42


def test_given_cloud_storage_use_cases_when_calling_validate_data_differences_then_it_works(
    kili_api_gateway: KiliAPIGateway, mocker: pytest_mock.MockerFixture
):
    # Given
    mocker.patch("kili.use_cases.cloud_storage.Retrying", return_value=[])
    kili_api_gateway.get_data_connection.return_value = {
        "id": "fake_data_con_id",
        "dataDifferencesSummary": {"added": 12, "removed": 0, "total": 12},
        "projectId": "fake_proj_id",
    }
    kili_api_gateway.count_assets.return_value = 0

    # When
    _validate_data_differences(
        DataDifferenceType.ADD,
        data_connection_id=DataConnectionId("fake_data_con_id"),
        kili_api_gateway=kili_api_gateway,
    )

    # Then
    kili_api_gateway.validate_data_connection_differences.assert_called_once_with(
        data_connection_id=DataConnectionId("fake_data_con_id"),
        data_difference_type=DataDifferenceType.ADD,
        fields=("id",),
    )


def test_given_cloud_storage_use_cases_when_calling_compute_differences_then_it_works(
    kili_api_gateway: KiliAPIGateway, mocker: pytest_mock.MockerFixture
):
    # Given
    mocker.patch("kili.use_cases.cloud_storage.Retrying", return_value=[])
    kili_api_gateway.get_data_connection.return_value = {
        "projectId": "fake_proj_id",
        "isChecking": False,
        "selectedFolders": None,
        "dataIntegration": {
            "platform": "AWS",
            "azureIsUsingServiceCredentials": None,
            "azureSASToken": None,
            "azureConnectionURL": None,
            "id": "fake_data_integration_id",
        },
    }

    # When
    _compute_differences(
        data_connection_id=DataConnectionId("fake_data_con_id"), kili_api_gateway=kili_api_gateway
    )

    # Then
    kili_api_gateway.compute_data_connection_differences.assert_called_once_with(
        data_connection_id=DataConnectionId("fake_data_con_id"), fields=("id",), data=None
    )
