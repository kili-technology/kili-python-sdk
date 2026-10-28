"""Types specific to import."""

from typing import Literal, NewType

Classes = NewType("Classes", dict[int, str])
LabelFormat = Literal["yolo", "yolo_v4", "yolo_v5", "yolo_v7", "kili", "raw"]

# The YOLO formats before "yolo", which reads any YOLO dataset: they still work and warn until a
# later release removes them
DEPRECATED_YOLO_FORMATS = ("yolo_v4", "yolo_v5", "yolo_v7")
