"""
Common code for the PASCAL VOC exporter.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, List, Tuple
from xml.dom import minidom

from PIL import Image

from kili.services.export.exceptions import NotCompatibleOptions
from kili.services.export.format.base import AbstractExporter
from kili.services.export.repository import AbstractContentRepository
from kili.utils.tempfile import TemporaryDirectory
from kili.utils.tqdm import tqdm


class VocExporter(AbstractExporter):
    """
    Common code for VOC exporter.
    """

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
        Converts the asset and save them into an archive file.
        """
        return self._process_and_save_pascal_voc_export(assets, output_filename)

    def _process_and_save_pascal_voc_export(
        self, assets: List[Dict], output_filename: Path
    ) -> None:
        # pylint: disable=too-many-locals, too-many-arguments
        """
        Save the assets and annotations to a zip file in the Pascal VOC format.
        """
        self.logger.info("Exporting VOC format")

        with TemporaryDirectory() as folder:
            base_folder = folder / self.project_id
            images_folder = base_folder / "images"
            labels_folder = base_folder / "labels"
            images_folder.mkdir(parents=True)
            labels_folder.mkdir(parents=True)

            remote_content = []
            video_metadata = {}

            for asset in tqdm(assets, disable=self.disable_tqdm):
                asset_remote_content, video_filenames = _process_asset_for_job(
                    self.content_repository, asset, images_folder, labels_folder
                )
                if video_filenames:
                    video_metadata[asset["externalId"]] = video_filenames
                remote_content.extend(asset_remote_content)

            if video_metadata:
                self.write_video_metadata_file(video_metadata, base_folder)

            if len(remote_content) > 0:
                self.write_remote_content_file(remote_content, images_folder)

            self.create_readme_kili_file(folder)
            self.make_archive(folder, output_filename)

        self.logger.warning(output_filename)


def _process_asset_for_job(
    content_repository: AbstractContentRepository,
    asset: Dict,
    images_folder: Path,
    labels_folder: Path,
) -> Tuple[List, List]:
    # pylint: disable=too-many-locals, too-many-branches
    """
    Process an asset
    """
    frames = {}
    is_frame = False
    asset_remote_content = []

    idx = leading_zeros = 0
    if "jsonResponse" in asset["latestLabel"]:
        number_of_frames = len(asset["latestLabel"]["jsonResponse"])
        leading_zeros = len(str(number_of_frames))
        for idx in range(number_of_frames):
            if str(idx) in asset["latestLabel"]["jsonResponse"]:
                is_frame = True
                frame_asset = asset["latestLabel"]["jsonResponse"][str(idx)]
                frames[idx] = {"latestLabel": {"jsonResponse": frame_asset}}

    if not frames:
        frames[-1] = asset

    content_frames = content_repository.get_content_frames_paths(asset)
    video_filenames = []
    content_frame = content_frames[idx] if content_frames else asset["content"]

    width, height = get_asset_dimensions(content_repository, content_frame, is_frame)
    for idx, frame in frames.items():
        if is_frame:
            filename = f"{asset['externalId']}_{str(idx + 1).zfill(leading_zeros)}"
            video_filenames.append(filename)
        else:
            filename = asset["externalId"]
        latest_label = frame["latestLabel"]
        json_response = latest_label["jsonResponse"]

        parameters = {"filename": f"{filename}.xml"}
        annotations = _convert_from_kili_to_voc_format(json_response, width, height, parameters)

        if not annotations:
            continue

        with open(labels_folder / f"{filename}.xml", "wb") as fout:
            fout.write(f"{annotations}\n".encode())

        asset_remote_content.append([asset["externalId"], content_frame, f"{filename}.xml"])

        is_served_by_kili = content_repository.is_serving(content_frame)
        if is_served_by_kili or asset.get("isProcessingAuthorized", False):
            if content_frames or not is_frame:
                response = content_repository.get_content_stream(
                    content_url=content_frame, block_size=1024
                )
                with open(images_folder / f"{filename}.jpg", "wb") as fout:
                    for block in response:
                        if not block:
                            break
                        fout.write(block)

    if not content_frames and is_frame and content_repository.is_serving(asset["content"]):
        raise NotImplementedError("Export of annotations on videos is not supported yet.")

    return asset_remote_content, video_filenames


def get_asset_dimensions(
    content_repository: AbstractContentRepository, url: str, is_frame: bool
) -> Tuple:
    """
    Download an asset and get width and height
    """
    content = url

    response = content_repository.get_content_stream(content_url=content, block_size=1024)
    with NamedTemporaryFile() as downloaded_file:
        with open(downloaded_file.name, "wb") as fout:
            for block in response:
                if not block:
                    break
                fout.write(block)
        if is_frame is True:
            raise NotImplementedError("Export of annotations on videos is not supported yet.")
            # probe = ffmpeg.probe(downloaded_file.name)
            # video_info = next(s for s in probe["streams"] if s["codec_type"] == "video")
            # width = video_info["width"]
            # height = video_info["height"]
        image = Image.open(downloaded_file.name)
        width, height = image.size

    return width, height


def _parse_annotations(
    response: dict, xml_label: ET.Element, img_width: int, img_height: int
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
    xml_label: ET.Element, img_width: int, img_height: int, parameters: dict
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
    response: dict, img_width: int, img_height: int, parameters: dict
) -> str:
    xml_label = ET.Element("annotation")

    _provide_voc_headers(xml_label, img_width, img_height, parameters=parameters)

    _parse_annotations(response, xml_label, img_width, img_height)

    xmlstr = minidom.parseString(ET.tostring(xml_label)).toprettyxml(indent="   ")

    return xmlstr
