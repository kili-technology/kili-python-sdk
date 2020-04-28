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


@deprecate(
    """
        This function is deprecated. get_asset used to fetch an asset from its ID. It is now achievable with assets.
        To fetch an asset from its ID, use:
            > playground.assets(asset_id=asset_id)
        """)
def get_asset(client, asset_id: str):
    return None


@deprecate(
    """
        This function is deprecated. get_assets used to fetch assets. It is now achievable with assets.
        To fetch assets, use:
            > playground.assets(project_id=project_id)
        """)
def get_assets(client, asset_id: str):
    return None


def assets(client, asset_id: str = None, project_id: str = None,
           skip: int = 0, first: int = None,
           external_id_contains: List[str] = None,
           status_in: List[str] = None,
           author_in: List[str] = None,
           consensus_mark_gt: float = None,
           consensus_mark_lt: float = None,
           honeypot_mark_gt: float = None,
           honeypot_mark_lt: float = None,
           skipped: bool = None,
           label_external_id_contains: str = None,
           label_type_in: List[str] = None,
           label_status_in: List[str] = None,
           label_author_in: List[str] = None,
           label_consensus_mark_gt: float = None,
           label_consensus_mark_lt: float = None,
           label_honeypot_mark_gt: float = None,
           label_honeypot_mark_lt: float = None,
           label_created_at_gt: float = None,
           label_created_at_lt: float = None,
           label_skipped: bool = None,
           format: str = None, disable_tqdm: bool = False, fragment=ASSET_FRAGMENT_SIMPLIFIED):
    saved_args = locals()
    count_args = {k: v for (k, v) in saved_args.items()
                  if k not in ['skip', 'first', 'disable_tqdm', 'format', 'fragment']}
    number_of_assets_with_search = count_assets(**count_args)
    total = min(number_of_assets_with_search,
                first) if first is not None else number_of_assets_with_search
    formatted_first = first if first else 100
    if total == 0:
        return []
    with tqdm(total=total, disable=disable_tqdm) as pbar:
        paged_assets = []
        while True:
            variables = {
                'assetID': asset_id,
                'projectID': project_id,
                'skip': skip,
                'first': formatted_first,
                'externalIdIn': external_id_contains,
                'statusIn': status_in,
                'authorIn': author_in,
                'consensusMarkGte': consensus_mark_gt,
                'consensusMarkLte': consensus_mark_lt,
                'honeypotMarkGte': honeypot_mark_gt,
                'honeypotMarkLte': honeypot_mark_lt,
                'skipped': skipped,
                'labelExternalIdContains': label_external_id_contains,
                'labelTypeIn': label_type_in,
                'labelStatusIn': label_status_in,
                'labelAuthorIn': label_author_in,
                'labelConsensusMarkGte': label_consensus_mark_gt,
                'labelConsensusMarkLte': label_consensus_mark_lt,
                'labelHoneypotMarkGte': label_honeypot_mark_gt,
                'labelHoneypotMarkLte': label_honeypot_mark_lt,
                'labelCreatedAtGte': label_created_at_gt,
                'labelCreatedAtLte': label_created_at_lt,
                'labelSkipped': label_skipped,
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


@deprecate(
    """
        This function is deprecated. get_assets_by_external_id used to fetch assets from an external_id. It is now achievable with assets.
        To fetch assets from and external_id, use:
            > playground.assets(project_id=project_id, external_id_contains=[external_id])
        """)
def get_assets_by_external_id(client, project_id: str, external_id: str):
    return None


def get_next_asset_from_label(client, label_asset_ids: List[str]):
    variables = {'labelAssetIDs': label_asset_ids}
    result = client.execute(GQL_GET_NEXT_ASSET_FROM_LABEL, variables)
    return format_result('data', result)


def get_next_asset_from_project(client, project_id: str):
    variables = {'projectID': project_id}
    result = client.execute(GQL_GET_NEXT_ASSET_FROM_PROJECT, variables)
    return format_result('data', result)


@deprecate(
    """
        This function is deprecated. export_assets used to fetch assets from a project. It is now achievable with assets.
        To fetch assets from a project, use:
            > playground.export_assets(project_id=project_id)
        """)
def export_assets(client, project_id: str):
    return None


def count_assets(client, asset_id: str = None,
                 project_id: str = None,
                 external_id_contains: List[str] = None,
                 status_in: List[str] = None,
                 author_in: List[str] = None,
                 consensus_mark_gt: float = None,
                 consensus_mark_lt: float = None,
                 honeypot_mark_gt: float = None,
                 honeypot_mark_lt: float = None,
                 skipped: bool = None,
                 label_external_id_contains: str = None,
                 label_type_in: List[str] = None,
                 label_status_in: List[str] = None,
                 label_author_in: List[str] = None,
                 label_consensus_mark_gt: float = None,
                 label_consensus_mark_lt: float = None,
                 label_honeypot_mark_gt: float = None,
                 label_honeypot_mark_lt: float = None,
                 label_created_at_gt: float = None,
                 label_created_at_lt: float = None,
                 label_skipped: bool = None):
    variables = {
        'assetID': asset_id,
        'projectID': project_id,
        'externalIdIn': external_id_contains,
        'statusIn': status_in,
        'authorIn': author_in,
        'consensusMarkGte': consensus_mark_gt,
        'consensusMarkLte': consensus_mark_lt,
        'honeypotMarkGte': honeypot_mark_gt,
        'honeypotMarkLte': honeypot_mark_lt,
        'skipped': skipped,
        'labelExternalIdContains': label_external_id_contains,
        'labelTypeIn': label_type_in,
        'labelStatusIn': label_status_in,
        'labelAuthorIn': label_author_in,
        'labelConsensusMarkGte': label_consensus_mark_gt,
        'labelConsensusMarkLte': label_consensus_mark_lt,
        'labelHoneypotMarkGte': label_honeypot_mark_gt,
        'labelHoneypotMarkLte': label_honeypot_mark_lt,
        'labelCreatedAtGte': label_created_at_gt,
        'labelCreatedAtLte': label_created_at_lt,
        'labelSkipped': label_skipped,
    }
    result = client.execute(GQL_ASSETS_COUNT, variables)
    count = format_result('data', result)
    return count
