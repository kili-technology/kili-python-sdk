"""Tests the Kili CLI."""

import csv
import os
from pathlib import Path
from typing import List
from unittest.mock import ANY, MagicMock, patch

import pytest
import pytest_mock
import requests
from click.testing import CliRunner

from kili.core.graphql.operations.asset.queries import AssetQuery
from kili.core.graphql.operations.project.queries import ProjectQuery
from kili.entrypoints.cli.project.create import create_project
from kili.entrypoints.cli.project.describe import describe_project
from kili.entrypoints.cli.project.export import export_labels
from kili.entrypoints.cli.project.import_ import import_assets
from kili.entrypoints.cli.project.list_ import list_projects
from tests.integration.entrypoints.cli.helpers import debug_subprocess_pytest

from .mocks.assets import mocked__project_assets
from .mocks.projects import mocked__ProjectQuery

kili_client = MagicMock()
kili_client.api_endpoint = "https://staging.cloud.kili-technology.com/api/label/v2/graphql"
kili_client.create_project = create_project_mock = MagicMock()
kili_client.http_client = requests.Session()


def test_list(mocker: pytest_mock.MockerFixture):
    mocker.patch.object(ProjectQuery, "__call__", side_effect=mocked__ProjectQuery)

    runner = CliRunner()
    result = runner.invoke(list_projects)
    assert (
        (result.exit_code == 0)
        and (result.output.count("100.0%") == 1)
        and (result.output.count("0.0%") == 2)
        and (result.output.count("nan") == 1)
    )


def test_create_project(*_):
    runner = CliRunner()
    runner.invoke(
        create_project,
        [
            "--interface",
            "tests/integration/entrypoints/cli/project/fixtures/image_interface.json",
            "--title",
            "Test project",
            "--description",
            "description",
            "--input-type",
            "IMAGE",
        ],
    )


def test_describe_project(mocker: pytest_mock.MockerFixture):
    mocker.patch.object(ProjectQuery, "__call__", side_effect=mocked__ProjectQuery)

    runner = CliRunner()
    result = runner.invoke(describe_project, ["project_id"])
    debug_subprocess_pytest(result)
    assert (
        (result.output.count("40.8%") == 1)
        and (result.output.count("N/A") == 2)
        and (result.output.count("Number of remaining assets") == 1)
        and (result.output.count("project title") == 1)
    )


