"""Common code for the GeoJson exporter."""

import json
from datetime import datetime, timezone
from pathlib import Path

from kili_formats.format.geojson import convert_from_kili_to_geojson_format
from kili_formats.types import Job, JobTool

from kili.domain.ontology import JobMLTask
from kili.services.export.exceptions import NotCompatibleInputType, NotCompatibleOptions
from kili.services.export.format.base import AbstractExporter
from kili.services.export.format.pixel_labeling import is_pixel_labeling_project
from kili.services.export.tools import is_geotiff_asset_with_lat_lon_coords
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
        if self.project["inputType"] not in ["IMAGE", "GEOSPATIAL"]:
            raise NotCompatibleInputType(
                f"Project with input type '{self.project['inputType']}' not compatible with"
                " GeoJson export format."
            )

        if is_pixel_labeling_project(self.project):
            raise NotCompatibleInputType(
                "GeoJson export is not available for projects labeled in image pixel"
                " coordinates. Use the Kili format, which exports pixel coordinates."
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

    def process_and_save(self, assets: list[dict], output_filename: Path) -> None:
        self.logger.info("Exporting to GeoJson format")

        labels_folder = self.base_folder / "labels"
        labels_folder.mkdir(parents=True, exist_ok=True)
        project_type = self.project.get("inputType")
        geotiff_assets = [
            asset
            for asset in assets
            if project_type == "GEOSPATIAL"
            or is_geotiff_asset_with_lat_lon_coords(asset, self.kili.http_client)
        ]
        if len(geotiff_assets) < len(assets):
            self.logger.warning(
                f"Among {len(assets)} assets, only {len(geotiff_assets)} are geotiff assets and"
                " will be exported."
            )

        # Get json_interface for GIS-friendly property names
        json_interface = self.project.get("jsonInterface")

        export_date = (
            datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        )

        for asset in tqdm(geotiff_assets, disable=self.disable_tqdm):
            _process_asset(
                asset,
                labels_folder,
                json_interface,
                flatten_properties=True,
                export_date=export_date,
            )

        self.create_readme_kili_file(self.export_root_folder)
        self.make_archive(self.export_root_folder, output_filename)

        self.logger.warning(output_filename)


def _process_asset(
    asset: dict,
    labels_folder: Path,
    json_interface: dict | None = None,
    flatten_properties: bool = False,
    export_date: str | None = None,
) -> None:
    # Collect all labels to process (handle both latestLabel and latestLabels)
    labels_to_process = []
    if "latestLabel" in asset and asset["latestLabel"]:
        labels_to_process.append(asset["latestLabel"])
    if "latestLabels" in asset and asset["latestLabels"]:
        for label in asset["latestLabels"]:
            if label is not None:
                labels_to_process.append(label)

    if not labels_to_process:
        return

    # Process each label
    for label_idx, latest_label in enumerate(labels_to_process, start=1):
        # Add label suffix if we have multiple labels
        label_suffix = f"_label{label_idx}" if len(labels_to_process) > 1 else ""

        geojson_feature_collection = convert_from_kili_to_geojson_format(
            latest_label["jsonResponse"],
            json_interface,
            flatten_properties,
        )
        label_author = (latest_label.get("author") or {}).get("email")
        _attach_export_metadata(geojson_feature_collection, asset, label_author, export_date)
        filepath = labels_folder / f"{asset['externalId']}{label_suffix}.geojson"
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(geojson_feature_collection, file)


def _attach_export_metadata(
    geojson_feature_collection: dict,
    asset: dict,
    author: str | None,
    export_date: str | None,
) -> None:
    """Attach asset/export-level metadata once at the root of the FeatureCollection.

    The metadata describes the asset and the export (not individual annotations), so it is
    stored once under `properties.kili` of the FeatureCollection rather than duplicated on
    every feature. `author` is the email of the labeler who created the exported label (each
    FeatureCollection corresponds to a single label), not the user who requested the export.
    """
    kili_properties = {
        "assetId": asset.get("id"),
        "author": author,
        "exportDate": export_date,
    }
    geospatial_export_metadata = asset.get("geospatialExportMetadata")
    if geospatial_export_metadata:
        kili_properties["geospatialExportMetadata"] = geospatial_export_metadata
    geojson_feature_collection.setdefault("properties", {})["kili"] = kili_properties
