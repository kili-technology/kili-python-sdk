import time
from json import dumps
from typing import List

import pandas as pd
from tqdm import tqdm

from ...helpers import Compatible, deprecate, format_result, fragment_builder
from .queries import gql_assets, GQL_ASSETS_COUNT
from ...constants import NO_ACCESS_RIGHT
from ...types import Asset


class QueriesAsset:

    def __init__(self, auth):
        """
        Initializes the subclass

        Parameters
        ----------
        - auth : KiliAuth object
        """
        self.auth = auth

    @Compatible(['v1', 'v2'])
    def assets(self, asset_id: str = None, project_id: str = None,
               skip: int = 0,
               fields: list = ['content', 'createdAt', 'externalId', 'id', 'isHoneypot', 'jsonMetadata', 'labels.author.id',
                               'labels.author.email', 'labels.createdAt', 'labels.id', 'labels.jsonResponse', 'status'],
               first: int = None,
               consensus_mark_gt: float = None,
               consensus_mark_lt: float = None,
               external_id_contains: List[str] = None,
               honeypot_mark_gt: float = None,
               honeypot_mark_lt: float = None,
               status_in: List[str] = None,
               label_type_in: List[str] = None,
               label_author_in: List[str] = None,
               label_consensus_mark_gt: float = None,
               label_consensus_mark_lt: float = None,
               label_created_at: str = None,
               label_created_at_gt: str = None,
               label_created_at_lt: str = None,
               label_honeypot_mark_gt: float = None,
               label_honeypot_mark_lt: float = None,
               label_json_response_contains: List[str] = None,
               label_skipped: bool = None,
               updated_at_gte: str = None,
               updated_at_lte: str = None,
               format: str = None, disable_tqdm: bool = False):
        """
        Get an array of assets from a project

        Parameters
        ----------
        - project_id : str
            Identifier of the project.
        - skip : int, optional (default = None)
            Number of assets to skip (they are ordered by their date of creation, first to last).
        - fields : list of string, optional (default = ['id', 'content', 'externalId', 'isHoneypot', 'isUsedForConsensus', 'jsonMetadata', 'labels.author.id', 'labels.author.email','labels.jsonResponse', 'labels.skipped', 'priority', 'projects.id', 'projects.title', 'project.jsonInterface'])
            All the fields to request among the possible fields for the assets, default for None are the non-calculated fields)
            Possible fields : see https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#asset
        - first : int, optional (default = None)
            Maximum number of assets to return. Can only be between 0 and 100.
        - consensus_mark_gt : float, optional (default = None)
            Minimum amout of consensus for the asset.
        - consensus_mark_lt : float, optional (default = None)
            Maximum amout of consensus for the asset.
        - external_id_contains : list of str, optional (default = None)
            Returned assets should have an external id that belongs to that list, if given.
        - honeypot_mark_gt : float, optional (default = None)
            Minimum amout of honeypot for the asset.
        - honeypot_mark_lt : float, optional (default = None)
            Maximum amout of honeypot for the asset.
        - status_in : list of str, optional (default = None)
            Returned assets should have a status that belongs to that list, if given.
            Possible choices : {'TODO', 'ONGOING', 'LABELED', 'REVIEWED'}
        - label_type_in : list of str, optional (default = None)
            Returned assets should have a label whose type belongs to that list, if given.
        - label_author_in : list of str, optional (default = None)
            Returned assets should have a label whose status belongs to that list, if given.
        - label_consensus_mark_gt, optional (default = None)
            Returned assets should have a label whose consensus is greater than this number.
        - label_consensus_mark_lt : float, optional (default = None)
            Returned assets should have a label whose consensus is lower than this number.
        - label_created_at : string, optional (default = None)
            Returned assets should have a label whose creation date is equal to this date.
            Formatted string should have format : "YYYY-MM-DD"
        - label_created_at_gt : string, optional (default = None)
            Returned assets should have a label whose creation date is greater than this date.
            Formatted string should have format : "YYYY-MM-DD"
        - label_created_at_lt : string, optional (default = None)
            Returned assets should have a label whose creation date is lower than this date.
            Formatted string should have format : "YYYY-MM-DD"
        - label_json_response_contains : list of str, optional (default = None)
            Returned assets should have a substring of the label's jsonResponse that belongs to that list, if given.
        - label_honeypot_mark_gt : float, optional (default = None)
            Returned assets should have a label whose honeypot is greater than this number.
        - label_honeypot_mark_lt : float, optional (default = None)
            Returned assets should have a label whose honeypot is lower than this number.
        - label_skipped : bool, optional (default = None)
            Returned assets should have a label which is skipped
        - updated_at_gte : string, optional (default = None)
            Returned assets should have a label whose update date is greated or equal to this date.
            Formatted string should have format : "YYYY-MM-DD"
        - updated_at_lte : string, optional (default = None)
            Returned assets should have a label whose update date is lower or equal to this date.
            Formatted string should have format : "YYYY-MM-DD"
        - format : str, optional (default = None)
            If equal to 'pandas', returns a pandas DataFrame
        - disable_tqdm : bool, optional (default = False)

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.
        """
        saved_args = locals()
        count_args = {k: v for (k, v) in saved_args.items()
                      if k not in ['skip', 'first', 'disable_tqdm', 'format', 'fields', 'self']}
        number_of_assets_with_search = self.count_assets(**count_args)
        total = min(number_of_assets_with_search,
                    first) if first is not None else number_of_assets_with_search
        formatted_first = first if first else 100
        if total == 0:
            return []
        with tqdm(total=total, disable=disable_tqdm) as pbar:
            paged_assets = []
            while True:
                variables = {
                    'where': {
                        'id': asset_id,
                        'project': {
                            'id': project_id,
                        },
                        'externalIdIn': external_id_contains,
                        'statusIn': status_in,
                        'consensusMarkGte': consensus_mark_gt,
                        'consensusMarkLte': consensus_mark_lt,
                        'honeypotMarkGte': honeypot_mark_gt,
                        'honeypotMarkLte': honeypot_mark_lt,
                        'label': {
                            'typeIn': label_type_in,
                            'authorIn': label_author_in,
                            'consensusMarkGte': label_consensus_mark_gt,
                            'consensusMarkLte': label_consensus_mark_lt,
                            'createdAt': label_created_at,
                            'createdAtGte': label_created_at_gt,
                            'createdAtLte': label_created_at_lt,
                            'honeypotMarkGte': label_honeypot_mark_gt,
                            'honeypotMarkLte': label_honeypot_mark_lt,
                            'jsonResponseContains': label_json_response_contains,
                            'skipped': label_skipped,
                        },
                        'updatedAtGte': updated_at_gte,
                        'updatedAtLte': updated_at_lte,
                    },
                    'skip': skip,
                    'first': formatted_first,
                }
                GQL_ASSETS = gql_assets(fragment_builder(fields, Asset))
                result = self.auth.client.execute(GQL_ASSETS, variables)
                assets = format_result('data', result)
                if assets is None or len(assets) == 0 or (first is not None and len(paged_assets) == first):
                    if format == 'pandas':
                        return pd.DataFrame(paged_assets)
                    return paged_assets
                if first is not None:
                    assets = assets[:max(0, first - len(paged_assets))]
                paged_assets += assets
                skip += formatted_first
                pbar.update(len(assets))

    @Compatible(['v1', 'v2'])
    def count_assets(self, asset_id: str = None,
                     project_id: str = None,
                     external_id_contains: List[str] = None,
                     status_in: List[str] = None,
                     consensus_mark_gt: float = None,
                     consensus_mark_lt: float = None,
                     honeypot_mark_gt: float = None,
                     honeypot_mark_lt: float = None,
                     label_type_in: List[str] = None,
                     label_author_in: List[str] = None,
                     label_consensus_mark_gt: float = None,
                     label_consensus_mark_lt: float = None,
                     label_created_at: str = None,
                     label_created_at_gt: str = None,
                     label_created_at_lt: str = None,
                     label_honeypot_mark_gt: float = None,
                     label_honeypot_mark_lt: float = None,
                     label_json_response_contains: List[str] = None,
                     label_skipped: bool = None,
                     updated_at_gte: str = None,
                     updated_at_lte: str = None):
        """
        Count and return the number of assets with the given parameters

        Parameters beginning with 'label_' apply to labels, others apply to assets.

        Parameters
        ----------
        - asset_id : str
            Identifier of the asset
        - project_id : str
            Identifier of the project
        - external_id_contains : list of str, optional (default = None)
            Returned assets should have an external id that belongs to that list, if given.
        - status_in : list of str, optional (default = None)
            Returned assets should have a status that belongs to that list, if given.
            Possible choices : {'TODO', 'ONGOING', 'LABELED', 'REVIEWED'}
        - consensus_mark_gt : float, optional (default = None)
            Minimum amout of consensus for the asset.
        - consensus_mark_lt : float, optional (default = None)
            Maximum amout of consensus for the asset.
        - honeypot_mark_gt : float, optional (default = None)
            Minimum amout of honeypot for the asset.
        - honeypot_mark_lt : float, optional (default = None)
            Maximum amout of consensus for the asset.
        - label_type_in : list of str, optional (default = None)
            Returned assets should have a label whose type belongs to that list, if given.
        - label_author_in : list of str, optional (default = None)
            Returned assets should have a label whose status belongs to that list, if given.
        - label_consensus_mark_gt : float, optional (default = None)
            Returned assets should have a label whose consensus is greater than this number.
        - label_consensus_mark_lt : float, optional (default = None)
            Returned assets should have a label whose consensus is lower than this number.
        - label_created_at : string, optional (default = None)
            Returned assets should have a label whose creation date is equal to this date.
            Formatted string should have format : "YYYY-MM-DD"
        - label_created_at_gt : string, optional (default = None)
            Returned assets should have a label whose creation date is greater than this date.
            Formatted string should have format : "YYYY-MM-DD"
        - label_created_at_lt : string, optional (default = None)
            Returned assets should have a label whose creation date is lower than this date.
            Formatted string should have format : "YYYY-MM-DD"
        - label_honeypot_mark_gt : float, optional (default = None)
            Returned assets should have a label whose honeypot is greater than this number.
        - label_honeypot_mark_lt : float, optional (default = None)
            Returned assets should have a label whose honeypot is lower than this number.
        - label_json_response_contains : list of str, optional (default = None)
            Returned assets should have a substring of the label's jsonResponse that belongs to that list, if given.
        - label_skipped : bool, optional (default = None)
            Returned assets should have a label which is skipped
        - updated_at_gte : string, optional (default = None)
            Returned assets should have a label whose update date is greated or equal to this date.
            Formatted string should have format : "YYYY-MM-DD"
        - updated_at_lte : string, optional (default = None)
            Returned assets should have a label whose update date is lower or equal to this date.
            Formatted string should have format : "YYYY-MM-DD"

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.
        """
        variables = {
            'where': {
                'id': asset_id,
                'project': {
                    'id': project_id,
                },
                'externalIdIn': external_id_contains,
                'statusIn': status_in,
                'consensusMarkGte': consensus_mark_gt,
                'consensusMarkLte': consensus_mark_lt,
                'honeypotMarkGte': honeypot_mark_gt,
                'honeypotMarkLte': honeypot_mark_lt,
                'label': {
                    'typeIn': label_type_in,
                    'authorIn': label_author_in,
                    'consensusMarkGte': label_consensus_mark_gt,
                    'consensusMarkLte': label_consensus_mark_lt,
                    'createdAt': label_created_at,
                    'createdAtGte': label_created_at_gt,
                    'createdAtLte': label_created_at_lt,
                    'honeypotMarkGte': label_honeypot_mark_gt,
                    'honeypotMarkLte': label_honeypot_mark_lt,
                    'jsonResponseContains': label_json_response_contains,
                    'skipped': label_skipped,
                },
                'updatedAtGte': updated_at_gte,
                'updatedAtLte': updated_at_lte,
            }
        }
        result = self.auth.client.execute(GQL_ASSETS_COUNT, variables)
        count = format_result('data', result)
        return count
