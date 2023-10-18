"""Tag use cases."""

from collections import defaultdict
from typing import Dict, List, Optional

from kili.adapters.kili_api_gateway.tag.types import UpdateTagReturnData
from kili.domain.project import ProjectId
from kili.domain.tag import TagId
from kili.domain.types import ListOrTuple
from kili.use_cases.base import BaseUseCases
from kili.utils.tqdm import tqdm


class TagUseCases(BaseUseCases):
    """Tag use cases."""

    def get_tags_of_organization(self, fields: ListOrTuple[str]) -> List[Dict]:
        """Get tags of organization."""
        return self._kili_api_gateway.list_tags_by_org(fields=fields)

    def get_tags_of_project(self, project_id: ProjectId, fields: ListOrTuple[str]) -> List[Dict]:
        """Get tags of project."""
        return self._kili_api_gateway.list_tags_by_project(project_id=project_id, fields=fields)

    def tag_project(
        self, project_id: ProjectId, tag_ids: ListOrTuple[TagId], disable_tqdm: Optional[bool]
    ) -> List[TagId]:
        """Assign tags to a project."""
        tags_of_orga = self._kili_api_gateway.list_tags_by_org(fields=("id",))
        tags_of_orga_ids = [tag["id"] for tag in tags_of_orga]

        tags_of_project = self._kili_api_gateway.list_tags_by_project(project_id, fields=("id",))
        tags_of_project_ids = [tag["id"] for tag in tags_of_project]

        ret_tags = []
        for tag_id in tqdm(tag_ids, desc="Tagging project", disable=disable_tqdm):
            if tag_id not in tags_of_orga_ids:
                raise ValueError(
                    f"Tag {tag_id} not found in organization with tag ids: {tags_of_orga}"
                )

            if tag_id in tags_of_project_ids:
                ret_tags.append(tag_id)
            else:
                ret_tags.append(
                    self._kili_api_gateway.check_tag(project_id=project_id, tag_id=tag_id)
                )

        return ret_tags

    def untag_project(
        self,
        project_id: ProjectId,
        tag_ids: ListOrTuple[TagId],
        disable_tqdm: Optional[bool],
    ) -> List[TagId]:
        """Remove tags from a project."""
        tag_ids_of_project = {
            tag["id"]
            for tag in self._kili_api_gateway.list_tags_by_project(
                project_id=ProjectId(project_id), fields=("id",)
            )
        }

        for tag in tag_ids:
            if tag not in tag_ids_of_project:
                raise ValueError(
                    f"Tag {tag} not found in project with tag ids: {tag_ids_of_project}"
                )

        return [
            self._kili_api_gateway.uncheck_tag(
                project_id=ProjectId(project_id), tag_id=TagId(tag_id)
            )
            for tag_id in tqdm(tag_ids, desc="Untagging project", disable=disable_tqdm)
        ]

    def get_tag_ids_from_labels(self, labels: ListOrTuple[str]) -> List[TagId]:
        """Get tag ids from labels."""
        tags_of_orga = self._kili_api_gateway.list_tags_by_org(fields=("id", "label"))

        tag_label_to_id = defaultdict(list)
        for tag in tags_of_orga:
            tag_label_to_id[tag["label"]].append(tag["id"])

        tag_ids = []
        for label in labels:
            if label not in tag_label_to_id:
                raise ValueError(
                    f"Tag `{label}` not found in organization with tag ids: {tags_of_orga}"
                )
            if len(tag_label_to_id[label]) > 1:
                raise ValueError(
                    f"Several tags with ids ({tag_label_to_id[label]}) have the same label"
                    f" `{label}`. Please use tag ids instead."
                )
            tag_ids.append(TagId(tag_label_to_id[label][0]))

        return tag_ids

    def update_tag(self, tag_id: TagId, new_tag_name: str) -> UpdateTagReturnData:
        """Update tag.

        This operation is organization-wide.
        The tag will be updated for all projects of the organization.

        Args:
            tag_id: Id of the tag to update.
            new_tag_name: New name of the tag.

        Returns:
            The updated tag.
        """
        return self._kili_api_gateway.update_tag(tag_id=tag_id, label=new_tag_name)

    def delete_tag(self, tag_id: TagId) -> bool:
        """Delete the given tag.

        This operation is organization-wide.
        The tag will no longer be proposed for projects of the organization.
        If this tag is checked for one or more projects of the organization, it will be unchecked.

        Args:
            tag_id: Id of the tag to remove.

        Returns:
            Whether the tag was successfully removed.
        """
        return self._kili_api_gateway.delete_tag(tag_id=tag_id)
