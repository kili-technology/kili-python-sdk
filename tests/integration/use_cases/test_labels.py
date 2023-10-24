import json
from pathlib import Path

import pytest

from kili.adapters.kili_api_gateway import KiliAPIGateway
from kili.adapters.kili_api_gateway.label.types import (
    AppendLabelData,
    AppendManyLabelsData,
)
from kili.domain.asset import AssetExternalId
from kili.domain.asset.asset import AssetId
from kili.domain.project import ProjectId
from kili.domain.user import UserId
from kili.use_cases.label import LabelUseCases
from kili.use_cases.label.types import LabelToCreateUseCaseInput

json_response = json.load(
    Path("./tests/unit/services/import_labels/fixtures/json_response_image.json").open()
)


def test_import_default_labels_with_asset_id(kili_api_gateway: KiliAPIGateway):
    # Given
    project_id = "project_id"
    label_type = "DEFAULT"
    overwrite = False
    model_name = None
    labels = [
        LabelToCreateUseCaseInput(
            asset_id=AssetId("asset_id_1"),
            json_response=json_response,
            asset_external_id=None,
            label_type=label_type,
            author_id=None,
            seconds_to_label=None,
            model_name=model_name,
        ),
        LabelToCreateUseCaseInput(
            asset_id=AssetId("asset_id_2"),
            json_response=json_response,
            asset_external_id=None,
            label_type=label_type,
            author_id=None,
            seconds_to_label=None,
            model_name=model_name,
        ),
    ]

    # When
    LabelUseCases(kili_api_gateway).append_labels(
        labels=labels,
        disable_tqdm=True,
        overwrite=overwrite,
        label_type=label_type,
        project_id=ProjectId(project_id),
        fields=("id",),
    )

    # Then
    kili_api_gateway.append_many_labels.assert_called_once_with(
        disable_tqdm=True,
        data=AppendManyLabelsData(
            label_type=label_type,
            overwrite=overwrite,
            labels_data=[
                AppendLabelData(
                    asset_id=AssetId("asset_id_1"),
                    author_id=None,
                    json_response=json_response,
                    model_name=None,
                    seconds_to_label=None,
                    client_version=None,
                    reviewed_label=None,
                ),
                AppendLabelData(
                    asset_id=AssetId("asset_id_2"),
                    author_id=None,
                    json_response=json_response,
                    model_name=None,
                    seconds_to_label=None,
                    client_version=None,
                    reviewed_label=None,
                ),
            ],
        ),
        fields=("id",),
    )


def test_import_default_labels_with_external_id(kili_api_gateway: KiliAPIGateway):
    kili_api_gateway.list_assets.return_value = (
        asset
        for asset in [
            {"id": "asset_id_1", "externalId": "asset_external_id_1"},
            {"id": "asset_id_2", "externalId": "asset_external_id_2"},
        ]
    )

    # Given
    project_id = "project_id"
    label_type = "DEFAULT"
    overwrite = False
    model_name = None
    labels = [
        LabelToCreateUseCaseInput(
            asset_id=None,
            json_response=json_response,
            asset_external_id=AssetExternalId("asset_external_id_1"),
            label_type=label_type,
            author_id=None,
            seconds_to_label=None,
            model_name=model_name,
        ),
        LabelToCreateUseCaseInput(
            asset_id=None,
            json_response=json_response,
            asset_external_id=AssetExternalId("asset_external_id_2"),
            label_type=label_type,
            author_id=None,
            seconds_to_label=None,
            model_name=model_name,
        ),
    ]

    # When
    LabelUseCases(kili_api_gateway).append_labels(
        labels=labels,
        disable_tqdm=True,
        overwrite=overwrite,
        label_type=label_type,
        project_id=ProjectId(project_id),
        fields=("id",),
    )

    # Then
    kili_api_gateway.append_many_labels.assert_called_once_with(
        disable_tqdm=True,
        data=AppendManyLabelsData(
            label_type=label_type,
            overwrite=overwrite,
            labels_data=[
                AppendLabelData(
                    asset_id=AssetId("asset_id_1"),
                    author_id=None,
                    json_response=json_response,
                    model_name=None,
                    seconds_to_label=None,
                    client_version=None,
                    reviewed_label=None,
                ),
                AppendLabelData(
                    asset_id=AssetId("asset_id_2"),
                    author_id=None,
                    json_response=json_response,
                    model_name=None,
                    seconds_to_label=None,
                    client_version=None,
                    reviewed_label=None,
                ),
            ],
        ),
        fields=("id",),
    )


