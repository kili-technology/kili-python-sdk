"""Service for importing objects into kili"""

from typing import List

from kili.authentication import KiliAuth
from kili.constants import NO_ACCESS_RIGHT
from kili.queries.project import QueriesProject
from kili.services.asset_import.legacy import LegacyImporter
from kili.services.asset_import.types import AssetToImport


def import_assets(
    auth: KiliAuth,
    project_id: str,
    assets: List[AssetToImport],
):
    """
    import the selected assets into the specified project
    """
    kili = QueriesProject(auth)
    projects = kili.projects(project_id, disable_tqdm=True)
    assert len(projects) == 1, NO_ACCESS_RIGHT
    input_type = projects[0]["inputType"]

    legacy_importer = LegacyImporter(auth=auth, project_id=project_id, input_type=input_type)
    result = legacy_importer.import_assets(assets=assets)
    return result
