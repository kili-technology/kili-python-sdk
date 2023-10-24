import json
from unittest.mock import MagicMock

import pytest

from kili.adapters.kili_api_gateway.label.operations import (
    get_append_many_labels_mutation,
)


def mocked_AssetQuery(*_):
    return [
        {"id": "asset_id_1", "externalId": "asset_external_id_1"},
        {"id": "asset_id_2", "externalId": "asset_external_id_2"},
    ]


class TestImportLabelsFromDict:
    """Test class for import_label_from_dict_service."""

    def setup_class(self):
        self.kili = MagicMock()
        self.kili.kili_api_gateway.list_assets = MagicMock(side_effect=mocked_AssetQuery)
        self.kili.graphql_client.execute = MagicMock()
        with open(
            "./tests/unit/services/import_labels/fixtures/json_response_image.json"
        ) as json_file:
            self.json_response = json.load(json_file)

    def test_import_default_labels_with_asset_id(self):
        project_id = "project_id"
        label_type = "DEFAULT"
        overwrite = False
        model_name = None
        labels = [
            {"json_response": self.json_response, "asset_id": "asset_id_1"},
            {"json_response": self.json_response, "asset_id": "asset_id_2"},
        ]

        call = {
            "data": {
                "labelType": "DEFAULT",
                "overwrite": overwrite,
                "labelsData": [
                    {
                        "assetID": "asset_id_1",
                        "authorID": None,
                        "jsonResponse": json.dumps(self.json_response),
                        "modelName": None,
                        "secondsToLabel": None,
                    },
                    {
                        "assetID": "asset_id_2",
                        "authorID": None,
                        "jsonResponse": json.dumps(self.json_response),
                        "modelName": None,
                        "secondsToLabel": None,
                    },
                ],
            },
            "where": {"idIn": ["asset_id_1", "asset_id_2"]},
        }

        import_labels_from_dict(self.kili, project_id, labels, label_type, overwrite, model_name)
        self.kili.graphql_client.execute.assert_called_with(
            get_append_many_labels_mutation(" id"), call, timeout=60
        )

    def test_import_default_labels_with_external_id(self):
        project_id = "project_id"
        label_type = "DEFAULT"
        overwrite = False
        model_name = None
        labels = [
            {"json_response": self.json_response, "asset_external_id": "asset_external_id_1"},
            {"json_response": self.json_response, "asset_external_id": "asset_external_id_2"},
        ]

        call = {
            "data": {
                "labelType": "DEFAULT",
                "overwrite": overwrite,
                "labelsData": [
                    {
                        "assetID": "asset_id_1",
                        "authorID": None,
                        "jsonResponse": json.dumps(self.json_response),
                        "modelName": None,
                        "secondsToLabel": None,
                    },
                    {
                        "assetID": "asset_id_2",
                        "authorID": None,
                        "jsonResponse": json.dumps(self.json_response),
                        "modelName": None,
                        "secondsToLabel": None,
                    },
                ],
            },
            "where": {"idIn": ["asset_id_1", "asset_id_2"]},
        }

        import_labels_from_dict(self.kili, project_id, labels, label_type, overwrite, model_name)
        self.kili.graphql_client.execute.assert_called_with(
            get_append_many_labels_mutation(" id"), call, timeout=60
        )

    def test_import_labels_with_optional_params(self):
        project_id = "project_id"
        label_type = "DEFAULT"
        model_name = None
        overwrite = False
        author_id = "author_id"
        seconds_to_label = 3
        labels = [
            {
                "json_response": self.json_response,
                "asset_id": "asset_id",
                "author_id": author_id,
                "seconds_to_label": seconds_to_label,
            }
        ]

        call = {
            "data": {
                "labelType": "DEFAULT",
                "overwrite": overwrite,
                "labelsData": [
                    {
                        "assetID": "asset_id",
                        "authorID": author_id,
                        "jsonResponse": json.dumps(self.json_response),
                        "modelName": None,
                        "secondsToLabel": seconds_to_label,
                    }
                ],
            },
            "where": {"idIn": ["asset_id"]},
        }

        import_labels_from_dict(self.kili, project_id, labels, label_type, overwrite, model_name)
        self.kili.graphql_client.execute.assert_called_with(
            get_append_many_labels_mutation(" id"), call, timeout=60
        )

    def test_return_error_when_give_unexisting_label_field(self):
        project_id = "project_id"
        label_type = "DEFAULT"
        overwrite = False
        model_name = None
        labels = [
            {"json_response": self.json_response, "asset_id": "asset_id", "unexisting_field": 3}
        ]
        with pytest.raises(ValueError, match="The `unexisting_field` key is not a valid key."):
            import_labels_from_dict(
                self.kili, project_id, labels, label_type, overwrite, model_name
            )

    def test_return_error_when_give_wrong_field_type(self):
        project_id = "project_id"
        label_type = "DEFAULT"
        overwrite = False
        model_name = None
        labels = [
            {
                "json_response": self.json_response,
                "asset_id": "asset_id",
                "seconds_to_label": "wrong_type",
            }
        ]
        with pytest.raises(TypeError):
            import_labels_from_dict(
                self.kili, project_id, labels, label_type, overwrite, model_name
            )

    def test_import_predictions(self):
        project_id = "project_id"
        label_type = "PREDICTION"
        model_name = "model_name"
        overwrite = False
        labels = [
            {"json_response": self.json_response, "asset_external_id": "asset_external_id_1"},
            {"json_response": self.json_response, "asset_external_id": "asset_external_id_2"},
        ]

        call = {
            "data": {
                "labelType": "PREDICTION",
                "overwrite": overwrite,
                "labelsData": [
                    {
                        "assetID": "asset_id_1",
                        "authorID": None,
                        "jsonResponse": json.dumps(self.json_response),
                        "modelName": model_name,
                        "secondsToLabel": None,
                    },
                    {
                        "assetID": "asset_id_2",
                        "authorID": None,
                        "jsonResponse": json.dumps(self.json_response),
                        "modelName": model_name,
                        "secondsToLabel": None,
                    },
                ],
            },
            "where": {"idIn": ["asset_id_1", "asset_id_2"]},
        }

        import_labels_from_dict(self.kili, project_id, labels, label_type, overwrite, model_name)
        self.kili.graphql_client.execute.assert_called_with(
            get_append_many_labels_mutation(" id"), call, timeout=60
        )

    def test_import_predictions_with_overwritting(self):
        project_id = "project_id"
        label_type = "PREDICTION"
        model_name = "model_name"
        overwrite = True
        labels = [
            {"json_response": self.json_response, "asset_external_id": "asset_external_id_1"},
        ]

        call = {
            "data": {
                "labelType": "PREDICTION",
                "overwrite": overwrite,
                "labelsData": [
                    {
                        "assetID": "asset_id_1",
                        "authorID": None,
                        "jsonResponse": json.dumps(self.json_response),
                        "modelName": model_name,
                        "secondsToLabel": None,
                    },
                ],
            },
            "where": {"idIn": ["asset_id_1"]},
        }

        import_labels_from_dict(self.kili, project_id, labels, label_type, overwrite, model_name)
        self.kili.graphql_client.execute.assert_called_with(
            get_append_many_labels_mutation(" id"), call, timeout=60
        )

    def test_import_predictions_without_giving_model_name(self):
        self.kili.assets = MagicMock(
            return_value=[{"id": "asset_id", "externalId": "asset_external_id"}]
        )
        project_id = "project_id"
        label_type = "PREDICTION"
        model_name = None
        overwrite = False
        labels = [{"json_response": self.json_response, "asset_external_id": "asset_external_id"}]

        with pytest.raises(ValueError):
            import_labels_from_dict(
                self.kili, project_id, labels, label_type, overwrite, model_name
            )
