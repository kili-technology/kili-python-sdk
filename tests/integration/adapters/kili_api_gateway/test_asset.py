from copy import deepcopy

from kili.adapters.kili_api_gateway.asset.operations_mixin import AssetOperationMixin
from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.domain.asset import AssetFilters
from kili.domain.project import ProjectId


def test_given_video_project_only_latest_label_json_response_requested_annotations_not_fetched_for_labels(
    graphql_client, http_client
):
    """For VIDEO projects, when only latestLabel.jsonResponse is requested (not labels.jsonResponse).

    The annotations fragment should only be injected into latestLabel in the GraphQL query,
    not into labels.
    """
    captured_queries = []

    def mock_graphql_execute(query, *_args, **_kwargs) -> dict:
        captured_queries.append(query)

        if "query countAssets" in query:
            return {"data": 1}

        if "projects(" in query:
            return {
                "data": [
                    {
                        "id": "project_id",
                        "inputType": "VIDEO",
                        "jsonInterface": '{"jobs": {}}',
                    }
                ]
            }

        if "query assets" in query:
            return {
                "data": [
                    {
                        "id": "fake_asset_id",
                        "labels": [{"id": "label_id"}],
                        "latestLabel": {
                            "jsonResponseUrl": "https://storage.example.com/label.json",
                        },
                        "content": "",
                        "jsonContent": "",
                        "resolution": {"width": 100, "height": 100},
                    }
                ]
            }

        return None

    mock_http_response = http_client.get.return_value
    mock_http_response.json.return_value = {"jobs": {"OBJECT_DETECTION_JOB": {}}}

    graphql_client.execute.side_effect = mock_graphql_execute

    asset_operations = AssetOperationMixin()
    asset_operations.graphql_client = graphql_client
    asset_operations.http_client = http_client
    filters = AssetFilters(project_id=ProjectId("project_id"))
    fields = ["id", "labels.id", "latestLabel.jsonResponse"]

    # when
    assets = list(
        asset_operations.list_assets(filters, fields, options=QueryOptions(disable_tqdm=None))
    )

    # then
    assert len(assets) == 1
    assert assets[0]["id"] == "fake_asset_id"
    # jsonResponse was downloaded from jsonResponseUrl and jsonResponseUrl was removed
    assert assets[0]["latestLabel"]["jsonResponse"] == {"jobs": {"OBJECT_DETECTION_JOB": {}}}
    assert "jsonResponseUrl" not in assets[0]["latestLabel"]
    # annotations were never fetched: not in latestLabel, not in labels
    assert "annotations" not in assets[0]["latestLabel"]
    assert "annotations" not in assets[0]["labels"][0]

    # then: the GraphQL query fetches jsonResponseUrl for latestLabel, not annotations
    assets_query = next(q for q in captured_queries if "query assets" in q)
    assert "jsonResponseUrl" in assets_query  # latestLabel has the jsonResponseUrl fragment
    assert "annotations" not in assets_query  # annotations fragment was not added
    assert "labels{ id}" in assets_query  # labels block only has id


def test_given_a_query_returning_serialized_json_it_parses_json_fields(graphql_client, http_client):
    # mocking
    def mock_graphql_execute(query, variables, **kwargs) -> dict | None:
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
