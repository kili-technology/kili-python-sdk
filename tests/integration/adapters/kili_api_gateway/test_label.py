import pytest_mock

from kili.adapters.http_client import HttpClient
from kili.adapters.kili_api_gateway.helpers.queries import (
    PaginatedGraphQLQuery,
    QueryOptions,
)
from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.adapters.kili_api_gateway.label.operations import (
    GQL_DELETE_LABELS,
    get_append_many_labels_mutation,
    get_labels_query,
)
from kili.adapters.kili_api_gateway.label.types import (
    AppendLabelData,
    AppendManyLabelsData,
)
from kili.core.graphql.graphql_client import GraphQLClient
from kili.domain.asset import AssetExternalId, AssetFilters
from kili.domain.asset.asset import AssetId
from kili.domain.label import LabelFilters, LabelId
from kili.domain.project import ProjectId
from kili.domain.user import UserId
from kili.utils.tempfile import TemporaryDirectory
from tests.unit.adapters.kili_api_gateway.label.test_data import test_case_1


def test_given_kili_gateway_when_querying_labels__it_calls_proper_resolver(
    graphql_client: GraphQLClient,
    http_client: HttpClient,
    mocker: pytest_mock.MockerFixture,
):
    # Given
    mocker.patch.object(PaginatedGraphQLQuery, "get_number_of_elements_to_query", return_value=1)
    graphql_client.execute.return_value = {"data": [{"id": "fake_label_id"}]}
    kili_gateway = KiliAPIGateway(graphql_client=graphql_client, http_client=http_client)

    # When
    labels_gen = kili_gateway.list_labels(
        LabelFilters(
            id=LabelId("fake_label_id"),
            project_id=ProjectId("fake_proj_id"),
            asset=AssetFilters(
                external_id_in=[AssetExternalId("fake_asset_id")],
                project_id=ProjectId("fake_proj_id"),
            ),
        ),
        fields=("id",),
        options=QueryOptions(disable_tqdm=True),
    )
    _ = list(labels_gen)

    # Then
    cleaned_variables = GraphQLClient._remove_nullable_inputs(
        graphql_client.execute.call_args[0][1]
    )
    graphql_client.execute.assert_called_once_with(
        get_labels_query(" id"),
        graphql_client.execute.call_args[0][1],
    )
    assert cleaned_variables == {
        "where": {
            "id": "fake_label_id",
            "project": {"id": "fake_proj_id"},
            "asset": {
                "externalIdIn": ["fake_asset_id"],
                "project": {"id": "fake_proj_id"},
                "label": {},
                "issue": {},
            },
        },
        "first": 1,
        "skip": 0,
    }


def test_given_kili_gateway_when_i_delete_labels_then_it_calls_proper_resolver(
    graphql_client: GraphQLClient, http_client: HttpClient
):
    # Given
    kili_gateway = KiliAPIGateway(graphql_client=graphql_client, http_client=http_client)

    # When
    kili_gateway.delete_labels(ids=[LabelId("id1"), LabelId("id2")], disable_tqdm=True)

    # Then
    graphql_client.execute.assert_called_once_with(
        GQL_DELETE_LABELS,
        {"ids": ["id1", "id2"]},
    )


def test_given_kili_gateway_when_i_delete_labels_then_it_does_by_batch(
    graphql_client: GraphQLClient, http_client: HttpClient
):
    # Given
    kili_gateway = KiliAPIGateway(graphql_client=graphql_client, http_client=http_client)

    # When
    kili_gateway.delete_labels(ids=[LabelId("id1")] * 101, disable_tqdm=True)

    # Then
    assert graphql_client.execute.call_count == 2


