import pytest_mock

from kili.adapters.kili_api_gateway import KiliAPIGateway
from kili.presentation.client.cloud_storage import CloudStorageClientMethods
from kili.use_cases.cloud_storage import CloudStorageUseCases


def test_given_kili_client_when_calling_cloud_storage_connections_then_it_works(
    kili_api_gateway: KiliAPIGateway, mocker: pytest_mock.MockerFixture
):
    # Given
    kili = CloudStorageClientMethods()
    kili.kili_api_gateway = kili_api_gateway
    data_connections = [{"id": "fake_data_connection_id"}]
    mocker.patch.object(
        CloudStorageUseCases, "list_data_connections", return_value=data_connections
    )

    # When
    ret = kili.cloud_storage_connections(project_id="fake_proj_id")

    # Then
    assert ret == data_connections


def test_given_kili_client_when_calling_cloud_storage_connection_then_it_works(
    kili_api_gateway: KiliAPIGateway, mocker: pytest_mock.MockerFixture
):
    # Given
    kili = CloudStorageClientMethods()
    kili.kili_api_gateway = kili_api_gateway
    data_connection = {"id": "fake_data_connection_id"}
    mocker.patch.object(CloudStorageUseCases, "get_data_connection", return_value=data_connection)

    # When
    ret = kili.cloud_storage_connections(cloud_storage_connection_id="fake_data_connection_id")

    # Then
    assert ret == [data_connection]
