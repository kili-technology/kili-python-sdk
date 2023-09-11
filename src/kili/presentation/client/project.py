"""Client presentation methods for projects."""

from typing import Dict, Generator, Iterable, List, Literal, Optional, cast, overload

from typeguard import typechecked

from kili.core.enums import ProjectType
from kili.domain.project import InputType, ProjectFilters, ProjectId
from kili.domain.tag import TagId
from kili.domain.types import ListOrTuple
from kili.use_cases.project.project import ProjectUseCases
from kili.use_cases.tag import TagUseCases
from kili.utils.logcontext import for_all_methods, log_call

from .base import BaseClientMethods


@for_all_methods(log_call, exclude=["__init__"])
class ProjectClientMethods(BaseClientMethods):
    """Methods attached to the Kili client, to run actions on projects."""

    @typechecked
    # pylint: disable=too-many-arguments
    def create_project(
        self,
        input_type: InputType,
        json_interface: Dict,
        title: str,
        description: str = "",
        project_type: Optional[ProjectType] = None,
        tags: Optional[ListOrTuple[str]] = None,
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
            tag_use_cases.tag_project(
                project_id=project_id, tag_ids=cast(ListOrTuple[TagId], tag_ids), disable_tqdm=True
            )

        return {"id": project_id}

    @overload
    # pylint: disable=too-many-arguments
    def projects(
        self,
        project_id: Optional[str] = None,
        search_query: Optional[str] = None,
        should_relaunch_kpi_computation: Optional[bool] = None,
        updated_at_gte: Optional[str] = None,
        updated_at_lte: Optional[str] = None,
        archived: Optional[bool] = None,
        starred: Optional[bool] = None,
        tags_in: Optional[ListOrTuple[str]] = None,
        fields: ListOrTuple[str] = (
            "consensusTotCoverage",
            "id",
            "inputType",
            "jsonInterface",
            "minConsensusSize",
            "reviewCoverage",
            "roles.id",
            "roles.role",
            "roles.user.email",
            "roles.user.id",
            "title",
        ),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: Literal[True],
    ) -> Generator[Dict, None, None]: ...

    @overload
    # pylint: disable=too-many-arguments
    def projects(
        self,
        project_id: Optional[str] = None,
        search_query: Optional[str] = None,
        should_relaunch_kpi_computation: Optional[bool] = None,
        updated_at_gte: Optional[str] = None,
        updated_at_lte: Optional[str] = None,
        archived: Optional[bool] = None,
        starred: Optional[bool] = None,
        tags_in: Optional[ListOrTuple[str]] = None,
        fields: ListOrTuple[str] = (
            "consensusTotCoverage",
            "id",
            "inputType",
            "jsonInterface",
            "minConsensusSize",
            "reviewCoverage",
            "roles.id",
            "roles.role",
            "roles.user.email",
            "roles.user.id",
            "title",
        ),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: Literal[False] = False,
    ) -> List[Dict]: ...

    @typechecked
    # pylint: disable=too-many-arguments,too-many-locals
    def projects(
        self,
        project_id: Optional[str] = None,
        search_query: Optional[str] = None,
        should_relaunch_kpi_computation: Optional[bool] = None,
        updated_at_gte: Optional[str] = None,
        updated_at_lte: Optional[str] = None,
        archived: Optional[bool] = None,
        starred: Optional[bool] = None,
        tags_in: Optional[ListOrTuple[str]] = None,
        fields: ListOrTuple[str] = (
            "consensusTotCoverage",
            "id",
            "inputType",
            "jsonInterface",
            "minConsensusSize",
            "reviewCoverage",
            "roles.id",
            "roles.role",
            "roles.user.email",
            "roles.user.id",
            "title",
        ),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: bool = False,
    ) -> Iterable[Dict]:
        # pylint: disable=line-too-long
        """Get a generator or a list of projects that match a set of criteria.

        Args:
            project_id: Select a specific project through its project_id.
            search_query: Returned projects with a title or a description matching this [PostgreSQL ILIKE](https://www.postgresql.org/docs/current/functions-matching.html#FUNCTIONS-LIKE) pattern.
            should_relaunch_kpi_computation: Deprecated, do not use.
            updated_at_gte: Returned projects should have a label whose update date is greater or equal
                to this date.
            updated_at_lte: Returned projects should have a label whose update date is lower or equal to this date.
            archived: If `True`, only archived projects are returned, if `False`, only active projects are returned.
                `None` disables this filter.
            starred: If `True`, only starred projects are returned, if `False`, only unstarred projects are returned.
                `None` disables this filter.
            tags_in: Returned projects should have at least one of these tags.
            fields: All the fields to request among the possible fields for the projects.
                See [the documentation](https://docs.kili-technology.com/reference/graphql-api#project) for all possible fields.
            first: Maximum number of projects to return.
            skip: Number of projects to skip (they are ordered by their creation).
            disable_tqdm: If `True`, the progress bar will be disabled.
            as_generator: If `True`, a generator on the projects is returned.

        !!! info "Dates format"
            Date strings should have format: "YYYY-MM-DD"

        Returns:
            A list of projects or a generator of projects if `as_generator` is `True`.

        Examples:
            >>> # List all my projects
            >>> kili.projects()
        """
        tag_ids = (
            TagUseCases(self.kili_api_gateway).get_tag_ids_from_labels(tags_in) if tags_in else None
        )

        projects_gen = ProjectUseCases(self.kili_api_gateway).list_projects(
            ProjectFilters(
                id=ProjectId(project_id) if project_id else None,
                archived=archived,
                search_query=search_query,
                should_relaunch_kpi_computation=should_relaunch_kpi_computation,
                starred=starred,
                updated_at_gte=updated_at_gte,
                updated_at_lte=updated_at_lte,
                created_at_gte=None,
                created_at_lte=None,
                tag_ids=tag_ids,
            ),
            fields,
            first,
            skip,
            disable_tqdm,
        )

        if as_generator:
            return projects_gen
        return list(projects_gen)
