"""Projects domain namespace for the Kili Python SDK.

This module provides a comprehensive interface for project-related operations
including lifecycle management, user management, workflow configuration, and versioning.
"""

from functools import cached_property
from typing import (
    TYPE_CHECKING,
    Dict,
    Generator,
    Iterable,
    List,
    Literal,
    Optional,
    overload,
)

from typeguard import typechecked

from kili.core.enums import DemoProjectType
from kili.domain.project import ComplianceTag, InputType, WorkflowStepCreate, WorkflowStepUpdate
from kili.domain.types import ListOrTuple
from kili.domain_api.base import DomainNamespace
from kili.domain_v2.project import (
    IdResponse,
    ProjectRoleView,
    ProjectVersionView,
    ProjectView,
    WorkflowStepView,
    validate_project,
    validate_project_role,
    validate_project_version,
    validate_workflow_step,
)

if TYPE_CHECKING:
    from kili.client import Kili as KiliLegacy


class AnonymizationNamespace:
    """Nested namespace for project anonymization operations."""

    def __init__(self, parent: "ProjectsNamespace") -> None:
        """Initialize anonymization namespace.

        Args:
            parent: The parent ProjectsNamespace instance
        """
        self._parent = parent

    @typechecked
    def update(self, project_id: str, should_anonymize: bool = True) -> IdResponse:
        """Anonymize the project for the labelers and reviewers.

        Args:
            project_id: Identifier of the project
            should_anonymize: The value to be applied. Defaults to `True`.

        Returns:
            An IdResponse with the project id indicating if the mutation was successful.

        Examples:
            >>> projects.anonymization.update(project_id=project_id)
            >>> projects.anonymization.update(project_id=project_id, should_anonymize=False)
        """
        result = self._parent.client.update_project_anonymization(
            project_id=project_id, should_anonymize=should_anonymize
        )
        return IdResponse(result)


