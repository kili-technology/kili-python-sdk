from json import dumps
from typing import List

from ...helpers import Compatible, format_result
from .queries import (GQL_APPEND_TO_LABELS, GQL_CREATE_HONEYPOT,
                      GQL_CREATE_PREDICTIONS,
                      GQL_UPDATE_PROPERTIES_IN_LABEL)


class MutationsLabel:

    def __init__(self, auth):
        """
        Initializes the subclass

        Parameters
        ----------
        - auth : KiliAuth object
        """
        self.auth = auth

    @Compatible(['v1', 'v2'])
    def create_predictions(self, project_id: str, external_id_array: List[str], model_name_array: List[str], json_response_array: List[dict]):
        """
        Create predictions for some assets

        For more detailed examples on how to create predictions, see [the recipe](https://github.com/kili-technology/kili-playground/blob/master/recipes/import_predictions.ipynb).

        Parameters
        ----------
        - project_id : str
        - external_id_array : list of str
            The external identifiers of the assets for which we want to add predictions
        - model_name_array : list of str
            In case you want to precise from which model the label originated
        - json_response_array : list of dict
            The predictions are given here. An example can be found here, for a polygon.
            For other examples, see [the recipe](https://github.com/kili-technology/kili-playground/blob/master/recipes/import_predictions.ipynb).
            ```
            {
                "JOB_0": {
                    "annotations": [
                        {
                            "categories": [{ "name": "OBJECT_B", "confidence": 100 }],
                            "boundingPoly": [
                                {
                                    "normalizedVertices": [
                                        { "x": 0.07, "y": 0.88 },
                                        { "x": 0.07, "y": 0.32 },
                                        { "x": 0.94, "y": 0.32 },
                                        { "x": 0.94, "y": 0.88 }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
            ```

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.
        """
        assert len(external_id_array) == len(
            json_response_array), "IDs list and predictions list should have the same length"
        assert len(external_id_array) == len(
            model_name_array), "IDs list and model names list should have the same length"
        variables = {
            'projectID': project_id,
            'externalIDArray': external_id_array,
            'modelNameArray': model_name_array,
            'jsonResponseArray': [dumps(elem) for elem in json_response_array]
        }
        result = self.auth.client.execute(GQL_CREATE_PREDICTIONS, variables)
        return format_result('data', result)

    @Compatible(['v1', 'v2'])
    def append_to_labels(self, json_response: dict, label_asset_id: str, author_id: str = None, label_type: str = 'DEFAULT', seconds_to_label: int = 0, skipped: bool = False):
        """
        Append a label to an asset

        Parameters
        ----------
        - json_response : dict
            Label is given here
        - label_asset_id : str
            Identifier of the asset
        - author_id : str, optional (default = auth.user_id)
            ID of the author of the label
        - label_type : str, optional (default = 'DEFAULT')
            Can be one of {'AUTOSAVE', 'DEFAULT', 'PREDICTION', 'REVIEW'}
        - seconds_to_label : int, optional (default = 0)
        - skipped : bool, optional (default = False)

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.

        Examples
        -------
        >>> playground.append_to_labels(label_asset_id=asset_id, json_response={...})
        """
        if author_id is None:
            author_id = self.auth.user_id
        variables = {
            'authorID': author_id,
            'jsonResponse': dumps(json_response),
            'labelAssetID': label_asset_id,
            'labelType': label_type,
            'secondsToLabel': seconds_to_label,
            'skipped': skipped
        }
        result = self.auth.client.execute(GQL_APPEND_TO_LABELS, variables)
        return format_result('data', result)

    @Compatible(['v1', 'v2'])
    def update_properties_in_label(self, label_id: str, seconds_to_label: int = None, model_name: str = None, json_response: dict = None):
        """
        Update properties of a label

        Parameters
        ----------
        - label_id : str
            Identifier of the label
        - seconds_to_label : int, optional (default = None)
        - model_name : str, optional (default = None)
        - json_response : dict, optional (default = None)
            The label is given here

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.

        Examples
        -------
        >>> playground.update_properties_in_label(label_id=label_id, json_response={...})
        """
        formatted_json_response = None if json_response is None else dumps(
            json_response)
        variables = {
            'labelID': label_id,
            'secondsToLabel': seconds_to_label,
            'modelName': model_name,
            'jsonResponse': formatted_json_response
        }
        result = self.auth.client.execute(
            GQL_UPDATE_PROPERTIES_IN_LABEL, variables)
        return format_result('data', result)

    @Compatible(['v1', 'v2'])
    def create_honeypot(self, asset_id: str, json_response: dict):
        """
        Create honeypot for an asset. 

        Uses the json_response given to create a "REVIEW" label. This allows to compute a `honeypotMark`,
        which measures how similar are other labels compared to this one.

        Parameters
        ----------
        - asset_id : str
            Identifier of the asset
        - json_response : dict
            The honeypot label of the asset

        Returns
        -------
        - a result object which indicates if the mutation was successful, or an error message else.
        """
        variables = {
            'assetID': asset_id,
            'jsonResponse': dumps(json_response)
        }
        result = self.auth.client.execute(GQL_CREATE_HONEYPOT, variables)
        return format_result('data', result)
