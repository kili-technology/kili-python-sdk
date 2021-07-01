from typing import List, Optional
from functools import partial

from typeguard import typechecked

from ...helpers import (Compatible,
                        convert_to_list_of_none,
                        format_metadata,
                        format_result)
from .queries import GQL_UPDATE_PROPERTIES_IN_DATASET_ASSETS
from ...orm import Asset


class MutationsDatasetAsset:

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
    def update_properties_in_dataset_assets(self, asset_ids: List[str],
                                            external_ids: Optional[List[str]] = None,
                                            json_metadatas: Optional[List[dict]] = None,
                                            contents: Optional[List[str]] = None,
                                            json_contents: Optional[List[str]] = None):
        """
        Update the properties of one or more assets of datasets.

        Parameters
        ----------
        - asset_ids : List[str]
            The asset IDs to modify
        - external_ids : List[str], optional (default = None)
            Change the external id of the assets
        - json_metadatas : List[dict] , optional (default = None)
            The metadata given to an asset should be stored in a json like dict with keys 
            "imageUrl", "text", "url".
            json_metadata = {'imageUrl': '','text': '','url': ''}
        - contents : List[str] (default = None)
            - For a NLP project, the content can be directly in text format
            - For an Image / Video / Pdf project, the content must be hosted on a web server,
            and you point Kili to your data by giving the URLs
        - json_contents : List[str] (default = None)
            - For a NLP project, the json_content is a a text formatted using RichText
            - For a Video project, the json_content is a json containg urls pointing to each frame of the video.

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.

        Examples
        -------
        kili.update_properties_in_dataset_assets(
                asset_ids=["ckg22d81r0jrg0885unmuswj8", "ckg22d81s0jrh0885pdxfd03n"],
                contents=[None, 'https://to/second/asset.png'],
                external_ids=['external-id-of-your-choice-1', 'external-id-of-your-choice-2']
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
        list_of_properties = [external_ids,
                              formatted_json_metadatas, contents, json_contents]
        data = list(map(partial(convert_to_list_of_none,
                                length=nb_assets_to_modify), list_of_properties))
        property_names = [
            'externalId',
            'jsonMetadata',
            'content',
            'jsonContent',
            'status'
        ]
        for i, properties in enumerate(zip(*data)):
            for property, property_value in zip(property_names, properties):
                data_array[i][property] = property_value
        variables = {
            'whereArray': where_array,
            'dataArray': data_array
        }
        result = self.auth.client.execute(
            GQL_UPDATE_PROPERTIES_IN_DATASET_ASSETS, variables)
        return format_result('data', result, Asset)
