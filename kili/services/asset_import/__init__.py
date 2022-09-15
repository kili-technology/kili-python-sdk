"""Service for importing objects into kili"""

from typing import List

from kili.authentication import KiliAuth
from kili.constants import NO_ACCESS_RIGHT
from kili.queries.project import QueriesProject
from kili.services.asset_import.legacy import LegacyDataImporter
from kili.services.asset_import.pdf_importer import PdfDataImporter
from kili.services.asset_import.types import AssetToImport

from .base import ProcessingParams, ProjectParams


def import_assets(auth: KiliAuth, project_id: str, assets: List[AssetToImport], raise_error=True):
    """
    import the selected assets into the specified project
    """
    kili = QueriesProject(auth)
    projects = kili.projects(project_id, disable_tqdm=True)
    assert len(projects) == 1, NO_ACCESS_RIGHT
    input_type = projects[0]["inputType"]
    project_params = ProjectParams(project_id=project_id, input_type=input_type)
    processing_params = ProcessingParams(raise_error=raise_error)

    if input_type == "PDF":
        data_importer = PdfDataImporter(auth, project_params, processing_params)
    else:
        data_importer = LegacyDataImporter(auth, project_params, processing_params)

    data_importer.import_assets(assets=assets)
