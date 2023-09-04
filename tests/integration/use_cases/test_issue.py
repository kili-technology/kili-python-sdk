"""Tests for issues use cases."""

import pytest

from kili.domain.issue import Issue
from kili.gateways.kili_api_gateway import KiliAPIGateway
from kili.use_cases.issue import IssueUseCases
from kili.use_cases.issue.types import IssueToCreateUseCaseInput


@pytest.mark.skip(reason="Waiting to implement queries")
def test_create_one_issue(kili_api_gateway: KiliAPIGateway):
    issue_use_cases = IssueUseCases(kili_api_gateway)

    # given one issue to create
    issues = [IssueToCreateUseCaseInput(label_id="label_id", text="text", object_mid="object_mid")]
    issue_entities = [Issue(id_="issue_id")]
    kili_api_gateway.create_issues.return_value(issue_entities)

    # when creating one issue
    issues = issue_use_cases.create_issues(project_id="project_id", issues=issues)

    # then
    assert issues == issue_entities