def test_given_kili_gateway_when_adding_labels_then_it_calls_proper_resolver(
    graphql_client: GraphQLClient, http_client: HttpClient
):
    # Given
    kili_gateway = KiliAPIGateway(graphql_client=graphql_client, http_client=http_client)

    # When
    kili_gateway.append_many_labels(
        data=AppendManyLabelsData(
            label_type="PREDICTION",
            overwrite=True,
            labels_data=[
                AppendLabelData(
                    asset_id=AssetId("fake_asset_id"),
                    json_response={"CLASSIF_JOB": {}},
                    author_id=UserId("some_author_id"),
                    client_version=None,
                    seconds_to_label=42,
                    model_name="fake_model_name",
                    referenced_label_id=None,
                )
            ],
        ),
        fields=("id",),
        disable_tqdm=True,
        project_id=None,
    )

    # Then
    graphql_client.execute.asset_called_once_with(
        get_append_many_labels_mutation(" id"),
        {
            "data": {
                "labelType": "PREDICTION",
                "overwrite": True,
                "labelsData": [
                    {
                        "assetId": "fake_asset_id",
                        "authorId": "some_author_id",
                        "clientVersion": None,
                        "jsonResponse": r'{"CLASSIF_JOB": {}}',
                        "modelName": "fake_model_name",
                        "secondsToLabel": 42,
                    }
                ],
            },
            "where": {"idIn": ["fake_asset_id"], "project": {"id": None}},
        },
    )


def test_given_kili_gateway_when_adding_labels_by_batch_then_it_calls_proper_resolver(
    graphql_client: GraphQLClient, http_client: HttpClient
):
    # Given
    kili_gateway = KiliAPIGateway(graphql_client=graphql_client, http_client=http_client)

    # When
    kili_gateway.append_many_labels(
        data=AppendManyLabelsData(
            label_type="PREDICTION",
            overwrite=True,
            labels_data=[
                AppendLabelData(
                    asset_id=AssetId(f"fake_asset_id_{i}"),
                    author_id=UserId("some_author_id"),
                    client_version=None,
                    json_response={"CLASSIF_JOB": {}},
                    model_name="fake_model_name",
                    seconds_to_label=42,
                    referenced_label_id=None,
                )
                for i in range(101)
            ],
        ),
        fields=("id",),
        disable_tqdm=True,
        project_id=ProjectId("project_id"),
    )

    # Then
    assert graphql_client.execute.call_count == 2
    graphql_client.execute.asset_called_with(
        get_append_many_labels_mutation(" id"),
        {
            "data": {
                "labelType": "PREDICTION",
                "overwrite": True,
                "labelsData": [
                    {
                        "assetId": "fake_asset_id_101",
                        "jsonResponse": r'{"CLASSIF_JOB": {}}',
                        "secondsToLabel": 42,
                        "modelName": "fake_model_name",
                        "authorId": "some_author_id",
                        "clientVersion": None,
                    }
                ],
            },
            "where": {"idIn": ["fake_asset_id_101"], "project": {"id": "project_id"}},
        },
    )


def test_given_project_with_new_annotations_when_calling_list_labels_it_converts_to_json_response(
    graphql_client: GraphQLClient, http_client: HttpClient, mocker: pytest_mock.MockerFixture
):
    # Given
    with TemporaryDirectory() as tmp_dir:
        video_path = tmp_dir / "video1.mp4"
        video_path.write_bytes(b"fake video content")

        def mocked_graphql_execute(query, variables, **kwargs):
            if "assets(" in query:
                return {
                    "data": [
                        {
                            "id": "fake_asset_id",
                            "resolution": {"width": 1920, "height": 1080},
                            "content": str(video_path),
                            "jsonContent": "",
                        }
                    ]
                }
            if "projects(" in query:
                return {
                    "data": [{"inputType": "VIDEO", "jsonInterface": test_case_1.json_interface}]
                }

            if "countProjects(" in query:
                return {"data": 1}

            if "countLabels(" in query:
                return {"data": 1}

            if "labels(" in query:
                return {
                    "data": [
                        {
                            "id": "fake_label_id",
                            "jsonResponse": "{}",
                            "annotations": test_case_1.annotations,
                            "assetId": "fake_asset_id",
                        }
                    ]
                }

            raise NotImplementedError

    graphql_client.execute.side_effect = mocked_graphql_execute

    kili_gateway = KiliAPIGateway(graphql_client=graphql_client, http_client=http_client)

    # When
    labels = list(
        kili_gateway.list_labels(
            LabelFilters(project_id=ProjectId("fake_proj_id")),
            fields=("jsonResponse",),
            options=QueryOptions(disable_tqdm=True),
        )
    )

    # Then
    assert labels[0]["jsonResponse"] == test_case_1.expected_json_resp
