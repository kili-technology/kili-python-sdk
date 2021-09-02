from functools import partial
from json import dumps
from typing import List, Optional

from typeguard import typechecked

from ...helpers import (Compatible,
                        format_result)
from .queries import GQL_APPEND_TO_LABEL_HISTORY


class MutationsLabelHistory:

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
    def append_to_label_history(self, asset_id: str,
                                author_id: str,
                                input_type: str,
                                json_interface: dict,
                                json_response: dict):
        """
        Appends label to label history
        Parameters
        ----------
        - asset_id : str
            Asset ID
        - author_id : str
            Author ID
        - input_type : str
            Currently, one of {AUDIO, IMAGE, PDF, TEXT, URL, VIDEO, NA}
        - json_interface : dict
            Object of the interface
        - json_response : dict
            Object of the response
        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.
        Examples
        -------
        kili.append_to_label_history(
            asset_id='ckg22d81r0jrg0885unmuswj8',
            author_id='0885unmuswj8ckg22d81r0jrg',
            input_type='IMAGE',
            json_interface={},
            json_response={})
        """

        variables = {
            'assetID': asset_id,
            'authorID': author_id,
            'inputType': input_type,
            'jsonInterface': dumps(json_interface) if json_interface is not None else None,
            'jsonResponse': dumps(json_response) if json_response is not None else None,
        }
        result = self.auth.client.execute(GQL_APPEND_TO_LABEL_HISTORY, variables)
        return format_result('data', result)


    