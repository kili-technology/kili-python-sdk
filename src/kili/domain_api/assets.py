"""Assets domain namespace for the Kili Python SDK."""
# pylint: disable=too-many-lines

import warnings
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generator,
    List,
    Literal,
    Optional,
    TypedDict,
    Union,
    cast,
    overload,
)

from typeguard import typechecked
from typing_extensions import deprecated

from kili.core.helpers import is_url
from kili.domain.asset import (
    AssetStatus,
)
from kili.domain.asset.asset import StatusInStep
from kili.domain.issue import IssueStatus, IssueType
from kili.domain.label import LabelType
from kili.domain.types import ListOrTuple
from kili.domain_api.base import DomainNamespace
from kili.domain_api.namespace_utils import get_available_methods

if TYPE_CHECKING:
    import pandas as pd


class AssetFilter(TypedDict, total=False):
    """Filter options for querying assets.

    This TypedDict defines all available filter parameters that can be used
    when listing or counting assets. All fields are optional.

    Use this filter with `kili.assets.list()` and `kili.assets.count()` methods
    to filter assets based on various criteria such as status, assignee, labels,
    metadata, and more.
    """

    asset_id_in: Optional[List[str]]
    asset_id_not_in: Optional[List[str]]
    assignee_in: Optional[ListOrTuple[str]]
    assignee_not_in: Optional[ListOrTuple[str]]
    consensus_mark_gt: Optional[float]
    consensus_mark_gte: Optional[float]
    consensus_mark_lt: Optional[float]
    consensus_mark_lte: Optional[float]
    created_at_gte: Optional[str]
    created_at_lte: Optional[str]
    external_id_in: Optional[List[str]]
    external_id_strictly_in: Optional[List[str]]
    honeypot_mark_gt: Optional[float]
    honeypot_mark_gte: Optional[float]
    honeypot_mark_lt: Optional[float]
    honeypot_mark_lte: Optional[float]
    inference_mark_gte: Optional[float]
    inference_mark_lte: Optional[float]
    issue_status: Optional[IssueStatus]
    issue_type: Optional[IssueType]
    label_author_in: Optional[List[str]]
    label_category_search: Optional[str]
    label_consensus_mark_gt: Optional[float]
    label_consensus_mark_gte: Optional[float]
    label_consensus_mark_lt: Optional[float]
    label_consensus_mark_lte: Optional[float]
    label_created_at_gt: Optional[str]
    label_created_at_gte: Optional[str]
    label_created_at_lt: Optional[str]
    label_created_at_lte: Optional[str]
    label_created_at: Optional[str]
    label_honeypot_mark_gt: Optional[float]
    label_honeypot_mark_gte: Optional[float]
    label_honeypot_mark_lt: Optional[float]
    label_honeypot_mark_lte: Optional[float]
    label_labeler_in: Optional[ListOrTuple[str]]
    label_labeler_not_in: Optional[ListOrTuple[str]]
    label_reviewer_in: Optional[ListOrTuple[str]]
    label_reviewer_not_in: Optional[ListOrTuple[str]]
    label_type_in: Optional[List[LabelType]]
    metadata_where: Optional[Dict[str, Any]]
    skipped: Optional[bool]
    status_in: Optional[List[AssetStatus]]
    step_name_in: Optional[List[str]]
    step_status_in: Optional[List[StatusInStep]]
    updated_at_gte: Optional[str]
    updated_at_lte: Optional[str]


class VideoProcessingParameters(TypedDict, total=False):
    """Processing parameters for video assets.

    These parameters control how video assets are processed and displayed in Kili.

    Attributes:
        frames_played_per_second: Frame rate for video playback (frames per second)
        number_of_frames: Total number of frames in the video
        start_time: Starting time offset in seconds
    """

    frames_played_per_second: int

    number_of_frames: int

    start_time: float


class ImageLayerParam(TypedDict, total=False):
    """Parameters of an image or geospatial layer.

    Attributes:
        path: local path to the file to use as a layer
        name: Optional name for the layer
    """

    path: str
    name: Optional[str]


class GeospatialLayerParam(ImageLayerParam, total=False):
    """Parameters for geospatial layers, extending ImageLayerParam.

    Attributes:
        path: URL or local path to the geospatial layer file
        name: Optional name for the layer
        bounds: Optional bounding box coordinates [[minX, minY], [maxX, maxY]]
        epsg: Optional coordinate reference system (EPSG3857 or EPSG4326)
    """

    bounds: Optional[List[List[float]]]
    epsg: Optional[Literal["EPSG3857", "EPSG4326"]]


def convert_to_web_layer(layer: GeospatialLayerParam) -> dict[str, Any]:
    """Convert a GeospatialLayerParam to web layer format for URL-based geospatial layers.

    Args:
        layer: Layer parameter dictionary with name, path, bounds, and epsg

    Returns:
        Dictionary with web layer configuration including tileLayerUrl and coordinates settings
    """
    res = {
        "bounds": layer.get("bounds"),
        "epsg": layer.get("epsg") if layer.get("epsg") else "EPSG3857",
        "name": layer.get("name"),
        "tileLayerUrl": layer.get("path"),
        "useClassicCoordinates": False,
        "isBaseLayer": False,
    }
    return res


def convert_to_local_layer(layer: GeospatialLayerParam) -> dict[str, Any]:
    """Convert a GeospatialLayerParam to local layer format for file-based geospatial layers.

    Args:
        layer: Layer parameter dictionary with name and path

    Returns:
        Dictionary with local layer configuration containing name and path
    """
    if layer.get("bounds"):
        warnings.warn(
            "Custom bounds are not yet supported for local layers.",
            stacklevel=1,
        )
    if layer.get("epsg"):
        warnings.warn(
            "Forced epsg are not yet supported for local layers.",
            stacklevel=1,
        )
    res = {
        "name": layer.get("name"),
        "path": layer.get("path"),
    }
    return res


def _snake_to_camel_case(snake_str: str) -> str:
    """Convert snake_case string to camelCase.

    Args:
        snake_str: String in snake_case format

    Returns:
        String in camelCase format
    """
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def _transform_processing_parameters(
    params: Dict[str, Any],
) -> Dict[str, Any]:
    """Transform processing parameter keys from snake_case to camelCase.

    Args:
        params: Processing parameters with snake_case keys (video or GeoTIFF)

    Returns:
        Dictionary with camelCase keys
    """
    return {_snake_to_camel_case(key): value for key, value in params.items()}


def _prepare_video_processing_parameters(
    params: VideoProcessingParameters, use_native_video: bool
) -> Dict[str, Any]:
    """Prepare video processing parameters with defaults.

    Transforms keys from snake_case to camelCase and adds default parameters:
    - shouldUseNativeVideo: True for native video, False for frame-based video
    - shouldKeepNativeFrameRate: False (if framesPlayedPerSecond is specified)

    Args:
        params: Video processing parameters with snake_case keys
        use_native_video: True for native video, False for frame-based video

    Returns:
        Dictionary with camelCase keys and default parameters added
    """
    # Transform to camelCase
    transformed = _transform_processing_parameters(cast(Dict[str, Any], params))

    # Add shouldUseNativeVideo based on the method
    transformed["shouldUseNativeVideo"] = use_native_video

    # Add shouldKeepNativeFrameRate=False if framesPlayedPerSecond is defined
    if "framesPlayedPerSecond" in transformed:
        transformed["shouldKeepNativeFrameRate"] = False

    return transformed