def test_import_labels_with_optional_params(kili_api_gateway: KiliAPIGateway):
    # Given
    project_id = "project_id"
    label_type = "DEFAULT"
    model_name = None
    overwrite = False
    author_id = UserId("author_id")
    seconds_to_label = 3
    labels = [
        LabelToCreateUseCaseInput(
            asset_id=AssetId("asset_id"),
            json_response=json_response,
            asset_external_id=None,
            label_type=label_type,
            author_id=author_id,
            seconds_to_label=seconds_to_label,
            model_name=model_name,
        ),
    ]

    # When
    LabelUseCases(kili_api_gateway).append_labels(
        labels=labels,
        disable_tqdm=True,
        overwrite=overwrite,
        label_type=label_type,
        project_id=ProjectId(project_id),
        fields=("id",),
    )

    # Then
    kili_api_gateway.append_many_labels.assert_called_once_with(
        disable_tqdm=True,
        data=AppendManyLabelsData(
            label_type=label_type,
            overwrite=overwrite,
            labels_data=[
                AppendLabelData(
                    asset_id=AssetId("asset_id"),
                    author_id=author_id,
                    json_response=json_response,
                    model_name=None,
                    seconds_to_label=seconds_to_label,
                    client_version=None,
                    reviewed_label=None,
                ),
            ],
        ),
        fields=("id",),
    )


def test_import_predictions(kili_api_gateway: KiliAPIGateway):
    kili_api_gateway.list_assets.return_value = (
        asset
        for asset in [
            {"id": "asset_id_1", "externalId": "asset_external_id_1"},
            {"id": "asset_id_2", "externalId": "asset_external_id_2"},
        ]
    )

    # Given
    project_id = "project_id"
    label_type = "PREDICTION"
    model_name = "model_name"
    overwrite = False
    labels = [
        LabelToCreateUseCaseInput(
            asset_id=None,
            json_response=json_response,
            asset_external_id=AssetExternalId("asset_external_id_1"),
            label_type=label_type,
            author_id=None,
            seconds_to_label=None,
            model_name=model_name,
        ),
        LabelToCreateUseCaseInput(
            asset_id=None,
            json_response=json_response,
            asset_external_id=AssetExternalId("asset_external_id_2"),
            label_type=label_type,
            author_id=None,
            seconds_to_label=None,
            model_name=model_name,
        ),
    ]

    # When
    LabelUseCases(kili_api_gateway).append_labels(
        labels=labels,
        disable_tqdm=True,
        overwrite=overwrite,
        label_type=label_type,
        project_id=ProjectId(project_id),
        fields=("id",),
    )

    # Then
    kili_api_gateway.append_many_labels.assert_called_once_with(
        disable_tqdm=True,
        data=AppendManyLabelsData(
            label_type=label_type,
            overwrite=overwrite,
            labels_data=[
                AppendLabelData(
                    asset_id=AssetId("asset_id_1"),
                    author_id=None,
                    json_response=json_response,
                    model_name=model_name,
                    seconds_to_label=None,
                    client_version=None,
                    reviewed_label=None,
                ),
                AppendLabelData(
                    asset_id=AssetId("asset_id_2"),
                    author_id=None,
                    json_response=json_response,
                    model_name=model_name,
                    seconds_to_label=None,
                    client_version=None,
                    reviewed_label=None,
                ),
            ],
        ),
        fields=("id",),
    )


def test_import_predictions_with_overwritting(kili_api_gateway: KiliAPIGateway):
    kili_api_gateway.list_assets.return_value = (
        asset
        for asset in [
            {"id": "asset_id_1", "externalId": "asset_external_id_1"},
            {"id": "asset_id_2", "externalId": "asset_external_id_2"},
        ]
    )

    # Given
    project_id = "project_id"
    label_type = "PREDICTION"
    model_name = "model_name"
    overwrite = True
    labels = [
        LabelToCreateUseCaseInput(
            asset_id=None,
            json_response=json_response,
            asset_external_id=AssetExternalId("asset_external_id_1"),
            label_type=label_type,
            author_id=None,
            seconds_to_label=None,
            model_name=model_name,
        ),
    ]

    # When
    LabelUseCases(kili_api_gateway).append_labels(
        labels=labels,
        disable_tqdm=True,
        overwrite=overwrite,
        label_type=label_type,
        project_id=ProjectId(project_id),
        fields=("id",),
    )

    # Then
    kili_api_gateway.append_many_labels.assert_called_once_with(
        disable_tqdm=True,
        data=AppendManyLabelsData(
            label_type=label_type,
            overwrite=overwrite,
            labels_data=[
                AppendLabelData(
                    asset_id=AssetId("asset_id_1"),
                    author_id=None,
                    json_response=json_response,
                    model_name=model_name,
                    seconds_to_label=None,
                    client_version=None,
                    reviewed_label=None,
                ),
            ],
        ),
        fields=("id",),
    )


def test_import_predictions_without_giving_model_name(kili_api_gateway: KiliAPIGateway):
    # Given
    project_id = "project_id"
    label_type = "PREDICTION"
    model_name = None
    overwrite = False
    labels = [
        LabelToCreateUseCaseInput(
            asset_id=AssetId("asset_id"),
            json_response=json_response,
            asset_external_id=None,
            label_type=label_type,
            author_id=None,
            seconds_to_label=None,
            model_name=model_name,
        ),
    ]

    # When Then
    with pytest.raises(
        ValueError, match="You must provide `model_name` when uploading `PREDICTION` labels."
    ):
        LabelUseCases(kili_api_gateway).append_labels(
            labels=labels,
            disable_tqdm=True,
            overwrite=overwrite,
            label_type=label_type,
            project_id=ProjectId(project_id),
            fields=("id",),
        )
