"""Common and generic functions to import files into a project."""

import abc
import logging
import mimetypes
import os
import warnings
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from json import dumps, loads
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    NamedTuple,
    Optional,
    Tuple,
    Union,
)
from uuid import uuid4

from tenacity import Retrying
from tenacity.retry import retry_if_exception_type
from tenacity.wait import wait_exponential

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.core.graphql.operations.asset.mutations import (
    GQL_APPEND_MANY_ASSETS,
    GQL_APPEND_MANY_FRAMES_TO_DATASET,
)
from kili.core.helpers import T, format_result, get_mime_type, is_url
from kili.core.utils.pagination import batcher
from kili.domain.organization import OrganizationFilters
from kili.domain.project import InputType, ProjectId
from kili.domain.types import ListOrTuple
from kili.services.asset_import.constants import (
    IMPORT_BATCH_SIZE,
    project_compatible_mimetypes,
)
from kili.services.asset_import.exceptions import (
    BatchImportError,
    BatchImportPendingNotificationError,
    ImportValidationError,
    MimeTypeError,
    UploadFromLocalDataForbiddenError,
)
from kili.services.asset_import.types import AssetLike, KiliResolverAsset
from kili.utils import bucket
from kili.utils.tqdm import tqdm

FILTER_EXISTING_BATCH_SIZE = 1000


if TYPE_CHECKING:
    from kili.client import Kili


class BatchParams(NamedTuple):
    """Contains all parameters related to the batch to import."""

    is_asynchronous: bool
    is_hosted: bool


class ProcessingParams(NamedTuple):
    """Contains all parameters related to the assets processing."""

    raise_error: bool
    verify: bool


class ProjectParams(NamedTuple):
    """Contains all parameters related to the batch to import."""

    project_id: ProjectId
    input_type: InputType


class LoggerParams(NamedTuple):
    """Contains all parameters related to logging."""

    disable_tqdm: Optional[bool]


