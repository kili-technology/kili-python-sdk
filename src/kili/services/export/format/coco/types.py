"""Types for the Coco export."""


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
    bbox: list[int]
    segmentation: list[list[float]]  # [[x, y, x, y, x ...]]
    area: int
    iscrowd: int


class CocoFormat(TypedDict):
    """Handle the coco format data."""

    info: dict  # type: ignore
    licenses: list[dict]  # type: ignore
    categories: list[CocoCategory]
    images: list[CocoImage]
    annotations: list[CocoAnnotation]
