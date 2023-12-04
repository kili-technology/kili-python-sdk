"""Common code for the GeoJson exporter."""

import json
from pathlib import Path
from typing import Dict, List

from kili.domain.ontology import JobMLTask, JobTool
from kili.services.export.exceptions import NotCompatibleInputType, NotCompatibleOptions
from kili.services.export.format.base import AbstractExporter
from kili.services.export.tools import is_geotiff_asset_with_lat_lon_coords
from kili.services.types import Job
from kili.utils.labels.geojson import kili_json_response_to_feature_collection
from kili.utils.tqdm import tqdm


class GeoJsonExporter(AbstractExporter):
    """Common code for GeoJson exporter."""

    def _check_arguments_compatibility(self) -> None:
        """Checks if the export label format is compatible with the export options."""
        if self.normalized_coordinates is not None:
            raise NotCompatibleOptions(
                "The GeoJson annotation format can only be exported with lat/long coordinates."
                " Please set `normalized_coordinates` to None."
            )

        if self.split_option != "merged":
            raise NotCompatibleOptions(
                "The current implementation only supports merged annotations."
            )

        if self.single_file:
            raise NotCompatibleOptions(
                "The GeoJson annotation format cannot be exported into a single file."
            )

    def _check_project_compatibility(self) -> None:
        """Checks if the export label format is compatible with the project."""
        if self.project["inputType"] != "IMAGE":
            raise NotCompatibleInputType(
                f"Project with input type '{self.project['inputType']}' not compatible with"
                " GeoJson export format."
            )

    def _is_job_compatible(self, job: Job) -> bool:
        """Check if the export label format is compatible with the job."""
        if "tools" not in job:
            return False

        if job["mlTask"] != JobMLTask.OBJECT_DETECTION:
            return False

        compatible_tools = {
            JobTool.RECTANGLE,
            JobTool.POLYGON,
            JobTool.SEMANTIC,
            JobTool.MARKER,
            JobTool.POLYLINE,
        }

        return all(
            tool in compatible_tools
            for tool in job["tools"]  # pyright: ignore[reportGeneralTypeIssues]
        )

    def process_and_save(self, assets: List[Dict], output_filename: Path) -> None:
        self.logger.info("Exporting to GeoJson format")

        labels_folder = self.base_folder / "labels"
        labels_folder.mkdir(parents=True, exist_ok=True)

        geotiff_assets = [
            asset
            for asset in assets
            if is_geotiff_asset_with_lat_lon_coords(asset, self.kili.http_client)
        ]
        if len(geotiff_assets) < len(assets):
            self.logger.warning(
                f"Among {len(assets)} assets, only {len(geotiff_assets)} are geotiff assets and"
                " will be exported."
            )

        for asset in tqdm(geotiff_assets, disable=self.disable_tqdm):
            _process_asset(asset, labels_folder)

        self.create_readme_kili_file(self.export_root_folder)
        self.make_archive(self.export_root_folder, output_filename)

        self.logger.warning(output_filename)


def _process_asset(asset: Dict, labels_folder: Path) -> None:
    geojson_feature_collection = kili_json_response_to_feature_collection(
        asset["latestLabel"]["jsonResponse"]
    )
    filepath = labels_folder / f'{asset["externalId"]}.geojson'
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(geojson_feature_collection, file)