class BaseBatchImporter:  # pylint: disable=too-many-instance-attributes
    """Base class for BatchImporters."""

    def __init__(
        self, kili: "Kili", project_params: ProjectParams, batch_params: BatchParams, pbar: tqdm
    ) -> None:
        self.kili = kili
        self.project_id = project_params.project_id
        self.input_type = project_params.input_type
        self.is_hosted = batch_params.is_hosted
        self.is_asynchronous = batch_params.is_asynchronous
        self.pbar = pbar
        self.http_client = kili.http_client

        logging.basicConfig()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def import_batch(self, assets: ListOrTuple[AssetLike], verify: bool) -> List[str]:
        """Base actions to import a batch of asset.

        Returns:
            created_assets_ids: list of ids of the created assets
        """
        assets = self.loop_on_batch(self.stringify_metadata)(assets)
        assets = self.loop_on_batch(self.stringify_json_content)(assets)
        assets_ = self.loop_on_batch(self.fill_empty_fields)(assets)
        if self.is_asynchronous and verify:
            notification = self.import_to_kili(assets_)
            if isinstance(notification, list):
                error_message = (
                    "import_to_kili should return a notification for asynchronous "
                    "imports, not a list"
                )
                raise TypeError(error_message)
            self.verify_batch_imported(notification["id"])
            return []

        created_assets_ids = self.import_to_kili(assets_)
        self.pbar.update(n=len(assets))
        return created_assets_ids

    def verify_batch_imported(self, notification_id: str) -> None:
        """Verify that the batch import is completed for asynchronous imports."""
        self.logger.info("Waiting for the import to complete.")

        for attempt in Retrying(
            retry=retry_if_exception_type(BatchImportPendingNotificationError),
            wait=wait_exponential(multiplier=1, min=1, max=16),
            reraise=True,
        ):
            with attempt:
                notification = self.kili.notifications(notification_id=notification_id)[0]
                if notification["status"] == "FAILURE":
                    error_message = (
                        "Some assets were not imported. "
                        "Please check the notification report in the application "
                        "for more information."
                    )
                    raise BatchImportError(error_message)
                if notification["status"] == "SUCCESS":
                    return
                raise BatchImportPendingNotificationError

    def add_ids(self, assets: List[AssetLike]):
        """Adds ids to all assets."""
        return self.loop_on_batch(self.add_id_to_asset)(assets)

    def generate_project_bucket_path(self) -> str:
        """Returns ids."""
        return f"projects/{self.project_id}/assets"

    @staticmethod
    def stringify_metadata(asset: AssetLike) -> AssetLike:
        """Stringify the metadata."""
        json_metadata = asset.get("json_metadata", {})
        if not isinstance(json_metadata, str):
            json_metadata = dumps(json_metadata)
        return {**asset, "json_metadata": json_metadata}

    @staticmethod
    def stringify_json_content(asset: AssetLike) -> AssetLike:
        """Stringify the metadata."""
        json_content = asset.get("json_content", "")
        if not isinstance(json_content, str):
            json_content = dumps(json_content)
        return {**asset, "json_content": json_content}

    @staticmethod
    def add_id_to_asset(asset: AssetLike) -> AssetLike:
        """Generates an asset id."""
        return {**asset, "id": asset.get("id", bucket.generate_unique_id())}

    @staticmethod
    def fill_empty_fields(asset: AssetLike):
        """Fill empty fields with their default value."""
        asset_fields_default_value = AssetLike(
            content="",
            multi_layer_content=None,
            json_content="",
            external_id=uuid4().hex,
            json_metadata="{}",
            is_honeypot=False,
            id="",
        )
        field_names = asset_fields_default_value.keys()
        return KiliResolverAsset(
            **{field: asset.get(field, asset_fields_default_value[field]) for field in field_names}
        )

    @staticmethod
    def loop_on_batch(
        func: Callable[[AssetLike], T],
    ) -> Callable[[ListOrTuple[AssetLike]], List[T]]:
        """Apply a function, that takes a single asset as input, on the whole batch."""

        def loop_func(assets: ListOrTuple[AssetLike]):
            return [func(asset) for asset in assets]

        return loop_func

    @staticmethod
    def build_url_from_parts(*parts) -> str:
        """Builds an url from the parts."""
        return "/".join(parts)

    @staticmethod
    def are_native_videos(assets) -> bool:
        """Determine if assets should be imported asynchronously and cut into frames."""
        should_use_native_video_array = []
        for asset in assets:
            json_metadata = asset.get("json_metadata", "{}")
            json_metadata_ = loads(json_metadata)
            processing_parameters = json_metadata_.get("processingParameters", {})
            should_use_native_video_array.append(
                processing_parameters.get("shouldUseNativeVideo", True)
            )
        if all(should_use_native_video_array):
            return True
        if all(not b for b in should_use_native_video_array):
            return False
        raise ImportValidationError(
            """
            Cannot upload videos to split into frames
            and video to keep as native in the same time.
            Please separate the assets into 2 calls
            """
        )

    def _async_import_to_kili(self, assets: List[KiliResolverAsset]):
        """Import assets with asynchronous resolver."""
        if self.input_type == "IMAGE":
            upload_type = "GEO_SATELLITE"
        elif self.input_type in ("VIDEO", "VIDEO_LEGACY"):
            upload_type = "NATIVE_VIDEO" if self.are_native_videos(assets) else "FRAME_VIDEO"
        else:
            raise NotImplementedError(
                f"Import of {self.input_type} assets is not supported in async calls"
            )

        content = (
            {
                "multiLayerContentArray": [asset["multi_layer_content"] for asset in assets],
                "jsonContentArray": [asset["json_content"] for asset in assets],
            }
            if all(asset.get("multi_layer_content") is not None for asset in assets)
            else {"contentArray": [asset["content"] for asset in assets]}
        )
        payload = {
            "data": {
                **content,
                "externalIDArray": [asset["external_id"] for asset in assets],
                "idArray": [asset["id"] for asset in assets],
                "jsonMetadataArray": [asset["json_metadata"] for asset in assets],
                "uploadType": upload_type,
            },
            "where": {"id": self.project_id},
        }
        result = self.kili.graphql_client.execute(GQL_APPEND_MANY_FRAMES_TO_DATASET, payload)
        return format_result("data", result, None, self.kili.http_client)

    def _sync_import_to_kili(self, assets: List[KiliResolverAsset]):
        """Import assets with synchronous resolver."""
        payload = {
            "data": {
                "contentArray": [asset["content"] for asset in assets],
                "externalIDArray": [asset["external_id"] for asset in assets],
                "idArray": [asset["id"] for asset in assets],
                "isHoneypotArray": [asset["is_honeypot"] for asset in assets],
                "jsonContentArray": [asset["json_content"] for asset in assets],
                "jsonMetadataArray": [asset["json_metadata"] for asset in assets],
            },
            "where": {"id": self.project_id},
        }
        result = self.kili.graphql_client.execute(GQL_APPEND_MANY_ASSETS, payload)
        created_assets = format_result("data", result, None, self.kili.http_client)
        return [asset["id"] for asset in created_assets]

    def import_to_kili(self, assets: List[KiliResolverAsset]):
        """Import assets to Kili with the right resolver.

        Returns:
            created_assets_ids: list of ids of the created assets
        """
        if self.is_asynchronous:
            return self._async_import_to_kili(assets)
        return self._sync_import_to_kili(assets)


