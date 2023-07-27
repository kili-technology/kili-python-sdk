"""
Issue mutations
"""

from itertools import repeat
from typing import Dict, List, Optional

from typeguard import typechecked
from typing_extensions import Literal

from kili.authentication import KiliAuth
from kili.graphql import QueryOptions
from kili.graphql.operations.label.queries import LabelQuery, LabelWhere
from kili.mutations.asset.helpers import get_asset_ids_or_throw_error
from kili.services.helpers import assert_all_arrays_have_same_size
from kili.utils.logcontext import for_all_methods, log_call

from ...helpers import deprecate, format_result
from .helpers import get_issue_numbers, get_labels_asset_ids_map
from .queries import GQL_CREATE_ISSUES


@for_all_methods(log_call, exclude=["__init__"])
class MutationsIssue:
    """Set of Issue mutations."""

    # pylint: disable=too-many-arguments

    def __init__(self, auth: KiliAuth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    @deprecate(
        msg=(
            "append_to_issues is deprecated. Please use `create_issues` or `create_questions`"
            " instead. These new methods allow to import several issues or questions at the same"
            " time and provide better performances."
        )
    )
    @typechecked
    def append_to_issues(
        self,
        label_id: str,
        project_id: str,
        object_mid: Optional[str] = None,
        text: Optional[str] = None,
        type_: Literal["ISSUE", "QUESTION"] = "ISSUE",
    ) -> Dict:
        """Create an issue.

        !!! danger "Deprecated"
            append_to_issues is deprecated.
            Please use `create_issues` or `create_questions` instead.
            These new methods allow to import several issues or questions at the same time
            and provide better performances.

        Args:
            label_id: Id of the label to add an issue to
            object_mid: Mid of the object in the label to associate the issue to
            type_: type of the issue to add. Can be either "ISSUE" or "QUESTION"
            text: If given, write a comment related to the issue
            project_id: Id of the project

        Returns:
            A result object which indicates if the mutation was successful,
                or an error message.
        """
        issue_number = get_issue_numbers(self.auth, project_id, type_, 1)[0]
        try:
            options = QueryOptions(disable_tqdm=True)
            where = LabelWhere(
                project_id=project_id,
                label_id=label_id,
            )
            asset_id: str = list(
                LabelQuery(self.auth.client, self.auth.ssl_verify)(
                    where=where, fields=["labelOf.id"], options=options
                )
            )[0]["labelOf"]["id"]
        except:
            # pylint: disable=raise-missing-from
            raise ValueError(
                f"Label ID {label_id} does not exist in the project of ID {project_id}"
            )
        variables = {
            "issues": [
                {
                    "issueNumber": issue_number,
                    "labelID": label_id,
                    "objectMid": object_mid,
                    "type": type_,
                    "assetId": asset_id,
                    "text": text,
                }
            ],
            "where": {"id": asset_id},
        }

        result = self.auth.client.execute(GQL_CREATE_ISSUES, variables)
        return format_result("data", result, None, self.auth.ssl_verify)[0]

    @typechecked
    def create_issues(
        self,
        project_id: str,
        label_id_array: List[str],
        object_mid_array: Optional[List[Optional[str]]] = None,
        text_array: Optional[List[Optional[str]]] = None,
    ) -> List[Dict]:
        """Create an issue.

        Args:
            project_id: Id of the project
            label_id_array: list of Ids of the labels to add an issue to
            object_mid: list of Mid of the objects in the labels to associate the issue to
            text_array: list of texts to associate to the issues

        Returns:
            A list of dictionary with the `id` key of the created issues
        """
        assert_all_arrays_have_same_size([label_id_array, object_mid_array, text_array])
        issue_number_array = get_issue_numbers(self.auth, project_id, "ISSUE", len(label_id_array))
        label_asset_ids_map = get_labels_asset_ids_map(self.auth, project_id, label_id_array)
        variables = {
            "issues": [
                {
                    "issueNumber": issue_number,
                    "labelID": label_id,
                    "objectMid": object_mid,
                    "type": "ISSUE",
                    "assetId": label_asset_ids_map[label_id],
                    "text": text,
                }
                for (issue_number, label_id, object_mid, text) in zip(
                    issue_number_array,
                    label_id_array,
                    object_mid_array or repeat(None),
                    text_array or repeat(None),
                )
            ],
            "where": {"idIn": list(label_asset_ids_map.values())},
        }

        result = self.auth.client.execute(GQL_CREATE_ISSUES, variables)
        return format_result("data", result, None, self.auth.ssl_verify)

    @typechecked
    def create_questions(
        self,
        project_id: str,
        text_array: List[Optional[str]],
        asset_id_array: Optional[List[str]] = None,
        asset_external_id_array: Optional[List[str]] = None,
    ) -> List[Dict]:
        """Create an issue.

        Args:
            project_id: Id of the project
            text_array: list of the question text
            asset_id_array: list of the assets to add a question to

        Returns:
            A list of dictionary with the `id` key of the created questions
        """
        assert_all_arrays_have_same_size([text_array, asset_id_array])
        issue_number_array = get_issue_numbers(self.auth, project_id, "QUESTION", len(text_array))
        asset_id_array = get_asset_ids_or_throw_error(
            self.auth, asset_id_array, asset_external_id_array, project_id
        )
        variables = {
            "issues": [
                {"issueNumber": issue_number, "type": "QUESTION", "assetId": asset_id, "text": text}
                for (asset_id, text, issue_number) in zip(
                    asset_id_array, text_array, issue_number_array
                )
            ],
            "where": {"idIn": asset_id_array},
        }

        result = self.auth.client.execute(GQL_CREATE_ISSUES, variables)
        return format_result("data", result, None, self.auth.ssl_verify)
