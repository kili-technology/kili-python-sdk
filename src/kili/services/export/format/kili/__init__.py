"""Common code for the Kili exporter."""

import json
from pathlib import Path
from typing import Callable, Dict, List

from kili.services.export.exceptions import NotCompatibleInputType, NotCompatibleOptions
from kili.services.export.format.base import AbstractExporter
from kili.services.export.media.video import cut_video
from kili.services.types import Job


class KiliExporter(AbstractExporter):
    """Common code for Kili exporters."""

    ASSETS_DIR_NAME = "assets"

    def _check_arguments_compatibility(self) -> None:
        """Check if the export label format is compatible with the export options."""

    def _check_project_compatibility(self) -> None:
        """Check if the export label format is compatible with the project."""

    def _is_job_compatible(self, job: Job) -> bool:
        """Check if the export label format is compatible with the job."""
        _ = job
        return True  # kili format is compatible with all jobs

    def _save_assets_export(self, assets: List[Dict], output_filename: Path) -> None:
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
                file_path = labels_folder / f"{external_id}.json"
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with file_path.open("wb") as output_file:
                    output_file.write(asset_json.encode("utf-8"))

        self.create_readme_kili_file(self.export_root_folder)

        self.make_archive(self.export_root_folder, output_filename)

        self.logger.warning(output_filename)

    def _clean_filepaths(self, assets: List[Dict]) -> List[Dict]:
        # pylint: disable=line-too-long
        """Remove TemporaryDirectory() prefix from filepaths in "jsonContent" and "content" fields."""
        for asset in assets:
            if Path(asset["content"]).is_file():
                asset["content"] = str(Path(self.ASSETS_DIR_NAME) / Path(asset["content"]).name)

            json_content_list = []
            if isinstance(asset["jsonContent"], list):
                json_content_list = [
                    str(Path(self.ASSETS_DIR_NAME) / Path(filepath).name)
                    for filepath in asset["jsonContent"]
                    if Path(filepath).is_file()
                ]

                asset["jsonContent"] = json_content_list
        return assets

    def _cut_video_assets(self, assets: List[Dict]) -> List[Dict]:
        """Cut video assets into frames."""
        for asset in assets:
            if asset["jsonContent"] == "" and Path(asset["content"]).is_file():
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

    def process_and_save(self, assets: List[Dict], output_filename: Path) -> None:
        """Extract formatted annotations from labels and save the json in the buckets."""
        clean_assets = self.preprocess_assets(assets)

        if self.normalized_coordinates is False:
            clean_assets = [self.convert_to_pixel_coords(asset) for asset in clean_assets]

        return self._save_assets_export(
            clean_assets,
            output_filename,
        )

    @property
    def images_folder(self) -> Path:
        """Export images folder."""
        return self.base_folder / self.ASSETS_DIR_NAME

    def convert_to_pixel_coords(self, asset: Dict) -> Dict:
        """Convert asset JSON response normalized vertices to pixel coordinates."""
        if asset.get("latestLabel", {}):
            self._scale_label_vertices(asset["latestLabel"], asset)

        if asset.get("labels"):
            for label in asset["labels"]:
                self._scale_label_vertices(label, asset)

        return asset

    def _scale_label_vertices(self, label: Dict, asset: Dict) -> None:
        if not label.get("jsonResponse", {}):
            return

        is_label_rotated = (
            label["jsonResponse"]["ROTATION_JOB"]["rotation"] in [90, 270]
            if "ROTATION_JOB" in label["jsonResponse"]
            else False
        )

        if self.project["inputType"] == "PDF":
            self._scale_json_response_vertices(
                label["jsonResponse"],
                asset,
                is_label_rotated,
                _scale_normalized_vertices_pdf_annotation,
            )

        elif self.project["inputType"] == "IMAGE":
            self._scale_json_response_vertices(
                label["jsonResponse"],
                asset,
                is_label_rotated,
                _scale_normalized_vertices_image_video_annotation,
            )

        elif self.project["inputType"] == "VIDEO":
            for frame_resp in label["jsonResponse"].values():
                if frame_resp:
                    self._scale_json_response_vertices(
                        frame_resp,
                        asset,
                        is_label_rotated,
                        _scale_normalized_vertices_image_video_annotation,
                    )

        else:
            raise NotCompatibleInputType(
                f"Labels of input type {self.project['inputType']} cannot be converted to pixel"
                " coordinates."
            )

    def _scale_json_response_vertices(
        self,
        json_resp: Dict,
        asset: Dict,
        is_label_rotated: bool,
        annotation_scaler: Callable[[Dict, Dict, bool], None],
    ) -> None:
        for job_name in json_resp:
            if self._can_scale_vertices_for_job_name(job_name) and json_resp.get(job_name, {}).get(
                "annotations"
            ):
                for ann in json_resp[job_name]["annotations"]:
                    annotation_scaler(ann, asset, is_label_rotated)

    def _can_scale_vertices_for_job_name(self, job_name: str) -> bool:
        return (
            # some old labels might not up to date with the json interface
            job_name in self.project["jsonInterface"]["jobs"]
            and (
                self.project["jsonInterface"]["jobs"][job_name]["mlTask"] == "OBJECT_DETECTION"
                or (
                    self.project["inputType"] == "PDF"
                    and self.project["jsonInterface"]["jobs"][job_name]["mlTask"]
                    == "NAMED_ENTITIES_RECOGNITION"  # PDF NER jobs have vertices
                )
            )
        )


