"""Service for importing objects into kili."""

from typing import TYPE_CHECKING, Dict, List, Optional, Type, cast

from kili.domain.project import ProjectId
from kili.services.asset_import.exceptions import (
    ImportValidationError,
)

from .base import (
    BaseAbstractAssetImporter,
    LoggerParams,
    ProcessingParams,
    ProjectParams,
)
from .image import ImageDataImporter
from .llm import LLMDataImporter
from .pdf import PdfDataImporter
from .text import TextDataImporter
from .types import AssetLike
from .video import VideoDataImporter

if TYPE_CHECKING:
    from kili.client import Kili

importer_by_type: Dict[str, Type[BaseAbstractAssetImporter]] = {
    "PDF": PdfDataImporter,
    "IMAGE": ImageDataImporter,
    "TEXT": TextDataImporter,
    "VIDEO": VideoDataImporter,
    "VIDEO_LEGACY": VideoDataImporter,
    "LLM_RLHF": LLMDataImporter,
}


def import_assets(  # pylint: disable=too-many-arguments
    kili: "Kili",
    project_id: ProjectId,
    assets: List[Dict],
    raise_error: bool = True,
    disable_tqdm: Optional[bool] = False,
    verify: bool = True,
):
    """Import the selected assets into the specified project."""
    input_type = kili.kili_api_gateway.get_project(project_id, ("inputType",))["inputType"]

    project_params = ProjectParams(project_id=project_id, input_type=input_type)
    processing_params = ProcessingParams(raise_error=raise_error, verify=verify)
    logger_params = LoggerParams(disable_tqdm=disable_tqdm)
    importer_params = (kili, project_params, processing_params, logger_params)

    if input_type not in importer_by_type:
        raise NotImplementedError(f"There is no importer for the input type: {input_type}")
    if input_type != "IMAGE" and any(asset.get("multi_layer_content") for asset in assets):
        raise ImportValidationError(
            f"Import of multi-layer assets is not supported for input type: {input_type}"
        )
    asset_importer = importer_by_type[input_type](*importer_params)
    casted_assets = cast(List[AssetLike], assets)
    asset_importer.check_asset_contents(casted_assets)
    return asset_importer.import_assets(assets=casted_assets)
