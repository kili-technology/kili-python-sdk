"""Functions to import assets into an IMAGE project."""
import mimetypes
import os
from typing import List

from .base import BaseAbstractAssetImporter, BatchParams, ContentBatchImporter
from .constants import LARGE_IMAGE_THRESHOLD_SIZE
from .types import AssetLike


class ImageDataImporter(BaseAbstractAssetImporter):
    """Class for importing assets into an IMAGE project."""

    def import_assets(self, assets: List[AssetLike]):
        """Import IMAGE assets into Kili."""
        self._check_upload_is_allowed(assets)
        is_hosted = self.is_hosted_content(assets)
        if not is_hosted:
            assets = self.filter_local_assets(assets, self.raise_error)
        assets = self.filter_duplicate_external_ids(assets)
        sync_assets, async_assets = self.split_asset_by_upload_type(assets, is_hosted)
        created_asset_ids: List[str] = []
        if len(sync_assets) > 0:
            sync_batch_params = BatchParams(is_hosted=is_hosted, is_asynchronous=False)
            batch_importer = ContentBatchImporter(
                self.kili, self.project_params, sync_batch_params, self.pbar
            )
            created_asset_ids += self.import_assets_by_batch(sync_assets, batch_importer)
        if len(async_assets) > 0:
            async_batch_params = BatchParams(is_hosted=is_hosted, is_asynchronous=True)
            batch_importer = ContentBatchImporter(
                self.kili, self.project_params, async_batch_params, self.pbar
            )
            created_asset_ids += self.import_assets_by_batch(async_assets, batch_importer)
        return created_asset_ids

    @staticmethod
    def split_asset_by_upload_type(assets: List[AssetLike], is_hosted: bool):
        """Split assets into two groups, assets to to imported synchronously or asynchronously."""
        if is_hosted:
            return assets, []
        sync_assets, async_assets = [], []
        for asset in assets:
            path = asset.get("content")
            assert path
            assert isinstance(path, str)
            mime_type, _ = mimetypes.guess_type(path.lower())
            is_large_image = os.path.getsize(path) >= LARGE_IMAGE_THRESHOLD_SIZE
            is_tiff = mime_type == "image/tiff"
            if is_large_image or is_tiff:
                async_assets.append(asset)
            else:
                sync_assets.append(asset)
        return sync_assets, async_assets
