from datetime import datetime

import pytz

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.organization.operations_mixin import (
    OrganizationOperationMixin,
)
from kili.core.graphql.graphql_client import GraphQLClient
from kili.domain.organization import (
    OrganizationFilters,
    OrganizationId,
    OrganizationMetricsFilters,
    OrganizationToCreateInput,
    OrganizationToUpdateInput,
)


def test_create_organization(graphql_client):
    # Given
    kili_api_gateway = OrganizationOperationMixin()
    kili_api_gateway.graphql_client = graphql_client
    organization_name = "test_organization"
    kili_api_gateway.graphql_client.execute.return_value = {
        "data": {
            "id": "fake_organization_id",
            "name": organization_name,
        }
    }

    # When
    organization = kili_api_gateway.create_organization(
        OrganizationToCreateInput(
            name=organization_name,
        ),
    )

    # Then
    assert organization["name"] == organization_name

    kili_api_gateway.graphql_client.execute.assert_called_with(
        "\nmutation(\n    $data: CreateOrganizationData!\n) {\n  data: createOrganization(\n   "
        " data: $data\n  ) {\n     id\n  }\n}\n",
        {
            "data": {
                "name": "test_organization",
            }
        },
    )


def test_list_organization(graphql_client):
    # Given
    kili_api_gateway = OrganizationOperationMixin()
    kili_api_gateway.graphql_client = graphql_client
    organization_name = "test_organization"
    kili_api_gateway.graphql_client.execute.side_effect = [
        {"data": 1},  # response to count query
        {  # response to list query
            "data": [
                {
                    "id": "fake_organization_id",
                    "name": organization_name,
                }
            ]
        },
    ]

    # When
    organizations = kili_api_gateway.list_organizations(
        filters=OrganizationFilters(),
        fields=["id", "name"],
        description="List organizations",
        options=QueryOptions(disable_tqdm=False),
    )

    # Then
    assert next(organizations)["name"] == organization_name
    kili_api_gateway.graphql_client.execute.assert_called_with(
        "\n        query organizations($where: OrganizationWhere!, $first: PageSize!, $skip:"
        " Int!) {\n            data: organizations(where: $where, first: $first, skip: $skip)"
        " {\n                 id name\n            }\n        }\n        ",
        {"where": {"id": None, "user": {"email": None}}, "skip": 0, "first": 1},
    )


def test_count_organization(graphql_client):
    # Given
    kili_api_gateway = OrganizationOperationMixin()
    kili_api_gateway.graphql_client = graphql_client
    kili_api_gateway.graphql_client.execute.return_value = {"data": 6}

    # When
    count = kili_api_gateway.count_organizations(
        filters=OrganizationFilters(email="jean.philippe@kili-technology.com"),
    )

    # Then
    assert count == 6
    kili_api_gateway.graphql_client.execute.assert_called_with(
        "\n        query countOrganizations($where: OrganizationWhere!) {\n        data:"
        " countOrganizations(where: $where)\n        }\n    ",
        {"where": {"id": None, "user": {"email": "jean.philippe@kili-technology.com"}}},
    )


def test_get_organization_metrics(graphql_client: GraphQLClient):
    # Given
    kili_api_gateway = OrganizationOperationMixin()
    kili_api_gateway.graphql_client = graphql_client
    kili_api_gateway.graphql_client.execute.return_value = {
        "data": {"numberOfAnnotations": 18, "numberOfHours": 5, "numberOfLabeledAssets": 3}
    }

    # When
    metrics = kili_api_gateway.get_organization_metrics(
        filters=OrganizationMetricsFilters(
            id=OrganizationId("fake_organization_id"),
            start_datetime=datetime(2022, 1, 1, tzinfo=pytz.UTC),
            end_datetime=datetime(2022, 1, 5, tzinfo=pytz.UTC),
        ),
        fields=["numberOfAnnotations", "numberOfHours", "numberOfLabeledAssets"],
    )

    # Then
    assert metrics == {"numberOfAnnotations": 18, "numberOfHours": 5, "numberOfLabeledAssets": 3}
    kili_api_gateway.graphql_client.execute.assert_called_with(
        "\n    query organizationMetrics($where: OrganizationMetricsWhere!) {\n        data:"
        " organizationMetrics(where: $where) {\n             numberOfAnnotations numberOfHours"
        " numberOfLabeledAssets\n        }\n    }\n    ",
        {
            "where": {
                "organizationId": "fake_organization_id",
                "startDate": "2022-01-01T00:00:00Z",
                "endDate": "2022-01-05T00:00:00Z",
            }
        },
    )


def test_update_organization(graphql_client: GraphQLClient):
    # Given
    kili_api_gateway = OrganizationOperationMixin()
    kili_api_gateway.graphql_client = graphql_client
    kili_api_gateway.graphql_client.execute.return_value = {
        "data": {"id": "fake_organization_id", "name": "new_name"}
    }

    # When
    organization = kili_api_gateway.update_organization(
        OrganizationId("fake_organization_id"),
        OrganizationToUpdateInput(name="new_name"),
    )

    # Then
    kili_api_gateway.graphql_client.execute.assert_called_with(
        "\nmutation(\n    $data: OrganizationData!,\n    $where: OrganizationWhere!\n) {\n "
        " data: updatePropertiesInOrganization(\n    data: $data\n    where: $where,\n  ) {\n  "
        "   id\n  }\n}\n",
        {"where": {"id": "fake_organization_id"}, "data": {"name": "new_name"}},
    )
    assert organization["name"] == "new_name"
