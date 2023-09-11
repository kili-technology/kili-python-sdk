import os
import tempfile
from typing import TYPE_CHECKING

import pytest
import pytest_mock

from kili.entrypoints.mutations.asset import MutationsAsset
from kili.services.asset_import_csv import get_text_assets_from_csv

if TYPE_CHECKING:
    from kili.client import Kili


@pytest.fixture()
def csv_file_path():
    csv_content = """content,category_column,externalId
asset_content_1,category_1,external_id_1
asset_content_2,category_2,external_id_2
"""
    with tempfile.TemporaryDirectory() as tmpdirname:
        with open(os.path.join(tmpdirname, "test.csv"), "w", encoding="utf-8") as file:
            file.write(csv_content)

        yield os.path.join(tmpdirname, "test.csv")


def test_get_text_assets_from_csv_with_external_id(csv_file_path: str):
    content_array, external_id_array = get_text_assets_from_csv(
        from_csv=csv_file_path,
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
    )

    assets = [
        {"content": "asset_content_1", "external_id": "external_id_1"},
        {"content": "asset_content_2", "external_id": "external_id_2"},
    ]
    mocker_import_assets.assert_called_once_with(
        kili, project_id="fake_proj_id", assets=assets, disable_tqdm=None, verify=True
    )
