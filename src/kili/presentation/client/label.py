"""Client presentation methods for labels."""

from typing import (
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
from kili.core.helpers import is_empty_list_with_warning, validate_category_search_query
from kili.domain.asset import AssetExternalId, AssetFilters, AssetStatus
from kili.domain.asset.asset import AssetId
from kili.domain.label import LabelFilters, LabelId, LabelType
from kili.domain.project import ProjectFilters, ProjectId
from kili.domain.types import ListOrTuple
from kili.domain.user import UserFilter, UserId
from kili.presentation.client.helpers.common_validators import (
    disable_tqdm_if_as_generator,
)
from kili.use_cases.label import LabelUseCases
from kili.utils.labels.parsing import ParsedLabel
from kili.utils.logcontext import for_all_methods, log_call

from .base import BaseClientMethods


@for_all_methods(log_call, exclude=["__init__"])
class LabelClientMethods(BaseClientMethods):
    """Methods attached to the Kili client, to run actions on labels."""

    @typechecked
    def count_labels(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[List[AssetStatus]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        asset_external_id_strictly_in: Optional[List[str]] = None,
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
        # pylint: disable=line-too-long
        """Get the number of labels for the given parameters.

        Args:
            project_id: Identifier of the project.
            asset_id: Identifier of the asset.
            asset_status_in: Returned labels should have a status that belongs to that list, if given.
                Possible choices : `TODO`, `ONGOING`, `LABELED` or `REVIEWED`
            asset_external_id_in: Returned labels should have an external id that belongs to that list, if given.
            asset_external_id_strictly_in: Returned labels should have an external id that exactly matches one of the ids in that list, if given.
            author_in: Returned labels should have been made by authors in that list, if given.
                An author can be designated by the first name, the last name, or the first name + last name.
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

        !!! info "Dates format"
            Date strings should have format: "YYYY-MM-DD"

        Returns:
            The number of labels with the parameters provided
        """
        if category_search:
            validate_category_search_query(category_search)

        filters = LabelFilters(
            project=ProjectFilters(id=ProjectId(project_id)),
            asset=AssetFilters(
                project_id=ProjectId(project_id),
                asset_id=AssetId(asset_id) if asset_id else None,
                status_in=asset_status_in,
                external_id_in=(
                    cast(ListOrTuple[AssetExternalId], asset_external_id_in)
                    if asset_external_id_in
                    else None
                ),
                external_id_strictly_in=(
                    cast(ListOrTuple[AssetExternalId], asset_external_id_strictly_in)
                    if asset_external_id_strictly_in
                    else None
                ),
            ),
            author_in=author_in,
            created_at=created_at,
            created_at_gte=created_at_gte,
            created_at_lte=created_at_lte,
            honeypot_mark_gte=honeypot_mark_gte,
            honeypot_mark_lte=honeypot_mark_lte,
            id_in=cast(List[LabelId], id_contains) if id_contains else None,
            id=LabelId(label_id) if label_id else None,
            type_in=type_in,
            user=UserFilter(id=UserId(user_id)) if user_id else None,
            search=category_search,
            consensus_mark_gte=None,
            consensus_mark_lte=None,
            labeler_in=None,
            reviewer_in=None,
        )

        return LabelUseCases(self.kili_api_gateway).count_labels(filters=filters)

    @overload
    def labels(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[ListOrTuple[AssetStatus]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        asset_external_id_strictly_in: Optional[List[str]] = None,
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
    ) -> Generator[Dict, None, None]: ...

    @overload
    def labels(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[ListOrTuple[AssetStatus]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        asset_external_id_strictly_in: Optional[List[str]] = None,
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
    ) -> List[Dict]: ...

    @overload
    def labels(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[ListOrTuple[AssetStatus]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        asset_external_id_strictly_in: Optional[List[str]] = None,
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
    ) -> List[ParsedLabel]: ...

    @overload
    def labels(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[ListOrTuple[AssetStatus]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        asset_external_id_strictly_in: Optional[List[str]] = None,
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
    ) -> Generator[ParsedLabel, None, None]: ...

    @typechecked
    def labels(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[ListOrTuple[AssetStatus]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        asset_external_id_strictly_in: Optional[List[str]] = None,
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
        # pylint: disable=line-too-long
        """Get a label list or a label generator from a project based on a set of criteria.

        Args:
            project_id: Identifier of the project.
            asset_id: Identifier of the asset.
            asset_status_in: Returned labels should have a status that belongs to that list, if given.
                Possible choices : `TODO`, `ONGOING`, `LABELED`, `TO REVIEW` or `REVIEWED`.
            asset_external_id_in: Returned labels should have an external id that belongs to that list, if given.
            asset_external_id_strictly_in: Returned labels should have an external id that exactly matches one of the ids in that list, if given.
            author_in: Returned labels should have been made by authors in that list, if given.
                An author can be designated by the first name, the last name, or the first name + last name.
            created_at: Returned labels should have their creation date equal to this date.
            created_at_gte: Returned labels should have their creation date greater or equal to this date.
            created_at_lte: Returned labels should have their creation date lower or equal to this date.
            fields: All the fields to request among the possible fields for the labels.
                See [the documentation](https://docs.kili-technology.com/reference/graphql-api#label) for all possible fields.
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
                If `parsed_label`, the output is an iterable of parsed labels objects. More information on parsed labels in the [documentation](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/label_parsing/).

        !!! info "Dates format"
            Date strings should have format: "YYYY-MM-DD"

        Returns:
            An iterable of labels.

        Examples:
            >>> kili.labels(project_id=project_id, fields=['jsonResponse', 'labelOf.externalId']) # returns a list of all labels of a project and their assets external ID
            >>> kili.labels(project_id=project_id, fields=['jsonResponse'], as_generator=True) # returns a generator of all labels of a project

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
                category_search = `JOB_CLASSIF.CATEGORY_A.count > 0`
                category_search = `JOB_CLASSIF.CATEGORY_A.count > 0 OR JOB_NER.CATEGORY_B.count > 0`
                category_search = `(JOB_CLASSIF.CATEGORY_A.count > 0 OR JOB_NER.CATEGORY_B.count > 0) AND JOB_BBOX.CATEGORY_C.count > 10`
        """
        if category_search:
            validate_category_search_query(category_search)

        disable_tqdm = disable_tqdm_if_as_generator(as_generator, disable_tqdm)
        options = QueryOptions(disable_tqdm, first, skip)

        filters = LabelFilters(
            project=ProjectFilters(id=ProjectId(project_id)),
            asset=AssetFilters(
                project_id=ProjectId(project_id),
                asset_id=AssetId(asset_id) if asset_id else None,
                status_in=asset_status_in,
                external_id_in=(
                    cast(ListOrTuple[AssetExternalId], asset_external_id_in)
                    if asset_external_id_in
                    else None
                ),
                external_id_strictly_in=(
                    cast(ListOrTuple[AssetExternalId], asset_external_id_strictly_in)
                    if asset_external_id_strictly_in
                    else None
                ),
            ),
            author_in=author_in,
            created_at=created_at,
            created_at_gte=created_at_gte,
            created_at_lte=created_at_lte,
            honeypot_mark_gte=honeypot_mark_gte,
            honeypot_mark_lte=honeypot_mark_lte,
            id_in=cast(List[LabelId], id_contains) if id_contains else None,
            id=LabelId(label_id) if label_id else None,
            type_in=type_in,
            user=UserFilter(id=UserId(user_id)) if user_id else None,
            search=category_search,
            consensus_mark_gte=None,
            consensus_mark_lte=None,
            labeler_in=None,
            reviewer_in=None,
        )

        labels_gen = LabelUseCases(self.kili_api_gateway).list_labels(
            filters=filters,
            options=options,
            fields=fields,
            output_format=output_format,
            project_id=ProjectId(project_id),
        )

        if as_generator:
            return labels_gen
        return list(labels_gen)

    @overload
    def predictions(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[ListOrTuple[AssetStatus]] = None,
        asset_external_id_in: Optional[List[str]] = None,
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
    ) -> Generator[Dict, None, None]: ...

    @overload
    def predictions(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[ListOrTuple[AssetStatus]] = None,
        asset_external_id_in: Optional[List[str]] = None,
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
    ) -> List[Dict]: ...

    @typechecked
    def predictions(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[ListOrTuple[AssetStatus]] = None,
        asset_external_id_in: Optional[List[str]] = None,
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
        # pylint: disable=line-too-long
        """Get prediction labels from a project based on a set of criteria.

        This method is equivalent to the `kili.labels()` method, but it only returns label of type "PREDICTION".

        Args:
            project_id: Identifier of the project.
            asset_id: Identifier of the asset.
            asset_status_in: Returned labels should have a status that belongs to that list, if given.
                Possible choices : `TODO`, `ONGOING`, `LABELED`, `TO REVIEW` or `REVIEWED`
            asset_external_id_in: Returned labels should have an external id that belongs to that list, if given.
            author_in: Returned labels should have been made by authors in that list, if given.
                An author can be designated by the first name, the last name, or the first name + last name.
            created_at: Returned labels should have a label whose creation date is equal to this date.
            created_at_gte: Returned labels should have a label whose creation date is greater than this date.
            created_at_lte: Returned labels should have a label whose creation date is lower than this date.
            fields: All the fields to request among the possible fields for the labels.
                See [the documentation](https://docs.kili-technology.com/reference/graphql-api#label) for all possible fields.
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

        Examples:
            >>> kili.predictions(project_id=project_id) # returns a list of prediction labels of a project
        """
        return self.labels(
            project_id=project_id,
            asset_id=asset_id,
            asset_status_in=asset_status_in,
            asset_external_id_in=asset_external_id_in,
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
            type_in=["PREDICTION"],
            user_id=user_id,
            disable_tqdm=disable_tqdm,
            category_search=category_search,
            as_generator=as_generator,  # pyright: ignore[reportGeneralTypeIssues]
        )

    @overload
    def inferences(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[ListOrTuple[AssetStatus]] = None,
        asset_external_id_in: Optional[List[str]] = None,
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
    ) -> Generator[Dict, None, None]: ...

    @overload
    def inferences(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[ListOrTuple[AssetStatus]] = None,
        asset_external_id_in: Optional[List[str]] = None,
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
    ) -> List[Dict]: ...

    @typechecked
    def inferences(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[ListOrTuple[AssetStatus]] = None,
        asset_external_id_in: Optional[List[str]] = None,
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
        # pylint: disable=line-too-long
        """Get inference labels from a project based on a set of criteria.

        This method is equivalent to the `kili.labels()` method, but it only returns label of type "INFERENCE".

        Args:
            project_id: Identifier of the project.
            asset_id: Identifier of the asset.
            asset_status_in: Returned labels should have a status that belongs to that list, if given.
                Possible choices : `TODO`, `ONGOING`, `LABELED`, `TO REVIEW` or `REVIEWED`
            asset_external_id_in: Returned labels should have an external id that belongs to that list, if given.
            author_in: Returned labels should have been made by authors in that list, if given.
                An author can be designated by the first name, the last name, or the first name + last name.
            created_at: Returned labels should have a label whose creation date is equal to this date.
            created_at_gte: Returned labels should have a label whose creation date is greater than this date.
            created_at_lte: Returned labels should have a label whose creation date is lower than this date.
            fields: All the fields to request among the possible fields for the labels.
                See [the documentation](https://docs.kili-technology.com/reference/graphql-api#label) for all possible fields.
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

        Examples:
            >>> kili.inferences(project_id=project_id) # returns a list of inference labels of a project
        """
        return self.labels(
            project_id=project_id,
            asset_id=asset_id,
            asset_status_in=asset_status_in,
            asset_external_id_in=asset_external_id_in,
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
            type_in=["INFERENCE"],
            user_id=user_id,
            disable_tqdm=disable_tqdm,
            category_search=category_search,
            as_generator=as_generator,  # pyright: ignore[reportGeneralTypeIssues]
        )

    @typechecked
    def update_properties_in_label(
        self,
        label_id: str,
        seconds_to_label: Optional[int] = None,
        model_name: Optional[str] = None,
        json_response: Optional[dict] = None,
    ) -> Dict[Literal["id"], str]:
        """Update properties of a label.

        Args:
            label_id: Identifier of the label
            seconds_to_label: Time to create the label
            model_name: Name of the model
            json_response: The label is given here

        Returns:
            A dictionary with the label `id`.

        Examples:
            >>> kili.update_properties_in_label(label_id=label_id, json_response={...})
        """
        return LabelUseCases(self.kili_api_gateway).update_properties_in_label(
            label_id=LabelId(label_id),
            seconds_to_label=seconds_to_label,
            model_name=model_name,
            json_response=json_response,
            fields=("id",),
        )

    @typechecked
    def delete_labels(
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
        if is_empty_list_with_warning("delete_labels", "ids", ids):
            return []

        return LabelUseCases(self.kili_api_gateway).delete_labels(
            ids=cast(ListOrTuple[LabelId], ids),
            disable_tqdm=disable_tqdm,
        )
