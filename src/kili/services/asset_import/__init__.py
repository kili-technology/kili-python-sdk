"""Service for importing objects into kili."""

from typing import Dict, List, Type, cast

from kili.services.project import get_project_field

from .base import (
    BaseAbstractAssetImporter,
    LoggerParams,
    ProcessingParams,
    ProjectParams,
)
from .image import ImageDataImporter
from .pdf import PdfDataImporter
from .text import TextDataImporter
from .types import AssetLike
from .video import VideoDataImporter

importer_by_type: Dict[str, Type[BaseAbstractAssetImporter]] = {
    "PDF": PdfDataImporter,
    "IMAGE": ImageDataImporter,
    "TEXT": TextDataImporter,
    "VIDEO": VideoDataImporter,
    "VIDEO_LEGACY": VideoDataImporter,
}


def import_assets(  # pylint: disable=too-many-arguments
    kili,
    project_id: str,
    assets: List[Dict],
    raise_error=True,
    disable_tqdm=False,
    verify=True,
):
    """Import the selected assets into the specified project."""
    input_type = get_project_field(kili, project_id, "inputType")

    project_params = ProjectParams(project_id=project_id, input_type=input_type)
    processing_params = ProcessingParams(raise_error=raise_error, verify=verify)
    logger_params = LoggerParams(disable_tqdm=disable_tqdm)
    importer_params = (kili, project_params, processing_params, logger_params)

    if input_type not in importer_by_type:
        raise NotImplementedError(f"There is no imported for the input type: {input_type}")
    asset_importer = importer_by_type[input_type](*importer_params)
    created_asset_ids = asset_importer.import_assets(assets=cast(List[AssetLike], assets))
    return created_asset_ids
