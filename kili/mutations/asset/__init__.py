from json import dumps
from uuid import uuid4
from typing import List
from functools import partial

from ...helpers import (Compatible,
                        content_escape,
                        convert_to_list_of_none,
                        deprecate,
                        encode_image,
                        format_metadata,
                        format_result,
                        is_not_none_or_empty,
                        is_url)
from ...queries.project import QueriesProject
from ...queries.asset import QueriesAsset
from .queries import (GQL_APPEND_MANY_TO_DATASET,
                      GQL_DELETE_MANY_FROM_DATASET,
                      GQL_UPDATE_PROPERTIES_IN_ASSET,
                      GQL_UPDATE_PROPERTIES_IN_ASSETS)
from ...constants import NO_ACCESS_RIGHT


class MutationsAsset:

    def __init__(self, auth):
        """
        Initializes the subclass

        Parameters
        ----------
        - auth : KiliAuth object
        """
        self.auth = auth

    @Compatible(['v1', 'v2'])
    def append_many_to_dataset(self, project_id: str, content_array: List[str] = None, external_id_array: List[str] = None,
                               is_honeypot_array: List[bool] = None, status_array: List[str] = None, json_content_array: List[List[str]] = None,
                               json_metadata_array: List[dict] = None):
        """
        Append assets to a project

        Parameters
        ----------
        - project_id : str
            Identifier of the project
        - content_array : List[str], optional (default = None)
            List of elements added to the assets of the project
            - For a Text project, the content is directly in text format.
            - For an Image project, the content can be paths to existing images on your computer.
            - For an Image / Video / Pdf project, the content must be hosted on a web server,
            and you point Kili to your data by giving the URLs.
            Must not be None except if you provide json_content_array.
        - external_id_array : List[str], optional (default = None)
            List of external ids given to identify the assets. If None, random identifiers are created.
        - is_honeypot_array : List[bool], optional (default = None)
        - status_array : List[str], optional (default = None)
            By default, all imported assets are set to 'TODO'. It can also be set to
            'ONGOING', 'LABELED', 'REVIEWED'
        - json_content_array : List[List[str]], optional (default = None)
            Useful for 'FRAME' projects only. Each element is a sequence of frames,
            i.e. a list of URLs to images.
        - json_metadata_array : List[Dict] , optional (default = None)
            The metadata given to each asset should be stored in a json like dict with keys 
            "imageUrl", "text", "url".
            json_metadata_array = [{'imageUrl': '','text': '','url': ''}] to upload one asset.

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.
        """
        playground = QueriesProject(self.auth)
        projects = playground.projects(project_id)
        assert len(projects) == 1, NO_ACCESS_RIGHT
        input_type = projects[0]['inputType']

        if content_array is None and json_content_array is None:
            raise ValueError(
                f"Variables content_array and json_content_array cannot be both None.")
        if content_array is None:
            content_array = [''] * len(json_content_array)
        if external_id_array is None:
            external_id_array = [
                uuid4().hex for _ in range(len(content_array))]
        is_honeypot_array = [
            False] * len(content_array) if not is_honeypot_array else is_honeypot_array
        status_array = ['TODO'] * \
            len(content_array) if not status_array else status_array
        if not json_content_array:
            formatted_json_content_array = [''] * len(content_array)
        elif input_type == 'FRAME':
            formatted_json_content_array = list(map(lambda json_content: dumps(
                dict(zip(range(len(json_content)), json_content))), json_content_array))
        else:
            formatted_json_content_array = [
                element if is_url(element) else dumps(element)
                for element in json_content_array]
        json_metadata_array = [
            {}] * len(content_array) if not json_metadata_array else json_metadata_array
        formatted_json_metadata_array = [
            dumps(elem) for elem in json_metadata_array]
        if input_type == 'IMAGE':
            content_array = [content if is_url(content) else encode_image(
                content) for content in content_array]
        elif input_type == 'FRAME' and json_content_array is None:
            for content in content_array:
                if not is_url(content):
                    raise ValueError(
                        f"Content {content} isn't a link to a video")
        variables = {
            'projectID': project_id,
            'contentArray': content_array,
            'externalIDArray': external_id_array,
            'isHoneypotArray': is_honeypot_array,
            'statusArray': status_array,
            'jsonContentArray': formatted_json_content_array,
            'jsonMetadataArray': formatted_json_metadata_array}
        result = self.auth.client.execute(
            GQL_APPEND_MANY_TO_DATASET, variables)
        return format_result('data', result)

    @Compatible()
    def update_properties_in_asset(self, asset_id: str, external_id: str = None,
                                   priority: int = None, json_metadata: dict = None, consensus_mark: float = None,
                                   honeypot_mark: float = None, to_be_labeled_by: List[str] = None, content: str = None,
                                   status: str = None, is_used_for_consensus: bool = None, is_honeypot: bool = None):
        """
        Update the properties of one asset

        Parameters
        ----------
        - asset_id : str
            The id of the asset to modify
        - external_id : str, optional (default = None)
            Change the external id of the asset
        - priority : int, optional (default = None)
            By default, all assets have a priority of 0
        - json_metadata : dict , optional (default = None)
            The metadata given to an asset should be stored in a json like dict with keys 
            "imageUrl", "text", "url".
            json_metadata = {'imageUrl': '','text': '','url': ''}
        - consensus_mark : float (default = None)
            Should be between 0 and 1
        - honeypot_mark : float (default = None)
            Should be between 0 and 1
        - to_be_labeled_by : list of str (default = None)
            If given, should contain the emails of the labelers authorized to label the asset
        - content : str (default = None)
            - For a NLP project, the content is directly in text format
            - For an Image / Video / Pdf project, the content must be hosted on a web server,
            and you point Kili to your data by giving the URLs
        - status : str (default = None)
            Should be in {'TODO', 'ONGOING', 'LABELED', 'REVIEWED'}
        - is_used_for_consensus : bool (default = None)
            Whether to use the asset to compute consensus kpis or not
        - is_honeypot : bool (default = None)
            Whether to use the asset for honeypot

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.
        """

        formatted_json_metadata = None
        if json_metadata is None:
            formatted_json_metadata = None
        elif isinstance(json_metadata, str):
            formatted_json_metadata = json_metadata
        elif isinstance(json_metadata, dict) or isinstance(json_metadata, list):
            formatted_json_metadata = dumps(json_metadata)
        else:
            raise Exception('json_metadata',
                            'Should be either a dict, a list or a string url')
        should_reset_to_be_labeled_by = to_be_labeled_by is not None and len(
            to_be_labeled_by) == 0
        variables = {
            'assetID': asset_id,
            'externalID': external_id,
            'priority': priority,
            'jsonMetadata': formatted_json_metadata,
            'consensusMark': consensus_mark,
            'honeypotMark': honeypot_mark,
            'toBeLabeledBy': to_be_labeled_by,
            'shouldResetToBeLabeledBy': should_reset_to_be_labeled_by,
            'content': content,
            'status': status,
            'isUsedForConsensus': is_used_for_consensus,
            'isHoneypot': is_honeypot,
        }
        result = self.auth.client.execute(
            GQL_UPDATE_PROPERTIES_IN_ASSET, variables)
        return format_result('data', result)

    @Compatible(['v2'])
    def update_properties_in_assets(self, asset_ids: List[str], external_ids: List[str] = None,
                                    priorities: List[int] = None, json_metadatas: List[dict] = None, consensus_marks: List[float] = None,
                                    honeypot_marks: List[float] = None, to_be_labeled_by_array: List[List[str]] = None, contents: List[str] = None,
                                    status_array: List[str] = None, is_used_for_consensus_array: List[bool] = None, is_honeypot_array: List[bool] = None):
        """
        Update the properties of one or more assets.

        This function is only available with the new endpoint : https://cloud.kili-technology.com/api/label/v2/graphql
        Example usage : 
        ```
        playground.update_properties_in_assets(
            asset_ids=["ckg22d81r0jrg0885unmuswj8", "ckg22d81s0jrh0885pdxfd03n"],
            priorities=[None, 2],
            external_ids=['op', 'truc'],
            consensus_marks=[1, 0.7],
            honeypot_marks=[0.8, 0.5],
            to_be_labeled_by_array=[['test+pierre@kili-technology.com'], None],
            contents=[None, 'https://drive.google.com/uc?export=download&id=1mM7ASFB4pGEk5rcr7pcw6qB8WVybTPmo'],
            status_array=['LABELED', 'REVIEWED'],
            is_used_for_consensus_array=[True, False],
            is_honeypot_array=[True, True]
        )
        ```

        Parameters
        ----------
        - asset_ids : List[str]
            The asset ids to modify
        - external_ids : List[str], optional (default = None)
            Change the external id of the assets
        - priorities : List[int], optional (default = None)
            You can change the priority of the assets
            By default, all assets have a priority of 0.
        - json_metadatas : List[dict] , optional (default = None)
            The metadata given to an asset should be stored in a json like dict with keys 
            "imageUrl", "text", "url".
            json_metadata = {'imageUrl': '','text': '','url': ''}
        - consensus_marks : List[float] (default = None)
            Should be between 0 and 1
        - honeypot_marks : List[float] (default = None)
            Should be between 0 and 1
        - to_be_labeled_by_array : List[List[str]] (default = None)
            If given, each element of the list should contain the emails of the labelers authorized to label the asset.
        - contents : List[str] (default = None)
            - For a NLP project, the content can be directly in text format
            - For an Image / Video / Pdf project, the content must be hosted on a web server,
            and you point Kili to your data by giving the URLs
        - status_array : List[str] (default = None)
            Each element should be in {'TODO', 'ONGOING', 'LABELED', 'REVIEWED'}
        - is_used_for_consensus_array : List[bool] (default = None)
            Whether to use the asset to compute consensus kpis or not
        - is_honeypot_array : List[bool] (default = None)
            Whether to use the asset for honeypot

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.
        """

        formatted_json_metadatas = None
        if json_metadatas is None:
            formatted_json_metadatas = None
        else:
            if isinstance(json_metadatas, list):
                formatted_json_metadatas = list(
                    map(format_metadata, json_metadatas))
            else:
                raise Exception('json_metadatas',
                                'Should be either a None or a list of None, string, list or dict')

        where_array = [{'id': asset_id} for asset_id in asset_ids]
        nb_assets_to_modify = len(where_array)
        if nb_assets_to_modify > 100:
            raise Exception(
                f'Too many assets ({nb_assets_to_modify}) updated at a time')
        data_array = [{} for i in range(len(where_array))]
        list_of_properties = [external_ids, priorities, formatted_json_metadatas, consensus_marks, honeypot_marks, to_be_labeled_by_array,
                              contents, status_array, is_used_for_consensus_array, is_honeypot_array]
        data = list(map(partial(convert_to_list_of_none,
                                length=nb_assets_to_modify), list_of_properties))
        property_names = [
            'externalId',
            'priority',
            'jsonMetadata',
            'consensusMark',
            'honeypotMark',
            'toBeLabeledBy',
            'content',
            'status',
            'isUsedForConsensus',
            'isHoneypot'
        ]
        to_be_labeled_by_array = data[5]
        should_reset_to_be_labeled_by_array = list(
            map(is_not_none_or_empty, to_be_labeled_by_array))
        for i, properties in enumerate(zip(*data)):
            for property, property_value in zip(property_names, properties):
                data_array[i][property] = property_value
        for i in range(nb_assets_to_modify):
            data_array[i]['shouldResetToBeLabeledBy'] = should_reset_to_be_labeled_by_array[i]
        variables = {
            'whereArray': where_array,
            'dataArray': data_array
        }
        result = self.auth.client.execute(
            GQL_UPDATE_PROPERTIES_IN_ASSETS, variables)
        return format_result('data', result)

    @Compatible(['v1', 'v2'])
    def delete_many_from_dataset(self, asset_ids: List[str]):
        """
        Delete assets from a project

        Parameters
        ----------
        - asset_ids : list of str
            The list of identifiers of the assets to delete.

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.
        """
        variables = {'assetIDs': asset_ids}
        result = self.auth.client.execute(
            GQL_DELETE_MANY_FROM_DATASET, variables)
        return format_result('data', result)
