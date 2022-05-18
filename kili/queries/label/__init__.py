"""Label queries."""

from typing import Generator, List, Optional, Union
import warnings

from typeguard import typechecked
import pandas as pd


from ...helpers import Compatible, format_result, fragment_builder
from ..asset import QueriesAsset
from ..project import QueriesProject
from .queries import gql_labels, GQL_LABELS_COUNT
from ...constants import NO_ACCESS_RIGHT
from ...types import Label as LabelType
from ...orm import Label
from ...utils import row_generator_from_paginated_calls


class QueriesLabel:
    """Set of Label queries."""

    # pylint: disable=too-many-arguments,too-many-locals

    def __init__(self, auth):
        """Initialize the subclass.

        Args:
            auth: KiliAuth object
        """
        self.auth = auth

    # pylint: disable=dangerous-default-value
    @Compatible(['v1', 'v2'])
    @typechecked
    def labels(self,
               asset_id: Optional[str] = None,
               asset_status_in: Optional[List[str]] = None,
               asset_external_id_in: Optional[List[str]] = None,
               author_in: Optional[List[str]] = None,
               created_at: Optional[str] = None,
               created_at_gte: Optional[str] = None,
               created_at_lte: Optional[str] = None,
               fields: List[str] = ['author.email', 'author.id', 'id',
                                    'jsonResponse', 'labelType', 'secondsToLabel', 'skipped'],
               first: Optional[int] = None,
               honeypot_mark_gte: Optional[float] = None,
               honeypot_mark_lte: Optional[float] = None,
               id_contains: Optional[List[str]] = None,
               json_response_contains: Optional[List[str]] = None,
               label_id: Optional[str] = None,
               project_id: Optional[str] = None,
               skip: int = 0,
               skipped: Optional[bool] = None,
               type_in: Optional[List[str]] = None,
               user_id: Optional[str] = None,
               disable_tqdm: bool = False,
               as_generator: bool = False,
               ) -> Union[List[dict], Generator[dict, None, None]]:
        # pylint: disable=line-too-long
        """Get a label list or a label generator from a project based on a set of criteria.

        Args:
            asset_id: Identifier of the asset.
            asset_status_in: Returned labels should have a status that belongs to that list, if given.
                Possible choices : `TODO`, `ONGOING`, `LABELED` or `REVIEWED`
            asset_external_id_in: Returned labels should have an external id that belongs to that list, if given.
            author_in: Returned labels should have a label whose status belongs to that list, if given.
            created_at: Returned labels should have a label whose creation date is equal to this date.
            created_at_gte: Returned labels should have a label whose creation date is greater than this date.
            created_at_lte: Returned labels should have a label whose creation date is lower than this date.
            fields: All the fields to request among the possible fields for the labels.
                See [the documentation](https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#label) for all possible fields.
            first: Maximum number of labels to return.
            honeypot_mark_gte: Returned labels should have a label whose honeypot is greater than this number.
            honeypot_mark_lte: Returned labels should have a label whose honeypot is lower than this number.
            id_contains: Filters out labels not belonging to that list. If empty, no filtering is applied.
            json_response_contains: Returned labels should have a substring of the jsonResponse that belongs
                to that list, if given.
            label_id: Identifier of the label.
            project_id: Identifier of the project.
            skip: Number of labels to skip (they are ordered by their date of creation, first to last).
            skipped: Returned labels should have a label which is skipped
            type_in: Returned labels should have a label whose type belongs to that list, if given.
            user_id: Identifier of the user.
            disable_tqdm: If `True`, the progress bar will be disabled
            as_generator: If `True`, a generator on the labels is returned.

        !!! info "Dates format"
            Date strings should have format: "YYYY-MM-DD"

        Returns:
            A result object which contains the query if it was successful, else an error message.

        Examples:
            >>> kili.labels(project_id=project_id, fields=['jsonResponse', 'labelOf.externalId']) # returns a list of all labels of a project and their assets external ID
            >>> kili.labels(project_id=project_id, fields=['jsonResponse'], as_generator=True) # returns a generator of all labels of a project
        """

        saved_args = locals()
        count_args = {
            k: v
            for (k, v) in saved_args.items()
            if k
            not in [
                'as_generator',
                'disable_tqdm',
                'fields',
                'first',
                'id_contains',
                'self',
                'skip',
            ]
        }

        # using tqdm with a generator is messy, so it is always disabled
        disable_tqdm = disable_tqdm or as_generator

        payload_query = {
            'where': {
                'id': label_id,
                'asset': {
                    'id': asset_id,
                    'externalIdIn': asset_external_id_in,
                    'statusIn': asset_status_in,
                },
                'project': {
                    'id': project_id,
                },
                'user': {
                    'id': user_id,
                },
                'createdAt': created_at,
                'createdAtGte': created_at_gte,
                'createdAtLte': created_at_lte,
                'authorIn': author_in,
                'honeypotMarkGte': honeypot_mark_gte,
                'honeypotMarkLte': honeypot_mark_lte,
                'idIn': id_contains,
                'jsonResponseContains': json_response_contains,
                'skipped': skipped,
                'typeIn': type_in,
            },
        }

        labels_generator = row_generator_from_paginated_calls(
            skip,
            first,
            self.count_labels,
            count_args,
            self._query_labels,
            payload_query,
            fields,
            disable_tqdm
        )

        if as_generator:
            return labels_generator
        return list(labels_generator)

    def _query_labels(self,
                      skip: int,
                      first: int,
                      payload: dict,
                      fields: List[str]):

        payload.update({'skip': skip, 'first': first})
        _gql_labels = gql_labels(fragment_builder(fields, LabelType))
        result = self.auth.client.execute(_gql_labels, payload)
        return format_result('data', result, Label)

    # pylint: disable=dangerous-default-value
    @typechecked
    def export_labels_as_df(self,
                            project_id: str,
                            fields: List[str] = [
                                'author.email',
                                'author.id',
                                'createdAt',
                                'id',
                                'labelType',
                                'skipped'
                            ],
                            asset_fields: List[str] = [
                                'externalId'
                            ]) -> pd.DataFrame:
        # pylint: disable=line-too-long
        """Get the labels of a project as a pandas DataFrame.

        Args:
            project_id: Identifier of the project
            fields: All the fields to request among the possible fields for the labels.
                See [the documentation](https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#label) for all possible fields.
            asset_fields: All the fields to request among the possible fields for the assets.
                See [the documentation](https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#asset) for all possible fields.

        Returns:
            pandas DataFrame containing the labels.
        """
        projects = QueriesProject(self.auth).projects(project_id)
        assert len(projects) == 1, NO_ACCESS_RIGHT
        assets = QueriesAsset(self.auth).assets(
            project_id=project_id,
            fields=asset_fields + ['labels.' + field for field in fields])
        labels = [dict(label, **dict((f'asset_{key}', asset[key]) for key in asset if key != 'labels'))
                  for asset in assets for label in asset['labels']]
        labels_df = pd.DataFrame(labels)
        return labels_df

    @Compatible(['v1', 'v2'])
    @typechecked
    def count_labels(self,
                     asset_id: Optional[str] = None,
                     asset_status_in: Optional[List[str]] = None,
                     asset_external_id_in: Optional[List[str]] = None,
                     author_in: Optional[List[str]] = None,
                     created_at: Optional[str] = None,
                     created_at_gte: Optional[str] = None,
                     created_at_lte: Optional[str] = None,
                     honeypot_mark_gte: Optional[float] = None,
                     honeypot_mark_lte: Optional[float] = None,
                     json_response_contains: Optional[List[str]] = None,
                     label_id: Optional[str] = None,
                     project_id: Optional[str] = None,
                     skipped: Optional[bool] = None,
                     type_in: Optional[List[str]] = None,
                     user_id: Optional[str] = None) -> int:
        # pylint: disable=line-too-long
        """Get the number of labels for the given parameters.

        Args:
            asset_id: Identifier of the asset.
            asset_status_in: Returned labels should have a status that belongs to that list, if given.
                Possible choices : `TODO`, `ONGOING`, `LABELED` or `REVIEWED`
            asset_external_id_in: Returned labels should have an external id that belongs to that list, if given.
            author_in: Returned labels should have a label whose status belongs to that list, if given.
            created_at: Returned labels should have a label whose creation date is equal to this date.
            created_at_gte: Returned labels should have a label whose creation date is greater than this date.
            created_at_lte: Returned labels should have a label whose creation date is lower than this date.
            honeypot_mark_gte: Returned labels should have a label whose honeypot is greater than this number.
            honeypot_mark_lte: Returned labels should have a label whose honeypot is lower than this number.
            json_response_contains: Returned labels should have a substring of the jsonResponse that
                belongs to that list, if given.
            label_id: Identifier of the label.
            project_id: Identifier of the project.
            skipped: Returned labels should have a label which is skipped
            type_in: Returned labels should have a label whose type belongs to that list, if given.
            user_id: Identifier of the user.

        !!! info "Dates format"
            Date strings should have format: "YYYY-MM-DD"

        Returns:
            The number of labels with the parameters provided
        """
        variables = {
            'where': {
                'id': label_id,
                'asset': {
                    'id': asset_id,
                    'externalIdIn': asset_external_id_in,
                    'statusIn': asset_status_in,
                },
                'project': {
                    'id': project_id,
                },
                'user': {
                    'id': user_id,
                },
                'createdAt': created_at,
                'createdAtGte': created_at_gte,
                'createdAtLte': created_at_lte,
                'authorIn': author_in,
                'honeypotMarkGte': honeypot_mark_gte,
                'honeypotMarkLte': honeypot_mark_lte,
                'jsonResponseContains': json_response_contains,
                'skipped': skipped,
                'typeIn': type_in,
            }
        }
        result = self.auth.client.execute(GQL_LABELS_COUNT, variables)
        count = format_result('data', result)
        return count
