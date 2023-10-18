"""Functions to import assets into a PDF project."""

from typing import List

from .base import BaseAbstractAssetImporter, BatchParams, ContentBatchImporter
from .types import AssetLike


class PdfDataImporter(BaseAbstractAssetImporter):
    """Class for importing data into a PDF project."""

    def import_assets(self, assets: List[AssetLike]):
        """Import PDF assets into Kili."""
        self._check_upload_is_allowed(assets)
        is_hosted = self.is_hosted_content(assets)
        assets = self.filter_duplicate_external_ids(assets)

        batch_params = BatchParams(is_hosted=is_hosted, is_asynchronous=False)
        batch_importer = ContentBatchImporter(
            self.kili, self.project_params, batch_params, self.pbar
        )
        return self.import_assets_by_batch(assets, batch_importer)
