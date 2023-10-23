"""Common code for the coco exporter."""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from kili.domain.ontology import JobMLTask, JobTool
from kili.services.export.exceptions import (
    NoCompatibleJobError,
    NotCompatibleInputType,
    NotCompatibleOptions,
)
from kili.services.export.format.base import AbstractExporter
from kili.services.export.format.coco.types import (
    CocoAnnotation,
    CocoCategory,
    CocoFormat,
    CocoImage,
)
from kili.services.export.media.image import get_frame_dimensions, get_image_dimensions
from kili.services.export.media.video import cut_video, get_video_dimensions
from kili.services.export.types import CocoAnnotationModifier
from kili.services.types import Job, JobName
from kili.utils.tqdm import tqdm

DATA_SUBDIR = "data"


# COCO format


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

    def process_and_save(self, assets: List[Dict], output_filename: Path):
        """Extract formatted annotations from labels."""
        clean_assets = self.preprocess_assets(assets)

        self._save_assets_export(
            clean_assets, self.export_root_folder, annotation_modifier=self.annotation_modifier
        )
        self.create_readme_kili_file(self.export_root_folder)
        self.make_archive(self.export_root_folder, output_filename)

        self.logger.warning(output_filename)

    def _save_assets_export(
        self,
        assets: List[Dict],
        output_directory: Path,
        annotation_modifier: Optional[CocoAnnotationModifier],
    ):
        """Save the assets to a file and return the link to that file."""
        if self.split_option == "split":
            for job_name, job in self.project["jsonInterface"]["jobs"].items():
                if self._is_job_compatible(job):
                    _convert_kili_semantic_to_coco(
                        jobs={job_name: job},
                        assets=assets,
                        output_dir=Path(output_directory) / self.project["id"],
                        title=self.project["title"],
                        project_input_type=self.project["inputType"],
                        annotation_modifier=annotation_modifier,
                        merged=False,
                    )
                else:
                    self.logger.warning(f"Job {job_name} is not compatible with the COCO format.")
        else:  # merged
            _convert_kili_semantic_to_coco(
                jobs={
                    k: job
                    for k, job in self.project["jsonInterface"]["jobs"].items()
                    if self._is_job_compatible(job)
                },
                assets=assets,
                output_dir=Path(output_directory) / self.project["id"],
                title=self.project["title"],
                project_input_type=self.project["inputType"],
                annotation_modifier=annotation_modifier,
                merged=True,
            )

    def _is_job_compatible(self, job: Job) -> bool:
        if "tools" not in job:
            return False
        return (JobTool.SEMANTIC in job["tools"] or JobTool.RECTANGLE in job["tools"]) and job[
            "mlTask"
        ] == JobMLTask.OBJECT_DETECTION


# pylint: disable=too-many-arguments
def _convert_kili_semantic_to_coco(
    jobs: Dict[JobName, Job],
    assets: List[Dict],
    output_dir: Path,
    title: str,
    project_input_type: str,
    annotation_modifier: Optional[CocoAnnotationModifier],
    merged: bool,
) -> Tuple[CocoFormat, List[Path]]:
    """Creates the following structure on the disk.

    <dataset_dir>/
        data/
            <filename0>.<ext>
            <filename1>.<ext>
            ...
        labels.json.

    We iterate on the assets and create a coco format for each asset.

    Note: the jobs should only contains elligible jobs.
    """
    infos_coco = {
        "year": time.strftime("%Y"),
        "version": "1.0",
        "description": f"{title} - Exported from Kili Python Client",
        "contributor": "Kili Technology",
        "url": "https://kili-technology.com",
        "date_created": datetime.now().isoformat(),
    }
    labels_json = CocoFormat(
        info=infos_coco,
        licenses=[],
        categories=[],
        images=[],
        annotations=[],
    )

    # Mapping category - category id
    cat_kili_id_to_coco_id, labels_json["categories"] = _get_coco_categories_with_mapping(
        jobs, merged
    )

    if merged:
        labels_json["images"], labels_json["annotations"] = _get_coco_images_and_annotations(
            jobs,
            assets,
            cat_kili_id_to_coco_id,
            project_input_type,
            annotation_modifier,
            is_single_job=False,
        )

        label_file_name = output_dir / "labels.json"
        label_file_name.parent.mkdir(parents=True, exist_ok=True)
        with label_file_name.open("w") as outfile:
            json.dump(labels_json, outfile)
        label_filenames = [label_file_name]
    else:  # split case
        label_filenames = []
        for job_name, job in jobs.items():
            labels_json["images"], labels_json["annotations"] = _get_coco_images_and_annotations(
                {job_name: job},
                assets,
                cat_kili_id_to_coco_id,
                project_input_type,
                annotation_modifier,
                is_single_job=True,
            )
            label_file_name = output_dir / job_name / "labels.json"

            label_file_name.parent.mkdir(parents=True, exist_ok=True)
            with label_file_name.open("w") as outfile:
                json.dump(labels_json, outfile)
            label_filenames.append(label_file_name)

    return labels_json, label_filenames


