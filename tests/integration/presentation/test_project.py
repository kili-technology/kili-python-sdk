import pytest_mock

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.adapters.kili_api_gateway.project.operations import (
    GQL_CREATE_PROJECT,
    get_update_properties_in_project_mutation,
)
from kili.presentation.client.project import ProjectClientMethods


def test_when_creating_project_then_it_returns_project_id(mocker: pytest_mock.MockerFixture):
    kili = ProjectClientMethods()
    kili.kili_api_gateway = KiliAPIGateway(
        graphql_client=mocker.MagicMock(), http_client=mocker.MagicMock()
    )
    kili.kili_api_gateway.get_project = mocker.MagicMock(return_value="fake_project_id")

    # When
    kili.create_project(input_type="IMAGE", json_interface={}, title="fake_title")

    # Then
    kili.kili_api_gateway.graphql_client.execute.assert_called_once_with(
        GQL_CREATE_PROJECT,
        {
            "data": {
                "description": "",
                "inputType": "IMAGE",
                "jsonInterface": "{}",
                "projectType": None,
                "title": "fake_title",
                "fromDemoProject": None,
            }
        },
    )


def test_when_updating_project_then_it_returns_updated_project(mocker: pytest_mock.MockerFixture):
    kili = ProjectClientMethods()
    kili.kili_api_gateway = KiliAPIGateway(
        graphql_client=mocker.MagicMock(), http_client=mocker.MagicMock()
    )
    # Given
    project_id = "fake_proj_id"

    # When
    kili.update_properties_in_project(project_id, review_coverage=42)

    # Then
    kili.kili_api_gateway.graphql_client.execute.assert_called_once_with(
        get_update_properties_in_project_mutation(" reviewCoverage id"),
        {
            "where": {"id": "fake_proj_id"},
            "data": {
                "archived": None,
                "author": None,
                "consensusMark": None,
                "consensusTotCoverage": None,
                "description": None,
                "canNavigateBetweenAssets": None,
                "canSkipAsset": None,
                "honeypotMark": None,
                "inputType": None,
                "instructions": None,
                "jsonInterface": None,
                "minConsensusSize": None,
                "rules": None,
                "reviewCoverage": 42,
                "shouldAutoAssign": None,
                "shouldRelaunchKpiComputation": None,
                "title": None,
                "useHoneyPot": None,
            },
        },
    )
