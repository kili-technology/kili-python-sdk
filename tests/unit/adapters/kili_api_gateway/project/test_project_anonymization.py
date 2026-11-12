from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.adapters.kili_api_gateway.project.operations import GQL_UPDATE_PROJECT_ANONYMIZATION
from kili.domain.project import ProjectId


def test_update_project_anonymization_sends_the_project_and_the_value(graphql_client, http_client):
    gateway = KiliAPIGateway(graphql_client=graphql_client, http_client=http_client)

    gateway.update_project_anonymization(ProjectId("project-id"), should_anonymize=True)

    graphql_client.execute.assert_called_once_with(
        GQL_UPDATE_PROJECT_ANONYMIZATION, {"input": {"id": "project-id", "shouldAnonymize": True}}
    )
