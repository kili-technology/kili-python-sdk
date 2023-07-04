"""Common code for the Kili exporter."""

import json
import os
from pathlib import Path
from typing import Dict, List

from kili.orm import Asset
from kili.services.export.format.base import AbstractExporter
from kili.services.types import Job

from ...exceptions import NotCompatibleInputType
from ...media.video import cut_video


class KiliExporter(AbstractExporter):
    """Common code for Kili exporters."""

    ASSETS_DIR_NAME = "assets"

    def _check_arguments_compatibility(self) -> None:
        """Checks if the export label format is compatible with the export options."""

    def _check_project_compatibility(self) -> None:
        """Checks if the export label format is compatible with the project."""

    def _is_job_compatible(self, job: Job) -> bool:
        """Check if the export label format is compatible with the job."""
        _ = job
        return True  # kili format is compatible with all jobs

    def _save_assets_export(self, assets: List[Asset], output_filename: Path) -> None:
        """Save the assets to a file and return the link to that file."""
        self.logger.info("Exporting to kili format...")

        if self.with_assets:
            if self.project["inputType"] == "VIDEO":
                assets = self._cut_video_assets(assets)

            assets = self._clean_filepaths(assets)

        if self.single_file:
            project_json = json.dumps(assets, sort_keys=True, indent=4)
            self.base_folder.mkdir(parents=True, exist_ok=True)
            with (self.base_folder / "data.json").open("wb") as output_file:
                output_file.write(project_json.encode("utf-8"))
        else:
            labels_folder = self.base_folder / "labels"
            labels_folder.mkdir(parents=True, exist_ok=True)
            for asset in assets:
                external_id = asset["externalId"].replace(" ", "_")
                asset_json = json.dumps(asset, sort_keys=True, indent=4)
                with (labels_folder / f"{external_id}.json").open("wb") as output_file:
                    output_file.write(asset_json.encode("utf-8"))

        self.create_readme_kili_file(self.export_root_folder)

        self.make_archive(self.export_root_folder, output_filename)

        self.logger.warning(output_filename)

    def _clean_filepaths(self, assets: List[Asset]) -> List[Asset]:
        # pylint: disable=line-too-long
        """Remove TemporaryDirectory() prefix from filepaths in "jsonContent" and "content" fields."""
        for asset in assets:
            if os.path.isfile(asset["content"]):
                asset["content"] = str(Path(self.ASSETS_DIR_NAME) / Path(asset["content"]).name)

            json_content_list = []
            if isinstance(asset["jsonContent"], list):
                for filepath in asset["jsonContent"]:
                    if os.path.isfile(filepath):
                        json_content_list.append(
                            str(Path(self.ASSETS_DIR_NAME) / Path(filepath).name)
                        )
                asset["jsonContent"] = json_content_list
        return assets

    def _cut_video_assets(self, assets: List[Asset]) -> List[Asset]:
        """Cut video assets into frames."""
        for asset in assets:
            if asset["jsonContent"] == "" and os.path.isfile(asset["content"]):
                nbr_frames = len(asset.get("latestLabel", {}).get("jsonResponse", {}))
                if nbr_frames == 0:
                    continue
                leading_zeros = len(str(nbr_frames))
                asset["jsonContent"] = cut_video(
                    video_path=asset["content"],
                    asset=asset,
                    leading_zeros=leading_zeros,
                    output_dir=self.images_folder,
                )
        return assets

    def process_and_save(self, assets: List[Asset], output_filename: Path) -> None:
        """Extract formatted annotations from labels and save the json in the buckets."""
        clean_assets = self.preprocess_assets(assets, self.label_format)

        if self.normalized_coordinates is False:
            if self.project["inputType"] == "PDF":
                clean_assets = [self.convert_to_pixel_coords(asset) for asset in clean_assets]
            else:
                raise NotCompatibleInputType(
                    "Export with pixel coordinates is currently only available for PDF assets."
                )

        return self._save_assets_export(
            clean_assets,
            output_filename,
        )

    @property
    def images_folder(self) -> Path:
        """Export images folder."""
        return self.base_folder / self.ASSETS_DIR_NAME

    def convert_to_pixel_coords(self, asset: Asset) -> Asset:
        """Convert asset JSON response normalized vertices to pixel coordinates."""
        if asset.get("latestLabel", {}).get("jsonResponse", {}):
            asset["latestLabel"]["jsonResponse"] = self._scale_label_vertices(
                asset["latestLabel"]["jsonResponse"], asset
            )

        if asset.get("labels"):
            for label in asset["labels"]:
                if label.get("jsonResponse", {}):
                    label["jsonResponse"] = self._scale_label_vertices(label["jsonResponse"], asset)

        return asset

    def _scale_label_vertices(self, json_resp: Dict, asset: Dict) -> Dict:
        scaler_func = (
            _scale_normalized_vertices_pdf_annotation
            if self.project["inputType"] == "PDF"
            else _scale_normalized_vertices_image_annotation
        )

        for job_name in json_resp.keys():
            if self.project["jsonInterface"]["jobs"][job_name]["mlTask"] != "OBJECT_DETECTION":
                continue

            if json_resp.get(job_name, {}).get("annotations"):
                json_resp[job_name]["annotations"] = [
                    scaler_func(ann, asset) for ann in json_resp[job_name]["annotations"]
                ]

        return json_resp


