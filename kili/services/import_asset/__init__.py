"""Service for importing objects into kili"""

from typing import List

from kili.authentication import KiliAuth
from kili.services.import_asset.legacy import LegacyImporter
from kili.services.import_asset.typing import AssetToImport
from kili.utils.typing import InputType


def import_assets(
    auth: KiliAuth,
    input_type: InputType,
    project_id: str,
    assets: List[AssetToImport],
):
    """
    import the selected assets into the specified project
    """
    legacy_importer = LegacyImporter(
        auth=auth, project_id=project_id, input_type=input_type, assets=assets
    )
    legacy_importer.import_assets()
