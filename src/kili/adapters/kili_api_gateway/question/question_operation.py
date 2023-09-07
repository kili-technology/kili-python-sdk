from typing import Dict, Generator, Iterable, List, Literal, Optional

from kili.adapters.kili_api_gateway.base import BaseOperationMixin
from kili.adapters.kili_api_gateway.issue.operations import GQL_CREATE_ISSUES
from kili.adapters.kili_api_gateway.question.types import QuestionsToCreateGatewayInput
from kili.core.utils.pagination import BatchIteratorBuilder
from kili.domain.project import ProjectId
from kili.domain.question import QuestionId
from kili.utils import tqdm


class QuestionOperationMixin(BaseOperationMixin):
    """Questions operations mixin."""

    def create_questions(
        self,
        project_id: ProjectId,
        questions: Iterable[QuestionsToCreateGatewayInput],
        disable_tqdm: Optional[bool],
    ) -> Generator[Dict[Literal["id"], QuestionId], None, None]:
        """Create questions."""
        created_questions: List[Dict[str, str]] = []
        total = len(questions) if isinstance(questions, list) else None
        with tqdm.tqdm(total=total, desc="Creating questions", disable=disable_tqdm) as pbar:
            asset_id_array, asset_external_id_array, text_array = list(
                *zip(*((q.asset_id, q.external_id, q.text) for q in questions))
            )
            self._get_asset_ids_or_throw_error(asset_id_array, asset_external_id_array, project_id)
            for batch_questions in BatchIteratorBuilder(
                list(zip(asset_id_array, asset_external_id_array, text_array))
            ):
                variables = {
                    "issues": [
                        {"issueNumber": 0, "type": "QUESTION", "assetId": asset_id, "text": text}
                        for (asset_id, text) in batch_questions
                    ],
                    "where": {"idIn": asset_id_array},
                }

                result = self.graphql_client.execute(GQL_CREATE_ISSUES, variables)
                batch_created_questions = result["data"]
                created_questions.extend(
                    [{"id": QuestionId(question["id"])} for question in batch_created_questions]
                )
                # batch_created_issues = result["data"]
                # created_issue_entities.extend(
                #     [IssueId(issue["id"]) for issue in batch_created_issues]
                # )
                # pbar.update(len(issues_batch))

                pbar.update(len(batch_questions))

        yield {"id": QuestionId("")}