def _scale_vertex(vertex: Dict, width: int, height: int) -> Dict:
    return {"x": vertex["x"] * width, "y": vertex["y"] * height}


def _scale_all_vertices_in_object(object_, width: int, height: int):
    if isinstance(object_, List):
        return [_scale_all_vertices_in_object(obj, width=width, height=height) for obj in object_]

    if isinstance(object_, Dict):
        if all(key in ("x", "y") for key in object_.keys()):
            return _scale_vertex(object_, width=width, height=height)
        return {
            key: _scale_all_vertices_in_object(value, width=width, height=height)
            for key, value in object_.items()
        }

    return object_


def _scale_normalized_vertices_pdf_annotation(annotation: Dict, asset: Dict) -> Dict:
    """Scale normalized vertices of a PDF annotation.

    PDF annotations are different from image annotations because the asset width/height can vary.
    """
    if "annotations" in annotation:
        # pdf annotations have two layers of "annotations"
        # https://docs.kili-technology.com/reference/export-object-entity-detection-and-relation#ner-in-pdfs
        annotation["annotations"] = [
            _scale_normalized_vertices_pdf_annotation(ann, asset)
            for ann in annotation["annotations"]
        ]
        return annotation

    page_number_to_dimensions = {
        page_resolution["pageNumber"]: {
            "width": page_resolution["width"],
            "height": page_resolution["height"],
        }
        for page_resolution in asset["pageResolutions"]
    }

    # an annotation has three keys:
    # - pageNumberArray: list of page numbers
    # - polys: list of polygons
    # - boundingPoly: list of bounding polygons
    # each polygon is a dict with a key "normalizedVertices" that is a list of vertices
    for key in ("polys", "boundingPoly"):
        annotation[key] = [
            {
                **value,  # keep the original normalizedVertices
                "vertices": _scale_all_vertices_in_object(
                    value["normalizedVertices"],
                    width=page_number_to_dimensions[page_number]["width"],
                    height=page_number_to_dimensions[page_number]["height"],
                ),
            }
            for value, page_number in zip(annotation[key], annotation["pageNumberArray"])
        ]

    return annotation


def _scale_normalized_vertices_image_annotation(annotation: Dict, asset: Dict) -> Dict:
    raise NotImplementedError("Image and video annotations are not yet supported.")
    # return _scale_all_vertices_in_object(annotation, asset)  # type: ignore
