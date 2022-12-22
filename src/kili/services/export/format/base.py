"""
Base class for all formatters and other utility classes.
"""

import csv
import json
import logging
import shutil
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, cast

from kili.orm import Asset, JobMLTask, JobTool, Label
from kili.services.export.repository import AbstractContentRepository
from kili.services.export.tools import fetch_assets
from kili.services.export.types import ExportType, LabelFormat, SplitOption
from kili.services.types import ProjectId
from kili.utils.tempfile import TemporaryDirectory


class ExportParams(NamedTuple):
    """
    Contains all parameters that change the result of the export
    """

    assets_ids: Optional[List[str]]
    export_type: ExportType
    project_id: ProjectId
    label_format: LabelFormat
    split_option: SplitOption
    single_file: bool
    output_file: Path
    with_assets: bool


class AbstractExporter(ABC):  # pylint: disable=too-many-instance-attributes
    """
    Abstract class defining the interface for all exporters.
    """

    def __init__(
        self,
        export_params: ExportParams,
        kili,
        logger: logging.Logger,
        disable_tqdm: bool,
        content_repository: AbstractContentRepository,
    ):  # pylint: disable=too-many-arguments
        self.project_id: ProjectId = export_params.project_id
        self.assets_ids: Optional[List[str]] = export_params.assets_ids
        self.export_type: ExportType = export_params.export_type
        self.label_format: LabelFormat = export_params.label_format
        self.single_file: bool = export_params.single_file
        self.split_option: SplitOption = export_params.split_option
        self.disable_tqdm: bool = disable_tqdm
        self.kili = kili
        self.logger: logging.Logger = logger
        self.content_repository: AbstractContentRepository = content_repository
        self.output_file = export_params.output_file
        self.with_assets: bool = export_params.with_assets
        self.export_root_folder: Path = Path()

    @abstractmethod
    def _check_arguments_compatibility(self) -> None:
        """
        Checks if the format is compatible with the export options.
        """

    @abstractmethod
    def process_and_save(self, assets: List[Dict], output_filename: Path) -> None:
        """
        Converts the asset and save them into an archive file.
        """

    def make_archive(self, root_folder: Path, output_filename: Path) -> Path:
        """
        Make the export archive
        """
        path_folder = root_folder / self.project_id
        path_archive = shutil.make_archive(str(path_folder), "zip", path_folder)
        shutil.copy(path_archive, output_filename)
        return output_filename

    def get_project_and_init(self):
        """
        Get and validate the project
        """
        json_interface = list(
            self.kili.projects(
                project_id=self.project_id, fields=["jsonInterface"], disable_tqdm=True
            )
        )[0]["jsonInterface"]

        ml_task = JobMLTask.ObjectDetection
        tool = JobTool.Rectangle

        return json_interface, ml_task, tool

    def create_readme_kili_file(self, root_folder: Path) -> None:
        """
        Create a README.kili.txt file to give information about exported labels
        """
        readme_file_name = root_folder / self.project_id / "README.kili.txt"
        project_info = list(
            self.kili.projects(
                project_id=self.project_id, fields=["title", "id", "description"], disable_tqdm=True
            )
        )[0]
        readme_file_name.parent.mkdir(parents=True, exist_ok=True)
        with readme_file_name.open("wb") as fout:
            fout.write("Exported Labels from KILI\n=========================\n\n".encode())
            fout.write(f"- Project name: {project_info['title']}\n".encode())
            fout.write(f"- Project identifier: {self.project_id}\n".encode())
            fout.write(f"- Project description: {project_info['description']}\n".encode())
            fout.write(f'- Export date: {datetime.now().strftime("%Y%m%d-%H%M%S")}\n'.encode())
            fout.write(f"- Exported format: {self.label_format}\n".encode())
            fout.write(f"- Exported labels: {self.export_type}\n".encode())

    @staticmethod
    def write_video_metadata_file(video_metadata: Dict, base_folder: Path) -> None:
        """
        Write video metadata file
        """
        video_metadata_json = json.dumps(video_metadata, sort_keys=True, indent=4)
        if video_metadata_json is not None:
            with (base_folder / "video_meta.json").open("wb") as output_file:
                output_file.write(video_metadata_json.encode("utf-8"))

    @staticmethod
    def write_remote_content_file(remote_content: List[str], images_folder: Path) -> None:
        """
        Write remote content file
        """
        remote_content_header = ["external id", "url", "label file"]
        with (images_folder / "remote_assets.csv").open("w", encoding="utf8") as file:
            writer = csv.writer(file)
            writer.writerow(remote_content_header)
            writer.writerows(remote_content)

    def export_project(
        self,
    ) -> None:
        """
        Export a project to a json.
        Return the name of the exported archive file in the bucket.
        """
        self._check_arguments_compatibility()

        self.logger.warning("Fetching assets...")

        with TemporaryDirectory() as export_root_folder:
            self.export_root_folder = export_root_folder
            assets = fetch_assets(
                self.kili,
                project_id=self.project_id,
                asset_ids=self.assets_ids,
                export_type=self.export_type,
                label_type_in=["DEFAULT", "REVIEW"],
                disable_tqdm=self.disable_tqdm,
                download_media=self.with_assets,
                local_media_dir=str(self.images_folder),
            )
            self.process_and_save(assets, self.output_file)

    @property
    def base_folder(self) -> Path:
        """
        Export base folder
        """
        return self.export_root_folder / self.project_id

    @property
    def images_folder(self) -> Path:
        """
        Export images folder
        """
        return self.base_folder / "images"

    @staticmethod
    def _filter_out_autosave_labels(assets: List[Asset]) -> List[Asset]:
        """
        Removes AUTOSAVE labels from exports
        """
        clean_assets = []
        for asset in assets:
            labels = asset.get("labels", [])
            clean_labels = list(filter(lambda label: label["labelType"] != "AUTOSAVE", labels))
            if clean_labels:
                asset["labels"] = clean_labels
            clean_assets.append(asset)
        return clean_assets

    @staticmethod
    def _format_json_response(label: Label, label_format: LabelFormat):
        """
        Format the label JSON response in the requested format
        """
        formatted_json_response = label.json_response(_format=label_format)
        json_response = {}
        for key, value in cast(Dict, formatted_json_response).items():
            if key.isdigit():
                json_response[int(key)] = value
                continue
            json_response[key] = value
        label["jsonResponse"] = json_response
        return label

    @staticmethod
    def process_assets(assets: List[Asset], label_format: LabelFormat) -> List[Asset]:
        """
        Format labels in the requested format, and filter out autosave labels
        """
        assets_in_format = []
        for asset in assets:
            if "labels" in asset:
                labels_of_asset = []
                for label in asset["labels"]:
                    clean_label = AbstractExporter._format_json_response(label, label_format)
                    labels_of_asset.append(clean_label)
                asset["labels"] = labels_of_asset
            if "latestLabel" in asset:
                label = asset["latestLabel"]
                if label is not None:
                    clean_label = AbstractExporter._format_json_response(label, label_format)
                    asset["latestLabel"] = clean_label
            assets_in_format.append(asset)

        clean_assets = AbstractExporter._filter_out_autosave_labels(assets_in_format)
        return clean_assets
