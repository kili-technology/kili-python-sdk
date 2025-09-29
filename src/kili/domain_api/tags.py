"""Tags domain namespace for the Kili Python SDK."""

from typing import Dict, List, Literal, Optional

from typeguard import typechecked
from typing_extensions import deprecated

from kili.domain.project import ProjectId
from kili.domain.tag import TagId
from kili.domain.types import ListOrTuple
from kili.domain_api.base import DomainNamespace
from kili.domain_api.namespace_utils import get_available_methods
from kili.use_cases.tag import TagUseCases


class TagsNamespace(DomainNamespace):
    """Tags domain namespace providing tag-related operations.

    This namespace provides access to all tag-related functionality
    including creating, updating, querying, and managing tags and their assignments to projects.

    The namespace provides the following main operations:
    - list(): Query and list tags (organization-wide or project-specific)
    - create(): Create new tags in the organization
    - update(): Update existing tags
    - delete(): Delete tags from the organization
    - assign(): Assign tags to projects (replaces tag_project)
    - unassign(): Remove tags from projects (replaces untag_project)

    Examples:
        >>> kili = Kili()
        >>> # List organization tags
        >>> tags = kili.tags.list()

        >>> # List project-specific tags
        >>> project_tags = kili.tags.list(project_id="my_project")

        >>> # Create a new tag
        >>> result = kili.tags.create(name="important", color="#ff0000")

        >>> # Update a tag
        >>> kili.tags.update(tag_name="old_name", new_name="new_name")

        >>> # Assign tags to a project
        >>> kili.tags.assign(
        ...     project_id="my_project",
        ...     tags=["important", "reviewed"]
        ... )

        >>> # Remove tags from a project
        >>> kili.tags.unassign(
        ...     project_id="my_project",
        ...     tags=["old_tag"]
        ... )

        >>> # Delete a tag
        >>> kili.tags.delete(tag_name="unwanted")
    """

    def __init__(self, client, gateway):
        """Initialize the tags namespace.

        Args:
            client: The Kili client instance
            gateway: The KiliAPIGateway instance for API operations
        """
        super().__init__(client, gateway, "tags")

    @deprecated(
        "'tags' is a namespace, not a callable method. "
        "Use kili.tags.list() or other available methods instead."
    )
    def __call__(self, *args, **kwargs):
        """Raise a helpful error when namespace is called like a method.

        This provides guidance to users migrating from the legacy API
        where tags were accessed via kili.tags(...) to the new domain API
        where they use kili.tags.list(...) or other methods.
        """
        available_methods = get_available_methods(self)
        methods_str = ", ".join(f"kili.{self._domain_name}.{m}()" for m in available_methods)
        raise TypeError(
            f"'{self._domain_name}' is a namespace, not a callable method. "
            f"The legacy API 'kili.{self._domain_name}(...)' has been replaced with the domain API.\n"
            f"Available methods: {methods_str}\n"
            f"Example: kili.{self._domain_name}.list(...)"
        )

    @typechecked
    def list(
        self,
        project_id: Optional[str] = None,
        fields: Optional[ListOrTuple[str]] = None,
    ) -> List[Dict]:
        """List tags from the organization or a specific project.

        Args:
            project_id: If provided, returns tags assigned to this project.
                If None, returns all organization tags.
            fields: List of fields to return. If None, returns default fields.
                See the API documentation for available fields.

        Returns:
            List of tags as dictionaries.

        Examples:
            >>> # Get all organization tags
            >>> tags = kili.tags.list()

            >>> # Get tags for a specific project
            >>> project_tags = kili.tags.list(project_id="my_project")

            >>> # Get specific fields only
            >>> tags = kili.tags.list(fields=["id", "label", "color"])
        """
        if fields is None:
            fields = ("id", "organizationId", "label", "checkedForProjects")

        tag_use_cases = TagUseCases(self._gateway)
        return (
            tag_use_cases.get_tags_of_organization(fields=fields)
            if project_id is None
            else tag_use_cases.get_tags_of_project(project_id=ProjectId(project_id), fields=fields)
        )

    @typechecked
    def create(
        self,
        name: str,
        color: Optional[str] = None,
    ) -> Dict[Literal["id"], str]:
        """Create a new tag in the organization.

        This operation is organization-wide.
        The tag will be proposed for projects of the organization.

        Args:
            name: Name of the tag to create.
            color: Color of the tag to create. If not provided, a default color will be used.

        Returns:
            Dictionary with the ID of the created tag.

        Examples:
            >>> # Create a simple tag
            >>> result = kili.tags.create(name="reviewed")

            >>> # Create a tag with a specific color
            >>> result = kili.tags.create(name="important", color="#ff0000")
        """
        tag_use_cases = TagUseCases(self._gateway)
        return tag_use_cases.create_tag(name, color)

    @typechecked
    def update(
        self,
        tag_name: str,
        new_name: str,
    ) -> Dict[Literal["id"], str]:
        """Update an existing tag.

        This operation is organization-wide.
        The tag will be updated for all projects of the organization.

        Args:
            tag_name: Current name of the tag to update.
            new_name: New name for the tag.

        Returns:
            Dictionary with the ID of the updated tag.

        Examples:
            >>> # Update tag by name
            >>> result = kili.tags.update(tag_name="old_name", new_name="new_name")
        """
        tag_use_cases = TagUseCases(self._gateway)
        resolved_tag_id = tag_use_cases.get_tag_ids_from_labels(labels=[tag_name])[0]

        return {
            "id": str(
                tag_use_cases.update_tag(
                    tag_id=resolved_tag_id, new_tag_name=new_name
                ).updated_tag_id
            )
        }

    @typechecked
    def delete(
        self,
        tag_name: str,
    ) -> bool:
        """Delete a tag from the organization.

        This operation is organization-wide.
        The tag will no longer be proposed for projects of the organization.
        If this tag is assigned to one or more projects, it will be unassigned.

        Args:
            tag_name: Name of the tag to delete.

        Returns:
            True if the tag was successfully deleted.

        Examples:
            >>> # Delete tag by name
            >>> success = kili.tags.delete(tag_name="unwanted")
        """
        tag_use_cases = TagUseCases(self._gateway)
        resolved_tag_id = tag_use_cases.get_tag_ids_from_labels(labels=[tag_name])[0]

        return tag_use_cases.delete_tag(tag_id=resolved_tag_id)

    @typechecked
    def assign(
        self,
        project_id: str,
        tag: Optional[str] = None,
        tags: Optional[ListOrTuple[str]] = None,
        disable_tqdm: Optional[bool] = None,
    ) -> List[Dict[Literal["id"], str]]:
        """Assign tags to a project.

        This method replaces the legacy tag_project method with a more intuitive name.

        Args:
            project_id: ID of the project.
            tag: Tag label to assign to the project.
            tags: Sequence of tag labels to assign to the project.
            disable_tqdm: Whether to disable the progress bar.

        Returns:
            List of dictionaries with the assigned tag IDs.

        Raises:
            ValueError: If neither tag nor tags is provided.

        Examples:
            >>> # Assign single tag by name
            >>> result = kili.tags.assign(
            ...     project_id="my_project",
            ...     tag="important"
            ... )

            >>> # Assign multiple tags by name
            >>> result = kili.tags.assign(
            ...     project_id="my_project",
            ...     tags=["important", "reviewed"]
            ... )
        """
        # Convert singular to plural
        if tag is not None:
            tags = [tag]

        if tags is None:
            raise ValueError("Either `tag` or `tags` must be provided.")

        tag_use_cases = TagUseCases(self._gateway)
        resolved_tag_ids = tag_use_cases.get_tag_ids_from_labels(labels=tags)

        assigned_tag_ids = tag_use_cases.tag_project(
            project_id=ProjectId(project_id),
            tag_ids=resolved_tag_ids,
            disable_tqdm=disable_tqdm,
        )

        return [{"id": str(tag_id)} for tag_id in assigned_tag_ids]

    @typechecked
    def unassign(
        self,
        project_id: str,
        tag: Optional[str] = None,
        tags: Optional[ListOrTuple[str]] = None,
        all: Optional[bool] = None,  # pylint: disable=redefined-builtin
        disable_tqdm: Optional[bool] = None,
    ) -> List[Dict[Literal["id"], str]]:
        """Remove tags from a project.

        This method replaces the legacy untag_project method with a more intuitive name.

        Args:
            project_id: ID of the project.
            tag: Tag label to remove from the project.
            tags: Sequence of tag labels to remove from the project.
            all: Whether to remove all tags from the project.
            disable_tqdm: Whether to disable the progress bar.

        Returns:
            List of dictionaries with the unassigned tag IDs.

        Raises:
            ValueError: If exactly one of tag, tags, or all must be provided.

        Examples:
            >>> # Remove single tag by name
            >>> result = kili.tags.unassign(
            ...     project_id="my_project",
            ...     tag="old_tag"
            ... )

            >>> # Remove multiple tags by name
            >>> result = kili.tags.unassign(
            ...     project_id="my_project",
            ...     tags=["old_tag", "obsolete"]
            ... )

            >>> # Remove all tags from project
            >>> result = kili.tags.unassign(
            ...     project_id="my_project",
            ...     all=True
            ... )
        """
        # Convert singular to plural
        if tag is not None:
            tags = [tag]

        provided_args = sum([tags is not None, all is not None])
        if provided_args != 1:
            raise ValueError("Exactly one of `tag`, `tags`, or `all` must be provided.")

        tag_use_cases = TagUseCases(self._gateway)

        if tags is not None:
            resolved_tag_ids = tag_use_cases.get_tag_ids_from_labels(labels=tags)
        elif all is not None:
            project_tags = tag_use_cases.get_tags_of_project(
                project_id=ProjectId(project_id), fields=("id",)
            )
            resolved_tag_ids = [TagId(tag["id"]) for tag in project_tags]
        else:
            # This should never happen due to validation above, but for safety
            raise ValueError("Either `tags` or `all` must be provided.")

        unassigned_tag_ids = tag_use_cases.untag_project(
            project_id=ProjectId(project_id),
            tag_ids=resolved_tag_ids,
            disable_tqdm=disable_tqdm,
        )

        return [{"id": str(tag_id)} for tag_id in unassigned_tag_ids]
