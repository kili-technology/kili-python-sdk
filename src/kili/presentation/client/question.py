"""Client methods for questions."""
from itertools import repeat
from typing import Dict, List, Optional

from typeguard import typechecked

from kili.adapters.kili_api_gateway.question.types import QuestionsToCreateGatewayInput
from kili.domain.project import ProjectId
from kili.entrypoints.mutations.asset.helpers import get_asset_ids_or_throw_error
from kili.presentation.client.base import BaseClientMethods
from kili.presentation.client.helpers.common_validators import (
    assert_all_arrays_have_same_size,
)
from kili.use_cases.question.question_use_cases import QuestionUseCases


class QuestionClientMethods(BaseClientMethods):
    """Question client methods."""

    # pylint: disable=too-many-arguments
    @typechecked
    def create_questions(
        self,
        project_id: str,
        text_array: List[Optional[str]],
        asset_id_array: Optional[List[str]] = None,
        asset_external_id_array: Optional[List[str]] = None,
        disable_tqdm: Optional[bool] = None,
    ) -> List[Dict]:
        # pylint:disable=line-too-long
        """Create questions.

        Args:
            project_id: Id of the project.
            text_array: List of question strings.
            asset_id_array: List of the assets to add the questions to.
            asset_external_id_array: List of the assets to add the questions to. Used if `asset_id_array` is not given.
            disable_tqdm: Disable tqdm progress bar.

        Returns:
            A list of dictionaries with the `id` key of the created questions.
        """
        assert_all_arrays_have_same_size([text_array, asset_id_array])

        # TODO: move to the kili gateway
        asset_id_array = get_asset_ids_or_throw_error(
            self.kili_api_gateway, asset_id_array, asset_external_id_array, project_id
        )
        question_use_cases = QuestionUseCases(self.kili_api_gateway)

        created_questions = question_use_cases.create_questions(
            project_id=ProjectId(project_id),
            questions=(
                QuestionsToCreateGatewayInput(
                    text=text,
                    asset_id=asset_id,
                    external_id=external_id,
                )
                for text, asset_id, external_id in zip(
                    text_array,
                    asset_id_array or repeat(None),
                    asset_external_id_array or repeat(None),
                )
            ),
            disable_tqdm=disable_tqdm,
        )

        return [{"id": str(q["id"])} for q in created_questions]