class AssetsNamespace(DomainNamespace):  # pylint: disable=too-many-public-methods
    """Assets domain namespace providing asset-related operations.

    This namespace provides access to all asset-related functionality
    including creating, updating, querying, and managing assets.

    The namespace provides the following main operations:
    - list(): Query and list assets
    - count(): Count assets matching filters
    - create_image(): Create image assets
    - create_video_native(): Create video assets from video files
    - create_video_frame(): Create video assets from frame sequences
    - create_geospatial(): Create multi-layer geospatial imagery assets
    - create_pdf(): Create PDF assets
    - create_text(): Create plain text assets
    - create_rich_text(): Create rich-text formatted text assets
    - delete(): Delete assets from projects
    - add_metadata(): Add metadata to assets
    - set_metadata(): Set metadata on assets
    - update_external_id(): Update asset external IDs
    - update_processing_parameter(): Update video processing parameters
    - invalidate(): Send assets back to queue (invalidate current step)
    - move_to_next_step(): Move assets to the next workflow step
    - assign(): Assign assets to labelers
    - update_priority(): Update asset priorities
    - skip(): Skip an asset
    - unskip(): Unskip an asset

    Examples:
        >>> kili = Kili()
        >>> # List assets
        >>> assets = kili.assets.list(project_id="my_project")

        >>> # Count assets
        >>> count = kili.assets.count(project_id="my_project")

        >>> # Create image assets
        >>> result = kili.assets.create_image(
        ...     project_id="my_project",
        ...     content_array=["https://example.com/image.png"]
        ... )

        >>> # Create video from video file
        >>> result = kili.assets.create_video_native(
        ...     project_id="my_project",
        ...     content="https://example.com/video.mp4",
        ...     processing_parameters={"frames_played_per_second": 25}
        ... )

        >>> # Add asset metadata
        >>> kili.assets.add_metadata(
        ...     json_metadata={"key": "value"},
        ...     project_id="my_project",
        ...     asset_id="asset_id"
        ... )

        >>> # Assign assets to labelers
        >>> kili.assets.assign(
        ...     asset_ids=["asset_id"],
        ...     to_be_labeled_by_array=[["user_id"]]
        ... )
    """

    def __init__(self, client, gateway):
        """Initialize the assets namespace.

        Args:
            client: The Kili client instance
            gateway: The KiliAPIGateway instance for API operations
        """
        super().__init__(client, gateway, "assets")

    @deprecated(
        "'assets' is a namespace, not a callable method. "
        "Use kili.assets.list() or other available methods instead."
    )
    def __call__(self, *args, **kwargs):
        """Raise a helpful error when namespace is called like a method.

        This provides guidance to users migrating from the legacy API
        where assets were accessed via kili.assets(...) to the new domain API
        where they use kili.assets.list(...) or other methods.
        """
        available_methods = get_available_methods(self)
        methods_str = ", ".join(f"kili.{self._domain_name}.{m}()" for m in available_methods)
        raise TypeError(
            f"'{self._domain_name}' is a namespace, not a callable method. "
            f"The legacy API 'kili.{self._domain_name}(...)' has been replaced with the domain API.\n"
            f"Available methods: {methods_str}\n"
            f"Example: kili.{self._domain_name}.list(...)"
        )

    @typechecked
    def list(
        self,
        project_id: str,
        disable_tqdm: Optional[bool] = None,
        download_media: bool = False,
        fields: Optional[ListOrTuple[str]] = None,
        filter: Optional[AssetFilter] = None,
        first: Optional[int] = None,
        format: Optional[str] = None,
        label_output_format: Literal["dict", "parsed_label"] = "dict",
        local_media_dir: Optional[str] = None,
        skip: int = 0,
    ) -> Union[List[Dict], "pd.DataFrame"]:
        """List assets from a project.

        Args:
            project_id: Identifier of the project.
            skip: Number of assets to skip (ordered by creation date).
            fields: List of fields to return. If None, returns default fields.
            filter: Additional asset filters to apply (see `AssetFilter` for available keys).
            disable_tqdm: If True, the progress bar will be disabled.
            first: Maximum number of assets to return.
            format: Output format; when set to `"pandas"` returns a DataFrame.
            download_media: If True, downloads media files locally.
            local_media_dir: Directory used when `download_media` is True.
            label_output_format: Format of the returned labels ("dict" or "parsed_label").

        Returns:
            A list of assets or a pandas DataFrame depending on `format`.
        """
        filter_kwargs = filter or {}
        return self._client.assets(
            as_generator=False,
            disable_tqdm=disable_tqdm,
            download_media=download_media,
            fields=fields,
            first=first,
            format=format,
            label_output_format=label_output_format,
            local_media_dir=local_media_dir,
            project_id=project_id,
            skip=skip,
            **filter_kwargs,
        )

    @typechecked
    def list_as_generator(
        self,
        project_id: str,
        disable_tqdm: Optional[bool] = None,
        download_media: bool = False,
        fields: Optional[ListOrTuple[str]] = None,
        filter: Optional[AssetFilter] = None,
        first: Optional[int] = None,
        label_output_format: Literal["dict", "parsed_label"] = "dict",
        local_media_dir: Optional[str] = None,
        skip: int = 0,
    ) -> Generator[Dict, None, None]:
        """List assets from a project.

        Args:
            project_id: Identifier of the project.
            skip: Number of assets to skip (ordered by creation date).
            fields: List of fields to return. If None, returns default fields.
            filter: Additional asset filters to apply (see `AssetFilter` for available keys).
            disable_tqdm: If True, the progress bar will be disabled.
            first: Maximum number of assets to return.
            download_media: If True, downloads media files locally.
            local_media_dir: Directory used when `download_media` is True.
            label_output_format: Format of the returned labels ("dict" or "parsed_label").

        Returns:
            A generator of a list of assets.
        """
        filter_kwargs = filter or {}
        return self._client.assets(
            as_generator=True,
            disable_tqdm=disable_tqdm,
            download_media=download_media,
            fields=fields,
            first=first,
            label_output_format=label_output_format,
            local_media_dir=local_media_dir,
            project_id=project_id,
            skip=skip,
            **filter_kwargs,
        )

    @typechecked
    def count(
        self,
        project_id: str,
        filter: Optional[AssetFilter] = None,
    ) -> int:
        """Count assets in a project.

        Args:
            project_id: Identifier of the project.
            filter: Additional asset filters to apply (see `AssetFilter` for available keys).

        Returns:
            The number of assets matching the filters.

        Examples:
            >>> # Count all assets in project
            >>> count = kili.assets.count(project_id="my_project")

            >>> # Count assets with specific status
            >>> count = kili.assets.count(
            ...     project_id="my_project",
            ...     filter={"status_in": ["TODO", "ONGOING"]}
            ... )
        """
        filter_kwargs = filter or {}
        return self._client.count_assets(
            project_id=project_id,
            **filter_kwargs,
        )

    @overload
    def create_image(
        self,
        *,
        project_id: str,
        content: Union[str, dict],
        external_id: Optional[str] = None,
        json_metadata: Optional[dict] = None,
        wait_until_availability: bool = True,
        **kwargs,
    ) -> Dict[Literal["id", "asset_ids"], Union[str, List[str]]]:
        ...

    @overload
    def create_image(
        self,
        *,
        project_id: str,
        content_array: Union[List[str], List[dict]],
        external_id_array: Optional[List[str]] = None,
        json_metadata_array: Optional[List[dict]] = None,
        disable_tqdm: Optional[bool] = None,
        wait_until_availability: bool = True,
        **kwargs,
    ) -> Dict[Literal["id", "asset_ids"], Union[str, List[str]]]:
        ...

    @typechecked
    def create_image(
        self,
        *,
        project_id: str,
        content: Optional[Union[str, dict]] = None,
        content_array: Optional[Union[List[str], List[dict]]] = None,
        external_id: Optional[str] = None,
        external_id_array: Optional[List[str]] = None,
        json_metadata: Optional[dict] = None,
        json_metadata_array: Optional[List[dict]] = None,
        disable_tqdm: Optional[bool] = None,
        wait_until_availability: bool = True,
        **kwargs,
    ) -> Dict[Literal["id", "asset_ids"], Union[str, List[str]]]:
        """Create image assets in a project.

        Args:
            project_id: Identifier of the project
            content: URL or local file path to an image
            content_array: List of URLs or local file paths to images
            external_id: External id to identify the asset
            external_id_array: List of external ids given to identify the assets
            json_metadata: The metadata given to the asset
            json_metadata_array: The metadata given to each asset
            disable_tqdm: If True, the progress bar will be disabled
            wait_until_availability: If True, waits until assets are fully processed
            **kwargs: Additional arguments (e.g., is_honeypot)

        Returns:
            A dictionary with project id and list of created asset ids

        Examples:
            >>> # Create single image asset
            >>> result = kili.assets.create_image(
            ...     project_id="my_project",
            ...     content="https://example.com/image.png"
            ... )

            >>> # Create multiple image assets
            >>> result = kili.assets.create_image(
            ...     project_id="my_project",
            ...     content_array=["https://example.com/image1.png", "https://example.com/image2.png"]
            ... )

            >>> # Create single asset with metadata
            >>> result = kili.assets.create_image(
            ...     project_id="my_project",
            ...     content="https://example.com/image.png",
            ...     json_metadata={"description": "Sample image"}
            ... )
        """
        # Convert singular to plural
        if content is not None:
            content_array = cast(Union[List[str], List[dict]], [content])
        if external_id is not None:
            external_id_array = [external_id]
        if json_metadata is not None:
            json_metadata_array = [json_metadata]

        # Call the legacy method directly through the client
        return self._client.append_many_to_dataset(
            project_id=project_id,
            content_array=content_array,
            external_id_array=external_id_array,
            json_metadata_array=json_metadata_array,
            disable_tqdm=disable_tqdm,
            wait_until_availability=wait_until_availability,
            **kwargs,
        )

    @overload
    def create_layered_image(
        self,
        *,
        project_id: str,
        layers: List[ImageLayerParam],
        external_id: Optional[str] = None,
        json_metadata: Optional[dict] = None,
        wait_until_availability: bool = True,
        **kwargs,
    ) -> Dict[Literal["id", "asset_ids"], Union[str, List[str]]]:
        ...

    @overload
    def create_layered_image(
        self,
        *,
        project_id: str,
        layers_array: List[List[ImageLayerParam]],
        external_id_array: Optional[List[str]] = None,
        json_metadata_array: Optional[List[dict]] = None,
        disable_tqdm: Optional[bool] = None,
        wait_until_availability: bool = True,
        **kwargs,
    ) -> Dict[Literal["id", "asset_ids"], Union[str, List[str]]]:
        ...

    @typechecked
    def create_layered_image(
        self,
        *,
        project_id: str,
        layers: Optional[List[ImageLayerParam]] = None,
        layers_array: Optional[List[List[ImageLayerParam]]] = None,
        external_id: Optional[str] = None,
        external_id_array: Optional[List[str]] = None,
        json_metadata: Optional[dict] = None,
        json_metadata_array: Optional[List[dict]] = None,
        disable_tqdm: Optional[bool] = None,
        wait_until_availability: bool = True,
        **kwargs,
    ) -> Dict[Literal["id", "asset_ids"], Union[str, List[str]]]:
        """Create image assets in a project.

        Args:
            project_id: Identifier of the project
            layers: List of image layers for a single asset
            layers_array: List of image layer lists for multiple assets
            external_id: External id to identify the asset
            external_id_array: List of external ids given to identify the assets
            json_metadata: The metadata given to the asset
            json_metadata_array: The metadata given to each asset
            disable_tqdm: If True, the progress bar will be disabled
            wait_until_availability: If True, waits until assets are fully processed
            **kwargs: Additional arguments (e.g., is_honeypot)

        Returns:
            A dictionary with project id and list of created asset ids

        Examples:
            >>> # Create single image asset
            >>> result = kili.assets.create_image(
            ...     project_id="my_project",
            ...     content="https://example.com/image.png"
            ... )

            >>> # Create multiple image assets
            >>> result = kili.assets.create_image(
            ...     project_id="my_project",
            ...     content_array=["https://example.com/image1.png", "https://example.com/image2.png"]
            ... )

            >>> # Create single asset with metadata
            >>> result = kili.assets.create_image(
            ...     project_id="my_project",
            ...     content="https://example.com/image.png",
            ...     json_metadata={"description": "Sample image"}
            ... )
        """
        # Convert singular to plural
        if layers is not None:
            layers_array = [layers]
        if external_id is not None:
            external_id_array = [external_id]
        if json_metadata is not None:
            json_metadata_array = [json_metadata]

        # Call the legacy method directly through the client
        return self._client.append_many_to_dataset(
            project_id=project_id,
            multi_layer_content_array=cast(Optional[List[List[dict]]], layers_array),
            external_id_array=external_id_array,
            json_metadata_array=json_metadata_array,
            disable_tqdm=disable_tqdm,
            wait_until_availability=wait_until_availability,
            **kwargs,
        )

    @overload
    def create_video_native(
        self,
        *,
        project_id: str,
        content: Union[str, dict],
        processing_parameters: Optional[VideoProcessingParameters] = None,
        external_id: Optional[str] = None,
        json_metadata: Optional[dict] = None,
        wait_until_availability: bool = True,
        **kwargs,
    ) -> Dict[Literal["id", "asset_ids"], Union[str, List[str]]]:
        ...

    @overload
    def create_video_native(
        self,
        *,
        project_id: str,
        content_array: Union[List[str], List[dict]],
        processing_parameters_array: Optional[List[VideoProcessingParameters]] = None,
        external_id_array: Optional[List[str]] = None,
        json_metadata_array: Optional[List[dict]] = None,
        disable_tqdm: Optional[bool] = None,
        wait_until_availability: bool = True,
        **kwargs,
    ) -> Dict[Literal["id", "asset_ids"], Union[str, List[str]]]:
        ...

    @typechecked
    def create_video_native(
        self,
        *,
        project_id: str,
        content: Optional[Union[str, dict]] = None,
        content_array: Optional[Union[List[str], List[dict]]] = None,
        processing_parameters: Optional[VideoProcessingParameters] = None,
        processing_parameters_array: Optional[List[VideoProcessingParameters]] = None,
        external_id: Optional[str] = None,
        external_id_array: Optional[List[str]] = None,
        json_metadata: Optional[dict] = None,
        json_metadata_array: Optional[List[dict]] = None,
        disable_tqdm: Optional[bool] = None,
        wait_until_availability: bool = True,
        **kwargs,
    ) -> Dict[Literal["id", "asset_ids"], Union[str, List[str]]]:
        """Create video assets from video files in a project.

        If processing parameters are incomplete, Kili will probe the videos to determine missing parameters.

        Args:
            project_id: Identifier of the project
            content: URL or local file path to a video file
            content_array: List of URLs or local file paths to video files
            processing_parameters: Video processing configuration
            processing_parameters_array: List of video processing configurations for each asset
            external_id: External id to identify the asset
            external_id_array: List of external ids given to identify the assets
            json_metadata: The metadata given to the asset
            json_metadata_array: The metadata given to each asset
            disable_tqdm: If True, the progress bar will be disabled
            wait_until_availability: If True, waits until assets are fully processed
            **kwargs: Additional arguments (e.g., is_honeypot)

        Returns:
            A dictionary with project id and list of created asset ids

        Examples:
            >>> # Create single video asset
            >>> result = kili.assets.create_video_native(
            ...     project_id="my_project",
            ...     content="https://example.com/video.mp4"
            ... )

            >>> # Create video with processing parameters
            >>> result = kili.assets.create_video_native(
            ...     project_id="my_project",
            ...     content="https://example.com/video.mp4",
            ...     processing_parameters={"frames_played_per_second": 25}
            ... )

            >>> # Create multiple video assets
            >>> result = kili.assets.create_video_native(
            ...     project_id="my_project",
            ...     content_array=["https://example.com/video1.mp4", "https://example.com/video2.mp4"],
            ...     processing_parameters_array=[{"frames_played_per_second": 25}, {"frames_played_per_second": 30}]
            ... )
        """
        # Convert singular to plural
        if content is not None:
            content_array = cast(Union[List[str], List[dict]], [content])
        if external_id is not None:
            external_id_array = [external_id]
        if json_metadata is not None:
            json_metadata_array = [json_metadata]
        if processing_parameters is not None:
            processing_parameters_array = [processing_parameters]

        # Merge processing parameters into json_metadata
        if processing_parameters_array is not None:
            if json_metadata_array is None:
                json_metadata_array = [{} for _ in processing_parameters_array]
            for i, params in enumerate(processing_parameters_array):
                if i < len(json_metadata_array):
                    json_metadata_array[i][
                        "processingParameters"
                    ] = _prepare_video_processing_parameters(params, use_native_video=True)

        # Call the legacy method directly through the client
        return self._client.append_many_to_dataset(
            project_id=project_id,
            content_array=content_array,
            external_id_array=external_id_array,
            json_metadata_array=json_metadata_array,
            disable_tqdm=disable_tqdm,
            wait_until_availability=wait_until_availability,
            **kwargs,
        )

    @overload
    def create_video_frame(
        self,
        *,
        project_id: str,
        json_content: Union[List[Union[dict, str]], None],
        processing_parameters: Optional[VideoProcessingParameters] = None,
        external_id: Optional[str] = None,
        json_metadata: Optional[dict] = None,
        wait_until_availability: bool = True,
        **kwargs,
    ) -> Dict[Literal["id", "asset_ids"], Union[str, List[str]]]:
        ...

    @overload
    def create_video_frame(
        self,
        *,
        project_id: str,
        json_content_array: List[Union[List[Union[dict, str]], None]],
        processing_parameters_array: Optional[List[VideoProcessingParameters]] = None,
        external_id_array: Optional[List[str]] = None,
        json_metadata_array: Optional[List[dict]] = None,
        disable_tqdm: Optional[bool] = None,
        wait_until_availability: bool = True,
        **kwargs,
    ) -> Dict[Literal["id", "asset_ids"], Union[str, List[str]]]:
        ...

    @typechecked
    def create_video_frame(
        self,
        *,
        project_id: str,
        json_content: Optional[Union[List[Union[dict, str]], None]] = None,
        json_content_array: Optional[List[Union[List[Union[dict, str]], None]]] = None,
        processing_parameters: Optional[VideoProcessingParameters] = None,
        processing_parameters_array: Optional[List[VideoProcessingParameters]] = None,
        external_id: Optional[str] = None,
        external_id_array: Optional[List[str]] = None,
        json_metadata: Optional[dict] = None,
        json_metadata_array: Optional[List[dict]] = None,
        disable_tqdm: Optional[bool] = None,
        wait_until_availability: bool = True,
        **kwargs,
    ) -> Dict[Literal["id", "asset_ids"], Union[str, List[str]]]:
        """Create video assets from frame sequences in a project.

        If processing parameters are incomplete, Kili will probe the videos to determine missing parameters.

        Args:
            project_id: Identifier of the project
            json_content: Sequence of frames (list of URLs or paths to images)
            json_content_array: List of frame sequences for each video
            processing_parameters: Video processing configuration
            processing_parameters_array: List of video processing configurations for each asset
            external_id: External id to identify the asset
            external_id_array: List of external ids given to identify the assets
            json_metadata: The metadata given to the asset
            json_metadata_array: The metadata given to each asset
            disable_tqdm: If True, the progress bar will be disabled
            wait_until_availability: If True, waits until assets are fully processed
            **kwargs: Additional arguments (e.g., is_honeypot)

        Returns:
            A dictionary with project id and list of created asset ids

        Examples:
            >>> # Create single video from frames
            >>> result = kili.assets.create_video_frame(
            ...     project_id="my_project",
            ...     json_content=["https://example.com/frame1.png", "https://example.com/frame2.png"]
            ... )

            >>> # Create video from frames with processing parameters
            >>> result = kili.assets.create_video_frame(
            ...     project_id="my_project",
            ...     json_content=["https://example.com/frame1.png", "https://example.com/frame2.png"],
            ...     processing_parameters={"frames_played_per_second": 25}
            ... )

            >>> # Create multiple videos from frames
            >>> result = kili.assets.create_video_frame(
            ...     project_id="my_project",
            ...     json_content_array=[
            ...         ["https://example.com/video1/frame1.png", "https://example.com/video1/frame2.png"],
            ...         ["https://example.com/video2/frame1.png", "https://example.com/video2/frame2.png"]
            ...     ]
            ... )
        """
        # Convert singular to plural
        if json_content is not None:
            json_content_array = [json_content]
        if external_id is not None:
            external_id_array = [external_id]
        if json_metadata is not None:
            json_metadata_array = [json_metadata]
        if processing_parameters is not None:
            processing_parameters_array = [processing_parameters]

        # Merge processing parameters into json_metadata
        if processing_parameters_array is not None:
            if json_metadata_array is None:
                json_metadata_array = [{} for _ in processing_parameters_array]
            for i, params in enumerate(processing_parameters_array):
                if i < len(json_metadata_array):
                    json_metadata_array[i][
                        "processingParameters"
                    ] = _prepare_video_processing_parameters(params, use_native_video=False)

        # Call the legacy method directly through the client
        return self._client.append_many_to_dataset(
            project_id=project_id,
            json_content_array=json_content_array,
            external_id_array=external_id_array,
            json_metadata_array=json_metadata_array,
            disable_tqdm=disable_tqdm,
            wait_until_availability=wait_until_availability,
            **kwargs,
        )

    @overload
    def create_geospatial(
        self,
        *,
        project_id: str,
        layer_array: Optional[List[GeospatialLayerParam]] = None,
        external_id: Optional[str] = None,
        json_metadata: Optional[dict] = None,
        wait_until_availability: bool = True,
        **kwargs,
    ) -> Dict[Literal["id", "asset_ids"], Union[str, List[str]]]:
        ...

    @overload
    def create_geospatial(
        self,
        *,
        project_id: str,
        layer_arrays: Optional[List[List[GeospatialLayerParam]]] = None,
        external_id_array: Optional[List[str]] = None,
        json_metadata_array: Optional[List[dict]] = None,
        disable_tqdm: Optional[bool] = None,
        wait_until_availability: bool = True,
        **kwargs,
    ) -> Dict[Literal["id", "asset_ids"], Union[str, List[str]]]:
        ...

    @typechecked
    def create_geospatial(
        self,
        *,
        project_id: str,
        layer_array: Optional[List[GeospatialLayerParam]] = None,
        layer_arrays: Optional[List[List[GeospatialLayerParam]]] = None,
        external_id: Optional[str] = None,
        external_id_array: Optional[List[str]] = None,
        json_metadata: Optional[dict] = None,
        json_metadata_array: Optional[List[dict]] = None,
        disable_tqdm: Optional[bool] = None,
        wait_until_availability: bool = True,
        **kwargs,
    ) -> Dict[Literal["id", "asset_ids"], Union[str, List[str]]]:
        """Create single/multi-layer geospatial imagery assets in a project.

        Args:
            project_id: Identifier of the project
            layer_array: List of layer paths for a single geospatial asset
            layer_arrays: List of multi-layer content for each geospatial asset
            external_id: External id to identify the asset
            external_id_array: List of external ids given to identify the assets
            json_metadata: The metadata given to the asset
            json_metadata_array: The metadata given to each asset
            disable_tqdm: If True, the progress bar will be disabled
            wait_until_availability: If True, waits until assets are fully processed
            **kwargs: Additional arguments (e.g., is_honeypot)

        Returns:
            A dictionary with project id and list of created asset ids

        Examples:
            >>> # Create single geospatial asset
            >>> result = kili.assets.create_geospatial(
            ...     project_id="my_project",
            ...     layer_array=[
            ...         {"path": "/path/to/layer1.tif"},
            ...         {"path": "/path/to/layer2.tif"}
            ...     ]
            ... )

            >>> # Create multiple geospatial assets
            >>> result = kili.assets.create_geospatial(
            ...     project_id="my_project",
            ...     layer_arrays=[
            ...         [{"path": "/path/to/asset1/layer1.tif"}, {"path": "/path/to/asset1/layer2.tif"}],
            ...         [{"path": "/path/to/asset2/layer1.tif"}]
            ...     ]
            ... )
        """
        # Convert singular to plural
        if layer_array is not None:
            layer_arrays = [layer_array]
        if external_id is not None:
            external_id_array = [external_id]
        if json_metadata is not None:
            json_metadata_array = [json_metadata]

        multi_layer_content_array = []
        json_content_array = []

        if layer_arrays is None:
            raise ValueError(
                "One of layer_array or layer_arrays parameter need to be filled"
                " to create a geospatial asset"
            )

        # Split layers into 2 arrays, depending on path parameter
        for layers in layer_arrays:
            multi_layer_contents = []
            json_contents = []
            for layer in layers:
                if is_url(layer.get("path")):
                    # is web url, check mandatory params
                    web_layer = convert_to_web_layer(layer)
                    json_contents.append(web_layer)
                else:
                    local_layer = convert_to_local_layer(layer)
                    multi_layer_contents.append(local_layer)
            multi_layer_content_array.append(multi_layer_contents)
            json_content_array.append(json_contents)

        # Call the legacy method directly through the client
        return self._client.append_many_to_dataset(
            project_id=project_id,
            multi_layer_content_array=multi_layer_content_array,
            external_id_array=external_id_array,
            json_metadata_array=json_metadata_array,
            json_content_array=json_content_array,
            disable_tqdm=disable_tqdm,
            wait_until_availability=wait_until_availability,
            **kwargs,
        )

    @overload
    def create_pdf(
        self,
        *,
        project_id: str,
        content: Union[str, dict],
        external_id: Optional[str] = None,
        json_metadata: Optional[dict] = None,
        wait_until_availability: bool = True,
        **kwargs,
    ) -> Dict[Literal["id", "asset_ids"], Union[str, List[str]]]:
        ...

    @overload
    def create_pdf(
        self,
        *,
        project_id: str,
        content_array: Union[List[str], List[dict]],
        external_id_array: Optional[List[str]] = None,
        json_metadata_array: Optional[List[dict]] = None,
        disable_tqdm: Optional[bool] = None,
        wait_until_availability: bool = True,
        **kwargs,
    ) -> Dict[Literal["id", "asset_ids"], Union[str, List[str]]]:
        ...

    @typechecked
    def create_pdf(
        self,
        *,
        project_id: str,
        content: Optional[Union[str, dict]] = None,
        content_array: Optional[Union[List[str], List[dict]]] = None,
        external_id: Optional[str] = None,
        external_id_array: Optional[List[str]] = None,
        json_metadata: Optional[dict] = None,
        json_metadata_array: Optional[List[dict]] = None,
        disable_tqdm: Optional[bool] = None,
        wait_until_availability: bool = True,
        **kwargs,
    ) -> Dict[Literal["id", "asset_ids"], Union[str, List[str]]]:
        """Create PDF assets in a project.

        Args:
            project_id: Identifier of the project
            content: URL or local file path to a PDF
            content_array: List of URLs or local file paths to PDFs
            external_id: External id to identify the asset
            external_id_array: List of external ids given to identify the assets
            json_metadata: The metadata given to the asset
            json_metadata_array: The metadata given to each asset
            disable_tqdm: If True, the progress bar will be disabled
            wait_until_availability: If True, waits until assets are fully processed
            **kwargs: Additional arguments (e.g., is_honeypot)

        Returns:
            A dictionary with project id and list of created asset ids

        Examples:
            >>> # Create single PDF asset
            >>> result = kili.assets.create_pdf(
            ...     project_id="my_project",
            ...     content="https://example.com/document.pdf"
            ... )

            >>> # Create multiple PDF assets
            >>> result = kili.assets.create_pdf(
            ...     project_id="my_project",
            ...     content_array=["https://example.com/doc1.pdf", "https://example.com/doc2.pdf"]
            ... )

            >>> # Create PDF with metadata
            >>> result = kili.assets.create_pdf(
            ...     project_id="my_project",
            ...     content="https://example.com/document.pdf",
            ...     json_metadata={"title": "Contract Document"}
            ... )
        """
        # Convert singular to plural
        if content is not None:
            content_array = cast(Union[List[str], List[dict]], [content])
        if external_id is not None:
            external_id_array = [external_id]
        if json_metadata is not None:
            json_metadata_array = [json_metadata]

        # Call the legacy method directly through the client
        return self._client.append_many_to_dataset(
            project_id=project_id,
            content_array=content_array,
            external_id_array=external_id_array,
            json_metadata_array=json_metadata_array,
            disable_tqdm=disable_tqdm,
            wait_until_availability=wait_until_availability,
            **kwargs,
        )

    @overload
    def create_text(
        self,
        *,
        project_id: str,
        content: Union[str, dict],
        external_id: Optional[str] = None,
        json_metadata: Optional[dict] = None,
        wait_until_availability: bool = True,
        **kwargs,
    ) -> Dict[Literal["id", "asset_ids"], Union[str, List[str]]]:
        ...

    @overload
    def create_text(
        self,
        *,
        project_id: str,
        content_array: Union[List[str], List[dict]],
        external_id_array: Optional[List[str]] = None,
        json_metadata_array: Optional[List[dict]] = None,
        disable_tqdm: Optional[bool] = None,
        wait_until_availability: bool = True,
        **kwargs,
    ) -> Dict[Literal["id", "asset_ids"], Union[str, List[str]]]:
        ...

    @typechecked
    def create_text(
        self,
        *,
        project_id: str,
        content: Optional[Union[str, dict]] = None,
        content_array: Optional[Union[List[str], List[dict]]] = None,
        external_id: Optional[str] = None,
        external_id_array: Optional[List[str]] = None,
        json_metadata: Optional[dict] = None,
        json_metadata_array: Optional[List[dict]] = None,
        disable_tqdm: Optional[bool] = None,
        wait_until_availability: bool = True,
        **kwargs,
    ) -> Dict[Literal["id", "asset_ids"], Union[str, List[str]]]:
        """Create plain text assets in a project.

        Args:
            project_id: Identifier of the project
            content: Raw text content or URL to text asset
            content_array: List of raw text contents or URLs to text assets
            external_id: External id to identify the asset
            external_id_array: List of external ids given to identify the assets
            json_metadata: The metadata given to the asset
            json_metadata_array: The metadata given to each asset
            disable_tqdm: If True, the progress bar will be disabled
            wait_until_availability: If True, waits until assets are fully processed
            **kwargs: Additional arguments (e.g., is_honeypot)

        Returns:
            A dictionary with project id and list of created asset ids

        Examples:
            >>> # Create single text asset
            >>> result = kili.assets.create_text(
            ...     project_id="my_project",
            ...     content="This is a sample text for annotation."
            ... )

            >>> # Create multiple text assets
            >>> result = kili.assets.create_text(
            ...     project_id="my_project",
            ...     content_array=["First text sample", "Second text sample"]
            ... )

            >>> # Create text asset with metadata
            >>> result = kili.assets.create_text(
            ...     project_id="my_project",
            ...     content="Sample text",
            ...     json_metadata={"source": "user_feedback"}
            ... )
        """
        # Convert singular to plural
        if content is not None:
            content_array = cast(Union[List[str], List[dict]], [content])
        if external_id is not None:
            external_id_array = [external_id]
        if json_metadata is not None:
            json_metadata_array = [json_metadata]

        # Call the legacy method directly through the client
        return self._client.append_many_to_dataset(
            project_id=project_id,
            content_array=content_array,
            external_id_array=external_id_array,
            json_metadata_array=json_metadata_array,
            disable_tqdm=disable_tqdm,
            wait_until_availability=wait_until_availability,
            **kwargs,
        )

    @overload
    def create_rich_text(
        self,
        *,
        project_id: str,
        json_content: Union[List[Union[dict, str]], None],
        external_id: Optional[str] = None,
        json_metadata: Optional[dict] = None,
        wait_until_availability: bool = True,
        **kwargs,
    ) -> Dict[Literal["id", "asset_ids"], Union[str, List[str]]]:
        ...

    @overload
    def create_rich_text(
        self,
        *,
        project_id: str,
        json_content_array: List[Union[List[Union[dict, str]], None]],
        external_id_array: Optional[List[str]] = None,
        json_metadata_array: Optional[List[dict]] = None,
        disable_tqdm: Optional[bool] = None,
        wait_until_availability: bool = True,
        **kwargs,
    ) -> Dict[Literal["id", "asset_ids"], Union[str, List[str]]]:
        ...

    @typechecked
    def create_rich_text(
        self,
        *,
        project_id: str,
        json_content: Optional[Union[List[Union[dict, str]], None]] = None,
        json_content_array: Optional[List[Union[List[Union[dict, str]], None]]] = None,
        external_id: Optional[str] = None,
        external_id_array: Optional[List[str]] = None,
        json_metadata: Optional[dict] = None,
        json_metadata_array: Optional[List[dict]] = None,
        disable_tqdm: Optional[bool] = None,
        wait_until_availability: bool = True,
        **kwargs,
    ) -> Dict[Literal["id", "asset_ids"], Union[str, List[str]]]:
        """Create rich-text formatted text assets in a project.

        Rich-text assets use a structured JSON format to represent formatted text content.
        See the Kili documentation for the rich-text format specification.

        Args:
            project_id: Identifier of the project
            json_content: Rich-text formatted content (JSON structure)
            json_content_array: List of rich-text formatted contents
            external_id: External id to identify the asset
            external_id_array: List of external ids given to identify the assets
            json_metadata: The metadata given to the asset
            json_metadata_array: The metadata given to each asset
            disable_tqdm: If True, the progress bar will be disabled
            wait_until_availability: If True, waits until assets are fully processed
            **kwargs: Additional arguments (e.g., is_honeypot)

        Returns:
            A dictionary with project id and list of created asset ids

        Examples:
            >>> # Create single rich-text asset
            >>> result = kili.assets.create_rich_text(
            ...     project_id="my_project",
            ...     json_content=[{"text": "Hello ", "style": "normal"}, {"text": "world", "style": "bold"}]
            ... )

            >>> # Create multiple rich-text assets
            >>> result = kili.assets.create_rich_text(
            ...     project_id="my_project",
            ...     json_content_array=[
            ...         [{"text": "First document", "style": "normal"}],
            ...         [{"text": "Second document", "style": "italic"}]
            ...     ]
            ... )

        !!! info "Rich-text format"
            For detailed information on the rich-text format, see the
            [Kili documentation on importing text assets](
                https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/import_text_assets/
            ).
        """
        # Convert singular to plural
        if json_content is not None:
            json_content_array = [json_content]
        if external_id is not None:
            external_id_array = [external_id]
        if json_metadata is not None:
            json_metadata_array = [json_metadata]

        # Call the legacy method directly through the client
        return self._client.append_many_to_dataset(
            project_id=project_id,
            json_content_array=json_content_array,
            external_id_array=external_id_array,
            json_metadata_array=json_metadata_array,
            disable_tqdm=disable_tqdm,
            wait_until_availability=wait_until_availability,
            **kwargs,
        )

    @overload
    def delete(
        self,
        *,
        asset_id: str,
        project_id: str = "",
    ) -> Optional[Dict[Literal["id"], str]]:
        ...

    @overload
    def delete(
        self,
        *,
        asset_ids: List[str],
        project_id: str = "",
    ) -> Optional[Dict[Literal["id"], str]]:
        ...

    @overload
    def delete(
        self,
        *,
        external_id: str,
        project_id: str = "",
    ) -> Optional[Dict[Literal["id"], str]]:
        ...

    @overload
    def delete(
        self,
        *,
        external_ids: List[str],
        project_id: str = "",
    ) -> Optional[Dict[Literal["id"], str]]:
        ...

    @typechecked
    def delete(
        self,
        *,
        asset_id: Optional[str] = None,
        asset_ids: Optional[List[str]] = None,
        external_id: Optional[str] = None,
        external_ids: Optional[List[str]] = None,
        project_id: str = "",
    ) -> Optional[Dict[Literal["id"], str]]:
        """Delete assets from a project.

        Args:
            asset_id: The asset internal ID to delete.
            asset_ids: The list of asset internal IDs to delete.
            external_id: The asset external ID to delete.
            external_ids: The list of asset external IDs to delete.
            project_id: The project ID. Only required if `external_id(s)` argument is provided.

        Returns:
            A dict object with the project `id`.

        Examples:
            >>> # Delete single asset by internal ID
            >>> result = kili.assets.delete(asset_id="ckg22d81r0jrg0885unmuswj8")

            >>> # Delete multiple assets by internal IDs
            >>> result = kili.assets.delete(
            ...     asset_ids=["ckg22d81r0jrg0885unmuswj8", "ckg22d81s0jrh0885pdxfd03n"]
            ... )

            >>> # Delete assets by external IDs
            >>> result = kili.assets.delete(
            ...     external_ids=["asset1", "asset2"],
            ...     project_id="my_project"
            ... )
        """
        # Convert singular to plural
        if asset_id is not None:
            asset_ids = [asset_id]
        if external_id is not None:
            external_ids = [external_id]

        # Call the legacy method directly through the client
        return self._client.delete_many_from_dataset(
            asset_ids=asset_ids,
            external_ids=external_ids,
            project_id=project_id,
        )

    @overload
    def update_processing_parameter(
        self,
        *,
        asset_id: str,
        processing_parameter: Union[dict, str],
        project_id: str = "",
        **kwargs,
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @overload
    def update_processing_parameter(
        self,
        *,
        asset_ids: List[str],
        processing_parameters: List[Union[dict, str]],
        project_id: str = "",
        **kwargs,
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @overload
    def update_processing_parameter(
        self,
        *,
        external_id: str,
        processing_parameter: Union[dict, str],
        project_id: str = "",
        **kwargs,
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @overload
    def update_processing_parameter(
        self,
        *,
        external_ids: List[str],
        processing_parameters: List[Union[dict, str]],
        project_id: str = "",
        **kwargs,
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @typechecked
    def update_processing_parameter(
        self,
        *,
        asset_id: Optional[str] = None,
        asset_ids: Optional[List[str]] = None,
        processing_parameter: Optional[Union[dict, str]] = None,
        processing_parameters: Optional[List[Union[dict, str]]] = None,
        external_id: Optional[str] = None,
        external_ids: Optional[List[str]] = None,
        project_id: str = "",
        **kwargs,
    ) -> List[Dict[Literal["id"], str]]:
        """Update processing_parameter of one or more assets.

        Args:
            asset_id: The internal asset ID to modify.
            asset_ids: The internal asset IDs to modify.
            processing_parameter: Video processing parameter for the asset.
            processing_parameters: Video processing parameters for the assets.
            external_id: The external asset ID to modify (if `asset_id` is not already provided).
            external_ids: The external asset IDs to modify (if `asset_ids` is not already provided).
            project_id: The project ID.
            **kwargs: Additional update parameters.

        Returns:
            A list of dictionaries with the asset ids.

        Examples:
            >>> # Single asset
            >>> result = kili.assets.update_processing_parameter(
            ...     asset_id="ckg22d81r0jrg0885unmuswj8",
            ...     processing_parameter={
            ...         "frames_played_per_second": 25,
            ...         "shouldKeepNativeFrameRate": True,
            ...         "shouldUseNativeVideo": True,
            ...         "codec": "h264",
            ...         "delayDueToMinPts": 0,
            ...         "numberOfFrames": 450,
            ...         "startTime": 0
            ...     }
            ... )

            >>> # Multiple assets
            >>> result = kili.assets.update_processing_parameter(
            ...     asset_ids=["ckg22d81r0jrg0885unmuswj8", "ckg22d81s0jrh0885pdxfd03n"],
            ...     processing_parameters=[{
            ...         "frames_played_per_second": 25,
            ...         "shouldKeepNativeFrameRate": True,
            ...     }, {
            ...         "frames_played_per_second": 30,
            ...         "shouldKeepNativeFrameRate": False,
            ...     }]
            ... )
        """
        # Convert singular to plural
        if asset_id is not None:
            asset_ids = [asset_id]
        if external_id is not None:
            external_ids = [external_id]
        if processing_parameter is not None:
            processing_parameters = [processing_parameter]

        json_metadatas = []
        for p in processing_parameters if processing_parameters is not None else []:
            json_metadatas.append({"processingParameters": p})

        # Call the legacy method directly through the client
        return self._client.update_properties_in_assets(
            asset_ids=asset_ids,
            external_ids=external_ids,
            project_id=project_id,
            json_metadatas=json_metadatas,
            **kwargs,
        )

    @overload
    def update_external_id(
        self,
        *,
        new_external_id: str,
        asset_id: str,
        project_id: str = "",
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @overload
    def update_external_id(
        self,
        *,
        new_external_ids: List[str],
        asset_ids: List[str],
        project_id: str = "",
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @overload
    def update_external_id(
        self,
        *,
        new_external_id: str,
        external_id: str,
        project_id: str = "",
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @overload
    def update_external_id(
        self,
        *,
        new_external_ids: List[str],
        external_ids: List[str],
        project_id: str = "",
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @typechecked
    def update_external_id(
        self,
        *,
        new_external_id: Optional[str] = None,
        new_external_ids: Optional[List[str]] = None,
        asset_id: Optional[str] = None,
        asset_ids: Optional[List[str]] = None,
        external_id: Optional[str] = None,
        external_ids: Optional[List[str]] = None,
        project_id: str = "",
    ) -> List[Dict[Literal["id"], str]]:
        """Update the external ID of one or more assets.

        Args:
            new_external_id: The new external ID of the asset.
            new_external_ids: The new external IDs of the assets.
            asset_id: The asset ID to modify.
            asset_ids: The asset IDs to modify.
            external_id: The external asset ID to modify (if `asset_id` is not already provided).
            external_ids: The external asset IDs to modify (if `asset_ids` is not already provided).
            project_id: The project ID. Only required if `external_id(s)` argument is provided.

        Returns:
            A list of dictionaries with the asset ids.

        Examples:
            >>> # Single asset
            >>> kili.assets.update_external_id(
                    new_external_id="new_asset1",
                    asset_id="ckg22d81r0jrg0885unmuswj8",
                )

            >>> # Multiple assets
            >>> kili.assets.update_external_id(
                    new_external_ids=["asset1", "asset2"],
                    asset_ids=["ckg22d81r0jrg0885unmuswj8", "ckg22d81s0jrh0885pdxfd03n"],
                )
        """
        # Convert singular to plural
        if new_external_id is not None:
            new_external_ids = [new_external_id]
        if asset_id is not None:
            asset_ids = [asset_id]
        if external_id is not None:
            external_ids = [external_id]

        assert new_external_ids is not None, "new_external_ids must be provided"

        return self._client.change_asset_external_ids(
            new_external_ids=new_external_ids,
            asset_ids=asset_ids,
            external_ids=external_ids,
            project_id=project_id,
        )

    @overload
    def add_metadata(
        self,
        *,
        json_metadata: Dict[str, Union[str, int, float]],
        project_id: str,
        asset_id: str,
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @overload
    def add_metadata(
        self,
        *,
        json_metadata: List[Dict[str, Union[str, int, float]]],
        project_id: str,
        asset_ids: List[str],
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @overload
    def add_metadata(
        self,
        *,
        json_metadata: Dict[str, Union[str, int, float]],
        project_id: str,
        external_id: str,
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @overload
    def add_metadata(
        self,
        *,
        json_metadata: List[Dict[str, Union[str, int, float]]],
        project_id: str,
        external_ids: List[str],
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @typechecked
    def add_metadata(
        self,
        *,
        json_metadata: Union[
            Dict[str, Union[str, int, float]], List[Dict[str, Union[str, int, float]]]
        ],
        project_id: str,
        asset_id: Optional[str] = None,
        asset_ids: Optional[List[str]] = None,
        external_id: Optional[str] = None,
        external_ids: Optional[List[str]] = None,
    ) -> List[Dict[Literal["id"], str]]:
        """Add metadata to assets without overriding existing metadata.

        Args:
            json_metadata: Metadata dictionary to add to asset, or list of metadata dictionaries to add to each asset.
                Each dictionary contains key/value pairs to be added to the asset's metadata.
            project_id: The project ID.
            asset_id: The asset ID to modify.
            asset_ids: The asset IDs to modify.
            external_id: The external asset ID to modify (if `asset_id` is not already provided).
            external_ids: The external asset IDs to modify (if `asset_ids` is not already provided).

        Returns:
            A list of dictionaries with the asset ids.

        Examples:
            >>> # Single asset
            >>> kili.assets.add_metadata(
                    json_metadata={"key1": "value1", "key2": "value2"},
                    project_id="cm92to3cx012u7l0w6kij9qvx",
                    asset_id="ckg22d81r0jrg0885unmuswj8"
                )

            >>> # Multiple assets
            >>> kili.assets.add_metadata(
                    json_metadata=[
                        {"key1": "value1", "key2": "value2"},
                        {"key3": "value3"}
                    ],
                    project_id="cm92to3cx012u7l0w6kij9qvx",
                    asset_ids=["ckg22d81r0jrg0885unmuswj8", "ckg22d81s0jrh0885pdxfd03n"]
                )
        """
        # Convert singular to plural
        if asset_id is not None:
            asset_ids = [asset_id]
        if external_id is not None:
            external_ids = [external_id]
        if isinstance(json_metadata, dict):
            json_metadata = [json_metadata]

        return self._client.add_metadata(
            json_metadata=json_metadata,
            project_id=project_id,
            asset_ids=asset_ids,
            external_ids=external_ids,
        )

    @overload
    def set_metadata(
        self,
        *,
        json_metadata: Dict[str, Union[str, int, float]],
        project_id: str,
        asset_id: str,
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @overload
    def set_metadata(
        self,
        *,
        json_metadata: List[Dict[str, Union[str, int, float]]],
        project_id: str,
        asset_ids: List[str],
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @overload
    def set_metadata(
        self,
        *,
        json_metadata: Dict[str, Union[str, int, float]],
        project_id: str,
        external_id: str,
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @overload
    def set_metadata(
        self,
        *,
        json_metadata: List[Dict[str, Union[str, int, float]]],
        project_id: str,
        external_ids: List[str],
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @typechecked
    def set_metadata(
        self,
        *,
        json_metadata: Union[
            Dict[str, Union[str, int, float]], List[Dict[str, Union[str, int, float]]]
        ],
        project_id: str,
        asset_id: Optional[str] = None,
        asset_ids: Optional[List[str]] = None,
        external_id: Optional[str] = None,
        external_ids: Optional[List[str]] = None,
    ) -> List[Dict[Literal["id"], str]]:
        """Set metadata on assets, replacing any existing metadata.

        Args:
            json_metadata: Metadata dictionary to set on asset, or list of metadata dictionaries to set on each asset.
                Each dictionary contains key/value pairs to be set as the asset's metadata.
            project_id: The project ID.
            asset_id: The asset ID to modify.
            asset_ids: The asset IDs to modify (if `external_ids` is not already provided).
            external_id: The external asset ID to modify (if `asset_id` is not already provided).
            external_ids: The external asset IDs to modify (if `asset_ids` is not already provided).

        Returns:
            A list of dictionaries with the asset ids.

        Examples:
            >>> # Single asset
            >>> kili.assets.set_metadata(
                    json_metadata={"key1": "value1", "key2": "value2"},
                    project_id="cm92to3cx012u7l0w6kij9qvx",
                    asset_id="ckg22d81r0jrg0885unmuswj8"
                )

            >>> # Multiple assets
            >>> kili.assets.set_metadata(
                    json_metadata=[
                        {"key1": "value1", "key2": "value2"},
                        {"key3": "value3"}
                    ],
                    project_id="cm92to3cx012u7l0w6kij9qvx",
                    asset_ids=["ckg22d81r0jrg0885unmuswj8", "ckg22d81s0jrh0885pdxfd03n"]
                )
        """
        # Convert singular to plural
        if asset_id is not None:
            asset_ids = [asset_id]
        if external_id is not None:
            external_ids = [external_id]
        if isinstance(json_metadata, dict):
            json_metadata = [json_metadata]

        return self._client.set_metadata(
            json_metadata=json_metadata,
            project_id=project_id,
            asset_ids=asset_ids,
            external_ids=external_ids,
        )

    @typechecked
    def skip(
        self,
        *,
        asset_id: str,
        project_id: str,
        reason: str,
    ) -> str:
        """Skip an asset.

        Args:
            asset_id: ID of the asset you want to skip.
            project_id: The project ID.
            reason: The reason why you skip an asset.

        Returns:
            The asset ID of the asset skipped. An error message if mutation failed.

        Examples:
            >>> kili.assets.skip(
                project_id="ckg22d81r0jrg0885unmuswj8",
                asset_id="ckg22d81s0jrh0885pdxfd03n",
                reason="Test"
                )
        """
        return self._client.skip_or_unskip(
            action="skip",
            asset_id=asset_id,
            project_id=project_id,
            reason=reason,
        )

    @typechecked
    def unskip(
        self,
        *,
        asset_id: str,
        project_id: str,
    ) -> str:
        """Unskip an asset.

        Args:
            asset_id: ID of the asset you want to unskip.
            project_id: The project ID.

        Returns:
            The asset ID of the asset unskipped. An error message if mutation failed.

        Examples:
            >>> kili.assets.unskip(
                asset_id="ckg22d81s0jrh0885pdxfd03n"
                project_id="ckg22d81r0jrg0885unmuswj8"
            )
        """
        return self._client.skip_or_unskip(
            action="unskip", asset_id=asset_id, project_id=project_id
        )

    @overload
    def invalidate(
        self,
        *,
        external_id: str,
        project_id: str = "",
    ) -> Optional[Dict[str, Any]]:
        ...

    @overload
    def invalidate(
        self,
        *,
        external_ids: List[str],
        project_id: str = "",
    ) -> Optional[Dict[str, Any]]:
        ...

    @overload
    def invalidate(
        self,
        *,
        asset_id: str,
        project_id: str = "",
    ) -> Optional[Dict[str, Any]]:
        ...

    @overload
    def invalidate(
        self,
        *,
        asset_ids: List[str],
        project_id: str = "",
    ) -> Optional[Dict[str, Any]]:
        ...

    @typechecked
    def invalidate(
        self,
        *,
        asset_id: Optional[str] = None,
        asset_ids: Optional[List[str]] = None,
        external_id: Optional[str] = None,
        external_ids: Optional[List[str]] = None,
        project_id: str = "",
    ) -> Optional[Dict[str, Any]]:
        """Send assets back to queue (invalidate current step).

        This method sends assets back to the queue, effectively invalidating their
        current workflow step status.

        Args:
            asset_id: Internal ID of asset to send back to queue.
            asset_ids: List of internal IDs of assets to send back to queue.
            external_id: External ID of asset to send back to queue.
            external_ids: List of external IDs of assets to send back to queue.
            project_id: The project ID. Only required if `external_id(s)` argument is provided.

        Returns:
            A dict object with the project `id` and the `asset_ids` of assets moved to queue.
            An error message if mutation failed.

        Examples:
            >>> # Single asset
            >>> kili.assets.invalidate(asset_id="ckg22d81r0jrg0885unmuswj8")

            >>> # Multiple assets
            >>> kili.assets.invalidate(
                    asset_ids=["ckg22d81r0jrg0885unmuswj8", "ckg22d81s0jrh0885pdxfd03n"]
                )
        """
        # Convert singular to plural
        if asset_id is not None:
            asset_ids = [asset_id]
        if external_id is not None:
            external_ids = [external_id]

        return self._client.send_back_to_queue(
            asset_ids=asset_ids,
            external_ids=external_ids,
            project_id=project_id,
        )

    @overload
    def move_to_next_step(
        self,
        *,
        asset_id: str,
        project_id: str = "",
    ) -> Optional[Dict[str, Any]]:
        ...

    @overload
    def move_to_next_step(
        self,
        *,
        asset_ids: List[str],
        project_id: str = "",
    ) -> Optional[Dict[str, Any]]:
        ...

    @overload
    def move_to_next_step(
        self,
        *,
        external_id: str,
        project_id: str = "",
    ) -> Optional[Dict[str, Any]]:
        ...

    @overload
    def move_to_next_step(
        self,
        *,
        external_ids: List[str],
        project_id: str = "",
    ) -> Optional[Dict[str, Any]]:
        ...

    @typechecked
    def move_to_next_step(
        self,
        *,
        asset_id: Optional[str] = None,
        asset_ids: Optional[List[str]] = None,
        external_id: Optional[str] = None,
        external_ids: Optional[List[str]] = None,
        project_id: str = "",
    ) -> Optional[Dict[str, Any]]:
        """Move assets to the next workflow step (typically review).

        This method moves assets to the next step in the workflow, typically
        adding them to review.

        Args:
            asset_id: The asset internal ID to add to review.
            asset_ids: The asset internal IDs to add to review.
            external_id: The asset external ID to add to review.
            external_ids: The asset external IDs to add to review.
            project_id: The project ID. Only required if `external_id(s)` argument is provided.

        Returns:
            A dict object with the project `id` and the `asset_ids` of assets moved to review.
            `None` if no assets have changed status (already had `TO_REVIEW` status for example).
            An error message if mutation failed.

        Examples:
            >>> # Single asset
            >>> kili.assets.move_to_next_step(asset_id="ckg22d81r0jrg0885unmuswj8")

            >>> # Multiple assets
            >>> kili.assets.move_to_next_step(
                    asset_ids=["ckg22d81r0jrg0885unmuswj8", "ckg22d81s0jrh0885pdxfd03n"]
                )
        """
        # Convert singular to plural
        if asset_id is not None:
            asset_ids = [asset_id]
        if external_id is not None:
            external_ids = [external_id]

        return self._client.add_to_review(
            asset_ids=asset_ids,
            external_ids=external_ids,
            project_id=project_id,
        )

    @overload
    def assign(
        self,
        *,
        to_be_labeled_by: List[str],
        asset_id: str,
        project_id: str = "",
    ) -> List[Dict[str, Any]]:
        ...

    @overload
    def assign(
        self,
        *,
        to_be_labeled_by_array: List[List[str]],
        asset_ids: List[str],
        project_id: str = "",
    ) -> List[Dict[str, Any]]:
        ...

    @overload
    def assign(
        self,
        *,
        to_be_labeled_by: List[str],
        external_id: str,
        project_id: str = "",
    ) -> List[Dict[str, Any]]:
        ...

    @overload
    def assign(
        self,
        *,
        to_be_labeled_by_array: List[List[str]],
        external_ids: List[str],
        project_id: str = "",
    ) -> List[Dict[str, Any]]:
        ...

    @typechecked
    def assign(
        self,
        *,
        to_be_labeled_by: Optional[List[str]] = None,
        to_be_labeled_by_array: Optional[List[List[str]]] = None,
        asset_id: Optional[str] = None,
        asset_ids: Optional[List[str]] = None,
        external_id: Optional[str] = None,
        external_ids: Optional[List[str]] = None,
        project_id: str = "",
    ) -> List[Dict[str, Any]]:
        """Assign a list of assets to a list of labelers.

        Args:
            to_be_labeled_by: List of labeler user IDs to assign to a single asset.
            to_be_labeled_by_array: Array of lists of labelers to assign per asset (list of userIds).
            asset_id: The internal asset ID to assign.
            asset_ids: The internal asset IDs to assign.
            external_id: The external asset ID to assign (if `asset_id` is not already provided).
            external_ids: The external asset IDs to assign (if `asset_ids` is not already provided).
            project_id: The project ID. Only required if `external_id(s)` argument is provided.

        Returns:
            A list of dictionaries with the asset ids.

        Examples:
            >>> # Single asset
            >>> kili.assets.assign(
                    asset_id="ckg22d81r0jrg0885unmuswj8",
                    to_be_labeled_by=['cm3yja6kv0i698697gcil9rtk','cm3yja6kv0i000000gcil9rtk']
                )

            >>> # Multiple assets
            >>> kili.assets.assign(
                    asset_ids=["ckg22d81r0jrg0885unmuswj8", "ckg22d81s0jrh0885pdxfd03n"],
                    to_be_labeled_by_array=[['cm3yja6kv0i698697gcil9rtk','cm3yja6kv0i000000gcil9rtk'],
                                            ['cm3yja6kv0i698697gcil9rtk']]
                )
        """
        # Convert singular to plural
        if asset_id is not None:
            asset_ids = [asset_id]
        if external_id is not None:
            external_ids = [external_id]
        if to_be_labeled_by is not None:
            to_be_labeled_by_array = [to_be_labeled_by]

        assert to_be_labeled_by_array is not None, "to_be_labeled_by_array must be provided"

        return self._client.assign_assets_to_labelers(
            asset_ids=asset_ids,
            external_ids=external_ids,
            project_id=project_id,
            to_be_labeled_by_array=to_be_labeled_by_array,
        )

    @overload
    def update_priority(
        self,
        *,
        asset_id: str,
        priority: int,
        project_id: str = "",
        **kwargs,
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @overload
    def update_priority(
        self,
        *,
        asset_ids: List[str],
        priorities: List[int],
        project_id: str = "",
        **kwargs,
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @overload
    def update_priority(
        self,
        *,
        external_id: str,
        priority: int,
        project_id: str = "",
        **kwargs,
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @overload
    def update_priority(
        self,
        *,
        external_ids: List[str],
        priorities: List[int],
        project_id: str = "",
        **kwargs,
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @typechecked
    def update_priority(
        self,
        *,
        asset_id: Optional[str] = None,
        asset_ids: Optional[List[str]] = None,
        priority: Optional[int] = None,
        priorities: Optional[List[int]] = None,
        external_id: Optional[str] = None,
        external_ids: Optional[List[str]] = None,
        project_id: str = "",
        **kwargs,
    ) -> List[Dict[Literal["id"], str]]:
        """Update the priority of one or more assets.

        Args:
            asset_id: The internal asset ID to modify.
            asset_ids: The internal asset IDs to modify.
            priority: Change the priority of the asset.
            priorities: Change the priority of the assets.
            external_id: The external asset ID to modify (if `asset_id` is not already provided).
            external_ids: The external asset IDs to modify (if `asset_ids` is not already provided).
            project_id: The project ID. Only required if `external_id(s)` argument is provided.
            **kwargs: Additional update parameters.

        Returns:
            A list of dictionaries with the asset ids.

        Examples:
            >>> # Single asset
            >>> result = kili.assets.update_priority(
            ...     asset_id="ckg22d81r0jrg0885unmuswj8",
            ...     priority=1,
            ... )

            >>> # Multiple assets
            >>> result = kili.assets.update_priority(
            ...     asset_ids=["ckg22d81r0jrg0885unmuswj8", "ckg22d81s0jrh0885pdxfd03n"],
            ...     priorities=[1, 2],
            ... )
        """
        # Convert singular to plural
        if asset_id is not None:
            asset_ids = [asset_id]
        if external_id is not None:
            external_ids = [external_id]
        if priority is not None:
            priorities = [priority]

        # Call the legacy method directly through the client
        return self._client.update_properties_in_assets(
            asset_ids=asset_ids,
            external_ids=external_ids,
            project_id=project_id,
            priorities=priorities if priorities is not None else [],
            **kwargs,
        )
