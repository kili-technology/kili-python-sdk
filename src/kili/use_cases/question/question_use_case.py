"""Question use cases."""

from dataclasses import dataclass
from typing import List, Optional, cast

from kili.adapters.kili_api_gateway.issue.types import IssueToCreateKiliAPIGatewayInput
from kili.domain.asset import AssetExternalId, AssetId
from kili.domain.project import ProjectId
from kili.domain.question import QuestionId
from kili.use_cases.asset.utils import AssetUseCasesUtils
from kili.use_cases.base import BaseUseCases


@dataclass
class QuestionToCreateUseCaseInput:
    """Question to create use case input."""

    text: Optional[str]
    asset_id: Optional[AssetId]
    asset_external_id: Optional[AssetExternalId]


class QuestionUseCases(BaseUseCases):
    """Question use cases."""

    def create_questions(
        self,
        project_id: ProjectId,
        questions: List[QuestionToCreateUseCaseInput],
    ) -> List[QuestionId]:
        """Create questions."""
        if questions[0].asset_id is not None:
            # we assume that if 1 question asset Id is not None, all there others are too
            asset_id_array = [cast(AssetId, question.asset_id) for question in questions]
            external_id_array = None
        else:
            asset_id_array = None
            external_id_array = [
                cast(AssetExternalId, question.asset_external_id) for question in questions
            ]

        asset_ids = AssetUseCasesUtils(self._kili_api_gateway).get_asset_ids_or_throw_error(
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
