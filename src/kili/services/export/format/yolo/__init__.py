"""Common code for the yolo exporter, laid out by kili-formats as the app's export lays it out."""

from pathlib import Path

from kili_formats.layout import (
    asset_label_files,
    exported_jobs,
    yolo_class_file,
    yolo_folders,
    yolo_label_file,
    yolo_label_filename,
    yolo_readme_notes,
)
from kili_formats.media.video import cut_video
from kili_formats.types import Job

from kili.services.export.exceptions import (
    NoCompatibleJobError,
    NotCompatibleInputType,
    NotCompatibleOptions,
)
from kili.services.export.format.base import AbstractExporter, keep_only_images
from kili.utils.tqdm import tqdm


class YoloExporter(AbstractExporter):
    """Common code for Yolo exporters.

    The export writes a dataset per Ultralytics task the project's jobs give: the bounding boxes'
    task with a bounding box job, detect, obb or segment by `bbox_as`; segment with a polygon or
    semantic job. Merged, with two, each goes in its own folder, named after its task, beside the
    shared `images/`; with one, at the export's root. Split, each job's folder is written for its
    own task. YOLO v4 has detect only.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.folders = yolo_folders(
            self.project["jsonInterface"],
            self.label_format,  # pyright: ignore[reportArgumentType]
            split=self.split_option != "merged",
            bounding_boxes=self.bbox_as,
        )

    def _check_arguments_compatibility(self) -> None:
        """Checks if the export label format is compatible with the export options."""
        if self.single_file:
            raise NotCompatibleOptions(
                f"The label format {self.label_format} can not be exported into a single file."
            )

        if self.normalized_coordinates is False:
            raise NotCompatibleOptions(
                "The YOLO annotation format does not support pixel coordinates."
            )

    def _check_project_compatibility(self) -> None:
        """Checks if the export label format is compatible with the project."""
        if self.project["inputType"] not in ("IMAGE", "VIDEO"):
            raise NotCompatibleInputType(
                f"Project with input type '{self.project['inputType']}' not compatible with YOLO"
                " export format."
            )

        if len(self.compatible_jobs) == 0:
            raise NoCompatibleJobError("Project needs at least one compatible job.")

        if not any(folder.categories for folder in self.folders.values()):
            raise NoCompatibleJobError(
                f"Error: There is no job in project {self.project_id} "
                f"that can be converted to the {self.label_format} format."
            )

    def _is_job_compatible(self, job: Job) -> bool:
        """The jobs the format exports, as the app's export takes them."""
        return bool(
            exported_jobs(
                {"jobs": {"job": job}},
                self.label_format,  # pyright: ignore[reportArgumentType]
            )
        )

    def process_and_save(self, assets: list[dict], output_filename: Path) -> None:
        """Write each asset's label files into every folder, as kili-formats lays them out, the
        images shared: the downloaded images no label file describes are left out.
        """
        self.logger.info(f"Exporting to yolo format {self.split_option}...")
        assets = self.preprocess_assets(assets)

        for path, folder in self.folders.items():
            class_file, content = yolo_class_file(
                folder,
                self.label_format,  # pyright: ignore[reportArgumentType]
            )
            (self.base_folder / path).mkdir(parents=True, exist_ok=True)
            (self.base_folder / path / class_file).write_text(content, encoding="utf8", newline="")

        # A remote image is listed once, whichever folders' label files point to it
        remote_rows: dict[tuple[str, str, str], None] = {}
        video_frames: dict[str, dict[str, list[str]]] = {path: {} for path in self.folders}
        images: set[Path] = set()
        for asset in tqdm(assets, disable=self.disable_tqdm):
            asset_remote_rows, frames_by_folder, asset_images = self._write_asset(asset)
            remote_rows.update(dict.fromkeys(asset_remote_rows))
            images |= asset_images
            for path, frame_names in frames_by_folder.items():
                if frame_names:
                    video_frames[path][asset["externalId"]] = frame_names

        for path, frames_by_asset in video_frames.items():
            if frames_by_asset:
                self.write_video_metadata_file(frames_by_asset, self.base_folder / path)
        if self.with_assets:
            keep_only_images(self.images_folder, images)
        if remote_rows:
            self.images_folder.mkdir(parents=True, exist_ok=True)
            self.write_remote_content_file([list(row) for row in remote_rows], self.images_folder)

        self.create_readme_kili_file(self.export_root_folder, yolo_readme_notes(self.folders))
        self.make_archive(self.export_root_folder, output_filename)

        self.logger.warning(output_filename)

    def _write_asset(
        self, asset: dict
    ) -> tuple[list[tuple[str, str, str]], dict[str, list[str]], set[Path]]:
        """Write an asset's label files into every folder.

        Return the rows of the remote images they point to, each folder's video frames, and the
        downloaded images they describe.
        """
        input_type = self.project["inputType"]
        content_frames = (
            [Path(path) for path in asset["jsonContent"]]
            if isinstance(asset.get("jsonContent"), list)
            else []
        )
        # A downloaded native video is cut into frames, named as kili-formats names them
        if (
            input_type == "VIDEO"
            and not content_frames
            and self.with_assets
            and Path(str(asset["content"])).is_file()
        ):
            try:
                content_frames = cut_video(Path(asset["content"]), asset, 0, self.images_folder)
            except ImportError as e:
                raise ImportError(
                    "Install with `pip install kili[video]` to use this feature."
                ) from e

        # Not downloaded, a video's frames are listed by url, as the app lists them: the frame count
        # names them
        frame_urls = (
            self.content_repository.get_frames(asset["jsonContent"])
            if input_type == "VIDEO"
            and not self.with_assets
            and isinstance(asset.get("jsonContent"), str)
            and asset["jsonContent"]
            else []
        )

        remote_rows = []
        images: set[Path] = set()
        frames_by_folder: dict[str, list[str]] = {}
        for path, folder in self.folders.items():
            files = asset_label_files(
                asset,
                input_type,
                [category.job_id for category in folder.categories.values()],
                len(content_frames) or len(frame_urls),
                self.project["jsonInterface"],
            )
            for file in files:
                label_filename = yolo_label_filename(file.stem)
                _write_labels_to_file(
                    self.base_folder / path / "labels",
                    label_filename,
                    yolo_label_file(file.json_response, folder),
                )
                if self.with_assets:
                    if file.frame is None:
                        images.add(Path(asset["content"]))
                    elif file.frame < len(content_frames):
                        images.add(content_frames[file.frame])
                else:
                    url = (
                        frame_urls[file.frame]
                        if file.frame is not None and file.frame < len(frame_urls)
                        else asset["content"]
                    )
                    if not self.content_repository.is_serving(url):
                        remote_rows.append((asset["externalId"], url, label_filename))
            frames_by_folder[path] = sorted(
                {file.image for file in files if file.frame is not None}
            )
        return remote_rows, frames_by_folder, images


def _write_labels_to_file(labels_folder: Path, filename: str, content: str) -> None:
    """Write a label file, its folder created: an external id can hold a slash."""
    file_path = labels_folder / filename
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf8", newline="")
