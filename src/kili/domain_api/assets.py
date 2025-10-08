"""Assets domain namespace for the Kili Python SDK."""

import warnings
from dataclasses import fields as dataclass_fields
from functools import cached_property
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generator,
    List,
    Optional,
    Union,
    cast,
)

from typeguard import typechecked

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.domain.asset import (
    AssetExternalId,
    AssetFilters,
    AssetId,
    AssetStatus,
    get_asset_default_fields,
)
from kili.domain.asset.asset import StatusInStep
from kili.domain.asset.helpers import check_asset_workflow_arguments
from kili.domain.project import ProjectId, ProjectStep, WorkflowVersion
from kili.domain.types import ListOrTuple
from kili.domain_api.base import DomainNamespace
from kili.domain_v2.asset import (
    AssetCreateResponse,
    AssetView,
    WorkflowStepResponse,
    validate_asset,
    validate_asset_create_response,
    validate_workflow_step_response,
)
from kili.domain_v2.project import IdListResponse, IdResponse
from kili.presentation.client.helpers.common_validators import (
    disable_tqdm_if_as_generator,
)
from kili.use_cases.asset import AssetUseCases
from kili.use_cases.project.project import ProjectUseCases

if TYPE_CHECKING:
    import pandas as pd


def _extract_step_ids_from_project_steps(
    project_steps: List[ProjectStep], step_name_in: List[str]
) -> List[str]:
    """Extract step ids from project steps."""
    matching_steps = [step for step in project_steps if step.get("name") in step_name_in]

    unmatched_names = [
        name for name in step_name_in if name not in [step.get("name") for step in project_steps]
    ]
    if unmatched_names:
        raise ValueError(f"The following step names do not match any steps: {unmatched_names}")

    return [step["id"] for step in matching_steps]


class WorkflowStepNamespace:
    """Nested namespace for workflow step operations."""

    def __init__(self, assets_namespace: "AssetsNamespace"):
        """Initialize the workflow step namespace.

        Args:
            assets_namespace: The parent assets namespace
        """
        self._assets_namespace = assets_namespace

    @typechecked
    def invalidate(
        self,
        asset_ids: Optional[List[str]] = None,
        external_ids: Optional[List[str]] = None,
        project_id: Optional[str] = None,
    ) -> Optional[WorkflowStepResponse]:
        """Send assets back to queue (invalidate current step).

        This method sends assets back to the queue, effectively invalidating their
        current workflow step status.

        Args:
            asset_ids: List of internal IDs of assets to send back to queue.
            external_ids: List of external IDs of assets to send back to queue.
            project_id: The project ID. Only required if `external_ids` argument is provided.

        Returns:
            A response object with the project `id` and the `asset_ids` of assets moved to queue.
            Returns None if no assets have changed status.
            An error message if mutation failed.

        Examples:
            >>> result = kili.assets.workflow.step.invalidate(
                    asset_ids=["ckg22d81r0jrg0885unmuswj8", "ckg22d81s0jrh0885pdxfd03n"]
                )
            >>> print(result.id)  # Project ID
            >>> print(result.asset_ids)  # List of invalidated asset IDs
        """
        result = self._assets_namespace.client.send_back_to_queue(
            asset_ids=asset_ids,
            external_ids=external_ids,
            project_id=project_id,
        )
        return WorkflowStepResponse(validate_workflow_step_response(result)) if result else None

    @typechecked
    def next(
        self,
        asset_ids: Optional[List[str]] = None,
        external_ids: Optional[List[str]] = None,
        project_id: Optional[str] = None,
    ) -> Optional[WorkflowStepResponse]:
        """Move assets to the next workflow step (typically review).

        This method moves assets to the next step in the workflow, typically
        adding them to review.

        Args:
            asset_ids: The asset internal IDs to add to review.
            external_ids: The asset external IDs to add to review.
            project_id: The project ID. Only required if `external_ids` argument is provided.

        Returns:
            A response object with the project `id` and the `asset_ids` of assets moved to review.
            Returns None if no assets have changed status (already had `TO_REVIEW` status for example).
            An error message if mutation failed.

        Examples:
            >>> result = kili.assets.workflow.step.next(
                    asset_ids=["ckg22d81r0jrg0885unmuswj8", "ckg22d81s0jrh0885pdxfd03n"]
                )
            >>> print(result.id)  # Project ID
            >>> print(result.asset_ids)  # List of assets moved to review
        """
        result = self._assets_namespace.client.add_to_review(
            asset_ids=asset_ids,
            external_ids=external_ids,
            project_id=project_id,
        )
        return WorkflowStepResponse(validate_workflow_step_response(result)) if result else None


