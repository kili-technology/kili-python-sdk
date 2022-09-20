"""
Functions to import assets into a VIDEO project
"""
import mimetypes
import os
from enum import Enum
from typing import List

from kili.helpers import is_url
from kili.utils import bucket

from .base import (
    BaseAssetImporter,
    BatchParams,
    ContentBatchImporter,
    JsonContentBatchImporter,
)
from .exceptions import ImportValidationError
from .types import AssetLike


class VideoDataType(Enum):
    LOCAL_FRAMES = "LOCAL_FRAMES"
    HOSTED_FRAMES = "HOSTED_FRAMES"
    LOCAL_FILE = "LOCAL_FILE"
    HOSTED_FILE = "HOSTED_FILE"


class VideoMixin:
    @staticmethod
    def add_video_processing_parameters(asset: AssetLike, from_frames: bool) -> AssetLike:
        """
        Base method for adding video processing parameters
        """
        json_metadata = asset.get("json_metadata", {})
        processing_parameters = json_metadata.get("processingParameters", {})
        video_parameters = [
            ("shouldKeepNativeFrameRate", not from_frames),
            ("framesPlayedPerSecond", 30),
            ("shouldUseNativeVideo", not from_frames),
        ]
        for (key, default_value) in video_parameters:
            processing_parameters[key] = processing_parameters.get(key, default_value)
        json_metadata = {**json_metadata, "processingParameters": processing_parameters}
        return {**asset, "json_metadata": json_metadata}

    @staticmethod
    def map_frame_urls_to_index(asset: AssetLike):
        """
        Map a list of frame url to their index in the video
        """
        json_content = asset.get("json_content")
        assert json_content
        json_content_index = range(len(json_content))
        json_content = dict(zip(json_content_index, json_content))
        return {**asset, "json_content": json_content}


class VideoContentBatchImporter(ContentBatchImporter, VideoMixin):
    def add_video_processing_parameters(self, asset: AssetLike):
        """
        Add video processing parameters for a content upload
        """
        return VideoMixin.add_video_processing_parameters(asset, from_frames=False)

    def import_batch(self, assets: List[AssetLike]):
        """
        Import a batch of video from content
        """
        assets = self.loop_on_batch(self.add_video_processing_parameters)(assets)
        return super().import_batch(assets)


class FrameBatchImporter(JsonContentBatchImporter, VideoMixin):
    def add_video_processing_parameters(self, asset: AssetLike):
        """
        Add video processing parameters for a frames upload
        """
        return VideoMixin.add_video_processing_parameters(asset, from_frames=True)

    def import_batch(self, assets: List[AssetLike]):
        """
        Import a batch of video from frames
        """
        if not self.is_hosted:
            assets = self.loop_on_batch(self.upload_frames_to_bucket)(assets)
        assets = self.loop_on_batch(self.map_frame_urls_to_index)(assets)
        assets = self.loop_on_batch(self.add_video_processing_parameters)(assets)
        return super().import_batch(assets)

    def upload_frames_to_bucket(self, asset: AssetLike):
        """
        Import the local frames to the bucket
        """
        frames = asset.get("json_content")
        assert frames
        signed_urls = bucket.request_signed_urls(self.auth, self.project_id, len(frames))
        uploaded_frames = []
        for i, frame_path in enumerate(frames):
            with open(frame_path, "rb") as file:
                data = file.read()
            content_type, _ = mimetypes.guess_type(frame_path)
            assert content_type
            uploaded_frame_url = bucket.upload_data_via_rest(signed_urls[i], data, content_type)
            cleaned_url = bucket.clean_signed_url(uploaded_frame_url)
            uploaded_frames.append(cleaned_url)
        return {**asset, "json_content": uploaded_frames}


class VideoDataImporter(BaseAssetImporter):
    """
    class for importing data into a VIDEO project
    """

    @staticmethod
    def is_hosted_frames(asset):
        """
        Determine if the frames to import are hosted
        """
        frames = asset.get("json_content", [])
        return all(is_url(frame) for frame in frames)

    @staticmethod
    def has_any_local_frame(asset):
        """
        Determine if at least one frame to import is a local file
        """
        frames = asset.get("json_content", [])
        return any(os.path.exists(frame) for frame in frames)

    def get_data_type(self, assets):
        """
        Determine the type of data to upload from the service payload
        """
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
        else:
            is_hosted_content = self.is_hosted_content(assets)
            if is_hosted_content:
                return VideoDataType.HOSTED_FILE
            else:
                return VideoDataType.LOCAL_FILE

    @staticmethod
    def should_cut_into_frames(assets):
        """
        Determine if assets should be imported asynchronously and cut into frames
        """
        should_use_native_video_array = []
        for asset in assets:
            json_metadata = asset.get("json_metadata", {})
            processing_parameters = json_metadata.get("processingParameters", {})
            should_use_native_video_array.append(
                processing_parameters.get("shouldUseNativeVideo", True)
            )
        if all(should_use_native_video_array):
            return False
        elif all(not b for b in should_use_native_video_array):
            return True
        else:
            raise ImportValidationError(
                """
                Cannot upload videos to split into frames and video to keep as native in the same time.
                Please separate the assets into 2 calls
                """
            )

    def import_assets(self, assets: List[AssetLike]):
        """
        Import video assets into Kili.
        """
        data_type = self.get_data_type(assets)
        if data_type == VideoDataType.LOCAL_FILE:
            assets = self.filter_local_assets(assets, self.raise_error)
            as_frames = self.should_cut_into_frames(assets)
            batch_params = BatchParams(is_hosted=False, is_asynchronous=as_frames)
            batch_importer = VideoContentBatchImporter(
                self.auth, self.project_params, batch_params, self.pbar
            )
        elif data_type == VideoDataType.HOSTED_FILE:
            as_frames = self.should_cut_into_frames(assets)
            batch_params = BatchParams(is_hosted=True, is_asynchronous=as_frames)
            batch_importer = VideoContentBatchImporter(
                self.auth, self.project_params, batch_params, self.pbar
            )
        elif data_type == VideoDataType.LOCAL_FRAMES:
            batch_params = BatchParams(is_hosted=False, is_asynchronous=False)
            batch_importer = FrameBatchImporter(
                self.auth, self.project_params, batch_params, self.pbar
            )
        elif data_type == VideoDataType.HOSTED_FRAMES:
            batch_params = BatchParams(is_hosted=True, is_asynchronous=False)
            batch_importer = FrameBatchImporter(
                self.auth, self.project_params, batch_params, self.pbar
            )
        result = self.import_assets_by_batch(assets, batch_importer)
        return result
