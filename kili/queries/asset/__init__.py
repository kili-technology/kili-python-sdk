import time
from json import dumps
from typing import List

import pandas as pd
from tqdm import tqdm

from ...helpers import format_result
from .queries import (GQL_COUNT_ASSETS_WITH_SEARCH, GQL_EXPORT_ASSETS,
                      GQL_GET_ASSET, GQL_GET_ASSETS_BY_EXTERNAL_ID,
                      GQL_GET_ASSETS_WITH_SEARCH,
                      GQL_GET_NEXT_ASSET_FROM_LABEL,
                      GQL_GET_NEXT_ASSET_FROM_PROJECT)


def get_asset(client, asset_id: str):
    variables = {'assetID': asset_id}
    result = client.execute(GQL_GET_ASSET, variables)
    return format_result('data', result)


def get_assets(client, project_id: str, skip: int = 0, first: int = None,
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
               format: str = None, disable_tqdm: bool = False):
    saved_args = locals()
    count_args = {k: v for (k, v) in saved_args.items()
                  if k not in ['skip', 'first', 'disable_tqdm', 'format']}
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
            result = client.execute(GQL_GET_ASSETS_WITH_SEARCH, variables)
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


def get_assets_by_external_id(client, project_id: str, external_id: str):
    variables = {'projectID': project_id, 'externalID': external_id}
    result = client.execute(GQL_GET_ASSETS_BY_EXTERNAL_ID, variables)
    return format_result('data', result)


def get_next_asset_from_label(client, label_asset_ids: List[str]):
    variables = {'labelAssetIDs': label_asset_ids}
    result = client.execute(GQL_GET_NEXT_ASSET_FROM_LABEL, variables)
    return format_result('data', result)


def get_next_asset_from_project(client, project_id: str):
    variables = {'projectID': project_id}
    result = client.execute(GQL_GET_NEXT_ASSET_FROM_PROJECT, variables)
    return format_result('data', result)


def export_assets(client, project_id: str):
    variables = {'projectID': project_id}
    result = client.execute(GQL_EXPORT_ASSETS, variables)
    return format_result('exportAssets', result)


def count_assets(client, project_id: str,
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
    result = client.execute(GQL_COUNT_ASSETS_WITH_SEARCH, variables)
    count = format_result('data', result)
    return count
