"""Label queries."""

from functools import partial
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

import pandas as pd
from typeguard import typechecked

from kili.core.graphql import QueryOptions
from kili.core.graphql.operations.asset.queries import AssetQuery, AssetWhere
from kili.core.graphql.operations.label.queries import LabelQuery, LabelWhere
from kili.core.helpers import (
    disable_tqdm_if_as_generator,
    validate_category_search_query,
)
from kili.entrypoints.base import BaseOperationEntrypointMixin
from kili.services.export import export_labels
from kili.services.export.exceptions import NoCompatibleJobError
from kili.services.export.types import CocoAnnotationModifier, LabelFormat, SplitOption
from kili.services.helpers import infer_ids_from_external_ids
from kili.services.project import get_project
from kili.services.types import ProjectId
from kili.utils.labels.parsing import ParsedLabel, parse_labels
from kili.utils.logcontext import for_all_methods, log_call


@for_all_methods(log_call, exclude=["__init__"])
class QueriesLabel(BaseOperationEntrypointMixin):
    """Set of Label queries."""

    # pylint: disable=too-many-arguments,too-many-locals,dangerous-default-value

    @overload
    def labels(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[List[str]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        author_in: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
        fields: List[str] = [
            "author.email",
            "author.id",
            "id",
            "jsonResponse",
            "labelType",
            "secondsToLabel",
            "assetId",
        ],
        first: Optional[int] = None,
        honeypot_mark_gte: Optional[float] = None,
        honeypot_mark_lte: Optional[float] = None,
        id_contains: Optional[List[str]] = None,
        label_id: Optional[str] = None,
        skip: int = 0,
        type_in: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        disable_tqdm: bool = False,
        category_search: Optional[str] = None,
        output_format: Literal["dict"] = "dict",
        *,
        as_generator: Literal[True],
    ) -> Generator[Dict, None, None]:
        ...

    @overload
    def labels(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[List[str]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        author_in: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
        fields: List[str] = [
            "author.email",
            "author.id",
            "id",
            "jsonResponse",
            "labelType",
            "secondsToLabel",
            "assetId",
        ],
        first: Optional[int] = None,
        honeypot_mark_gte: Optional[float] = None,
        honeypot_mark_lte: Optional[float] = None,
        id_contains: Optional[List[str]] = None,
        label_id: Optional[str] = None,
        skip: int = 0,
        type_in: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        disable_tqdm: bool = False,
        category_search: Optional[str] = None,
        output_format: Literal["dict"] = "dict",
        *,
        as_generator: Literal[False] = False,
    ) -> List[Dict]:
        ...

    @overload
    def labels(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[List[str]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        author_in: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
        fields: List[str] = [
            "author.email",
            "author.id",
            "id",
            "jsonResponse",
            "labelType",
            "secondsToLabel",
            "assetId",
        ],
        first: Optional[int] = None,
        honeypot_mark_gte: Optional[float] = None,
        honeypot_mark_lte: Optional[float] = None,
        id_contains: Optional[List[str]] = None,
        label_id: Optional[str] = None,
        skip: int = 0,
        type_in: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        disable_tqdm: bool = False,
        category_search: Optional[str] = None,
        output_format: Literal["parsed_label"] = "parsed_label",
        *,
        as_generator: Literal[False] = False,
    ) -> List[ParsedLabel]:
        ...

    @overload
    def labels(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[List[str]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        author_in: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
        fields: List[str] = [
            "author.email",
            "author.id",
            "id",
            "jsonResponse",
            "labelType",
            "secondsToLabel",
            "assetId",
        ],
        first: Optional[int] = None,
        honeypot_mark_gte: Optional[float] = None,
        honeypot_mark_lte: Optional[float] = None,
        id_contains: Optional[List[str]] = None,
        label_id: Optional[str] = None,
        skip: int = 0,
        type_in: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        disable_tqdm: bool = False,
        category_search: Optional[str] = None,
        output_format: Literal["parsed_label"] = "parsed_label",
        *,
        as_generator: Literal[True] = True,
    ) -> Generator[ParsedLabel, None, None]:
        ...

    @typechecked
    def labels(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[List[str]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        author_in: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
        fields: List[str] = [
            "author.email",
            "author.id",
            "id",
            "jsonResponse",
            "labelType",
            "secondsToLabel",
            "isLatestLabelForUser",
            "assetId",
        ],
        first: Optional[int] = None,
        honeypot_mark_gte: Optional[float] = None,
        honeypot_mark_lte: Optional[float] = None,
        id_contains: Optional[List[str]] = None,
        label_id: Optional[str] = None,
        skip: int = 0,
        type_in: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        disable_tqdm: bool = False,
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

        where = LabelWhere(
            project_id=project_id,
            asset_id=asset_id,
            asset_status_in=asset_status_in,
            asset_external_id_in=asset_external_id_in,
            author_in=author_in,
            created_at=created_at,
            created_at_gte=created_at_gte,
            created_at_lte=created_at_lte,
            honeypot_mark_gte=honeypot_mark_gte,
            honeypot_mark_lte=honeypot_mark_lte,
            id_contains=id_contains,
            label_id=label_id,
            type_in=type_in,
            user_id=user_id,
            category_search=category_search,
        )

        post_call_function = None
        if output_format == "parsed_label":
            if "jsonResponse" not in fields:
                raise ValueError(
                    "The field 'jsonResponse' is required to parse labels. Please add it to the"
                    " 'fields' argument."
                )

            project = get_project(self, project_id, ["jsonInterface", "inputType"])

            post_call_function = partial(
                parse_labels,
                json_interface=project["jsonInterface"],
                input_type=project["inputType"],
            )

        disable_tqdm = disable_tqdm_if_as_generator(as_generator, disable_tqdm)
        options = QueryOptions(disable_tqdm, first, skip)
        labels_gen = LabelQuery(self.graphql_client, self.http_client)(
            where, fields, options, post_call_function
        )

        if as_generator:
            return labels_gen
        return list(labels_gen)

    @overload
    def predictions(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[List[str]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        author_in: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
        fields: Optional[List[str]] = None,
        first: Optional[int] = None,
        honeypot_mark_gte: Optional[float] = None,
        honeypot_mark_lte: Optional[float] = None,
        id_contains: Optional[List[str]] = None,
        label_id: Optional[str] = None,
        skip: int = 0,
        user_id: Optional[str] = None,
        disable_tqdm: bool = False,
        category_search: Optional[str] = None,
        *,
        as_generator: Literal[True],
    ) -> Generator[Dict, None, None]:
        ...

    @overload
    def predictions(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[List[str]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        author_in: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
        fields: Optional[List[str]] = None,
        first: Optional[int] = None,
        honeypot_mark_gte: Optional[float] = None,
        honeypot_mark_lte: Optional[float] = None,
        id_contains: Optional[List[str]] = None,
        label_id: Optional[str] = None,
        skip: int = 0,
        user_id: Optional[str] = None,
        disable_tqdm: bool = False,
        category_search: Optional[str] = None,
        *,
        as_generator: Literal[False] = False,
    ) -> List[Dict]:
        ...

    @typechecked
    def predictions(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[List[str]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        author_in: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
        fields: Optional[List[str]] = None,
        first: Optional[int] = None,
        honeypot_mark_gte: Optional[float] = None,
        honeypot_mark_lte: Optional[float] = None,
        id_contains: Optional[List[str]] = None,
        label_id: Optional[str] = None,
        skip: int = 0,
        user_id: Optional[str] = None,
        disable_tqdm: bool = False,
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
        if fields is None:
            fields = [
                "author.email",
                "author.id",
                "id",
                "jsonResponse",
                "labelType",
                "modelName",
            ]
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
            as_generator=as_generator,  # type: ignore
        )

    @overload
    def inferences(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[List[str]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        author_in: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
        fields: Optional[List[str]] = None,
        first: Optional[int] = None,
        honeypot_mark_gte: Optional[float] = None,
        honeypot_mark_lte: Optional[float] = None,
        id_contains: Optional[List[str]] = None,
        label_id: Optional[str] = None,
        skip: int = 0,
        user_id: Optional[str] = None,
        disable_tqdm: bool = False,
        category_search: Optional[str] = None,
        *,
        as_generator: Literal[True],
    ) -> Generator[Dict, None, None]:
        ...

    @overload
    def inferences(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[List[str]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        author_in: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
        fields: Optional[List[str]] = None,
        first: Optional[int] = None,
        honeypot_mark_gte: Optional[float] = None,
        honeypot_mark_lte: Optional[float] = None,
        id_contains: Optional[List[str]] = None,
        label_id: Optional[str] = None,
        skip: int = 0,
        user_id: Optional[str] = None,
        disable_tqdm: bool = False,
        category_search: Optional[str] = None,
        *,
        as_generator: Literal[False] = False,
    ) -> List[Dict]:
        ...

    @typechecked
    def inferences(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[List[str]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        author_in: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
        fields: Optional[List[str]] = None,
        first: Optional[int] = None,
        honeypot_mark_gte: Optional[float] = None,
        honeypot_mark_lte: Optional[float] = None,
        id_contains: Optional[List[str]] = None,
        label_id: Optional[str] = None,
        skip: int = 0,
        user_id: Optional[str] = None,
        disable_tqdm: bool = False,
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
        if fields is None:
            fields = [
                "author.email",
                "author.id",
                "id",
                "jsonResponse",
                "labelType",
                "modelName",
            ]
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
            as_generator=as_generator,  # type: ignore
        )

    @typechecked
    def export_labels_as_df(
        self,
        project_id: str,
        fields: List[str] = [
            "author.email",
            "author.id",
            "createdAt",
            "id",
            "labelType",
        ],
        asset_fields: List[str] = ["externalId"],
    ) -> pd.DataFrame:
        # pylint: disable=line-too-long
        """Get the labels of a project as a pandas DataFrame.

        Args:
            project_id: Identifier of the project
            fields: All the fields to request among the possible fields for the labels.
                See [the documentation](https://docs.kili-technology.com/reference/graphql-api#label) for all possible fields.
            asset_fields: All the fields to request among the possible fields for the assets.
                See [the documentation](https://docs.kili-technology.com/reference/graphql-api#asset) for all possible fields.

        Returns:
            A pandas DataFrame containing the labels.
        """
        get_project(self, project_id, ["id"])
        assets_gen = AssetQuery(self.graphql_client, self.http_client)(
            AssetWhere(project_id=project_id),
            asset_fields + ["labels." + field for field in fields],
            QueryOptions(disable_tqdm=False),
        )
        labels = [
            dict(
                label,
                **{f"asset_{key}": asset[key] for key in asset if key != "labels"},
            )
            for asset in assets_gen
            for label in asset["labels"]
        ]
        labels_df = pd.DataFrame(labels)
        return labels_df

    @typechecked
    def count_labels(
        self,
        project_id: str,
        asset_id: Optional[str] = None,
        asset_status_in: Optional[List[str]] = None,
        asset_external_id_in: Optional[List[str]] = None,
        author_in: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        created_at_lte: Optional[str] = None,
        honeypot_mark_gte: Optional[float] = None,
        honeypot_mark_lte: Optional[float] = None,
        label_id: Optional[str] = None,
        type_in: Optional[List[str]] = None,
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

        where = LabelWhere(
            project_id=project_id,
            asset_id=asset_id,
            asset_status_in=asset_status_in,
            asset_external_id_in=asset_external_id_in,
            author_in=author_in,
            created_at=created_at,
            created_at_gte=created_at_gte,
            created_at_lte=created_at_lte,
            honeypot_mark_gte=honeypot_mark_gte,
            honeypot_mark_lte=honeypot_mark_lte,
            id_contains=id_contains,
            label_id=label_id,
            type_in=type_in,
            user_id=user_id,
            category_search=category_search,
        )
        return LabelQuery(self.graphql_client, self.http_client).count(where)

    def export_labels(
        self,
        project_id: str,
        filename: str,
        fmt: LabelFormat,
        asset_ids: Optional[List[str]] = None,
        layout: SplitOption = "split",
        single_file: bool = False,
        disable_tqdm: bool = False,
        with_assets: bool = True,
        external_ids: Optional[List[str]] = None,
        annotation_modifier: Optional[CocoAnnotationModifier] = None,
        asset_filter_kwargs: Optional[Dict[str, object]] = None,
        normalized_coordinates: Optional[bool] = None,
    ) -> None:
        # pylint: disable=line-too-long
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
                This can be used if you want to add a new attribute to the COCO annotation. For
                example, you can add a method that computes if the annotation is a rectangle or not
                and add it to the COCO annotation (see example).
            asset_filter_kwargs: Optional dictionary of arguments to pass to `kili.assets()` in order to filter the assets the labels are exported from. The supported arguments are:

                - `consensus_mark_gte`
                - `consensus_mark_lte`
                - `external_id_strictly_in`
                - `external_id_in`
                - `honeypot_mark_gte`
                - `honeypot_mark_lte`
                - `label_author_in`
                - `label_reviewer_in`
                - `skipped`
                - `status_in`
                - `label_category_search`
                - `created_at_gte`
                - `created_at_lte`
                - `issue_type`
                - `issue_status`
                - `inference_mark_gte`
                - `inference_mark_lte`
                - `metadata_where`

                See the documentation of [`kili.assets()`](https://python-sdk-docs.kili-technology.com/latest/sdk/asset/#kili.queries.asset.__init__.QueriesAsset.assets) for more information.
            normalized_coordinates: This parameter is only effective on the Kili (a.k.a raw) format.
                If True, the coordinates of the `(x, y)` vertices are normalized between 0 and 1.
                If False, the json response will contain additional fields with coordinates in absolute values, that is, in pixels.

        !!! Info
            The supported formats are:

            - Yolo V4, V5, V7, V8 for object detection tasks.
            - Kili (a.k.a raw) for all tasks.
            - COCO for object detection tasks (bounding box and semantic segmentation).
            - Pascal VOC for object detection tasks (bounding box).

        !!! warning "Cloud storage"
            Export with asset download (`with_assets=True`) is not allowed for projects connected to a cloud storage.

        !!! Example
            ```python
            kili.export_labels("your_project_id", "export.zip", "yolo_v4")
            ```

        !!! Example
            ```python
            def is_rectangle(coco_annotation, coco_image, kili_annotation):
                is_rectangle = ...
                return {**coco_annotation, "attributes": {"is_rectangle": is_rectangle}}

            kili.export_labels(
                "your_project_id",
                "export.zip",
                "coco",
                annotation_modifier=add_is_rectangle
            )
            ```
        """
        if external_ids is not None and asset_ids is None:
            id_map = infer_ids_from_external_ids(
                kili=self, asset_external_ids=external_ids, project_id=project_id
            )
            asset_ids = [id_map[id] for id in external_ids]

        try:
            export_labels(
                self,
                asset_ids=asset_ids,
                project_id=cast(ProjectId, project_id),
                export_type="latest",
                label_format=fmt,
                split_option=layout,
                single_file=single_file,
                output_file=filename,
                disable_tqdm=disable_tqdm,
                log_level="WARNING",
                with_assets=with_assets,
                annotation_modifier=annotation_modifier,
                asset_filter_kwargs=asset_filter_kwargs,
                normalized_coordinates=normalized_coordinates,
            )
        except NoCompatibleJobError as excp:
            print(str(excp))
