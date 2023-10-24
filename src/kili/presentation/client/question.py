"""Client presentation methods for questions."""

from itertools import repeat
from typing import Dict, List, Literal, Optional

from typeguard import typechecked

from kili.domain.asset import AssetExternalId, AssetId
from kili.domain.project import ProjectId
from kili.domain.types import ListOrTuple
from kili.use_cases.question import QuestionToCreateUseCaseInput, QuestionUseCases

from .base import BaseClientMethods


class QuestionClientMethods(BaseClientMethods):
    """Client presentation methods for questions."""

    @typechecked
    def create_questions(
        self,
        project_id: str,
        text_array: ListOrTuple[Optional[str]],
        asset_id_array: Optional[ListOrTuple[str]] = None,
        asset_external_id_array: Optional[ListOrTuple[str]] = None,
    ) -> List[Dict[Literal["id"], str]]:
        # pylint:disable=line-too-long
        """Create questions.

        Args:
            project_id: Id of the project.
            text_array: List of question strings.
            asset_id_array: List of the assets to add the questions to.
            asset_external_id_array: List of the assets to add the questions to. Used if `asset_id_array` is not given.

        Returns:
            A list of dictionaries with the `id` key of the created questions.
        """
        use_case_questions = [
            QuestionToCreateUseCaseInput(
                text=text,
                asset_id=AssetId(asset_id) if asset_id else None,
                asset_external_id=AssetExternalId(asset_external_id) if asset_external_id else None,
            )
            for (text, asset_id, asset_external_id) in zip(
                text_array, asset_id_array or repeat(None), asset_external_id_array or repeat(None)
            )
        ]
        question_ids = QuestionUseCases(self.kili_api_gateway).create_questions(
            project_id=ProjectId(project_id),
            questions=use_case_questions,
        )

        return [{"id": question_id} for question_id in question_ids]
