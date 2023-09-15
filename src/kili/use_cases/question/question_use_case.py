"""Question use cases."""

from dataclasses import dataclass
from typing import List, Optional

from kili.adapters.kili_api_gateway.issue.types import IssueToCreateKiliAPIGatewayInput
from kili.domain.asset.asset import AssetExternalId, AssetId
from kili.domain.project import ProjectId
from kili.domain.question import QuestionId
from kili.use_cases.base import BaseUseCases
from kili.use_cases.utils import UseCasesUtils


@dataclass
class QuestionToCreateUseCaseInput:
    """Question to create use case input."""

    text: Optional[str]
    asset_id: Optional[str]
    asset_external_id: Optional[str]


class QuestionUseCases(BaseUseCases):
    def create_questions(
        self,
        project_id: ProjectId,
        questions: List[QuestionToCreateUseCaseInput],
        external_id_array: Optional[List[AssetExternalId]] = None,
    ) -> List[QuestionId]:
        if questions[0].asset_id is not None:
            # we assume that if 1 question is not None, all there others are too
            asset_id_array = [AssetId(question.asset_id) for question in questions]  # type: ignore
        else:
            asset_id_array = None

        asset_ids = UseCasesUtils(self._kili_api_gateway).get_asset_ids_or_throw_error(
            asset_ids=asset_id_array, external_ids=external_id_array, project_id=project_id
        )

        gateway_issues = [
            IssueToCreateKiliAPIGatewayInput(
                asset_id=asset_id,
                text=question.text,
                object_mid=None,
                label_id=None,
            )
            for (asset_id, question) in zip(asset_ids, questions)
        ]
        return [
            QuestionId(str(id_))
            for id_ in self._kili_api_gateway.create_issues(
                type_="QUESTION", issues=gateway_issues, description="Creating questions"
            )
        ]

        # # with tqdm.tqdm(total=len(text_array), desc="Creating questions") as pbar:
        # #     for batch_questions in BatchIteratorBuilder(list(zip(asset_id_array, text_array))):
        # #             "issues": [
        # #                 for (asset_id, text) in batch_questions
        # #             ],