class ContentBatchImporter(BaseBatchImporter):
    """Class defining the methods to import a batch of assets with content."""

    def import_batch(self, assets: List[AssetLike], verify: bool):
        """Method to import a batch of asset with content."""
        assets = self.add_ids(assets)
        if not self.is_hosted:
            assets_with_content = [
                asset
                for asset in assets
                if asset.get("content") or asset.get("multi_layer_content")
            ]
            assets = [
                asset
                for asset in assets
                if not asset.get("content") and not asset.get("multi_layer_content")
            ]
            if len(assets_with_content) > 0:
                assets += self.upload_local_content_to_bucket(assets_with_content)
        return super().import_batch(assets, verify)

    def get_content_type_and_data_from_content(
        self, content: Optional[Union[str, bytes]]
    ) -> Tuple[bytes, Optional[str]]:
        """Returns the data of the content (path) and its content type."""
        assert content
        assert isinstance(content, str)
        with Path(content).open("rb") as file:
            data = file.read()
            content_type, _ = mimetypes.guess_type(content)
            return data, content_type

    def get_type_and_data_from_content_array(
        self, content_array: List[Optional[Union[str, bytes]]]
    ) -> List[Tuple[Union[bytes, str], Optional[str]]]:
        # pylint:disable=line-too-long
        """Returns the data of the content (path) and its content type for each element in the array."""
        return list(map(self.get_content_type_and_data_from_content, content_array))

    def upload_local_content_to_bucket(self, assets: List[AssetLike]):
        """Upload local content to a bucket."""
        project_bucket_path = self.generate_project_bucket_path()
        # tuple containing (bucket_path, file_path, asset_index, content_index)
        to_upload: List[Tuple[str, Any, int, Union[int, None]]] = []
        for i, asset in enumerate(assets):
            asset_id = asset.get("id", bucket.generate_unique_id())
            multi_layer_content = asset.get("multi_layer_content")
            if multi_layer_content:
                for j, item in enumerate(multi_layer_content):
                    bucket_path = BaseBatchImporter.build_url_from_parts(
                        project_bucket_path, asset_id, "content", str(j)
                    )
                    to_upload.append((bucket_path, item.get("path"), i, j))
            else:
                bucket_path = BaseBatchImporter.build_url_from_parts(
                    project_bucket_path, asset_id, "content"
                )
                to_upload.append((bucket_path, asset.get("content"), i, None))
        signed_urls = bucket.request_signed_urls(
            self.kili, [bucket_path for bucket_path, *_ in to_upload]
        )
        data_and_content_type_array = self.get_type_and_data_from_content_array(
            [file_path for _, file_path, *_ in to_upload]
        )
        data_array, content_type_array = zip(*data_and_content_type_array)
        with ThreadPoolExecutor() as threads:
            url_gen = threads.map(
                bucket.upload_data_via_rest,
                signed_urls,
                data_array,
                content_type_array,
                repeat(self.http_client),
            )
        assets_with_content = []
        for asset in assets:
            asset_copy = asset.copy()
            multi_layer_content = asset.get("multi_layer_content")
            if multi_layer_content:
                asset_copy["multi_layer_content"] = [
                    {key: value for key, value in content.items() if key != "path"}
                    for content in multi_layer_content
                ]
            assets_with_content.append(asset_copy)
        for (_, _, asset_index, content_index), url in zip(to_upload, url_gen):
            if content_index is not None:
                assets_with_content[asset_index]["multi_layer_content"][content_index]["url"] = url
            else:
                assets_with_content[asset_index]["content"] = url
        return assets_with_content


