"""
Common code for the PASCAL VOC exporter.
"""

import warnings
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple, Union
from xml.dom import minidom

from PIL import Image

from kili.services.export.exceptions import NotCompatibleOptions
from kili.services.export.format.base import AbstractExporter
from kili.services.export.repository import AbstractContentRepository
from kili.utils.tqdm import tqdm


class VocExporter(AbstractExporter):
    """
    Common code for VOC exporter.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.with_assets:
            warnings.warn(
                "For an export to the Pascal VOC format, the download of assets cannot be disabled."
            )
        self.with_assets = True

    def _check_arguments_compatibility(self):
        if self.single_file:
            raise NotCompatibleOptions(
                f"The label format {self.label_format} can not be exported into a single file."
            )
        if self.split_option != "merged":
            raise NotCompatibleOptions(
                "The current implementation only supports merged annotations."
            )

    def process_and_save(self, assets: List[Dict], output_filename: Path) -> None:
        """
        Save the assets and annotations to a zip file in the Pascal VOC format.
        """
        # pylint: disable=too-many-locals, too-many-arguments
        self.logger.info("Exporting VOC format")

        labels_folder = self.base_folder / "labels"
        labels_folder.mkdir(parents=True)

        for asset in tqdm(assets, disable=self.disable_tqdm):
            _process_asset_for_job(self.content_repository, asset, labels_folder)

        self.create_readme_kili_file(self.export_root_folder)
        self.make_archive(self.export_root_folder, output_filename)

        self.logger.warning(output_filename)


def _process_asset_for_job(
    content_repository: AbstractContentRepository,
    asset: Dict,
    labels_folder: Path,
) -> None:
    # pylint: disable=too-many-locals, too-many-branches
    """
    Process an asset
    """
    frames = {}
    is_frame = False

    idx = 0
    if "jsonResponse" in asset["latestLabel"]:
        number_of_frames = len(asset["latestLabel"]["jsonResponse"])
        for idx in range(number_of_frames):
            if str(idx) in asset["latestLabel"]["jsonResponse"]:
                is_frame = True
                frame_asset = asset["latestLabel"]["jsonResponse"][str(idx)]
                frames[idx] = {"latestLabel": {"jsonResponse": frame_asset}}

    if is_frame:
        raise NotImplementedError("Export of annotations on videos is not supported yet.")

    if not frames:
        frames[-1] = asset

    content_frames = content_repository.get_content_frames_paths(asset)
    content_frame = content_frames[idx] if content_frames else asset["content"]

    filename = asset["externalId"]
    width, height = get_asset_dimensions(content_frame)
    for frame in frames.values():
        latest_label = frame["latestLabel"]
        json_response = latest_label["jsonResponse"]
        parameters = {"filename": f"{filename}.xml"}
        annotations = _convert_from_kili_to_voc_format(json_response, width, height, parameters)

        with open(labels_folder / f"{filename}.xml", "wb") as fout:
            fout.write(f"{annotations}\n".encode())


def get_asset_dimensions(file_path: Union[Path, str]) -> Tuple:
    """
    Get an asset width and height
    """
    image = Image.open(file_path)
    width, height = image.size
    return width, height


def _parse_annotations(
    response: Dict, xml_label: ET.Element, img_width: int, img_height: int
) -> None:
    # pylint: disable=too-many-locals
    for _, job_response in response.items():
        if "annotations" in job_response:
            annotations = job_response["annotations"]
            for annotation in annotations:
                vertices = annotation["boundingPoly"][0]["normalizedVertices"]
                categories = annotation["categories"]
                for category in categories:
                    annotation_category = ET.SubElement(xml_label, "object")
                    name = ET.SubElement(annotation_category, "name")
                    name.text = category["name"]
                    pose = ET.SubElement(annotation_category, "pose")
                    pose.text = "Unspecified"
                    truncated = ET.SubElement(annotation_category, "truncated")
                    truncated.text = "0"
                    difficult = ET.SubElement(annotation_category, "difficult")
                    difficult.text = "0"
                    occluded = ET.SubElement(annotation_category, "occluded")
                    occluded.text = "0"
                    bndbox = ET.SubElement(annotation_category, "bndbox")
                    x_vertices = [int(round(v["x"] * img_width)) for v in vertices]
                    y_vertices = [int(round(v["y"] * img_height)) for v in vertices]
                    xmin = ET.SubElement(bndbox, "xmin")
                    xmin.text = str(min(x_vertices))
                    xmax = ET.SubElement(bndbox, "xmax")
                    xmax.text = str(max(x_vertices))
                    ymin = ET.SubElement(bndbox, "ymin")
                    ymin.text = str(min(y_vertices))
                    ymax = ET.SubElement(bndbox, "ymax")
                    ymax.text = str(max(y_vertices))


def _provide_voc_headers(
    xml_label: ET.Element, img_width: int, img_height: int, parameters: Dict
) -> None:
    folder = ET.SubElement(xml_label, "folder")
    folder.text = parameters.get("folder", "")

    filename = ET.SubElement(xml_label, "filename")
    filename.text = parameters.get("filename", "")

    path = ET.SubElement(xml_label, "path")
    path.text = parameters.get("path", "")

    source = ET.SubElement(xml_label, "source")
    database = ET.SubElement(source, "database")
    database.text = "Kili Technology"

    size = ET.SubElement(xml_label, "size")
    width_xml = ET.SubElement(size, "width")
    width_xml.text = str(img_width)
    height_xml = ET.SubElement(size, "height")
    height_xml.text = str(img_height)
    depth = ET.SubElement(size, "depth")
    depth.text = parameters.get("depth", "3")

    segmented = ET.SubElement(xml_label, "segmented")
    segmented.text = None


def _convert_from_kili_to_voc_format(
    response: Dict, img_width: int, img_height: int, parameters: Dict
) -> str:
    xml_label = ET.Element("annotation")

    _provide_voc_headers(xml_label, img_width, img_height, parameters=parameters)

    _parse_annotations(response, xml_label, img_width, img_height)

    xmlstr = minidom.parseString(ET.tostring(xml_label)).toprettyxml(indent="   ")

    return xmlstr
