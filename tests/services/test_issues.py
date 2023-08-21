"""Tests for issues service."""

from kili.domain.issues import Issue
from kili.services.issue import IssueService
from kili.services.issue.types import IssueToCreateServiceInput


def test_create_one_issue(graphql_gateway):
    issue_service = IssueService(graphql_gateway)

    # given one issue to create
    issues = [IssueToCreateServiceInput(label_id="label_id", text="text", object_mid="object_mid")]
    issue_entities = [Issue(id_="issue_id")]
    graphql_gateway.create_issues.return_value(issue_entities)

    # when creating one issue
    issues = issue_service.create_issues(project_id="project_id", issues=issues)

    # then
    assert issues == issue_entities
