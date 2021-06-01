from json import dumps
from uuid import uuid4
from typing import List, Optional, Union
from functools import partial

from typeguard import typechecked

from ...helpers import (Compatible,
                        content_escape,
                        convert_to_list_of_none,
                        deprecate,
                        encode_base64,
                        format_metadata,
                        format_result,
                        is_none_or_empty,
                        is_url,
                        list_is_not_none_else_none)
from ...queries.project import QueriesProject
from ...queries.asset import QueriesAsset
from .queries import (GQL_APPEND_MANY_TO_DATASET,
                      GQL_DELETE_MANY_FROM_DATASET,
                      GQL_UPDATE_PROPERTIES_IN_ASSETS)
from ...constants import NO_ACCESS_RIGHT
from ...orm import Asset


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
    @typechecked
    def append_many_to_dataset(self, project_id: str, content_array: Optional[List[str]] = None, external_id_array: Optional[List[str]] = None,
                               is_honeypot_array: Optional[List[bool]] = None, status_array: Optional[List[str]] = None, json_content_array: Optional[List[List[Union[dict, str]]]] = None,
                               json_metadata_array: Optional[List[dict]] = None):
        """
        Append assets to a project

        For more detailed examples on how to import assets, see [the recipe](https://github.com/kili-technology/kili-playground/blob/master/recipes/import_assets.ipynb).
        For more detailed examples on how to import specifically text assets, see [the recipe](https://github.com/kili-technology/kili-playground/blob/master/recipes/import_text_assets.ipynb).

        Parameters
        ----------
        - project_id : str
            Identifier of the project
        - content_array : List[str], optional (default = None)
            List of elements added to the assets of the project
            - For a Text project, the content can be either raw text, or URLs to TEXT assets.
            - For an Image / PDF project, the content can be either URLs or paths to existing images/pdf on your computer.
            - For a Video  project, the content must be hosted on a web server,
            and you point Kili to your data by giving the URLs.
            Must not be None except if you provide json_content_array.
        - external_id_array : List[str], optional (default = None)
            List of external ids given to identify the assets. If None, random identifiers are created.
        - is_honeypot_array : List[bool], optional (default = None)
        - status_array : List[str], optional (default = None)
            By default, all imported assets are set to 'TODO'. It can also be set to
            'ONGOING', 'LABELED', 'REVIEWED'
        - json_content_array : List[List[str]], optional (default = None)
            Useful for 'FRAME' or 'TEXT' projects only. 
            For FRAME projects, each element is a sequence of frames, i.e. a list of URLs to images or a list of paths to images 
            For TEXT projects, each element is a json_content dict, formatted according to documentation on how to import rich-text assets: https://github.com/kili-technology/kili-playground/blob/master/recipes/import_text_assets.ipynb
        - json_metadata_array : List[Dict] , optional (default = None)
            The metadata given to each asset should be stored in a json like dict with keys 
            "imageUrl", "text", "url".
            json_metadata_array = [{'imageUrl': '','text': '','url': ''}] to upload one asset.

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.

        Examples
        -------
        >>> kili.append_many_to_dataset(project_id=project_id, content_array=['https://upload.wikimedia.org/wikipedia/en/7/7d/Lenna_%28test_image%29.png'])
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
            formatted_json_content_array = list(map(lambda json_content: json_content if is_url(json_content) else dumps(
                dict(zip(range(len(json_content)), list(map(lambda frame_content: frame_content if is_url(frame_content) else encode_base64(frame_content), json_content))))), json_content_array))
        else:
            formatted_json_content_array = [
                element if is_url(element) else dumps(element)
                for element in json_content_array]
        json_metadata_array = [
            {}] * len(content_array) if not json_metadata_array else json_metadata_array
        formatted_json_metadata_array = [
            dumps(elem) for elem in json_metadata_array]
        if input_type == 'IMAGE' or input_type == 'PDF':
            content_array = [content if is_url(content) else encode_base64(
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
        return format_result('data', result, Asset)

    @Compatible(['v2'])
    @typechecked
    def update_properties_in_assets(self, asset_ids: List[str],
                                    external_ids: Optional[List[str]] = None,
                                    priorities: Optional[List[int]] = None, json_metadatas: Optional[List[dict]] = None, consensus_marks: Optional[List[float]] = None,
                                    honeypot_marks: Optional[List[float]] = None, to_be_labeled_by_array: Optional[List[List[str]]] = None, contents: Optional[List[str]] = None,
                                    json_contents: Optional[List[str]] = None, status_array: Optional[List[str]] = None, is_used_for_consensus_array: Optional[List[bool]] = None, 
                                    is_honeypot_array: Optional[List[bool]] = None):
        """
        Update the properties of one or more assets.

        Parameters
        ----------
        - asset_ids : List[str]
            The asset IDs to modify
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
        - json_contents : List[str] (default = None)
            - For a NLP project, the json_content is a a text formatted using RichText
            - For a Video project, the json_content is a json containg urls pointing to each frame of the video.
        - status_array : List[str] (default = None)
            Each element should be in {'TODO', 'ONGOING', 'LABELED', 'REVIEWED'}
        - is_used_for_consensus_array : List[bool] (default = None)
            Whether to use the asset to compute consensus kpis or not
        - is_honeypot_array : List[bool] (default = None)
            Whether to use the asset for honeypot

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.

        Examples
        -------
        kili.update_properties_in_assets(
                asset_ids=["ckg22d81r0jrg0885unmuswj8", "ckg22d81s0jrh0885pdxfd03n"],
                consensus_marks=[1, 0.7],
                contents=[None, 'https://to/second/asset.png'],
                external_ids=['external-id-of-your-choice-1', 'external-id-of-your-choice-2'],
                honeypot_marks=[0.8, 0.5],
                is_honeypot_array=[True, True],
                is_used_for_consensus_array=[True, False],
                priorities=[None, 2],
                status_array=['LABELED', 'REVIEWED'],
                to_be_labeled_by_array=[['test+pierre@kili-technology.com'], None],
        )
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
                              contents, json_contents, status_array, is_used_for_consensus_array, is_honeypot_array]
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
            'jsonContent',
            'status',
            'isUsedForConsensus',
            'isHoneypot'
        ]
        to_be_labeled_by_array = data[5]
        should_reset_to_be_labeled_by_array = list(
            map(is_none_or_empty, to_be_labeled_by_array))
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
        return format_result('data', result, Asset)

    @Compatible(['v1', 'v2'])
    @typechecked
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
        return format_result('data', result, Asset)
