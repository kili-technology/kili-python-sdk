"""A Kili API gateway whose GraphQL client answers the workflow operations, and records them."""

import copy
from typing import Any, Optional
from unittest.mock import MagicMock

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway


def assignees(*user_ids: str) -> list[dict[str, str]]:
    return [{"id": user_id, "email": f"{user_id}@acme.com"} for user_id in user_ids]


# Two groups whose labeling steps share their name.
MULTI_GROUP_PROJECT: dict[str, Any] = {
    "workflowVersion": "V3",
    "steps": [
        {
            "id": "label-1",
            "name": "Labeling",
            "type": "DEFAULT",
            "stepGroupId": "group-1",
            "assignees": assignees("labeler"),
        },
        {
            "id": "review-1",
            "name": "Review",
            "type": "REVIEW",
            "stepGroupId": "group-1",
            "assignees": assignees("reviewer"),
        },
        {
            "id": "label-2",
            "name": "Labeling",
            "type": "DEFAULT",
            "stepGroupId": "group-2",
            "assignees": assignees("labeler"),
        },
        {
            "id": "review-2",
            "name": "Expert review",
            "type": "REVIEW",
            "stepGroupId": "group-2",
            "assignees": assignees("reviewer"),
        },
    ],
    "stepGroups": [
        {"id": "group-1", "name": "Team", "order": 1, "allowedJobNames": [], "steps": []},
        {"id": "group-2", "name": "Experts", "order": 2, "allowedJobNames": [], "steps": []},
    ],
}

MULTI_STEP_PROJECT: dict[str, Any] = {
    "workflowVersion": "V2",
    "steps": [
        {
            "id": "label",
            "name": "Labeling",
            "type": "DEFAULT",
            "stepGroupId": "default",
            "assignees": assignees("labeler"),
        },
        {
            "id": "review",
            "name": "Review",
            "type": "REVIEW",
            "stepGroupId": "default",
            "assignees": assignees("reviewer"),
        },
    ],
    "stepGroups": [{"id": "default", "name": "Default", "order": 1, "allowedJobNames": []}],
}

MEMBERS = [
    {"role": "LABELER", "user": {"id": "labeler", "email": "labeler@acme.com"}},
    {"role": "REVIEWER", "user": {"id": "reviewer", "email": "reviewer@acme.com"}},
]


class FakeWorkflowServer:
    """Answers a query with `project`, a mutation with `answer`, and records both."""

    def __init__(self, project: dict, answer: Optional[dict] = None) -> None:
        self.project = copy.deepcopy(project)
        self.answer = answer if answer is not None else {}
        self.queries: list[str] = []
        self.mutations: list[tuple[str, dict]] = []
        self.mutation_documents: list[str] = []

    def execute(self, query: str, variables: Optional[dict] = None, **_) -> dict:
        if query.lstrip().startswith("mutation"):
            name = query.split("mutation ", 1)[1].split("(", 1)[0].strip()
            self.mutations.append((name, (variables or {})["input"]))
            self.mutation_documents.append(query)
            return {"data": self.answer}
        self.queries.append(query)
        return {"data": [self.project]}

    @property
    def mutation(self) -> tuple[str, dict]:
        """The one mutation sent."""
        assert len(self.mutations) == 1, self.mutations
        return self.mutations[0]


def gateway_of(server: FakeWorkflowServer) -> KiliAPIGateway:
    graphql_client = MagicMock()
    graphql_client.execute.side_effect = server.execute
    gateway = KiliAPIGateway(graphql_client, MagicMock())
    gateway.list_activated_project_users = MagicMock(return_value=MEMBERS)
    return gateway
