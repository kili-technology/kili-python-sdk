"""
Common and generic functions to import files into a project
"""
import mimetypes
import os
from concurrent.futures import ThreadPoolExecutor
from json import dumps
from pathlib import Path
from typing import Callable, List, NamedTuple, Optional, Tuple, Union

from kili.authentication import KiliAuth
from kili.graphql.operations.asset.mutations import (
    GQL_APPEND_MANY_FRAMES_TO_DATASET,
    GQL_APPEND_MANY_TO_DATASET,
)
from kili.helpers import T, format_result, is_url
from kili.orm import Asset
from kili.queries.asset import QueriesAsset
from kili.services.asset_import.constants import (
    ASSET_FIELDS_DEFAULT_VALUE,
    IMPORT_BATCH_SIZE,
    project_compatible_mimetypes,
)
from kili.services.asset_import.exceptions import ImportValidationError, MimeTypeError
from kili.services.asset_import.types import AssetLike, KiliResolverAsset
from kili.utils import bucket, pagination
from kili.utils.tqdm import tqdm


class BatchParams(NamedTuple):
    """
    Contains all parameters related to the batch to import
    """

    is_asynchronous: bool
    is_hosted: bool


class ProcessingParams(NamedTuple):
    """
    Contains all parameters related to the assets processing
    """

    raise_error: bool


class ProjectParams(NamedTuple):
    """
    Contains all parameters related to the batch to import
    """

    project_id: str
    input_type: str


class LoggerParams(NamedTuple):
    """
    Contains all parameters related to logging
    """

    disable_tqdm: bool


class BaseBatchImporter:  # pylint: disable=too-few-public-methods
    """
    Base class for BatchImporters
    """

    def __init__(
        self, auth: KiliAuth, project_params: ProjectParams, batch_params: BatchParams, pbar: tqdm
    ):
        self.auth = auth
        self.project_id = project_params.project_id
        self.input_type = project_params.input_type
        self.is_hosted = batch_params.is_hosted
        self.is_asynchronous = batch_params.is_asynchronous
        self.pbar = pbar

    @pagination.api_throttle
    def import_batch(self, assets: List[AssetLike]):
        """
        Base actions to import a batch of asset
        """
        assets = self.loop_on_batch(self.stringify_metadata)(assets)
        assets = self.loop_on_batch(self.stringify_json_content)(assets)
        assets_ = self.loop_on_batch(self.fill_empty_fields)(assets)
        result_batch = self.import_to_kili(assets_)
        self.pbar.update(n=len(assets))
        return result_batch

    def add_ids(self, assets: List[AssetLike]):
        """
        Adds ids to all assets
        """
        return self.loop_on_batch(self.add_id_to_asset)(assets)

    def generate_project_bucket_path(self) -> str:
        """
        Returns ids
        """
        return f"projects/{self.project_id}/assets"

    @staticmethod
    def stringify_metadata(asset: AssetLike) -> AssetLike:
        """
        Stringify the metadata
        """
        json_metadata = asset.get("json_metadata", {})
        if not isinstance(json_metadata, str):
            json_metadata = dumps(json_metadata)
        return {**asset, "json_metadata": json_metadata}

    @staticmethod
    def stringify_json_content(asset: AssetLike) -> AssetLike:
        """
        Stringify the metadata
        """
        json_content = asset.get("json_content", "")
        if not isinstance(json_content, str):
            json_content = dumps(json_content)
        return {**asset, "json_content": json_content}

    @staticmethod
    def add_id_to_asset(asset: AssetLike) -> AssetLike:
        """
        Generates an asset id
        """

        return {**asset, "id": asset.get("id", bucket.generate_unique_id())}

    @staticmethod
    def fill_empty_fields(asset: AssetLike):
        """
        fill empty fields with their default value
        """
        field_names = ASSET_FIELDS_DEFAULT_VALUE.keys()
        return KiliResolverAsset(
            **{field: asset.get(field, ASSET_FIELDS_DEFAULT_VALUE[field]) for field in field_names}
        )

    @staticmethod
    def loop_on_batch(func: Callable[[AssetLike], T]) -> Callable[[List[AssetLike]], List[T]]:
        """
        Apply a function, that takes a single asset as input, on the whole batch
        """

        def loop_func(assets: List[AssetLike]):
            return [func(asset) for asset in assets]

        return loop_func

    def _async_import_to_kili(self, assets: List[KiliResolverAsset]):
        """
        Import assets with asynchronous resolver.
        """
        upload_type = "GEO_SATELLITE" if self.input_type == "IMAGE" else "VIDEO"
        payload = {
            "data": {
                "contentArray": [asset["content"] for asset in assets],
                "externalIDArray": [asset["external_id"] for asset in assets],
                "idArray": [asset["id"] for asset in assets],
                "jsonMetadataArray": [asset["json_metadata"] for asset in assets],
                "uploadType": upload_type,
            },
            "where": {"id": self.project_id},
        }
        results = self.auth.client.execute(GQL_APPEND_MANY_FRAMES_TO_DATASET, payload)
        return format_result("data", results, Asset)

    def _sync_import_to_kili(self, assets: List[KiliResolverAsset]):
        """
        Import assets with synchronous resolver
        """
        payload = {
            "data": {
                "contentArray": [asset["content"] for asset in assets],
                "externalIDArray": [asset["external_id"] for asset in assets],
                "idArray": [asset["id"] for asset in assets],
                "isHoneypotArray": [asset["is_honeypot"] for asset in assets],
                "statusArray": [asset["status"] for asset in assets],
                "jsonContentArray": [asset["json_content"] for asset in assets],
                "jsonMetadataArray": [asset["json_metadata"] for asset in assets],
            },
            "where": {"id": self.project_id},
        }
        results = self.auth.client.execute(GQL_APPEND_MANY_TO_DATASET, payload)
        return format_result("data", results, Asset)

    def import_to_kili(self, assets: List[KiliResolverAsset]):
        """
        Import assets to Kili with the right resolver
        """
        if self.is_asynchronous:
            return self._async_import_to_kili(assets)
        return self._sync_import_to_kili(assets)


