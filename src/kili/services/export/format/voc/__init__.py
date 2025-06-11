"""Common code for the PASCAL VOC exporter."""

from pathlib import Path
from typing import Dict, List, Sequence

from kili_formats import convert_from_kili_to_voc_format
from kili_formats.media.image import get_frame_dimensions, get_image_dimensions
from kili_formats.media.video import cut_video, get_video_dimensions
from kili_formats.types import Job, JobTool

from kili.domain.ontology import JobMLTask
from kili.services.export.exceptions import (
    NoCompatibleJobError,
    NotCompatibleInputType,
    NotCompatibleOptions,
)
from kili.services.export.format.base import AbstractExporter
from kili.utils.tqdm import tqdm


class VocExporter(AbstractExporter):
    """Common code for VOC exporter."""

    def _check_arguments_compatibility(self) -> None:
        """Check if the export label format is compatible with the export options."""
        if self.single_file:
            raise NotCompatibleOptions(
                "The Pascal VOC annotation format cannot be exported into a single file.",
            )

        if self.split_option != "merged":
            raise NotCompatibleOptions(
                "The current implementation only supports merged annotations."
            )

        if self.normalized_coordinates is True:
            raise NotCompatibleOptions(
                "The Pascal VOC annotation format does not support normalized coordinates."
            )

    def _check_project_compatibility(self) -> None:
        """Check if the export label format is compatible with the project."""
        if self.project["inputType"] not in ("IMAGE", "VIDEO"):
            raise NotCompatibleInputType(
                f"Project with input type '{self.project['inputType']}' not compatible with"
                " Pascal VOC export format."
            )

        if len(self.compatible_jobs) == 0:
            raise NoCompatibleJobError(
                f"Project needs at least one {JobMLTask.OBJECT_DETECTION} task with bounding boxes."
            )

    def _is_job_compatible(self, job: Job) -> bool:
        """Check job compatibility with the Pascal VOC format."""
        if "tools" not in job:
            return False
        return JobTool.RECTANGLE in job["tools"] and job["mlTask"] == JobMLTask.OBJECT_DETECTION

    def process_and_save(self, assets: List[Dict], output_filename: Path) -> None:
        """Save the assets and annotations to a zip file in the Pascal VOC format."""
        self.logger.info("Exporting VOC format")

        labels_folder = self.base_folder / "labels"
        labels_folder.mkdir(parents=True, exist_ok=True)

        for asset in tqdm(assets, disable=self.disable_tqdm):
            _process_asset(asset, labels_folder, self.project["inputType"], self.compatible_jobs)

        self.create_readme_kili_file(self.export_root_folder)
        self.make_archive(self.export_root_folder, output_filename)

        self.logger.warning(output_filename)


# pylint: disable=too-many-locals
def _process_asset(
    asset: Dict, labels_folder: Path, project_input_type: str, valid_jobs: Sequence[str]
) -> None:
    """Process an asset."""
    if project_input_type == "VIDEO":
        nbr_frames = len(asset.get("latestLabel", {}).get("jsonResponse", {}))
        if nbr_frames < 1:
            return
        leading_zeros = len(str(nbr_frames))

        width = height = 0
        frame_ext = ""
        # jsonContent with frames
        if isinstance(asset["jsonContent"], list) and Path(asset["jsonContent"][0]).is_file():
            width, height = get_frame_dimensions(asset)
            frame_ext = Path(asset["jsonContent"][0]).suffix

        # video with shouldUseNativeVideo set to True (no frames available)
        elif Path(asset["content"]).is_file():
            try:
                width, height = get_video_dimensions(asset)
                cut_video(asset["content"], asset, leading_zeros, Path(asset["content"]).parent)
                frame_ext = ".jpg"
            except ImportError as e:
                raise ImportError(
                    "Install with `pip install kili[video]` to use this feature."
                ) from e

        else:
            raise FileNotFoundError(f"Could not find frames or video for asset {asset}")

        for frame_id, json_response in asset["latestLabel"]["jsonResponse"].items():
            frame_name = f'{asset["externalId"]}_{str(int(frame_id)+1).zfill(leading_zeros)}'
            parameters = {"filename": f"{frame_name}{frame_ext}"}
            annotations = convert_from_kili_to_voc_format(
                json_response, width, height, parameters, valid_jobs
            )
            filepath = labels_folder / f"{frame_name}.xml"
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, "wb") as fout:
                fout.write(f"{annotations}\n".encode())

    elif project_input_type == "IMAGE":
        json_response = asset["latestLabel"]["jsonResponse"]
        width, height = get_image_dimensions(asset)
        filename = (
            Path(asset["content"]).name if Path(asset["content"]).is_file() else asset["externalId"]
        )
        parameters = {"filename": filename}
        annotations = convert_from_kili_to_voc_format(
            json_response, width, height, parameters, valid_jobs
        )
        xml_filename = f'{asset["externalId"]}.xml'
        filepath = labels_folder / xml_filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "wb") as fout:
            fout.write(f"{annotations}\n".encode())
