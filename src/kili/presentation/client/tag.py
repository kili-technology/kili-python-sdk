"""Client presentation methods for tags."""

from typing import Dict, List, Literal, Optional, Sequence

from typeguard import typechecked

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
        fields: Sequence[str] = ("id", "organizationId", "label", "checkedForProjects"),
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
            else (tag_use_cases.get_tags_of_project(project_id=project_id, fields=fields))
        )

    @typechecked
    def tag_project(
        self, project_id: str, tags: Sequence[str], disable_tqdm: bool = False
    ) -> List[Dict[Literal["id"], str]]:
        """Link tags to a project.

        Args:
            project_id: Id of the project.
            tags: Sequence of tags to associate to the project.
                The value of each tag can be its name or its id.
            disable_tqdm: Whether to disable the progress bar.

        Returns:
            A list of dictionaries with the tag ids.
        """
        tag_use_cases = TagUseCases(self.kili_api_gateway)
        return tag_use_cases.tag_project(
            project_id=project_id, tags=tags, disable_tqdm=disable_tqdm
        )

    @typechecked
    def untag_project(
        self,
        project_id: str,
        tags: Optional[Sequence[str]] = None,
        all: Optional[bool] = None,  # pylint: disable=redefined-builtin
        disable_tqdm: bool = False,
    ) -> List[Dict[Literal["id"], str]]:
        """Remove tags from a project.

        Args:
            project_id: Id of the project.
            tags: Sequence of tags to remove from the project.
                The value of each tag can be its name or its id.
            all: Whether to remove all tags from the project.
            disable_tqdm: Whether to disable the progress bar.
        """
        if (tags is None and all is None) or (tags is not None and all is not None):
            raise ValueError("You must provide either `tags` or `all`.")

        tag_use_cases = TagUseCases(self.kili_api_gateway)
        return tag_use_cases.untag_project(
            project_id=project_id,
            tags=tags,
            all=all,
            disable_tqdm=disable_tqdm,
        )
