"""Functions to import assets into an AUDIO project."""

import os
from enum import Enum

from kili.core.helpers import is_url
from kili.domain.project import InputType

from .base import (
    BaseAbstractAssetImporter,
    BatchParams,
    ContentBatchImporter,
)
from .exceptions import ImportValidationError
from .types import AssetLike


class AudioDataType(Enum):
    """Audio data type."""

    LOCAL_FILE = "LOCAL_FILE"
    HOSTED_FILE = "HOSTED_FILE"


class AudioDataImporter(BaseAbstractAssetImporter):
    """Class for importing data into an AUDIO project."""

    @staticmethod
    def get_data_type(assets: list[AssetLike]) -> AudioDataType:
        """Determine the type of data to upload from the service payload."""
        content_array = [asset.get("content", "") for asset in assets]
        has_local_file = any(os.path.exists(content) for content in content_array)  # type: ignore
        has_hosted_file = any(is_url(content) for content in content_array)
        if has_local_file and has_hosted_file:
            raise ImportValidationError(
                """
                Cannot upload hosted data and local files at the same time.
                Please separate the assets into 2 calls
                """
            )
        if has_local_file:
            return AudioDataType.LOCAL_FILE
        return AudioDataType.HOSTED_FILE

    def import_assets(self, assets: list[AssetLike], input_type: InputType):
        """Import AUDIO assets into Kili."""
        self._check_upload_is_allowed(assets)
        data_type = self.get_data_type(assets)
        assets = self.filter_duplicate_external_ids(assets)
        if data_type == AudioDataType.LOCAL_FILE:
            assets = self.filter_local_assets(assets, self.raise_error)
            batch_params = BatchParams(is_hosted=False, is_asynchronous=False)
            batch_importer = ContentBatchImporter(
                self.kili, self.project_params, batch_params, self.pbar
            )
        elif data_type == AudioDataType.HOSTED_FILE:
            batch_params = BatchParams(is_hosted=True, is_asynchronous=False)
            batch_importer = ContentBatchImporter(
                self.kili, self.project_params, batch_params, self.pbar
            )
        else:
            raise ImportValidationError
        return self.import_assets_by_batch(assets, batch_importer)
