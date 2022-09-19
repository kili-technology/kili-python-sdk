"""
Functions to import files into an PDF project
"""
from typing import List

from .base import BaseAssetImporter, BaseBatchImporter, BatchParams
from .types import AssetLike


class PdfDataImporter(BaseAssetImporter):
    """
    class for importing data into a PDF project
    """

    def import_assets(self, assets: List[AssetLike]):
        """
        Import PDF assets into Kili.
        """
        is_hosted = self.is_hosted_data(assets)
        batch_params = BatchParams(is_hosted=is_hosted, is_asynchronous=False)
        batch_importer = BaseBatchImporter(self.auth, self.project_params, batch_params, self.pbar)
        if not is_hosted:
            self.filter_local_assets(assets, self.raise_error)
        result = self.import_assets_by_batch(assets, batch_importer)
        return result