class WorkflowNamespace:
    """Nested namespace for workflow operations."""

    def __init__(self, assets_namespace: "AssetsNamespace"):
        """Initialize the workflow namespace.

        Args:
            assets_namespace: The parent assets namespace
        """
        self._assets_namespace = assets_namespace

    @cached_property
    def step(self) -> WorkflowStepNamespace:
        """Get the workflow step namespace.

        Returns:
            WorkflowStepNamespace: Workflow step operations namespace
        """
        return WorkflowStepNamespace(self._assets_namespace)

    @typechecked
    def assign(
        self,
        to_be_labeled_by_array: List[List[str]],
        asset_ids: Optional[List[str]] = None,
        external_ids: Optional[List[str]] = None,
        project_id: Optional[str] = None,
    ) -> IdListResponse:
        """Assign a list of assets to a list of labelers.

        Args:
            asset_ids: The internal asset IDs to assign.
            external_ids: The external asset IDs to assign (if `asset_ids` is not already provided).
            project_id: The project ID. Only required if `external_ids` argument is provided.
            to_be_labeled_by_array: The array of list of labelers to assign per labelers (list of userIds).

        Returns:
            A response object containing the list of assigned asset IDs.

        Examples:
            >>> result = kili.assets.workflow.assign(
                    asset_ids=["ckg22d81r0jrg0885unmuswj8", "ckg22d81s0jrh0885pdxfd03n"],
                    to_be_labeled_by_array=[['cm3yja6kv0i698697gcil9rtk','cm3yja6kv0i000000gcil9rtk'],
                                            ['cm3yja6kv0i698697gcil9rtk']]
                )
            >>> print(result.ids)  # List of assigned asset IDs
        """
        result = self._assets_namespace.client.assign_assets_to_labelers(
            asset_ids=asset_ids,
            external_ids=external_ids,
            project_id=project_id,
            to_be_labeled_by_array=to_be_labeled_by_array,
        )
        return IdListResponse(result)


class ExternalIdsNamespace:
    """Nested namespace for external ID operations."""

    def __init__(self, assets_namespace: "AssetsNamespace"):
        """Initialize the external IDs namespace.

        Args:
            assets_namespace: The parent assets namespace
        """
        self._assets_namespace = assets_namespace

    @typechecked
    def update(
        self,
        new_external_ids: List[str],
        asset_ids: Optional[List[str]] = None,
        external_ids: Optional[List[str]] = None,
        project_id: Optional[str] = None,
    ) -> IdListResponse:
        """Update the external IDs of one or more assets.

        Args:
            new_external_ids: The new external IDs of the assets.
            asset_ids: The asset IDs to modify.
            external_ids: The external asset IDs to modify (if `asset_ids` is not already provided).
            project_id: The project ID. Only required if `external_ids` argument is provided.

        Returns:
            A response object containing the list of updated asset IDs.

        Examples:
            >>> result = kili.assets.external_ids.update(
                    new_external_ids=["asset1", "asset2"],
                    asset_ids=["ckg22d81r0jrg0885unmuswj8", "ckg22d81s0jrh0885pdxfd03n"],
                )
            >>> print(result.ids)  # List of updated asset IDs
        """
        result = self._assets_namespace.client.change_asset_external_ids(
            new_external_ids=new_external_ids,
            asset_ids=asset_ids,
            external_ids=external_ids,
            project_id=project_id,
        )
        return IdListResponse(result)


