import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.adapters.kili_api_gateway.label.types import (
    AppendLabelData,
    AppendManyLabelsData,
)
from kili.domain.asset import AssetExternalId
from kili.domain.asset.asset import AssetId
from kili.domain.project import ProjectId
from kili.domain.user import UserId
from kili.exceptions import IncompatibleArgumentsError, NotFound
from kili.use_cases.asset.utils import AssetUseCasesUtils
from kili.use_cases.label import LabelUseCases
from kili.use_cases.label.types import LabelToCreateUseCaseInput

json_response = json.load(
    Path("./tests/unit/services/import_labels/fixtures/json_response_image.json").open()
)


def test_import_default_labels_with_asset_id(kili_api_gateway: KiliAPIGateway):
    # Given
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
            referenced_label_id=None,
        ),
        LabelToCreateUseCaseInput(
            asset_id=AssetId("asset_id_2"),
            json_response=json_response,
            asset_external_id=None,
            label_type=label_type,
            author_id=None,
            seconds_to_label=None,
            model_name=model_name,
            referenced_label_id=None,
        ),
    ]

    # When
    LabelUseCases(kili_api_gateway).append_labels(
        labels=labels,
        disable_tqdm=True,
        overwrite=overwrite,
        label_type=label_type,
        project_id=None,
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
                    referenced_label_id=None,
                ),
                AppendLabelData(
                    asset_id=AssetId("asset_id_2"),
                    author_id=None,
                    json_response=json_response,
                    model_name=None,
                    seconds_to_label=None,
                    client_version=None,
                    referenced_label_id=None,
                ),
            ],
        ),
        fields=("id",),
        project_id=None,
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
            referenced_label_id=None,
        ),
        LabelToCreateUseCaseInput(
            asset_id=None,
            json_response=json_response,
            asset_external_id=AssetExternalId("asset_external_id_2"),
            label_type=label_type,
            author_id=None,
            seconds_to_label=None,
            model_name=model_name,
            referenced_label_id=None,
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
                    referenced_label_id=None,
                ),
                AppendLabelData(
                    asset_id=AssetId("asset_id_2"),
                    author_id=None,
                    json_response=json_response,
                    model_name=None,
                    seconds_to_label=None,
                    client_version=None,
                    referenced_label_id=None,
                ),
            ],
        ),
        fields=("id",),
        project_id=ProjectId(project_id),
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
            referenced_label_id=None,
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
                    referenced_label_id=None,
                ),
            ],
        ),
        fields=("id",),
        project_id=ProjectId(project_id),
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
            referenced_label_id=None,
        ),
        LabelToCreateUseCaseInput(
            asset_id=None,
            json_response=json_response,
            asset_external_id=AssetExternalId("asset_external_id_2"),
            label_type=label_type,
            author_id=None,
            seconds_to_label=None,
            model_name=model_name,
            referenced_label_id=None,
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
                    referenced_label_id=None,
                ),
                AppendLabelData(
                    asset_id=AssetId("asset_id_2"),
                    author_id=None,
                    json_response=json_response,
                    model_name=model_name,
                    seconds_to_label=None,
                    client_version=None,
                    referenced_label_id=None,
                ),
            ],
        ),
        fields=("id",),
        project_id=ProjectId(project_id),
    )


def test_import_predictions_with_overwriting(kili_api_gateway: KiliAPIGateway):
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
            referenced_label_id=None,
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
                    referenced_label_id=None,
                ),
            ],
        ),
        fields=("id",),
        project_id=ProjectId(project_id),
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
            referenced_label_id=None,
        ),
    ]

    # When Then
    with pytest.raises(
        ValueError,
        match="You must provide `model_name` when uploading `PREDICTION` labels.",
    ):
        LabelUseCases(kili_api_gateway).append_labels(
            labels=labels,
            disable_tqdm=True,
            overwrite=overwrite,
            label_type=label_type,
            project_id=ProjectId(project_id),
            fields=("id",),
        )


