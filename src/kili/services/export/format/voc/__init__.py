"""Common code for the PASCAL VOC exporter."""

from collections.abc import Sequence
from pathlib import Path

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

    def process_and_save(self, assets: list[dict], output_filename: Path) -> None:
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
def _process_video_asset(
    asset: dict,
    latest_label: dict,
    labels_folder: Path,
    label_suffix: str,
    valid_jobs: Sequence[str],
) -> None:
    """Process a video asset and save annotations."""
    nbr_frames = len(latest_label.get("jsonResponse", {}))
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
            raise ImportError("Install with `pip install kili[video]` to use this feature.") from e

    else:
        raise FileNotFoundError(f"Could not find frames or video for asset {asset}")

    for frame_id, json_response in latest_label["jsonResponse"].items():
        frame_name = (
            f'{asset["externalId"]}_{str(int(frame_id)+1).zfill(leading_zeros)}{label_suffix}'
        )
        parameters = {"filename": f"{frame_name}{frame_ext}"}
        annotations = convert_from_kili_to_voc_format(
            json_response, width, height, parameters, valid_jobs
        )
        filepath = labels_folder / f"{frame_name}.xml"
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "wb") as fout:
            fout.write(f"{annotations}\n".encode())


def _process_image_asset(
    asset: dict,
    latest_label: dict,
    labels_folder: Path,
    label_suffix: str,
    valid_jobs: Sequence[str],
) -> None:
    """Process an image asset and save annotations."""
    json_response = latest_label["jsonResponse"]
    width, height = get_image_dimensions(asset)
    filename = (
        Path(asset["content"]).name if Path(asset["content"]).is_file() else asset["externalId"]
    )
    parameters = {"filename": filename}
    annotations = convert_from_kili_to_voc_format(
        json_response, width, height, parameters, valid_jobs
    )
    xml_filename = f'{asset["externalId"]}{label_suffix}.xml'
    filepath = labels_folder / xml_filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "wb") as fout:
        fout.write(f"{annotations}\n".encode())


def _process_asset(
    asset: dict, labels_folder: Path, project_input_type: str, valid_jobs: Sequence[str]
) -> None:
    """Process an asset."""
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

        if project_input_type == "VIDEO":
            _process_video_asset(asset, latest_label, labels_folder, label_suffix, valid_jobs)
        elif project_input_type == "IMAGE":
            _process_image_asset(asset, latest_label, labels_folder, label_suffix, valid_jobs)