def _scale_vertex(vertex: Dict, width: int, height: int) -> Dict:
    return {"x": vertex["x"] * width, "y": vertex["y"] * height}


def _scale_all_vertices(object_, width: int, height: int):
    if isinstance(object_, List):
        return [_scale_all_vertices(obj, width=width, height=height) for obj in object_]

    if isinstance(object_, Dict):
        if sorted(object_.keys()) == ["x", "y"]:
            return _scale_vertex(object_, width=width, height=height)
        return {
            key: _scale_all_vertices(value, width=width, height=height)
            for key, value in object_.items()
        }

    return object_


def _scale_normalized_vertices_pdf_annotation(
    annotation: Dict, asset: Dict, is_label_rotated: bool = False
) -> None:
    """Scale normalized vertices of a PDF annotation.

    PDF annotations are different from image annotations because the asset width/height can vary.

    PDF only have BBox detection, so we only scale the boundingPoly and polys keys.
    """
    if is_label_rotated:
        raise NotCompatibleOptions("PDF labels cannot be rotated")

    if "annotations" in annotation:
        # pdf annotations have two layers of "annotations"
        # https://docs.kili-technology.com/reference/export-object-entity-detection-and-relation#ner-in-pdfs
        for ann in annotation["annotations"]:
            _scale_normalized_vertices_pdf_annotation(ann, asset)

    # an annotation has three keys:
    # - pageNumberArray: list of page numbers
    # - polys: list of polygons
    # - boundingPoly: list of bounding polygons
    # each polygon is a dict with a key "normalizedVertices" that is a list of vertices
    if "polys" in annotation and "boundingPoly" in annotation:
        try:
            page_number_to_dimensions = {
                page_resolution["pageNumber"]: {
                    "width": page_resolution["width"],
                    "height": page_resolution["height"],
                }
                for page_resolution in asset["pageResolutions"]
            }
        except (KeyError, TypeError) as err:
            raise NotCompatibleOptions(
                "PDF labels export with absolute coordinates require `pageResolutions` in the"
                " asset. Please use `kili.update_properties_in_assets(page_resolutions_array=...)`"
                " to update the page resolutions of your asset.`"
            ) from err

        for key in ("polys", "boundingPoly"):
            annotation[key] = [
                {
                    **value,  # keep the original normalizedVertices
                    "vertices": _scale_all_vertices(
                        value["normalizedVertices"],
                        width=page_number_to_dimensions[page_number]["width"],
                        height=page_number_to_dimensions[page_number]["height"],
                    ),
                }
                for value, page_number in zip(annotation[key], annotation["pageNumberArray"])
            ]


def _scale_normalized_vertices_image_video_annotation(
    annotation: Dict, asset: Dict, is_label_rotated: bool
) -> None:
    """Scale normalized vertices of an image/video object detection annotation."""
    if "resolution" not in asset or asset["resolution"] is None:
        raise NotCompatibleOptions(
            "Image and video labels export with absolute coordinates require `resolution` in the"
            " asset. Please use `kili.update_properties_in_assets(resolution_array=...)` to update"
            " the resolution of your asset.`"
        )

    width = asset["resolution"]["width"] if not is_label_rotated else asset["resolution"]["height"]
    height = asset["resolution"]["height"] if not is_label_rotated else asset["resolution"]["width"]

    # bbox, segmentation, polygons
    if "boundingPoly" in annotation:
        annotation["boundingPoly"] = [
            {
                **norm_vertices_dict,  # keep the original normalizedVertices
                "vertices": _scale_all_vertices(
                    norm_vertices_dict["normalizedVertices"], width=width, height=height
                ),
            }
            for norm_vertices_dict in annotation["boundingPoly"]
        ]

    # point jobs
    if "point" in annotation:
        annotation["pointPixels"] = _scale_all_vertices(
            annotation["point"], width=width, height=height
        )

    # line, vector jobs
    if "polyline" in annotation:
        annotation["polylinePixels"] = _scale_all_vertices(
            annotation["polyline"], width=width, height=height
        )

    # pose estimation jobs
    if "points" in annotation:
        for point_dict in annotation["points"]:
            if "point" in point_dict:
                point_dict["pointPixels"] = _scale_all_vertices(
                    point_dict["point"], width=width, height=height
                )
