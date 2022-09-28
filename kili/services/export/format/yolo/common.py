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
