"""Base class for all formatters and other utility classes."""

import csv
import json
import logging
import os
import shutil
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Tuple, cast

from kili.core.graphql import QueryOptions
from kili.core.graphql.operations.data_connection.queries import (
    DataConnectionsQuery,
    DataConnectionsWhere,
)
from kili.orm import Asset, Label
from kili.services.export.repository import AbstractContentRepository
from kili.services.export.tools import fetch_assets
from kili.services.export.types import (
    CocoAnnotationModifier,
    ExportType,
    LabelFormat,
    SplitOption,
)
from kili.services.project import get_project
from kili.services.types import Job, ProjectId
from kili.utils.tempfile import TemporaryDirectory

from ..exceptions import NotCompatibleOptions, NotExportableAssetError
from ..tools import is_geotiff_asset_with_lat_lon_coords


class ExportParams(NamedTuple):
    """Contains all parameters that change the result of the export."""

    assets_ids: Optional[List[str]]
    export_type: ExportType
    project_id: ProjectId
    label_format: LabelFormat
    split_option: SplitOption
    single_file: bool
    output_file: Path
    with_assets: bool
    annotation_modifier: Optional[CocoAnnotationModifier]
    asset_filter_kwargs: Optional[Dict[str, object]]
    normalized_coordinates: Optional[bool]


