from datetime import datetime, timedelta, timezone
from unittest.mock import call

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.organization.operations import (
    GET_ORGANIZATION_USAGE_QUERY,
    LIST_ORGANIZATION_USAGE_BY_PROJECT_QUERY,
)
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
    OrganizationUsageByProjectFilters,
    OrganizationUsageFilters,
)
from kili.domain.project import ProjectId


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
            start_datetime=datetime(2022, 1, 1, tzinfo=timezone.utc),
            end_datetime=datetime(2022, 1, 5, tzinfo=timezone.utc),
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


def test_get_organization_usage_sends_the_period_in_utc(graphql_client: GraphQLClient):
    # Given
    kili_api_gateway = OrganizationOperationMixin()
    kili_api_gateway.graphql_client = graphql_client
    usage = [{"metric": "LABELED_ASSETS", "total": 3.0, "details": []}]
    kili_api_gateway.graphql_client.execute.return_value = {"data": usage}

    # When
    result = kili_api_gateway.get_organization_usage(
        OrganizationUsageFilters(
            metrics=("LABELED_ASSETS", "LABELING_TIME"),
            project_id=ProjectId("project_id"),
            start_datetime=datetime(2026, 10, 1),
            end_datetime=datetime(2026, 11, 1, 2, tzinfo=timezone(timedelta(hours=2))),
            granularity="DAY",
        )
    )

    # Then
    assert result == usage
    kili_api_gateway.graphql_client.execute.assert_called_once_with(
        GET_ORGANIZATION_USAGE_QUERY,
        {
            "where": {
                "metrics": ["LABELED_ASSETS", "LABELING_TIME"],
                "projectId": "project_id",
                "startDate": "2026-10-01T00:00:00+00:00",
                "endDate": "2026-11-01T00:00:00+00:00",
                "granularity": "DAY",
            }
        },
    )


def test_get_organization_usage_reads_a_null_answer_as_no_metric(graphql_client: GraphQLClient):
    # Given
    kili_api_gateway = OrganizationOperationMixin()
    kili_api_gateway.graphql_client = graphql_client
    kili_api_gateway.graphql_client.execute.return_value = {"data": None}

    # When
    result = kili_api_gateway.get_organization_usage(
        OrganizationUsageFilters(metrics=("LABELED_ASSETS",))
    )

    # Then
    assert result == []
    kili_api_gateway.graphql_client.execute.assert_called_once_with(
        GET_ORGANIZATION_USAGE_QUERY, {"where": {"metrics": ["LABELED_ASSETS"]}}
    )


def _usage_page(project_ids: list[str], total_count: int) -> dict:
    return {
        "data": {
            "data": [
                {
                    "projectId": project_id,
                    "projectTitle": project_id,
                    "isDeleted": False,
                    "metrics": [{"metric": "LABELED_ASSETS", "total": 1.0}],
                }
                for project_id in project_ids
            ],
            "totalCount": total_count,
        }
    }


def test_list_organization_usage_by_project_pages_until_the_total_count(
    graphql_client: GraphQLClient,
):
    # Given
    kili_api_gateway = OrganizationOperationMixin()
    kili_api_gateway.graphql_client = graphql_client
    first_page = [f"project_{i}" for i in range(50)]
    kili_api_gateway.graphql_client.execute.side_effect = [
        _usage_page(first_page, 52),
        _usage_page(["project_50", "project_51"], 52),
    ]
    filters = OrganizationUsageByProjectFilters(metrics=("LABELED_ASSETS",), search_query="shelves")

    # When
    projects = list(
        kili_api_gateway.list_organization_usage_by_project(
            filters, QueryOptions(disable_tqdm=True)
        )
    )

    # Then
    assert [project["projectId"] for project in projects] == [
        *first_page,
        "project_50",
        "project_51",
    ]
    where = {"metrics": ["LABELED_ASSETS"], "searchQuery": "shelves"}
    assert kili_api_gateway.graphql_client.execute.call_args_list == [
        call(LIST_ORGANIZATION_USAGE_BY_PROJECT_QUERY, {"where": where, "first": 50, "skip": 0}),
        call(LIST_ORGANIZATION_USAGE_BY_PROJECT_QUERY, {"where": where, "first": 50, "skip": 50}),
    ]


def test_list_organization_usage_by_project_asks_only_for_first_projects(
    graphql_client: GraphQLClient,
):
    # Given
    kili_api_gateway = OrganizationOperationMixin()
    kili_api_gateway.graphql_client = graphql_client
    kili_api_gateway.graphql_client.execute.return_value = _usage_page(
        ["project_5", "project_6"], 52
    )

    # When
    projects = list(
        kili_api_gateway.list_organization_usage_by_project(
            OrganizationUsageByProjectFilters(metrics=("LABELED_ASSETS",)),
            QueryOptions(disable_tqdm=True, first=2, skip=5),
        )
    )

    # Then
    assert [project["projectId"] for project in projects] == ["project_5", "project_6"]
    kili_api_gateway.graphql_client.execute.assert_called_once_with(
        LIST_ORGANIZATION_USAGE_BY_PROJECT_QUERY,
        {"where": {"metrics": ["LABELED_ASSETS"]}, "first": 2, "skip": 5},
    )


def test_list_organization_usage_by_project_asks_the_last_page_for_what_first_leaves(
    graphql_client: GraphQLClient,
):
    # Given
    kili_api_gateway = OrganizationOperationMixin()
    kili_api_gateway.graphql_client = graphql_client
    kili_api_gateway.graphql_client.execute.side_effect = [
        _usage_page([f"project_{i}" for i in range(50)], 80),
        _usage_page([f"project_{i}" for i in range(50, 60)], 80),
    ]

    # When
    projects = list(
        kili_api_gateway.list_organization_usage_by_project(
            OrganizationUsageByProjectFilters(metrics=("LABELED_ASSETS",)),
            QueryOptions(disable_tqdm=True, first=60),
        )
    )

    # Then
    assert len(projects) == 60
    where = {"metrics": ["LABELED_ASSETS"]}
    assert kili_api_gateway.graphql_client.execute.call_args_list == [
        call(LIST_ORGANIZATION_USAGE_BY_PROJECT_QUERY, {"where": where, "first": 50, "skip": 0}),
        call(LIST_ORGANIZATION_USAGE_BY_PROJECT_QUERY, {"where": where, "first": 10, "skip": 50}),
    ]


def test_list_organization_usage_by_project_asks_nothing_for_first_0(
    graphql_client: GraphQLClient,
):
    # Given
    kili_api_gateway = OrganizationOperationMixin()
    kili_api_gateway.graphql_client = graphql_client

    # When
    projects = list(
        kili_api_gateway.list_organization_usage_by_project(
            OrganizationUsageByProjectFilters(metrics=("LABELED_ASSETS",)),
            QueryOptions(disable_tqdm=True, first=0),
        )
    )

    # Then
    assert projects == []
    kili_api_gateway.graphql_client.execute.assert_not_called()
