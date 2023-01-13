"""
Parser classes
"""
import csv
import json
from abc import abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from kili.services.label_import.types import Classes


class AbstractLabelParser:  # pylint: disable=too-few-public-methods
    """
    Abstract label parser
    """

    def __init__(self, classes_by_id: Optional[Classes], target_job: Optional[str]) -> None:
        self.classes_by_id = classes_by_id
        self.target_job = target_job

    @abstractmethod
    def parse(self, label_file: Path) -> Dict[str, Any]:
        """
        Parses a label file
        """


class YoloLabelParser(AbstractLabelParser):  # pylint: disable=too-few-public-methods
    """
    Yolo label parser
    """

    def parse(self, label_file: Path) -> Dict[str, Any]:
        """
        Parses a Yolo label file
        """
        annotations = []
        assert self.classes_by_id
        assert self.target_job
        with open(label_file, "r", encoding="ascii") as l_f:
            csv_reader = csv.reader(l_f, delimiter=" ")
            for row in csv_reader:
                if len(row) == 0:
                    continue
                vertices, category, proba = self._parse(row)
                annotations.append(
                    {
                        "boundingPoly": [
                            {"normalizedVertices": [{"x": v[0], "y": v[1]} for v in vertices]}
                        ],
                        "categories": [
                            {
                                "name": self.classes_by_id[category],
                                "confidence": 100 if proba is None else int(100 * float(proba)),
                            }
                        ],
                    }
                )

        kili_json_response = {self.target_job: {"annotations": annotations}}

        return kili_json_response

    @staticmethod
    def _parse(row) -> Tuple[List[List[float]], int, Optional[float]]:
        try:
            class_id, x, y, width, height, proba = row  # pylint: disable=invalid-name
        except ValueError:
            class_id, x, y, width, height = row  # pylint: disable=invalid-name
            proba = None
        _class_id = int(class_id)
        half_width = float(width) / 2
        half_height = float(height) / 2
        _x = float(x)
        _y = float(y)
        return (
            [
                [_x - half_width, _y - half_height],
                [_x - half_width, _y + half_height],
                [_x + half_width, _y + half_height],
                [_x + half_width, _y - half_height],
            ],
            _class_id,
            proba,
        )


class KiliRawLabelParser(AbstractLabelParser):  # pylint: disable=too-few-public-methods
    """
    Kili raw label parser
    """

    def parse(self, label_file: Path) -> Dict[str, Any]:
        with label_file.open("r", encoding="utf-8") as l_f:
            return json.load(l_f)
