"""Service for importing objects into kili"""

from typing import Dict, List

from kili.authentication import KiliAuth
from kili.queries.project import QueriesProject
from kili.services.asset_import.image import ImageDataImporter
from kili.services.asset_import.pdf import PdfDataImporter
from kili.services.asset_import.text import TextDataImporter
from kili.services.asset_import.video import VideoDataImporter
from kili.services.project import get_project

from .base import LoggerParams, ProcessingParams, ProjectParams

importer_by_type = {
    "PDF": PdfDataImporter,
    "IMAGE": ImageDataImporter,
    "TEXT": TextDataImporter,
    "VIDEO": VideoDataImporter,
    "VIDEO_LEGACY": VideoDataImporter,
}


def import_assets(
    auth: KiliAuth,
    project_id: str,
    assets: List[Dict],
    raise_error=True,
    disable_tqdm=False,
):
    """
    import the selected assets into the specified project
    """
    kili = QueriesProject(auth)
    input_type = get_project(kili, project_id, ["inputType"])["inputType"]

    project_params = ProjectParams(project_id=project_id, input_type=input_type)
    processing_params = ProcessingParams(raise_error=raise_error)
    logger_params = LoggerParams(disable_tqdm=disable_tqdm)
    importer_params = (auth, project_params, processing_params, logger_params)

    if input_type not in importer_by_type:
        raise NotImplementedError(f"There is no imported for the input type: {input_type}")
    asset_importer = importer_by_type[input_type](*importer_params)
    result = asset_importer.import_assets(assets=assets)  # type:ignore X
    return result
