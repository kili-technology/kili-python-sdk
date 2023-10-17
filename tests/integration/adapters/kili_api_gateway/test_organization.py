from datetime import datetime

import pytz
from pytest_mock import MockerFixture

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.organization.operations_mixin import (
    OrganizationOperationMixin,
)
from kili.adapters.kili_api_gateway.organization.types import (
    KiliAPIGateWayCreateOrganizationInput,
    KiliAPIGateWayUpdateOrganizationInput,
)
from kili.core.graphql.graphql_client import GraphQLClient
from kili.domain.organization import (
    OrganizationFilters,
    OrganizationId,
    OrganizationMetricsFilters,
)


def test_create_organization(mocker, graphql_client):
    # Given
    kili_api_gateway = OrganizationOperationMixin()
    kili_api_gateway.graphql_client = graphql_client
    organization_name = "test_organization"
    execute = mocker.patch.object(
        kili_api_gateway.graphql_client,
        "execute",
        return_value={
            "data": {
                "id": "fake_organization_id",
                "name": organization_name,
            }
        },
    )

    # When
    organization = kili_api_gateway.create_organization(
        KiliAPIGateWayCreateOrganizationInput(
            name=organization_name,
            address="1, rue de Rivoli",
            city="Paris",
            country="France",
            zip_code="75001",
        ),
        description="Create organization",
        disable_tqdm=False,
    )

    # Then
    assert organization["name"] == organization_name
    print(execute.calls)

    execute.assert_called_with(
        "\nmutation(\n    $data: CreateOrganizationData!\n) {\n  data: createOrganization(\n   "
        " data: $data\n  ) {\n    \nid\n\n  }\n}\n",
        {
            "data": {
                "name": "test_organization",
                "address": "1, rue de Rivoli",
                "city": "Paris",
                "country": "France",
                "zipCode": "75001",
            }
        },
    )


def test_list_organization(mocker, graphql_client):
    # Given
    kili_api_gateway = OrganizationOperationMixin()
    kili_api_gateway.graphql_client = graphql_client
    organization_name = "test_organization"
    execute = mocker.patch.object(
        kili_api_gateway.graphql_client,
        "execute",
        side_effect=[
            {"data": 1},  # response to count query
            {  # response to list query
                "data": [
                    {
                        "id": "fake_organization_id",
                        "name": organization_name,
                    }
                ]
            },
        ],
    )

    # When
    organizations = kili_api_gateway.list_organizations(
        filters=OrganizationFilters(),
        fields=["id", "name"],
        description="List organizations",
        options=QueryOptions(disable_tqdm=False),
    )

    # Then
    assert next(organizations)["name"] == organization_name
    execute.assert_called_with(
        "\n        query organizations($where: OrganizationWhere!, $first: PageSize!, $skip:"
        " Int!) {\n            data: organizations(where: $where, first: $first, skip: $skip)"
        " {\n                 id name\n            }\n        }\n        ",
        {"where": {"id": None, "user": {"email": None}}, "skip": 0, "first": 1},
    )


def test_count_organization(mocker, graphql_client):
    # Given
    kili_api_gateway = OrganizationOperationMixin()
    kili_api_gateway.graphql_client = graphql_client
    execute = mocker.patch.object(
        kili_api_gateway.graphql_client,
        "execute",
        return_value={"data": 6},
    )

    # When
    count = kili_api_gateway.count_organizations(
        filters=OrganizationFilters(email="jean.philippe@kili-technology.com"),
    )

    # Then
    assert count == 6
    execute.assert_called_with(
        "\n        query countOrganizations($where: OrganizationWhere!) {\n        data:"
        " countOrganizations(where: $where)\n        }\n    ",
        {"where": {"id": None, "user": {"email": "jean.philippe@kili-technology.com"}}},
    )


def test_get_organization_metrics(mocker: MockerFixture, graphql_client: GraphQLClient):
    # Given
    kili_api_gateway = OrganizationOperationMixin()
    kili_api_gateway.graphql_client = graphql_client
    execute = mocker.patch.object(
        kili_api_gateway.graphql_client,
        "execute",
        return_value={
            "data": {"numberOfAnnotations": 18, "numberOfHours": 5, "numberOfLabeledAssets": 3}
        },
    )

    # When
    metrics = kili_api_gateway.get_organization_metrics(
        filters=OrganizationMetricsFilters(
            id=OrganizationId("fake_organization_id"),
            start_datetime=datetime(2022, 1, 1, tzinfo=pytz.UTC),
            end_datetime=datetime(2022, 1, 5, tzinfo=pytz.UTC),
        ),
        disable_tqdm=True,
        description="Get organization metrics",
    )

    # Then
    assert metrics == {"numberOfAnnotations": 18, "numberOfHours": 5, "numberOfLabeledAssets": 3}
    execute.assert_called_with(
        "\n    query organizationMetrics($where: OrganizationMetricsWhere!) {\n        data:"
        " organizationMetrics(where: $where) {\n            numberOfAnnotations\n           "
        " numberOfHours\n            numberOfLabeledAssets\n        }\n    }\n    ",
        {
            "where": {
                "organizationId": "fake_organization_id",
                "startDate": "2022-01-01T00:00:00.000+00:00Z",
                "endDate": "2022-01-05T00:00:00.000+00:00Z",
            }
        },
    )


def test_update_organization(mocker: MockerFixture, graphql_client: GraphQLClient):
    # Given
    kili_api_gateway = OrganizationOperationMixin()
    kili_api_gateway.graphql_client = graphql_client
    execute = mocker.patch.object(
        kili_api_gateway.graphql_client,
        "execute",
        return_value={"data": {"id": "fake_organization_id", "name": "new_name"}},
    )

    # When
    organization = kili_api_gateway.update_organization(
        OrganizationId("fake_organization_id"),
        KiliAPIGateWayUpdateOrganizationInput(name="new_name"),
        disable_tqdm=None,
        description="Update organization",
    )

    # Then
    execute.assert_called_with(
        "\nmutation(\n    $id: ID!\n    $name: String\n    $license: String\n) {\n  data:"
        " updatePropertiesInOrganization(\n    where: {id: $id}\n    data: {\n      name:"
        " $name\n      license: $license\n    }\n  ) {\n    \nid\n\n  }\n}\n",
        {"id": "fake_organization_id", "name": "new_name"},
    )
    assert organization["name"] == "new_name"
