import json
from unittest.mock import MagicMock, patch

import pydantic
import pytest

from kili import services
from kili.core.graphql.operations.asset.queries import AssetQuery
from kili.core.graphql.operations.label.mutations import GQL_APPEND_MANY_LABELS


def mocked_AssetQuery(*_):
    return [
        {"id": "asset_id_1", "externalId": "asset_external_id_1"},
        {"id": "asset_id_2", "externalId": "asset_external_id_2"},
    ]


class TestImportLabelsFromDict:
    """Test class for import_label_from_dict_service."""

    def setup_class(self):
        self.kili = MagicMock()
        self.kili.auth.client.execute = MagicMock()
        with open("./tests/services/import_labels/fixtures/json_response_image.json") as json_file:
            self.json_response = json.load(json_file)

    def test_import_default_labels_with_asset_id(self):
        project_id = "project_id"
        label_type = "DEFAULT"
        model_name = None
        labels = [
            {"json_response": self.json_response, "asset_id": "asset_id_1"},
            {"json_response": self.json_response, "asset_id": "asset_id_2"},
        ]

        call = {
            "data": {
                "labelType": "DEFAULT",
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

        services.import_labels_from_dict(self.kili.auth, project_id, labels, label_type, model_name)
        self.kili.auth.client.execute.assert_called_with(GQL_APPEND_MANY_LABELS, call)

    @patch.object(AssetQuery, "__call__", side_effect=mocked_AssetQuery)
    def test_import_default_labels_with_external_id(self, mocker):
        project_id = "project_id"
        label_type = "DEFAULT"
        model_name = None
        labels = [
            {"json_response": self.json_response, "asset_external_id": "asset_external_id_1"},
            {"json_response": self.json_response, "asset_external_id": "asset_external_id_2"},
        ]

        call = {
            "data": {
                "labelType": "DEFAULT",
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

        services.import_labels_from_dict(self.kili.auth, project_id, labels, label_type, model_name)
        self.kili.auth.client.execute.assert_called_with(GQL_APPEND_MANY_LABELS, call)

    def test_import_labels_with_optional_params(self):
        project_id = "project_id"
        label_type = "DEFAULT"
        model_name = None
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

        services.import_labels_from_dict(self.kili.auth, project_id, labels, label_type, model_name)
        self.kili.auth.client.execute.assert_called_with(GQL_APPEND_MANY_LABELS, call)

    def test_return_error_when_give_unexisting_label_field(self):
        project_id = "project_id"
        label_type = "DEFAULT"
        model_name = None
        labels = [
            {"json_response": self.json_response, "asset_id": "asset_id", "unexisting_field": 3}
        ]
        with pytest.raises(pydantic.ValidationError):
            services.import_labels_from_dict(
                self.kili.auth, project_id, labels, label_type, model_name
            )

    def test_return_error_when_give_wrong_field_type(self):
        project_id = "project_id"
        label_type = "DEFAULT"
        model_name = None
        labels = [
            {
                "json_response": self.json_response,
                "asset_id": "asset_id",
                "seconds_to_label": "wrong_type",
            }
        ]
        with pytest.raises(pydantic.ValidationError):
            services.import_labels_from_dict(
                self.kili.auth, project_id, labels, label_type, model_name
            )

    @patch.object(
        AssetQuery,
        "__call__",
        side_effect=mocked_AssetQuery,
    )
    def test_import_predictions(self, mocker):
        project_id = "project_id"
        label_type = "PREDICTION"
        model_name = "model_name"
        labels = [
            {"json_response": self.json_response, "asset_external_id": "asset_external_id_1"},
            {"json_response": self.json_response, "asset_external_id": "asset_external_id_2"},
        ]

        call = {
            "data": {
                "labelType": "PREDICTION",
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

        services.import_labels_from_dict(self.kili.auth, project_id, labels, label_type, model_name)
        self.kili.auth.client.execute.assert_called_with(GQL_APPEND_MANY_LABELS, call)

    def test_import_predictions_without_giving_model_name(self):
        self.kili.assets = MagicMock(
            return_value=[{"id": "asset_id", "externalId": "asset_external_id"}]
        )
        project_id = "project_id"
        label_type = "PREDICTION"
        model_name = None
        labels = [{"json_response": self.json_response, "asset_external_id": "asset_external_id"}]

        with pytest.raises(ValueError):
            services.import_labels_from_dict(
                self.kili.auth, project_id, labels, label_type, model_name
            )
