"""Common code for the PASCAL VOC exporter."""

from collections.abc import Sequence
from pathlib import Path
from typing import Optional

from kili_formats import convert_from_kili_to_voc_format
from kili_formats.layout import asset_label_files, exported_jobs
from kili_formats.media.image import get_frame_dimensions, get_image_dimensions
from kili_formats.media.video import cut_video, get_video_dimensions
from kili_formats.types import Job

from kili.domain.ontology import JobMLTask
from kili.services.export.exceptions import (
    NoCompatibleJobError,
    NotCompatibleInputType,
    NotCompatibleOptions,
)
from kili.services.export.format.base import AbstractExporter, keep_only_images
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
        """The bounding box jobs: Pascal VOC holds rectangles only, as the app's export takes them."""
        return bool(exported_jobs({"jobs": {"job": job}}, "pascal_voc"))

    def process_and_save(self, assets: list[dict], output_filename: Path) -> None:
        """Save the assets and annotations to a zip file in the Pascal VOC format."""
        self.logger.info("Exporting VOC format")

        labels_folder = self.base_folder / "labels"
        labels_folder.mkdir(parents=True, exist_ok=True)

        images: set[Path] = set()
        frames_by_asset: dict[str, list[str]] = {}
        for asset in tqdm(self.preprocess_assets(assets), disable=self.disable_tqdm):
            asset_images, frame_names = _process_asset(
                asset,
                labels_folder,
                self.project["inputType"],
                self.compatible_jobs,
                self.project["jsonInterface"],
                self.images_folder,
            )
            images |= asset_images
            if frame_names:
                frames_by_asset[asset["externalId"]] = frame_names

        if frames_by_asset:
            self.write_video_metadata_file(frames_by_asset, self.base_folder)
        if self.with_assets:
            keep_only_images(self.images_folder, images)
        self.create_readme_kili_file(self.export_root_folder)
        self.make_archive(self.export_root_folder, output_filename)

        self.logger.warning(output_filename)


def _process_asset(
    asset: dict,
    labels_folder: Path,
    project_input_type: str,
    valid_jobs: Sequence[str],
    json_interface: Optional[dict] = None,
    images_folder: Optional[Path] = None,
) -> tuple[set[Path], list[str]]:
    """Write an asset's Pascal VOC files, as kili-formats lays them out, each naming the image it
    describes.

    Return the downloaded images they describe, and the names of the video's frames.
    """
    content = Path(str(asset["content"]))
    frames = (
        [Path(path) for path in asset["jsonContent"]]
        if isinstance(asset.get("jsonContent"), list)
        else []
    )
    if project_input_type == "VIDEO":
        if frames and frames[0].is_file():
            width, height = get_frame_dimensions(asset)
        # video with shouldUseNativeVideo set to True (no frames available)
        elif content.is_file():
            try:
                width, height = get_video_dimensions(asset)
                frames = cut_video(content, asset, 0, content.parent)
            except ImportError as e:
                raise ImportError(
                    "Install with `pip install kili[video]` to use this feature."
                ) from e
        else:
            raise FileNotFoundError(f"Could not find frames or video for asset {asset}")
    else:
        width, height = get_image_dimensions(asset)

    images: set[Path] = set()
    files = asset_label_files(asset, project_input_type, valid_jobs, len(frames), json_interface)
    for file in files:
        if file.frame is None:
            image_name = asset["externalId"]
            if content.is_file():
                images.add(content)
                # Its path in the images folder, as the app names it: an external id holding a
                # slash puts it in a subfolder
                image_name = (
                    content.resolve().relative_to(images_folder.resolve()).as_posix()
                    if images_folder and content.resolve().is_relative_to(images_folder.resolve())
                    else content.name
                )
        elif file.frame < len(frames):
            image_name = frames[file.frame].name
            images.add(frames[file.frame])
        else:
            image_name = f"{file.image}.jpg"
        annotations = convert_from_kili_to_voc_format(
            file.json_response, width, height, {"filename": image_name}, valid_jobs
        )
        filepath = labels_folder / f"{file.stem}.xml"
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(f"{annotations}\n", encoding="utf8", newline="")
    return images, sorted({file.image for file in files if file.frame is not None})
