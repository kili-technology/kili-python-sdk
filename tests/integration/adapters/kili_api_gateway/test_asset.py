from copy import deepcopy

from kili.adapters.kili_api_gateway.asset.operations_mixin import AssetOperationMixin
from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.domain.asset import AssetFilters
from kili.domain.project import ProjectId


def test_given_a_query_returning_serialized_json_it_parses_json_fields(graphql_client, http_client):
    # mocking
    def mock_graphql_execute(query, variables, **kwargs):
        if "query assets" in query:
            label = {"jsonResponse": "{}"}
            return {
                "data": [
                    {
                        "id": "fake_asset_id",
                        "jsonMetadata": '{"test": 3}',
                        "labels": [deepcopy(label)],
                        "latestLabel": deepcopy(label),
                    },
                ]
            }

        if "query countAssets" in query:
            return {"data": 1}

        if "projects(" in query:
            return {"data": [{"id": "project_id", "inputType": "IMAGE", "jsonInterface": "{}"}]}

        return None

    graphql_client.execute.side_effect = mock_graphql_execute

    # given parameters to query assets
    asset_operations = AssetOperationMixin()
    asset_operations.graphql_client = graphql_client
    asset_operations.http_client = http_client
    filters = AssetFilters(project_id=ProjectId("project_id"))
    fields = [
        "jsonMetadata",
        "labels.jsonResponse",
        "latestLabel.jsonResponse",
        "id",
    ]

    # when
    assets = list(
        asset_operations.list_assets(filters, fields, options=QueryOptions(disable_tqdm=None))
    )

    # then
    assert assets[0] == {
        "id": "fake_asset_id",
        "jsonMetadata": {"test": 3},
        "labels": [{"jsonResponse": {}}],
        "latestLabel": {"jsonResponse": {}},
    }