class AbstractExporter(ABC):  # pylint: disable=too-many-instance-attributes
    """Abstract class defining the interface for all exporters."""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        export_params: ExportParams,
        kili,
        logger: logging.Logger,
        disable_tqdm: bool,
        content_repository: AbstractContentRepository,
    ) -> None:
        """Initialize the exporter."""
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
        self.annotation_modifier = export_params.annotation_modifier
        self.asset_filter_kwargs = export_params.asset_filter_kwargs
        self.normalized_coordinates = export_params.normalized_coordinates

        self.project = get_project(
            self.kili, self.project_id, ["jsonInterface", "inputType", "title", "description", "id"]
        )

    @abstractmethod
    def _check_arguments_compatibility(self) -> None:
        """Checks if the export label format is compatible with the export options."""

    @abstractmethod
    def _check_project_compatibility(self) -> None:
        """Checks if the export label format is compatible with the project."""

    @abstractmethod
    def _is_job_compatible(self, job: Job) -> bool:
        """Check if the export label format is compatible with the job."""

    @property
    def compatible_jobs(self) -> Tuple[str]:
        """Get all job names compatible with the export format."""
        return tuple(
            job_name
            for job_name, job in self.project["jsonInterface"]["jobs"].items()
            if self._is_job_compatible(job)
        )

    @abstractmethod
    def process_and_save(self, assets: List[Dict], output_filename: Path) -> None:
        """Converts the asset and save them into an archive file."""

    def make_archive(self, root_folder: Path, output_filename: Path) -> Path:
        """Make the export archive."""
        path_folder = root_folder / self.project_id
        path_archive = shutil.make_archive(str(path_folder), "zip", path_folder)
        output_filename.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(path_archive, output_filename)
        return output_filename

    def create_readme_kili_file(self, root_folder: Path) -> None:
        """Create a README.kili.txt file to give information about exported labels."""
        readme_file_name = root_folder / self.project_id / "README.kili.txt"
        readme_file_name.parent.mkdir(parents=True, exist_ok=True)
        with readme_file_name.open("wb") as fout:
            fout.write(b"Exported Labels from KILI\n=========================\n\n")
            fout.write(f"- Project name: {self.project['title']}\n".encode())
            fout.write(f"- Project identifier: {self.project['id']}\n".encode())
            fout.write(f"- Project description: {self.project.get('description', '')}\n".encode())
            fout.write(f'- Export date: {datetime.now().strftime(r"%Y%m%d-%H%M%S")}\n'.encode())
            fout.write(f"- Exported format: {self.label_format}\n".encode())
            fout.write(f"- Exported labels: {self.export_type}\n".encode())

    @staticmethod
    def write_video_metadata_file(video_metadata: Dict, base_folder: Path) -> None:
        """Write video metadata file."""
        video_metadata_json = json.dumps(video_metadata, sort_keys=True, indent=4)
        if video_metadata_json is not None:
            with (base_folder / "video_meta.json").open("wb") as output_file:
                output_file.write(video_metadata_json.encode("utf-8"))

    @staticmethod
    def write_remote_content_file(remote_content: List[str], images_folder: Path) -> None:
        """Write remote content file."""
        remote_content_header = ["external id", "url", "label file"]
        # newline="" to disable universal newlines translation (bug fix for windows)
        with (images_folder / "remote_assets.csv").open("w", newline="", encoding="utf8") as file:
            writer = csv.writer(file)
            writer.writerow(remote_content_header)
            writer.writerows(remote_content)

    def export_project(
        self,
    ) -> None:
        """Export a project to a json.

        Return the name of the exported archive file.
        """
        self._check_arguments_compatibility()
        self._check_project_compatibility()
        self._check_and_ensure_asset_access()

        self.logger.info("Fetching assets...")

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
                asset_filter_kwargs=self.asset_filter_kwargs,
            )
            # if the asset["externalId"] has slashes in it, the export will not work
            # since the slashes will be interpreted as folders
            if any(asset["externalId"].find(os.sep) != -1 for asset in assets):
                raise NotExportableAssetError(
                    "The export is not supported for assets with externalIds that contain slashes."
                    " Please remove the slashes from the externalIds using"
                    " `kili.change_asset_external_ids()` and try again."
                )

            self._check_geotiff_export_compatibility(assets)

            self.process_and_save(assets, self.output_file)

    def _check_and_ensure_asset_access(self) -> None:
        """Check asset access.

        If there is a data connection, and that the format requires a data access, or that
        with assets is passed, then output an error.

        If not, if the format requires a data access, ensure that the assets are requested.
        """
        if self._has_data_connection() and self.with_assets:
            raise NotCompatibleOptions(
                "Export with download of assets is not allowed on projects with data connections."
                " Please disable the download of assets by setting `with_assets=False`."
            )

    def _has_data_connection(self) -> bool:
        data_connections_gen = DataConnectionsQuery(
            self.kili.graphql_client, self.kili.http_client
        )(
            where=DataConnectionsWhere(project_id=self.project_id),
            fields=["id"],
            options=QueryOptions(disable_tqdm=True, first=1, skip=0),
        )
        return len(list(data_connections_gen)) > 0

    def _check_geotiff_export_compatibility(self, assets: List[Dict]) -> None:
        # pylint: disable=line-too-long
        """Check if one of the assets is a geotiff asset, and if the export params are compatible.

        If one of the assets is a geotiff asset, then:

        - we can only allow the export for Kili or geojson formats, since geotiff normalizedVertices are lat/lon coordinates
        - we cannot allow normalized_coordinates != None, for the same reason
        """
        if (
            self.label_format not in ("raw", "kili", "geojson")
            or self.normalized_coordinates is not None
        ):
            has_geotiff_asset = any(
                is_geotiff_asset_with_lat_lon_coords(asset, self.kili.http_client)
                for asset in assets
            )

            if self.label_format not in ("raw", "kili", "geojson") and has_geotiff_asset:
                raise NotCompatibleOptions(
                    "Cannot export geotiff assets with geospatial coordinates in"
                    f" {self.label_format} format. Please use 'kili', 'raw' or 'geojson' formats"
                    " instead."
                )

            if self.normalized_coordinates is not None and has_geotiff_asset:
                raise NotCompatibleOptions(
                    "Cannot export geotiff assets with geospatial latitude and longitude"
                    f" coordinates with normalized_coordinates={self.normalized_coordinates}."
                    " Please use `normalized_coordinates=None` instead."
                )

    @property
    def base_folder(self) -> Path:
        """Export base folder."""
        return self.export_root_folder / self.project_id

    @property
    def images_folder(self) -> Path:
        """Export images folder."""
        return self.base_folder / "images"

    @staticmethod
    def _filter_out_autosave_labels(assets: List[Asset]) -> List[Asset]:
        """Removes AUTOSAVE labels from exports."""
        clean_assets = []
        for asset in assets:
            labels = asset.get("labels", [])
            clean_labels = list(filter(lambda label: label["labelType"] != "AUTOSAVE", labels))
            if clean_labels:
                asset["labels"] = clean_labels
            clean_assets.append(asset)
        return clean_assets

    @staticmethod
    def _format_json_response(label: Label, label_format: LabelFormat) -> Label:
        """Format the label JSON response in the requested format."""
        formatted_json_response = label.json_response(format_=label_format)
        json_response = {}
        for key, value in cast(Dict, formatted_json_response).items():
            if key.isdigit():
                json_response[int(key)] = value
                continue
            json_response[key] = value
        label["jsonResponse"] = json_response
        return label

    def preprocess_assets(self, assets: List[Asset], label_format: LabelFormat) -> List[Asset]:
        """Format labels in the requested format, and filter out autosave labels."""
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
