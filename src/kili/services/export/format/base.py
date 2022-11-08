"""
Base class for all formatters and other utility classes.
"""

import logging
import os
import shutil
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Type

from kili.orm import AnnotationFormat, Asset, JobMLTask, JobTool
from kili.services.export.exceptions import NotCompatibleOptions
from kili.services.export.repository import SDKContentRepository
from kili.services.export.tools import fetch_assets
from kili.services.export.types import ExportType, LabelFormat, SplitOption
from kili.services.types import LogLevel


class ExportParams(NamedTuple):
    """
    Contains all parameters that change the result of the export
    """

    assets_ids: Optional[List[str]]
    export_type: ExportType
    project_id: str
    label_format: LabelFormat
    split_option: SplitOption
    single_file: bool
    output_file: str


class LoggerParams(NamedTuple):
    """
    Contains all parameters related to logging.
    """

    disable_tqdm: bool
    level: LogLevel


class ContentRepositoryParams(NamedTuple):
    """
    Contains all the parameters related to the content repository.
    """

    router_endpoint: str
    router_headers: Dict[str, str]


class BaseExporter(ABC):  # pylint: disable=too-many-instance-attributes

    """
    Abstract class defining the interface for all exporters.
    """

    download_media = False  # Whether or not we need to download the media for the given format.

    def __init__(
        self,
        project_id,
        export_type,
        label_format,
        single_file,
        disable_tqdm,
        kili,
        logger,
        content_repository,
    ):  # pylint: disable=too-many-arguments
        self.project_id = project_id
        self.export_type = export_type
        self.label_format = label_format
        self.single_file = single_file
        self.disable_tqdm = disable_tqdm
        self.kili = kili
        self.logger = logger
        self.content_repository = content_repository

    def _check_arguments_compatibility(self):
        if self.single_file and self.label_format not in ["raw", "kili"]:
            raise NotCompatibleOptions(
                f"The label format {self.label_format} can not be exported in a single file."
            )

    @abstractmethod
    def process_and_save(self, assets: List[Dict], output_filename: str) -> None:
        """
        Converts the asset and save them into an archive file.
        """

    def make_archive(self, root_folder: str, output_filename: str) -> str:
        """
        Make the export archive
        """
        path_folder = os.path.join(root_folder, self.project_id)
        path_archive = shutil.make_archive(path_folder, "zip", path_folder)
        shutil.copy(path_archive, output_filename)
        return output_filename

    def get_project_and_init(self):
        """
        Get and validate the project
        """
        json_interface = self.kili.projects(
            project_id=self.project_id, fields=["jsonInterface"], disable_tqdm=True
        )[0]["jsonInterface"]

        ml_task = JobMLTask.ObjectDetection
        tool = JobTool.Rectangle

        return json_interface, ml_task, tool

    def create_readme_kili_file(self, root_folder: Path) -> None:
        """
        Create a README.kili.txt file to give information about exported labels
        """
        readme_file_name = root_folder / self.project_id / "README.kili.txt"
        project_info = self.kili.projects(
            project_id=self.project_id, fields=["title", "id", "description"], disable_tqdm=True
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

    def export_project(
        self,
        kili,
        export_params: ExportParams,
        logger_params: LoggerParams,
    ) -> None:
        """
        Export a project to a json.
        Return the name of the exported archive file in the bucket.
        """
        self._check_arguments_compatibility()
        assets = fetch_assets(
            kili,
            project_id=export_params.project_id,
            asset_ids=export_params.assets_ids,
            export_type=export_params.export_type,
            label_type_in=["DEFAULT", "REVIEW"],
            disable_tqdm=logger_params.disable_tqdm,
            download_media=self.download_media,
        )
        self.process_and_save(assets, export_params.output_file)

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
    def _format_json_response(label, label_format):
        """
        Format the label JSON response in the requested format
        """
        formatted_json_response = label.json_response(_format=label_format.lower())
        if label_format.lower() == AnnotationFormat.Simple:
            label["jsonResponse"] = formatted_json_response
        else:
            json_response = {}
            for key, value in formatted_json_response.items():
                if key.isdigit():
                    json_response[int(key)] = value
                    continue
                json_response[key] = value
            label["jsonResponse"] = json_response
        return label

    @staticmethod
    def process_assets(assets: List[Asset], label_format: str) -> List[Asset]:
        """
        Format labels in the requested format, and filter out autosave labels
        """
        assets_in_format = []
        for asset in assets:
            if "labels" in asset:
                labels_of_asset = []
                for label in asset["labels"]:
                    clean_label = BaseExporter._format_json_response(label, label_format)
                    labels_of_asset.append(clean_label)
                asset["labels"] = labels_of_asset
            if "latestLabel" in asset:
                label = asset["latestLabel"]
                if label is not None:
                    clean_label = BaseExporter._format_json_response(label, label_format)
                    asset["latestLabel"] = clean_label
            assets_in_format.append(asset)

        clean_assets = BaseExporter._filter_out_autosave_labels(assets_in_format)
        return clean_assets


class BaseExporterSelector(ABC):
    # pylint: disable=too-few-public-methods

    """
    Abstract class defining a standard signature for all formatters
    """

    @staticmethod
    def get_logger_assets_and_content_repo(
        kili,
        export_params: ExportParams,
        logger_params: LoggerParams,
        content_repository_params: ContentRepositoryParams,
    ):
        """
        Fetches assets and gets right logger and content repository depending on parameters
        """
        logger = BaseExporterSelector.get_logger(logger_params.level)

        logger.info("Fetching assets ...")
        assets = fetch_assets(
            kili,
            project_id=export_params.project_id,
            asset_ids=export_params.assets_ids,
            export_type=export_params.export_type,
            label_type_in=["DEFAULT", "REVIEW"],
            disable_tqdm=logger_params.disable_tqdm,
        )
        content_repository = SDKContentRepository(
            content_repository_params.router_endpoint,
            content_repository_params.router_headers,
            verify_ssl=True,
        )
        return logger, assets, content_repository

    @staticmethod
    @abstractmethod
    def select_exporter_class(
        split_param: SplitOption,
    ) -> Type[BaseExporter]:
        """
        Return the right exporter class.
        """

    @classmethod
    def init_exporter(
        cls,
        kili,
        logger_params,
        export_params: ExportParams,
        content_repository_params: ContentRepositoryParams,
    ) -> BaseExporter:
        """
        Return the right exporter.
        """
        logger = BaseExporterSelector.get_logger(logger_params.level)

        logger.info("Fetching assets ...")
        content_repository = SDKContentRepository(
            content_repository_params.router_endpoint,
            content_repository_params.router_headers,
            verify_ssl=True,
        )
        exporter_class = cls.select_exporter_class(export_params.split_option)
        return exporter_class(
            export_params.project_id,
            export_params.export_type,
            export_params.label_format,
            export_params.single_file,
            logger_params.disable_tqdm,
            kili,
            logger,
            content_repository,
        )

    @staticmethod
    def get_logger(level: LogLevel):
        """Gets the export logger"""
        logger = logging.getLogger("kili.services.export")
        logger.setLevel(level)
        if logger.hasHandlers():
            logger.handlers.clear()
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        return logger
