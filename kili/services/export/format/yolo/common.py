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
        assets: Dict,
        output_file: ,
    ):  # pylint: disable=too-many-arguments
        """
        Write all the labels into a single folder.
        """
        with open(output_file, "w") as f:
            f.write(json.dumps(assets, sort_keys=True, indent=4))


