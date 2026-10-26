"""Common code for the coco exporter."""

import json
from pathlib import Path
from typing import Optional

from kili_formats import convert_from_kili_to_coco_format
from kili_formats.layout import exported_jobs, one_asset_per_label
from kili_formats.types import Job

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
        # An asset with several labels is exported once per label, as the app exports it
        expanded_assets = [copy for asset in clean_assets for copy in one_asset_per_label(asset)]
        try:
            self._save_assets_export(
                expanded_assets,
                self.export_root_folder,
                annotation_modifier=self.annotation_modifier,
            )
        except ImportError as e:
            raise ImportError("Install with `pip install kili[coco]` to use this feature.") from e
        # A native video's frames are archived, the video itself is not, as the app archives it
        for asset in expanded_assets:
            video = Path(str(asset.get("content", "")))
            if (
                self.project["inputType"] == "VIDEO"
                and not isinstance(asset.get("jsonContent"), list)
                and video.is_file()
            ):
                video.unlink()
        self.create_readme_kili_file(self.export_root_folder)
        self.make_archive(self.export_root_folder, output_filename)

        self.logger.warning(output_filename)

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
        """The shapes' jobs, polygon-only jobs included, as the app's COCO export takes them."""
        return bool(exported_jobs({"jobs": {"job": job}}, "coco"))
