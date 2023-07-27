import pytest_mock

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
