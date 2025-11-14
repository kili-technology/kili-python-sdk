# pylint: disable=too-many-lines
"""Labels domain namespace for the Kili Python SDK.

This module provides a comprehensive interface for label-related operations
including creation, querying, management, and event handling.
"""

from typing import (
    TYPE_CHECKING,
    Dict,
    Generator,
    List,
    Literal,
    Optional,
    TypedDict,
    Union,
    overload,
)

from typeguard import typechecked
from typing_extensions import deprecated

from kili.domain.asset import AssetStatus
from kili.domain.asset.asset import StatusInStep
from kili.domain.label import LabelType
from kili.domain.types import ListOrTuple
from kili.domain_api.base import DomainNamespace
from kili.domain_api.namespace_utils import get_available_methods
from kili.utils.labels.parsing import ParsedLabel

if TYPE_CHECKING:
    from kili.client import Kili as KiliLegacy


class LabelFilter(TypedDict, total=False):
    """Filter options for querying labels.

    Attributes:
        asset_external_id_in: Returned labels should have an external id that belongs to
            that list, if given.
        asset_external_id_strictly_in: Returned labels should have an external id that
            exactly matches one of the ids in that list, if given.
        asset_id: Identifier of the asset.
        asset_status_in: Returned labels should have a status that belongs to that list, if given.
        asset_step_name_in: Returned assets are in a step whose name belong to that list, if given.
        asset_step_status_in: Returned assets have the status of their step that belongs to that list, if given.
        author_in: Returned labels should have been made by authors in that list, if given.
        category_search: Query to filter labels based on the content of their jsonResponse.
        created_at_gte: Returned labels should have their creation date greater or equal to this date.
        created_at_lte: Returned labels should have their creation date lower or equal to this date.
        created_at: Returned labels should have their creation date equal to this date.
        honeypot_mark_gte: Returned labels should have a label whose honeypot is greater than this number.
        honeypot_mark_lte: Returned labels should have a label whose honeypot is lower than this number.
        id_contains: Filters out labels not belonging to that list. If empty, no filtering is applied.
        label_id: Identifier of the label.
        type_in: Returned labels should have a label whose type belongs to that list, if given.
        user_id: Identifier of the user.
    """

    asset_external_id_in: Optional[List[str]]
    asset_external_id_strictly_in: Optional[List[str]]
    asset_id: Optional[str]
    asset_status_in: Optional[List[AssetStatus]]
    asset_step_name_in: Optional[List[str]]
    asset_step_status_in: Optional[List[StatusInStep]]
    author_in: Optional[List[str]]
    category_search: Optional[str]
    created_at_gte: Optional[str]
    created_at_lte: Optional[str]
    created_at: Optional[str]
    honeypot_mark_gte: Optional[float]
    honeypot_mark_lte: Optional[float]
    id_contains: Optional[List[str]]
    label_id: Optional[str]
    type_in: Optional[List[LabelType]]
    user_id: Optional[str]


