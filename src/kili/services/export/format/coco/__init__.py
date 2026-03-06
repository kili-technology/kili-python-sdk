"""Common code for the coco exporter."""

import json
from pathlib import Path
from typing import Optional

from kili_formats import convert_from_kili_to_coco_format
from kili_formats.types import Job, JobTool

from kili.domain.ontology import JobMLTask
from kili.services.export.exceptions import (
    NoCompatibleJobError,
    NotCompatibleInputType,
    NotCompatibleOptions,
)
from kili.services.export.format.base import AbstractExporter
from kili.services.export.types import CocoAnnotationModifier

DATA_SUBDIR = "data"


class CocoExporter(AbstractExporter):
    """Common code for COCO exporter."""

    def _check_arguments_compatibility(self) -> None:
        """Checks if the export label format is compatible with the export options."""
        if self.normalized_coordinates is True:
            raise NotCompatibleOptions(
                "The COCO annotation format does not support normalized coordinates."
            )

    def _check_project_compatibility(self) -> None:
        """Checks if the export label format is compatible with the project."""
        if self.project["inputType"] not in ("IMAGE", "VIDEO"):
            raise NotCompatibleInputType(
                f"Project with input type '{self.project['inputType']}' not compatible with COCO"
                " export format."
            )

        if len(self.compatible_jobs) == 0:
            raise NoCompatibleJobError(
                f"Project needs at least one {JobMLTask.OBJECT_DETECTION} task with bounding boxes"
                " or segmentations."
            )

    @property
    def images_folder(self) -> Path:
        """Export images folder."""
        return self.base_folder / DATA_SUBDIR

    def process_and_save(self, assets: list[dict], output_filename: Path):
        """Extract formatted annotations from labels."""
        clean_assets = self.preprocess_assets(assets)
        # Expand assets with latestLabels into multiple assets
        expanded_assets = self._expand_assets_with_multiple_labels(clean_assets)
        try:
            self._save_assets_export(
                expanded_assets,
                self.export_root_folder,
                annotation_modifier=self.annotation_modifier,
            )
        except ImportError as e:
            raise ImportError("Install with `pip install kili[coco]` to use this feature.") from e
        self.create_readme_kili_file(self.export_root_folder)
        self.make_archive(self.export_root_folder, output_filename)

        self.logger.warning(output_filename)

    def _expand_assets_with_multiple_labels(self, assets: list[dict]) -> list[dict]:
        """Expand assets with latestLabels into multiple asset entries with latestLabel.

        When an asset has multiple labels (latestLabels), create separate asset entries
        for each label with a unique externalId suffix (_label0, _label1, etc.).
        """
        expanded_assets = []
        for asset in assets:
            # Collect all labels to process (handle both latestLabel and latestLabels)
            labels_to_process = []
            if "latestLabel" in asset and asset["latestLabel"]:
                labels_to_process.append(asset["latestLabel"])
            if "latestLabels" in asset and asset["latestLabels"]:
                for label in asset["latestLabels"]:
                    if label is not None:
                        labels_to_process.append(label)

            if not labels_to_process:
                continue

            # Create asset copy for each label
            for label_idx, latest_label in enumerate(labels_to_process, start=1):
                asset_copy = asset.copy()
                # Add label suffix if we have multiple labels
                if len(labels_to_process) > 1:
                    label_suffix = f"_label{label_idx}"
                    asset_copy["externalId"] = f"{asset['externalId']}{label_suffix}"

                # Set latestLabel and remove latestLabels
                asset_copy["latestLabel"] = latest_label
                if "latestLabels" in asset_copy:
                    del asset_copy["latestLabels"]

                expanded_assets.append(asset_copy)

        return expanded_assets

    def _save_assets_export(
        self,
        assets: list[dict],
        output_directory: Path,
        annotation_modifier: Optional[CocoAnnotationModifier],
    ):
        """Save the assets to a file and return the link to that file."""
        if self.split_option == "split":
            for job_name, job in self.project["jsonInterface"]["jobs"].items():
                if self._is_job_compatible(job):
                    labels_json = convert_from_kili_to_coco_format(
                        jobs={job_name: job},
                        assets=assets,
                        title=self.project["title"],
                        project_input_type=self.project["inputType"],
                        annotation_modifier=annotation_modifier,
                        merged=False,
                    )
                    label_file_name = (
                        Path(output_directory) / self.project["id"] / job_name / "labels.json"
                    )
                    label_file_name.parent.mkdir(parents=True, exist_ok=True)
                    with label_file_name.open("w") as outfile:
                        json.dump(labels_json, outfile)
                else:
                    self.logger.warning(f"Job {job_name} is not compatible with the COCO format.")
        else:  # merged
            labels_json = convert_from_kili_to_coco_format(
                jobs={
                    k: job
                    for k, job in self.project["jsonInterface"]["jobs"].items()
                    if self._is_job_compatible(job)
                },
                assets=assets,
                title=self.project["title"],
                project_input_type=self.project["inputType"],
                annotation_modifier=annotation_modifier,
                merged=True,
            )
            label_file_name = Path(output_directory) / self.project["id"] / "labels.json"
            label_file_name.parent.mkdir(parents=True, exist_ok=True)
            with label_file_name.open("w") as outfile:
                json.dump(labels_json, outfile)

    def _is_job_compatible(self, job: Job) -> bool:
        if "tools" not in job:
            return False
        return (JobTool.SEMANTIC in job["tools"] or JobTool.RECTANGLE in job["tools"]) and job[
            "mlTask"
        ] == JobMLTask.OBJECT_DETECTION
