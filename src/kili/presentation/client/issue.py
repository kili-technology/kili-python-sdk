"""Client presentation methods for issues."""

from itertools import repeat
from typing import Dict, List, Literal, Optional

import requests
from typeguard import typechecked

from kili.gateways.kili_api_gateway import KiliAPIGateway
from kili.services.helpers import assert_all_arrays_have_same_size
from kili.use_cases.issue import IssueUseCases
from kili.use_cases.issue.types import IssueToCreateUseCaseInput
from kili.utils.logcontext import for_all_methods, log_call


@for_all_methods(log_call, exclude=["__init__"])
class IssueClientMethods:
    """Methods attached to the Kili client, to run actions on issues."""

    kili_api_gateway: KiliAPIGateway
    http_client: requests.Session

    @typechecked
    def create_issues(
        self,
        project_id: str,
        label_id_array: List[str],
        object_mid_array: Optional[List[Optional[str]]] = None,
        text_array: Optional[List[Optional[str]]] = None,
    ) -> List[Dict[Literal["id"], str]]:
        """Create an issue.

        Args:
            project_id: Id of the project.
            label_id_array: List of Ids of the labels to add an issue to.
            object_mid_array: List of mids of the objects in the labels to associate the issues to.
            text_array: List of texts to associate to the issues.

        Returns:
            A list of dictionary with the `id` key of the created issues.
        """
        assert_all_arrays_have_same_size([label_id_array, object_mid_array, text_array])
        issues = [
            IssueToCreateUseCaseInput(label_id=label_id, object_mid=object_mid, text=text)
            for (label_id, object_mid, text) in zip(
                label_id_array,
                object_mid_array or repeat(None),
                text_array or repeat(None),
            )
        ]
        issue_service = IssueUseCases(self.kili_api_gateway)
        issues_entities = issue_service.create_issues(project_id=project_id, issues=issues)
        return [{"id": issue.id_} for issue in issues_entities]