class MetadataNamespace:
    """Nested namespace for metadata operations."""

    def __init__(self, assets_namespace: "AssetsNamespace"):
        """Initialize the metadata namespace.

        Args:
            assets_namespace: The parent assets namespace
        """
        self._assets_namespace = assets_namespace

    @typechecked
    def add(
        self,
        json_metadata: List[Dict[str, Union[str, int, float]]],
        project_id: str,
        asset_ids: Optional[List[str]] = None,
        external_ids: Optional[List[str]] = None,
    ) -> IdListResponse:
        """Add metadata to assets without overriding existing metadata.

        Args:
            json_metadata: List of metadata dictionaries to add to each asset.
                Each dictionary contains key/value pairs to be added to the asset's metadata.
            project_id: The project ID.
            asset_ids: The asset IDs to modify.
            external_ids: The external asset IDs to modify (if `asset_ids` is not already provided).

        Returns:
            A response object containing the list of modified asset IDs.

        Examples:
            >>> result = kili.assets.metadata.add(
                    json_metadata=[
                        {"key1": "value1", "key2": "value2"},
                        {"key3": "value3"}
                    ],
                    project_id="cm92to3cx012u7l0w6kij9qvx",
                    asset_ids=["ckg22d81r0jrg0885unmuswj8", "ckg22d81s0jrh0885pdxfd03n"]
                )
            >>> print(result.ids)  # List of modified asset IDs
        """
        result = self._assets_namespace.client.add_metadata(
            json_metadata=json_metadata,
            project_id=project_id,
            asset_ids=asset_ids,
            external_ids=external_ids,
        )
        return IdListResponse(result)

    @typechecked
    def set(
        self,
        json_metadata: List[Dict[str, Union[str, int, float]]],
        project_id: str,
        asset_ids: Optional[List[str]] = None,
        external_ids: Optional[List[str]] = None,
    ) -> IdListResponse:
        """Set metadata on assets, replacing any existing metadata.

        Args:
            json_metadata: List of metadata dictionaries to set on each asset.
                Each dictionary contains key/value pairs to be set as the asset's metadata.
            project_id: The project ID.
            asset_ids: The asset IDs to modify (if `external_ids` is not already provided).
            external_ids: The external asset IDs to modify (if `asset_ids` is not already provided).

        Returns:
            A response object containing the list of modified asset IDs.

        Examples:
            >>> result = kili.assets.metadata.set(
                    json_metadata=[
                        {"key1": "value1", "key2": "value2"},
                        {"key3": "value3"}
                    ],
                    project_id="cm92to3cx012u7l0w6kij9qvx",
                    asset_ids=["ckg22d81r0jrg0885unmuswj8", "ckg22d81s0jrh0885pdxfd03n"]
                )
            >>> print(result.ids)  # List of modified asset IDs
        """
        result = self._assets_namespace.client.set_metadata(
            json_metadata=json_metadata,
            project_id=project_id,
            asset_ids=asset_ids,
            external_ids=external_ids,
        )
        return IdListResponse(result)


