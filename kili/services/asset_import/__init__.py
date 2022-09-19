"""Service for importing objects into kili"""

from typing import List

from kili.authentication import KiliAuth
from kili.constants import NO_ACCESS_RIGHT
from kili.queries.project import QueriesProject
from kili.services.asset_import.image import ImageDataImporter
from kili.services.asset_import.legacy import LegacyDataImporter
from kili.services.asset_import.pdf import PdfDataImporter
from kili.services.asset_import.types import AssetLike

from .base import LoggerParams, ProcessingParams, ProjectParams


def import_assets(
    auth: KiliAuth, project_id: str, assets: List[AssetLike], raise_error=True, disable_tqdm=False
):
    """
    import the selected assets into the specified project
    """
    kili = QueriesProject(auth)
    projects = kili.projects(project_id, disable_tqdm=True)
    assert len(projects) == 1, NO_ACCESS_RIGHT
    input_type = projects[0]["inputType"]
    project_params = ProjectParams(project_id=project_id, input_type=input_type)
    processing_params = ProcessingParams(raise_error=raise_error)
    logger_params = LoggerParams(disable_tqdm=disable_tqdm)

    importer_params = (auth, project_params, processing_params, logger_params)
    if input_type == "PDF":
        data_importer = PdfDataImporter(*importer_params)
    elif input_type == "IMAGE":
        data_importer = ImageDataImporter(*importer_params)
    else:
        data_importer = LegacyDataImporter(*importer_params)

    data_importer.import_assets(assets=assets)
