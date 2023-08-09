import os
import tempfile

import pytest
import pytest_mock

from kili.client import Kili
from kili.entrypoints.mutations.asset import MutationsAsset
from kili.services.asset_import_csv import get_text_assets_from_csv


@pytest.fixture
def csv_file_path():
    csv_content = """asset_content_column,category_column,external_id_column
asset_content_1,category_1,external_id_1
asset_content_2,category_2,external_id_2
"""
    with tempfile.TemporaryDirectory() as tmpdirname:
        with open(os.path.join(tmpdirname, "test.csv"), "w", encoding="utf-8") as file:
            file.write(csv_content)

        yield os.path.join(tmpdirname, "test.csv")


def test_get_text_assets_from_csv(csv_file_path: str):
    content_array, external_id_array = get_text_assets_from_csv(
        from_csv=csv_file_path,
        csv_content_column="asset_content_column",
        external_id_array=None,
        csv_external_id_column=None,
        csv_separator=",",
    )

    assert content_array == ["asset_content_1", "asset_content_2"]
    assert external_id_array == ["1", "2"]


def test_get_text_assets_from_csv_with_external_id(csv_file_path: str):
    content_array, external_id_array = get_text_assets_from_csv(
        from_csv=csv_file_path,
        csv_content_column="asset_content_column",
        external_id_array=None,
        csv_external_id_column="external_id_column",
        csv_separator=",",
    )

    assert content_array == ["asset_content_1", "asset_content_2"]
    assert external_id_array == ["external_id_1", "external_id_2"]


def test_append_many_to_dataset_from_csv(csv_file_path: str, mocker: pytest_mock.MockerFixture):
    kili: Kili = MutationsAsset()  # type: ignore
    kili.graphql_client = mocker.MagicMock()
    mocker_import_assets = mocker.patch("kili.entrypoints.mutations.asset.import_assets")

    kili.append_many_to_dataset(
        project_id="fake_proj_id",
        content_array=None,
        external_id_array=None,
        from_csv=csv_file_path,
        csv_content_column="asset_content_column",
        csv_external_id_column=None,
    )

    assets = [
        {"content": "asset_content_1", "external_id": "1"},
        {"content": "asset_content_2", "external_id": "2"},
    ]
    mocker_import_assets.assert_called_once_with(
        kili, project_id="fake_proj_id", assets=assets, disable_tqdm=False, verify=True
    )