class UsersNamespace:
    """Nested namespace for project user management operations."""

    def __init__(self, parent: "ProjectsNamespace") -> None:
        """Initialize users namespace.

        Args:
            parent: The parent ProjectsNamespace instance
        """
        self._parent = parent

    @typechecked
    def add(
        self,
        project_id: str,
        email: str,
        role: Literal["ADMIN", "TEAM_MANAGER", "REVIEWER", "LABELER"] = "LABELER",
    ) -> ProjectRoleView:
        """Add a user to a project.

        If the user does not exist in your organization, he/she is invited and added
        both to your organization and project. This function can also be used to change
        the role of the user in the project.

        Args:
            project_id: Identifier of the project
            email: The email of the user.
                This email is used as the unique identifier of the user.
            role: The role of the user.

        Returns:
            A ProjectRoleView with the project user information.

        Examples:
            >>> projects.users.add(project_id=project_id, email='john@doe.com')
        """
        result = self._parent.client.append_to_roles(
            project_id=project_id, user_email=email, role=role
        )
        return ProjectRoleView(validate_project_role(result))

    @typechecked
    def remove(self, role_id: str) -> IdResponse:
        """Remove users by their role_id.

        Args:
            role_id: Identifier of the project user (not the ID of the user)

        Returns:
            An IdResponse with the project id.
        """
        result = self._parent.client.delete_from_roles(role_id=role_id)
        return IdResponse(result)

    @typechecked
    def update(self, role_id: str, project_id: str, user_id: str, role: str) -> ProjectRoleView:
        """Update properties of a role.

        To be able to change someone's role, you must be either of:
        - an admin of the project
        - a team manager of the project
        - an admin of the organization

        Args:
            role_id: Role identifier of the user. E.g. : 'to-be-deactivated'
            project_id: Identifier of the project
            user_id: The email or identifier of the user with updated role
            role: The new role.
                Possible choices are: `ADMIN`, `TEAM_MANAGER`, `REVIEWER`, `LABELER`

        Returns:
            A ProjectRoleView with the project user information.
        """
        result = self._parent.client.update_properties_in_role(
            role_id=role_id, project_id=project_id, user_id=user_id, role=role
        )
        return ProjectRoleView(validate_project_role(result))

    @overload
    def list(
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
            "roles.id",
            "roles.role",
            "roles.user.email",
            "roles.user.id",
        ),
        deleted: Optional[bool] = None,
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: Literal[True],
    ) -> Generator[ProjectRoleView, None, None]:
        ...

    @overload
    def list(
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
            "roles.id",
            "roles.role",
            "roles.user.email",
            "roles.user.id",
        ),
        deleted: Optional[bool] = None,
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: Literal[False] = False,
    ) -> List[ProjectRoleView]:
        ...

    @typechecked
    def list(
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
            "roles.id",
            "roles.role",
            "roles.user.email",
            "roles.user.id",
        ),
        deleted: Optional[bool] = None,
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: bool = False,
    ) -> Iterable[ProjectRoleView]:
        """Get project users from projects that match a set of criteria.

        Args:
            project_id: Select a specific project through its project_id.
            search_query: Returned projects with a title or a description matching this pattern.
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
            fields: All the fields to request among the possible fields for the project users.
            first: Maximum number of projects to return.
            skip: Number of projects to skip (they are ordered by their creation).
            disable_tqdm: If `True`, the progress bar will be disabled.
            as_generator: If `True`, a generator on the projects is returned.
            deleted: If `True`, all projects are returned (including deleted ones).

        Returns:
            A list of project users or a generator of project users if `as_generator` is `True`.
        """
        projects = self._parent.client.projects(
            project_id=project_id,
            search_query=search_query,
            should_relaunch_kpi_computation=should_relaunch_kpi_computation,
            updated_at_gte=updated_at_gte,
            updated_at_lte=updated_at_lte,
            archived=archived,
            starred=starred,
            tags_in=tags_in,
            organization_id=organization_id,
            fields=fields,
            deleted=deleted,
            first=first,
            skip=skip,
            disable_tqdm=disable_tqdm,
            as_generator=as_generator,  # pyright: ignore[reportGeneralTypeIssues]
        )

        # Extract roles from projects and wrap with ProjectRoleView
        if as_generator:

            def users_generator():
                for project in projects:
                    for role in project.get("roles", []):
                        yield ProjectRoleView(validate_project_role(role))

            return users_generator()

        users = []
        for project in projects:
            for role in project.get("roles", []):
                users.append(ProjectRoleView(validate_project_role(role)))
        return users

    @typechecked
    def count(
        self,
        project_id: Optional[str] = None,
        search_query: Optional[str] = None,
        should_relaunch_kpi_computation: Optional[bool] = None,
        updated_at_gte: Optional[str] = None,
        updated_at_lte: Optional[str] = None,
        archived: Optional[bool] = None,
        deleted: Optional[bool] = None,
    ) -> int:
        """Count the number of project users with the given parameters.

        Args:
            project_id: Select a specific project through its project_id.
            search_query: Returned projects with a title or a description matching this pattern.
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

        Returns:
            The number of project users with the parameters provided
        """
        projects = self._parent.client.projects(
            project_id=project_id,
            search_query=search_query,
            should_relaunch_kpi_computation=should_relaunch_kpi_computation,
            updated_at_gte=updated_at_gte,
            updated_at_lte=updated_at_lte,
            archived=archived,
            deleted=deleted,
            fields=("roles.id",),
            as_generator=False,
        )

        total_users = 0
        for project in projects:
            total_users += len(project.get("roles", []))
        return total_users


class WorkflowStepsNamespace:
    """Nested namespace for workflow steps operations."""

    def __init__(self, parent: "WorkflowNamespace") -> None:
        """Initialize workflow steps namespace.

        Args:
            parent: The parent WorkflowNamespace instance
        """
        self._parent = parent

    @typechecked
    def list(self, project_id: str) -> List[WorkflowStepView]:
        """Get steps in a project workflow.

        Args:
            project_id: Id of the project.

        Returns:
            A list with the steps of the project workflow.
        """
        steps = self._parent._parent.client.get_steps(project_id=project_id)  # pylint: disable=protected-access
        return [WorkflowStepView(validate_workflow_step(step)) for step in steps]


