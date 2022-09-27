"""
Common code for the yolo exporter.
"""

import csv
import json
import logging
import os
from typing import Dict, List, Set

from kili.services.export.format.base import BaseExporter
from kili.services.export.repository import AbstractContentRepository, DownloadError
from kili.services.export.types import JobCategory, LabelFormat, YoloAnnotation
from kili.utils.tqdm import tqdm


class LabelFrames:
    """
    Holds asset frames data.
    """

    @staticmethod
    def from_asset(asset, job_ids) -> "LabelFrames":
        """
        Instantiate the label frames from the asset. It handles the case when there are several
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
        return LabelFrames(frames, number_of_frames, is_frame_group, asset["externalId"])

    def __init__(
        self, frames: Dict[int, Dict], number_frames: int, is_frame_group: bool, external_id: str
    ) -> None:
        self.frames: Dict[int, Dict] = frames
        self.number_frames: int = number_frames
        self.is_frame_group: bool = is_frame_group
        self.external_id: str = external_id

    def get_leading_zeros(self) -> int:
        """
        Get leading zeros for file name building
        """
        return len(str(self.number_frames))

    def get_label_filename(self, idx: int) -> str:
        """
        Get label filemame for index
        """
        return f"{self.external_id}_{str(idx + 1).zfill(self.get_leading_zeros())}"


class YoloExporter(BaseExporter):
    """
    Common code for Yolo exporters.
    """

    def write_labels_into_single_folder(
        self,
        assets: List[Dict],
        categories_id: Dict[str, JobCategory],
        labels_folder: str,
        images_folder: str,
        base_folder: str,
    ):  # pylint: disable=too-many-arguments
        """
        Write all the labels into a single folder.
        """
        _write_class_file(base_folder, categories_id, self.label_format)

        remote_content = []
        video_metadata = {}

        for asset in tqdm(assets, disable=self.disable_tqdm):
            asset_remote_content, video_filenames = _process_asset(
                asset, images_folder, labels_folder, categories_id, self.content_repository
            )
            if video_filenames:
                video_metadata[asset["externalId"]] = video_filenames
            remote_content.extend(asset_remote_content)

        if video_metadata:
            _write_video_metadata_file(video_metadata, base_folder)

        if len(remote_content) > 0:
            _write_remote_content_file(remote_content, images_folder)


def _convert_from_kili_to_yolo_format(
    job_id: str, label: Dict, category_ids: Dict[str, JobCategory]
) -> List[YoloAnnotation]:
    # pylint: disable=too-many-locals
    """
    Extract formatted annotations from labels and save the zip in the buckets.
    """
    if label is None or "jsonResponse" not in label:
        return []
    json_response = label["jsonResponse"]
    if not (job_id in json_response and "annotations" in json_response[job_id]):
        return []
    annotations = json_response[job_id]["annotations"]
    converted_annotations = []
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
        x_s = [vertice["x"] for vertice in normalized_vertices]
        y_s = [vertice["y"] for vertice in normalized_vertices]
        x_min, y_min = min(x_s), min(y_s)
        x_max, y_max = max(x_s), max(y_s)
        _x_, _y_ = (x_max + x_min) / 2, (y_max + y_min) / 2
        _w_, _h_ = x_max - x_min, y_max - y_min

        converted_annotations.append((category_idx.id, _x_, _y_, _w_, _h_))
    return converted_annotations


def get_category_full_name(job_id: str, category_name: str):
    """
    Return a full name to identify uniquely a category
    """
    return f"{job_id}__{category_name}"


def _process_asset(
    asset: Dict,
    images_folder: str,
    labels_folder: str,
    category_ids: Dict[str, JobCategory],
    content_repository: AbstractContentRepository,
):
    # pylint: disable=too-many-locals, too-many-branches
    """
    Process an asset for all job_ids of category_ids.
    """
    asset_remote_content = []
    job_ids = set(map(lambda job_category: job_category.job_id, category_ids.values()))

    label_frames = LabelFrames.from_asset(asset, job_ids)

    content_frames = content_repository.get_content_frames_paths(asset)

    video_filenames = []

    for idx, frame in label_frames.frames.items():
        if label_frames.is_frame_group:
            filename = label_frames.get_label_filename(idx)
            video_filenames.append(filename)
        else:
            filename = asset["externalId"]

        frame_labels = _get_frame_labels(frame, job_ids, category_ids)

        if not frame_labels:
            continue

        _write_labels_to_file(labels_folder, filename, frame_labels)

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

    if (
        not content_frames
        and label_frames.is_frame_group
        and content_repository.is_serving(asset["content"])
    ):
        raise NotImplementedError("Export of annotations on videos is not supported yet.")

    return asset_remote_content, video_filenames


def _write_class_file(folder: str, category_ids: Dict[str, JobCategory], label_format: LabelFormat):
    """
    Create a file that contains meta information about the export, depending of Yolo version
    """
    if label_format == "yolo_v4":
        with open(os.path.join(folder, "classes.txt"), "wb") as fout:
            for job_category in category_ids.values():
                fout.write(f"{job_category.id} {job_category.category_name}\n".encode())
    if label_format == "yolo_v5":
        with open(os.path.join(folder, "data.yaml"), "wb") as fout:
            fout.write("names:\n".encode())
            categories = ""
            for ind, job_category in enumerate(category_ids.values()):
                fout.write(f"  {ind}: {job_category.category_name}\n".encode())
    if label_format == "yolo_v7":
        with open(os.path.join(folder, "data.yaml"), "wb") as fout:
            categories = ""
            for job_category in category_ids.values():
                categories += f"'{job_category.category_name}', "
            fout.write(f"nc: {len(category_ids.items())}\n".encode())
            fout.write(f"names: [{categories[:-2]}]\n".encode())


def _get_frame_labels(
    frame: Dict, job_ids: Set[str], category_ids: Dict[str, JobCategory]
) -> List[YoloAnnotation]:
    annotations = []
    for job_id in job_ids:
        job_annotations = _convert_from_kili_to_yolo_format(
            job_id, frame["latestLabel"], category_ids
        )
        annotations += job_annotations

    return annotations


def _write_content_frame_to_file(
    url_content_frame: str,
    images_folder: str,
    filename: str,
    content_repository: AbstractContentRepository,
):
    content_iterator = content_repository.get_content_stream(url_content_frame, 1024)
    with open(os.path.join(images_folder, f"{filename}.jpg"), "wb") as fout:
        for block in content_iterator:
            if not block:
                break
            fout.write(block)


def _write_labels_to_file(
    labels_folder: str, filename: str, annotations: List[YoloAnnotation]
) -> None:
    with open(os.path.join(labels_folder, f"{filename}.txt"), "wb") as fout:
        for category_idx, _x_, _y_, _w_, _h_ in annotations:
            fout.write(f"{category_idx} {_x_} {_y_} {_w_} {_h_}\n".encode())


def _write_video_metadata_file(video_metadata: Dict, base_folder: str) -> None:
    """
    Write video metadata file
    """
    video_metadata_json = json.dumps(video_metadata, sort_keys=True, indent=4)
    if video_metadata_json is not None:
        meta_json_path = os.path.join(base_folder, "video_meta.json")
        with open(meta_json_path, "wb") as output_file:
            output_file.write(video_metadata_json.encode("utf-8"))


def _write_remote_content_file(remote_content: List[str], images_folder: str) -> None:
    """
    Write remote content file
    """
    remote_content_header = ["external id", "url", "label file"]
    remote_file_path = os.path.join(images_folder, "remote_assets.csv")
    with open(remote_file_path, "w", encoding="utf8") as file:
        writer = csv.writer(file)
        writer.writerow(remote_content_header)
        writer.writerows(remote_content)
