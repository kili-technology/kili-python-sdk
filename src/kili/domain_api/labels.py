"""Labels domain namespace for the Kili Python SDK.

This module provides a comprehensive interface for label-related operations
including creation, querying, management, and event handling.
"""
# pylint: disable=too-many-lines

from functools import cached_property
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    Literal,
    Optional,
    Union,
    overload,
)

from typeguard import typechecked

from kili.domain.asset import AssetStatus
from kili.domain.asset.asset import StatusInStep
from kili.domain.label import LabelType
from kili.domain.types import ListOrTuple
from kili.domain_api.base import DomainNamespace
from kili.services.export.types import CocoAnnotationModifier, LabelFormat, SplitOption
from kili.utils.labels.parsing import ParsedLabel

if TYPE_CHECKING:
    from kili.client import Kili as KiliLegacy


class PredictionsNamespace:
    """Nested namespace for prediction-related operations."""

    def __init__(self, parent: "LabelsNamespace") -> None:
        """Initialize predictions namespace.

        Args:
            parent: The parent LabelsNamespace instance
        """
        self._parent = parent

    @typechecked
    def create(
        self,
        project_id: str,
        external_id_array: Optional[List[str]] = None,
        model_name_array: Optional[List[str]] = None,
        json_response_array: Optional[List[dict]] = None,
        model_name: Optional[str] = None,
        asset_id_array: Optional[List[str]] = None,
        disable_tqdm: Optional[bool] = None,
        overwrite: bool = False,
    ) -> Dict[Literal["id"], str]:
        """Create predictions for specific assets.

        Args:
            project_id: Identifier of the project.
            external_id_array: The external IDs of the assets for which we want to add predictions.
            model_name_array: Deprecated, use `model_name` instead.
            json_response_array: The predictions are given here.
            model_name: The name of the model that generated the predictions
            asset_id_array: The internal IDs of the assets for which we want to add predictions.
            disable_tqdm: Disable tqdm progress bar.
            overwrite: if True, it will overwrite existing predictions of
                the same model name on the targeted assets.

        Returns:
            A dictionary with the project `id`.
        """
        # Call the client method directly to bypass namespace routing
        return self._parent.client.create_predictions(
            project_id=project_id,
            external_id_array=external_id_array,
            model_name_array=model_name_array,
            json_response_array=json_response_array,
            model_name=model_name,
            asset_id_array=asset_id_array,
            disable_tqdm=disable_tqdm,
            overwrite=overwrite,
        )

    @overload
    def list(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[ListOrTuple[AssetStatus]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        asset_step_name_in: Optional[List[str]] = None,
        asset_step_status_in: Optional[List[StatusInStep]] = None,
        author_in: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
        fields: ListOrTuple[str] = (
            "author.email",
            "author.id",
            "id",
            "jsonResponse",
            "labelType",
            "modelName",
        ),
        first: Optional[int] = None,
        honeypot_mark_gte: Optional[float] = None,
        honeypot_mark_lte: Optional[float] = None,
        id_contains: Optional[List[str]] = None,
        label_id: Optional[str] = None,
        skip: int = 0,
        user_id: Optional[str] = None,
        disable_tqdm: Optional[bool] = None,
        category_search: Optional[str] = None,
        *,
        as_generator: Literal[True],
    ) -> Generator[Dict, None, None]:
        ...

    @overload
    def list(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[ListOrTuple[AssetStatus]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        asset_step_name_in: Optional[List[str]] = None,
        asset_step_status_in: Optional[List[StatusInStep]] = None,
        author_in: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
        fields: ListOrTuple[str] = (
            "author.email",
            "author.id",
            "id",
            "jsonResponse",
            "labelType",
            "modelName",
        ),
        first: Optional[int] = None,
        honeypot_mark_gte: Optional[float] = None,
        honeypot_mark_lte: Optional[float] = None,
        id_contains: Optional[List[str]] = None,
        label_id: Optional[str] = None,
        skip: int = 0,
        user_id: Optional[str] = None,
        disable_tqdm: Optional[bool] = None,
        category_search: Optional[str] = None,
        *,
        as_generator: Literal[False] = False,
    ) -> List[Dict]:
        ...

    @typechecked
    def list(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[ListOrTuple[AssetStatus]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        asset_step_name_in: Optional[List[str]] = None,
        asset_step_status_in: Optional[List[StatusInStep]] = None,
        author_in: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
        fields: ListOrTuple[str] = (
            "author.email",
            "author.id",
            "id",
            "jsonResponse",
            "labelType",
            "modelName",
        ),
        first: Optional[int] = None,
        honeypot_mark_gte: Optional[float] = None,
        honeypot_mark_lte: Optional[float] = None,
        id_contains: Optional[List[str]] = None,
        label_id: Optional[str] = None,
        skip: int = 0,
        user_id: Optional[str] = None,
        disable_tqdm: Optional[bool] = None,
        category_search: Optional[str] = None,
        *,
        as_generator: bool = False,
    ) -> Iterable[Dict]:
        """Get prediction labels from a project based on a set of criteria.

        This method is equivalent to the `labels()` method, but it only returns labels of type "PREDICTION".

        Args:
            project_id: Identifier of the project.
            asset_id: Identifier of the asset.
            asset_status_in: Returned labels should have a status that belongs to that list, if given.
            asset_external_id_in: Returned labels should have an external id that belongs to that list, if given.
            asset_step_name_in: Returned assets are in a step whose name belong to that list, if given.
            asset_step_status_in: Returned assets have the status of their step that belongs to that list, if given.
            author_in: Returned labels should have been made by authors in that list, if given.
            created_at: Returned labels should have a label whose creation date is equal to this date.
            created_at_gte: Returned labels should have a label whose creation date is greater than this date.
            created_at_lte: Returned labels should have a label whose creation date is lower than this date.
            fields: All the fields to request among the possible fields for the labels.
            first: Maximum number of labels to return.
            honeypot_mark_gte: Returned labels should have a label whose honeypot is greater than this number.
            honeypot_mark_lte: Returned labels should have a label whose honeypot is lower than this number.
            id_contains: Filters out labels not belonging to that list. If empty, no filtering is applied.
            label_id: Identifier of the label.
            skip: Number of labels to skip (they are ordered by their date of creation, first to last).
            user_id: Identifier of the user.
            disable_tqdm: If `True`, the progress bar will be disabled
            as_generator: If `True`, a generator on the labels is returned.
            category_search: Query to filter labels based on the content of their jsonResponse

        Returns:
            An iterable of labels.
        """
        # Call the client method directly to bypass namespace routing
        return self._parent.client.predictions(
            project_id=project_id,
            asset_id=asset_id,
            asset_status_in=asset_status_in,
            asset_external_id_in=asset_external_id_in,
            asset_step_name_in=asset_step_name_in,
            asset_step_status_in=asset_step_status_in,
            author_in=author_in,
            created_at=created_at,
            created_at_gte=created_at_gte,
            created_at_lte=created_at_lte,
            fields=fields,
            first=first,
            honeypot_mark_gte=honeypot_mark_gte,
            honeypot_mark_lte=honeypot_mark_lte,
            id_contains=id_contains,
            label_id=label_id,
            skip=skip,
            user_id=user_id,
            disable_tqdm=disable_tqdm,
            category_search=category_search,
            as_generator=as_generator,  # pyright: ignore[reportGeneralTypeIssues]
        )


class InferencesNamespace:
    """Nested namespace for inference-related operations."""

    def __init__(self, parent: "LabelsNamespace") -> None:
        """Initialize inferences namespace.

        Args:
            parent: The parent LabelsNamespace instance
        """
        self._parent = parent

    @overload
    def list(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[ListOrTuple[AssetStatus]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        asset_step_name_in: Optional[List[str]] = None,
        asset_step_status_in: Optional[List[StatusInStep]] = None,
        author_in: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
        fields: ListOrTuple[str] = (
            "author.email",
            "author.id",
            "id",
            "jsonResponse",
            "labelType",
            "modelName",
        ),
        first: Optional[int] = None,
        honeypot_mark_gte: Optional[float] = None,
        honeypot_mark_lte: Optional[float] = None,
        id_contains: Optional[List[str]] = None,
        label_id: Optional[str] = None,
        skip: int = 0,
        user_id: Optional[str] = None,
        disable_tqdm: Optional[bool] = None,
        category_search: Optional[str] = None,
        *,
        as_generator: Literal[True],
    ) -> Generator[Dict, None, None]:
        ...

    @overload
    def list(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[ListOrTuple[AssetStatus]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        asset_step_name_in: Optional[List[str]] = None,
        asset_step_status_in: Optional[List[StatusInStep]] = None,
        author_in: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
        fields: ListOrTuple[str] = (
            "author.email",
            "author.id",
            "id",
            "jsonResponse",
            "labelType",
            "modelName",
        ),
        first: Optional[int] = None,
        honeypot_mark_gte: Optional[float] = None,
        honeypot_mark_lte: Optional[float] = None,
        id_contains: Optional[List[str]] = None,
        label_id: Optional[str] = None,
        skip: int = 0,
        user_id: Optional[str] = None,
        disable_tqdm: Optional[bool] = None,
        category_search: Optional[str] = None,
        *,
        as_generator: Literal[False] = False,
    ) -> List[Dict]:
        ...

    @typechecked
    def list(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[ListOrTuple[AssetStatus]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        asset_step_name_in: Optional[List[str]] = None,
        asset_step_status_in: Optional[List[StatusInStep]] = None,
        author_in: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
        fields: ListOrTuple[str] = (
            "author.email",
            "author.id",
            "id",
            "jsonResponse",
            "labelType",
            "modelName",
        ),
        first: Optional[int] = None,
        honeypot_mark_gte: Optional[float] = None,
        honeypot_mark_lte: Optional[float] = None,
        id_contains: Optional[List[str]] = None,
        label_id: Optional[str] = None,
        skip: int = 0,
        user_id: Optional[str] = None,
        disable_tqdm: Optional[bool] = None,
        category_search: Optional[str] = None,
        *,
        as_generator: bool = False,
    ) -> Iterable[Dict]:
        """Get inference labels from a project based on a set of criteria.

        This method is equivalent to the `labels()` method, but it only returns labels of type "INFERENCE".

        Args:
            project_id: Identifier of the project.
            asset_id: Identifier of the asset.
            asset_status_in: Returned labels should have a status that belongs to that list, if given.
            asset_external_id_in: Returned labels should have an external id that belongs to that list, if given.
            asset_step_name_in: Returned assets are in a step whose name belong to that list, if given.
            asset_step_status_in: Returned assets have the status of their step that belongs to that list, if given.
            author_in: Returned labels should have been made by authors in that list, if given.
            created_at: Returned labels should have a label whose creation date is equal to this date.
            created_at_gte: Returned labels should have a label whose creation date is greater than this date.
            created_at_lte: Returned labels should have a label whose creation date is lower than this date.
            fields: All the fields to request among the possible fields for the labels.
            first: Maximum number of labels to return.
            honeypot_mark_gte: Returned labels should have a label whose honeypot is greater than this number.
            honeypot_mark_lte: Returned labels should have a label whose honeypot is lower than this number.
            id_contains: Filters out labels not belonging to that list. If empty, no filtering is applied.
            label_id: Identifier of the label.
            skip: Number of labels to skip (they are ordered by their date of creation, first to last).
            user_id: Identifier of the user.
            disable_tqdm: If `True`, the progress bar will be disabled
            as_generator: If `True`, a generator on the labels is returned.
            category_search: Query to filter labels based on the content of their jsonResponse

        Returns:
            An iterable of inference labels.
        """
        # Call the client method directly to bypass namespace routing
        return self._parent.client.inferences(
            project_id=project_id,
            asset_id=asset_id,
            asset_status_in=asset_status_in,
            asset_external_id_in=asset_external_id_in,
            asset_step_name_in=asset_step_name_in,
            asset_step_status_in=asset_step_status_in,
            author_in=author_in,
            created_at=created_at,
            created_at_gte=created_at_gte,
            created_at_lte=created_at_lte,
            fields=fields,
            first=first,
            honeypot_mark_gte=honeypot_mark_gte,
            honeypot_mark_lte=honeypot_mark_lte,
            id_contains=id_contains,
            label_id=label_id,
            skip=skip,
            user_id=user_id,
            disable_tqdm=disable_tqdm,
            category_search=category_search,
            as_generator=as_generator,  # pyright: ignore[reportGeneralTypeIssues]
        )


class HoneypotsNamespace:
    """Nested namespace for honeypot-related operations."""

    def __init__(self, parent: "LabelsNamespace") -> None:
        """Initialize honeypots namespace.

        Args:
            parent: The parent LabelsNamespace instance
        """
        self._parent = parent

    @typechecked
    def create(
        self,
        json_response: dict,
        asset_external_id: Optional[str] = None,
        asset_id: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> Dict:
        """Create honeypot for an asset.

        Uses the given `json_response` to create a `REVIEW` label.
        This enables Kili to compute a `honeypotMark`,
        which measures the similarity between this label and other labels.

        Args:
            json_response: The JSON response of the honeypot label of the asset.
            asset_id: Identifier of the asset.
                Either provide `asset_id` or `asset_external_id` and `project_id`.
            asset_external_id: External identifier of the asset.
                Either provide `asset_id` or `asset_external_id` and `project_id`.
            project_id: Identifier of the project.
                Either provide `asset_id` or `asset_external_id` and `project_id`.

        Returns:
            A dictionary-like object representing the created label.
        """
        # Call the client method directly to bypass namespace routing
        return self._parent.client.create_honeypot(
            json_response=json_response,
            asset_external_id=asset_external_id,
            asset_id=asset_id,
            project_id=project_id,
        )


class EventsNamespace:
    """Nested namespace for event-related operations."""

    def __init__(self, parent: "LabelsNamespace") -> None:
        """Initialize events namespace.

        Args:
            parent: The parent LabelsNamespace instance
        """
        self._parent = parent

    def on_change(
        self,
        project_id: str,
        callback: Callable[[Dict], None],
        **kwargs: Any,
    ) -> None:
        """Subscribe to label change events for a project.

        This method sets up a WebSocket subscription to listen for label creation
        and update events in real-time.

        Args:
            project_id: The project ID to monitor for label changes
            callback: Function to call when a label change event occurs.
                     The callback receives the label data as a dictionary.
            **kwargs: Additional arguments for the subscription (e.g., filters)

        Examples:
            >>> def handle_label_change(label_data):
            ...     print(f"Label changed: {label_data['id']}")
            >>>
            >>> labels.events.on_change(
            ...     project_id="project_123",
            ...     callback=handle_label_change
            ... )

        Note:
            This is a placeholder implementation. The actual WebSocket subscription
            functionality would need to be implemented using the GraphQL subscription
            infrastructure found in the codebase.
        """
        # TODO: Implement WebSocket subscription using GraphQL subscriptions
        # This would use the GQL_LABEL_CREATED_OR_UPDATED subscription
        # and the WebSocket GraphQL client
        raise NotImplementedError(
            "Label change event subscription is not yet implemented. "
            "This requires WebSocket subscription infrastructure."
        )


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

    @cached_property
    def predictions(self) -> PredictionsNamespace:
        """Access prediction-related operations.

        Returns:
            PredictionsNamespace instance for prediction operations
        """
        return PredictionsNamespace(self)

    @cached_property
    def inferences(self) -> InferencesNamespace:
        """Access inference-related operations.

        Returns:
            InferencesNamespace instance for inference operations
        """
        return InferencesNamespace(self)

    @cached_property
    def honeypots(self) -> HoneypotsNamespace:
        """Access honeypot-related operations.

        Returns:
            HoneypotsNamespace instance for honeypot operations
        """
        return HoneypotsNamespace(self)

    @cached_property
    def events(self) -> EventsNamespace:
        """Access event-related operations.

        Returns:
            EventsNamespace instance for event operations
        """
        return EventsNamespace(self)

    @overload
    def list(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[ListOrTuple[AssetStatus]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        asset_external_id_strictly_in: Optional[List[str]] = None,
        asset_step_name_in: Optional[List[str]] = None,
        asset_step_status_in: Optional[List[StatusInStep]] = None,
        author_in: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
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
        honeypot_mark_gte: Optional[float] = None,
        honeypot_mark_lte: Optional[float] = None,
        id_contains: Optional[List[str]] = None,
        label_id: Optional[str] = None,
        skip: int = 0,
        type_in: Optional[List[LabelType]] = None,
        user_id: Optional[str] = None,
        disable_tqdm: Optional[bool] = None,
        category_search: Optional[str] = None,
        output_format: Literal["dict"] = "dict",
        *,
        as_generator: Literal[True],
    ) -> Generator[Dict, None, None]:
        ...

    @overload
    def list(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[ListOrTuple[AssetStatus]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        asset_external_id_strictly_in: Optional[List[str]] = None,
        asset_step_name_in: Optional[List[str]] = None,
        asset_step_status_in: Optional[List[StatusInStep]] = None,
        author_in: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
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
        honeypot_mark_gte: Optional[float] = None,
        honeypot_mark_lte: Optional[float] = None,
        id_contains: Optional[List[str]] = None,
        label_id: Optional[str] = None,
        skip: int = 0,
        type_in: Optional[List[LabelType]] = None,
        user_id: Optional[str] = None,
        disable_tqdm: Optional[bool] = None,
        category_search: Optional[str] = None,
        output_format: Literal["dict"] = "dict",
        *,
        as_generator: Literal[False] = False,
    ) -> List[Dict]:
        ...

    @overload
    def list(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[ListOrTuple[AssetStatus]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        asset_external_id_strictly_in: Optional[List[str]] = None,
        asset_step_name_in: Optional[List[str]] = None,
        asset_step_status_in: Optional[List[StatusInStep]] = None,
        author_in: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
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
        honeypot_mark_gte: Optional[float] = None,
        honeypot_mark_lte: Optional[float] = None,
        id_contains: Optional[List[str]] = None,
        label_id: Optional[str] = None,
        skip: int = 0,
        type_in: Optional[List[LabelType]] = None,
        user_id: Optional[str] = None,
        disable_tqdm: Optional[bool] = None,
        category_search: Optional[str] = None,
        output_format: Literal["parsed_label"] = "parsed_label",
        *,
        as_generator: Literal[False] = False,
    ) -> List[ParsedLabel]:
        ...

    @overload
    def list(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[ListOrTuple[AssetStatus]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        asset_external_id_strictly_in: Optional[List[str]] = None,
        asset_step_name_in: Optional[List[str]] = None,
        asset_step_status_in: Optional[List[StatusInStep]] = None,
        author_in: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
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
        honeypot_mark_gte: Optional[float] = None,
        honeypot_mark_lte: Optional[float] = None,
        id_contains: Optional[List[str]] = None,
        label_id: Optional[str] = None,
        skip: int = 0,
        type_in: Optional[List[LabelType]] = None,
        user_id: Optional[str] = None,
        disable_tqdm: Optional[bool] = None,
        category_search: Optional[str] = None,
        output_format: Literal["parsed_label"] = "parsed_label",
        *,
        as_generator: Literal[True] = True,
    ) -> Generator[ParsedLabel, None, None]:
        ...

    @typechecked
    def list(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[ListOrTuple[AssetStatus]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        asset_external_id_strictly_in: Optional[List[str]] = None,
        asset_step_name_in: Optional[List[str]] = None,
        asset_step_status_in: Optional[List[StatusInStep]] = None,
        author_in: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
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
        honeypot_mark_gte: Optional[float] = None,
        honeypot_mark_lte: Optional[float] = None,
        id_contains: Optional[List[str]] = None,
        label_id: Optional[str] = None,
        skip: int = 0,
        type_in: Optional[List[LabelType]] = None,
        user_id: Optional[str] = None,
        disable_tqdm: Optional[bool] = None,
        category_search: Optional[str] = None,
        output_format: Literal["dict", "parsed_label"] = "dict",
        *,
        as_generator: bool = False,
    ) -> Iterable[Union[Dict, ParsedLabel]]:
        """Get a label list or a label generator from a project based on a set of criteria.

        Args:
            project_id: Identifier of the project.
            asset_id: Identifier of the asset.
            asset_status_in: Returned labels should have a status that belongs to that list, if given.
            asset_external_id_in: Returned labels should have an external id that belongs to that list, if given.
            asset_external_id_strictly_in: Returned labels should have an external id that
                exactly matches one of the ids in that list, if given.
            asset_step_name_in: Returned assets are in a step whose name belong to that list, if given.
            asset_step_status_in: Returned assets have the status of their step that belongs to that list, if given.
            author_in: Returned labels should have been made by authors in that list, if given.
            created_at: Returned labels should have their creation date equal to this date.
            created_at_gte: Returned labels should have their creation date greater or equal to this date.
            created_at_lte: Returned labels should have their creation date lower or equal to this date.
            fields: All the fields to request among the possible fields for the labels.
            first: Maximum number of labels to return.
            honeypot_mark_gte: Returned labels should have a label whose honeypot is greater than this number.
            honeypot_mark_lte: Returned labels should have a label whose honeypot is lower than this number.
            id_contains: Filters out labels not belonging to that list. If empty, no filtering is applied.
            label_id: Identifier of the label.
            skip: Number of labels to skip (they are ordered by their date of creation, first to last).
            type_in: Returned labels should have a label whose type belongs to that list, if given.
            user_id: Identifier of the user.
            disable_tqdm: If `True`, the progress bar will be disabled.
            as_generator: If `True`, a generator on the labels is returned.
            category_search: Query to filter labels based on the content of their jsonResponse.
            output_format: If `dict`, the output is an iterable of Python dictionaries.
                If `parsed_label`, the output is an iterable of parsed labels objects.

        Returns:
            An iterable of labels.
        """
        # Use super() to bypass namespace routing and call the legacy method directly
        return self.client.labels(
            project_id=project_id,
            asset_id=asset_id,
            asset_status_in=asset_status_in,
            asset_external_id_in=asset_external_id_in,
            asset_external_id_strictly_in=asset_external_id_strictly_in,
            asset_step_name_in=asset_step_name_in,
            asset_step_status_in=asset_step_status_in,
            author_in=author_in,
            created_at=created_at,
            created_at_gte=created_at_gte,
            created_at_lte=created_at_lte,
            fields=fields,
            first=first,
            honeypot_mark_gte=honeypot_mark_gte,
            honeypot_mark_lte=honeypot_mark_lte,
            id_contains=id_contains,
            label_id=label_id,
            skip=skip,
            type_in=type_in,
            user_id=user_id,
            disable_tqdm=disable_tqdm,
            category_search=category_search,
            output_format=output_format,  # pyright: ignore[reportGeneralTypeIssues]
            as_generator=as_generator,  # pyright: ignore[reportGeneralTypeIssues]
        )

    @typechecked
    def count(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[List[AssetStatus]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        asset_external_id_strictly_in: Optional[List[str]] = None,
        asset_step_name_in: Optional[List[str]] = None,
        asset_step_status_in: Optional[List[StatusInStep]] = None,
        author_in: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
        honeypot_mark_gte: Optional[float] = None,
        honeypot_mark_lte: Optional[float] = None,
        label_id: Optional[str] = None,
        type_in: Optional[List[LabelType]] = None,
        user_id: Optional[str] = None,
        category_search: Optional[str] = None,
        id_contains: Optional[List[str]] = None,
    ) -> int:
        """Get the number of labels for the given parameters.

        Args:
            project_id: Identifier of the project.
            asset_id: Identifier of the asset.
            asset_status_in: Returned labels should have a status that belongs to that list, if given.
            asset_external_id_in: Returned labels should have an external id that belongs to that list, if given.
            asset_external_id_strictly_in: Returned labels should have an external id that
                exactly matches one of the ids in that list, if given.
            asset_step_name_in: Returned assets are in a step whose name belong to that list, if given.
            asset_step_status_in: Returned assets have the status of their step that belongs to that list, if given.
            author_in: Returned labels should have been made by authors in that list, if given.
            created_at: Returned labels should have a label whose creation date is equal to this date.
            created_at_gte: Returned labels should have a label whose creation date is greater than this date.
            created_at_lte: Returned labels should have a label whose creation date is lower than this date.
            honeypot_mark_gte: Returned labels should have a label whose honeypot is greater than this number.
            honeypot_mark_lte: Returned labels should have a label whose honeypot is lower than this number.
            label_id: Identifier of the label.
            type_in: Returned labels should have a label whose type belongs to that list, if given.
            user_id: Identifier of the user.
            category_search: Query to filter labels based on the content of their jsonResponse
            id_contains: Filters out labels not belonging to that list. If empty, no filtering is applied.

        Returns:
            The number of labels with the parameters provided
        """
        # Use super() to bypass namespace routing and call the legacy method directly
        return self.client.count_labels(
            project_id=project_id,
            asset_id=asset_id,
            asset_status_in=asset_status_in,
            asset_external_id_in=asset_external_id_in,
            asset_external_id_strictly_in=asset_external_id_strictly_in,
            asset_step_name_in=asset_step_name_in,
            asset_step_status_in=asset_step_status_in,
            author_in=author_in,
            created_at=created_at,
            created_at_gte=created_at_gte,
            created_at_lte=created_at_lte,
            honeypot_mark_gte=honeypot_mark_gte,
            honeypot_mark_lte=honeypot_mark_lte,
            label_id=label_id,
            type_in=type_in,
            user_id=user_id,
            category_search=category_search,
            id_contains=id_contains,
        )

    @typechecked
    def create(
        self,
        asset_id_array: Optional[List[str]] = None,
        json_response_array: ListOrTuple[Dict] = (),
        author_id_array: Optional[List[str]] = None,
        seconds_to_label_array: Optional[List[int]] = None,
        model_name: Optional[str] = None,
        label_type: LabelType = "DEFAULT",
        project_id: Optional[str] = None,
        external_id_array: Optional[List[str]] = None,
        disable_tqdm: Optional[bool] = None,
        overwrite: bool = False,
        step_name: Optional[str] = None,
    ) -> List[Dict[Literal["id"], str]]:
        """Create labels to assets.

        Args:
            asset_id_array: list of asset internal ids to append labels on.
            json_response_array: list of labels to append.
            author_id_array: list of the author id of the labels.
            seconds_to_label_array: list of times taken to produce the label, in seconds.
            model_name: Name of the model that generated the labels.
                Only useful when uploading PREDICTION or INFERENCE labels.
            label_type: Can be one of `AUTOSAVE`, `DEFAULT`, `PREDICTION`, `REVIEW` or `INFERENCE`.
            project_id: Identifier of the project.
            external_id_array: list of asset external ids to append labels on.
            disable_tqdm: Disable tqdm progress bar.
            overwrite: when uploading prediction or inference labels, if True,
                it will overwrite existing labels with the same model name
                and of the same label type, on the targeted assets.
            step_name: Name of the step to which the labels belong.
                The label_type must match accordingly.

        Returns:
            A list of dictionaries with the label ids.
        """
        # Use super() to bypass namespace routing and call the legacy method directly
        return self.client.append_labels(
            asset_id_array=asset_id_array,
            json_response_array=json_response_array,
            author_id_array=author_id_array,
            seconds_to_label_array=seconds_to_label_array,
            model_name=model_name,
            label_type=label_type,
            project_id=project_id,
            asset_external_id_array=external_id_array,
            disable_tqdm=disable_tqdm,
            overwrite=overwrite,
            step_name=step_name,
        )

    @typechecked
    def delete(
        self,
        ids: ListOrTuple[str],
        disable_tqdm: Optional[bool] = None,
    ) -> List[str]:
        """Delete labels.

        Currently, only `PREDICTION` and `INFERENCE` labels can be deleted.

        Args:
            ids: List of label ids to delete.
            disable_tqdm: If `True`, the progress bar will be disabled.

        Returns:
            The deleted label ids.
        """
        # Use super() to bypass namespace routing and call the legacy method directly
        return self.client.delete_labels(ids=ids, disable_tqdm=disable_tqdm)

    def export(
        self,
        project_id: str,
        filename: Optional[str],
        fmt: LabelFormat,
        asset_ids: Optional[List[str]] = None,
        layout: SplitOption = "split",
        single_file: bool = False,
        disable_tqdm: Optional[bool] = None,
        with_assets: bool = True,
        external_ids: Optional[List[str]] = None,
        annotation_modifier: Optional[CocoAnnotationModifier] = None,
        asset_filter_kwargs: Optional[Dict[str, Any]] = None,
        normalized_coordinates: Optional[bool] = None,
        label_type_in: Optional[List[str]] = None,
        include_sent_back_labels: Optional[bool] = None,
    ) -> Optional[List[Dict[str, Union[List[str], str]]]]:
        """Export the project labels with the requested format into the requested output path.

        Args:
            project_id: Identifier of the project.
            filename: Relative or full path of the archive that will contain
                the exported data.
            fmt: Format of the exported labels.
            asset_ids: Optional list of the assets internal IDs from which to export the labels.
            layout: Layout of the exported files. "split" means there is one folder
                per job, "merged" that there is one folder with every labels.
            single_file: Layout of the exported labels. Single file mode is
                only available for some specific formats (COCO and Kili).
            disable_tqdm: Disable the progress bar if True.
            with_assets: Download the assets in the export.
            external_ids: Optional list of the assets external IDs from which to export the labels.
            annotation_modifier: (For COCO export only) function that takes the COCO annotation, the
                COCO image, and the Kili annotation, and should return an updated COCO annotation.
            asset_filter_kwargs: Optional dictionary of arguments to pass to `kili.assets()`
                in order to filter the assets the labels are exported from.
            normalized_coordinates: This parameter is only effective on the Kili (a.k.a raw) format.
                If True, the coordinates of the `(x, y)` vertices are normalized between 0 and 1.
                If False, the json response will contain additional fields with coordinates in
                absolute values, that is, in pixels.
            label_type_in: Optional list of label type. Exported assets should have a label
                whose type belongs to that list.
                By default, only `DEFAULT` and `REVIEW` labels are exported.
            include_sent_back_labels: If True, the export will include the labels that have been sent back.

        Returns:
            Export information or None if export failed.
        """
        # Use super() to bypass namespace routing and call the legacy method directly
        return self.client.export_labels(
            project_id=project_id,
            filename=filename,
            fmt=fmt,
            asset_ids=asset_ids,
            layout=layout,
            single_file=single_file,
            disable_tqdm=disable_tqdm,
            with_assets=with_assets,
            external_ids=external_ids,
            annotation_modifier=annotation_modifier,
            asset_filter_kwargs=asset_filter_kwargs,
            normalized_coordinates=normalized_coordinates,
            label_type_in=label_type_in,
            include_sent_back_labels=include_sent_back_labels,
        )

    @typechecked
    def append(
        self,
        asset_id_array: Optional[List[str]] = None,
        json_response_array: ListOrTuple[Dict] = (),
        author_id_array: Optional[List[str]] = None,
        seconds_to_label_array: Optional[List[int]] = None,
        model_name: Optional[str] = None,
        label_type: LabelType = "DEFAULT",
        project_id: Optional[str] = None,
        external_id_array: Optional[List[str]] = None,
        disable_tqdm: Optional[bool] = None,
        overwrite: bool = False,
        step_name: Optional[str] = None,
    ) -> List[Dict[Literal["id"], str]]:
        """Append labels to assets.

        This is an alias for the `create` method to maintain compatibility.

        Args:
            asset_id_array: list of asset internal ids to append labels on.
            json_response_array: list of labels to append.
            author_id_array: list of the author id of the labels.
            seconds_to_label_array: list of times taken to produce the label, in seconds.
            model_name: Name of the model that generated the labels.
                Only useful when uploading PREDICTION or INFERENCE labels.
            label_type: Can be one of `AUTOSAVE`, `DEFAULT`, `PREDICTION`, `REVIEW` or `INFERENCE`.
            project_id: Identifier of the project.
            external_id_array: list of asset external ids to append labels on.
            disable_tqdm: Disable tqdm progress bar.
            overwrite: when uploading prediction or inference labels, if True,
                it will overwrite existing labels with the same model name
                and of the same label type, on the targeted assets.
            step_name: Name of the step to which the labels belong.
                The label_type must match accordingly.

        Returns:
            A list of dictionaries with the label ids.
        """
        return self.create(
            asset_id_array=asset_id_array,
            json_response_array=json_response_array,
            author_id_array=author_id_array,
            seconds_to_label_array=seconds_to_label_array,
            model_name=model_name,
            label_type=label_type,
            project_id=project_id,
            external_id_array=external_id_array,
            disable_tqdm=disable_tqdm,
            overwrite=overwrite,
            step_name=step_name,
        )

    @typechecked
    def create_from_geojson(
        self,
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
            geojson_file_paths: List of file paths to the GeoJSON files to be processed.
            job_names: Optional list of job names in the Kili project, one for each GeoJSON file.
            category_names: Optional list of category names, one for each GeoJSON file.
            label_type: Can be one of `AUTOSAVE`, `DEFAULT`, `PREDICTION`, `REVIEW` or `INFERENCE`.
            step_name: Name of the step to which the labels belong.
            model_name: Name of the model that generated the labels.
        """
        # Use super() to bypass namespace routing and call the legacy method directly
        return self.client.append_labels_from_geojson_files(
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
    def create_from_shapefile(
        self,
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
            shapefile_paths: List of file paths to the shapefiles to be processed.
            job_names: List of job names in the Kili project, corresponding to each shapefile.
            category_names: List of category names corresponding to each shapefile.
            from_epsgs: Optional list of EPSG codes specifying the coordinate reference systems
                       of the shapefiles. If not provided, EPSG:4326 (WGS84) is assumed for all files.
            label_type: Can be one of `AUTOSAVE`, `DEFAULT`, `PREDICTION`, `REVIEW` or `INFERENCE`.
            step_name: Name of the step to which the labels belong.
            model_name: Name of the model that generated the labels.
        """
        # Use super() to bypass namespace routing and call the legacy method directly
        return self.client.append_labels_from_shapefiles(
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
