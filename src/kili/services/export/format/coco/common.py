"""
Common code for the coco exporter.
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import cv2
import numpy as np
from tqdm.autonotebook import tqdm
from typing_extensions import TypedDict

from kili.orm import AnnotationFormat
from kili.services.export.format.base import BaseExporter
from kili.services.export.types import InputType, Job, JobName, Jobs, ProjectId


# COCO format
class ImageCoco(TypedDict):
    id: int
    license: int
    file_name: str
    height: int
    width: int
    date_captured: None


class CategoryCoco(TypedDict):
    id: int
    name: str
    supercategory: str


class AnnotationsCoco(TypedDict):
    id: int
    image_id: int
    category_id: int
    bbox: List[int]
    segmentation: List[List[float]]  # [[x, y, x, y, x ...]]
    area: int
    iscrowd: int


class CocoFormat(TypedDict):
    info: Dict  # type: ignore
    licenses: List[Dict]  # type: ignore
    categories: List[CategoryCoco]
    images: List[ImageCoco]
    annotations: List[AnnotationsCoco]


def get_mapping_category_name_cat_kili_id(job: Job):
    cats = job["content"]["categories"]
    mapping_category_name_category_ids = {cat["name"]: catId for catId, cat in cats.items()}
    return mapping_category_name_category_ids


def _filter_out_autosave_labels(assets: List[Dict]):
    """
    Removes AUTOSAVE labels from exports

    Parameters
    ----------
    - assets: list of assets
    """
    clean_assets = []
    for asset in assets:
        labels = asset.get("labels", [])
        clean_labels = list(filter(lambda label: label["labelType"] != "AUTOSAVE", labels))
        if clean_labels:
            asset["labels"] = clean_labels
        clean_assets.append(asset)
    return clean_assets


def _format_json_response(label, label_format):
    """
    Format the label JSON response in the requested format
    """
    formatted_json_response = label.json_response(_format=label_format.lower())
    if label_format.lower() == AnnotationFormat.Simple:
        label["jsonResponse"] = formatted_json_response
    else:
        json_response = {}
        for key, value in formatted_json_response.items():
            if key.isdigit():
                json_response[int(key)] = value
                continue
            json_response[key] = value
        label["jsonResponse"] = json_response
    return label


def _process_assets(assets, label_format):
    """
    Format labels in the requested format, and filter out autosave labels
    """
    assets_in_format = []
    for asset in assets:
        if "labels" in asset:
            labels_of_asset = []
            for label in asset["labels"]:
                clean_label = _format_json_response(label, label_format)
                labels_of_asset.append(clean_label)
            asset["labels"] = labels_of_asset
        if "latestLabel" in asset:
            label = asset["latestLabel"]
            if label is not None:
                clean_label = _format_json_response(label, label_format)
                asset["latestLabel"] = clean_label
        assets_in_format.append(asset)

    clean_assets = _filter_out_autosave_labels(assets_in_format)
    return clean_assets


def convert_kili_semantic_to_coco(
    job_name: JobName,
    assets: List[Dict],
    output_dir: Path,
    job: Job,
) -> Tuple[CocoFormat, List[str]]:
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
        "description": "Exported from Kili Python Client",
        "contributor": "Kili Technology",
        "url": "https://kili-technology.com",
        "date_created": time.strftime("%Y %m %d %H %M"),
    }
    labels_json = CocoFormat(
        info=infos_coco,
        licenses=[],
        categories=[],
        images=[],
        annotations=[],
    )

    # Prepare output folder
    data_dir = output_dir / "data"
    os.makedirs(data_dir, exist_ok=True)

    # Mapping category - category id
    mapping_cat_name_cat_kili_id = get_mapping_category_name_cat_kili_id(job)
    cat_kili_ids = list(mapping_cat_name_cat_kili_id.values())
    cat_kili_id_to_coco_id = {categoryId: i for i, categoryId in enumerate(cat_kili_ids)}
    for cat_kili_id, cat_coco_id in cat_kili_id_to_coco_id.items():
        categories_coco: CategoryCoco = {
            "id": cat_coco_id,
            "name": cat_kili_id,
            "supercategory": "",
        }
        labels_json["categories"].append(categories_coco)

    # Fill labels_json
    annotation_j = -1
    for asset_i, asset in tqdm(
        enumerate(assets),
        total=len(assets),
        desc="Convert to coco format",
    ):
        annotations_ = asset["latestLabel"]["jsonResponse"][job_name]

        img = cv2.imread(asset["content"])
        file_name = data_dir / f"{asset_i}.jpg"
        cv2.imwrite(str(file_name), img)
        height = img.shape[0]
        width = img.shape[1]
        image_coco = ImageCoco(
            id=asset_i,
            license=0,
            file_name=str(file_name),
            height=height,
            width=width,
            date_captured=None,
        )
        labels_json["images"].append(image_coco)

        for annotation in annotations_:
            annotation_j += 1
            print("Annotation", annotation)
            if not annotation:
                print("continue")
                continue
            bounding_poly = annotation["boundingPoly"]
            px: List[float] = [
                float(v["x"]) * width for v in bounding_poly[0]["normalizedVertices"]
            ]
            py: List[float] = [
                float(v["y"]) * height for v in bounding_poly[0]["normalizedVertices"]
            ]
            poly_ = [(float(x), float(y)) for x, y in zip(px, py)]
            if len(poly_) < 3:
                print("A polygon must contain more than 2 points. Skipping this polygon...")
                continue

            poly = [p for x in poly_ for p in x]

            categories = annotation["categories"]
            cat_coco_id = cat_kili_id_to_coco_id[categories[0]["name"]]
            annotations_coco = AnnotationsCoco(
                id=annotation_j,
                image_id=asset_i,
                category_id=cat_coco_id,
                bbox=[int(np.min(px)), int(np.min(py)), int(np.max(px)), int(np.max(py))],
                # Objects have only one connected part.
                # But a type of object can appear several times on the same image.
                # The limitation of the single connected part comes from Kili.
                segmentation=[poly],
                area=height * width,
                iscrowd=0,
            )
            labels_json["annotations"].append(annotations_coco)

    with (output_dir / "labels.json").open("w") as outfile:
        json.dump(labels_json, outfile)

    classes: List[str] = list(cat_kili_id_to_coco_id.keys())
    return labels_json, classes


def get_project(kili, project_id: ProjectId) -> Tuple[InputType, Jobs, str]:
    projects = kili.projects(project_id=project_id, fields=["inputType", "jsonInterface", "title"])

    if len(projects) == 0:
        raise ValueError(
            "no such project. Maybe your KILI_API_KEY does not belong to a member of the project."
        )
    input_type = projects[0]["inputType"]
    jobs = projects[0]["jsonInterface"].get("jobs", {})
    title = projects[0]["title"]
    return input_type, jobs, title


class CocoExporter(BaseExporter):
    """
    Common code for Kili exporters.
    """

    download_media = True

    def _save_assets_export(self, assets: List[Dict], output_filename: str):
        """
        Save the assets to a file and return the link to that file
        """
        input_type, jobs, title = get_project(self.kili, self.project_id)
        _ = input_type, title

        for job_name, job in jobs.items():
            convert_kili_semantic_to_coco(
                job_name=job_name,
                assets=assets,
                output_dir=Path(output_filename),
                job=job,
            )

    def process_and_save(self, assets: List[Dict], output_filename: str):
        """
        Extract formatted annotations from labels and save the json in the buckets.
        """
        clean_assets = _process_assets(assets, self.label_format)
        return self._save_assets_export(
            clean_assets,
            output_filename,
        )
