from typing import Dict, Generator, Iterable, Literal, Optional

from kili.adapters.kili_api_gateway.base import BaseOperationMixin
from kili.adapters.kili_api_gateway.question.types import QuestionsToCreateGatewayInput
from kili.domain.project import ProjectId
from kili.domain.question import QuestionId


class QuestionOperationMixin(BaseOperationMixin):
    """Questions operations mixin."""

    def create_questions(
        self,
        project_id: ProjectId,
        questions: Iterable[QuestionsToCreateGatewayInput],
        disable_tqdm: Optional[bool],
    ) -> Generator[Dict[Literal["id"], QuestionId], None, None]:
        """Create questions."""
        # created_issue_entities: List[QuestionID] = []
        # with tqdm.tqdm(total=len(issues), desc="Creating issues", disable=disable_tqdm) as pbar:
        #     for issues_batch in BatchIteratorBuilder(issues):
        #         batch_targeted_asset_ids = [issue.asset_id for issue in issues_batch]
        #         payload = {
        #             "issues": [
        #                 {
        #                     "issueNumber": 0,
        #                     "labelID": issue.label_id,
        #                     "objectMid": issue.object_mid,
        #                     "type": type_,
        #                     "assetId": issue.asset_id,
        #                     "text": issue.text,
        #                 }
        #                 for issue in issues_batch
        #             ],
        #             "where": {"idIn": batch_targeted_asset_ids},
        #         }
        #         result = self.graphql_client.execute(GQL_CREATE_ISSUES, payload)
        #         batch_created_issues = result["data"]
        #         created_issue_entities.extend(
        #             [IssueId(issue["id"]) for issue in batch_created_issues]
        #         )
        #         pbar.update(len(issues_batch))

        yield {"id": QuestionId("")}
