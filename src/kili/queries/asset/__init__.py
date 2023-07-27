"""Asset queries."""

from typing import Dict, Generator, Iterable, List, Optional, Union, overload

import pandas as pd
from typeguard import typechecked
from typing_extensions import Literal

from kili.authentication import KiliAuth
from kili.graphql import QueryOptions
from kili.graphql.operations.asset.queries import AssetQuery, AssetWhere
from kili.helpers import disable_tqdm_if_as_generator, validate_category_search_query
from kili.queries.asset.media_downloader import get_download_assets_function
from kili.utils.logcontext import for_all_methods, log_call


@for_all_methods(log_call, exclude=["__init__"])
class QueriesAsset:
    """
    Set of Asset queries
    """

    # pylint: disable=too-many-arguments,too-many-locals,dangerous-default-value,redefined-builtin

    def __init__(self, auth: KiliAuth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    @overload
    def assets(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        skip: int = 0,
        fields: List[str] = [
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
        ],
        asset_id_in: Optional[List[str]] = None,
        consensus_mark_gt: Optional[float] = None,
        consensus_mark_lt: Optional[float] = None,
        disable_tqdm: bool = False,
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
        label_type_in: Optional[List[str]] = None,
        metadata_where: Optional[dict] = None,
        skipped: Optional[bool] = None,
        status_in: Optional[List[str]] = None,
        updated_at_gte: Optional[str] = None,
        updated_at_lte: Optional[str] = None,
        label_category_search: Optional[str] = None,
        download_media: bool = False,
        local_media_dir: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
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
        fields: List[str] = [
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
        ],
        asset_id_in: Optional[List[str]] = None,
        consensus_mark_gt: Optional[float] = None,
        consensus_mark_lt: Optional[float] = None,
        disable_tqdm: bool = False,
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
        label_type_in: Optional[List[str]] = None,
        metadata_where: Optional[dict] = None,
        skipped: Optional[bool] = None,
        status_in: Optional[List[str]] = None,
        updated_at_gte: Optional[str] = None,
        updated_at_lte: Optional[str] = None,
        label_category_search: Optional[str] = None,
        download_media: bool = False,
        local_media_dir: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
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
        fields: List[str] = [
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
        ],
        asset_id_in: Optional[List[str]] = None,
        consensus_mark_gt: Optional[float] = None,
        consensus_mark_lt: Optional[float] = None,
        disable_tqdm: bool = False,
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
        label_type_in: Optional[List[str]] = None,
        metadata_where: Optional[dict] = None,
        skipped: Optional[bool] = None,
        status_in: Optional[List[str]] = None,
        updated_at_gte: Optional[str] = None,
        updated_at_lte: Optional[str] = None,
        label_category_search: Optional[str] = None,
        download_media: bool = False,
        local_media_dir: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
        *,
        as_generator: bool = False,
    ) -> Union[Iterable[Dict], pd.DataFrame]:
        # pylint: disable=line-too-long
        """Get an asset list, an asset generator or a pandas DataFrame that match a set of constraints.

        Args:
            project_id: Identifier of the project.
            asset_id: Identifier of the asset to retrieve.
            asset_id_in: A list of the IDs of the assets to retrieve.
            skip: Number of assets to skip (they are ordered by their date of creation, first to last).
            fields: All the fields to request among the possible fields for the assets.
                    See [the documentation](https://docs.kili-technology.com/reference/graphql-api#asset) for all possible fields.
            first: Maximum number of assets to return.
            consensus_mark_gt: Minimum amount of consensus for the asset.
            consensus_mark_lt: Maximum amount of consensus for the asset.
            external_id_contains: Returned assets have an external id that belongs to that list, if given.
            metadata_where: Filters by the values of the metadata of the asset.
            honeypot_mark_gt: Minimum amount of honeypot for the asset.
            honeypot_mark_lt : Maximum amount of honeypot for the asset.
            status_in: Returned assets should have a status that belongs to that list, if given.
                Possible choices: `TODO`, `ONGOING`, `LABELED`, `TO_REVIEW` or `REVIEWED`
            label_type_in: Returned assets should have a label whose type belongs to that list, if given.
            label_author_in: Returned assets should have a label whose status belongs to that list, if given.
            label_consensus_mark_gt: Returned assets should have a label whose consensus is greater than this number.
            label_consensus_mark_lt: Returned assets should have a label whose consensus is lower than this number.
            label_created_at: Returned assets should have a label whose creation date is equal to this date.
            label_created_at_gt: Returned assets should have a label whose creation date is greater than this date.
            label_created_at_lt: Returned assets should have a label whose creation date is lower than this date.
            label_honeypot_mark_gt: Returned assets should have a label whose honeypot is greater than this number
            label_honeypot_mark_lt: Returned assets should have a label whose honeypot is lower than this number
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

        !!! info "Dates format"
            Date strings should have format: "YYYY-MM-DD"

        Returns:
            A result object which contains the query if it was successful,
                or an error message.

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

            These operations can be separated by OR and AND operators

            Example:

                label_category_search = `JOB_CLASSIF.CATEGORY_A.count > 0`
                label_category_search = `JOB_CLASSIF.CATEGORY_A.count > 0 OR JOB_NER.CATEGORY_B.count > 0`
                label_category_search = `(JOB_CLASSIF.CATEGORY_A.count == 1 OR JOB_NER.CATEGORY_B.count > 0) AND JOB_BBOX.CATEGORY_C.count > 10`
        """
        if format == "pandas" and as_generator:
            raise ValueError(
                'Argument values as_generator==True and format=="pandas" are not compatible.'
            )

        if label_category_search:
            validate_category_search_query(label_category_search)

        where = AssetWhere(
            project_id=project_id,
            asset_id=asset_id,
            asset_id_in=asset_id_in,
            consensus_mark_gt=consensus_mark_gt,
            consensus_mark_lt=consensus_mark_lt,
            external_id_contains=external_id_contains,
            honeypot_mark_gt=honeypot_mark_gt,
            honeypot_mark_lt=honeypot_mark_lt,
            label_author_in=label_author_in,
            label_consensus_mark_gt=label_consensus_mark_gt,
            label_consensus_mark_lt=label_consensus_mark_lt,
            label_created_at=label_created_at,
            label_created_at_gt=label_created_at_gt,
            label_created_at_lt=label_created_at_lt,
            label_honeypot_mark_gt=label_honeypot_mark_gt,
            label_honeypot_mark_lt=label_honeypot_mark_lt,
            label_type_in=label_type_in,
            metadata_where=metadata_where,
            skipped=skipped,
            status_in=status_in,
            updated_at_gte=updated_at_gte,
            updated_at_lte=updated_at_lte,
            label_category_search=label_category_search,
            created_at_gte=created_at_gte,
            created_at_lte=created_at_lte,
        )
        disable_tqdm = disable_tqdm_if_as_generator(as_generator, disable_tqdm)
        options = QueryOptions(disable_tqdm, first, skip)
        post_call_function, fields = get_download_assets_function(
            self.auth, download_media, fields, project_id, local_media_dir
        )
        assets_gen = AssetQuery(self.auth.client, self.auth.ssl_verify)(
            where, fields, options, post_call_function
        )

        if format == "pandas":
            return pd.DataFrame(list(assets_gen))
        if as_generator:
            return assets_gen
        return list(assets_gen)

    @typechecked
    def count_assets(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_id_in: Optional[List[str]] = None,
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
    ) -> int:
        """Count and return the number of assets with the given constraints.

        Parameters beginning with 'label_' apply to labels, others apply to assets.

        Args:
            project_id: Identifier of the project
            asset_id: The unique id of the asset to retrieve.
            asset_id_in: A list of the ids of the assets to retrieve.
            external_id_contains: Returned assets should have an external id
                that belongs to that list, if given.
            metadata_where: Filters by the values of the metadata of the asset.
            status_in: Returned assets should have a status that belongs to that list, if given.
                Possible choices: `TODO`, `ONGOING`, `LABELED` or `REVIEWED`
            consensus_mark_gt: Minimum amount of consensus for the asset.
            consensus_mark_lt: Maximum amount of consensus for the asset.
            honeypot_mark_gt: Minimum amount of honeypot for the asset.
            honeypot_mark_lt: Maximum amount of consensus for the asset.
            label_type_in: Returned assets should have a label
                whose type belongs to that list, if given.
            label_author_in: Returned assets should have a label
                whose status belongs to that list, if given.
            label_consensus_mark_gt: Returned assets should have a label
                whose consensus is greater than this number.
            label_consensus_mark_lt: Returned assets should have a label
                whose consensus is lower than this number.
            label_created_at: Returned assets should have a label
                whose creation date is equal to this date.
            label_created_at_gt: Returned assets should have a label
                whose creation date is greater than this date.
            label_created_at_lt: Returned assets should have a label
                whose creation date is lower than this date.
            label_honeypot_mark_gt: Returned assets should have a label
                whose honeypot is greater than this number.
            label_honeypot_mark_lt: Returned assets should have a label
                whose honeypot is lower than this number.
            skipped: Returned assets should be skipped
            updated_at_gte: Returned assets should have a label
                whose update date is greated or equal to this date.
            updated_at_lte: Returned assets should have a label
                whose update date is lower or equal to this date.

        !!! info "Dates format"
            Date strings should have format: "YYYY-MM-DD"

        Returns:
            A result object which contains the query if it was successful,
                or an error message.

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

        where = AssetWhere(
            project_id=project_id,
            asset_id=asset_id,
            asset_id_in=asset_id_in,
            consensus_mark_gt=consensus_mark_gt,
            consensus_mark_lt=consensus_mark_lt,
            external_id_contains=external_id_contains,
            honeypot_mark_gt=honeypot_mark_gt,
            honeypot_mark_lt=honeypot_mark_lt,
            label_author_in=label_author_in,
            label_consensus_mark_gt=label_consensus_mark_gt,
            label_consensus_mark_lt=label_consensus_mark_lt,
            label_created_at=label_created_at,
            label_created_at_gt=label_created_at_gt,
            label_created_at_lt=label_created_at_lt,
            label_honeypot_mark_gt=label_honeypot_mark_gt,
            label_honeypot_mark_lt=label_honeypot_mark_lt,
            label_type_in=label_type_in,
            metadata_where=metadata_where,
            skipped=skipped,
            status_in=status_in,
            updated_at_gte=updated_at_gte,
            updated_at_lte=updated_at_lte,
            label_category_search=label_category_search,
            created_at_gte=created_at_gte,
            created_at_lte=created_at_lte,
        )
        return AssetQuery(self.auth.client, self.auth.ssl_verify).count(where)
