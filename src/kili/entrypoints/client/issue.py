"""Client entrypoints methods for issues."""

from itertools import repeat
from typing import Dict, List, Literal, Optional

import requests
from typeguard import typechecked

from kili.gateways.kili_api_gateway import KiliAPIGateway
from kili.services.helpers import assert_all_arrays_have_same_size
from kili.services.issue import IssueService
from kili.services.issue.types import (
    IssueToCreateServiceInput,
    QuestionToCreateServiceInput,
)
from kili.utils.logcontext import for_all_methods, log_call


@for_all_methods(log_call, exclude=["__init__"])
class IssueEntrypoints:
    """Set of Issue mutations."""

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
            IssueToCreateServiceInput(label_id=label_id, object_mid=object_mid, text=text)
            for (label_id, object_mid, text) in zip(
                label_id_array,
                object_mid_array or repeat(None),
                text_array or repeat(None),
            )
        ]
        issue_service = IssueService(self.kili_api_gateway)
        issues_entities = issue_service.create_issues(project_id=project_id, issues=issues)
        return [{"id": issue.id_} for issue in issues_entities]

    @typechecked
    def create_questions(
        self,
        project_id: str,
        text_array: List[str],
        asset_id_array: Optional[List[str]] = None,
        asset_external_id_array: Optional[List[str]] = None,
    ) -> List[Dict[Literal["id"], str]]:
        # pylint:disable=line-too-long
        """Create questions.

        Args:
            project_id: Id of the project.
            text_array: List of question strings.
            asset_id_array: List of the assets to add the questions to.
            asset_external_id_array: List of the assets to add the questions to. Used if `asset_id_array` is not given.

        Returns:
            A list of dictionary with the `id` key of the created questions.
        """
        assert_all_arrays_have_same_size([text_array, asset_id_array])
        if asset_id_array is not None and asset_external_id_array is not None:
            raise ValueError(
                "Only one of asset_id_array and asset_external_id_array should be given"
            )
        issue_service = IssueService(self.kili_api_gateway)
        questions = [
            QuestionToCreateServiceInput(
                asset_id=asset_id, asset_external_id=asset_external_id, text=text
            )
            for (asset_id, asset_external_id, text) in zip(
                asset_id_array or repeat(None),
                asset_external_id_array or repeat(None),
                text_array,
            )
        ]
        created_questions = issue_service.create_questions(project_id, questions)
        return [{"id": question.id_} for question in created_questions]
