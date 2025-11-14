"""Projects domain namespace for the Kili Python SDK.

This module provides a comprehensive interface for project-related operations
including lifecycle management, user management, workflow configuration, and versioning.
"""

from functools import cached_property
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generator,
    Iterable,
    List,
    Literal,
    Optional,
    Sequence,
    TypedDict,
)

from typeguard import typechecked
from typing_extensions import deprecated

from kili.core.enums import DemoProjectType
from kili.domain.project import (
    ComplianceTag,
    InputType,
    ProjectId,
    WorkflowStepCreate,
    WorkflowStepUpdate,
)
from kili.domain.types import ListOrTuple
from kili.domain_api.base import DomainNamespace
from kili.domain_api.namespace_utils import get_available_methods

if TYPE_CHECKING:
    from kili.client import Kili as KiliLegacy


class ProjectUserFilter(TypedDict, total=False):
    """Filter parameters for querying project users.

    Attributes:
        email: Filter by user email address.
        id: Filter by user ID.
        organization_id: Filter by organization ID.
        status_in: Filter by user status. Possible values: "ACTIVATED", "ORG_ADMIN", "ORG_SUSPENDED".
    """

    email: Optional[str]
    id: Optional[str]
    organization_id: Optional[str]
    status_in: Optional[Sequence[Literal["ACTIVATED", "ORG_ADMIN", "ORG_SUSPENDED"]]]


class ProjectFilter(TypedDict, total=False):
    """Filter parameters for querying projects.

    Attributes:
        archived: If True, only archived projects are returned. If False, only active projects are returned.
        deleted: If True, all projects are returned (including deleted ones).
        organization_id: Filter by organization ID.
        project_id: Filter by specific project ID.
        search_query: Filter projects with a title or description matching this PostgreSQL ILIKE pattern.
        starred: If True, only starred projects are returned. If False, only unstarred projects are returned.
        tags_in: Filter projects that have at least one of these tags.
        updated_at_gte: Filter projects with labels updated at or after this date.
        updated_at_lte: Filter projects with labels updated at or before this date.
    """

    archived: Optional[bool]
    deleted: Optional[bool]
    organization_id: Optional[str]
    project_id: Optional[str]
    search_query: Optional[str]
    starred: Optional[bool]
    tags_in: Optional[ListOrTuple[str]]
    updated_at_gte: Optional[str]
    updated_at_lte: Optional[str]