def _get_coco_categories_with_mapping(
    jobs: Dict[JobName, Job], merged: bool
) -> Tuple[Dict[JobName, Dict[str, int]], List[CocoCategory]]:
    """_get_coco_categories_with_mapping.

    Get the mapping between a category name in Kili of a given job and the COCO category id, and
    also return the list of COCO categories.
    """
    if merged:
        mapping_cat_name_cat_kili_id: Dict[str, str] = {}
        cat_kili_id_to_coco_id: Dict[JobName, Dict[str, int]] = {}
        id_offset = 0
        for job_name, job in sorted(jobs.items(), key=lambda x: x[0]):
            content = dict(job["content"])
            job_cats: Dict[str, Any] = content["categories"]
            mapping_cat_name_cat_kili_id = {
                "/".join([job_name, cat["name"]]): cat_id for cat_id, cat in job_cats.items()
            }

            cat_kili_ids = sorted(mapping_cat_name_cat_kili_id.values())
            cat_kili_id_to_coco_id[job_name] = {
                str(category_id): i + id_offset for i, category_id in enumerate(cat_kili_ids)
            }
            id_offset += len(cat_kili_ids)

    else:
        assert (
            len(list(jobs.values())) == 1
        ), "When this method is called with merged = False, the jobs should only contain 1 job"
        job_name = next(iter(jobs.keys()))
        cats = next(iter(jobs.values()))["content"]["categories"]
        mapping_cat_name_cat_kili_id = {cat["name"]: cat_id for cat_id, cat in cats.items()}
        cat_kili_ids = list(mapping_cat_name_cat_kili_id.values())
        cat_kili_id_to_coco_id = {
            job_name: {str(category_id): i for i, category_id in enumerate(cat_kili_ids)}
        }

    return cat_kili_id_to_coco_id, _get_coco_categories(cat_kili_id_to_coco_id, merged)


# pylint: disable=too-many-locals
def _get_coco_images_and_annotations(
    jobs: Dict[JobName, Job],
    assets: List[Dict],
    cat_kili_id_to_coco_id: Dict[JobName, Dict[str, int]],
    project_input_type: str,
    annotation_modifier: Optional[CocoAnnotationModifier],
    is_single_job: bool,
) -> Tuple[List[CocoImage], List[CocoAnnotation]]:
    if project_input_type == "IMAGE":
        return _get_images_and_annotation_for_images(
            jobs, assets, cat_kili_id_to_coco_id, annotation_modifier, is_single_job
        )

    if project_input_type == "VIDEO":
        return _get_images_and_annotation_for_videos(
            jobs, assets, cat_kili_id_to_coco_id, annotation_modifier, is_single_job
        )

    raise NotImplementedError(f"No conversion to COCO possible for input type {project_input_type}")


