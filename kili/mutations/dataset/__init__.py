"""
Dataset mutations
"""

from typing import List, Optional
from functools import partial

from typeguard import typechecked

from ...helpers import (Compatible,
                        format_result)
from .queries import GQL_APPEND_DATASETS_TO_PROJECT, GQL_APPEND_TO_DATASET, \
    GQL_APPEND_TO_DATASET_USERS, GQL_CREATE_DATASET, GQL_DELETE_DATASET, \
    GQL_UPDATE_PROPERTIES_IN_DATASET


class MutationsDataset:
    """
    Set of Dataset mutations
    """

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
    def append_to_dataset(self, content_array: List[str],
                          dataset_id: str,
                          external_id_array: List[str]):
        """
        Appends assets to a dataset.

        Parameters
        ----------
        - content_array : List[str]
            List of asset content to add
        - dataset_id : str
            Id of the target dataset
        - external_id_array : List[str]
            List of asset external ids to add

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.

        Examples
        -------
        kili.append_to_dataset(
            content_array=['Hello world!'],
            dataset_id='ckg22d81r0jrg0885unmuswj8',
            external_ids=['text-1'])
        """

        variables = {
            'data': {'contentArray': content_array,
                     'externalIdArray': external_id_array},
            'where': {'id': dataset_id}
        }
        result = self.auth.client.execute(GQL_APPEND_TO_DATASET, variables)
        return format_result('data', result)

    @Compatible(['v2'])
    @typechecked
    def append_to_dataset_users(self, dataset_id: str, user_email: str):
        """
        Adds users to a dataset.

        Parameters
        ----------
        - dataset_id : str
            Id of the target dataset
        - user_email : str
            Email of the user to add to the dataset

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.

        Examples
        -------
        kili.append_to_dataset_users(
            user_email='colleague@company.com',
            dataset_id='ckg22d81r0jrg0885unmuswj8',
        )
        """

        variables = {
            'data': {'userEmail': user_email},
            'where': {'id': dataset_id}
        }
        result = self.auth.client.execute(
            GQL_APPEND_TO_DATASET_USERS, variables)
        return format_result('data', result)

    @Compatible(['v2'])
    @typechecked
    def append_datasets_to_project(self, project_id: str,
                                   dataset_ids: List[str],
                                   dataset_asset_ids: List[str]):
        """
        Appends dataset assets to a project.

        Parameters
        ----------
        - project_id : str
            Id of the target project
        - dataset_ids : List[str]
            Ids of the source datasets
        - dataset_asset_ids : List[dict]
            List of asset ids

        Returns
        -------
        - a number indicating how many assets were added.

        Examples
        -------
        kili.append_datasets_to_project(
            project_id='ckg22d81s0jrh0885pdxfd03n',
            dataset_ids=['ckg22d81r0jrg0885unmuswj8'],
            dataset_asset_ids=['s0jrh0885unm1s0j0jrh0885p'])
        """

        variables = {
            'data': {'datasetIds': dataset_ids,
                     'datasetAssetIds': dataset_asset_ids},
            'where': {'id': project_id}
        }
        result = self.auth.client.execute(
            GQL_APPEND_DATASETS_TO_PROJECT, variables)
        return format_result('data', result)

    @Compatible(['v2'])
    @typechecked
    def create_dataset(self, name: str, asset_type: str):
        """
        Creates a dataset.

        Parameters
        ----------
        - name : str
            Id of the target project
        - asset_type : str
            Currently, one of {AUDIO, IMAGE, PDF, TEXT, URL, VIDEO, NA}

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.

        Examples
        -------
        kili.create_dataset(
            name='My image dataset',
            asset_type='IMAGE')
        """

        variables = {
            'data': {'name': name,
                     'assetType': asset_type},
        }
        result = self.auth.client.execute(GQL_CREATE_DATASET, variables)
        return format_result('data', result)

    @Compatible(['v2'])
    @typechecked
    def delete_dataset(self, dataset_id: str):
        """
        Deletes a dataset.

        Parameters
        ----------
        - dataset_id : str
            Id of the dataset to delete

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.

        Examples
        -------
        kili.delete_dataset(
            dataset_id='ckg22d81r0jrg0885unmuswj8')
        """

        variables = {
            'where': {'id': dataset_id},
        }
        result = self.auth.client.execute(GQL_DELETE_DATASET, variables)
        return format_result('data', result)

    @Compatible(['v2'])
    @typechecked
    def update_properties_in_dataset(self, dataset_id: str, asset_type: str, name: str):
        """
        Update properties in a dataset.

        Parameters
        ----------
        - dataset_id : str
            Id of the dataset to delete
        - asset_type : str
            Currently, one of {AUDIO, IMAGE, PDF, TEXT, URL, VIDEO, NA}
        - name : str
            Id of the target project

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.

        Examples
        -------
        kili.update_properties_in_dataset(
            dataset_id='ckg22d81r0jrg0885unmuswj8',
            asset_type='IMAGE',
            name='Image dataset')
        """

        variables = {
            'assetType': asset_type,
            'datasetId': dataset_id,
            'name': name,
        }
        result = self.auth.client.execute(
            GQL_UPDATE_PROPERTIES_IN_DATASET, variables)
        return format_result('data', result)
