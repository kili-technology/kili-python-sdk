"""Types specific to import."""

from typing import Dict, Literal, NewType

Classes = NewType("Classes", Dict[int, str])
LabelFormat = Literal["yolo_v4", "yolo_v5", "yolo_v7", "kili", "raw"]
