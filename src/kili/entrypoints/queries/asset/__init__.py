"""Asset queries."""

import warnings
from typing import List, Literal, Optional

from typeguard import typechecked

from kili.core.graphql.operations.asset.queries import AssetQuery, AssetWhere
from kili.core.helpers import validate_category_search_query
from kili.entrypoints.base import BaseOperationEntrypointMixin
from kili.utils.logcontext import for_all_methods, log_call


@for_all_methods(log_call, exclude=["__init__"])
class QueriesAsset(BaseOperationEntrypointMixin):
    """Set of Asset queries."""

    # pylint: disable=too-many-arguments,too-many-locals,dangerous-default-value,redefined-builtin

    @typechecked
    def count_assets(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_id_in: Optional[List[str]] = None,
        asset_id_not_in: Optional[List[str]] = None,
        external_id_contains: Optional[List[str]] = None,
        metadata_where: Optional[dict] = None,
        status_in: Optional[List[str]] = None,
        consensus_mark_gt: Optional[float] = None,
        consensus_mark_lt: Optional[float] = None,
        honeypot_mark_gt: Optional[float] = None,
        honeypot_mark_lt: Optional[float] = None,
        label_type_in: Optional[List[str]] = None,
        label_author_in: Optional[List[str]] = None,
        label_consensus_mark_gt: Optional[float] = None,
        label_consensus_mark_lt: Optional[float] = None,
        label_created_at: Optional[str] = None,
        label_created_at_gt: Optional[str] = None,
        label_created_at_lt: Optional[str] = None,
        label_honeypot_mark_gt: Optional[float] = None,
        label_honeypot_mark_lt: Optional[float] = None,
        skipped: Optional[bool] = None,
        updated_at_gte: Optional[str] = None,
        updated_at_lte: Optional[str] = None,
        label_category_search: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
        honeypot_mark_gte: Optional[float] = None,
        honeypot_mark_lte: Optional[float] = None,
        consensus_mark_gte: Optional[float] = None,
        consensus_mark_lte: Optional[float] = None,
        inference_mark_gte: Optional[float] = None,
        inference_mark_lte: Optional[float] = None,
        label_reviewer_in: Optional[List[str]] = None,
        label_consensus_mark_gte: Optional[float] = None,
        label_consensus_mark_lte: Optional[float] = None,
        label_created_at_gte: Optional[str] = None,
        label_created_at_lte: Optional[str] = None,
        label_honeypot_mark_gte: Optional[float] = None,
        label_honeypot_mark_lte: Optional[float] = None,
        issue_type: Optional[Literal["QUESTION", "ISSUE"]] = None,
        issue_status: Optional[Literal["OPEN", "SOLVED"]] = None,
        external_id_strictly_in: Optional[List[str]] = None,
        external_id_in: Optional[List[str]] = None,
    ) -> int:
        # pylint: disable=line-too-long
        """Count and return the number of assets with the given constraints.

        Parameters beginning with 'label_' apply to labels, others apply to assets.

        Args:
            project_id: Identifier of the project
            asset_id: The unique id of the asset to retrieve.
            asset_id_in: A list of the ids of the assets to retrieve.
            asset_id_not_in: A list of the ids of the assets to exclude.
            external_id_contains: Deprecated. Use `external_id_strictly_in` instead.
            metadata_where: Filters by the values of the metadata of the asset.
            status_in: Returned assets should have a status that belongs to that list, if given. Possible choices: `TODO`, `ONGOING`, `LABELED`, `TO_REVIEW` or `REVIEWED`.
            consensus_mark_gt: Deprecated. Use `consensus_mark_gte` instead.
            consensus_mark_lt: Deprecated. Use `consensus_mark_lte` instead.
            honeypot_mark_gt: Deprecated. Use `honeypot_mark_gte` instead.
            honeypot_mark_lt: Deprecated. Use `honeypot_mark_lte` instead.
            label_type_in: Returned assets should have a label whose type belongs to that list, if given.
            label_author_in: Returned assets should have a label whose author belongs to that list, if given. An author can be designated by the first name, the last name, or the first name + last name.
            label_consensus_mark_gt: Deprecated. Use `label_consensus_mark_gte` instead.
            label_consensus_mark_lt: Deprecated. Use `label_consensus_mark_lte` instead.
            label_created_at: Returned assets should have a label whose creation date is equal to this date.
            label_created_at_gt: Deprecated. Use `label_created_at_gte` instead.
            label_created_at_lt: Deprecated. Use `label_created_at_lte` instead.
            label_honeypot_mark_gt: Deprecated. Use `label_honeypot_mark_gte` instead.
            label_honeypot_mark_lt: Deprecated. Use `label_honeypot_mark_lte` instead.
            skipped: Returned assets should be skipped.
            updated_at_gte: Returned assets should have a label whose update date is greated or equal to this date.
            updated_at_lte: Returned assets should have a label whose update date is lower or equal to this date.
            label_category_search: Returned assets should have a label that follows this category search query.
            created_at_gte: Returned assets should have their import date greater or equal to this date.
            created_at_lte: Returned assets should have their import date lower or equal to this date.
            honeypot_mark_lte: Maximum amount of honeypot for the asset.
            honeypot_mark_gte: Minimum amount of honeypot for the asset.
            consensus_mark_lte: Maximum amount of consensus for the asset.
            consensus_mark_gte: Minimum amount of consensus for the asset.
            inference_mark_gte: Minimum amount of human/model IoU for the asset.
            inference_mark_lte: Maximum amount of human/model IoU for the asset.
            label_reviewer_in: Returned assets should have a label whose reviewer belongs to that list, if given.
            label_consensus_mark_gte: Returned assets should have a label whose consensus is greater or equal to this number.
            label_consensus_mark_lte: Returned assets should have a label whose consensus is lower or equal to this number.
            label_created_at_lte: Returned assets should have a label whose creation date is lower or equal to this date.
            label_created_at_gte: Returned assets should have a label whose creation date is greater or equal to this date.
            label_honeypot_mark_gte: Returned assets should have a label whose honeypot is greater or equal to this number.
            label_honeypot_mark_lte: Returned assets should have a label whose honeypot is lower or equal to this number.
            issue_type: Returned assets should have issues of type `QUESTION` or `ISSUE`.
            issue_status: Returned assets should have issues of status `OPEN` or `SOLVED`.
            external_id_strictly_in: Returned assets should have external ids that match exactly the ones in the list.
            external_id_in: Returned assets should have external ids that partially match the ones in the list.
                For example, with `external_id_in=['abc']`, any asset with an external id containing `'abc'` will be returned.

        !!! info "Dates format"
            Date strings should have format: "YYYY-MM-DD"

        Returns:
            The number of assets that match the given constraints.

        Examples:
            >>> kili.count_assets(project_id=project_id)
            250
            >>> kili.count_assets(asset_id=asset_id)
            1

        !!! example "How to filter based on Metadata"
            - `metadata_where = {key1: "value1"}` to filter on assets whose metadata
                have key "key1" with value "value1"
            - `metadata_where = {key1: ["value1", "value2"]}` to filter on assets whose metadata
                have key "key1" with value "value1" or value "value2
            - `metadata_where = {key2: [2, 10]}` to filter on assets whose metadata
                have key "key2" with a value between 2 and 10.
        """
        if label_category_search:
            validate_category_search_query(label_category_search)

        if external_id_contains is not None:
            warnings.warn(
                "external_id_contains is deprecated, use external_id_strictly_in instead",
                DeprecationWarning,
                stacklevel=1,
            )

        for arg_name, arg_value in zip(
            (
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
            ),
            (
                consensus_mark_gt,
                consensus_mark_lt,
                honeypot_mark_gt,
                honeypot_mark_lt,
                label_consensus_mark_gt,
                label_consensus_mark_lt,
                label_created_at_gt,
                label_created_at_lt,
                label_honeypot_mark_gt,
                label_honeypot_mark_lt,
            ),
        ):
            if arg_value:
                warnings.warn(
                    f"'{arg_name}' is deprecated, please use"
                    f" '{arg_name.replace('_gt', '_gte').replace('_lt', '_lte')}' instead.",
                    DeprecationWarning,
                    stacklevel=1,
                )

        where = AssetWhere(
            project_id=project_id,
            asset_id=asset_id,
            asset_id_in=asset_id_in,
            asset_id_not_in=asset_id_not_in,
            consensus_mark_gte=consensus_mark_gt or consensus_mark_gte,
            consensus_mark_lte=consensus_mark_lt or consensus_mark_lte,
            external_id_strictly_in=external_id_strictly_in or external_id_contains,
            external_id_in=external_id_in,
            honeypot_mark_gte=honeypot_mark_gt or honeypot_mark_gte,
            honeypot_mark_lte=honeypot_mark_lt or honeypot_mark_lte,
            inference_mark_gte=inference_mark_gte,
            inference_mark_lte=inference_mark_lte,
            label_author_in=label_author_in,
            label_reviewer_in=label_reviewer_in,
            label_consensus_mark_gte=label_consensus_mark_gt or label_consensus_mark_gte,
            label_consensus_mark_lte=label_consensus_mark_lt or label_consensus_mark_lte,
            label_created_at=label_created_at,
            label_created_at_gte=label_created_at_gt or label_created_at_gte,
            label_created_at_lte=label_created_at_lt or label_created_at_lte,
            label_honeypot_mark_gte=label_honeypot_mark_gt or label_honeypot_mark_gte,
            label_honeypot_mark_lte=label_honeypot_mark_lt or label_honeypot_mark_lte,
            label_type_in=label_type_in,
            metadata_where=metadata_where,
            skipped=skipped,
            status_in=status_in,
            updated_at_gte=updated_at_gte,
            updated_at_lte=updated_at_lte,
            label_category_search=label_category_search,
            created_at_gte=created_at_gte,
            created_at_lte=created_at_lte,
            issue_status=issue_status,
            issue_type=issue_type,
        )
        return AssetQuery(self.graphql_client, self.http_client).count(where)