class JsonContentBatchImporter(BaseBatchImporter):
    """Class defining the import methods for a batch of assets twith json_content."""

    @staticmethod
    def stringify_json_content(asset: AssetLike):
        """Stringify the json content if not a str."""
        json_content = asset.get("json_content", {})
        if not isinstance(json_content, str):
            json_content = dumps(json_content)
        return AssetLike(**{**asset, "json_content": json_content})  # type: ignore

    def upload_json_content_to_bucket(self, assets: List[AssetLike]):
        """Upload the json_contents to a bucket with signed urls."""
        project_bucket_path = self.generate_project_bucket_path()
        asset_json_content_paths = [
            BaseBatchImporter.build_url_from_parts(
                project_bucket_path,
                asset.get("id", bucket.generate_unique_id()),
                "jsonContent",
            )
            for asset in assets
        ]
        signed_urls = bucket.request_signed_urls(self.kili, asset_json_content_paths)
        json_content_array = [asset.get("json_content") for asset in assets]
        with ThreadPoolExecutor() as threads:
            url_gen = threads.map(
                bucket.upload_data_via_rest,
                signed_urls,
                json_content_array,
                ["text/plain"] * len(assets),
                repeat(self.http_client),
            )
        # pylint: disable=line-too-long
        return [AssetLike(**{**asset, "json_content": url}) for asset, url in zip(assets, url_gen)]  # type: ignore

    def import_batch(self, assets: List[AssetLike], verify: bool):
        """Method to import a batch of asset with json content."""
        assets = self.add_ids(assets)
        assets = self.loop_on_batch(self.stringify_json_content)(assets)
        assets = self.upload_json_content_to_bucket(assets)
        return super().import_batch(assets, verify)