class UsersNamespace:
    """Nested namespace for project user management operations."""

    def __init__(self, client) -> None:
        """Initialize users namespace.

        Args:
            client: The Kili client instance
        """
        self._client = client

    @typechecked
    def create(
        self,
        project_id: str,
        email: str,
        role: Literal["ADMIN", "TEAM_MANAGER", "REVIEWER", "LABELER"] = "LABELER",
    ) -> Dict:
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
            A dictionary with the project user information.

        Examples:
            >>> projects.users.create(project_id=project_id, email='john@doe.com')
        """
        return self._client.append_to_roles(project_id=project_id, user_email=email, role=role)

    @typechecked
    def remove(self, project_id: str, email: str) -> Dict[Literal["id"], str]:
        """Remove rights for an user to access a project.

        Args:
            project_id: Identifier of the project.
            email: The email of the user.

        Returns:
            A dict with the project id.
        """
        return self._client.delete_from_roles(project_id=project_id, user_email=email)

    @typechecked
    def update(
        self,
        project_id: str,
        user_email: str,
        role: Literal["ADMIN", "TEAM_MANAGER", "REVIEWER", "LABELER"] = "LABELER",
    ) -> Dict:
        """Update properties of a role.

        To be able to change someone's role, you must be either of:
        - an admin of the project
        - a team manager of the project
        - an admin of the organization

        Args:
            project_id: Identifier of the project
            user_email: The email of the user with updated role
            role: The new role.
                Possible choices are: `ADMIN`, `TEAM_MANAGER`, `REVIEWER`, `LABELER`

        Returns:
            A dictionary with the project user information.
        """
        return self._client.update_properties_in_project_user(
            project_id=project_id, user_email=user_email, role=role
        )

    @typechecked
    def list(
        self,
        project_id: str,
        fields: ListOrTuple[str] = (
            "activated",
            "role",
            "starred",
            "user.email",
            "user.id",
            "status",
        ),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        filter: Optional[ProjectUserFilter] = None,
    ) -> Iterable[Dict]:
        """Get project users from a project."""
        filter_kwargs = filter or {}
        return self._client.project_users(
            project_id=project_id,
            fields=fields,
            first=first,
            skip=skip,
            disable_tqdm=disable_tqdm,
            as_generator=False,
            **filter_kwargs,
        )

    @typechecked
    def list_as_generator(
        self,
        project_id: str,
        fields: ListOrTuple[str] = (
            "activated",
            "role",
            "starred",
            "user.email",
            "user.id",
            "status",
        ),
        first: Optional[int] = None,
        skip: int = 0,
        filter: Optional[ProjectUserFilter] = None,
    ) -> Generator[Dict, None, None]:
        """Get project users from a project."""
        filter_kwargs = filter or {}
        return self._client.project_users(
            project_id=project_id,
            fields=fields,
            first=first,
            skip=skip,
            disable_tqdm=True,
            as_generator=True,
            **filter_kwargs,
        )

    @typechecked
    def count(
        self,
        project_id: str,
        filter: Optional[ProjectUserFilter] = None,
    ) -> int:
        """Count the number of project users with the given parameters.

        Args:
            project_id: Identifier of the project.
            filter: Optional filters for project users. See ProjectUserFilter for available fields.

        Returns:
            The number of project users matching the filter criteria.
        """
        filter_kwargs = filter or {}
        return self._client.count_project_users(project_id=project_id, **filter_kwargs)


class WorkflowNamespace:
    """Nested namespace for project workflow operations."""

    def __init__(self, client: "KiliLegacy") -> None:
        """Initialize workflow namespace.

        Args:
            client: The Kili client instance
        """
        self._client = client

    @typechecked
    def update(
        self,
        project_id: str,
        enforce_step_separation: Optional[bool] = None,
        create_steps: Optional[List[WorkflowStepCreate]] = None,
        update_steps: Optional[List[WorkflowStepUpdate]] = None,
        delete_steps: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
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
            A dict with the changed properties which indicates if the mutation was successful,
                else an error message.
        """
        return self._client.update_project_workflow(
            project_id=project_id,
            enforce_step_separation=enforce_step_separation,
            create_steps=create_steps,
            update_steps=update_steps,
            delete_steps=delete_steps,
        )

    @typechecked
    def list(self, project_id: str) -> List[Dict[str, Any]]:
        """Get steps in a project workflow.

        Args:
            project_id: Id of the project.

        Returns:
            A list with the steps of the project workflow.
        """
        return self._client.get_steps(project_id=project_id)


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

    @deprecated(
        "'projects' is a namespace, not a callable method. "
        "Use kili.projects.list() or other available methods instead."
    )
    def __call__(self, *args, **kwargs):
        """Raise a helpful error when namespace is called like a method.

        This provides guidance to users migrating from the legacy API
        where projects were accessed via kili.projects(...) to the new domain API
        where they use kili.projects.list(...) or other methods.
        """
        available_methods = get_available_methods(self)
        methods_str = ", ".join(f"kili.{self._domain_name}.{m}()" for m in available_methods)
        raise TypeError(
            f"'{self._domain_name}' is a namespace, not a callable method. "
            f"The legacy API 'kili.{self._domain_name}(...)' has been replaced with the domain API.\n"
            f"Available methods: {methods_str}\n"
            f"Nested namespaces: kili.{self._domain_name}.users, kili.{self._domain_name}.workflow\n"
            f"Example: kili.{self._domain_name}.list(...)"
        )

    @cached_property
    def users(self) -> UsersNamespace:
        """Access user management operations.

        Returns:
            UsersNamespace instance for user management operations
        """
        return UsersNamespace(self._client)

    @cached_property
    def workflow(self) -> WorkflowNamespace:
        """Access workflow-related operations.

        Returns:
            WorkflowNamespace instance for workflow operations
        """
        return WorkflowNamespace(self._client)

    @typechecked
    def list(
        self,
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
        filter: Optional[ProjectFilter] = None,
    ) -> List[Dict]:
        """Get a list of projects that match a set of criteria.

        Args:
            fields: All the fields to request among the possible fields for the projects.
            first: Maximum number of projects to return.
            skip: Number of projects to skip (they are ordered by their creation).
            disable_tqdm: If `True`, the progress bar will be disabled.
            filter: Optional filters for projects. See ProjectFilter for available fields:
                project_id, search_query, archived, starred, tags_in, organization_id,
                updated_at_gte, updated_at_lte, deleted.

        Returns:
            A list of projects matching the filter criteria.

        Examples:
            >>> # List all my projects
            >>> projects.list()
            >>> # List archived projects only
            >>> projects.list(filter={"archived": True})
        """
        filter_kwargs = filter or {}
        return self._client.projects(
            fields=fields,
            first=first,
            skip=skip,
            disable_tqdm=disable_tqdm,
            as_generator=False,
            **filter_kwargs,
        )

    @typechecked
    def list_as_generator(
        self,
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
        filter: Optional[ProjectFilter] = None,
    ) -> Generator[Dict, None, None]:
        """Get a generator of projects that match a set of criteria.

        Args:
            fields: All the fields to request among the possible fields for the projects.
            first: Maximum number of projects to return.
            skip: Number of projects to skip (they are ordered by their creation).
            disable_tqdm: If `True`, the progress bar will be disabled.
            filter: Optional filters for projects. See ProjectFilter for available fields:
                project_id, search_query, archived, starred, tags_in, organization_id,
                updated_at_gte, updated_at_lte, deleted.

        Returns:
            A generator yielding projects matching the filter criteria.

        Examples:
            >>> # Get projects as generator
            >>> for project in projects.list_as_generator():
            ...     print(project["title"])
            >>> # Get archived projects as generator
            >>> for project in projects.list_as_generator(filter={"archived": True}):
            ...     print(project["title"])
        """
        filter_kwargs = filter or {}
        return self._client.projects(
            fields=fields,
            first=first,
            skip=skip,
            disable_tqdm=disable_tqdm,
            as_generator=True,
            **filter_kwargs,
        )

    @typechecked
    def count(
        self,
        filter: Optional[ProjectFilter] = None,
    ) -> int:
        """Count the number of projects matching the given criteria.

        Args:
            filter: Optional filters for projects. See ProjectFilter for available fields:
                project_id, search_query, archived, starred, tags_in, organization_id,
                updated_at_gte, updated_at_lte, deleted.

        Returns:
            The number of projects matching the filter criteria.
        """
        filter_kwargs = filter or {}
        return self._client.count_projects(**filter_kwargs)

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
    ) -> Dict[Literal["id"], str]:
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
            A dict with the id of the created project.

        Examples:
            >>> projects.create(input_type='IMAGE', json_interface=json_interface, title='Example')
        """
        return self._client.create_project(
            title=title,
            description=description,
            input_type=input_type,
            json_interface=json_interface,
            project_id=ProjectId(project_id) if project_id is not None else None,
            tags=tags,
            compliance_tags=compliance_tags,
            from_demo_project=from_demo_project,
        )

    @typechecked
    def update_info(
        self,
        project_id: str,
        description: Optional[str] = None,
        title: Optional[str] = None,
        instructions: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update basic information of a project.

        Args:
            project_id: Identifier of the project.
            description: Description of the project.
            title: Title of the project.
            instructions: Instructions of the project.

        Returns:
            A dict with the changed properties which indicates if the mutation was successful,
                else an error message.

        Examples:
            >>> projects.update_info(
                    project_id=project_id,
                    title='New Project Title',
                    description='Updated description'
                )
        """
        return self._client.update_properties_in_project(
            project_id=project_id,
            description=description,
            title=title,
            instructions=instructions,
        )

    @typechecked
    def update_interface(
        self,
        project_id: str,
        json_interface: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """Update the interface configuration of a project.

        Args:
            project_id: Identifier of the project.
            json_interface: The json parameters of the project, see Edit your interface.

        Returns:
            A dict with the changed properties which indicates if the mutation was successful,
                else an error message.

        Examples:
            >>> projects.update_interface(
                    project_id=project_id,
                    json_interface={'jobs': {...}}
                )
        """
        return self._client.update_properties_in_project(
            project_id=project_id,
            json_interface=json_interface,
        )

    @typechecked
    def update_workflow_settings(
        self,
        project_id: str,
        can_navigate_between_assets: Optional[bool] = None,
        can_skip_asset: Optional[bool] = None,
        should_auto_assign: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Update workflow and assignment settings of a project.

        Args:
            project_id: Identifier of the project.
            can_navigate_between_assets:
                Activate / Deactivate the use of next and previous buttons in labeling interface.
            can_skip_asset: Activate / Deactivate the use of skip button in labeling interface.
            should_auto_assign: If `True`, assets are automatically assigned to users when they start annotating.

        Returns:
            A dict with the changed properties which indicates if the mutation was successful,
                else an error message.

        Examples:
            >>> projects.update_workflow_settings(
                    project_id=project_id,
                    should_auto_assign=True,
                    can_skip_asset=False
                )
        """
        return self._client.update_properties_in_project(
            project_id=project_id,
            can_navigate_between_assets=can_navigate_between_assets,
            can_skip_asset=can_skip_asset,
            should_auto_assign=should_auto_assign,
        )

    @typechecked
    def update_metadata_properties(
        self,
        project_id: str,
        metadata_properties: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """Update metadata properties of a project.

        Args:
            project_id: Identifier of the project.
            metadata_properties: Properties of the project metadata.

        Returns:
            A dict with the changed properties which indicates if the mutation was successful,
                else an error message.

        Examples:
            >>> projects.update_metadata_properties(
                    project_id=project_id,
                    metadata_properties={'key': 'value'}
                )
        """
        return self._client.update_properties_in_project(
            project_id=project_id,
            metadata_properties=metadata_properties,
        )

    @typechecked
    def update_privacy_settings(
        self,
        project_id: str,
        compliance_tags: Optional[ListOrTuple[ComplianceTag]] = None,
        should_anonymize: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Update privacy and compliance settings of a project.

        Args:
            project_id: Identifier of the project.
            compliance_tags: Compliance tags of the project.
                Compliance tags are used to categorize projects based on the sensitivity of
                the data being handled and the legal constraints associated with it.
                Possible values are: `PHI` and `PII`.
            should_anonymize: If `True`, anonymize labeler names.

        Returns:
            A dict with the changed properties which indicates if the mutation was successful,
                else an error message.

        Examples:
            >>> projects.update_privacy_settings(
                    project_id=project_id,
                    compliance_tags=['PHI'],
                    should_anonymize=True
                )
        """
        if should_anonymize is not None:
            self._client.update_project_anonymization(
                project_id=project_id, should_anonymize=should_anonymize
            )

        return self._client.update_properties_in_project(
            project_id=project_id,
            compliance_tags=compliance_tags,
        )

    @typechecked
    def archive(self, project_id: str) -> Dict[Literal["id"], str]:
        """Archive a project.

        Args:
            project_id: Identifier of the project.

        Returns:
            A dict with the id of the project.
        """
        return self._client.archive_project(project_id=project_id)

    @typechecked
    def unarchive(self, project_id: str) -> Dict[Literal["id"], str]:
        """Unarchive a project.

        Args:
            project_id: Identifier of the project

        Returns:
            A dict with the id of the project.
        """
        return self._client.unarchive_project(project_id=project_id)

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
        return self._client.copy_project(
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
    def delete(self, project_id: str) -> str:
        """Delete a project permanently.

        Args:
            project_id: Identifier of the project

        Returns:
            A string with the deleted project id.
        """
        return self._client.delete_project(project_id=project_id)
