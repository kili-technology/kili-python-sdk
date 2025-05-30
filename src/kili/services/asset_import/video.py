"""Functions to import assets into a VIDEO_LEGACY project."""

import os
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from itertools import repeat
from typing import List, Optional

from kili.core.helpers import get_mime_type, is_url
from kili.domain.project import InputType
from kili.services.asset_import.base import (
    BaseAbstractAssetImporter,
    BaseBatchImporter,
    BatchParams,
    ContentBatchImporter,
    JsonContentBatchImporter,
)
from kili.services.asset_import.constants import (
    FRAME_IMPORT_BATCH_SIZE,
    IMPORT_BATCH_SIZE,
)
from kili.services.asset_import.exceptions import ImportValidationError
from kili.services.asset_import.types import AssetLike
from kili.utils import bucket


class VideoDataType(Enum):
    """Video data type."""

    LOCAL_FRAMES = "LOCAL_FRAMES"
    HOSTED_FRAMES = "HOSTED_FRAMES"
    LOCAL_FILE = "LOCAL_FILE"
    HOSTED_FILE = "HOSTED_FILE"


class VideoMixin:
    """Helping functions for importing Video assets."""

    @staticmethod
    def get_video_processing_parameters(asset: AssetLike):
        """Base method for adding video processing parameters."""
        json_metadata = asset.get("json_metadata", {})
        return json_metadata.get(  # pyright: ignore[reportGeneralTypeIssues]
            "processingParameters", {}
        )

    @staticmethod
    def map_frame_urls_to_index(asset: AssetLike):
        """Map a list of frame url to their index in the video."""
        json_content = asset.get("json_content")
        assert json_content
        json_content_index = range(len(json_content))
        json_content = dict(zip(json_content_index, json_content))
        return AssetLike(
            **{**asset, "json_content": json_content}  # pyright: ignore[reportGeneralTypeIssues]
        )


class VideoContentBatchImporter(ContentBatchImporter, VideoMixin):
    """Class for importing a batch of video assets from content into a VIDEO project."""

    def add_video_processing_parameters(self, asset):
        """Add video processing parameters for a content upload."""
        json_metadata = asset.get("json_metadata", {})
        processing_parameters = self.get_video_processing_parameters(asset)
        json_metadata = {**json_metadata, "processingParameters": processing_parameters}
        return AssetLike(**{**asset, "json_metadata": json_metadata})  # type: ignore

    def import_batch(
        self, assets: List[AssetLike], verify: bool, input_type: Optional[InputType] = None
    ):
        """Import a batch of video assets from content into Kili."""
        assets = self.loop_on_batch(self.add_video_processing_parameters)(assets)
        return super().import_batch(assets, verify)


class FrameBatchImporter(JsonContentBatchImporter, VideoMixin):
    """Class for importing a batch of video assets from frames into a VIDEO project."""

    def add_video_processing_parameters(self, asset):
        """Add video processing parameters for a frames upload."""
        json_metadata = asset.get("json_metadata", {})
        processing_parameters = self.get_video_processing_parameters(asset)
        json_metadata = {**json_metadata, "processingParameters": processing_parameters}
        return AssetLike(**{**asset, "json_metadata": json_metadata})  # type: ignore

    def import_batch(
        self, assets: List[AssetLike], verify: bool, input_type: Optional[InputType] = None
    ):
        """Import a batch of video assets from frames."""
        assets = self.add_ids(assets)
        if not self.is_hosted:
            assets = self.loop_on_batch(self.upload_frames_to_bucket)(assets)
        assets = self.loop_on_batch(self.map_frame_urls_to_index)(assets)
        assets = self.loop_on_batch(self.add_video_processing_parameters)(assets)
        return super().import_batch(assets, verify)

    def upload_frames_to_bucket(self, asset: AssetLike):
        """Import the local frames to the bucket."""
        frames = asset.get("json_content")
        assert frames
        asset_id: str = asset.get("id") or f"unknown-{bucket.generate_unique_id()}"
        project_bucket_path = self.generate_project_bucket_path()
        asset_frames_paths = [
            BaseBatchImporter.build_url_from_parts(
                project_bucket_path, asset_id, "frame", str(frame_id)
            )
            for frame_id in range(len(frames))
        ]
        signed_urls = bucket.request_signed_urls(self.kili, asset_frames_paths)
        data_array = []
        content_type_array = []
        for frame_path in frames:
            with open(frame_path, "rb") as file:
                data_array.append(file.read())
            content_type = get_mime_type(frame_path)
            content_type_array.append(content_type)
        with ThreadPoolExecutor() as threads:
            url_gen = threads.map(
                bucket.upload_data_via_rest,
                signed_urls,
                data_array,
                content_type_array,
                repeat(self.http_client),
            )
        cleaned_urls = (bucket.clean_signed_url(url, self.kili.api_endpoint) for url in url_gen)
        return AssetLike(**{**asset, "json_content": list(cleaned_urls)})  # type: ignore


