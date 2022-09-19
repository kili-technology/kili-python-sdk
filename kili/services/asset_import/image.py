import mimetypes
import os
from typing import List

from .base import BaseAssetImporter, BaseBatchImporter, BatchParams
from .constants import LARGE_IMAGE_THRESHOLD_SIZE
from .types import AssetLike


class ImageDataImporter(BaseAssetImporter):
    """
    class for importing data into an IMAGE project
    """

    def import_assets(self, assets: List[AssetLike]):
        is_hosted = self.is_hosted_data(assets)
        if not is_hosted:
            self.filter_local_assets(assets, self.raise_error)
        sync_assets, async_assets = self.split_asset_by_upload_type(assets, is_hosted)
        if len(sync_assets) > 0:
            sync_batch_params = BatchParams(is_hosted=is_hosted, is_asynchronous=False)
            batch_importer = BaseBatchImporter(
                self.auth, self.project_params, sync_batch_params, self.pbar
            )
            result = result = self.import_assets_by_batch(sync_assets, batch_importer)
        if len(async_assets) > 0:
            async_batch_params = BatchParams(is_hosted=is_hosted, is_asynchronous=True)
            batch_importer = BaseBatchImporter(
                self.auth, self.project_params, async_batch_params, self.pbar
            )
            result = self.import_assets_by_batch(async_assets, batch_importer)
        return result

    def split_asset_by_upload_type(self, assets: List[AssetLike], is_hosted: bool):
        """
        Split assets into two groups, assets to to imported synchronously or asynchronously
        """
        if is_hosted:
            return assets, []
        sync_assets, async_assets = [], []
        for asset in assets:
            path = asset.get("content")
            assert path
            mime_type, _ = mimetypes.guess_type(path.lower())
            is_large_image = os.path.getsize(path) >= LARGE_IMAGE_THRESHOLD_SIZE
            is_tiff = mime_type == "image/tiff"
            if is_large_image or is_tiff:
                async_assets.append(asset)
            else:
                sync_assets.append(asset)
        return sync_assets, async_assets