class LabelsNamespace(DomainNamespace):
    """Labels domain namespace providing label-related operations.

    This namespace provides access to all label-related functionality
    including creating, updating, querying, and managing labels and annotations.
    It also provides nested namespaces for specialized operations on predictions,
    inferences, honeypots, and events.
    """

    def __init__(self, client: "KiliLegacy", gateway) -> None:
        """Initialize the labels namespace.

        Args:
            client: The Kili client instance
            gateway: The KiliAPIGateway instance for API operations
        """
        super().__init__(client, gateway, "labels")

    @deprecated(
        "'labels' is a namespace, not a callable method. "
        "Use kili.labels.list() or other available methods instead."
    )
    def __call__(self, *args, **kwargs):
        """Raise a helpful error when namespace is called like a method.

        This provides guidance to users migrating from the legacy API
        where labels were accessed via kili.labels(...) to the new domain API
        where they use kili.labels.list(...) or other methods.
        """
        available_methods = get_available_methods(self)
        methods_str = ", ".join(f"kili.{self._domain_name}.{m}()" for m in available_methods)
        raise TypeError(
            f"'{self._domain_name}' is a namespace, not a callable method. "
            f"The legacy API 'kili.{self._domain_name}(...)' has been replaced with the domain API.\n"
            f"Available methods: {methods_str}\n"
            f"Example: kili.{self._domain_name}.list(...)"
        )

    @overload
    def list(
        self,
        project_id: str,
        fields: ListOrTuple[str] = (
            "author.email",
            "author.id",
            "id",
            "jsonResponse",
            "labelType",
            "secondsToLabel",
            "isLatestLabelForUser",
            "assetId",
        ),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        output_format: Literal["dict"] = "dict",
        filter: Optional[LabelFilter] = None,
    ) -> List[Dict]:
        ...

    @overload
    def list(
        self,
        project_id: str,
        fields: ListOrTuple[str] = (
            "author.email",
            "author.id",
            "id",
            "jsonResponse",
            "labelType",
            "secondsToLabel",
            "isLatestLabelForUser",
            "assetId",
        ),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        output_format: Literal["parsed_label"] = "parsed_label",
        filter: Optional[LabelFilter] = None,
    ) -> List[ParsedLabel]:
        ...

    @typechecked
    def list(
        self,
        project_id: str,
        fields: ListOrTuple[str] = (
            "author.email",
            "author.id",
            "id",
            "jsonResponse",
            "labelType",
            "secondsToLabel",
            "isLatestLabelForUser",
            "assetId",
        ),
        first: Optional[int] = None,
        skip: int = 0,
        disable_tqdm: Optional[bool] = None,
        output_format: Literal["dict", "parsed_label"] = "dict",
        filter: Optional[LabelFilter] = None,
    ) -> Union[List[Dict], List[ParsedLabel]]:
        """Get a label list from a project based on a set of criteria.

        Args:
            project_id: Identifier of the project.
            fields: All the fields to request among the possible fields for the labels.
            first: Maximum number of labels to return.
            skip: Number of labels to skip (they are ordered by their date of creation, first to last).
            disable_tqdm: If `True`, the progress bar will be disabled.
            output_format: If `dict`, the output is a list of Python dictionaries.
                If `parsed_label`, the output is a list of parsed labels objects.
            filter: Optional dictionary to filter labels. See `LabelFilter` for available filter options.

        Returns:
            A list of labels.

        Examples:
            >>> # List all labels in a project
            >>> labels = kili.labels.list(project_id="my_project")

            >>> # List labels with specific filters
            >>> labels = kili.labels.list(
            ...     project_id="my_project",
            ...     filter={
            ...         "asset_id": "asset_123",
            ...         "author_in": ["user1@example.com", "user2@example.com"]
            ...     }
            ... )

            >>> # Get parsed label objects
            >>> parsed_labels = kili.labels.list(
            ...     project_id="my_project",
            ...     output_format="parsed_label"
            ... )
        """
        filter_kwargs = filter or {}
        return self._client.labels(
            project_id=project_id,
            fields=fields,
            first=first,
            skip=skip,
            disable_tqdm=disable_tqdm,
            output_format=output_format,
            as_generator=False,
            **filter_kwargs,
        )

    @overload
    def list_as_generator(
        self,
        project_id: str,
        fields: ListOrTuple[str] = (
            "author.email",
            "author.id",
            "id",
            "jsonResponse",
            "labelType",
            "secondsToLabel",
            "isLatestLabelForUser",
            "assetId",
        ),
        first: Optional[int] = None,
        skip: int = 0,
        output_format: Literal["dict"] = "dict",
        filter: Optional[LabelFilter] = None,
    ) -> Generator[Dict, None, None]:
        ...

    @overload
    def list_as_generator(
        self,
        project_id: str,
        fields: ListOrTuple[str] = (
            "author.email",
            "author.id",
            "id",
            "jsonResponse",
            "labelType",
            "secondsToLabel",
            "isLatestLabelForUser",
            "assetId",
        ),
        first: Optional[int] = None,
        skip: int = 0,
        output_format: Literal["parsed_label"] = "parsed_label",
        filter: Optional[LabelFilter] = None,
    ) -> Generator[ParsedLabel, None, None]:
        ...

    @typechecked
    def list_as_generator(
        self,
        project_id: str,
        fields: ListOrTuple[str] = (
            "author.email",
            "author.id",
            "id",
            "jsonResponse",
            "labelType",
            "secondsToLabel",
            "isLatestLabelForUser",
            "assetId",
        ),
        first: Optional[int] = None,
        skip: int = 0,
        output_format: Literal["dict", "parsed_label"] = "dict",
        filter: Optional[LabelFilter] = None,
    ) -> Union[Generator[Dict, None, None], Generator[ParsedLabel, None, None]]:
        """Get a label generator from a project based on a set of criteria.

        Args:
            project_id: Identifier of the project.
            fields: All the fields to request among the possible fields for the labels.
            first: Maximum number of labels to return.
            skip: Number of labels to skip (they are ordered by their date of creation, first to last).
            output_format: If `dict`, the output is a generator of Python dictionaries.
                If `parsed_label`, the output is a generator of parsed labels objects.
            filter: Optional dictionary to filter labels. See `LabelFilter` for available filter options.

        Returns:
            A generator yielding labels.

        Examples:
            >>> # Iterate over all labels
            >>> for label in kili.labels.list_as_generator(project_id="my_project"):
            ...     print(label["id"])

            >>> # Filter by author and status
            >>> for label in kili.labels.list_as_generator(
            ...     project_id="my_project",
            ...     filter={
            ...         "author_in": ["user@example.com"],
            ...         "asset_status_in": ["LABELED"]
            ...     }
            ... ):
            ...     print(label["id"])
        """
        filter_kwargs = filter or {}
        return self._client.labels(
            project_id=project_id,
            fields=fields,
            first=first,
            skip=skip,
            disable_tqdm=True,
            output_format=output_format,
            as_generator=True,
            **filter_kwargs,
        )

    @typechecked
    def count(self, project_id: str, filter: Optional[LabelFilter] = None) -> int:
        """Get the number of labels for the given parameters.

        Args:
            project_id: Identifier of the project.
            filter: Optional dictionary to filter labels. See `LabelFilter` for available filter options.

        Returns:
            The number of labels with the parameters provided.

        Examples:
            >>> # Count all labels in a project
            >>> count = kili.labels.count(project_id="my_project")

            >>> # Count labels with filters
            >>> count = kili.labels.count(
            ...     project_id="my_project",
            ...     filter={
            ...         "asset_status_in": ["LABELED"],
            ...         "type_in": ["DEFAULT"]
            ...     }
            ... )
        """
        filter_kwargs = filter or {}
        return self._client.count_labels(
            project_id=project_id,
            **filter_kwargs,
        )

    @typechecked
    def __create(
        self,
        *,
        asset_id_array: Optional[List[str]] = None,
        asset_id: Optional[str] = None,
        disable_tqdm: Optional[bool] = None,
        external_id_array: Optional[List[str]] = None,
        external_id: Optional[str] = None,
        json_response_array: Optional[ListOrTuple[Dict]] = None,
        json_response: Optional[Dict] = None,
        label_type: LabelType = "DEFAULT",
        model_name: Optional[str] = None,
        overwrite: bool = False,
        project_id: str,
        reviewed_label_id_array: Optional[List[str]],
        reviewed_label_id: Optional[str],
        step_name: Optional[str] = None,
    ) -> List[Dict[Literal["id"], str]]:
        """Create labels to assets.

        Args:
            asset_id: Asset internal id to append label on.
            asset_id_array: List of asset internal ids to append labels on.
            json_response: Label to append.
            json_response_array: List of labels to append.
            model_name: Name of the model that generated the labels.
                Only useful when uploading PREDICTION or INFERENCE labels.
            label_type: Can be one of `AUTOSAVE`, `DEFAULT`, `PREDICTION`, `REVIEW` or `INFERENCE`.
            project_id: Identifier of the project.
            external_id: Asset external id to append label on.
            external_id_array: List of asset external ids to append labels on.
            disable_tqdm: Disable tqdm progress bar.
            overwrite: when uploading prediction or inference labels, if True,
                it will overwrite existing labels with the same model name
                and of the same label type, on the targeted assets.
            step_name: Name of the step to which the labels belong.
                The label_type must match accordingly.

        Returns:
            A list of dictionaries with the label ids.
        """
        # Convert singular to plural
        if asset_id is not None:
            asset_id_array = [asset_id]
        if json_response is not None:
            json_response_array = [json_response]
        if external_id is not None:
            external_id_array = [external_id]
        if reviewed_label_id is not None:
            reviewed_label_id_array = [reviewed_label_id]

        return self._client.append_labels(
            asset_external_id_array=external_id_array,
            asset_id_array=asset_id_array,
            disable_tqdm=disable_tqdm,
            json_response_array=json_response_array if json_response_array else (),
            label_type=label_type,
            model_name=model_name,
            overwrite=overwrite,
            project_id=project_id,
            reviewed_label_id_array=reviewed_label_id_array,
            step_name=step_name,
        )

    @overload
    def create_default(
        self,
        *,
        asset_id: str,
        json_response: Dict,
        project_id: str,
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @overload
    def create_default(
        self,
        *,
        asset_id_array: List[str],
        json_response_array: ListOrTuple[Dict],
        disable_tqdm: Optional[bool] = None,
        project_id: str,
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @overload
    def create_default(
        self,
        *,
        external_id: str,
        json_response: Dict,
        project_id: str,
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @overload
    def create_default(
        self,
        *,
        external_id_array: List[str],
        json_response_array: ListOrTuple[Dict],
        disable_tqdm: Optional[bool] = None,
        project_id: str,
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @typechecked
    def create_default(
        self,
        *,
        asset_id_array: Optional[List[str]] = None,
        asset_id: Optional[str] = None,
        disable_tqdm: Optional[bool] = None,
        external_id_array: Optional[List[str]] = None,
        external_id: Optional[str] = None,
        json_response_array: Optional[ListOrTuple[Dict]] = None,
        json_response: Optional[Dict] = None,
        project_id: str,
    ) -> List[Dict[Literal["id"], str]]:
        """Create DEFAULT labels to assets.

        Args:
            asset_id: Asset internal id to append label on.
            asset_id_array: List of asset internal ids to append labels on.
            json_response: Label to append.
            json_response_array: List of labels to append.
            project_id: Identifier of the project.
            external_id: Asset external id to append label on.
            external_id_array: List of asset external ids to append labels on.
            disable_tqdm: Disable tqdm progress bar.

        Returns:
            A list of dictionaries with the label ids.
        """
        return self.__create(
            asset_id_array=asset_id_array,
            asset_id=asset_id,
            disable_tqdm=disable_tqdm,
            external_id_array=external_id_array,
            external_id=external_id,
            json_response_array=json_response_array,
            json_response=json_response,
            label_type="DEFAULT",
            project_id=project_id,
            reviewed_label_id=None,
            reviewed_label_id_array=None,
            step_name="Default",
        )

    @overload
    def create_review(
        self,
        *,
        asset_id: str,
        json_response: Dict,
        reviewed_label_id: str,
        project_id: str,
        model_name: Optional[str] = None,
        step_name: Optional[str] = None,
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @overload
    def create_review(
        self,
        *,
        asset_id_array: List[str],
        json_response_array: ListOrTuple[Dict],
        disable_tqdm: Optional[bool] = None,
        model_name: Optional[str] = None,
        project_id: str,
        reviewed_label_id_array: List[str],
        step_name: Optional[str] = None,
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @overload
    def create_review(
        self,
        *,
        external_id: str,
        json_response: Dict,
        model_name: Optional[str] = None,
        project_id: str,
        reviewed_label_id: str,
        step_name: Optional[str] = None,
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @overload
    def create_review(
        self,
        *,
        external_id_array: List[str],
        json_response_array: ListOrTuple[Dict],
        disable_tqdm: Optional[bool] = None,
        model_name: Optional[str] = None,
        project_id: str,
        reviewed_label_id_array: List[str],
        step_name: Optional[str] = None,
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @typechecked
    def create_review(
        self,
        *,
        asset_id_array: Optional[List[str]] = None,
        asset_id: Optional[str] = None,
        disable_tqdm: Optional[bool] = None,
        external_id_array: Optional[List[str]] = None,
        external_id: Optional[str] = None,
        json_response_array: Optional[ListOrTuple[Dict]] = None,
        json_response: Optional[Dict] = None,
        model_name: Optional[str] = None,
        project_id: str,
        reviewed_label_id_array: Optional[List[str]] = None,
        reviewed_label_id: Optional[str] = None,
        step_name: Optional[str] = None,
    ) -> List[Dict[Literal["id"], str]]:
        """Create REVIEW labels to assets.

        Args:
            asset_id: Asset internal id to append label on.
            asset_id_array: List of asset internal ids to append labels on.
            json_response: Label to append.
            json_response_array: List of labels to append.
            model_name: Name of the model that generated the labels.
            project_id: Identifier of the project.
            external_id: Asset external id to append label on.
            external_id_array: List of asset external ids to append labels on.
            disable_tqdm: Disable tqdm progress bar.
            reviewed_label_id: ID of the label being reviewed (for single asset).
            reviewed_label_id_array: List of IDs of labels being reviewed (for multiple assets).
            step_name: Name of the step to which the labels belong.

        Returns:
            A list of dictionaries with the label ids.
        """
        return self.__create(
            asset_id_array=asset_id_array,
            asset_id=asset_id,
            disable_tqdm=disable_tqdm,
            external_id_array=external_id_array,
            external_id=external_id,
            json_response_array=json_response_array,
            json_response=json_response,
            label_type="REVIEW",
            reviewed_label_id=reviewed_label_id,
            reviewed_label_id_array=reviewed_label_id_array,
            model_name=model_name,
            project_id=project_id,
            step_name=step_name,
        )

    @overload
    def create_inference(
        self,
        *,
        asset_id: str,
        json_response: Dict,
        model_name: str,
        overwrite: Optional[bool] = False,
        project_id: str,
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @overload
    def create_inference(
        self,
        *,
        asset_id_array: List[str],
        disable_tqdm: Optional[bool] = None,
        json_response_array: ListOrTuple[Dict],
        model_name: str,
        overwrite: Optional[bool] = False,
        project_id: str,
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @overload
    def create_inference(
        self,
        *,
        external_id: str,
        json_response: Dict,
        model_name: str,
        overwrite: Optional[bool] = False,
        project_id: str,
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @overload
    def create_inference(
        self,
        *,
        disable_tqdm: Optional[bool] = None,
        external_id_array: List[str],
        json_response_array: ListOrTuple[Dict],
        model_name: str,
        overwrite: Optional[bool] = False,
        project_id: str,
    ) -> List[Dict[Literal["id"], str]]:
        ...

    @typechecked
    def create_inference(
        self,
        *,
        asset_id_array: Optional[List[str]] = None,
        asset_id: Optional[str] = None,
        disable_tqdm: Optional[bool] = None,
        external_id_array: Optional[List[str]] = None,
        external_id: Optional[str] = None,
        json_response_array: Optional[ListOrTuple[Dict]] = None,
        json_response: Optional[Dict] = None,
        model_name: str,
        overwrite: Optional[bool] = False,
        project_id: str,
    ) -> List[Dict[Literal["id"], str]]:
        """Create INFERENCE labels to assets.

        Args:
            asset_id: Asset internal id to append label on.
            asset_id_array: List of asset internal ids to append labels on.
            json_response: Label to append.
            json_response_array: List of labels to append.
            model_name: Name of the model that generated the labels.
            project_id: Identifier of the project.
            external_id: Asset external id to append label on.
            external_id_array: List of asset external ids to append labels on.
            disable_tqdm: Disable tqdm progress bar.
            overwrite: when uploading labels, if True,
                it will overwrite existing labels of the same label type on the targeted assets.

        Returns:
            A list of dictionaries with the label ids.
        """
        return self.__create(
            asset_id_array=asset_id_array,
            asset_id=asset_id,
            disable_tqdm=disable_tqdm,
            external_id_array=external_id_array,
            external_id=external_id,
            json_response_array=json_response_array,
            json_response=json_response,
            label_type="INFERENCE",
            model_name=model_name,
            overwrite=bool(overwrite),
            project_id=project_id,
            reviewed_label_id=None,
            reviewed_label_id_array=None,
        )

    @overload
    def delete(
        self,
        *,
        id: str,
        disable_tqdm: Optional[bool] = None,
    ) -> List[str]:
        ...

    @overload
    def delete(
        self,
        *,
        ids: ListOrTuple[str],
        disable_tqdm: Optional[bool] = None,
    ) -> List[str]:
        ...

    @typechecked
    def delete(
        self,
        *,
        id: Optional[str] = None,
        ids: Optional[ListOrTuple[str]] = None,
        disable_tqdm: Optional[bool] = None,
    ) -> List[str]:
        """Delete labels.

        Currently, only `PREDICTION` and `INFERENCE` labels can be deleted.

        Args:
            id: Label id to delete.
            ids: List of label ids to delete.
            disable_tqdm: If `True`, the progress bar will be disabled.

        Returns:
            The deleted label ids.
        """
        # Convert singular to plural
        if id is not None:
            ids = [id]

        assert ids is not None, "ids must be provided"

        return self._client.delete_labels(ids=ids, disable_tqdm=disable_tqdm)

    @typechecked
    def __create_from_geojson(
        self,
        *,
        project_id: str,
        asset_external_id: str,
        geojson_file_paths: List[str],
        job_names: Optional[List[str]] = None,
        category_names: Optional[List[str]] = None,
        label_type: LabelType = "DEFAULT",
        step_name: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> None:
        """Import and convert GeoJSON files into annotations for a specific asset in a Kili project.

        This method processes GeoJSON feature collections, converts them to the appropriate
        Kili annotation format, and appends them as labels to the specified asset.

        Args:
            project_id: The ID of the Kili project to add the labels to.
            asset_external_id: The external ID of the asset to label.
            geojson_file_path: File path to the GeoJSON file to be processed.
            geojson_file_paths: List of file paths to the GeoJSON files to be processed.
            job_name: Job name in the Kili project.
            job_names: Optional list of job names in the Kili project, one for each GeoJSON file.
            category_name: Category name.
            category_names: Optional list of category names, one for each GeoJSON file.
            label_type: Can be one of `AUTOSAVE`, `DEFAULT`, `PREDICTION`, `REVIEW` or `INFERENCE`.
            step_name: Name of the step to which the labels belong.
            model_name: Name of the model that generated the labels.
        """
        return self._client.append_labels_from_geojson_files(
            project_id=project_id,
            asset_external_id=asset_external_id,
            geojson_file_paths=geojson_file_paths,
            job_names=job_names,
            category_names=category_names,
            label_type=label_type,
            step_name=step_name,
            model_name=model_name,
        )

    @typechecked
    def create_default_from_geojson(
        self,
        *,
        project_id: str,
        asset_external_id: str,
        geojson_file_paths: List[str],
        job_names: Optional[List[str]] = None,
        category_names: Optional[List[str]] = None,
        step_name: Optional[str] = None,
    ) -> None:
        """Import and convert GeoJSON files into DEFAULT annotations for a specific asset in a Kili project.

        This method processes GeoJSON feature collections, converts them to the appropriate
        Kili annotation format, and appends them as DEFAULT labels to the specified asset.

        Args:
            project_id: The ID of the Kili project to add the labels to.
            asset_external_id: The external ID of the asset to label.
            geojson_file_paths: List of file paths to the GeoJSON files to be processed.
            job_names: Optional list of job names in the Kili project, one for each GeoJSON file.
            category_names: Optional list of category names, one for each GeoJSON file.
            step_name: Name of the step to which the labels belong.
        """
        return self.__create_from_geojson(
            project_id=project_id,
            asset_external_id=asset_external_id,
            geojson_file_paths=geojson_file_paths,
            job_names=job_names,
            category_names=category_names,
            label_type="DEFAULT",
            step_name=step_name,
        )

    @typechecked
    def create_prediction_from_geojson(
        self,
        *,
        project_id: str,
        asset_external_id: str,
        geojson_file_paths: List[str],
        job_names: Optional[List[str]] = None,
        category_names: Optional[List[str]] = None,
        model_name: Optional[str] = None,
    ) -> None:
        """Import and convert GeoJSON files into PREDICTION annotations for a specific asset in a Kili project.

        This method processes GeoJSON feature collections, converts them to the appropriate
        Kili annotation format, and appends them as PREDICTION labels to the specified asset.

        Args:
            project_id: The ID of the Kili project to add the labels to.
            asset_external_id: The external ID of the asset to label.
            geojson_file_paths: List of file paths to the GeoJSON files to be processed.
            job_names: Optional list of job names in the Kili project, one for each GeoJSON file.
            category_names: Optional list of category names, one for each GeoJSON file.
            model_name: Name of the model that generated the labels.
        """
        return self.__create_from_geojson(
            project_id=project_id,
            asset_external_id=asset_external_id,
            geojson_file_paths=geojson_file_paths,
            job_names=job_names,
            category_names=category_names,
            label_type="PREDICTION",
            model_name=model_name,
        )

    @typechecked
    def create_inference_from_geojson(
        self,
        *,
        project_id: str,
        asset_external_id: str,
        geojson_file_paths: List[str],
        job_names: Optional[List[str]] = None,
        category_names: Optional[List[str]] = None,
        model_name: Optional[str] = None,
    ) -> None:
        """Import and convert GeoJSON files into INFERENCE annotations for a specific asset in a Kili project.

        This method processes GeoJSON feature collections, converts them to the appropriate
        Kili annotation format, and appends them as INFERENCE labels to the specified asset.

        Args:
            project_id: The ID of the Kili project to add the labels to.
            asset_external_id: The external ID of the asset to label.
            geojson_file_paths: List of file paths to the GeoJSON files to be processed.
            job_names: Optional list of job names in the Kili project, one for each GeoJSON file.
            category_names: Optional list of category names, one for each GeoJSON file.
            model_name: Name of the model that generated the labels.
        """
        return self.__create_from_geojson(
            project_id=project_id,
            asset_external_id=asset_external_id,
            geojson_file_paths=geojson_file_paths,
            job_names=job_names,
            category_names=category_names,
            label_type="INFERENCE",
            model_name=model_name,
        )

    @typechecked
    def __create_from_shapefile(
        self,
        *,
        project_id: str,
        asset_external_id: str,
        shapefile_paths: List[str],
        job_names: List[str],
        category_names: List[str],
        from_epsgs: Optional[List[int]] = None,
        label_type: LabelType = "DEFAULT",
        step_name: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> None:
        """Import and convert shapefiles into annotations for a specific asset in a Kili project.

        This method processes shapefile geometries (points, polylines, and polygons), converts them
        to the appropriate Kili annotation format, and appends them as labels to the specified asset.

        Args:
            project_id: The ID of the Kili project to add the labels to.
            asset_external_id: The external ID of the asset to label.
            shapefile_path: File path to the shapefile to be processed.
            shapefile_paths: List of file paths to the shapefiles to be processed.
            job_name: Job name in the Kili project.
            job_names: List of job names in the Kili project, corresponding to each shapefile.
            category_name: Category name.
            category_names: List of category names corresponding to each shapefile.
            from_epsg: EPSG code specifying the coordinate reference system of the shapefile.
            from_epsgs: Optional list of EPSG codes specifying the coordinate reference systems
                       of the shapefiles. If not provided, EPSG:4326 (WGS84) is assumed for all files.
            label_type: Can be one of `AUTOSAVE`, `DEFAULT`, `PREDICTION`, `REVIEW` or `INFERENCE`.
            step_name: Name of the step to which the labels belong.
            model_name: Name of the model that generated the labels.
        """
        return self._client.append_labels_from_shapefiles(
            project_id=project_id,
            asset_external_id=asset_external_id,
            shapefile_paths=shapefile_paths,
            job_names=job_names,
            category_names=category_names,
            from_epsgs=from_epsgs,
            label_type=label_type,
            step_name=step_name,
            model_name=model_name,
        )

    @typechecked
    def create_default_from_shapefile(
        self,
        *,
        project_id: str,
        asset_external_id: str,
        shapefile_paths: List[str],
        job_names: List[str],
        category_names: List[str],
        from_epsgs: Optional[List[int]] = None,
        step_name: Optional[str] = None,
    ) -> None:
        """Import and convert shapefiles into DEFAULT annotations for a specific asset in a Kili project.

        This method processes shapefile geometries (points, polylines, and polygons), converts them
        to the appropriate Kili annotation format, and appends them as DEFAULT labels to the specified asset.

        Args:
            project_id: The ID of the Kili project to add the labels to.
            asset_external_id: The external ID of the asset to label.
            shapefile_paths: List of file paths to the shapefiles to be processed.
            job_names: List of job names in the Kili project, corresponding to each shapefile.
            category_names: List of category names corresponding to each shapefile.
            from_epsgs: Optional list of EPSG codes specifying the coordinate reference systems
                       of the shapefiles. If not provided, EPSG:4326 (WGS84) is assumed for all files.
            step_name: Name of the step to which the labels belong.
        """
        return self.__create_from_shapefile(
            project_id=project_id,
            asset_external_id=asset_external_id,
            shapefile_paths=shapefile_paths,
            job_names=job_names,
            category_names=category_names,
            from_epsgs=from_epsgs,
            label_type="DEFAULT",
            step_name=step_name,
        )

    @typechecked
    def create_prediction_from_shapefile(
        self,
        *,
        project_id: str,
        asset_external_id: str,
        shapefile_paths: List[str],
        job_names: List[str],
        category_names: List[str],
        from_epsgs: Optional[List[int]] = None,
        model_name: Optional[str] = None,
    ) -> None:
        """Import and convert shapefiles into PREDICTION annotations for a specific asset in a Kili project.

        This method processes shapefile geometries (points, polylines, and polygons), converts them
        to the appropriate Kili annotation format, and appends them as PREDICTION labels to the specified asset.

        Args:
            project_id: The ID of the Kili project to add the labels to.
            asset_external_id: The external ID of the asset to label.
            shapefile_paths: List of file paths to the shapefiles to be processed.
            job_names: List of job names in the Kili project, corresponding to each shapefile.
            category_names: List of category names corresponding to each shapefile.
            from_epsgs: Optional list of EPSG codes specifying the coordinate reference systems
                       of the shapefiles. If not provided, EPSG:4326 (WGS84) is assumed for all files.
            model_name: Name of the model that generated the labels.
        """
        return self.__create_from_shapefile(
            project_id=project_id,
            asset_external_id=asset_external_id,
            shapefile_paths=shapefile_paths,
            job_names=job_names,
            category_names=category_names,
            from_epsgs=from_epsgs,
            label_type="PREDICTION",
            model_name=model_name,
        )

    @typechecked
    def create_inference_from_shapefile(
        self,
        *,
        project_id: str,
        asset_external_id: str,
        shapefile_paths: List[str],
        job_names: List[str],
        category_names: List[str],
        from_epsgs: Optional[List[int]] = None,
        model_name: Optional[str] = None,
    ) -> None:
        """Import and convert shapefiles into INFERENCE annotations for a specific asset in a Kili project.

        This method processes shapefile geometries (points, polylines, and polygons), converts them
        to the appropriate Kili annotation format, and appends them as INFERENCE labels to the specified asset.

        Args:
            project_id: The ID of the Kili project to add the labels to.
            asset_external_id: The external ID of the asset to label.
            shapefile_paths: List of file paths to the shapefiles to be processed.
            job_names: List of job names in the Kili project, corresponding to each shapefile.
            category_names: List of category names corresponding to each shapefile.
            from_epsgs: Optional list of EPSG codes specifying the coordinate reference systems
                       of the shapefiles. If not provided, EPSG:4326 (WGS84) is assumed for all files.
            model_name: Name of the model that generated the labels.
        """
        return self.__create_from_shapefile(
            project_id=project_id,
            asset_external_id=asset_external_id,
            shapefile_paths=shapefile_paths,
            job_names=job_names,
            category_names=category_names,
            from_epsgs=from_epsgs,
            label_type="INFERENCE",
            model_name=model_name,
        )

    @overload
    def create_prediction(
        self,
        *,
        project_id: str,
        asset_id: str,
        json_response: dict,
        model_name: str,
        overwrite: bool = False,
    ) -> Dict[Literal["id"], str]:
        ...

    @overload
    def create_prediction(
        self,
        *,
        project_id: str,
        asset_id_array: List[str],
        json_response_array: List[dict],
        model_name: str,
        disable_tqdm: Optional[bool] = None,
        overwrite: bool = False,
    ) -> Dict[Literal["id"], str]:
        ...

    @overload
    def create_prediction(
        self,
        *,
        project_id: str,
        external_id: str,
        json_response: dict,
        model_name: str,
        overwrite: bool = False,
    ) -> Dict[Literal["id"], str]:
        ...

    @overload
    def create_prediction(
        self,
        *,
        project_id: str,
        external_id_array: List[str],
        json_response_array: List[dict],
        model_name: str,
        disable_tqdm: Optional[bool] = None,
        overwrite: bool = False,
    ) -> Dict[Literal["id"], str]:
        ...

    @typechecked
    def create_prediction(
        self,
        *,
        project_id: str,
        model_name: str,
        external_id: Optional[str] = None,
        external_id_array: Optional[List[str]] = None,
        json_response: Optional[dict] = None,
        json_response_array: Optional[List[dict]] = None,
        asset_id: Optional[str] = None,
        asset_id_array: Optional[List[str]] = None,
        disable_tqdm: Optional[bool] = None,
        overwrite: bool = False,
    ) -> Dict[Literal["id"], str]:
        """Create prediction for specific assets.

        Args:
            project_id: Identifier of the project.
            external_id: The external ID of the asset for which we want to add prediction.
            external_id_array: The external IDs of the assets for which we want to add predictions.
            json_response: The prediction.
            json_response_array: The predictions are given here.
            model_name: The name of the model that generated the predictions.
            asset_id: The internal ID of the asset for which we want to add prediction.
            asset_id_array: The internal IDs of the assets for which we want to add predictions.
            disable_tqdm: Disable tqdm progress bar.
            overwrite: if True, it will overwrite existing predictions of
                the same model name on the targeted assets.

        Returns:
            A dictionary with the project `id`.
        """
        # Convert singular to plural
        if external_id is not None:
            external_id_array = [external_id]
        if json_response is not None:
            json_response_array = [json_response]
        if asset_id is not None:
            asset_id_array = [asset_id]

        return self._client.create_predictions(
            asset_id_array=asset_id_array,
            disable_tqdm=disable_tqdm,
            external_id_array=external_id_array,
            json_response_array=json_response_array,
            model_name=model_name,
            overwrite=overwrite,
            project_id=project_id,
        )