def test_download_annotation_file_writes_the_bytes(kili_api_gateway: KiliAPIGateway, tmp_path):
    # Given a file annotation whose id resolves to a short lived url
    kili_api_gateway.get_annotation_file_url.return_value = "https://bucket.example.com/signed"
    response = MagicMock()
    response.__enter__.return_value = response
    response.iter_content.return_value = [b"ren", b"der"]
    kili_api_gateway.http_client.get.return_value = response
    output_path = tmp_path / "nested" / "render.mp4"

    # When
    written = LabelUseCases(kili_api_gateway).download_annotation_file(
        project_id=ProjectId("project_id"),
        asset_id=AssetId("asset_id"),
        asset_external_id=None,
        file_id="file_id",
        output_path=output_path,
    )

    # Then
    kili_api_gateway.get_annotation_file_url.assert_called_once_with(
        project_id="project_id", asset_id="asset_id", file_id="file_id"
    )
    assert written == str(output_path)
    assert output_path.read_bytes() == b"render"


def test_download_annotation_file_asks_for_the_url_each_time(
    kili_api_gateway: KiliAPIGateway, tmp_path
):
    """The url is signed on demand and short lived, so it must not be cached between downloads."""
    # Given
    kili_api_gateway.get_annotation_file_url.return_value = "https://bucket.example.com/signed"
    response = MagicMock()
    response.__enter__.return_value = response
    response.iter_content.return_value = [b"x"]
    kili_api_gateway.http_client.get.return_value = response

    # When
    for name in ("first.mp4", "second.mp4"):
        LabelUseCases(kili_api_gateway).download_annotation_file(
            project_id=ProjectId("project_id"),
            asset_id=AssetId("asset_id"),
            asset_external_id=None,
            file_id="file_id",
            output_path=tmp_path / name,
        )

    # Then
    assert kili_api_gateway.get_annotation_file_url.call_count == 2


def test_upload_annotation_file_returns_the_job_answer(kili_api_gateway: KiliAPIGateway, tmp_path):
    # Given
    kili_api_gateway.create_annotation_file_upload.return_value = {
        "fileId": "file_id",
        "uploadUrl": "https://bucket.example.com/put",
    }
    file_path = tmp_path / "render.mp4"
    file_path.write_bytes(b"render")

    # When
    answer = LabelUseCases(kili_api_gateway).upload_annotation_file(
        project_id=ProjectId("project_id"), asset_id=AssetId("asset_id"), file_path=file_path
    )

    # Then the answer is the whole of that job's jsonResponse
    assert answer == {
        "fileId": "file_id",
        "fileName": "render.mp4",
        "fileMimeType": "video/mp4",
    }
    kili_api_gateway.create_annotation_file_upload.assert_called_once_with(
        project_id="project_id", asset_id="asset_id"
    )
    _, kwargs = kili_api_gateway.http_client.put.call_args
    assert kwargs["headers"] == {"Content-Type": "video/mp4"}


def test_upload_annotation_file_leaves_an_unknown_type_to_the_server(
    kili_api_gateway: KiliAPIGateway, tmp_path
):
    """The server fills a missing mime type from the file name, so guessing badly here is worse."""
    # Given
    kili_api_gateway.create_annotation_file_upload.return_value = {
        "fileId": "file_id",
        "uploadUrl": "https://bucket.example.com/put",
    }
    file_path = tmp_path / "scene.blend"
    file_path.write_bytes(b"scene")

    # When
    answer = LabelUseCases(kili_api_gateway).upload_annotation_file(
        project_id=ProjectId("project_id"), asset_id=AssetId("asset_id"), file_path=file_path
    )

    # Then
    assert answer["fileMimeType"] == ""
    _, kwargs = kili_api_gateway.http_client.put.call_args
    assert kwargs["headers"] == {}


