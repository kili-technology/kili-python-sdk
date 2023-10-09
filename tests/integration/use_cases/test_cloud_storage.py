import pytest_mock

from kili.adapters.kili_api_gateway import KiliAPIGateway
from kili.domain.cloud_storage import DataConnectionId, DataDifferenceType
from kili.use_cases.cloud_storage import (
    _compute_differences,
    _validate_data_differences,
)


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
