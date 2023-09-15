"""Client presentation methods for questions."""

from itertools import repeat
from typing import Dict, List, Optional

from typeguard import typechecked

from kili.use_cases.question import QuestionUseCase
from kili.use_cases.question.question_use_case import QuestionToCreateUseCaseInput

from .base import BaseClientMethods


class QuestionClientMethods(BaseClientMethods):
    @typechecked
    def create_questions(
        self,
        project_id: str,
        text_array: List[Optional[str]],
        asset_id_array: Optional[List[str]] = None,
        asset_external_id_array: Optional[List[str]] = None,
    ) -> List[Dict]:
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
                text=text, asset_id=asset_id, asset_external_id=asset_external_id
            )
            for (text, asset_id, asset_external_id) in zip(
                text_array, asset_id_array or repeat(None), asset_external_id_array or repeat(None)
            )
        ]
        questions = QuestionUseCase(self.kili_api_gateway).create_questions(
            project_id=project_id,
            questions=use_case_questions,
            external_id_array=asset_external_id_array,
        )

        return [{"id": question.id} for question in questions]
