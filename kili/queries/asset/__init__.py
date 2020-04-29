import time
from json import dumps
from typing import List

import pandas as pd
from tqdm import tqdm

from ...helpers import deprecate, format_result
from .queries import (GQL_ASSETS,
                      GQL_ASSETS_COUNT,
                      GQL_GET_NEXT_ASSET_FROM_LABEL,
                      GQL_GET_NEXT_ASSET_FROM_PROJECT)
from .fragments import ASSET_FRAGMENT_SIMPLIFIED


class QueriesAsset:

    def __init__(self, auth):
        """
        Initializes the subclass

        Parameters
        ----------
        - auth : KiliAuth object
        """
        self.auth = auth

    @deprecate(
        """
        This function is deprecated. get_asset used to fetch an asset from its ID. It is now achievable with assets.
        To fetch an asset from its ID, use:
            > playground.assets(asset_id=asset_id)
        """)
    def get_asset(self, asset_id: str):
        """
        Get an asset by its id

        Parameters
        ----------
        - asset_id : str

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.
        """
        variables = {'assetID': asset_id}
        result = self.auth.client.execute(GQL_GET_ASSET, variables)
        return format_result('data', result)

    @deprecate(
        """
        This function is deprecated. get_assets used to fetch assets. It is now achievable with assets.
        To fetch assets, use:
            > playground.assets(project_id=project_id)
        """)
    def get_assets(self, asset_id: str):
        return None

    def assets(self, asset_id: str = None, project_id: str = None,
               skip: int = 0, first: int = None,
               external_id_contains: List[str] = None,
               status_in: List[str] = None,
               author_in: List[str] = None,
               consensus_mark_gt: float = None,
               consensus_mark_lt: float = None,
               honeypot_mark_gt: float = None,
               honeypot_mark_lt: float = None,
               label_type_in: List[str] = None,
               label_author_in: List[str] = None,
               label_consensus_mark_gt: float = None,
               label_consensus_mark_lt: float = None,
               label_honeypot_mark_gt: float = None,
               label_honeypot_mark_lt: float = None,
               label_created_at_gt: float = None,
               label_created_at_lt: float = None,
               label_skipped: bool = None,
               format: str = None, disable_tqdm: bool = False,
               fragment=ASSET_FRAGMENT_SIMPLIFIED):
        """
        Get an array of assets from a project

        Parameters
        ----------
        - project_id : str
            Identifier of the project.
        - skip : int, optional (default = None)
            Number of assets to skip (they are ordered by their date of creation, first to last).
        - first : int, optional (default = None)
            Maximum number of assets to return.
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
            Maximum amout of honeypot for the asset.
        - label_type_in : list of str, optional (default = None)
            Returned assets should have a label whose type belongs to that list, if given.
        - label_author_in : list of str, optional (default = None)
            Returned assets should have a label whose status belongs to that list, if given.
        - label_consensus_mark_gt, optional (default = None)
            Returned assets should have a label whose consensus is greater than this number.
        - label_consensus_mark_lt : float, optional (default = None)
            Returned assets should have a label whose consensus is lower than this number.
        - label_honeypot_mark_gt : float, optional (default = None)
            Returned assets should have a label whose honeypot is greater than this number.
        - label_honeypot_mark_lt : float, optional (default = None)
            Returned assets should have a label whose honeypot is lower than this number.
        - label_created_at_gt : float, optional (default = None)
            Returned assets should have a label whose creation date is greater than this date.
        - label_created_at_lt : float, optional (default = None)
            Returned assets should have a label whose creation date is lower than this date.
        - label_skipped : bool, optional (default = None)
            Returned assets should have a label which is skipped
        - format : str, optional (default = None)
            If equal to 'pandas', returns a pandas DataFrame
        - disable_tqdm : bool, optional (default = False)
        - fragment : str, optional (default = ASSET_FRAGMENT_SIMPLIFIED)


        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.
        """
        return get_assets(self.auth.client, asset_id, project_id,
                          skip, first,
                          external_id_contains,
                          status_in,
                          author_in,
                          consensus_mark_gt,
                          consensus_mark_lt,
                          honeypot_mark_gt,
                          honeypot_mark_lt,
                          label_type_in,
                          label_author_in,
                          label_consensus_mark_gt,
                          label_consensus_mark_lt,
                          label_honeypot_mark_gt,
                          label_honeypot_mark_lt,
                          label_created_at_gt,
                          label_created_at_lt,
                          label_skipped,
                          format, disable_tqdm,
                          fragment)

    @deprecate(
        """
        This function is deprecated. get_assets_by_external_id used to fetch assets from an external_id. It is now achievable with assets.
        To fetch assets from and external_id, use:
            > playground.assets(project_id=project_id, external_id_contains=[external_id])
        """)
    def get_assets_by_external_id(self, project_id: str, external_id: str):
        """
        Get an asset by its external id

        The project id is needed as the external id is not guaranteed to uniquely identify the asset.

        Parameters
        ----------
        - project_id : str
        - external_id : str

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.
        """
        return None

    @deprecate(
        """
        This function is deprecated. It will be removed on June 1st.
        """)
    def get_next_asset_from_label(self, label_asset_ids: List[str]):
        """
        Get next asset to label from previously labeled asset identifiers

        Parameters
        ----------
        - label_asset_ids : list of str
            The identifiers of the assets that have been labeled

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.
        """
        variables = {'labelAssetIDs': label_asset_ids}
        result = self.auth.client.execute(
            GQL_GET_NEXT_ASSET_FROM_LABEL, variables)
        return format_result('data', result)

    @deprecate(
        """
        This function is deprecated. It will be removed on June 1st.
        """)
    def get_next_asset_from_project(self, project_id: str):
        """
        Get next asset to label from project id

        Returns the next asset to label to the current user for the current project.

        Parameters
        ----------
        - project_id : str

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.
        """
        variables = {'projectID': project_id}
        result = self.auth.client.execute(
            GQL_GET_NEXT_ASSET_FROM_PROJECT, variables)
        return format_result('data', result)

    @deprecate(
        """
        This function is deprecated. export_assets used to fetch assets from a project. It is now achievable with assets.
        To fetch assets from a project, use:
            > playground.export_assets(project_id=project_id)
        """)
    def export_assets(self, project_id: str):
        """
        Export assets from project

        Parameters
        ----------
        - project_id : str

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.
        """
        return None

    def count_assets(self, asset_id: str = None,
                     project_id: str = None,
                     external_id_contains: List[str] = None,
                     status_in: List[str] = None,
                     author_in: List[str] = None,
                     consensus_mark_gt: float = None,
                     consensus_mark_lt: float = None,
                     honeypot_mark_gt: float = None,
                     honeypot_mark_lt: float = None,
                     label_type_in: List[str] = None,
                     label_author_in: List[str] = None,
                     label_consensus_mark_gt: float = None,
                     label_consensus_mark_lt: float = None,
                     label_honeypot_mark_gt: float = None,
                     label_honeypot_mark_lt: float = None,
                     label_created_at_gt: float = None,
                     label_created_at_lt: float = None,
                     label_skipped: bool = None):
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
        - author_in : list of str, optional (default = None)
            Returned assets should have an author that belongs to that list, if given.
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
        - label_honeypot_mark_gt : float, optional (default = None)
            Returned assets should have a label whose honeypot is greater than this number.
        - label_honeypot_mark_lt : float, optional (default = None)
            Returned assets should have a label whose honeypot is lower than this number.
        - label_created_at_gt : float, optional (default = None)
            Returned assets should have a label whose creation date is greater than this date.
        - label_created_at_lt : float, optional (default = None)
            Returned assets should have a label whose creation date is lower than this date.
        - label_skipped : bool, optional (default = None)
            Returned assets should have a label which is skipped

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.
        """
        return get_count_assets(self.auth.client, asset_id,
                                project_id,
                                external_id_contains,
                                status_in,
                                author_in,
                                consensus_mark_gt,
                                consensus_mark_lt,
                                honeypot_mark_gt,
                                honeypot_mark_lt,
                                label_type_in,
                                label_author_in,
                                label_consensus_mark_gt,
                                label_consensus_mark_lt,
                                label_honeypot_mark_gt,
                                label_honeypot_mark_lt,
                                label_created_at_gt,
                                label_created_at_lt,
                                label_skipped)


def get_assets(client, asset_id: str, project_id: str,
               skip: int, first: int,
               external_id_contains: List[str],
               status_in: List[str],
               author_in: List[str],
               consensus_mark_gt: float,
               consensus_mark_lt: float,
               honeypot_mark_gt: float,
               honeypot_mark_lt: float,
               label_type_in: List[str],
               label_author_in: List[str],
               label_consensus_mark_gt: float,
               label_consensus_mark_lt: float,
               label_honeypot_mark_gt: float,
               label_honeypot_mark_lt: float,
               label_created_at_gt: float,
               label_created_at_lt: float,
               label_skipped: bool,
               format: str, disable_tqdm: bool,
               fragment: str):
    saved_args = locals()
    count_args = {k: v for (k, v) in saved_args.items()
                  if k not in ['skip', 'first', 'disable_tqdm', 'format', 'fragment']}
    number_of_assets_with_search = get_count_assets(**count_args)
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
                    'authorIn': author_in,
                    'consensusMarkGte': consensus_mark_gt,
                    'consensusMarkLte': consensus_mark_lt,
                    'honeypotMarkGte': honeypot_mark_gt,
                    'honeypotMarkLte': honeypot_mark_lt,
                    'label': {
                        'typeIn': label_type_in,
                        'authorIn': label_author_in,
                        'consensusMarkGte': label_consensus_mark_gt,
                        'consensusMarkLte': label_consensus_mark_lt,
                        'honeypotMarkGte': label_honeypot_mark_gt,
                        'honeypotMarkLte': label_honeypot_mark_lt,
                        'createdAtGte': label_created_at_gt,
                        'createdAtLte': label_created_at_lt,
                        'skipped': label_skipped,
                    }
                },
                'skip': skip,
                'first': formatted_first,
            }
            result = client.execute(GQL_ASSETS(fragment), variables)
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


def get_count_assets(client, asset_id: str,
                     project_id: str,
                     external_id_contains: List[str],
                     status_in: List[str],
                     author_in: List[str],
                     consensus_mark_gt: float,
                     consensus_mark_lt: float,
                     honeypot_mark_gt: float,
                     honeypot_mark_lt: float,
                     label_type_in: List[str],
                     label_author_in: List[str],
                     label_consensus_mark_gt: float,
                     label_consensus_mark_lt: float,
                     label_honeypot_mark_gt: float,
                     label_honeypot_mark_lt: float,
                     label_created_at_gt: float,
                     label_created_at_lt: float,
                     label_skipped: bool):
    variables = {
        'where': {
            'id': asset_id,
            'project': {
                'id': project_id,
            },
            'externalIdIn': external_id_contains,
            'statusIn': status_in,
            'authorIn': author_in,
            'consensusMarkGte': consensus_mark_gt,
            'consensusMarkLte': consensus_mark_lt,
            'honeypotMarkGte': honeypot_mark_gt,
            'honeypotMarkLte': honeypot_mark_lt,
            'label': {
                'typeIn': label_type_in,
                'authorIn': label_author_in,
                'consensusMarkGte': label_consensus_mark_gt,
                'consensusMarkLte': label_consensus_mark_lt,
                'honeypotMarkGte': label_honeypot_mark_gt,
                'honeypotMarkLte': label_honeypot_mark_lt,
                'createdAtGte': label_created_at_gt,
                'createdAtLte': label_created_at_lt,
                'skipped': label_skipped,
            }
        }
    }
    result = client.execute(GQL_ASSETS_COUNT, variables)
    count = format_result('data', result)
    return count
