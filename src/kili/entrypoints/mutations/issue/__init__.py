"""Issue mutations."""

from typing import Dict, Optional

from typeguard import typechecked

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.issue.operations import GQL_CREATE_ISSUES
from kili.core.helpers import deprecate
from kili.domain.issue import IssueType
from kili.domain.label import LabelFilters, LabelId
from kili.domain.project import ProjectId
from kili.entrypoints.base import BaseOperationEntrypointMixin
from kili.use_cases.label import LabelUseCases
from kili.utils.logcontext import for_all_methods, log_call


@for_all_methods(log_call, exclude=["__init__"])
class MutationsIssue(BaseOperationEntrypointMixin):
    """Set of Issue mutations."""

    # pylint: disable=too-many-arguments
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
        type_: IssueType = "ISSUE",
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
        labels = list(
            LabelUseCases(self.kili_api_gateway).list_labels(
                filters=LabelFilters(id=LabelId(label_id), project_id=ProjectId(project_id)),
                project_id=ProjectId(project_id),
                fields=("assetId",),
                output_format="dict",
                options=QueryOptions(disable_tqdm=True, first=1),
            )
        )
        if not labels:
            raise ValueError(
                f"Label ID {label_id} does not exist in the project of ID {project_id}"
            )

        asset_id = labels[0]["assetId"]
        variables = {
            "issues": [
                {
                    "issueNumber": 0,
                    "labelID": label_id,
                    "objectMid": object_mid,
                    "type": type_,
                    "assetId": asset_id,
                    "text": text,
                }
            ],
            "where": {"id": asset_id},
        }

        result = self.graphql_client.execute(GQL_CREATE_ISSUES, variables)
        return self.format_result("data", result)[0]
