"""Tags domain namespace for the Kili Python SDK."""

from typing import Dict, List, Literal, Optional

from typeguard import typechecked

from kili.domain.project import ProjectId
from kili.domain.tag import TagId
from kili.domain.types import ListOrTuple
from kili.domain_api.base import DomainNamespace
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

        tag_use_cases = TagUseCases(self.gateway)
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
        tag_use_cases = TagUseCases(self.gateway)
        return tag_use_cases.create_tag(name, color)

    @typechecked
    def update(
        self,
        new_name: str,
        tag_name: Optional[str] = None,
        tag_id: Optional[str] = None,
    ) -> Dict[Literal["id"], str]:
        """Update an existing tag.

        This operation is organization-wide.
        The tag will be updated for all projects of the organization.

        Args:
            tag_name: Current name of the tag to update.
            tag_id: ID of the tag to update. Use this if you have several tags with the same name.
            new_name: New name for the tag.

        Returns:
            Dictionary with the ID of the updated tag.

        Raises:
            ValueError: If neither tag_name nor tag_id is provided.

        Examples:
            >>> # Update tag by name
            >>> result = kili.tags.update(new_name="new_name", tag_name="old_name")

            >>> # Update tag by ID (more precise)
            >>> result = kili.tags.update(new_name="new_name", tag_id="tag_id_123")
        """
        if tag_id is None and tag_name is None:
            raise ValueError("Either `tag_name` or `tag_id` must be provided.")

        tag_use_cases = TagUseCases(self.gateway)
        if tag_id is None:
            # tag_name is guaranteed to be not None here due to validation above
            resolved_tag_id = tag_use_cases.get_tag_ids_from_labels(labels=[tag_name])[0]  # type: ignore[list-item]
        else:
            resolved_tag_id = TagId(tag_id)

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
        tag_name: Optional[str] = None,
        tag_id: Optional[str] = None,
    ) -> bool:
        """Delete a tag from the organization.

        This operation is organization-wide.
        The tag will no longer be proposed for projects of the organization.
        If this tag is assigned to one or more projects, it will be unassigned.

        Args:
            tag_name: Name of the tag to delete.
            tag_id: ID of the tag to delete. Use this if you have several tags with the same name.

        Returns:
            True if the tag was successfully deleted.

        Raises:
            ValueError: If neither tag_name nor tag_id is provided.

        Examples:
            >>> # Delete tag by name
            >>> success = kili.tags.delete(tag_name="unwanted")

            >>> # Delete tag by ID (more precise)
            >>> success = kili.tags.delete(tag_id="tag_id_123")
        """
        if tag_id is None and tag_name is None:
            raise ValueError("Either `tag_name` or `tag_id` must be provided.")

        tag_use_cases = TagUseCases(self.gateway)
        if tag_id is None:
            # tag_name is guaranteed to be not None here due to validation above
            resolved_tag_id = tag_use_cases.get_tag_ids_from_labels(labels=[tag_name])[0]  # type: ignore[list-item]
        else:
            resolved_tag_id = TagId(tag_id)

        return tag_use_cases.delete_tag(tag_id=resolved_tag_id)

    @typechecked
    def assign(
        self,
        project_id: str,
        tags: Optional[ListOrTuple[str]] = None,
        tag_ids: Optional[ListOrTuple[str]] = None,
        disable_tqdm: Optional[bool] = None,
    ) -> List[Dict[Literal["id"], str]]:
        """Assign tags to a project.

        This method replaces the legacy tag_project method with a more intuitive name.

        Args:
            project_id: ID of the project.
            tags: Sequence of tag labels to assign to the project.
            tag_ids: Sequence of tag IDs to assign to the project.
                Only used if `tags` is not provided.
            disable_tqdm: Whether to disable the progress bar.

        Returns:
            List of dictionaries with the assigned tag IDs.

        Raises:
            ValueError: If neither tags nor tag_ids is provided.

        Examples:
            >>> # Assign tags by name
            >>> result = kili.tags.assign(
            ...     project_id="my_project",
            ...     tags=["important", "reviewed"]
            ... )

            >>> # Assign tags by ID
            >>> result = kili.tags.assign(
            ...     project_id="my_project",
            ...     tag_ids=["tag_id_1", "tag_id_2"]
            ... )
        """
        if tags is None and tag_ids is None:
            raise ValueError("Either `tags` or `tag_ids` must be provided.")

        tag_use_cases = TagUseCases(self.gateway)

        if tag_ids is None:
            # tags is guaranteed to be not None here due to validation above
            resolved_tag_ids = tag_use_cases.get_tag_ids_from_labels(labels=tags)  # type: ignore[arg-type]
        else:
            resolved_tag_ids = [TagId(tag_id) for tag_id in tag_ids]

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
        tags: Optional[ListOrTuple[str]] = None,
        tag_ids: Optional[ListOrTuple[str]] = None,
        all: Optional[bool] = None,  # pylint: disable=redefined-builtin
        disable_tqdm: Optional[bool] = None,
    ) -> List[Dict[Literal["id"], str]]:
        """Remove tags from a project.

        This method replaces the legacy untag_project method with a more intuitive name.

        Args:
            project_id: ID of the project.
            tags: Sequence of tag labels to remove from the project.
            tag_ids: Sequence of tag IDs to remove from the project.
            all: Whether to remove all tags from the project.
            disable_tqdm: Whether to disable the progress bar.

        Returns:
            List of dictionaries with the unassigned tag IDs.

        Raises:
            ValueError: If exactly one of tags, tag_ids, or all must be provided.

        Examples:
            >>> # Remove specific tags by name
            >>> result = kili.tags.unassign(
            ...     project_id="my_project",
            ...     tags=["old_tag", "obsolete"]
            ... )

            >>> # Remove specific tags by ID
            >>> result = kili.tags.unassign(
            ...     project_id="my_project",
            ...     tag_ids=["tag_id_1", "tag_id_2"]
            ... )

            >>> # Remove all tags from project
            >>> result = kili.tags.unassign(
            ...     project_id="my_project",
            ...     all=True
            ... )
        """
        provided_args = sum([tags is not None, tag_ids is not None, all is not None])
        if provided_args != 1:
            raise ValueError("Exactly one of `tags`, `tag_ids`, or `all` must be provided.")

        tag_use_cases = TagUseCases(self.gateway)

        if tag_ids is None:
            if tags is not None:
                resolved_tag_ids = tag_use_cases.get_tag_ids_from_labels(labels=tags)
            elif all is not None:
                project_tags = tag_use_cases.get_tags_of_project(
                    project_id=ProjectId(project_id), fields=("id",)
                )
                resolved_tag_ids = [TagId(tag["id"]) for tag in project_tags]
            else:
                # This should never happen due to validation above, but for safety
                raise ValueError("Either `tags`, `tag_ids`, or `all` must be provided.")
        else:
            resolved_tag_ids = [TagId(tag_id) for tag_id in tag_ids]

        unassigned_tag_ids = tag_use_cases.untag_project(
            project_id=ProjectId(project_id),
            tag_ids=resolved_tag_ids,
            disable_tqdm=disable_tqdm,
        )

        return [{"id": str(tag_id)} for tag_id in unassigned_tag_ids]