class VideoDataImporter(BaseAbstractAssetImporter):
    """Class for importing data into a VIDEO project."""

    @staticmethod
    def is_hosted_frames(asset) -> bool:
        """Determine if the frames to import are hosted."""
        frames = asset.get("json_content", [])
        return all(is_url(frame) for frame in frames)

    @staticmethod
    def has_any_local_frame(asset) -> bool:
        """Determine if at least one frame to import is a local file."""
        frames = asset.get("json_content", [])
        return any(os.path.exists(frame) for frame in frames)

    def get_data_type(self, assets):
        """Determine the type of data to upload from the service payload."""
        content_array = [asset.get("content", "") for asset in assets]
        has_json_content = any(asset.get("json_content") for asset in assets)
        if has_json_content:
            if any(content and not is_url(content) for content in content_array):
                raise ImportValidationError(
                    "Cannot import content that is not an url when importing a video from frames"
                )
            if all(self.is_hosted_frames(asset) for asset in assets):
                return VideoDataType.HOSTED_FRAMES
            return VideoDataType.LOCAL_FRAMES
        is_hosted_content = self.is_hosted_content(assets)
        if is_hosted_content:
            return VideoDataType.HOSTED_FILE
        return VideoDataType.LOCAL_FILE

    def import_assets(self, assets: List[AssetLike], input_type: InputType):
        """Import video assets into Kili."""
        self._check_upload_is_allowed(assets)
        data_type = self.get_data_type(assets)
        assets = self.filter_duplicate_external_ids(assets)
        if data_type == VideoDataType.LOCAL_FILE:
            assets = self.filter_local_assets(assets, self.raise_error)
            batch_params = BatchParams(is_hosted=False, is_asynchronous=True)
            batch_importer = VideoContentBatchImporter(
                self.kili, self.project_params, batch_params, self.pbar
            )
            batch_size = IMPORT_BATCH_SIZE
        elif data_type == VideoDataType.HOSTED_FILE:
            batch_params = BatchParams(is_hosted=True, is_asynchronous=True)
            batch_importer = VideoContentBatchImporter(
                self.kili, self.project_params, batch_params, self.pbar
            )
            batch_size = IMPORT_BATCH_SIZE
        elif data_type == VideoDataType.LOCAL_FRAMES:
            batch_params = BatchParams(is_hosted=False, is_asynchronous=False)
            batch_importer = FrameBatchImporter(
                self.kili, self.project_params, batch_params, self.pbar
            )
            batch_size = FRAME_IMPORT_BATCH_SIZE
        elif data_type == VideoDataType.HOSTED_FRAMES:
            batch_params = BatchParams(is_hosted=True, is_asynchronous=False)
            batch_importer = FrameBatchImporter(
                self.kili, self.project_params, batch_params, self.pbar
            )
            batch_size = IMPORT_BATCH_SIZE
        else:
            raise ImportValidationError
        return self.import_assets_by_batch(assets, batch_importer, batch_size)
