import pytest_mock
import requests

from kili.core.graphql.graphql_client import GraphQLClient
from kili.entrypoints.mutations.project import MutationsProject


def test_update_project_anonymization(mocker: pytest_mock.MockerFixture):
    kili = MutationsProject()
    kili.graphql_client = mocker.MagicMock()
    kili.http_client = mocker.MagicMock()
    kili.update_project_anonymization(project_id="project_id", should_anonymize=True)

    kili.graphql_client.execute.assert_called_once_with(
        "\nmutation($input: UpdateProjectAnonymizationInput!) {\n  data:"
        " updateProjectAnonymization(input: $input) {\n    \nid\n\n  }\n}\n",
        {"input": {"id": "project_id", "shouldAnonymize": True}},
    )


def test_update_properties_in_project_user_returns_the_updated_member(
    mocker: pytest_mock.MockerFixture,
):
    # Given
    kili = MutationsProject()
    kili.graphql_client = mocker.MagicMock(spec=GraphQLClient)
    kili.http_client = mocker.MagicMock(spec=requests.Session)
    member = {"role": "REVIEWER", "user": {"email": "user@kili-technology.com", "id": "user-id"}}
    kili.graphql_client.execute.return_value = {"data": member}

    # When
    result = kili.update_properties_in_project_user(
        project_id="project_id", user_email="user@kili-technology.com", role="REVIEWER"
    )

    # Then
    query, variables = kili.graphql_client.execute.call_args.args
    assert "data: updatePropertiesInRole(" in query
    assert variables == {
        "data": {"role": "REVIEWER"},
        "where": {"project": {"id": "project_id"}, "user": {"email": "user@kili-technology.com"}},
    }
    assert result == member