class AssetsNamespace(DomainNamespace):
    """Assets domain namespace providing asset-related operations.

    This namespace provides access to all asset-related functionality
    including creating, updating, querying, and managing assets.

    The namespace provides the following main operations:
    - list(): Query and list assets
    - count(): Count assets matching filters
    - create(): Create new assets in bulk
    - delete(): Delete assets from projects
    - update(): Update asset properties

    It also provides nested namespaces for specialized operations:
    - workflow: Asset workflow management (assign, step operations)
    - external_ids: External ID management
    - metadata: Asset metadata management

    Examples:
        >>> kili = Kili()
        >>> # List assets
        >>> assets = kili.assets.list(project_id="my_project")

        >>> # Count assets
        >>> count = kili.assets.count(project_id="my_project")

        >>> # Create assets
        >>> result = kili.assets.create(
        ...     project_id="my_project",
        ...     content_array=["https://example.com/image.png"]
        ... )

        >>> # Update asset metadata
        >>> kili.assets.metadata.add(
        ...     json_metadata=[{"key": "value"}],
        ...     project_id="my_project",
        ...     asset_ids=["asset_id"]
        ... )

        >>> # Manage workflow
        >>> kili.assets.workflow.assign(
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

    @cached_property
    def workflow(self) -> WorkflowNamespace:
        """Get the workflow namespace for asset workflow operations.

        Returns:
            WorkflowNamespace: Workflow operations namespace
        """
        return WorkflowNamespace(self)

    @cached_property
    def external_ids(self) -> ExternalIdsNamespace:
        """Get the external IDs namespace for external ID operations.

        Returns:
            ExternalIdsNamespace: External ID operations namespace
        """
        return ExternalIdsNamespace(self)

    @cached_property
    def metadata(self) -> MetadataNamespace:
        """Get the metadata namespace for metadata operations.

        Returns:
            MetadataNamespace: Metadata operations namespace
        """
        return MetadataNamespace(self)

    def _parse_filter_kwargs(
        self,
        kwargs: Dict[str, Any],
        project_id: str,
        asset_id: Optional[str],
        project_steps: List[ProjectStep],
        project_workflow_version: WorkflowVersion,
    ) -> AssetFilters:
        """Parse and validate filter kwargs into AssetFilters object.

        Args:
            kwargs: Dictionary of filter arguments
            project_id: Project identifier
            asset_id: Optional asset identifier
            project_steps: List of project workflow steps
            project_workflow_version: Project workflow version

        Returns:
            AssetFilters object with validated filters

        Raises:
            TypeError: If unknown or deprecated parameters are provided
        """
        # Handle workflow-related filters
        step_name_in = kwargs.pop("step_name_in", None)
        step_status_in = kwargs.pop("step_status_in", None)
        status_in = kwargs.pop("status_in", None)
        skipped = kwargs.pop("skipped", None)
        step_id_in = None
        if (
            step_name_in is not None
            or step_status_in is not None
            or status_in is not None
            or skipped is not None
        ):
            check_asset_workflow_arguments(
                project_workflow_version=project_workflow_version,
                asset_workflow_filters={
                    "skipped": skipped,
                    "status_in": status_in,
                    "step_name_in": step_name_in,
                    "step_status_in": step_status_in,
                },
            )
            if project_workflow_version == "V2" and step_name_in is not None:
                step_id_in = _extract_step_ids_from_project_steps(
                    project_steps=project_steps,
                    step_name_in=step_name_in,
                )

        # Extract all filter parameters
        def _pop(name: str) -> Any:
            return kwargs.pop(name, None)

        asset_id_in = _pop("asset_id_in")
        asset_id_not_in = _pop("asset_id_not_in")
        consensus_mark_gte = _pop("consensus_mark_gte")
        consensus_mark_lte = _pop("consensus_mark_lte")
        honeypot_mark_gte = _pop("honeypot_mark_gte")
        honeypot_mark_lte = _pop("honeypot_mark_lte")
        label_author_in = _pop("label_author_in")
        label_consensus_mark_gte = _pop("label_consensus_mark_gte")
        label_consensus_mark_lte = _pop("label_consensus_mark_lte")
        label_created_at = _pop("label_created_at")
        label_created_at_gte = _pop("label_created_at_gte")
        label_created_at_lte = _pop("label_created_at_lte")
        label_honeypot_mark_gte = _pop("label_honeypot_mark_gte")
        label_honeypot_mark_lte = _pop("label_honeypot_mark_lte")
        label_type_in = _pop("label_type_in")
        metadata_where = _pop("metadata_where")
        updated_at_gte = _pop("updated_at_gte")
        updated_at_lte = _pop("updated_at_lte")
        label_category_search = _pop("label_category_search")
        created_at_gte = _pop("created_at_gte")
        created_at_lte = _pop("created_at_lte")
        external_id_strictly_in = _pop("external_id_strictly_in")
        external_id_in = _pop("external_id_in")
        label_labeler_in = _pop("label_labeler_in")
        label_labeler_not_in = _pop("label_labeler_not_in")
        label_reviewer_in = _pop("label_reviewer_in")
        label_reviewer_not_in = _pop("label_reviewer_not_in")
        assignee_in = _pop("assignee_in")
        assignee_not_in = _pop("assignee_not_in")
        inference_mark_gte = _pop("inference_mark_gte")
        inference_mark_lte = _pop("inference_mark_lte")
        issue_type = _pop("issue_type")
        issue_status = _pop("issue_status")

        remaining_filter_kwargs: Dict[str, Any] = {}
        asset_filter_field_names = {field.name for field in dataclass_fields(AssetFilters)}
        for key in list(kwargs.keys()):
            if key in asset_filter_field_names:
                remaining_filter_kwargs[key] = kwargs.pop(key)

        if kwargs:
            raise TypeError(f"Unknown asset filter arguments: {', '.join(sorted(kwargs.keys()))}")

        return AssetFilters(
            project_id=ProjectId(project_id),
            asset_id=AssetId(asset_id) if asset_id else None,
            asset_id_in=cast(List[AssetId], asset_id_in) if asset_id_in else None,
            asset_id_not_in=cast(List[AssetId], asset_id_not_in) if asset_id_not_in else None,
            consensus_mark_gte=consensus_mark_gte,
            consensus_mark_lte=consensus_mark_lte,
            external_id_strictly_in=cast(List[AssetExternalId], external_id_strictly_in)
            if external_id_strictly_in
            else None,
            external_id_in=cast(List[AssetExternalId], external_id_in) if external_id_in else None,
            honeypot_mark_gte=honeypot_mark_gte,
            honeypot_mark_lte=honeypot_mark_lte,
            inference_mark_gte=inference_mark_gte,
            inference_mark_lte=inference_mark_lte,
            label_author_in=label_author_in,
            label_consensus_mark_gte=label_consensus_mark_gte,
            label_consensus_mark_lte=label_consensus_mark_lte,
            label_created_at=label_created_at,
            label_created_at_gte=label_created_at_gte,
            label_created_at_lte=label_created_at_lte,
            label_honeypot_mark_gte=label_honeypot_mark_gte,
            label_honeypot_mark_lte=label_honeypot_mark_lte,
            label_type_in=label_type_in,
            metadata_where=metadata_where,
            skipped=skipped,
            status_in=cast(Optional[List[AssetStatus]], status_in),
            updated_at_gte=updated_at_gte,
            updated_at_lte=updated_at_lte,
            label_category_search=label_category_search,
            created_at_gte=created_at_gte,
            created_at_lte=created_at_lte,
            label_labeler_in=label_labeler_in,
            label_labeler_not_in=label_labeler_not_in,
            label_reviewer_in=label_reviewer_in,
            label_reviewer_not_in=label_reviewer_not_in,
            assignee_in=assignee_in,
            assignee_not_in=assignee_not_in,
            issue_status=issue_status,
            issue_type=issue_type,
            step_id_in=cast(Optional[List[str]], step_id_in),
            step_status_in=cast(Optional[List[StatusInStep]], step_status_in),
            **remaining_filter_kwargs,
        )

    @typechecked
    def list(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        skip: int = 0,
        fields: Optional[ListOrTuple[str]] = None,
        first: Optional[int] = None,
        disable_tqdm: Optional[bool] = None,
        as_generator: bool = True,
        **kwargs,
    ) -> Union[Generator[AssetView, None, None], List[AssetView], "pd.DataFrame"]:
        """List assets from a project.

        Args:
            project_id: Identifier of the project
            asset_id: Identifier of the asset to retrieve. If provided, returns only this asset
            skip: Number of assets to skip (they are ordered by creation date)
            fields: List of fields to return. If None, returns default fields
            first: Maximum number of assets to return
            disable_tqdm: If True, the progress bar will be disabled
            as_generator: If True, returns a generator. If False, returns a list
            **kwargs: Additional filter arguments (asset_id_in, external_id_contains, etc.)

        Returns:
            Generator, list, or DataFrame of assets depending on parameters
        """
        kwargs = dict(kwargs)
        deprecated_parameters = {
            "external_id_contains",
            "consensus_mark_gt",
            "consensus_mark_lt",
            "honeypot_mark_gt",
            "honeypot_mark_lt",
            "label_consensus_mark_gt",
            "label_consensus_mark_lt",
            "label_created_at_gt",
            "label_created_at_lt",
            "label_honeypot_mark_gt",
            "label_honeypot_mark_lt",
        }
        unsupported = sorted(param for param in deprecated_parameters if param in kwargs)
        if unsupported:
            raise TypeError(
                "Deprecated asset filter parameters are no longer supported: "
                + ", ".join(unsupported)
            )

        format_ = kwargs.pop("format", None)
        if format_ == "pandas" and as_generator:
            raise ValueError(
                'Argument values as_generator==True and format=="pandas" are not compatible.'
            )

        download_media = kwargs.pop("download_media", False)
        local_media_dir = kwargs.pop("local_media_dir", None)
        label_output_format = kwargs.pop("label_output_format", "dict")

        disable_tqdm = disable_tqdm_if_as_generator(as_generator, disable_tqdm)

        project_use_cases = ProjectUseCases(self.gateway)
        project_steps, project_workflow_version = project_use_cases.get_project_steps_and_version(
            project_id
        )

        if fields is None:
            fields = get_asset_default_fields(project_workflow_version=project_workflow_version)
        elif project_workflow_version == "V1":
            for invalid_field in filter(lambda f: f.startswith("currentStep."), fields):
                warnings.warn(
                    (
                        f"Field {invalid_field} requested : request 'status' field instead for this"
                        " project"
                    ),
                    stacklevel=2,
                )
        elif "status" in fields:
            warnings.warn(
                (
                    "Field status requested : request 'currentStep.name' and 'currentStep.status'"
                    " fields instead for this project"
                ),
                stacklevel=2,
            )

        filters = self._parse_filter_kwargs(
            kwargs, project_id, asset_id, project_steps, project_workflow_version
        )

        asset_use_cases = AssetUseCases(self.gateway)

        assets_gen = asset_use_cases.list_assets(
            filters=filters,
            fields=fields,
            options=QueryOptions(
                first=first,
                skip=skip,
                disable_tqdm=disable_tqdm or False,
            ),
            download_media=download_media,
            local_media_dir=local_media_dir,
            label_output_format=label_output_format,
        )

        if as_generator:
            return (AssetView(validate_asset(item)) for item in assets_gen)

        assets_list = list(assets_gen)

        if format_ == "pandas":
            try:
                import pandas as pd  # pylint: disable=import-outside-toplevel

                return pd.DataFrame(assets_list)
            except ImportError:
                warnings.warn(
                    "pandas not available, returning list instead", ImportWarning, stacklevel=2
                )

        return [AssetView(validate_asset(item)) for item in assets_list]

    @typechecked
    def count(
        self,
        project_id: str,
        **kwargs,
    ) -> int:
        """Count assets in a project.

        Args:
            project_id: Identifier of the project
            **kwargs: Additional filter arguments (asset_id_in, external_id_contains, etc.)

        Returns:
            Number of assets matching the filters
        """
        kwargs = dict(kwargs)
        asset_id = kwargs.pop("asset_id", None)

        project_use_cases = ProjectUseCases(self.gateway)
        project_steps, project_workflow_version = project_use_cases.get_project_steps_and_version(
            project_id
        )

        filters = self._parse_filter_kwargs(
            kwargs, project_id, asset_id, project_steps, project_workflow_version
        )

        asset_use_cases = AssetUseCases(self.gateway)
        return asset_use_cases.count_assets(filters)

    @typechecked
    def create(
        self,
        project_id: str,
        content_array: Optional[Union[List[str], List[dict], List[List[dict]]]] = None,
        multi_layer_content_array: Optional[List[List[dict]]] = None,
        external_id_array: Optional[List[str]] = None,
        is_honeypot_array: Optional[List[bool]] = None,
        json_content_array: Optional[List[Union[List[Union[dict, str]], None]]] = None,
        json_metadata_array: Optional[List[dict]] = None,
        disable_tqdm: Optional[bool] = None,
        wait_until_availability: bool = True,
        from_csv: Optional[str] = None,
        csv_separator: str = ",",
        **kwargs,
    ) -> AssetCreateResponse:
        """Create assets in a project.

        Args:
            project_id: Identifier of the project
            content_array: List of elements added to the assets of the project
            multi_layer_content_array: List containing multiple lists of paths for geosat assets
            external_id_array: List of external ids given to identify the assets
            is_honeypot_array: Whether to use the asset for honeypot
            json_content_array: Useful for VIDEO or TEXT or IMAGE projects only
            json_metadata_array: The metadata given to each asset
            disable_tqdm: If True, the progress bar will be disabled
            wait_until_availability: If True, waits until assets are fully processed
            from_csv: Path to a csv file containing the text assets to import
            csv_separator: Separator used in the csv file
            **kwargs: Additional arguments

        Returns:
            A response object with project id and list of created asset ids.

        Examples:
            >>> # Create image assets
            >>> result = kili.assets.create(
            ...     project_id="my_project",
            ...     content_array=["https://example.com/image.png"]
            ... )
            >>> print(result.id)  # Project ID
            >>> print(result.asset_ids)  # List of created asset IDs

            >>> # Create assets with metadata
            >>> result = kili.assets.create(
            ...     project_id="my_project",
            ...     content_array=["https://example.com/image.png"],
            ...     json_metadata_array=[{"description": "Sample image"}]
            ... )
        """
        # Call the legacy method directly through the client
        result = self.client.append_many_to_dataset(
            project_id=project_id,
            content_array=content_array,
            multi_layer_content_array=multi_layer_content_array,
            external_id_array=external_id_array,
            is_honeypot_array=is_honeypot_array,
            json_content_array=json_content_array,
            json_metadata_array=json_metadata_array,
            disable_tqdm=disable_tqdm,
            wait_until_availability=wait_until_availability,
            from_csv=from_csv,
            csv_separator=csv_separator,
            **kwargs,
        )
        return AssetCreateResponse(validate_asset_create_response(cast(Dict[str, Any], result)))

    @typechecked
    def delete(
        self,
        asset_ids: Optional[List[str]] = None,
        external_ids: Optional[List[str]] = None,
        project_id: Optional[str] = None,
    ) -> Optional[IdResponse]:
        """Delete assets from a project.

        Args:
            asset_ids: The list of asset internal IDs to delete
            external_ids: The list of asset external IDs to delete
            project_id: The project ID. Only required if `external_ids` argument is provided

        Returns:
            A response object with the project `id`, or None if no deletion occurred.

        Examples:
            >>> # Delete assets by internal IDs
            >>> result = kili.assets.delete(
            ...     asset_ids=["ckg22d81r0jrg0885unmuswj8", "ckg22d81s0jrh0885pdxfd03n"]
            ... )
            >>> print(result.id)  # Project ID

            >>> # Delete assets by external IDs
            >>> result = kili.assets.delete(
            ...     external_ids=["asset1", "asset2"],
            ...     project_id="my_project"
            ... )
        """
        # Call the legacy method directly through the client
        result = self.client.delete_many_from_dataset(
            asset_ids=asset_ids,
            external_ids=external_ids,
            project_id=project_id,
        )
        return IdResponse(result) if result else None

    @typechecked
    def update(
        self,
        asset_ids: Optional[List[str]] = None,
        external_ids: Optional[List[str]] = None,
        project_id: Optional[str] = None,
        priorities: Optional[List[int]] = None,
        json_metadatas: Optional[List[Union[dict, str]]] = None,
        consensus_marks: Optional[List[float]] = None,
        honeypot_marks: Optional[List[float]] = None,
        contents: Optional[List[str]] = None,
        json_contents: Optional[List[str]] = None,
        is_used_for_consensus_array: Optional[List[bool]] = None,
        is_honeypot_array: Optional[List[bool]] = None,
        **kwargs,
    ) -> IdListResponse:
        """Update the properties of one or more assets.

        Args:
            asset_ids: The internal asset IDs to modify
            external_ids: The external asset IDs to modify (if `asset_ids` is not already provided)
            project_id: The project ID. Only required if `external_ids` argument is provided
            priorities: Change the priority of the assets
            json_metadatas: The metadata given to assets
            consensus_marks: Should be between 0 and 1
            honeypot_marks: Should be between 0 and 1
            contents: Content URLs for the assets
            json_contents: JSON content for the assets
            is_used_for_consensus_array: Whether to use the asset to compute consensus kpis
            is_honeypot_array: Whether to use the asset for honeypot
            **kwargs: Additional update parameters

        Returns:
            A response object containing the list of updated asset IDs.

        Examples:
            >>> # Update asset priorities and metadata
            >>> result = kili.assets.update(
            ...     asset_ids=["ckg22d81r0jrg0885unmuswj8"],
            ...     priorities=[1],
            ...     json_metadatas=[{"updated": True}]
            ... )
            >>> print(result.ids)  # List of updated asset IDs

            >>> # Update honeypot settings
            >>> result = kili.assets.update(
            ...     asset_ids=["ckg22d81r0jrg0885unmuswj8"],
            ...     is_honeypot_array=[True],
            ...     honeypot_marks=[0.8]
            ... )
        """
        # Call the legacy method directly through the client
        result = self.client.update_properties_in_assets(
            asset_ids=asset_ids,
            external_ids=external_ids,
            project_id=project_id,
            priorities=priorities,
            json_metadatas=json_metadatas,
            consensus_marks=consensus_marks,
            honeypot_marks=honeypot_marks,
            contents=contents,
            json_contents=json_contents,
            is_used_for_consensus_array=is_used_for_consensus_array,
            is_honeypot_array=is_honeypot_array,
            **kwargs,
        )
        return IdListResponse(result)