class WorkflowNamespace:
    """Nested namespace for project workflow operations."""

    def __init__(self, parent: "ProjectsNamespace") -> None:
        """Initialize workflow namespace.

        Args:
            parent: The parent ProjectsNamespace instance
        """
        self._parent = parent

    @cached_property
    def steps(self) -> WorkflowStepsNamespace:
        """Access workflow steps operations.

        Returns:
            WorkflowStepsNamespace instance for workflow steps operations
        """
        return WorkflowStepsNamespace(self)

    @typechecked
    def update(
        self,
        project_id: str,
        enforce_step_separation: Optional[bool] = None,
        create_steps: Optional[List[WorkflowStepCreate]] = None,
        update_steps: Optional[List[WorkflowStepUpdate]] = None,
        delete_steps: Optional[List[str]] = None,
    ) -> IdResponse:
        """Update properties of a project workflow.

        Args:
            project_id: Id of the project.
            enforce_step_separation: Prevents the same user from being assigned to
                multiple steps in the workflow for a same asset,
                ensuring independent review and labeling processes
            create_steps: List of steps to create in the project workflow.
            update_steps: List of steps to update in the project workflow.
            delete_steps: List of step IDs to delete from the project workflow.

        Returns:
            An IdResponse with the project id indicating if the mutation was successful.
        """
        result = self._parent.client.update_project_workflow(
            project_id=project_id,
            enforce_step_separation=enforce_step_separation,
            create_steps=create_steps,
            update_steps=update_steps,
            delete_steps=delete_steps,
        )
        return IdResponse(result)


class VersionsNamespace:
    """Nested namespace for project version operations."""

    def __init__(self, parent: "ProjectsNamespace") -> None:
        """Initialize versions namespace.

        Args:
            parent: The parent ProjectsNamespace instance
        """
        self._parent = parent

    @overload
    def get(
        self,
        project_id: str,
        first: Optional[int] = None,
        skip: int = 0,
        fields: ListOrTuple[str] = ("createdAt", "id", "content", "name", "projectId"),
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: Literal[True],
    ) -> Generator[ProjectVersionView, None, None]:
        ...

    @overload
    def get(
        self,
        project_id: str,
        first: Optional[int] = None,
        skip: int = 0,
        fields: ListOrTuple[str] = ("createdAt", "id", "content", "name", "projectId"),
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: Literal[False] = False,
    ) -> List[ProjectVersionView]:
        ...

    @typechecked
    def get(
        self,
        project_id: str,
        first: Optional[int] = None,
        skip: int = 0,
        fields: ListOrTuple[str] = ("createdAt", "id", "content", "name", "projectId"),
        disable_tqdm: Optional[bool] = None,
        *,
        as_generator: bool = False,
    ) -> Iterable[ProjectVersionView]:
        """Get a generator or a list of project versions respecting a set of criteria.

        Args:
            project_id: Filter on Id of project
            fields: All the fields to request among the possible fields for the project versions
            first: Number of project versions to query
            skip: Number of project versions to skip (they are ordered by their date
                of creation, first to last).
            disable_tqdm: If `True`, the progress bar will be disabled
            as_generator: If `True`, a generator on the project versions is returned.

        Returns:
            An iterable of project version views.
        """
        results = self._parent.client.project_version(
            project_id=project_id,
            first=first,
            skip=skip,
            fields=fields,
            disable_tqdm=disable_tqdm,
            as_generator=as_generator,  # pyright: ignore[reportGeneralTypeIssues]
        )

        # Wrap results with ProjectVersionView
        if as_generator:
            return (ProjectVersionView(validate_project_version(item)) for item in results)
        return [ProjectVersionView(validate_project_version(item)) for item in results]

    @typechecked
    def count(self, project_id: str) -> int:
        """Count the number of project versions.

        Args:
            project_id: Filter on ID of project

        Returns:
            The number of project versions with the parameters provided
        """
        return self._parent.client.count_project_versions(project_id=project_id)

    @typechecked
    def update(self, project_version_id: str, content: Optional[str]) -> ProjectVersionView:
        """Update properties of a project version.

        Args:
            project_version_id: Identifier of the project version
            content: Link to download the project version

        Returns:
            A ProjectVersionView containing the updated project version.

        Examples:
            >>> projects.versions.update(
                    project_version_id=project_version_id,
                    content='test'
                )
        """
        result = self._parent.client.update_properties_in_project_version(
            project_version_id=project_version_id, content=content
        )
        return ProjectVersionView(validate_project_version(result))


