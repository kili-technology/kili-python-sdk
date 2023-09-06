"""Client presentation methods for projects."""

from typing import Dict, Literal, Optional, Sequence

from typeguard import typechecked

from kili.use_cases.project.project import ProjectUseCases
from kili.use_cases.tag import TagUseCases
from kili.utils.logcontext import for_all_methods, log_call

from .base import BaseClientMethods


@for_all_methods(log_call, exclude=["__init__"])
class ProjectClientMethods(BaseClientMethods):
    """Methods attached to the Kili client, to run actions on projects."""

    @typechecked
    def create_project(
        self,
        input_type: str,
        json_interface: dict,
        title: str,
        description: str = "",
        project_type: Optional[str] = None,
        tags: Optional[Sequence[str]] = None,
    ) -> Dict[Literal["id"], str]:
        # pylint: disable=line-too-long
        """Create a project.

        Args:
            input_type: Currently, one of `IMAGE`, `PDF`, `TEXT` or `VIDEO`.
            json_interface: The json parameters of the project, see Edit your interface.
            title: Title of the project.
            description: Description of the project.
            project_type: Currently, one of:

                - `IMAGE_CLASSIFICATION_MULTI`
                - `IMAGE_CLASSIFICATION_SINGLE`
                - `IMAGE_OBJECT_DETECTION_POLYGON`
                - `IMAGE_OBJECT_DETECTION_RECTANGLE`
                - `IMAGE_OBJECT_DETECTION_SEMANTIC`
                - `IMAGE_POSE_ESTIMATION`
                - `OCR`
                - `PDF_CLASSIFICATION_MULTI`
                - `PDF_CLASSIFICATION_SINGLE`
                - `PDF_NAMED_ENTITY_RECOGNITION`
                - `PDF_OBJECT_DETECTION_RECTANGLE`
                - `SPEECH_TO_TEXT`
                - `TEXT_CLASSIFICATION_MULTI`
                - `TEXT_CLASSIFICATION_SINGLE`
                - `TEXT_NER`
                - `TEXT_TRANSCRIPTION`
                - `TIME_SERIES`
                - `VIDEO_CLASSIFICATION_SINGLE`
                - `VIDEO_FRAME_CLASSIFICATION`
                - `VIDEO_FRAME_OBJECT_TRACKING`

            tags: Tags to add to the project. The tags must already exist in the organization.

        Returns:
            A dict with the id of the created project.

        Examples:
            >>> kili.create_project(input_type='IMAGE', json_interface=json_interface, title='Example')

        !!! example "Recipe"
            For more detailed examples on how to create projects,
                see [the recipe](https://docs.kili-technology.com/recipes/creating-a-project).
        """
        project_id = ProjectUseCases(self.kili_api_gateway).create_project(
            input_type=input_type,
            json_interface=json_interface,
            title=title,
            description=description,
            project_type=project_type,
        )

        if tags is not None:
            tag_use_cases = TagUseCases(self.kili_api_gateway)
            tag_ids = tag_use_cases.get_tag_ids_from_labels(labels=tags)
            tag_use_cases.tag_project(project_id=project_id, tag_ids=tag_ids, disable_tqdm=True)

        return {"id": project_id}
