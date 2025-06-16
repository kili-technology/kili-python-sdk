"""Client presentation methods for projects."""
import warnings
from typing import (
    Any,
    Dict,
    Generator,
    Iterable,
    List,
    Literal,
    Optional,
    cast,
    overload,
)

from typeguard import typechecked

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.core.enums import DemoProjectType, ProjectType
from kili.domain.project import ComplianceTag, InputType, ProjectFilters, ProjectId
from kili.domain.tag import TagId
from kili.domain.types import ListOrTuple
from kili.exceptions import IncompatibleArgumentsError
from kili.presentation.client.helpers.common_validators import (
    disable_tqdm_if_as_generator,
)
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
        title: str,
        description: str = "",
        input_type: Optional[InputType] = None,
        json_interface: Optional[Dict] = None,
        project_id: Optional[ProjectId] = None,
        project_type: Optional[ProjectType] = None,
        tags: Optional[ListOrTuple[str]] = None,
        compliance_tags: Optional[ListOrTuple[ComplianceTag]] = None,
        from_demo_project: Optional[DemoProjectType] = None,
    ) -> Dict[Literal["id"], str]:
        """Create a project.

        Args:
            input_type: Currently, one of `IMAGE`, `PDF`, `TEXT` or `VIDEO`.
            json_interface: The json parameters of the project, see Edit your interface.
            title: Title of the project.
            description: Description of the project.
            project_id: Identifier of the project to copy.
            project_type: Will be deprecated soon, use from_demo_project instead.
            tags: Tags to add to the project. The tags must already exist in the organization.
            compliance_tags: Compliance tags of the project.
                Compliance tags are used to categorize projects based on the sensitivity of
                the data being handled and the legal constraints associated with it.
                Possible values are: `PHI` and `PII`.
            from_demo_project: Currently, one of:

                - `DEMO_COMPUTER_VISION_TUTORIAL`
                - `DEMO_TEXT_TUTORIAL`
                - `DEMO_PDF_TUTORIAL`
                - `VIDEO_FRAME_OBJECT_TRACKING`
                - `DEMO_SEGMENTATION_COCO`
                - `DEMO_NER`
                - `DEMO_ID_OCR`
                - `DEMO_REVIEWS`
                - `DEMO_OCR`
                - `DEMO_NER_TWEETS`
                - `DEMO_PLASTIC`
                - `DEMO_CHATBOT`
                - `DEMO_PDF`
                - `DEMO_ANIMALS`
                - `DEMO_LLM`
                - `DEMO_LLM_INSTR_FOLLOWING`
                - `DEMO_SEGMENTATION`

        Returns:
            A dict with the id of the created project.

        Examples:
            >>> kili.create_project(input_type='IMAGE', json_interface=json_interface, title='Example')

        !!! example "Recipe"
            For more detailed examples on how to create projects,
                see [the recipe](https://docs.kili-technology.com/recipes/creating-a-project).
        """
        if project_type is not None:
            warnings.warn(
                "Parameter project_type will be soon deprecated, please use from_demo_project instead.",
                DeprecationWarning,
                stacklevel=1,
            )

        if project_type is not None and from_demo_project is not None:
            raise IncompatibleArgumentsError(
                "Either provide project_type or from_demo_project. Not both at the same time."
            )

        project_id = ProjectUseCases(self.kili_api_gateway).create_project(
            input_type=input_type,
            json_interface=json_interface,
            title=title,
            description=description,
            project_id=project_id,
            project_type=project_type,
            compliance_tags=compliance_tags,
            from_demo_project=from_demo_project,
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
        organization_id: Optional[str] = None,
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
        deleted: Optional[bool] = None,
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: Literal[True],
    ) -> Generator[Dict, None, None]:
        ...

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
        organization_id: Optional[str] = None,
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
        deleted: Optional[bool] = None,
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: Literal[False] = False,
    ) -> List[Dict]:
        ...

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
        organization_id: Optional[str] = None,
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
        deleted: Optional[bool] = None,
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
            organization_id: Returned projects should belong to this organization.
            fields: All the fields to request among the possible fields for the projects.
                See [the documentation](https://docs.kili-technology.com/reference/graphql-api#project) for all possible fields.
            first: Maximum number of projects to return.
            skip: Number of projects to skip (they are ordered by their creation).
            disable_tqdm: If `True`, the progress bar will be disabled.
            as_generator: If `True`, a generator on the projects is returned.
            deleted: If `True`, all projects are returned (including deleted ones).

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

        disable_tqdm = disable_tqdm_if_as_generator(as_generator, disable_tqdm)

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
                organization_id=organization_id,
                tag_ids=tag_ids,
                deleted=deleted,
            ),
            fields,
            options=QueryOptions(disable_tqdm=disable_tqdm, first=first, skip=skip),
        )

        if as_generator:
            return projects_gen
        return list(projects_gen)

    @typechecked
    # pylint: disable=too-many-arguments,too-many-locals
    def update_properties_in_project(
        self,
        project_id: str,
        can_navigate_between_assets: Optional[bool] = None,
        can_skip_asset: Optional[bool] = None,
        compliance_tags: Optional[ListOrTuple[ComplianceTag]] = None,
        consensus_mark: Optional[float] = None,
        consensus_tot_coverage: Optional[int] = None,
        description: Optional[str] = None,
        honeypot_mark: Optional[float] = None,
        instructions: Optional[str] = None,
        input_type: Optional[InputType] = None,
        json_interface: Optional[dict] = None,
        min_consensus_size: Optional[int] = None,
        review_coverage: Optional[int] = None,
        should_relaunch_kpi_computation: Optional[bool] = None,
        title: Optional[str] = None,
        use_honeypot: Optional[bool] = None,
        metadata_types: Optional[dict] = None,
        metadata_properties: Optional[dict] = None,
        seconds_to_label_before_auto_assign: Optional[int] = None,
        should_auto_assign: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Update properties of a project.

        Args:
            project_id: Identifier of the project.
            can_navigate_between_assets:
                Activate / Deactivate the use of next and previous buttons in labeling interface.
            can_skip_asset: Activate / Deactivate the use of skip button in labeling interface.
            compliance_tags: Compliance tags of the project.
                Compliance tags are used to categorize projects based on the sensitivity of
                the data being handled and the legal constraints associated with it.
                Possible values are: `PHI` and `PII`.
            consensus_mark: Should be between 0 and 1.
            consensus_tot_coverage: Should be between 0 and 100.
                It is the percentage of the dataset that will be annotated several times.
            description: Description of the project.
            honeypot_mark: Should be between 0 and 1
            instructions: Instructions of the project.
            input_type: Currently, one of `IMAGE`, `PDF`, `TEXT` or `VIDEO`.
            json_interface: The json parameters of the project, see Edit your interface.
            min_consensus_size: Should be between 1 and 10
                Number of people that will annotate the same asset, for consensus computation.
            review_coverage: Allow to set the percentage of assets
                that will be queued in the review interface.
                Should be between 0 and 100
            should_relaunch_kpi_computation: Technical field, added to indicate changes
                in honeypot or consensus settings
            title: Title of the project
            use_honeypot: Activate / Deactivate the use of honeypot in the project
            metadata_types: DEPRECATED. Types of the project metadata.
                Should be a `dict` of metadata fields name as keys and metadata types as values.
                Currently, possible types are: `string`, `number`
            metadata_properties: Properties of the project metadata.
                Should be a `dict` of metadata fields name as keys and metadata properties as values.
                Each property is a dict with the following keys:
                    - `type`: Type of the metadata. Currently, possible types are: `string`, `number`, `date`
                    - `filterable`: If `True`, the metadata can be used as filters in project queue
                    - `visibleByLabeler`: If `True`, the metadata is visible one the asset by labelers
                    - `visibleByReviewer`: If `True`, the metadata is visible one the asset by reviewers
            seconds_to_label_before_auto_assign: DEPRECATED, use `should_auto_assign` instead.
            should_auto_assign: If `True`, assets are automatically assigned to users when they start annotating.

        Returns:
            A dict with the changed properties which indicates if the mutation was successful,
                else an error message.

        !!! example "Change Metadata Properties"
            Metadata fields are by default interpreted as `string` types and have default properties.
            To change the properties of a metadata field, you can use the `update_properties_in_project`
            function with the `metadata_properties` argument. `metadata_properties` is given as a dict
            of metadata field names as keys and metadata properties as values.

            ```python
            kili.update_properties_in_project(
                project_id = project_id,
                metadata_properties = {
                    'customConsensus': {
                        'filterable': True,
                        'type': 'number',
                        'visibleByLabeler': True,
                        'visibleByReviewer': True,
                    },
                    'sensitiveData': {
                        'filterable': True,
                        'type': 'string',
                        'visibleByLabeler': False,
                        'visibleByReviewer': True,
                    },
                    'date': {
                        'filterable': True,
                        'type': 'date',
                        'visibleByLabeler': False,
                        'visibleByReviewer': True,
                    },
                }
            )
            ```

            Not providing a property or providing an unsupported one will use the default values:
            ```
            filterable: True
            type: 'string'
            visibleByLabeler: True
            visibleByReviewer: True
            ```

        !!! note "Deprecated: Change Metadata Types"
            The `metadata_types` parameter is deprecated. Please use `metadata_properties` instead.
        """
        if seconds_to_label_before_auto_assign is not None:
            warnings.warn(
                "seconds_to_label_before_auto_assign is going to be deprecated. Please use"
                " `should_auto_assign` field instead to auto assign assets",
                DeprecationWarning,
                stacklevel=1,
            )

        if metadata_types is not None:
            warnings.warn(
                "metadata_types is going to be deprecated. Please use"
                " `metadata_properties` field instead to configure metadata properties.",
                DeprecationWarning,
                stacklevel=1,
            )

        return ProjectUseCases(self.kili_api_gateway).update_properties_in_project(
            ProjectId(project_id),
            can_navigate_between_assets=can_navigate_between_assets,
            can_skip_asset=can_skip_asset,
            compliance_tags=compliance_tags,
            consensus_mark=consensus_mark,
            consensus_tot_coverage=consensus_tot_coverage,
            description=description,
            honeypot_mark=honeypot_mark,
            instructions=instructions,
            input_type=input_type,
            json_interface=json_interface,
            min_consensus_size=min_consensus_size,
            review_coverage=review_coverage,
            should_relaunch_kpi_computation=should_relaunch_kpi_computation,
            use_honeypot=use_honeypot,
            title=title,
            metadata_types=metadata_types,
            metadata_properties=metadata_properties,
            should_auto_assign=should_auto_assign,
            seconds_to_label_before_auto_assign=seconds_to_label_before_auto_assign,
        )

    @typechecked
    # pylint: disable=too-many-arguments
    def count_projects(
        self,
        project_id: Optional[str] = None,
        search_query: Optional[str] = None,
        should_relaunch_kpi_computation: Optional[bool] = None,
        updated_at_gte: Optional[str] = None,
        updated_at_lte: Optional[str] = None,
        archived: Optional[bool] = None,
        deleted: Optional[bool] = None,
    ) -> int:
        # pylint: disable=line-too-long
        """Count the number of projects with a search_query.

        Args:
            project_id: Select a specific project through its project_id.
            search_query: Returned projects with a title or a description matching this [PostgreSQL ILIKE](https://www.postgresql.org/docs/current/functions-matching.html#FUNCTIONS-LIKE) pattern.
            should_relaunch_kpi_computation: Technical field, added to indicate changes in honeypot
                or consensus settings
            updated_at_gte: Returned projects should have a label
                whose update date is greater
                or equal to this date.
            updated_at_lte: Returned projects should have a label
                whose update date is lower or equal to this date.
            archived: If `True`, only archived projects are returned, if `False`, only active projects are returned.
                None disable this filter.
            deleted: If `True` all projects are counted (including deleted ones).

        !!! info "Dates format"
            Date strings should have format: "YYYY-MM-DD"

        Returns:
            The number of projects with the parameters provided
        """
        return ProjectUseCases(self.kili_api_gateway).count_projects(
            ProjectFilters(
                id=ProjectId(project_id) if project_id else None,
                search_query=search_query,
                should_relaunch_kpi_computation=should_relaunch_kpi_computation,
                updated_at_gte=updated_at_gte,
                updated_at_lte=updated_at_lte,
                archived=archived,
                deleted=deleted,
            )
        )