@pytest.mark.parametrize(
    "case_name,files,options,flags,expected_service_payload",
    [
        (
            "AAU, when I import a list of file to an image project, I see a success",
            [
                str(Path("test_tree") / "image1.png"),
                str(Path("test_tree") / "leaf" / "image3.png"),
            ],
            {
                "project-id": "image_project",
            },
            None,
            (
                ANY,
                "image_project",
                [
                    {
                        "content": str(Path("test_tree") / "image1.png"),
                        "external_id": "image1",
                    },
                    {
                        "content": str(Path("test_tree") / "leaf" / "image3.png"),
                        "external_id": "image3",
                    },
                ],
                ANY,
            ),
        ),
        (
            "AAU, when I import files with stars, I see a success",
            [
                str(Path("test_tree") / "**.jpg"),
                str(Path("test_tree") / "leaf" / "**.jpg"),
            ],
            {
                "project-id": "image_project",
            },
            None,
            (
                ANY,
                "image_project",
                [
                    {
                        "content": str(Path("test_tree") / "image2.jpg"),
                        "external_id": "image2",
                    },
                    {
                        "content": str(Path("test_tree") / "leaf" / "image4.jpg"),
                        "external_id": "image4",
                    },
                ],
                ANY,
            ),
        ),
        (
            "AAU, when I import a files to a text project, I see a success",
            [str(Path("test_tree/")), str(Path("test_tree") / "leaf")],
            {"project-id": "text_project"},
            None,
            (
                ANY,
                "text_project",
                [
                    {"content": str(Path("test_tree") / "image1.png"), "external_id": "image1"},
                    {"content": str(Path("test_tree") / "image2.jpg"), "external_id": "image2"},
                    {
                        "content": str(Path("test_tree") / "leaf" / "image3.png"),
                        "external_id": "image3",
                    },
                    {
                        "content": str(Path("test_tree") / "leaf" / "image4.jpg"),
                        "external_id": "image4",
                    },
                    {
                        "content": str(Path("test_tree") / "leaf" / "texte2.txt"),
                        "external_id": "texte2",
                    },
                    {"content": str(Path("test_tree") / "texte1.txt"), "external_id": "texte1"},
                    {"content": str(Path("test_tree") / "video1.mp4"), "external_id": "video1"},
                    {"content": str(Path("test_tree") / "video2.mp4"), "external_id": "video2"},
                ],
                ANY,
            ),
        ),
        (
            "AAU, when I import a files to a text project, I see a success",
            [str(Path("test_tree/")), str(Path("test_tree") / "leaf")],
            {"project-id": "text_project"},
            None,
            (
                ANY,
                "text_project",
                [
                    {"content": str(Path("test_tree") / "image1.png"), "external_id": "image1"},
                    {"content": str(Path("test_tree") / "image2.jpg"), "external_id": "image2"},
                    {
                        "content": str(Path("test_tree") / "leaf" / "image3.png"),
                        "external_id": "image3",
                    },
                    {
                        "content": str(Path("test_tree") / "leaf" / "image4.jpg"),
                        "external_id": "image4",
                    },
                    {
                        "content": str(Path("test_tree") / "leaf" / "texte2.txt"),
                        "external_id": "texte2",
                    },
                    {"content": str(Path("test_tree") / "texte1.txt"), "external_id": "texte1"},
                    {"content": str(Path("test_tree") / "video1.mp4"), "external_id": "video1"},
                    {"content": str(Path("test_tree") / "video2.mp4"), "external_id": "video2"},
                ],
                ANY,
            ),
        ),
        (
            (
                "AAU, when I import videos to a video project, as native by changing the fps, I"
                " see a success"
            ),
            [str(Path("test_tree/"))],
            {
                "project-id": "frame_project",
                "fps": "10",
            },
            None,
            (
                ANY,
                "frame_project",
                [
                    {
                        "content": str(Path("test_tree") / "image1.png"),
                        "external_id": "image1",
                        "json_metadata": {
                            "processingParameters": {
                                "shouldKeepNativeFrameRate": False,
                                "framesPlayedPerSecond": 10,
                                "shouldUseNativeVideo": True,
                            }
                        },
                    },
                    {
                        "content": str(Path("test_tree") / "image2.jpg"),
                        "external_id": "image2",
                        "json_metadata": {
                            "processingParameters": {
                                "shouldKeepNativeFrameRate": False,
                                "framesPlayedPerSecond": 10,
                                "shouldUseNativeVideo": True,
                            }
                        },
                    },
                    {
                        "content": str(Path("test_tree") / "texte1.txt"),
                        "external_id": "texte1",
                        "json_metadata": {
                            "processingParameters": {
                                "shouldKeepNativeFrameRate": False,
                                "framesPlayedPerSecond": 10,
                                "shouldUseNativeVideo": True,
                            }
                        },
                    },
                    {
                        "content": str(Path("test_tree") / "video1.mp4"),
                        "external_id": "video1",
                        "json_metadata": {
                            "processingParameters": {
                                "shouldKeepNativeFrameRate": False,
                                "framesPlayedPerSecond": 10,
                                "shouldUseNativeVideo": True,
                            }
                        },
                    },
                    {
                        "content": str(Path("test_tree") / "video2.mp4"),
                        "external_id": "video2",
                        "json_metadata": {
                            "processingParameters": {
                                "shouldKeepNativeFrameRate": False,
                                "framesPlayedPerSecond": 10,
                                "shouldUseNativeVideo": True,
                            }
                        },
                    },
                ],
                ANY,
            ),
        ),
        (
            (
                "AAU, when I import videos to a video project, as frames with the native frame"
                " rate, I see a success"
            ),
            [str(Path("test_tree/"))],
            {
                "project-id": "frame_project",
            },
            ["frames"],
            (
                ANY,
                "frame_project",
                [
                    {
                        "content": str(Path("test_tree") / "image1.png"),
                        "external_id": "image1",
                        "json_metadata": {
                            "processingParameters": {
                                "shouldKeepNativeFrameRate": True,
                                "framesPlayedPerSecond": None,
                                "shouldUseNativeVideo": False,
                            }
                        },
                    },
                    {
                        "content": str(Path("test_tree") / "image2.jpg"),
                        "external_id": "image2",
                        "json_metadata": {
                            "processingParameters": {
                                "shouldKeepNativeFrameRate": True,
                                "framesPlayedPerSecond": None,
                                "shouldUseNativeVideo": False,
                            }
                        },
                    },
                    {
                        "content": str(Path("test_tree") / "texte1.txt"),
                        "external_id": "texte1",
                        "json_metadata": {
                            "processingParameters": {
                                "shouldKeepNativeFrameRate": True,
                                "framesPlayedPerSecond": None,
                                "shouldUseNativeVideo": False,
                            }
                        },
                    },
                    {
                        "content": str(Path("test_tree") / "video1.mp4"),
                        "external_id": "video1",
                        "json_metadata": {
                            "processingParameters": {
                                "shouldKeepNativeFrameRate": True,
                                "framesPlayedPerSecond": None,
                                "shouldUseNativeVideo": False,
                            }
                        },
                    },
                    {
                        "content": str(Path("test_tree") / "video2.mp4"),
                        "external_id": "video2",
                        "json_metadata": {
                            "processingParameters": {
                                "shouldKeepNativeFrameRate": True,
                                "framesPlayedPerSecond": None,
                                "shouldUseNativeVideo": False,
                            }
                        },
                    },
                ],
                ANY,
            ),
        ),
        (
            "AAU, when I import assets from a csv file, I see a success",
            [],
            {
                "project-id": "image_project",
                "from-csv": "assets_to_import.csv",
            },
            None,
            (
                ANY,
                "image_project",
                [
                    {
                        "content": str(Path("test_tree") / "leaf" / "image3.png"),
                        "external_id": "image3",
                    },
                    {
                        "content": (
                            "https://files.readme.io/cac9114-Kili_Wordmark_SoftWhite_RGB.svg"
                        ),
                        "external_id": "test",
                    },
                ],
                ANY,
            ),
        ),
    ],
)
def test_import(
    case_name: str,
    files: List[str],
    options,
    expected_service_payload,
    flags,
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch.object(ProjectQuery, "__call__", side_effect=mocked__ProjectQuery)

    runner = CliRunner()
    with runner.isolated_filesystem():
        _ = case_name
        os.mkdir("test_tree")
        # pylint: disable=unspecified-encoding
        open("test_tree/image1.png", "w")
        open("test_tree/image2.jpg", "w")
        open("test_tree/texte1.txt", "w")
        open("test_tree/video1.mp4", "w")
        open("test_tree/video2.mp4", "w")
        os.mkdir("test_tree/leaf")
        open("test_tree/leaf/image3.png", "w")
        open("test_tree/leaf/image4.jpg", "w")
        open("test_tree/leaf/texte2.txt", "w")
        # newline="" to disable universal newlines translation (bug fix for windows)
        with open("assets_to_import.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["external_id", "content"])
            writer.writerow(["image3", str(Path("test_tree") / "leaf" / "image3.png")])
            writer.writerow(
                [
                    "test",
                    "https://files.readme.io/cac9114-Kili_Wordmark_SoftWhite_RGB.svg",
                ]
            )

        arguments = files
        for k, v in options.items():
            arguments.append("--" + k)
            arguments.append(v)
        if flags:
            arguments.extend(["--" + flag for flag in flags])
        with patch("kili.services.asset_import.import_assets") as mocked_import_assets_service:
            result = runner.invoke(import_assets, arguments)
            debug_subprocess_pytest(result)
            mocked_import_assets_service.assert_called_with(*expected_service_payload)


@pytest.mark.parametrize(
    "name,test_case",
    [
        (
            "Export to Yolo v4 format using CLI",
            [
                "--output-format",
                "yolo_v4",
                "--output-file",
                "export.zip",
                "--project-id",
                "object_detection",
                "--layout",
                "split",
                "--verbose",
                "--api-key",
                "toto",
                "--endpoint",
                "localhost",
                "--without-assets",
            ],
        ),
        (
            "Export to Kili format using CLI",
            [
                "--output-format",
                "raw",
                "--output-file",
                "export.zip",
                "--project-id",
                "object_detection",
                "--layout",
                "split",
                "--verbose",
                "--api-key",
                "toto",
                "--endpoint",
                "localhost",
                "--without-assets",
            ],
        ),
    ],
)
def test_export(name: str, test_case: List[str], mocker: pytest_mock.MockerFixture):
    mocker.patch.object(ProjectQuery, "__call__", side_effect=mocked__ProjectQuery)

    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            export_labels,
            test_case,
        )
        debug_subprocess_pytest(result)
        assert result.output.count("export.zip")
