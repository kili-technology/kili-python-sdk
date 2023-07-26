import os

import pytest
import pytest_mock

from kili.client import Kili
from kili.entrypoints.mutations.project import MutationsProject
from kili.entrypoints.mutations.project.import_csv import (
    _create_project,
    _get_json_response_array,
    _read_csv,
)


@pytest.fixture
def csv_file_path():
    csv_content = """asset_content_column,category_column,external_id_column
asset_content_1,category_1,external_id_1
asset_content_2,category_2,external_id_2
"""

    with open("test.csv", "w", encoding="utf-8") as file:
        file.write(csv_content)

    yield "test.csv"

    os.remove("test.csv")


def test__read_csv_assets_only(csv_file_path: str):
    content_array, categories_array, external_id_array = _read_csv(
        csv_file=csv_file_path,
        content_column="asset_content_column",
        category_column=None,
        external_id_column=None,
        csv_separator=",",
    )

    assert content_array == ["asset_content_1", "asset_content_2"]
    assert categories_array is None
    assert external_id_array == ["1", "2"]


def test__read_csv_with_labels(csv_file_path: str):
    content_array, categories_array, external_id_array = _read_csv(
        csv_file=csv_file_path,
        content_column="asset_content_column",
        category_column="category_column",
        external_id_column=None,
        csv_separator=",",
    )

    assert content_array == ["asset_content_1", "asset_content_2"]
    assert categories_array == ["category_1", "category_2"]
    assert external_id_array == ["1", "2"]


def test__read_csv_with_external_id(csv_file_path: str):
    content_array, categories_array, external_id_array = _read_csv(
        csv_file=csv_file_path,
        content_column="asset_content_column",
        category_column="category_column",
        external_id_column="external_id_column",
        csv_separator=",",
    )

    assert content_array == ["asset_content_1", "asset_content_2"]
    assert categories_array == ["category_1", "category_2"]
    assert external_id_array == ["external_id_1", "external_id_2"]


def test__create_project(mocker: pytest_mock.MockerFixture):
    kili = mocker.MagicMock()
    kili.create_project.return_value = {"id": "fake_project_id"}
    project_id = _create_project(kili, "title", "description", ["category_1", "category_2"])

    assert project_id == "fake_project_id"
    assert kili.create_project.called_once_with(
        input_type="TEXT",
        json_interface={
            "jobs": {
                "CLASSIFICATION_JOB": {
                    "content": {
                        "categories": {
                            "category_1": {"children": [], "name": "category_1"},
                            "category_2": {"children": [], "name": "category_2"},
                        },
                        "input": "radio",
                    },
                    "instruction": "Classification job",
                    "mlTask": "CLASSIFICATION",
                    "required": 0,
                    "isChild": False,
                }
            }
        },
        title="title",
        description="description",
    )


def test__get_json_response_array():
    json_resp_array = _get_json_response_array(["category_1", "category_2", "category_1"])
    assert json_resp_array == [
        {"CLASSIFICATION_JOB": {"categories": [{"name": "category_1"}]}},
        {"CLASSIFICATION_JOB": {"categories": [{"name": "category_2"}]}},
        {"CLASSIFICATION_JOB": {"categories": [{"name": "category_1"}]}},
    ]


def test_kili_import_csv_new_project(csv_file_path: str, mocker: pytest_mock.MockerFixture):
    kili: Kili = MutationsProject()  # type: ignore
    kili.graphql_client = mocker.MagicMock()
    kili.create_project = mocker.MagicMock(return_value={"id": "fake_project_id"})
    kili.append_many_to_dataset = mocker.MagicMock()
    kili.append_labels = mocker.MagicMock()

    kili.import_csv(
        csv_file=csv_file_path,
        content_column="asset_content_column",
        unique_categories=["category_1", "category_2", "category_3"],
        category_column="category_column",
        external_id_column="external_id_column",
        project_title="title",
        project_description="description",
    )

    assert sorted(
        list(
            kili.create_project.call_args_list[0]
            .kwargs["json_interface"]["jobs"]["CLASSIFICATION_JOB"]["content"]["categories"]
            .keys()
        )
    ) == ["category_1", "category_2", "category_3"]

    kili.append_many_to_dataset.assert_called_once_with(
        project_id="fake_project_id",
        content_array=["asset_content_1", "asset_content_2"],
        external_id_array=["external_id_1", "external_id_2"],
        wait_until_availability=True,
    )

    kili.append_labels.assert_called_once_with(
        json_response_array=[
            {"CLASSIFICATION_JOB": {"categories": [{"name": "category_1"}]}},
            {"CLASSIFICATION_JOB": {"categories": [{"name": "category_2"}]}},
        ],
        project_id="fake_project_id",
        asset_external_id_array=["external_id_1", "external_id_2"],
        label_type="DEFAULT",
    )


def test_kili_import_csv_existing_project(csv_file_path: str, mocker: pytest_mock.MockerFixture):
    kili: Kili = MutationsProject()  # type: ignore
    kili.graphql_client = mocker.MagicMock()
    kili.create_project = mocker.MagicMock(return_value={"id": "fake_project_id"})
    kili.append_many_to_dataset = mocker.MagicMock()
    kili.append_labels = mocker.MagicMock()

    kili.import_csv(
        csv_file=csv_file_path,
        content_column="asset_content_column",
        category_column="category_column",
        external_id_column="external_id_column",
        project_id="fake_project_id",
    )

    kili.create_project.assert_not_called()

    kili.append_many_to_dataset.assert_called_once_with(
        project_id="fake_project_id",
        content_array=["asset_content_1", "asset_content_2"],
        external_id_array=["external_id_1", "external_id_2"],
        wait_until_availability=True,
    )

    kili.append_labels.assert_called_once_with(
        json_response_array=[
            {"CLASSIFICATION_JOB": {"categories": [{"name": "category_1"}]}},
            {"CLASSIFICATION_JOB": {"categories": [{"name": "category_2"}]}},
        ],
        project_id="fake_project_id",
        asset_external_id_array=["external_id_1", "external_id_2"],
        label_type="DEFAULT",
    )


def test_kili_import_csv_unique_columns(csv_file_path: str, mocker: pytest_mock.MockerFixture):
    kili: Kili = MutationsProject()  # type: ignore
    kili.graphql_client = mocker.MagicMock()
    kili.create_project = mocker.MagicMock(return_value={"id": "fake_project_id"})
    kili.append_many_to_dataset = mocker.MagicMock()
    kili.append_labels = mocker.MagicMock()

    kili.import_csv(
        csv_file=csv_file_path,
        content_column="asset_content_column",
        category_column="category_column",
        external_id_column="external_id_column",
        project_id="fake_project_id",
    )

    kili.create_project.assert_not_called()

    kili.append_many_to_dataset.assert_called_once_with(
        project_id="fake_project_id",
        content_array=["asset_content_1", "asset_content_2"],
        external_id_array=["external_id_1", "external_id_2"],
        wait_until_availability=True,
    )

    kili.append_labels.assert_called_once_with(
        json_response_array=[
            {"CLASSIFICATION_JOB": {"categories": [{"name": "category_1"}]}},
            {"CLASSIFICATION_JOB": {"categories": [{"name": "category_2"}]}},
        ],
        project_id="fake_project_id",
        asset_external_id_array=["external_id_1", "external_id_2"],
        label_type="DEFAULT",
    )