def test_upload_annotation_file_raises_when_the_bucket_refuses(
    kili_api_gateway: KiliAPIGateway, tmp_path
):
    # Given
    kili_api_gateway.create_annotation_file_upload.return_value = {
        "fileId": "file_id",
        "uploadUrl": "https://bucket.example.com/put",
    }
    kili_api_gateway.http_client.put.return_value.raise_for_status.side_effect = RuntimeError("403")
    file_path = tmp_path / "render.mp4"
    file_path.write_bytes(b"render")

    # When / Then a failed upload is not reported as a usable answer
    with pytest.raises(RuntimeError):
        LabelUseCases(kili_api_gateway).upload_annotation_file(
            project_id=ProjectId("project_id"), asset_id=AssetId("asset_id"), file_path=file_path
        )


def _upload_returns(kili_api_gateway: KiliAPIGateway, file_id: str = "file_id") -> None:
    kili_api_gateway.create_annotation_file_upload.return_value = {
        "fileId": file_id,
        "uploadUrl": "https://bucket.example.com/put",
    }


def test_append_labels_uploads_a_file_a_job_names_by_path(
    kili_api_gateway: KiliAPIGateway, tmp_path
):
    # Given a job answered with a path rather than a file reference
    _upload_returns(kili_api_gateway)
    render = tmp_path / "render.mp4"
    render.write_bytes(b"render")

    # When
    LabelUseCases(kili_api_gateway).append_labels(
        labels=[
            LabelToCreateUseCaseInput(
                asset_id=AssetId("asset_id"),
                json_response={"RENDER": str(render)},
                asset_external_id=None,
                author_id=None,
                label_type="DEFAULT",
                seconds_to_label=None,
                model_name=None,
                referenced_label_id=None,
            )
        ],
        label_type="DEFAULT",
        overwrite=False,
        project_id=ProjectId("project_id"),
        fields=("id",),
        disable_tqdm=True,
    )

    # Then the label carries the answer, not the path
    _, kwargs = kili_api_gateway.append_many_labels.call_args
    assert kwargs["data"].labels_data[0].json_response == {
        "RENDER": {"fileId": "file_id", "fileName": "render.mp4", "fileMimeType": "video/mp4"}
    }


def test_append_labels_uploads_a_file_under_asset_level(kili_api_gateway: KiliAPIGateway, tmp_path):
    """On video an asset level job sits under `assetLevel`, beside the frame keys."""
    # Given
    _upload_returns(kili_api_gateway)
    render = tmp_path / "render.mp4"
    render.write_bytes(b"render")

    # When
    LabelUseCases(kili_api_gateway).append_labels(
        labels=[
            LabelToCreateUseCaseInput(
                asset_id=AssetId("asset_id"),
                json_response={"0": {}, "assetLevel": {"RENDER": str(render)}},
                asset_external_id=None,
                author_id=None,
                label_type="DEFAULT",
                seconds_to_label=None,
                model_name=None,
                referenced_label_id=None,
            )
        ],
        label_type="DEFAULT",
        overwrite=False,
        project_id=ProjectId("project_id"),
        fields=("id",),
        disable_tqdm=True,
    )

    # Then the frame keys are untouched and the asset level job is resolved
    _, kwargs = kili_api_gateway.append_many_labels.call_args
    json_response = kwargs["data"].labels_data[0].json_response
    assert json_response["0"] == {}
    assert json_response["assetLevel"]["RENDER"]["fileId"] == "file_id"


def test_append_labels_leaves_an_already_uploaded_file_alone(
    kili_api_gateway: KiliAPIGateway,
):
    """A label read back from Kili carries the answer, and must be submittable again as is."""
    # Given
    answer = {"fileId": "file_id", "fileName": "render.mp4", "fileMimeType": "video/mp4"}

    # When
    LabelUseCases(kili_api_gateway).append_labels(
        labels=[
            LabelToCreateUseCaseInput(
                asset_id=AssetId("asset_id"),
                json_response={"RENDER": answer},
                asset_external_id=None,
                author_id=None,
                label_type="DEFAULT",
                seconds_to_label=None,
                model_name=None,
                referenced_label_id=None,
            )
        ],
        label_type="DEFAULT",
        overwrite=False,
        project_id=ProjectId("project_id"),
        fields=("id",),
        disable_tqdm=True,
    )

    # Then nothing was uploaded
    kili_api_gateway.create_annotation_file_upload.assert_not_called()
    _, kwargs = kili_api_gateway.append_many_labels.call_args
    assert kwargs["data"].labels_data[0].json_response == {"RENDER": answer}


