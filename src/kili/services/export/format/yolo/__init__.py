"""Common code for the yolo exporter."""

import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple

from kili.domain.ontology import JobMLTask, JobTool
from kili.services.export.exceptions import (
    NoCompatibleJobError,
    NotCompatibleInputType,
    NotCompatibleOptions,
)
from kili.services.export.format.base import AbstractExporter
from kili.services.export.media.video import cut_video
from kili.services.export.repository import AbstractContentRepository, DownloadError
from kili.services.export.types import JobCategory, LabelFormat, SplitOption
from kili.services.types import Job
from kili.utils.tqdm import tqdm


class YoloExporter(AbstractExporter):
    """Common code for Yolo exporters."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if self.split_option == "merged":
            self.merged_categories_id = self._get_merged_categories(self.project["jsonInterface"])
        else:
            self.categories_by_job = self._get_categories_by_job(self.project["jsonInterface"])

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

        if self.split_option == "merged":
            if not self.merged_categories_id:
                raise NoCompatibleJobError(
                    f"Error: There is no job in project {self.project_id} "
                    f"that can be converted to the {self.label_format} format."
                )
        else:
            if not self.categories_by_job:
                raise NoCompatibleJobError(
                    f"Error: There is no job in project {self.project_id} "
                    f"that can be converted to the {self.label_format} format."
                )

    def _is_job_compatible(self, job: Job) -> bool:
        """Check job compatibility with the YOLO format."""
        if "tools" not in job:
            return False

        compatible_tools = {JobTool.RECTANGLE, JobTool.POLYGON, JobTool.SEMANTIC}

        return job["mlTask"] == JobMLTask.OBJECT_DETECTION and all(
            tool in compatible_tools
            for tool in job["tools"]  # pyright: ignore[reportGeneralTypeIssues]
        )

    def process_and_save(self, assets: List[Dict], output_filename: Path) -> None:
        """Yolo specific process and save."""
        if self.split_option == "merged":
            return self._process_and_save_merge(assets, output_filename)
        return self._process_and_save_split(assets, output_filename)

    def _process_and_save_split(self, assets: List[Dict], output_filename: Path) -> None:
        self.logger.info("Exporting to yolo format split...")

        self._write_jobs_labels_into_split_folders(
            assets,
            self.categories_by_job,
            self.export_root_folder,
            self.images_folder,
        )
        self.create_readme_kili_file(self.export_root_folder)
        self.make_archive(self.export_root_folder, output_filename)

        self.logger.warning(output_filename)

    def _process_and_save_merge(self, assets: List[Dict], output_filename: Path) -> None:
        self.logger.info("Exporting to yolo format merged...")

        labels_folder = self.base_folder / "labels"
        labels_folder.mkdir(parents=True, exist_ok=True)
        self._write_labels_into_single_folder(
            assets,
            self.merged_categories_id,
            labels_folder,
            self.images_folder,
            self.base_folder,
        )
        self.create_readme_kili_file(self.export_root_folder)
        self.make_archive(self.export_root_folder, output_filename)

        self.logger.warning(output_filename)

    def _write_labels_into_single_folder(
        self,
        assets: List[Dict],
        categories_id: Dict[str, JobCategory],
        labels_folder: Path,
        images_folder: Path,
        base_folder: Path,
    ):  # pylint: disable=too-many-arguments
        """Write all the labels into a single folder."""
        _write_class_file(base_folder, categories_id, self.label_format, self.split_option)

        remote_content = []
        video_metadata = {}

        for asset in tqdm(assets, disable=self.disable_tqdm):
            asset_remote_content, video_filenames = _process_asset(
                asset,
                images_folder,
                labels_folder,
                categories_id,
                self.content_repository,
                self.with_assets,
                self.project["inputType"],
            )
            if video_filenames:
                video_metadata[asset["externalId"]] = video_filenames
            remote_content.extend(asset_remote_content)

        if video_metadata:
            self.write_video_metadata_file(video_metadata, base_folder)

        if len(remote_content) > 0:
            self.images_folder.mkdir(parents=True, exist_ok=True)
            self.write_remote_content_file(remote_content, images_folder)

    def _write_jobs_labels_into_split_folders(
        self,
        assets: List[Dict],
        categories_by_job: Dict[str, Dict[str, JobCategory]],
        root_folder: Path,
        images_folder: Path,
    ) -> None:
        """Write assets into split folders."""
        for job_id, category_ids in categories_by_job.items():
            base_folder = root_folder / self.project_id / job_id
            labels_folder = base_folder / "labels"
            labels_folder.mkdir(parents=True, exist_ok=True)

            self._write_labels_into_single_folder(
                assets,
                category_ids,
                labels_folder,
                images_folder,
                base_folder,
            )

    def _get_merged_categories(self, json_interface: Dict) -> Dict[str, JobCategory]:
        """Return a dictionary of JobCategory instances by category full name."""
        cat_number = 0
        merged_categories_id: Dict[str, JobCategory] = {}
        for job_id, job in json_interface.get("jobs", {}).items():
            if not self._is_job_compatible(job):
                continue

            for category in job.get("content", {}).get("categories", {}):
                merged_categories_id[get_category_full_name(job_id, category)] = JobCategory(
                    category_name=category, id=cat_number, job_id=job_id
                )
                cat_number += 1

        return merged_categories_id

    def _get_categories_by_job(self, json_interface: Dict) -> Dict[str, Dict[str, JobCategory]]:
        """Return a dictionary of JobCategory instances by category full name and job id."""
        categories_by_job: Dict[str, Dict[str, JobCategory]] = {}
        for job_id, job in json_interface.get("jobs", {}).items():
            if not self._is_job_compatible(job):
                continue

            categories: Dict[str, JobCategory] = {}
            for cat_id, category in enumerate(job.get("content", {}).get("categories", {})):
                categories[get_category_full_name(job_id, category)] = JobCategory(
                    category_name=category, id=cat_id, job_id=job_id
                )
            categories_by_job[job_id] = categories
        return categories_by_job


class _LabelFrames:
    """Holds asset frames data."""

    @staticmethod
    def from_asset(asset, job_ids) -> "_LabelFrames":
        """Instantiate the label frames from the asset.

        It handles the case when there are several
        frames by label or a single one.
        """
        frames = {}
        number_of_frames = 0
        is_frame_group = False
        if "jsonResponse" in asset["latestLabel"]:
            number_of_frames = len(asset["latestLabel"]["jsonResponse"])
            for idx in range(number_of_frames):
                if str(idx) in asset["latestLabel"]["jsonResponse"]:
                    is_frame_group = True
                    frame_asset = asset["latestLabel"]["jsonResponse"][str(idx)]
                    for job_id in job_ids:
                        if (
                            job_id in frame_asset
                            and "annotations" in frame_asset[job_id]
                            and frame_asset[job_id]["annotations"]
                        ):
                            frames[idx] = {"latestLabel": {"jsonResponse": frame_asset}}
                            break

        if not frames:
            frames[-1] = asset
        return _LabelFrames(frames, number_of_frames, is_frame_group, asset["externalId"])

    def __init__(
        self, frames: Dict[int, Dict], number_frames: int, is_frame_group: bool, external_id: str
    ) -> None:
        self.frames: Dict[int, Dict] = frames
        self.number_frames: int = number_frames
        self.is_frame_group: bool = is_frame_group
        self.external_id: str = external_id

    def get_leading_zeros(self) -> int:
        """Get leading zeros for file name building."""
        return len(str(self.number_frames))

    def get_label_filename(self, idx: int) -> str:
        """Get label filemame for index."""
        return f"{self.external_id}_{str(idx + 1).zfill(self.get_leading_zeros())}"


def _convert_from_kili_to_yolo_format(
    job_id: str, label: Dict, category_ids: Dict[str, JobCategory]
) -> List[Tuple]:
    # pylint: disable=too-many-locals
    """Extract formatted annotations from labels and save the zip in the buckets."""
    if label is None or "jsonResponse" not in label:
        return []
    json_response = label["jsonResponse"]
    if not (job_id in json_response and "annotations" in json_response[job_id]):
        return []
    annotations = json_response[job_id]["annotations"]
    converted_annotations: List[Tuple] = []
    for annotation in annotations:
        category_idx: JobCategory = category_ids[
            get_category_full_name(job_id, annotation["categories"][0]["name"])
        ]
        if "boundingPoly" not in annotation:
            continue
        bounding_poly = annotation["boundingPoly"]
        if len(bounding_poly) < 1 or "normalizedVertices" not in bounding_poly[0]:
            continue
        normalized_vertices = bounding_poly[0]["normalizedVertices"]
        x_s: List[float] = [vertice["x"] for vertice in normalized_vertices]
        y_s: List[float] = [vertice["y"] for vertice in normalized_vertices]

        if annotation["type"] == JobTool.RECTANGLE:
            x_min, y_min = min(x_s), min(y_s)
            x_max, y_max = max(x_s), max(y_s)
            bbox_center_x, bbox_center_y = (x_min + x_max) / 2, (y_min + y_max) / 2  # type: ignore
            bbox_width, bbox_height = x_max - x_min, y_max - y_min  # type: ignore
            converted_annotations.append(
                (category_idx.id, bbox_center_x, bbox_center_y, bbox_width, bbox_height)
            )

        elif annotation["type"] in {JobTool.POLYGON, JobTool.SEMANTIC}:
            # <class-index> <x1> <y1> <x2> <y2> ... <xn> <yn>
            # Each segmentation label must have a minimum of 3 xy points (polygon)
            points = [val for pair in zip(x_s, y_s) for val in pair]
            converted_annotations.append((category_idx.id, *points))

    return converted_annotations


def get_category_full_name(job_id: str, category_name: str):
    """Return a full name to identify uniquely a category."""
    return f"{job_id}__{category_name}"


def _process_asset(
    asset: Dict,
    images_folder: Path,
    labels_folder: Path,
    category_ids: Dict[str, JobCategory],
    content_repository: AbstractContentRepository,
    with_assets: bool,
    project_input_type: str,
) -> Tuple[List[Tuple[str, str, str]], List[str]]:
    # pylint: disable=too-many-locals, too-many-arguments
    """Process an asset for all job_ids of category_ids."""
    asset_remote_content = []
    job_ids = {job_category.job_id for job_category in category_ids.values()}

    label_frames = _LabelFrames.from_asset(asset, job_ids)

    leading_zeros = 0
    if label_frames.is_frame_group:
        nbr_frames = label_frames.number_frames
        leading_zeros = len(str(nbr_frames))

    # If the asset is a video, we need to cut it into frames
    if project_input_type == "VIDEO" and asset["jsonContent"] == "" and with_assets:
        asset["jsonContent"] = cut_video(
            video_path=asset["content"],
            asset=asset,
            leading_zeros=leading_zeros,
            output_dir=images_folder,
        )

    content_frames = []
    if isinstance(asset["jsonContent"], list):
        content_frames = asset["jsonContent"]
        content_frames = [str(path) for path in content_frames]

    video_filenames = []

    for idx, frame in label_frames.frames.items():
        if label_frames.is_frame_group:
            filename = label_frames.get_label_filename(idx)
            video_filenames.append(filename)
        else:
            filename = asset["externalId"]

        frame_labels = _get_frame_labels(frame, job_ids, category_ids)

        _write_labels_to_file(labels_folder, filename, frame_labels)

        # no need to write asset urls since they are already downloaded
        if with_assets:
            continue

        content_frame = content_frames[idx] if content_frames else asset["content"]
        if content_repository.is_serving(content_frame):
            if content_frames and not label_frames.is_frame_group:
                try:
                    _write_content_frame_to_file(
                        content_frame, images_folder, filename, content_repository
                    )
                except DownloadError as download_error:
                    asset_id = asset["id"]
                    logging.warning("for asset %s: %s", asset_id, str(download_error))
        else:
            asset_remote_content.append([asset["externalId"], content_frame, f"{filename}.txt"])

    return asset_remote_content, video_filenames


def _write_class_file(
    folder: Path,
    category_ids: Dict[str, JobCategory],
    label_format: LabelFormat,
    layout: SplitOption,
):
    """Create a file that contains meta information about the export, depending of Yolo version.

    For the "merged" layout, the category name is prefixed with the job id to avoid duplicates
    since a same category name can be used in several jobs.
    """
    if label_format == "yolo_v4":
        with (folder / "classes.txt").open("wb") as fout:
            for job_category in category_ids.values():
                prefix = f"{job_category.job_id}/" if layout == "merged" else ""
                fout.write(f"{job_category.id} {prefix}{job_category.category_name}\n".encode())

    elif label_format == "yolo_v5":
        with (folder / "data.yaml").open("wb") as fout:
            fout.write(b"names:\n")
            for ind, job_category in enumerate(category_ids.values()):
                prefix = f"{job_category.job_id}/" if layout == "merged" else ""
                fout.write(f"  {ind}: {prefix}{job_category.category_name}\n".encode())

    elif label_format in ("yolo_v7", "yolo_v8"):
        with (folder / "data.yaml").open("wb") as fout:
            categories = ""
            for job_category in category_ids.values():
                prefix = f"{job_category.job_id}/" if layout == "merged" else ""
                categories += f"'{prefix}{job_category.category_name}', "
            fout.write(f"nc: {len(category_ids.items())}\n".encode())
            fout.write(f"names: [{categories[:-2]}]\n".encode())  # remove last comma

    else:
        raise ValueError(f"Unknown Yolo label format: {label_format}")


def _get_frame_labels(
    frame: Dict, job_ids: Set[str], category_ids: Dict[str, JobCategory]
) -> List[Tuple]:
    annotations = []
    for job_id in job_ids:
        job_annotations = _convert_from_kili_to_yolo_format(
            job_id, frame["latestLabel"], category_ids
        )
        annotations += job_annotations

    return annotations


def _write_content_frame_to_file(
    url_content_frame: str,
    images_folder: Path,
    filename: str,
    content_repository: AbstractContentRepository,
):
    content_iterator = content_repository.get_content_stream(url_content_frame, 1024)
    with (images_folder / f"{filename}.jpg").open("wb") as fout:
        for block in content_iterator:
            if not block:
                break
            fout.write(block)


def _write_labels_to_file(labels_folder: Path, filename: str, annotations: List[Tuple]) -> None:
    file_path = labels_folder / f"{filename}.txt"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("wb") as fout:
        for category_idx, *points in annotations:
            points_str = " ".join([str(point) for point in points])
            fout.write(f"{category_idx} {points_str}\n".encode())
