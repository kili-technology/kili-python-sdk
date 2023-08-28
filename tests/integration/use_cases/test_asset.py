from pathlib import Path
from tempfile import TemporaryDirectory

from kili.gateways.kili_api_gateway import KiliAPIGateway
from kili.gateways.kili_api_gateway.asset.types import AssetWhere
from kili.gateways.kili_api_gateway.queries import QueryOptions
from kili.use_cases.asset import AssetUseCases
from kili.utils.labels.parsing import ParsedLabel


def test_given_query_parameters_I_can_query_assets(kili_api_gateway: KiliAPIGateway):
    # mocking
    nb_assets = 200
    assets = [{"id": "asset_id"}] * nb_assets
    kili_api_gateway.list_assets.return_value = assets

    # given parameters to query assets
    asset_use_cases = AssetUseCases(kili_api_gateway)
    where = AssetWhere(project_id="project_id")
    fields = ["id"]
    options = QueryOptions(disable_tqdm=False)

    # when creating query assets
    asset_gen = asset_use_cases.list_assets(
        where,
        fields,
        options,
        download_media=False,
        local_media_dir=None,
        label_output_format="dict",
    )

    # then
    assert list(asset_gen) == assets


def test_given_query_parameters_I_can_query_assets_and_get_their_labels_parsed(
    kili_api_gateway: KiliAPIGateway,
):
    # mocking
    label = {
        "author": {
            "id": "cldbnzmmq00go0jwc20fq1jkl",
            "email": "john.doe@kili-technology.com",
        },
        "createdAt": "2023-05-11T16:01:48.093Z",
        "id": "clhjbhrul015m0k7hct21drz4",
        "jsonResponse": {"JOB_0": {"text": "some text abc"}},
    }
    asset = {
        "labels": [label],
        "latestLabel": label,
        "content": "https://storage.googleapis.com/label-backend-staging/",
        "createdAt": "2023-05-11T15:55:01.134Z",
        "externalId": "4bad2303e43bfefa0169d890c68f5c9d--cherry-blossom-tree-blossom-trees.jpg",
        "id": "asset_id",
        "isHoneypot": False,
        "jsonMetadata": {},
        "skipped": False,
        "status": "LABELED",
    }
    json_interface = {
        "jobs": {"JOB_0": {"mlTask": "TRANSCRIPTION", "required": 1, "isChild": False}}
    }
    kili_api_gateway.list_assets.return_value = (asset for asset in [asset])
    kili_api_gateway.get_project.return_value = {
        "jsonInterface": json_interface,
        "inputType": "TEXT",
    }

    # given parameters to query assets
    asset_use_cases = AssetUseCases(kili_api_gateway)
    where = AssetWhere(project_id="project_id")
    fields = [
        "content",
        "createdAt",
        "externalId",
        "id",
        "isHoneypot",
        "jsonMetadata",
        "labels.author.id",
        "labels.author.email",
        "labels.createdAt",
        "labels.id",
        "labels.jsonResponse",
        "skipped",
        "status",
        "latestLabel.jsonResponse",
    ]
    options = QueryOptions(disable_tqdm=False)

    # when creating query assets
    asset_gen = asset_use_cases.list_assets(
        where,
        fields,
        options,
        download_media=False,
        local_media_dir=None,
        label_output_format="parsed_label",
    )

    # then
    returned_assets = list(asset_gen)
    assert len(returned_assets) == 1
    returned_asset = returned_assets[0]
    assert returned_asset == asset
    assert isinstance(returned_asset["latestLabel"], ParsedLabel)
    assert returned_asset["latestLabel"].jobs["JOB_0"].text == "some text abc"
    assert isinstance(returned_asset["labels"][0], ParsedLabel)
    assert returned_asset["labels"][0].jobs["JOB_0"].text == "some text abc"


def test_given_query_parameters_I_can_query_assets_and_download_their_media(
    kili_api_gateway: KiliAPIGateway,
):
    # mocking
    asset = {
        "id": "asset_id",
        "content": "http://test.jpg",
        "externalId": "external_id.jpg",
    }
    kili_api_gateway.list_assets.return_value = (asset for asset in [asset])

    # given parameters to query assets
    asset_use_cases = AssetUseCases(kili_api_gateway)
    where = AssetWhere(project_id="project_id")
    fields = ["id", "content"]
    options = QueryOptions(disable_tqdm=False)

    # when creating query assets
    with TemporaryDirectory() as tmp_dir:
        asset_gen = asset_use_cases.list_assets(
            where,
            fields,
            options,
            download_media=True,
            local_media_dir=tmp_dir,
            label_output_format="dict",
        )
        returned_asset = list(asset_gen)[0]

        # then
        expected_file_path = Path(tmp_dir) / "external_id.jpg"
        assert returned_asset == {
            "id": "asset_id",
            "content": str(expected_file_path),
        }
        assert expected_file_path.is_file()