class ProjectsNamespace(DomainNamespace):
    """Projects domain namespace providing project-related operations.

    This namespace provides access to all project-related functionality
    including lifecycle management, user management, workflow configuration,
    and version management. It also provides nested namespaces for specialized
    operations on anonymization, users, workflow, and versions.
    """

    def __init__(self, client: "KiliLegacy", gateway) -> None:
        """Initialize the projects namespace.

        Args:
            client: The Kili client instance
            gateway: The KiliAPIGateway instance for API operations
        """
        super().__init__(client, gateway, "projects")

    @cached_property
    def anonymization(self) -> AnonymizationNamespace:
        """Access anonymization-related operations.

        Returns:
            AnonymizationNamespace instance for anonymization operations
        """
        return AnonymizationNamespace(self)

    @cached_property
    def users(self) -> UsersNamespace:
        """Access user management operations.

        Returns:
            UsersNamespace instance for user management operations
        """
        return UsersNamespace(self)

    @cached_property
    def workflow(self) -> WorkflowNamespace:
        """Access workflow-related operations.

        Returns:
            WorkflowNamespace instance for workflow operations
        """
        return WorkflowNamespace(self)

    @cached_property
    def versions(self) -> VersionsNamespace:
        """Access version-related operations.

        Returns:
            VersionsNamespace instance for version operations
        """
        return VersionsNamespace(self)

    @overload
    def list(
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
    ) -> Generator[ProjectView, None, None]:
        ...

    @overload
    def list(
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
    ) -> List[ProjectView]:
        ...

    @typechecked
    def list(
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
    ) -> Iterable[ProjectView]:
        """Get a generator or a list of projects that match a set of criteria.

        Args:
            project_id: Select a specific project through its project_id.
            search_query: Returned projects with a title or a description matching this
                PostgreSQL ILIKE pattern.
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
            first: Maximum number of projects to return.
            skip: Number of projects to skip (they are ordered by their creation).
            disable_tqdm: If `True`, the progress bar will be disabled.
            as_generator: If `True`, a generator on the projects is returned.
            deleted: If `True`, all projects are returned (including deleted ones).

        Returns:
            A list of projects or a generator of projects if `as_generator` is `True`.

        Examples:
            >>> # List all my projects
            >>> projects.list()
        """
        results = self.client.projects(
            project_id=project_id,
            search_query=search_query,
            should_relaunch_kpi_computation=should_relaunch_kpi_computation,
            updated_at_gte=updated_at_gte,
            updated_at_lte=updated_at_lte,
            archived=archived,
            starred=starred,
            tags_in=tags_in,
            organization_id=organization_id,
            fields=fields,
            deleted=deleted,
            first=first,
            skip=skip,
            disable_tqdm=disable_tqdm,
            as_generator=as_generator,  # pyright: ignore[reportGeneralTypeIssues]
        )

        # Wrap results with ProjectView
        if as_generator:
            return (ProjectView(validate_project(item)) for item in results)
        return [ProjectView(validate_project(item)) for item in results]

    @typechecked
    def count(
        self,
        project_id: Optional[str] = None,
        search_query: Optional[str] = None,
        should_relaunch_kpi_computation: Optional[bool] = None,
        updated_at_gte: Optional[str] = None,
        updated_at_lte: Optional[str] = None,
        archived: Optional[bool] = None,
        deleted: Optional[bool] = None,
    ) -> int:
        """Count the number of projects with a search_query.

        Args:
            project_id: Select a specific project through its project_id.
            search_query: Returned projects with a title or a description matching this
                PostgreSQL ILIKE pattern.
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

        Returns:
            The number of projects with the parameters provided
        """
        return self.client.count_projects(
            project_id=project_id,
            search_query=search_query,
            should_relaunch_kpi_computation=should_relaunch_kpi_computation,
            updated_at_gte=updated_at_gte,
            updated_at_lte=updated_at_lte,
            archived=archived,
            deleted=deleted,
        )

    @typechecked
    def create(
        self,
        title: str,
        description: str = "",
        input_type: Optional[InputType] = None,
        json_interface: Optional[Dict] = None,
        project_id: Optional[str] = None,
        tags: Optional[ListOrTuple[str]] = None,
        compliance_tags: Optional[ListOrTuple[ComplianceTag]] = None,
        from_demo_project: Optional[DemoProjectType] = None,
    ) -> IdResponse:
        """Create a project.

        Args:
            input_type: Currently, one of `IMAGE`, `PDF`, `TEXT` or `VIDEO`.
            json_interface: The json parameters of the project, see Edit your interface.
            title: Title of the project.
            description: Description of the project.
            project_id: Identifier of the project to copy.
            tags: Tags to add to the project. The tags must already exist in the organization.
            compliance_tags: Compliance tags of the project.
                Compliance tags are used to categorize projects based on the sensitivity of
                the data being handled and the legal constraints associated with it.
                Possible values are: `PHI` and `PII`.
            from_demo_project: Demo project type to create from.

        Returns:
            An IdResponse with the id of the created project.

        Examples:
            >>> projects.create(input_type='IMAGE', json_interface=json_interface, title='Example')
        """
        result = self.client.create_project(
            title=title,
            description=description,
            input_type=input_type,
            json_interface=json_interface,
            project_id=project_id,  # pyright: ignore[reportGeneralTypeIssues]
            tags=tags,
            compliance_tags=compliance_tags,
            from_demo_project=from_demo_project,
        )
        return IdResponse(result)

    @typechecked
    def update(
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
    ) -> IdResponse:
        """Update properties of a project.

        Args:
            project_id: Identifier of the project.
            can_navigate_between_assets:
                Activate / Deactivate the use of next and previous buttons in labeling interface.
            can_skip_asset: Activate / Deactivate the use of skip button in labeling interface.
            compliance_tags: Compliance tags of the project.
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
            metadata_properties: Properties of the project metadata.
            seconds_to_label_before_auto_assign: DEPRECATED, use `should_auto_assign` instead.
            should_auto_assign: If `True`, assets are automatically assigned to users when they start annotating.

        Returns:
            An IdResponse with the project id indicating if the mutation was successful.
        """
        result = self.client.update_properties_in_project(
            project_id=project_id,
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
            title=title,
            use_honeypot=use_honeypot,
            metadata_types=metadata_types,
            metadata_properties=metadata_properties,
            seconds_to_label_before_auto_assign=seconds_to_label_before_auto_assign,
            should_auto_assign=should_auto_assign,
        )
        return IdResponse(result)

    @typechecked
    def archive(self, project_id: str) -> IdResponse:
        """Archive a project.

        Args:
            project_id: Identifier of the project.

        Returns:
            An IdResponse with the id of the project.
        """
        result = self.client.archive_project(project_id=project_id)
        return IdResponse(result)

    @typechecked
    def unarchive(self, project_id: str) -> IdResponse:
        """Unarchive a project.

        Args:
            project_id: Identifier of the project

        Returns:
            An IdResponse with the id of the project.
        """
        result = self.client.unarchive_project(project_id=project_id)
        return IdResponse(result)

    @typechecked
    def copy(
        self,
        from_project_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        copy_json_interface: bool = True,
        copy_quality_settings: bool = True,
        copy_members: bool = True,
        copy_assets: bool = False,
        copy_labels: bool = False,
        disable_tqdm: Optional[bool] = None,
    ) -> str:
        """Create new project from an existing project.

        Args:
            from_project_id: Project ID to copy from.
            title: Title for the new project. Defaults to source project
                title if `None` is provided.
            description: Description for the new project. Defaults to empty string
                if `None` is provided.
            copy_json_interface: Deprecated. Always include json interface in the copy.
            copy_quality_settings: Deprecated. Always include quality settings in the copy.
            copy_members: Include members in the copy.
            copy_assets: Include assets in the copy.
            copy_labels: Include labels in the copy.
            disable_tqdm: Disable tqdm progress bars.

        Returns:
            The created project ID.

        Examples:
            >>> projects.copy(from_project_id="clbqn56b331234567890l41c0")
        """
        return self.client.copy_project(
            from_project_id=from_project_id,
            title=title,
            description=description,
            copy_json_interface=copy_json_interface,
            copy_quality_settings=copy_quality_settings,
            copy_members=copy_members,
            copy_assets=copy_assets,
            copy_labels=copy_labels,
            disable_tqdm=disable_tqdm,
        )

    @typechecked
    def delete(self, project_id: str) -> IdResponse:
        """Delete a project permanently.

        Args:
            project_id: Identifier of the project

        Returns:
            An IdResponse with the deleted project id.
        """
        result = self.client.delete_project(project_id=project_id)
        # delete_project returns a string ID, so wrap it in a dict
        return IdResponse({"id": result})
