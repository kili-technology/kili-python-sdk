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
    json_response = {"JOB_0": {"categories": [{"name": "CATGORY_A"}]}}
    asset = {
        "id": "asset_id",
        "labels": [{"jsonResponse": json_response}],
        "latestLabel": {"jsonResponse": json_response},
    }
    json_interface = {
        "jobs": {
            "JOB_0": {
                "mlTask": "CLASSIFICATION",
                "isChild": False,
                "content": {
                    "categories": {
                        "CATGORY_A": {"children": [], "name": "category A", "id": "category30"},
                    },
                    "input": "checkbox",
                },
            }
        }
    }
    kili_api_gateway.list_assets.return_value = (asset for asset in [asset])
    kili_api_gateway.get_project.return_value = {
        "jsonInterface": json_interface,
        "inputType": "TEXT",
    }

    # given parameters to query assets
    asset_use_cases = AssetUseCases(kili_api_gateway)
    where = AssetWhere(project_id="project_id")
    fields = ["id", "label.jsonResponse", "latestLabel.jsonresponse"]
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
    returned_asset = list(asset_gen)[0]

    # then
    assert returned_asset == asset
    assert isinstance(returned_asset["latestLabel"], ParsedLabel)
    assert isinstance(returned_asset["labels"][0], ParsedLabel)


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
