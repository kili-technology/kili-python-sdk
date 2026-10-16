"""Parser classes."""

import json
from abc import abstractmethod
from pathlib import Path
from typing import Any, Optional

from kili.services.label_import.types import Classes


class AbstractLabelParser:  # pylint: disable=too-few-public-methods
    """Abstract label parser."""

    def __init__(self, classes_by_id: Optional[Classes], target_job: Optional[str]) -> None:
        self.classes_by_id = classes_by_id
        self.target_job = target_job

    @abstractmethod
    def parse(self, label_file: Path) -> dict[str, Any]:
        """Parses a label file."""


class YoloLabelParser(AbstractLabelParser):  # pylint: disable=too-few-public-methods
    """Yolo label parser."""

    def parse(self, label_file: Path) -> dict[str, Any]:
        """Parses a Yolo label file.

        The annotations carry no type: the target job's tool decides it, so a box line imports
        into a polygon job and a segment line into a semantic job.
        """
        annotations = []
        assert self.classes_by_id
        assert self.target_job
        with open(label_file, encoding="ascii") as l_f:
            for line_number, line in enumerate(l_f, start=1):
                row = line.split()
                if not row:
                    continue
                try:
                    vertices, category, proba = self._parse(row)
                    category_name = self.classes_by_id[category]
                except (KeyError, ValueError) as error:
                    raise ValueError(
                        f"{label_file}, line {line_number}: {line.strip()!r} is not a YOLO line"
                        " of a known class: expected `class x y w h [confidence]` or"
                        f" `class x1 y1 x2 y2 x3 y3 ...` ({error!r})"
                    ) from error
                annotations.append(
                    {
                        "boundingPoly": [
                            {"normalizedVertices": [{"x": v[0], "y": v[1]} for v in vertices]}
                        ],
                        "categories": [
                            {
                                "name": category_name,
                                "confidence": 100 if proba is None else int(100 * float(proba)),
                            }
                        ],
                    }
                )

        return {self.target_job: {"annotations": annotations}}

    @staticmethod
    def _parse(row: list[str]) -> tuple[list[list[float]], int, Optional[float]]:
        # A segment line, `class x1 y1 ... xn yn` with n >= 3: its polygon as given.
        if len(row) >= 7 and len(row) % 2 == 1:
            coordinates = [float(value) for value in row[1:]]
            return (
                [coordinates[i : i + 2] for i in range(0, len(coordinates), 2)],
                int(row[0]),
                None,
            )
        # A box line, `class x y w h [confidence]`.
        if len(row) not in (5, 6):
            raise ValueError(f"{len(row)} values")
        class_id, x, y, width, height = row[:5]
        proba = float(row[5]) if len(row) == 6 else None
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
            int(class_id),
            proba,
        )


class KiliRawLabelParser(AbstractLabelParser):  # pylint: disable=too-few-public-methods
    """Kili raw label parser."""

    def parse(self, label_file: Path) -> dict[str, Any]:
        with label_file.open("r", encoding="utf-8") as l_f:
            return json.load(l_f)