class ContentBatchImporter(BaseBatchImporter):
    """
    Class defining the methods to import of a batch of assets with content
    """

    @pagination.api_throttle
    def import_batch(self, assets: List[AssetLike]):
        """
        Method to import a batch of asset with content
        """
        assets = self.add_ids(assets)
        if not self.is_hosted:
            assets = self.upload_local_content_to_bucket(assets)
        return super().import_batch(assets)

    def get_content_type_and_data_from_content(
        self, content: Optional[Union[str, bytes]]
    ) -> Tuple[bytes, Optional[str]]:
        """
        Returns the data of the content (path) and its content type
        """
        assert content
        assert isinstance(content, str)
        with Path(content).open("rb") as file:
            data = file.read()
            content_type, _ = mimetypes.guess_type(content)
            return data, content_type

    def get_type_and_data_from_content_array(
        self, content_array: List[Optional[Union[str, bytes]]]
    ) -> List[Tuple[Union[bytes, str], Optional[str]]]:
        """
        Returns the data of the content (path) and its content type for each element in the array
        """
        return list(map(self.get_content_type_and_data_from_content, content_array))

    def upload_local_content_to_bucket(self, assets: List[AssetLike]):
        """
        Upload local content to a bucket
        """
        project_bucket_path = self.generate_project_bucket_path()
        asset_content_paths = [
            Path(project_bucket_path) / asset.get("id", bucket.generate_unique_id()) / "content"
            for asset in assets
        ]
        signed_urls = bucket.request_signed_urls(self.auth, asset_content_paths)
        data_and_content_type_array = self.get_type_and_data_from_content_array(
            list(map(lambda asset: asset.get("content"), assets))
        )
        data_array, content_type_array = zip(*data_and_content_type_array)
        with ThreadPoolExecutor() as threads:
            url_gen = threads.map(
                bucket.upload_data_via_rest, signed_urls, data_array, content_type_array
            )
        return [AssetLike(**{**asset, "content": url}) for asset, url in zip(assets, url_gen)]


