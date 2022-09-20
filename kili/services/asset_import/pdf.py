"""
Functions to import assets into a PDF project
"""
from typing import List

from .base import BaseAssetImporter, BatchParams, ContentBatchImporter
from .types import AssetLike


class PdfDataImporter(BaseAssetImporter):
    """
    class for importing data into a PDF project
    """

    def import_assets(self, assets: List[AssetLike]):
        """
        Import PDF assets into Kili.
        """
        is_hosted = self.is_hosted_content(assets)
        if not is_hosted:
            assets = self.filter_local_assets(assets, self.raise_error)
        assets = self.filter_duplicate_external_ids(assets)

        batch_params = BatchParams(is_hosted=is_hosted, is_asynchronous=False)
        batch_importer = ContentBatchImporter(
            self.auth, self.project_params, batch_params, self.pbar
        )
        result = self.import_assets_by_batch(assets, batch_importer)
        return result
