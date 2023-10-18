"""Types for the Coco export."""

from typing import Dict, List

from typing_extensions import TypedDict


class CocoImage(TypedDict):
    """Handle the coco image data."""

    id: int
    license: int
    file_name: str
    height: int
    width: int
    date_captured: None


class CocoCategory(TypedDict):
    """Handle the coco category data."""

    id: int
    name: str
    supercategory: str


class CocoAnnotation(TypedDict):
    """Handle the coco annotation data."""

    id: int
    image_id: int
    category_id: int
    bbox: List[int]
    segmentation: List[List[float]]  # [[x, y, x, y, x ...]]
    area: int
    iscrowd: int


class CocoFormat(TypedDict):
    """Handle the coco format data."""

    info: Dict  # type: ignore
    licenses: List[Dict]  # type: ignore
    categories: List[CocoCategory]
    images: List[CocoImage]
    annotations: List[CocoAnnotation]