class BaseAbstractAssetImporter(abc.ABC):
    """Base class for DataImporters classes."""

    def __init__(
        self,
        kili: "Kili",
        project_params: ProjectParams,
        processing_params: ProcessingParams,
        logger_params: LoggerParams,
    ) -> None:
        self.kili = kili
        self.project_params = project_params
        self.raise_error = processing_params.raise_error
        self.verify = processing_params.verify
        self.pbar = tqdm(disable=logger_params.disable_tqdm)

    @abc.abstractmethod
    def import_assets(self, assets: List[AssetLike]) -> List[str]:
        """Import assets into Kili.

        Returns:
            created_assets_ids: list of ids of the created assets
        """
        raise NotImplementedError

    @staticmethod
    def is_hosted_content(assets: List[AssetLike]) -> bool:
        """Determine if the assets to upload are from local files or hosted data.

        Raise an error if a mix of both.
        """
        multi_layer_contents = [
            asset.get("multi_layer_content") for asset in assets if asset.get("multi_layer_content")
        ]
        if len(multi_layer_contents) > 0:
            if any(
                not isinstance(content.get("path"), str)
                for multi_layer_content in multi_layer_contents
                for content in multi_layer_content  # type: ignore
                if content
            ):
                raise ImportValidationError(
                    "Cannot import multi_layer_content with empty path. Please provide a path for"
                    " each multi_layer_content"
                )
            return False
        contents = [asset.get("content") for asset in assets if asset.get("content")]
        if all(is_url(content) for content in contents):
            return True
        if any(is_url(content) for content in contents):
            raise ImportValidationError(
                "Cannot upload hosted data and local files at the same time. Please separate the"
                " assets into 2 calls."
            )
        return False

    @staticmethod
    def check_asset_contents(assets: List[AssetLike]) -> None:
        """Determine if the assets have at least one content or json_content.

        Raise an error if not
        """
        # Raise an error if there is an asset with no content,
        # no multi_layer_content and no json_content
        for asset in assets:
            if (
                not asset.get("content")
                and not asset.get("multi_layer_content")
                and not asset.get("json_content")
            ):
                raise ImportValidationError(
                    "Cannot import asset with empty content, empty"
                    " multi_layer_content and empty json_content"
                )

    def _can_upload_from_local_data(self) -> bool:
        user_me = self.kili.kili_api_gateway.get_current_user(fields=("email",))
        options = QueryOptions(first=1, disable_tqdm=True)
        organization = self._get_organization(user_me["email"], options)
        return organization["license"]["uploadLocalData"]

    def _get_organization(self, email: str, options: QueryOptions) -> Dict:
        return next(
            self.kili.kili_api_gateway.list_organizations(
                filters=OrganizationFilters(email=email),
                fields=["license.uploadLocalData"],
                description="",
                options=options,
            )
        )

    def _check_upload_is_allowed(self, assets: List[AssetLike]) -> None:
        # TODO: avoid querying API for each asset to upload when doing this check
        if not self.is_hosted_content(assets) and not self._can_upload_from_local_data():
            raise UploadFromLocalDataForbiddenError("Cannot upload content from local data")

    def filter_local_assets(self, assets: List[AssetLike], raise_error: bool):
        """Filter out local files that cannot be imported.

        Return an error at the first file that cannot be imported if raise_error is True
        """
        filtered_assets = []
        for asset in assets:
            json_content = asset.get("json_content")
            multi_layer_content = asset.get("multi_layer_content")
            path = asset.get("content")
            if multi_layer_content or (json_content and not path):
                filtered_assets.append(asset)
                continue
            assert path
            assert isinstance(path, str)
            try:
                self.check_mime_type_compatibility(path)
                filtered_assets.append(asset)
            except (FileNotFoundError, MimeTypeError):
                if raise_error:
                    raise
        if len(filtered_assets) == 0:
            # pylint: disable=line-too-long
            raise ImportValidationError(
                """No files to upload. Check that the paths exist and file types are compatible with the project."""
            )
        return filtered_assets

    def check_mime_type_compatibility(self, path: str):
        """Check that the mimetype of a local file is compatible with the project input type.

        Raise:
             FileNotFoundError: if path do not exists
             MimeTypeError: if the asset is not compatible with the project type
        """
        if not os.path.isfile(path):
            raise FileNotFoundError(f"file {path} does not exist")
        mime_type = get_mime_type(path)
        if mime_type is None:
            raise MimeTypeError(f"The mime type of the asset {path} has not been found")

        input_type = self.project_params.input_type
        if mime_type not in project_compatible_mimetypes[input_type]:
            raise MimeTypeError(
                f"File mime type for {path} is {mime_type} and does not correspond to the type of"
                " the project. File mime type should be one of"
                f" {project_compatible_mimetypes[input_type]}"
            )
        return True

    def filter_duplicate_external_ids(self, assets):
        """Filter out assets whose external_id is already in the project."""
        if len(assets) == 0:
            raise ImportValidationError("No assets to import")
        assets_external_ids = [
            asset.get("external_id") for asset in assets if asset.get("external_id")
        ]
        # split assets_external_ids into chunks of 1000
        assets_external_ids_chunks = [
            assets_external_ids[x : x + FILTER_EXISTING_BATCH_SIZE]
            for x in range(0, len(assets_external_ids), FILTER_EXISTING_BATCH_SIZE)
        ]
        external_ids_in_project = []
        for assets_external_ids_chunk in assets_external_ids_chunks:
            external_ids_in_project += self.kili.kili_api_gateway.filter_existing_assets(
                self.project_params.project_id,
                assets_external_ids_chunk,
            )

        if len(external_ids_in_project) == len(assets):
            raise ImportValidationError(
                "No assets to import, all given external_ids already exist in the project"
            )
        nb_duplicate_assets = len(external_ids_in_project)
        if nb_duplicate_assets > 0:
            warnings.warn(
                f"{nb_duplicate_assets} assets were not imported because their external_id are"
                " already in the project",
                stacklevel=2,
            )
        filtered_assets = [
            asset for asset in assets if asset.get("external_id") not in external_ids_in_project
        ]
        return filtered_assets

    def import_assets_by_batch(
        self,
        assets: List[AssetLike],
        batch_importer: BaseBatchImporter,
        batch_size=IMPORT_BATCH_SIZE,
    ):
        """Split assets by batch and import them with a given batch importer."""
        batch_generator = batcher(assets, batch_size)
        nb_batch = (len(assets) - 1) // batch_size + 1
        self.pbar.total = len(assets)
        self.pbar.refresh()

        created_asset_ids: List[str] = []
        for i, batch_assets in enumerate(batch_generator):
            # check last batch only
            verify = i == (nb_batch - 1) and self.verify
            created_asset_ids += batch_importer.import_batch(batch_assets, verify)
        return created_asset_ids
