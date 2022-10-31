"""
Common code for the coco exporter.
"""

import json
import os
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, List, Tuple, cast

import numpy as np
from PIL import Image
from tqdm.autonotebook import tqdm
from typeguard import typechecked
from typing_extensions import TypedDict

from kili.orm import AnnotationFormat, Asset, Label
from kili.services.export.format.base import BaseExporter
from kili.services.export.types import (
    InputType,
    Job,
    JobName,
    Jobs,
    LabelFormat,
    ProjectId,
)


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


def convert_kili_semantic_to_coco(
    job_name: JobName,
    assets: List[Asset],
    output_dir: Path,
    job: Job,
    title: str,
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
        "date_created": time.strftime("%Y %m %d %H %M"),
    }
    labels_json = _CocoFormat(
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
    cat_kili_id_to_coco_id = _get_kili_cat_id_to_coco_cat_id_mapping(job)
    labels_json["categories"] = _get_coco_categories(cat_kili_id_to_coco_id)
    labels_json["images"], labels_json["annotations"] = _get_coco_images_and_annotations(
        job_name, assets, data_dir, cat_kili_id_to_coco_id
    )

    with (output_dir / "labels.json").open("w") as outfile:
        json.dump(labels_json, outfile)

    classes = list(cat_kili_id_to_coco_id.keys())
    return labels_json, classes


def _filter_out_autosave_labels(
    assets: List[Asset],
) -> List[Asset]:  # FIXME: check if it is handled in the other export jobs
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


def _format_json_response(
    label: Label, label_format: LabelFormat
) -> Dict[str, Dict]:  # FIXME: probably not necessary?
    """
    Format the label JSON response in the requested format
    """
    formatted_json_response = label.json_response(_format=label_format.lower())
    if label_format.lower() == AnnotationFormat.Simple:
        label["jsonResponse"] = formatted_json_response
    else:
        json_response = {}
        if formatted_json_response is not None:
            for key, value in cast(Dict, formatted_json_response).items():  # FIXME: see above
                if key.isdigit():
                    json_response[int(key)] = value
                    continue
                json_response[key] = value
            label["jsonResponse"] = json_response
        else:
            label["jsonResponse"] = {}
    return label


def _process_assets(assets: List[Asset], label_format: LabelFormat) -> List[Asset]:
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


def _get_kili_cat_id_to_coco_cat_id_mapping(job: Job) -> Dict[str, int]:
    cats = job["content"]["categories"]
    mapping_cat_name_cat_kili_id = {cat["name"]: catId for catId, cat in cats.items()}
    cat_kili_ids = list(mapping_cat_name_cat_kili_id.values())
    cat_kili_id_to_coco_id = {str(categoryId): i for i, categoryId in enumerate(cat_kili_ids)}
    return cat_kili_id_to_coco_id


def _get_coco_images_and_annotations(
    job_name, assets, data_dir, cat_kili_id_to_coco_id
) -> Tuple[List[_CocoImage], List[_CocoAnnotation]]:
    coco_images = []
    coco_annotations = []
    annotation_offset = -1
    for asset_i, asset in tqdm(
        enumerate(assets),
        desc="Convert to coco format",
    ):
        annotations_ = asset["latestLabel"]["jsonResponse"][job_name]["annotations"]
        img = Image.open(asset["content"])

        file_name = data_dir / f"{asset_i}.jpg"  # FIXME: take original format
        width, height = img.size
        img.save(file_name)

        image_coco = _CocoImage(
            id=asset_i,
            license=0,
            file_name=str(file_name),
            height=height,
            width=width,
            date_captured=None,
        )

        coco_images.append(image_coco)
        coco_img_annotations, annotation_offset = _get_coco_image_annotations(
            annotations_,
            cat_kili_id_to_coco_id,
            annotation_offset,
            asset_i,
            width,
            height,
        )
        coco_annotations.extend(coco_img_annotations)
    return coco_images, coco_annotations


@typechecked
def _get_coco_image_annotations(
    annotations_: List[Dict],
    cat_kili_id_to_coco_id: Dict[str, int],
    annotation_offset: int,
    asset_i: int,
    width: int,
    height: int,
) -> Tuple[List[_CocoAnnotation], int]:
    coco_annotations = []

    annotation_j = annotation_offset

    for annotation in annotations_:  # we do not use enumerate as some annotations may be empty
        annotation_j += 1

        if not annotation:
            print("continue")
            continue
        print(annotation)
        bounding_poly = annotation["boundingPoly"]
        print(bounding_poly[0])
        p_x = [float(v["x"]) * width for v in bounding_poly[0]["normalizedVertices"]]
        p_y = [float(v["y"]) * height for v in bounding_poly[0]["normalizedVertices"]]
        poly_ = [(float(x), float(y)) for x, y in zip(p_x, p_y)]
        if len(poly_) < 3:
            print("A polygon must contain more than 2 points. Skipping this polygon...")
            continue

        poly = [p for x in poly_ for p in x]

        categories = annotation["categories"]
        cat_coco_id = cat_kili_id_to_coco_id[categories[0]["name"]]
        annotations_coco = _CocoAnnotation(
            id=annotation_j,
            image_id=asset_i,
            category_id=cat_coco_id,
            bbox=[int(np.min(p_x)), int(np.min(p_y)), int(np.max(p_x)), int(np.max(p_y))],
            # Objects have only one connected part.
            # But a type of object can appear several times on the same image.
            # The limitation of the single connected part comes from Kili.
            segmentation=[poly],
            area=height * width,
            iscrowd=0,
        )
        coco_annotations.append(annotations_coco)
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


def _get_project(kili, project_id: ProjectId) -> Tuple[InputType, Jobs, str]:
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

    def _save_assets_export(self, assets: List[Asset], output_directory: str):
        """
        Save the assets to a file and return the link to that file
        """
        _, jobs, title = _get_project(self.kili, self.project_id)

        for job_name, job in jobs.items():
            convert_kili_semantic_to_coco(
                job_name=job_name,
                assets=assets,
                output_dir=Path(output_directory) / job_name,
                job=job,
                title=title,
            )

    def process_and_save(self, assets: List[Asset], output_filename: str):
        """
        Extract formatted annotations from labels.
        """
        clean_assets = _process_assets(assets, self.label_format)

        with TemporaryDirectory() as tmp_dir:
            self._save_assets_export(
                clean_assets,
                tmp_dir,
            )
            assert os.path.exists(tmp_dir)
            self.create_readme_kili_file(Path(tmp_dir))
            self.make_archive(tmp_dir, output_filename)

        self.logger.warning(output_filename)