class JsonContentBatchImporter(BaseBatchImporter):
    """
    Class defining the import methods for a batch of assets twith json_content
    """

    @staticmethod
    def stringify_json_content(asset: AssetLike):
        """
        Stringify the json content if not a str.
        """
        json_content = asset.get("json_content", {})
        if not isinstance(json_content, str):
            json_content = dumps(json_content)
        return AssetLike(**{**asset, "json_content": json_content})

    def upload_json_content_to_bucket(self, assets: List[AssetLike]):
        """
        Upload the json_contents to a bucket with signed urls
        """
        project_bucket_path = self.generate_project_bucket_path()
        asset_json_content_paths = [
            Path(project_bucket_path) / asset.get("id", bucket.generate_unique_id()) / "jsonContent"
            for asset in assets
        ]
        signed_urls = bucket.request_signed_urls(self.auth, asset_json_content_paths)
        json_content_array = [asset.get("json_content") for asset in assets]
        with ThreadPoolExecutor() as threads:
            url_gen = threads.map(
                bucket.upload_data_via_rest,
                signed_urls,
                json_content_array,
                ["text/plain"] * len(assets),
            )
        return [AssetLike(**{**asset, "json_content": url}) for asset, url in zip(assets, url_gen)]

    @pagination.api_throttle
    def import_batch(self, assets: List[AssetLike]):
        """
        Method to import a batch of asset with json content
        """
        assets = self.add_ids(assets)
        assets = self.loop_on_batch(self.stringify_json_content)(assets)
        assets = self.upload_json_content_to_bucket(assets)
        return super().import_batch(assets)


class BaseAssetImporter:
    """
    Base class for DataImporters classes
    """

    def __init__(
        self,
        auth: KiliAuth,
        project_params: ProjectParams,
        processing_params: ProcessingParams,
        logger_params: LoggerParams,
    ):
        self.auth = auth
        self.project_params = project_params
        self.raise_error = processing_params.raise_error
        self.pbar = tqdm(disable=logger_params.disable_tqdm)

    @staticmethod
    def is_hosted_content(assets: List[AssetLike]):
        """
        Determine if the assets to upload are from local files or hosted data
        Raise an error if a mix of both
        """
        contents = [asset.get("content") for asset in assets]
        if all(is_url(content) for content in contents):
            return True
        if any(is_url(content) for content in contents):
            raise ImportValidationError(
                """
                Cannot upload hosted data and local files at the same time.
                Please separate the assets into 2 calls
                """
            )
        return False

    def filter_local_assets(self, assets: List[AssetLike], raise_error: bool):
        """
        Filter out local files that cannot be imported.
        Return an error at the first file that cannot be imported if raise_error is True
        """
        filtered_assets = []
        for asset in assets:
            path = asset.get("content")
            assert path
            assert isinstance(path, str)
            try:
                self.check_mime_type_compatibility(path)
                filtered_assets.append(asset)
            except (FileNotFoundError, MimeTypeError) as err:
                if raise_error:
                    raise err
        if len(filtered_assets) == 0:
            raise ImportValidationError(
                """
                No files to upload.
                Check that the paths exist and file types are compatible with the project
                """
            )
        return filtered_assets

    def check_mime_type_compatibility(self, path: str):
        """
        Check that the mimetype of a local file is compatible with the project input type.

        Raise:
             FileNotFoundError: if path do not exists
             MimeTypeError: if the asset is not compatible with the project type
        """
        if not os.path.isfile(path):
            raise FileNotFoundError(f"file {path} does not exist")
        mime_type, _ = mimetypes.guess_type(path)
        if mime_type is None:
            raise MimeTypeError(f"The mime type of the asset {path} has not been found")

        input_type = self.project_params.input_type
        if mime_type not in project_compatible_mimetypes[input_type]:
            raise MimeTypeError(
                f"""
                File mime type for {path} is {mime_type} and does not correspond
                to the type of the project.
                File mime type should be one of {project_compatible_mimetypes[input_type]}
                """
            )
        return True

    def filter_duplicate_external_ids(self, assets):
        """Filter out assets whose external_id is already in the project."""
        if len(assets) == 0:
            raise ImportValidationError("No assets to import")
        assets_in_project = QueriesAsset(self.auth).assets(
            project_id=self.project_params.project_id, fields=["externalId"], disable_tqdm=True
        )
        external_ids_in_project = [asset["externalId"] for asset in assets_in_project]
        filtered_assets = [
            asset for asset in assets if asset.get("external_id") not in external_ids_in_project
        ]
        if len(filtered_assets) == 0:
            raise ImportValidationError(
                "No assets to import, all given external_ids already exist in the project"
            )
        return filtered_assets

    def import_assets_by_batch(
        self,
        assets: List[AssetLike],
        batch_importer: BaseBatchImporter,
        batch_size=IMPORT_BATCH_SIZE,
    ):
        """Split assets by batch and import them with a given batch importer."""
        batch_generator = pagination.batch_iterator_builder(assets, batch_size)
        self.pbar.total = len(assets)
        self.pbar.refresh()
        responses = []
        for batch_assets in batch_generator:
            responses.append(batch_importer.import_batch(batch_assets))
        return responses[-1]
