from kili.services.issues import IssueUseCases
from kili.services.issues.types import IssueToCreateServiceInput


def test_create_one_issue(graphql_gateway):
    issue_use_case = IssueUseCases(graphql_gateway)

    # given one issue to create
    issues = [IssueToCreateServiceInput(label_id="label_id", text="text", object_mid="object_mid")]
    graphql_gateway.create_issues.return_value(["issue_id"])

    # when creating one issue
    issues = issue_use_case.create_issues(project_id="project_id", issues=issues)

    # then
    assert issues == ["issue_id"]
