import time
from json import dumps
from typing import List, Optional

from typeguard import typechecked
import pandas as pd
from tqdm import tqdm

from ...helpers import Compatible, format_result, fragment_builder
from .queries import gql_assets, GQL_DATASET_ASSETS_COUNT
from ...types import DatasetAsset as DatasetAssetType
from ...orm import Asset


class QueriesDatasetAsset:

    def __init__(self, auth):
        """
        Initializes the subclass

        Parameters
        ----------
        - auth : KiliAuth object
        """
        self.auth = auth

    @Compatible(['v2'])
    @typechecked
    def dataset_assets(self, asset_id: Optional[str] = None, dataset_id: Optional[str] = None,
                       skip: int = 0,
                       fields: list = ['content', 'createdAt', 'externalId', 'id', 'jsonMetadata'],
                       disable_tqdm: bool = False,
                       first: Optional[int] = None,
                       ):
        """
        Get an array of dataset assets respecting a set of constraints

        Parameters
        ----------
        - asset_id : str, optional (default = None)
            The unique id of the asset to retrieve.
        - dataset_id : str
            Identifier of the dataset.
        - skip : int, optional (default = None)
            Number of assets to skip (they are ordered by their date of creation, first to last).
        - fields : list of string, optional (default = ['content', 'createdAt', 'externalId', 'id', 'jsonMetadata'])
            All the fields to request among the possible fields for the assets.
            See [the documentation](https://cloud.kili-technology.com/docs/python-graphql-api/graphql-api/#datasetasset) for all possible fields.
        - first : int, optional (default = None)
            Maximum number of assets to return. Can only be between 0 and 100.
        - disable_tqdm : bool, optional (default = False)

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.

        Examples
        -------
        >>> kili.dataset_assets(dataset_id=dataset_id)
        >>> kili.dataset_assets(asset_id=asset_id)
        """
        saved_args = locals()
        count_args = {k: v for (k, v) in saved_args.items()
                      if k not in ['skip', 'first', 'fields', 'self', 'disable_tqdm']}
        number_of_assets_with_search = self.count_dataset_assets(**count_args)
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
                        'dataset': {
                            'id': dataset_id,
                        },
                    },
                    'skip': skip,
                    'first': formatted_first,
                }
                GQL_ASSETS = gql_assets(
                    fragment_builder(fields, DatasetAssetType))
                result = self.auth.client.execute(GQL_ASSETS, variables)
                assets = format_result('data', result, Asset)
                if assets is None or len(assets) == 0 or (first is not None and len(paged_assets) == first):
                    if format == 'pandas':
                        return pd.DataFrame(paged_assets)
                    return paged_assets
                if first is not None:
                    assets = assets[:max(0, first - len(paged_assets))]
                paged_assets += assets
                skip += formatted_first
                pbar.update(len(assets))

    @Compatible(['v2'])
    @typechecked
    def count_dataset_assets(self, asset_id: Optional[str] = None, dataset_id: Optional[str] = None):
        """
        Count and return the number of assets with the given constraints

        Parameters
        ----------
        - asset_id : str, optional (default = None)
            The unique id of the asset to retrieve.
        - dataset_id : str
            Identifier of the dataset.

        Returns
        -------
        - a result object which contains the query if it was successful, or an error message else.

        Examples
        -------
        >>> kili.count_dataset_assets(dataset_id=dataset_id)
        23
        >>> kili.count_dataset_assets(asset_id=asset_id)
        1
        """
        variables = {
            'where': {
                'id': asset_id,
                'dataset': {
                    'id': dataset_id,
                },
            }
        }
        result = self.auth.client.execute(GQL_DATASET_ASSETS_COUNT, variables)
        count = format_result('data', result)
        return count
