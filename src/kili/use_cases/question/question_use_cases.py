"""Question use cases."""

from typing import Dict, Generator, Iterable, Literal, Optional

from kili.adapters.kili_api_gateway.question.types import QuestionsToCreateGatewayInput
from kili.domain.project import ProjectId
from kili.domain.question import QuestionId
from kili.use_cases.base import AbstractUseCases


class QuestionUseCases(AbstractUseCases):
    """Question use cases."""

    def create_questions(
        self,
        project_id: ProjectId,
        questions: Iterable[QuestionsToCreateGatewayInput],
        disable_tqdm: Optional[bool],
    ) -> Generator[Dict[Literal["id"], QuestionId], None, None]:
        """Create questions in project."""
        yield from self._kili_api_gateway.create_questions(
            project_id=project_id,
            questions=questions,
            disable_tqdm=disable_tqdm,
        )
