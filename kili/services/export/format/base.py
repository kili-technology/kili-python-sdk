"""
Base class for all formatters and other utility classes.
"""

import os
import shutil
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, NamedTuple, Optional

from kili.orm import JobMLTask, JobTool
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


class BaseExporterSelector(ABC):
    # pylint: disable=too-few-public-methods

    """
    Abstract class defining a standard signature for all formatters
    """

    @staticmethod
    @abstractmethod
    def export_project(
        kili,
        export_params: ExportParams,
        logger_params: LoggerParams,
        content_repository_params: ContentRepositoryParams,
    ) -> str:
        """
        Export a project to a json.
        Return the name of the exported archive file in the bucket.
        """


class BaseExporter(ABC):
    """
    Abstract class defining the interface for all exporters.
    """

    def __init__(
        self, project_id, export_type, label_format, disable_tqdm, kili, logger, content_repository
    ):  # pylint: disable=too-many-arguments
        self.project_id = project_id
        self.export_type = export_type
        self.label_format = label_format
        self.disable_tqdm = disable_tqdm
        self.kili = kili
        self.logger = logger
        self.content_repository = content_repository

    @abstractmethod
    def process_and_save(self, assets: List[Dict], output_filename: str) -> None:
        """
        Converts the asset and save them into an archive.
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

    def create_readme_kili_file(self, root_folder: str) -> None:
        """
        Create a README.kili.txt file to give information about exported labels
        """
        readme_file_name = os.path.join(root_folder, self.project_id, "README.kili.txt")
        project_info = self.kili.projects(
            project_id=self.project_id, fields=["title", "id", "description"], disable_tqdm=True
        )[0]
        with open(readme_file_name, "wb") as fout:
            fout.write("Exported Labels from KILI\n=========================\n\n".encode())
            fout.write(f"- Project name: {project_info['title']}\n".encode())
            fout.write(f"- Project identifier: {self.project_id}\n".encode())
            fout.write(f"- Project description: {project_info['description']}\n".encode())
            fout.write(f'- Export date: {datetime.now().strftime("%Y%m%d-%H%M%S")}\n'.encode())
            fout.write(f"- Exported format: {self.label_format}\n".encode())
            fout.write(f"- Exported labels: {self.export_type}\n".encode())
