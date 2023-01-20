"""
Common code for the coco exporter.
"""

import json
import time
import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from typing_extensions import TypedDict

from kili.orm import Asset, JobMLTask, JobTool
from kili.services.export.exceptions import NoCompatibleJobError, NotCompatibleInputType
from kili.services.export.format.base import AbstractExporter
from kili.services.types import Job, JobName
from kili.utils.tqdm import tqdm

from ...media.image import get_image_dimensions
from ...media.video import cut_video, get_video_dimensions

DATA_SUBDIR = "data"


# COCO format
class _CocoImage(TypedDict):
    id: int
    license: int
    file_name: str
    height: int
    width: int
    date_captured: None


class _CocoCategory(TypedDict):
    id: int
    name: str
    supercategory: str


class _CocoAnnotation(TypedDict):
    id: int
    image_id: int
    category_id: int
    bbox: List[int]
    segmentation: List[List[float]]  # [[x, y, x, y, x ...]]
    area: int
    iscrowd: int


class _CocoFormat(TypedDict):
    info: Dict  # type: ignore
    licenses: List[Dict]  # type: ignore
    categories: List[_CocoCategory]
    images: List[_CocoImage]
    annotations: List[_CocoAnnotation]


class CocoExporter(AbstractExporter):
    """
    Common code for COCO exporter.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.with_assets:
            warnings.warn(
                "For an export to the COCO format, the download of assets cannot be disabled."
            )
        self.with_assets = True

    def _check_arguments_compatibility(self):
        """
        Checks if the export label format is compatible with the export options.
        """

    def _check_project_compatibility(self) -> None:
        """
        Checks if the export label format is compatible with the project.
        """
        if self.project_input_type not in ("IMAGE", "VIDEO"):
            raise NotCompatibleInputType(
                f"Project with input type '{self.project_input_type}' not compatible with COCO"
                " export format."
            )

        if len(self.compatible_jobs) == 0:
            raise NoCompatibleJobError(
                f"Project needs at least one {JobMLTask.ObjectDetection} task with bounding boxes"
                " or segmentations."
            )

    @property
    def images_folder(self) -> Path:
        """
        Export images folder
        """
        return self.base_folder / DATA_SUBDIR

    def process_and_save(self, assets: List[Asset], output_filename: Path):
        """
        Extract formatted annotations from labels.
        """
        clean_assets = self.process_assets(assets, self.label_format)

        self._save_assets_export(
            clean_assets,
            self.export_root_folder,
        )
        self.create_readme_kili_file(self.export_root_folder)
        self.make_archive(self.export_root_folder, output_filename)

        self.logger.warning(output_filename)

    def _save_assets_export(self, assets: List[Asset], output_directory: Path):
        """
        Save the assets to a file and return the link to that file
        """
        for job_name, job in self.project_json_interface["jobs"].items():
            if self._is_job_compatibile(job):
                _convert_kili_semantic_to_coco(
                    job_name=job_name,
                    assets=assets,
                    output_dir=Path(output_directory) / self.project_id,
                    job=job,
                    title=self.project_title,
                    project_input_type=self.project_input_type,
                )
            else:
                self.logger.warning(f"Job {job_name} is not compatible with the COCO format.")

    def _is_job_compatibile(self, job: Job) -> bool:
        if "tools" not in job:
            return False
        return (JobTool.Semantic in job["tools"] or JobTool.Rectangle in job["tools"]) and job[
            "mlTask"
        ] == JobMLTask.ObjectDetection


# pylint: disable=too-many-arguments
def _convert_kili_semantic_to_coco(
    job_name: JobName,
    assets: List[Asset],
    output_dir: Path,
    job: Job,
    title: str,
    project_input_type: str,
) -> Tuple[_CocoFormat, List[str]]:
    """
    creates the following structure on the disk:
    <dataset_dir>/
        data/
            <filename0>.<ext>
            <filename1>.<ext>
            ...
        labels.json


    We iterate on the assets and create a coco format for each asset.
    """
    infos_coco = {
        "year": time.strftime("%Y"),
        "version": "1.0",
        "description": f"{title} - Exported from Kili Python Client",
        "contributor": "Kili Technology",
        "url": "https://kili-technology.com",
        "date_created": datetime.now().isoformat(),
    }
    labels_json = _CocoFormat(
        info=infos_coco,
        licenses=[],
        categories=[],
        images=[],
        annotations=[],
    )

    # Mapping category - category id
    cat_kili_id_to_coco_id = _get_kili_cat_id_to_coco_cat_id_mapping(job)
    labels_json["categories"] = _get_coco_categories(cat_kili_id_to_coco_id)
    labels_json["images"], labels_json["annotations"] = _get_coco_images_and_annotations(
        job_name, assets, cat_kili_id_to_coco_id, project_input_type
    )

    label_file_name = output_dir / job_name / "labels.json"
    label_file_name.parent.mkdir(parents=True, exist_ok=True)
    with (output_dir / job_name / "labels.json").open("w") as outfile:
        json.dump(labels_json, outfile)

    classes = list(cat_kili_id_to_coco_id.keys())
    return labels_json, classes


def _get_kili_cat_id_to_coco_cat_id_mapping(job: Job) -> Dict[str, int]:
    cats = job["content"]["categories"]
    mapping_cat_name_cat_kili_id = {cat["name"]: catId for catId, cat in cats.items()}
    cat_kili_ids = list(mapping_cat_name_cat_kili_id.values())
    cat_kili_id_to_coco_id = {str(categoryId): i for i, categoryId in enumerate(cat_kili_ids)}
    return cat_kili_id_to_coco_id


# pylint: disable=too-many-locals
def _get_coco_images_and_annotations(
    job_name, assets, cat_kili_id_to_coco_id, project_input_type
) -> Tuple[List[_CocoImage], List[_CocoAnnotation]]:
    coco_images = []
    coco_annotations = []
    annotation_offset = 0
    for asset_i, asset in tqdm(enumerate(assets), desc="Convert to coco format"):
        if project_input_type == "IMAGE":
            width, height = get_image_dimensions(asset["content"])
            coco_image = _CocoImage(
                id=asset_i,
                license=0,
                file_name=str(DATA_SUBDIR + "/" + Path(asset["content"]).name),
                height=height,
                width=width,
                date_captured=None,
            )

            coco_images.append(coco_image)
            if job_name not in asset["latestLabel"]["jsonResponse"]:
                coco_img_annotations = []
                # annotation offset is unchanged
            else:
                coco_img_annotations, annotation_offset = _get_coco_image_annotations(
                    asset["latestLabel"]["jsonResponse"][job_name]["annotations"],
                    cat_kili_id_to_coco_id,
                    annotation_offset,
                    coco_image,
                )
            coco_annotations.extend(coco_img_annotations)

        elif project_input_type == "VIDEO":
            nbr_frames = len(asset.get("latestLabel", {}).get("jsonResponse", {}))
            leading_zeros = len(str(nbr_frames))

            width = height = 0
            frame_ext = ""
            # jsonContent with frames
            if isinstance(asset["jsonContent"], list) and Path(asset["jsonContent"][0]).is_file():
                width, height = get_image_dimensions(asset["jsonContent"][0])
                frame_ext = Path(asset["jsonContent"][0]).suffix

            # video with shouldUseNativeVideo set to True (no frames available)
            elif Path(asset["content"]).is_file():
                width, height = get_video_dimensions(asset["content"])
                cut_video(asset["content"], asset, leading_zeros, Path(asset["content"]).parent)
                frame_ext = ".jpg"

            else:
                raise FileNotFoundError(f"Could not find frames or video for asset {asset}")

            for frame_i, (frame_id, json_response) in enumerate(
                asset["latestLabel"]["jsonResponse"].items()
            ):
                frame_name = f'{asset["externalId"]}_{str(int(frame_id)+1).zfill(leading_zeros)}'
                coco_image = _CocoImage(
                    id=frame_i + len(assets),  # add offset to avoid duplicate ids
                    license=0,
                    file_name=str(DATA_SUBDIR + "/" + f"{frame_name}{frame_ext}"),
                    height=height,
                    width=width,
                    date_captured=None,
                )
                coco_images.append(coco_image)

                if job_name not in json_response:
                    coco_img_annotations = []
                    # annotation offset is unchanged
                else:
                    coco_img_annotations, annotation_offset = _get_coco_image_annotations(
                        json_response[job_name]["annotations"],
                        cat_kili_id_to_coco_id,
                        annotation_offset,
                        coco_image,
                    )
                coco_annotations.extend(coco_img_annotations)

    return coco_images, coco_annotations


def _get_coco_image_annotations(
    annotations_: List[Dict],
    cat_kili_id_to_coco_id: Dict[str, int],
    annotation_offset: int,
    asset: _CocoImage,
) -> Tuple[List[_CocoAnnotation], int]:
    coco_annotations = []

    annotation_j = annotation_offset

    for annotation in annotations_:  # we do not use enumerate as some annotations may be empty
        annotation_j += 1

        if not annotation:
            print("continue")
            continue
        bounding_poly = annotation["boundingPoly"]
        p_x = [float(v["x"]) * asset["width"] for v in bounding_poly[0]["normalizedVertices"]]
        p_y = [float(v["y"]) * asset["height"] for v in bounding_poly[0]["normalizedVertices"]]
        poly_ = [(float(x), float(y)) for x, y in zip(p_x, p_y)]
        if len(poly_) < 3:
            print("A polygon must contain more than 2 points. Skipping this polygon...")
            continue

        poly = [p for x in poly_ for p in x]

        categories = annotation["categories"]
        coco_annotations.append(
            _CocoAnnotation(
                id=annotation_j,
                image_id=asset["id"],
                category_id=cat_kili_id_to_coco_id[categories[0]["name"]],
                bbox=[int(np.min(p_x)), int(np.min(p_y)), int(np.max(p_x)), int(np.max(p_y))],
                # Objects have only one connected part.
                # But a type of object can appear several times on the same image.
                # The limitation of the single connected part comes from Kili.
                segmentation=[poly],
                area=asset["height"] * asset["width"],
                iscrowd=0,
            )
        )
    return coco_annotations, annotation_j


def _get_coco_categories(cat_kili_id_to_coco_id) -> List[_CocoCategory]:
    categories_coco: List[_CocoCategory] = []
    for cat_kili_id, cat_coco_id in cat_kili_id_to_coco_id.items():
        categories_coco.append(
            {
                "id": cat_coco_id,
                "name": cat_kili_id,
                "supercategory": "",
            }
        )

    return categories_coco