def _get_images_and_annotation_for_images(
    jobs: Dict[JobName, Job],
    assets: List[Dict],
    cat_kili_id_to_coco_id: Dict[JobName, Dict[str, int]],
    annotation_modifier: Optional[CocoAnnotationModifier],
    is_single_job: bool,
) -> Tuple[List[CocoImage], List[CocoAnnotation]]:
    coco_images = []
    coco_annotations = []
    annotation_offset = 0

    for asset_i, asset in tqdm(enumerate(assets), desc="Convert to coco format"):
        width, height = get_image_dimensions(asset)
        if Path(asset["content"]).is_file():
            filename = str(DATA_SUBDIR + "/" + Path(asset["content"]).name)
        else:
            filename = str(DATA_SUBDIR + "/" + asset["externalId"])
        coco_image = CocoImage(
            id=asset_i,
            license=0,
            file_name=filename,
            height=height,
            width=width,
            date_captured=None,
        )

        coco_images.append(coco_image)
        if is_single_job:
            assert len(list(jobs.keys())) == 1
            job_name = next(iter(jobs.keys()))

            if job_name not in asset["latestLabel"]["jsonResponse"]:
                coco_img_annotations = []
                # annotation offset is unchanged
            else:
                coco_img_annotations, annotation_offset = _get_coco_image_annotations(
                    asset["latestLabel"]["jsonResponse"][job_name]["annotations"],
                    cat_kili_id_to_coco_id[job_name],
                    annotation_offset,
                    coco_image,
                    annotation_modifier=annotation_modifier,
                )
            coco_annotations.extend(coco_img_annotations)
        else:
            for job_name in jobs:
                if job_name not in asset["latestLabel"]["jsonResponse"]:
                    continue
                    # annotation offset is unchanged

                coco_img_annotations, annotation_offset = _get_coco_image_annotations(
                    asset["latestLabel"]["jsonResponse"][job_name]["annotations"],
                    cat_kili_id_to_coco_id[job_name],
                    annotation_offset,
                    coco_image,
                    annotation_modifier=annotation_modifier,
                )
                coco_annotations.extend(coco_img_annotations)
    return coco_images, coco_annotations


def _get_images_and_annotation_for_videos(
    jobs: Dict[JobName, Job],
    assets: List[Dict],
    cat_kili_id_to_coco_id: Dict[JobName, Dict[str, int]],
    annotation_modifier: Optional[CocoAnnotationModifier],
    is_single_job: bool,
) -> Tuple[List[CocoImage], List[CocoAnnotation]]:
    coco_images = []
    coco_annotations = []
    annotation_offset = 0

    for asset in tqdm(assets, desc="Convert to coco format"):
        nbr_frames = len(asset.get("latestLabel", {}).get("jsonResponse", {}))
        leading_zeros = len(str(nbr_frames))

        width = height = 0
        frame_ext = ""
        # jsonContent with frames
        if isinstance(asset["jsonContent"], list) and Path(asset["jsonContent"][0]).is_file():
            width, height = get_frame_dimensions(asset)
            frame_ext = Path(asset["jsonContent"][0]).suffix

        # video with shouldUseNativeVideo set to True (no frames available)
        elif Path(asset["content"]).is_file():
            width, height = get_video_dimensions(asset)
            cut_video(asset["content"], asset, leading_zeros, Path(asset["content"]).parent)
            frame_ext = ".jpg"

        else:
            raise FileNotFoundError(f"Could not find frames or video for asset {asset}")

        for frame_i, (frame_id, json_response) in enumerate(
            asset["latestLabel"]["jsonResponse"].items()
        ):
            frame_name = f'{asset["externalId"]}_{str(int(frame_id)+1).zfill(leading_zeros)}'
            coco_image = CocoImage(
                id=frame_i + len(assets),  # add offset to avoid duplicate ids
                license=0,
                file_name=str(DATA_SUBDIR + "/" + f"{frame_name}{frame_ext}"),
                height=height,
                width=width,
                date_captured=None,
            )
            coco_images.append(coco_image)

            if is_single_job:
                job_name = next(iter(jobs.keys()))
                if job_name not in json_response:
                    coco_img_annotations = []
                    # annotation offset is unchanged
                else:
                    coco_img_annotations, annotation_offset = _get_coco_image_annotations(
                        json_response[job_name]["annotations"],
                        cat_kili_id_to_coco_id[job_name],
                        annotation_offset,
                        coco_image,
                        annotation_modifier,
                    )
                coco_annotations.extend(coco_img_annotations)
            else:
                for job_name in jobs:
                    if job_name not in asset["latestLabel"]["jsonResponse"]:
                        continue
                    coco_img_annotations, annotation_offset = _get_coco_image_annotations(
                        json_response[job_name]["annotations"],
                        cat_kili_id_to_coco_id[job_name],
                        annotation_offset,
                        coco_image,
                        annotation_modifier,
                    )

                    coco_annotations.extend(coco_img_annotations)

    return coco_images, coco_annotations


