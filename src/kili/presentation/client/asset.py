"""Client presentation methods for assets."""

import warnings
from typing import (
    TYPE_CHECKING,
    Dict,
    Generator,
    Iterable,
    List,
    Literal,
    Optional,
    Union,
    cast,
    overload,
)

from typeguard import typechecked

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.domain.asset import AssetExternalId, AssetFilters, AssetId, AssetStatus
from kili.domain.issue import IssueStatus, IssueType
from kili.domain.label import LabelType
from kili.domain.project import ProjectId
from kili.domain.types import ListOrTuple
from kili.presentation.client.helpers.common_validators import (
    disable_tqdm_if_as_generator,
)
from kili.use_cases.asset import AssetUseCases
from kili.utils.logcontext import for_all_methods, log_call

from .base import BaseClientMethods

if TYPE_CHECKING:
    import pandas as pd


@for_all_methods(log_call, exclude=["__init__"])
class AssetClientMethods(BaseClientMethods):
    """Methods attached to the Kili client, to run actions on assets."""

    # pylint: disable=too-many-arguments, redefined-builtin, too-many-locals
    @overload
    def assets(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        skip: int = 0,
        fields: ListOrTuple[str] = (
            "content",
            "createdAt",
            "externalId",
            "id",
            "isHoneypot",
            "jsonMetadata",
            "labels.author.id",
            "labels.author.email",
            "labels.createdAt",
            "labels.id",
            "labels.jsonResponse",
            "skipped",
            "status",
        ),
        asset_id_in: Optional[List[str]] = None,
        asset_id_not_in: Optional[List[str]] = None,
        consensus_mark_gt: Optional[float] = None,
        consensus_mark_lt: Optional[float] = None,
        disable_tqdm: Optional[bool] = None,
        external_id_contains: Optional[List[str]] = None,
        first: Optional[int] = None,
        format: Optional[str] = None,
        honeypot_mark_gt: Optional[float] = None,
        honeypot_mark_lt: Optional[float] = None,
        label_author_in: Optional[List[str]] = None,
        label_consensus_mark_gt: Optional[float] = None,
        label_consensus_mark_lt: Optional[float] = None,
        label_created_at: Optional[str] = None,
        label_created_at_gt: Optional[str] = None,
        label_created_at_lt: Optional[str] = None,
        label_honeypot_mark_gt: Optional[float] = None,
        label_honeypot_mark_lt: Optional[float] = None,
        label_type_in: Optional[List[LabelType]] = None,
        metadata_where: Optional[dict] = None,
        skipped: Optional[bool] = None,
        status_in: Optional[List[AssetStatus]] = None,
        updated_at_gte: Optional[str] = None,
        updated_at_lte: Optional[str] = None,
        label_category_search: Optional[str] = None,
        download_media: bool = False,
        local_media_dir: Optional[str] = None,
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
        issue_type: Optional[IssueType] = None,
        issue_status: Optional[IssueStatus] = None,
        external_id_strictly_in: Optional[List[str]] = None,
        external_id_in: Optional[List[str]] = None,
        label_output_format: Literal["dict", "parsed_label"] = "dict",
        *,
        as_generator: Literal[True],
    ) -> Generator[Dict, None, None]:
        ...

    @overload
    def assets(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        skip: int = 0,
        fields: ListOrTuple[str] = (
            "content",
            "createdAt",
            "externalId",
            "id",
            "isHoneypot",
            "jsonMetadata",
            "labels.author.id",
            "labels.author.email",
            "labels.createdAt",
            "labels.id",
            "labels.jsonResponse",
            "skipped",
            "status",
        ),
        asset_id_in: Optional[List[str]] = None,
        asset_id_not_in: Optional[List[str]] = None,
        consensus_mark_gt: Optional[float] = None,
        consensus_mark_lt: Optional[float] = None,
        disable_tqdm: Optional[bool] = None,
        external_id_contains: Optional[List[str]] = None,
        first: Optional[int] = None,
        format: Optional[str] = None,
        honeypot_mark_gt: Optional[float] = None,
        honeypot_mark_lt: Optional[float] = None,
        label_author_in: Optional[List[str]] = None,
        label_consensus_mark_gt: Optional[float] = None,
        label_consensus_mark_lt: Optional[float] = None,
        label_created_at: Optional[str] = None,
        label_created_at_gt: Optional[str] = None,
        label_created_at_lt: Optional[str] = None,
        label_honeypot_mark_gt: Optional[float] = None,
        label_honeypot_mark_lt: Optional[float] = None,
        label_type_in: Optional[List[LabelType]] = None,
        metadata_where: Optional[dict] = None,
        skipped: Optional[bool] = None,
        status_in: Optional[List[AssetStatus]] = None,
        updated_at_gte: Optional[str] = None,
        updated_at_lte: Optional[str] = None,
        label_category_search: Optional[str] = None,
        download_media: bool = False,
        local_media_dir: Optional[str] = None,
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
        label_output_format: Literal["dict", "parsed_label"] = "dict",
        *,
        as_generator: Literal[False] = False,
    ) -> List[Dict]:
        ...

    @typechecked
    def assets(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        skip: int = 0,
        fields: ListOrTuple[str] = (
            "content",
            "createdAt",
            "externalId",
            "id",
            "isHoneypot",
            "jsonMetadata",
            "labels.author.id",
            "labels.author.email",
            "labels.createdAt",
            "labels.id",
            "labels.jsonResponse",
            "skipped",
            "status",
        ),
        asset_id_in: Optional[List[str]] = None,
        asset_id_not_in: Optional[List[str]] = None,
        consensus_mark_gt: Optional[float] = None,
        consensus_mark_lt: Optional[float] = None,
        disable_tqdm: Optional[bool] = None,
        external_id_contains: Optional[List[str]] = None,
        first: Optional[int] = None,
        format: Optional[str] = None,
        honeypot_mark_gt: Optional[float] = None,
        honeypot_mark_lt: Optional[float] = None,
        label_author_in: Optional[List[str]] = None,
        label_consensus_mark_gt: Optional[float] = None,
        label_consensus_mark_lt: Optional[float] = None,
        label_created_at: Optional[str] = None,
        label_created_at_gt: Optional[str] = None,
        label_created_at_lt: Optional[str] = None,
        label_honeypot_mark_gt: Optional[float] = None,
        label_honeypot_mark_lt: Optional[float] = None,
        label_type_in: Optional[List[LabelType]] = None,
        metadata_where: Optional[dict] = None,
        skipped: Optional[bool] = None,
        status_in: Optional[List[AssetStatus]] = None,
        updated_at_gte: Optional[str] = None,
        updated_at_lte: Optional[str] = None,
        label_category_search: Optional[str] = None,
        download_media: bool = False,
        local_media_dir: Optional[str] = None,
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
        label_output_format: Literal["dict", "parsed_label"] = "dict",
        *,
        as_generator: bool = False,
    ) -> Union[Iterable[Dict], "pd.DataFrame"]:
        # pylint: disable=line-too-long
        """Get an asset list, an asset generator or a pandas DataFrame that match a set of constraints.

        Args:
            project_id: Identifier of the project.
            asset_id: Identifier of the asset to retrieve.
            asset_id_in: A list of the IDs of the assets to retrieve.
            asset_id_not_in: A list of the IDs of the assets to exclude.
            skip: Number of assets to skip (they are ordered by their date of creation, first to last).
            fields: All the fields to request among the possible fields for the assets.
                    See [the documentation](https://docs.kili-technology.com/reference/graphql-api#asset) for all possible fields.
            first: Maximum number of assets to return.
            consensus_mark_gt: Deprecated. Use `consensus_mark_gte` instead.
            consensus_mark_lt: Deprecated. Use `consensus_mark_lte` instead.
            external_id_contains: Deprecated. Use `external_id_strictly_in` instead.
            metadata_where: Filters by the values of the metadata of the asset.
            honeypot_mark_gt: Deprecated. Use `honeypot_mark_gte` instead.
            honeypot_mark_lt: Deprecated. Use `honeypot_mark_lte` instead.
            status_in: Returned assets should have a status that belongs to that list, if given.
                Possible choices: `TODO`, `ONGOING`, `LABELED`, `TO_REVIEW` or `REVIEWED`.
            label_type_in: Returned assets should have a label whose type belongs to that list, if given.
            label_author_in: Returned assets should have a label whose author belongs to that list, if given. An author can be designated by the first name, the last name, or the first name + last name.
            label_consensus_mark_gt: Deprecated. Use `label_consensus_mark_gte` instead.
            label_consensus_mark_lt: Deprecated. Use `label_consensus_mark_lte` instead.
            label_created_at: Returned assets should have a label whose creation date is equal to this date.
            label_created_at_gt: Deprecated. Use `label_created_at_gte` instead.
            label_created_at_lt: Deprecated. Use `label_created_at_lte` instead.
            label_honeypot_mark_gt: Deprecated. Use `label_honeypot_mark_gte` instead.
            label_honeypot_mark_lt: Deprecated. Use `label_honeypot_mark_lte` instead.
            skipped: Returned assets should be skipped
            updated_at_gte: Returned assets should have a label whose update date is greater or equal to this date.
            updated_at_lte: Returned assets should have a label whose update date is lower or equal to this date.
            format: If equal to 'pandas', returns a pandas DataFrame
            disable_tqdm: If `True`, the progress bar will be disabled
            as_generator: If `True`, a generator on the assets is returned.
            label_category_search: Returned assets should have a label that follows this category search query.
            download_media: Tell is the media have to be downloaded or not.
            local_media_dir: Directory where the media are downloaded if `download_media` is True.
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
            label_output_format: If `parsed_label`, the labels in the assets will be parsed. More information on parsed labels in the [documentation](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/label_parsing/).

        !!! info "Dates format"
            Date strings should have format: "YYYY-MM-DD"

        !!! info "Filtering by label properties"
            When the assets are filtered by label properties using any of `label_*` filter arguments, as soon as **one**
            label matches **all** the label property criteria, the asset is kept and returned by the method. If any of the
            `labels.*` or `latestLabel.*` subfields are queried, **all** the labels of the kept assets are returned together
            with the assets (and not only the ones matching the criteria)

        Returns:
            An asset list, an asset generator or a pandas DataFrame that match a set of constraints.

        Example:
            ```
            # returns the assets list of the project
            >>> kili.assets(project_id)
            >>> kili.assets(project_id, asset_id=asset_id)
            # returns a generator of the project assets
            >>> kili.assets(project_id, as_generator=True)
            ```

        !!! example "How to filter based on Metadata"
            - `metadata_where = {key1: "value1"}` to filter on assets whose metadata
                have key "key1" with value "value1"
            - `metadata_where = {key1: ["value1", "value2"]}` to filter on assets whose metadata
                have key "key1" with value "value1" or value "value2
            - `metadata_where = {key2: [2, 10]}` to filter on assets whose metadata
                have key "key2" with a value between 2 and 10.

        !!! example "How to filter based on label categories"
            The search query is composed of logical expressions following this format:

                [job_name].[category_name].count [comparaison_operator] [value]
            where:

            - `[job_name]` is the name of the job in the interface
            - `[category_name]` is the name of the category in the interface for this job
            - `[comparaison_operator]` can be one of: [`==`, `>=`, `<=`, `<`, `>`]
            - `[value]` is an integer that represents the count of such objects of the given category in the label

            These operations can be separated by OR and AND operators:
                ```python
                label_category_search = `JOB_CLASSIF.CATEGORY_A.count > 0`
                label_category_search = `JOB_CLASSIF.CATEGORY_A.count > 0 OR JOB_NER.CATEGORY_B.count > 0`
                label_category_search = `(JOB_CLASSIF.CATEGORY_A.count == 1 OR JOB_NER.CATEGORY_B.count > 0) AND JOB_BBOX.CATEGORY_C.count > 10`
                ```
        """
        if format == "pandas" and as_generator:
            raise ValueError(
                'Argument values as_generator==True and format=="pandas" are not compatible.'
            )

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

        disable_tqdm = disable_tqdm_if_as_generator(as_generator, disable_tqdm)

        asset_use_cases = AssetUseCases(self.kili_api_gateway)
        filters = AssetFilters(
            project_id=ProjectId(project_id),
            asset_id=AssetId(asset_id) if asset_id else None,
            asset_id_in=cast(List[AssetId], asset_id_in) if asset_id_in else None,
            asset_id_not_in=cast(List[AssetId], asset_id_not_in) if asset_id_not_in else None,
            consensus_mark_gte=consensus_mark_gt or consensus_mark_gte,
            consensus_mark_lte=consensus_mark_lt or consensus_mark_lte,
            external_id_strictly_in=(
                cast(List[AssetExternalId], external_id_strictly_in or external_id_contains)
                if external_id_strictly_in or external_id_contains
                else None
            ),
            external_id_in=cast(List[AssetExternalId], external_id_in) if external_id_in else None,
            honeypot_mark_gte=honeypot_mark_gt or honeypot_mark_gte,
            honeypot_mark_lte=honeypot_mark_lt or honeypot_mark_lte,
            inference_mark_gte=inference_mark_gte,
            inference_mark_lte=inference_mark_lte,
            label_author_in=label_author_in,
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
            label_reviewer_in=label_reviewer_in,
            issue_status=issue_status,
            issue_type=issue_type,
        )
        assets_gen = asset_use_cases.list_assets(
            filters,
            fields,
            download_media=download_media,
            local_media_dir=local_media_dir,
            label_output_format=label_output_format,
            options=QueryOptions(disable_tqdm=disable_tqdm, first=first, skip=skip),
        )

        if format == "pandas":
            import pandas as pd  # pylint: disable=import-outside-toplevel

            return pd.DataFrame(list(assets_gen))

        if as_generator:
            return assets_gen
        return list(assets_gen)

    # pylint: disable=too-many-arguments,too-many-locals
    @typechecked
    def count_assets(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_id_in: Optional[List[str]] = None,
        asset_id_not_in: Optional[List[str]] = None,
        external_id_contains: Optional[List[str]] = None,
        metadata_where: Optional[dict] = None,
        status_in: Optional[List[AssetStatus]] = None,
        consensus_mark_gt: Optional[float] = None,
        consensus_mark_lt: Optional[float] = None,
        honeypot_mark_gt: Optional[float] = None,
        honeypot_mark_lt: Optional[float] = None,
        label_type_in: Optional[List[LabelType]] = None,
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
        issue_type: Optional[IssueType] = None,
        issue_status: Optional[IssueStatus] = None,
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

        filters = AssetFilters(
            project_id=ProjectId(project_id),
            asset_id=AssetId(asset_id) if asset_id else None,
            asset_id_in=cast(List[AssetId], asset_id_in) if asset_id_in else None,
            asset_id_not_in=cast(List[AssetId], asset_id_not_in) if asset_id_not_in else None,
            consensus_mark_gte=consensus_mark_gt or consensus_mark_gte,
            consensus_mark_lte=consensus_mark_lt or consensus_mark_lte,
            external_id_strictly_in=(
                cast(List[AssetExternalId], external_id_strictly_in or external_id_contains)
                if external_id_strictly_in or external_id_contains
                else None
            ),
            external_id_in=cast(List[AssetExternalId], external_id_in) if external_id_in else None,
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
        asset_use_cases = AssetUseCases(self.kili_api_gateway)
        return asset_use_cases.count_assets(filters)
