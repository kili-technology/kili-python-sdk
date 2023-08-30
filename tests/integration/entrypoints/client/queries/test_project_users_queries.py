import pytest_mock

from kili.entrypoints.queries.project_user import QueriesProjectUser


def test_project_users_query(mocker: pytest_mock.MockFixture):
    kili = QueriesProjectUser()
    kili.graphql_client = mocked_graphql = mocker.MagicMock()
    kili.http_client = mocker.MagicMock()

    kili.project_users(project_id="fake_project_id", status="ACTIVATED")

    query, variables = mocked_graphql.execute.call_args[0]

    assert "query projectUsers" in query
    assert variables == {
        "where": {
            "id": None,
            "status": "ACTIVATED",
            "activeInProject": None,
            "project": {"id": "fake_project_id"},
            "user": {"email": None, "organization": {"id": None}},
        },
        "skip": 0,
        "first": 1,
    }