def _get_coco_image_annotations(
    annotations_: List[Dict],
    cat_kili_id_to_coco_id: Dict[str, int],
    annotation_offset: int,
    coco_image: CocoImage,
    annotation_modifier: Optional[CocoAnnotationModifier],
) -> Tuple[List[CocoAnnotation], int]:
    coco_annotations = []

    annotation_j = annotation_offset

    for annotation in annotations_:  # we do not use enumerate as some annotations may be empty
        annotation_j += 1

        if not annotation:
            print("continue")
            continue
        bounding_poly = annotation["boundingPoly"]
        bbox, poly = _get_coco_geometry_from_kili_bpoly(
            bounding_poly, coco_image["width"], coco_image["height"]
        )
        if len(poly) < 6:  # twice the number of vertices
            print("A polygon must contain more than 2 points. Skipping this polygon...")
            continue

        categories = annotation["categories"]
        coco_annotation = CocoAnnotation(
            id=annotation_j,
            image_id=coco_image["id"],
            category_id=cat_kili_id_to_coco_id[categories[0]["name"]],
            bbox=bbox,
            # Objects have only one connected part.
            # But a type of object can appear several times on the same image.
            # The limitation of the single connected part comes from Kili.
            segmentation=[poly],
            area=coco_image["height"] * coco_image["width"],
            iscrowd=0,
        )

        if annotation_modifier:
            coco_annotation = annotation_modifier(
                dict(coco_annotation), dict(coco_image), annotation
            )

        coco_annotations.append(coco_annotation)
    return coco_annotations, annotation_j


def _get_coco_geometry_from_kili_bpoly(
    bounding_poly: List[Dict], asset_width: int, asset_height: int
):
    normalized_vertices = bounding_poly[0]["normalizedVertices"]
    p_x = [float(vertice["x"]) * asset_width for vertice in normalized_vertices]
    p_y = [float(vertice["y"]) * asset_height for vertice in normalized_vertices]
    poly_vertices = [(float(x), float(y)) for x, y in zip(p_x, p_y)]
    x_min, y_min = min(p_x), min(p_y)
    x_max, y_max = max(p_x), max(p_y)
    bbox_width, bbox_height = x_max - x_min, y_max - y_min
    bbox = [int(x_min), int(y_min), int(bbox_width), int(bbox_height)]
    poly = [p for vertice in poly_vertices for p in vertice]
    return bbox, poly


def _get_coco_categories(cat_kili_id_to_coco_id, merged) -> List[CocoCategory]:
    categories_coco: List[CocoCategory] = []
    for job_name, mapping in sorted(cat_kili_id_to_coco_id.items(), key=lambda x: x[0]):
        for cat_kili_id, cat_coco_id in sorted(mapping.items(), key=lambda x: x[1]):
            categories_coco.append(
                {
                    "id": cat_coco_id,
                    "name": cat_kili_id if not merged else f"{job_name}/{cat_kili_id}",
                    "supercategory": job_name,
                }
            )

    return categories_coco