def test_append_labels_asks_for_the_project_when_a_job_names_a_path(
    kili_api_gateway: KiliAPIGateway, tmp_path
):
    # Given no project id, which the upload needs
    render = tmp_path / "render.mp4"
    render.write_bytes(b"render")

    # When / Then
    with pytest.raises(ValueError, match="project_id"):
        LabelUseCases(kili_api_gateway).append_labels(
            labels=[
                LabelToCreateUseCaseInput(
                    asset_id=AssetId("asset_id"),
                    json_response={"RENDER": str(render)},
                    asset_external_id=None,
                    author_id=None,
                    label_type="DEFAULT",
                    seconds_to_label=None,
                    model_name=None,
                    referenced_label_id=None,
                )
            ],
            label_type="DEFAULT",
            overwrite=False,
            project_id=None,
            fields=("id",),
            disable_tqdm=True,
        )


def test_download_annotation_file_resolves_an_external_id(
    kili_api_gateway: KiliAPIGateway, tmp_path, mocker
):
    """A pipeline that names assets by external id should not have to resolve the id itself."""
    # Given
    mocker.patch.object(
        AssetUseCasesUtils, "get_asset_ids_or_throw_error", return_value=[AssetId("asset_id")]
    )
    kili_api_gateway.get_annotation_file_url.return_value = "https://bucket.example.com/signed"
    response = MagicMock()
    response.__enter__.return_value = response
    response.iter_content.return_value = [b"render"]
    kili_api_gateway.http_client.get.return_value = response

    # When
    LabelUseCases(kili_api_gateway).download_annotation_file(
        project_id=ProjectId("project_id"),
        asset_id=None,
        asset_external_id=AssetExternalId("my_asset"),
        file_id="file_id",
        output_path=tmp_path / "render.mp4",
    )

    # Then the resolved id is what addresses the file
    kili_api_gateway.get_annotation_file_url.assert_called_once_with(
        project_id="project_id", asset_id="asset_id", file_id="file_id"
    )


def test_download_annotation_file_refuses_both_identifiers(
    kili_api_gateway: KiliAPIGateway, tmp_path
):
    with pytest.raises(IncompatibleArgumentsError):
        LabelUseCases(kili_api_gateway).download_annotation_file(
            project_id=ProjectId("project_id"),
            asset_id=AssetId("asset_id"),
            asset_external_id=AssetExternalId("my_asset"),
            file_id="file_id",
            output_path=tmp_path / "render.mp4",
        )


def test_download_annotation_file_says_which_file_is_missing(
    kili_api_gateway: KiliAPIGateway, tmp_path
):
    """The bucket's own 404 names neither the file nor the asset, and carries the signed url."""
    # Given a file id that resolves to nothing, or belongs to another asset
    signed_url = "https://bucket.example.com/signed?X-Amz-Signature=secret"
    kili_api_gateway.get_annotation_file_url.return_value = signed_url
    response = MagicMock()
    response.__enter__.return_value = response
    response.status_code = 404
    kili_api_gateway.http_client.get.return_value = response

    # When / Then
    with pytest.raises(NotFound) as raised:
        LabelUseCases(kili_api_gateway).download_annotation_file(
            project_id=ProjectId("project_id"),
            asset_id=AssetId("asset_id"),
            asset_external_id=None,
            file_id="file_id",
            output_path=tmp_path / "render.mp4",
        )

    message = str(raised.value)
    assert "file_id" in message
    assert "asset_id" in message
    # A signed url is a credential, so it has no business in the caller's logs.
    assert "X-Amz-Signature" not in message
