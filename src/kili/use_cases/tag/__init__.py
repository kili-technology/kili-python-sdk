"""Tag use cases."""

from collections import defaultdict
from typing import Optional

from kili.adapters.kili_api_gateway.tag.types import UpdateTagReturnData
from kili.domain.project import ProjectId
from kili.domain.tag import TagId
from kili.domain.types import ListOrTuple
from kili.use_cases.base import BaseUseCases
from kili.utils.tqdm import tqdm

# What the backend's JavaScript `trim()` removes (ECMAScript WhiteSpace and LineTerminator):
# Python's `strip()` also removes U+001C-U+001F and U+0085, and keeps U+FEFF.
_JS_WHITESPACE = (
    "\t\n\v\f\r \u00a0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a"
    "\u2028\u2029\u202f\u205f\u3000\ufeff"
)


def _same_name(label: str) -> str:
    # The backend's rule for two tag names being the same name: outer spaces and case aside.
    return label.strip(_JS_WHITESPACE).lower()


class TagUseCases(BaseUseCases):
    """Tag use cases."""

    def get_tags_of_organization(self, fields: ListOrTuple[str]) -> list[dict]:
        """Get tags of organization."""
        return self._kili_api_gateway.list_tags_by_org(fields=fields)

    def get_tags_of_project(self, project_id: ProjectId, fields: ListOrTuple[str]) -> list[dict]:
        """Get tags of project."""
        return self._kili_api_gateway.list_tags_by_project(project_id=project_id, fields=fields)

    def tag_project(
        self, project_id: ProjectId, tag_ids: ListOrTuple[TagId], disable_tqdm: Optional[bool]
    ) -> list[TagId]:
        """Assign tags to a project."""
        tags_of_orga = self._kili_api_gateway.list_tags_by_org(fields=("id",))
        tags_of_orga_ids = [tag["id"] for tag in tags_of_orga]

        tags_of_project = self._kili_api_gateway.list_tags_by_project(project_id, fields=("id",))
        tags_of_project_ids = {tag["id"] for tag in tags_of_project}

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
                # Two names of one tag ("Q4", "q4") check it once.
                tags_of_project_ids.add(tag_id)

        return ret_tags

    def untag_project(
        self,
        project_id: ProjectId,
        tag_ids: ListOrTuple[TagId],
        disable_tqdm: Optional[bool],
    ) -> list[TagId]:
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

    def get_tag_ids_from_labels(self, labels: ListOrTuple[str]) -> list[TagId]:
        """Get tag ids from labels, matched exactly, else ignoring case and outer spaces."""
        tags_of_orga = self._kili_api_gateway.list_tags_by_org(fields=("id", "label"))

        # An exact label first, so duplicates created before the backend made names unique
        # (`Urgent` and `urgent`) still resolve; else the name as the backend compares it.
        tag_label_to_id = defaultdict(list)
        tag_name_to_id = defaultdict(list)
        for tag in tags_of_orga:
            tag_label_to_id[tag["label"]].append(tag["id"])
            tag_name_to_id[_same_name(tag["label"])].append(tag["id"])

        tag_ids = []
        for label in labels:
            ids = tag_label_to_id.get(label) or tag_name_to_id.get(_same_name(label))
            if not ids:
                raise ValueError(
                    f"Tag `{label}` not found in organization with tag ids: {tags_of_orga}"
                )
            if len(ids) > 1:
                raise ValueError(
                    f"Several tags with ids ({ids}) match the label `{label}`. Please use tag ids"
                    " instead."
                )
            tag_ids.append(TagId(ids[0]))

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

    def create_tag(self, name: str, color: Optional[str]) -> dict:
        """Create a tag."""
        return self._kili_api_gateway.create_tag(label=name, color=color)
