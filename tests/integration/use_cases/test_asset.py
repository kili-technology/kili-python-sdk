from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.mixin import KiliAPIGateway
from kili.domain.asset import AssetFilters
from kili.domain.project import ProjectId
from kili.use_cases.asset import AssetUseCases
from kili.use_cases.asset.media_downloader import MediaDownloader
from kili.utils.labels.parsing import ParsedLabel


def test_given_query_parameters_I_can_query_assets(kili_api_gateway: KiliAPIGateway):
    # mocking
    nb_assets = 200
    assets = [{"id": "asset_id"}] * nb_assets
    kili_api_gateway.list_assets.return_value = assets

    # given parameters to query assets
    asset_use_cases = AssetUseCases(kili_api_gateway)
    filters = AssetFilters(project_id=ProjectId("project_id"))
    fields = ["id"]

    # when creating query assets
    asset_gen = asset_use_cases.list_assets(
        filters,
        fields,
        download_media=False,
        local_media_dir=None,
        label_output_format="dict",
        options=QueryOptions(disable_tqdm=False, first=None, skip=0),
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
    filters = AssetFilters(project_id=ProjectId("project_id"))
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

    # when creating query assets
    asset_gen = asset_use_cases.list_assets(
        filters,
        fields,
        download_media=False,
        local_media_dir=None,
        label_output_format="parsed_label",
        options=QueryOptions(first=None, skip=0, disable_tqdm=False),
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
    kili_api_gateway: KiliAPIGateway, mocker
):
    # mocking
    kili_api_gateway.get_project.return_value = {"inputType": "IMAGE", "dataConnections": None}
    media_downloader_mock = mocker.patch.object(MediaDownloader, "__init__", return_value=None)

    # given parameters to query assets
    asset_use_cases = AssetUseCases(kili_api_gateway)
    filters = AssetFilters(project_id=ProjectId("project_id"))
    fields = ["id", "content"]

    # when creating query assets
    asset_use_cases.list_assets(
        filters,
        fields,
        download_media=True,
        local_media_dir="temp_dir",
        label_output_format="dict",
        options=QueryOptions(first=None, skip=0, disable_tqdm=False),
    )

    # then
    media_downloader_mock.assert_called_once_with(
        "temp_dir",
        "project_id",
        False,
        "IMAGE",
        kili_api_gateway.http_client,
    )
