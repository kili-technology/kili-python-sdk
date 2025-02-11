"""Copy project implementation."""

import itertools
import logging
from typing import TYPE_CHECKING, Optional

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.project.types import CopyProjectInput
from kili.domain.asset import AssetFilters
from kili.domain.label import LabelFilters
from kili.domain.project import ProjectId

if TYPE_CHECKING:
    from kili.client import Kili


class ProjectCopier:  # pylint: disable=too-few-public-methods
    """Class for copying an existing project."""

    FIELDS_PROJECT = (
        "title",
        "description",
        "id",
        "dataConnections.id",
    )

    def __init__(self, kili: "Kili") -> None:
        self.disable_tqdm = False
        self.kili = kili

    def copy_project(  # pylint: disable=too-many-arguments
        self,
        from_project_id: str,
        title: Optional[str],
        description: Optional[str],
        copy_members: bool,
        copy_assets: bool,
        copy_labels: bool,
        disable_tqdm: Optional[bool],
    ) -> str:
        """Copy an existing project."""
        self.disable_tqdm = disable_tqdm

        logging.basicConfig()
        logger = logging.getLogger("kili.services.copy_project")
        logger.setLevel(logging.INFO)

        if copy_labels:
            if not copy_assets:
                raise ValueError(
                    "`copy_assets` must be set to `True` for copying the source project labels."
                )
            if not copy_members:
                raise ValueError(
                    "`copy_members` must be set to `True` for copying the source project labels."
                )

        fields = self.FIELDS_PROJECT

        src_project = self.kili.kili_api_gateway.get_project(ProjectId(from_project_id), fields)

        if src_project["dataConnections"] and copy_assets:
            raise NotImplementedError("Copying projects with cloud storage is not supported.")

        logger.info("Copying new project...")

        new_project_id = self.kili.kili_api_gateway.copy_project(
            ProjectId(from_project_id),
            CopyProjectInput(
                should_copy_members=copy_members,
                should_copy_assets=copy_assets,
            ),
        )

        logger.info(f"Created new project {new_project_id}")

        self.kili.update_properties_in_project(
            project_id=new_project_id,
            title=title or self._generate_project_title(src_project["title"]),
            description=description,
        )

        logger.info("Updated title/description")

        if copy_labels:
            logger.info("Copying labels...")
            self._copy_labels(from_project_id, new_project_id)

        return new_project_id

    def _generate_project_title(self, src_title: str) -> str:
        projects = self.kili.projects(
            fields=["title"], search_query=f"{src_title}%", disable_tqdm=True
        )
        proj_titles = {proj["title"] for proj in projects}
        new_title = f"{src_title} (copy)"
        i = 1
        while new_title in proj_titles:
            new_title = f"{src_title} (copy {i})"
            i += 1
        return new_title

    # pylint: disable=too-many-locals
    def _copy_labels(self, from_project_id: str, new_project_id: str) -> None:
        assets_new_project = self.kili.kili_api_gateway.list_assets(
            AssetFilters(project_id=ProjectId(new_project_id)),
            ["id", "externalId"],
            QueryOptions(disable_tqdm=True),
        )
        assets_new_project_map = {asset["externalId"]: asset["id"] for asset in assets_new_project}

        members_new_project = self.kili.project_users(
            project_id=new_project_id, fields=["user.email", "user.id"], disable_tqdm=True
        )
        members_new_project_map = {
            member["user"]["email"]: member["user"]["id"] for member in members_new_project
        }

        nb_labels_to_copy = self.kili.kili_api_gateway.count_labels(
            LabelFilters(project_id=ProjectId(from_project_id))
        )
        if nb_labels_to_copy == 0:
            return

        labels = self.kili.labels(
            project_id=from_project_id,
            fields=[
                "author.email",
                "jsonResponse",
                "secondsToLabel",
                "isLatestLabelForUser",
                "labelOf.externalId",
                "labelType",
                "modelName",
            ],
            disable_tqdm=True,
        )
        labels = [
            label for label in labels if (label["isLatestLabelForUser"] or label.get("modelName"))
        ]

        # `append_labels` does not take arrays for `model_name` and `label_type` arguments
        # we need to sort and group the labels by `model_name` and `label_type`
        # and upload the grouped labels by batch to `append_labels`
        labels = sorted(
            labels,
            key=lambda label: (
                label["labelType"],
                label["modelName"] is None,
                label["isLatestLabelForUser"],
                label["modelName"],
            ),
        )
        labels_iterator = itertools.groupby(
            labels,
            key=lambda label: (
                label["labelType"],
                label["modelName"] is None,
                label["isLatestLabelForUser"],
                label["modelName"],
            ),
        )

        for key, group in labels_iterator:
            label_type, _, _, model_name = key
            group = list(group)

            # map external id of source project asset to
            # internal id of new project corresponding asset
            # since both source_project and new_project have the same externalIds
            asset_id_array = [
                assets_new_project_map[label["labelOf"]["externalId"]] for label in group
            ]
            json_response_array = [label["jsonResponse"] for label in group]
            author_id_array = [members_new_project_map[label["author"]["email"]] for label in group]
            seconds_to_label_array = [label["secondsToLabel"] for label in group]

            self.kili.append_labels(
                asset_id_array=asset_id_array,
                json_response_array=json_response_array,
                author_id_array=author_id_array,
                seconds_to_label_array=seconds_to_label_array,
                model_name=model_name,
                label_type=label_type,
                disable_tqdm=False,
            )
