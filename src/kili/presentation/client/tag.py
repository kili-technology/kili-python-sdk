"""Client presentation methods for tags."""

from typing import Dict, List, Literal, Optional

from typeguard import typechecked

from kili.domain.project import ProjectId
from kili.domain.tag import TagId
from kili.domain.types import ListOrTuple
from kili.use_cases.tag import TagUseCases
from kili.utils.logcontext import for_all_methods, log_call

from .base import BaseClientMethods


@for_all_methods(log_call, exclude=["__init__"])
class TagClientMethods(BaseClientMethods):
    """Methods attached to the Kili client, to run actions on tags."""

    @typechecked
    def tags(
        self,
        project_id: Optional[str] = None,
        fields: ListOrTuple[str] = ("id", "organizationId", "label", "checkedForProjects"),
    ) -> List[Dict]:
        """Get tags.

        Args:
            project_id: Id of the project to which the tags belong.
                If not provided, tags of the organization are retrieved.
            fields: Fields of tags to be retrieved.
                See the [documentation](https://docs.kili-technology.com/reference/graphql-api#tag)
                for all possible fields.

        Returns:
            A list of tags as dictionaries.
        """
        tag_use_cases = TagUseCases(self.kili_api_gateway)
        return (
            tag_use_cases.get_tags_of_organization(fields=fields)
            if project_id is None
            else tag_use_cases.get_tags_of_project(project_id=ProjectId(project_id), fields=fields)
        )

    @typechecked
    def tag_project(
        self,
        project_id: str,
        tags: Optional[ListOrTuple[str]] = None,
        tag_ids: Optional[ListOrTuple[str]] = None,
        disable_tqdm: Optional[bool] = None,
    ) -> List[Dict[Literal["id"], str]]:
        """Link tags to a project.

        Args:
            project_id: Id of the project.
            tags: Sequence of tag labels to associate to the project.
            tag_ids: Sequence of tag ids to associate to the project.
                Only used if `tags` is not provided.
            disable_tqdm: Whether to disable the progress bar.

        Returns:
            A list of dictionaries with the tag ids.
        """
        tag_use_cases = TagUseCases(self.kili_api_gateway)

        if tag_ids is None:
            if tags is None:
                raise ValueError("Either `tags` or `tag_ids` must be provided.")
            tag_ids = tag_use_cases.get_tag_ids_from_labels(
                labels=tags  # pyright: ignore[reportGeneralTypeIssues]
            )

        return [
            {"id": str(tag_id)}
            for tag_id in tag_use_cases.tag_project(
                project_id=ProjectId(project_id),
                tag_ids=tag_ids,  # pyright: ignore[reportGeneralTypeIssues]
                disable_tqdm=disable_tqdm,
            )
        ]

    @typechecked
    # pylint: disable=too-many-arguments
    def untag_project(
        self,
        project_id: str,
        tags: Optional[ListOrTuple[str]] = None,
        tag_ids: Optional[ListOrTuple[str]] = None,
        all: Optional[bool] = None,  # pylint: disable=redefined-builtin
        disable_tqdm: Optional[bool] = None,
    ) -> List[Dict[Literal["id"], str]]:
        """Remove tags from a project.

        Args:
            project_id: Id of the project.
            tags: Sequence of tag labels to remove from the project.
            tag_ids: Sequence of tag ids to remove from the project.
            all: Whether to remove all tags from the project.
            disable_tqdm: Whether to disable the progress bar.

        Returns:
            A list of dictionaries with the tag ids.

        Raises:
            ValueError: Either `tags` or `tag_ids` or `all` must be provided.
        """
        if sum([tags is not None, tag_ids is not None, all is not None]) != 1:
            raise ValueError("Only one of `tags`, `tag_ids` or `all` must be provided.")

        tag_use_cases = TagUseCases(self.kili_api_gateway)

        if tag_ids is None:
            if tags is not None:
                tag_ids = tag_use_cases.get_tag_ids_from_labels(
                    labels=tags  # pyright: ignore[reportGeneralTypeIssues]
                )
            elif all is not None:
                tag_ids = [
                    tag["id"]
                    for tag in tag_use_cases.get_tags_of_project(
                        project_id=ProjectId(project_id), fields=("id",)
                    )
                ]
            else:
                raise ValueError("Either `tags` or `tag_ids` or `all` must be provided.")

        return [
            {"id": str(tag_id)}
            for tag_id in tag_use_cases.untag_project(
                project_id=ProjectId(project_id),
                tag_ids=tag_ids,  # pyright: ignore[reportGeneralTypeIssues]
                disable_tqdm=disable_tqdm,
            )
        ]

    def update_tag(self, tag_name: str, new_tag_name: str) -> Dict[Literal["id"], str]:
        """Update a tag.

        This operation is organization-wide.
        The tag will be updated for all projects of the organization.

        Args:
            tag_name: Name of the tag to update.
            new_tag_name: New name of the tag.

        Returns:
            The id of the updated tag.
        """
        tag_use_cases = TagUseCases(self.kili_api_gateway)
        tag_id = tag_use_cases.get_tag_ids_from_labels(labels=(tag_name,))[0]
        return {
            "id": str(
                tag_use_cases.update_tag(tag_id=tag_id, new_tag_name=new_tag_name).updated_tag_id
            )
        }

    def delete_tag(self, tag_name: Optional[str] = None, tag_id: Optional[str] = None) -> bool:
        """Delete the given tag.

        This operation is organization-wide.
        The tag will no longer be proposed for projects of the organization.
        If this tag is checked for one or more projects of the organization, it will be unchecked.

        Args:
            tag_name: Name of the tag to remove.
            tag_id: Id of the tag to remove.
                Use this argument if you have several tags with the same name.

        Returns:
            Whether the tag was successfully removed.
        """
        tag_use_cases = TagUseCases(self.kili_api_gateway)
        if tag_id is None:
            if tag_name is None:
                raise ValueError("Either `tag_name` or `tag_id` must be provided.")
            tag_id = tag_use_cases.get_tag_ids_from_labels(labels=(tag_name,))[0]
        return tag_use_cases.delete_tag(tag_id=TagId(tag_id))
