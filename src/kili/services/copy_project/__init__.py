"""
Copy project implementation.
"""
import itertools
import logging
from typing import Dict, Optional

from kili import services
from kili.utils.tempfile import TemporaryDirectory
from kili.utils.tqdm import tqdm


class ProjectCopier:  # pylint: disable=too-few-public-methods
    """
    Class for copying an existing project.
    """

    FIELDS_PROJECT = ["title", "inputType", "description", "id"]
    FIELDS_JSON_INTERFACE = ["jsonInterface"]
    FIELDS_QUALITY_SETTINGS = [
        "consensusTotCoverage",
        "minConsensusSize",
        "useHoneyPot",
        "reviewCoverage",
    ]

    def __init__(self, kili) -> None:
        self.disable_tqdm = False
        self.kili = kili

    def copy_project(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        from_project_id: str,
        title: Optional[str],
        description: Optional[str],
        copy_json_interface: bool,
        copy_quality_settings: bool,
        copy_members: bool,
        copy_assets: bool,
        copy_labels: bool,
        disable_tqdm: bool,
    ) -> str:
        """
        Copy an existing project.
        """
        self.disable_tqdm = disable_tqdm

        logging.basicConfig()
        logger = logging.getLogger("kili.services.copy_project")
        logger.setLevel(logging.INFO)

        if not any(
            (copy_json_interface, copy_quality_settings, copy_members, copy_assets, copy_labels)
        ):
            raise ValueError("At least one element has to be copied.")

        if copy_labels:
            if not copy_json_interface:
                raise ValueError(
                    "`copy_json_interface` must be set to `True` for copying the source project"
                    " labels."
                )
            if not copy_assets:
                raise ValueError(
                    "`copy_assets` must be set to `True` for copying the source project labels."
                )
            if not copy_members:
                raise ValueError(
                    "`copy_members` must be set to `True` for copying the source project labels."
                )

        fields = self.FIELDS_PROJECT
        if copy_json_interface:
            fields = fields + self.FIELDS_JSON_INTERFACE
        if copy_quality_settings:
            fields = fields + self.FIELDS_QUALITY_SETTINGS

        src_project = services.get_project(self.kili, from_project_id, fields)

        new_project_title = title or self._generate_project_title(src_title=src_project["title"])

        new_project_description = description or ""

        json_interface = src_project["jsonInterface"] if copy_json_interface else {"jobs": {}}

        new_project_id = self.kili.create_project(
            input_type=src_project["inputType"],
            json_interface=json_interface,
            title=new_project_title,
            description=new_project_description,
        )["id"]
        logger.info(f"Creating new project with id: '{new_project_id}'")

        if copy_members:
            logger.info("Copying members...")
            self._copy_members(from_project_id, new_project_id)

        if copy_quality_settings:
            logger.info("Copying quality settings...")
            self._copy_quality_settings(new_project_id, src_project)

        if copy_assets:
            logger.info("Copying assets...")
            self._copy_assets(from_project_id, new_project_id)

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

    def _copy_members(self, from_project_id: str, new_project_id: str) -> None:
        members = self.kili.project_users(
            project_id=from_project_id,
            fields=["activated", "role", "user.email", "invitationStatus", "id"],
            disable_tqdm=True,
        )

        members = [
            memb
            for memb in members
            if memb["invitationStatus"] != "DEFAULT_ACCEPTED" and memb["activated"]
        ]

        for member in tqdm(members, disable=self.disable_tqdm):
            self.kili.append_to_roles(
                project_id=new_project_id,
                user_email=member["user"]["email"],
                role=member["role"],
            )

    def _copy_quality_settings(self, new_project_id: str, src_project: Dict) -> None:
        self.kili.update_properties_in_project(
            project_id=new_project_id,
            consensus_tot_coverage=src_project["consensusTotCoverage"],
            min_consensus_size=src_project["minConsensusSize"],
            use_honeypot=src_project["useHoneyPot"],
            review_coverage=src_project["reviewCoverage"],
        )

    # pylint: disable=too-many-locals
    def _copy_assets(self, from_project_id: str, new_project_id: str):
        """
        Copy assets from a project to another.

        Fetches assets by batch since `content` urls expire.
        """
        batch_size = 200

        nb_assets_to_copy = self.kili.count_assets(project_id=from_project_id)

        skip = 0
        with tqdm(total=nb_assets_to_copy, disable=self.disable_tqdm) as pbar:
            while skip < nb_assets_to_copy:
                with TemporaryDirectory() as tmp_dir:
                    assets = self.kili.assets(
                        project_id=from_project_id,
                        fields=[
                            "content",
                            "externalId",
                            "isHoneypot",
                            "jsonContent",
                            "jsonMetadata",
                        ],
                        skip=skip,
                        first=batch_size,
                        download_media=True,
                        local_media_dir=str(tmp_dir.resolve()),
                        disable_tqdm=True,
                    )

                    # cannot pass both content_array and json_content_array
                    # to append_many_to_dataset
                    # we sort and group by (asset["content"], asset["jsonContent"])
                    assets = sorted(
                        assets,
                        key=lambda asset: (asset["content"] != "", asset["jsonContent"] != ""),
                    )
                    assets_iterator = itertools.groupby(
                        assets,
                        key=lambda asset: (asset["content"] != "", asset["jsonContent"] != ""),
                    )

                    for key, group in assets_iterator:
                        has_content, has_jsoncontent = key
                        group = list(group)

                        content_array = (
                            [asset["content"] for asset in group] if has_content else None
                        )
                        external_id_array = [asset["externalId"] for asset in group]
                        is_honeypot_array = [asset["isHoneypot"] for asset in group]
                        json_content_array = (
                            [asset["jsonContent"] for asset in group] if has_jsoncontent else None
                        )
                        json_metadata_array = [asset["jsonMetadata"] for asset in group]

                        self.kili.append_many_to_dataset(
                            project_id=new_project_id,
                            content_array=content_array,
                            external_id_array=external_id_array,
                            is_honeypot_array=is_honeypot_array,
                            json_content_array=json_content_array,
                            json_metadata_array=json_metadata_array,
                            disable_tqdm=True,
                        )

                        skip += len(group)
                        pbar.update(skip)

    # pylint: disable=too-many-locals
    def _copy_labels(self, from_project_id: str, new_project_id: str):
        assets_new_project = self.kili.assets(
            new_project_id, fields=["externalId", "id"], disable_tqdm=True
        )
        assets_new_project_map = {asset["externalId"]: asset["id"] for asset in assets_new_project}

        members_new_project = self.kili.project_users(
            project_id=new_project_id, fields=["user.email", "user.id"], disable_tqdm=True
        )
        members_new_project_map = {
            member["user"]["email"]: member["user"]["id"] for member in members_new_project
        }

        nb_labels_to_copy = self.kili.count_labels(project_id=from_project_id)
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
        labels = [label for label in labels if label["isLatestLabelForUser"]]

        # `append_labels` does not take arrays for `model_name` and `label_type` arguments
        # we need to sort and group the labels by `model_name` and `label_type`
        # and upload the grouped labels by batch to `append_labels`
        labels = sorted(
            labels,
            key=lambda label: (label["labelType"], label["modelName"] is None, label["modelName"]),
        )
        labels_iterator = itertools.groupby(
            labels,
            key=lambda label: (label["labelType"], label["modelName"] is None, label["modelName"]),
        )

        for key, group in labels_iterator:
            label_type, _, model_name = key
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
