import json
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import TYPE_CHECKING
from zipfile import ZipFile

import pytest_mock
from kili_formats import convert_to_pixel_coords

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.presentation.client.label import LabelClientMethods
from kili.services.export.format.base import AbstractExporter
from kili.services.export.format.kili import KiliExporter
from tests.fakes.fake_data import (
    kili_format_expected_frame_asset_output,
    kili_format_frame_asset,
)
from tests.unit.adapters.kili_api_gateway.label.test_data import test_case_13

from .expected.geojson_project_assets_export import geojson_project_asset
from .expected.image_project_assets_unnormalized import image_project_asset_unnormalized
from .expected.pdf_project_assets_unnormalized import pdf_project_asset_unnormalized
from .expected.video_project_assets_unnormalized import video_project_asset_unnormalized

if TYPE_CHECKING:
    from kili_formats.types import ProjectDict


def test_preprocess_assets(mocker: pytest_mock.MockFixture):
    mocker_exporter = mocker.MagicMock()
    clean_assets = AbstractExporter.preprocess_assets(mocker_exporter, [kili_format_frame_asset])
    assert len(clean_assets) == 1
    assert clean_assets[0] == kili_format_expected_frame_asset_output


def test_kili_exporter_convert_to_pixel_coords_pdf(mocker: pytest_mock.MockerFixture):
    mocker.patch.object(KiliExporter, "__init__", return_value=None)
    exporter = KiliExporter()  # type: ignore  # pylint: disable=no-value-for-parameter
    exporter.normalized_coordinates = None

    project: ProjectDict = {
        "id": "fake_project_id",
        "title": "Fake Project Title",
        "description": "Fake Project Description",
        "organizationId": "fake_organization_id",
        "inputType": "PDF",
        "jsonInterface": {
            "jobs": {
                "OBJECT_DETECTION_JOB": {
                    "content": {
                        "categories": {
                            "A": {"children": [], "color": "#472CED", "name": "A"},
                            "B": {"children": [], "name": "B", "color": "#5CE7B7"},
                        },
                        "input": "radio",
                    },
                    "instruction": "BB",
                    "mlTask": "OBJECT_DETECTION",
                    "required": 1,
                    "tools": ["rectangle"],
                    "isChild": False,
                }
            }
        },
    }
    asset = {
        "latestLabel": {
            "author": {
                "id": "user-feat1-1",
                "email": "test+admin+1@kili-technology.com",
                "firstname": "Feat1",
                "lastname": "Test Admin",
                "name": "Feat1 Test Admin",
            },
            "jsonResponse": {
                "OBJECT_DETECTION_JOB": {
                    "annotations": [
                        {
                            "children": {},
                            "annotations": [
                                {
                                    "boundingPoly": [
                                        {
                                            "normalizedVertices": [
                                                {"x": 0.47, "y": 0.1},
                                                {"x": 0.47, "y": 0.23},
                                                {"x": 0.67, "y": 0.23},
                                                {"x": 0.67, "y": 0.1},
                                            ]
                                        }
                                    ],
                                    "pageNumberArray": [1],
                                    "polys": [
                                        {
                                            "normalizedVertices": [
                                                {"x": 0.47, "y": 0.1},
                                                {"x": 0.47, "y": 0.23},
                                                {"x": 0.67, "y": 0.23},
                                                {"x": 0.67, "y": 0.1},
                                            ]
                                        }
                                    ],
                                }
                            ],
                            "categories": [{"confidence": 100, "name": "A"}],
                            "content": "",
                            "mid": "20230703112327217-43948",
                            "type": "rectangle",
                        },
                    ]
                }
            },
            "createdAt": "2023-07-03T12:18:08.825Z",
            "isLatestLabelForUser": True,
            "labelType": "DEFAULT",
            "modelName": None,
        },
        "pageResolutions": [
            {"pageNumber": 1, "height": 842, "width": 595, "rotation": 0},
            {"pageNumber": 2, "height": 842, "width": 595, "rotation": 0},
        ],
        "content": "https://",
        "jsonContent": "https://",
    }
    scaled_asset = convert_to_pixel_coords(asset, project)

    assert scaled_asset == {
        "content": "https://",
        "jsonContent": "https://",
        "latestLabel": {
            "author": {
                "id": "user-feat1-1",
                "email": "test+admin+1@kili-technology.com",
                "firstname": "Feat1",
                "lastname": "Test Admin",
                "name": "Feat1 Test Admin",
            },
            "jsonResponse": {
                "OBJECT_DETECTION_JOB": {
                    "annotations": [
                        {
                            "children": {},
                            "annotations": [
                                {
                                    "boundingPoly": [
                                        {
                                            "normalizedVertices": [
                                                {"x": 0.47, "y": 0.1},
                                                {"x": 0.47, "y": 0.23},
                                                {"x": 0.67, "y": 0.23},
                                                {"x": 0.67, "y": 0.1},
                                            ],
                                            "vertices": [
                                                {"x": 0.47 * 595, "y": 0.1 * 842},
                                                {"x": 0.47 * 595, "y": 0.23 * 842},
                                                {"x": 0.67 * 595, "y": 0.23 * 842},
                                                {"x": 0.67 * 595, "y": 0.1 * 842},
                                            ],
                                        }
                                    ],
                                    "pageNumberArray": [1],
                                    "polys": [
                                        {
                                            "normalizedVertices": [
                                                {"x": 0.47, "y": 0.1},
                                                {"x": 0.47, "y": 0.23},
                                                {"x": 0.67, "y": 0.23},
                                                {"x": 0.67, "y": 0.1},
                                            ],
                                            "vertices": [
                                                {"x": 0.47 * 595, "y": 0.1 * 842},
                                                {"x": 0.47 * 595, "y": 0.23 * 842},
                                                {"x": 0.67 * 595, "y": 0.23 * 842},
                                                {"x": 0.67 * 595, "y": 0.1 * 842},
                                            ],
                                        }
                                    ],
                                }
                            ],
                            "categories": [{"confidence": 100, "name": "A"}],
                            "content": "",
                            "mid": "20230703112327217-43948",
                            "type": "rectangle",
                        },
                    ]
                }
            },
            "createdAt": "2023-07-03T12:18:08.825Z",
            "isLatestLabelForUser": True,
            "labelType": "DEFAULT",
            "modelName": None,
        },
        "pageResolutions": [
            {"pageNumber": 1, "height": 842, "width": 595, "rotation": 0},
            {"pageNumber": 2, "height": 842, "width": 595, "rotation": 0},
        ],
    }


def test_kili_exporter_convert_to_pixel_coords_pdf_polygon(mocker: pytest_mock.MockerFixture):
    """A PDF polygon scales to pixels against the dimensions of its own page.

    Self-contained on purpose: `fakes/pdf_project_assets.json` is left untouched so that the
    bounding box expectations keep proving that nothing regressed for existing PDF projects.
    """
    mocker.patch.object(KiliExporter, "__init__", return_value=None)
    exporter = KiliExporter()  # type: ignore  # pylint: disable=no-value-for-parameter
    exporter.normalized_coordinates = None

    project: ProjectDict = {
        "id": "fake_project_id",
        "title": "Fake Project Title",
        "description": "Fake Project Description",
        "organizationId": "fake_organization_id",
        "inputType": "PDF",
        "jsonInterface": {
            "jobs": {
                "OBJECT_DETECTION_JOB": {
                    "content": {
                        "categories": {
                            "A": {"children": [], "color": "#472CED", "name": "A"},
                            "B": {"children": [], "name": "B", "color": "#5CE7B7"},
                        },
                        "input": "radio",
                    },
                    "instruction": "Polygon",
                    "mlTask": "OBJECT_DETECTION",
                    "required": 1,
                    "tools": ["polygon"],
                    "isChild": False,
                }
            }
        },
    }
    normalized_vertices = [
        {"x": 0.1, "y": 0.1},
        {"x": 0.3, "y": 0.05},
        {"x": 0.4, "y": 0.3},
        {"x": 0.25, "y": 0.45},
        {"x": 0.08, "y": 0.3},
    ]
    enclosing_rectangle = [
        {"x": 0.08, "y": 0.05},
        {"x": 0.08, "y": 0.45},
        {"x": 0.4, "y": 0.45},
        {"x": 0.4, "y": 0.05},
    ]
    # page 2 is landscape, so scaling against page 1 would give a different result
    page_resolutions = [
        {"pageNumber": 1, "height": 842, "width": 595, "rotation": 0},
        {"pageNumber": 2, "height": 595, "width": 842, "rotation": 0},
    ]
    asset = {
        "latestLabel": {
            "author": {
                "id": "user-feat1-1",
                "email": "test+admin+1@kili-technology.com",
                "firstname": "Feat1",
                "lastname": "Test Admin",
                "name": "Feat1 Test Admin",
            },
            "jsonResponse": {
                "OBJECT_DETECTION_JOB": {
                    "annotations": [
                        {
                            "children": {},
                            "annotations": [
                                {
                                    # the backend derives boundingPoly as the enclosing rectangle,
                                    # so only polys carries the polygon's own five vertices
                                    "boundingPoly": [
                                        {"normalizedVertices": [enclosing_rectangle]}
                                    ],
                                    "pageNumberArray": [2],
                                    "polys": [{"normalizedVertices": [normalized_vertices]}],
                                }
                            ],
                            "categories": [{"confidence": 100, "name": "A"}],
                            "content": "",
                            "mid": "20230703112327217-43948",
                            "type": "polygon",
                        },
                    ]
                }
            },
            "createdAt": "2023-07-03T12:18:08.825Z",
            "isLatestLabelForUser": True,
            "labelType": "DEFAULT",
            "modelName": None,
        },
        "pageResolutions": page_resolutions,
        "content": "https://",
        "jsonContent": "https://",
    }

    scaled_asset = convert_to_pixel_coords(asset, project)

    def to_pixels(vertices):
        return [[{"x": vertex["x"] * 842, "y": vertex["y"] * 595} for vertex in vertices]]

    scaled_page_annotation = scaled_asset["latestLabel"]["jsonResponse"]["OBJECT_DETECTION_JOB"][
        "annotations"
    ][0]["annotations"][0]

    assert scaled_page_annotation["polys"] == [
        {
            "normalizedVertices": [normalized_vertices],
            "vertices": to_pixels(normalized_vertices),
        }
    ]
    assert scaled_page_annotation["boundingPoly"] == [
        {
            "normalizedVertices": [enclosing_rectangle],
            "vertices": to_pixels(enclosing_rectangle),
        }
    ]
    assert scaled_page_annotation["pageNumberArray"] == [2]
    # the polygon keeps its five vertices in polys, while boundingPoly stays the 4-vertex box
    assert len(scaled_page_annotation["polys"][0]["vertices"][0]) == 5
    assert len(scaled_page_annotation["boundingPoly"][0]["vertices"][0]) == 4


def test_kili_export_labels_non_normalized_pdf(mocker: pytest_mock.MockerFixture):
    get_project_return_val = {
        "inputType": "PDF",
        "dataConnections": None,
        "id": "fake_proj_id",
        "title": "fake_proj_title",
        "description": "fake_proj_description",
        "jsonInterface": {
            "jobs": {
                "OBJECT_DETECTION_JOB": {
                    "content": {
                        "categories": {
                            "A": {"children": [], "color": "#472CED", "name": "A"},
                            "B": {"children": [], "name": "B", "color": "#5CE7B7"},
                        },
                        "input": "radio",
                    },
                    "instruction": "BBox",
                    "mlTask": "OBJECT_DETECTION",
                    "required": 1,
                    "tools": ["rectangle"],
                    "isChild": False,
                },
                "CLASSIFICATION_JOB": {
                    "content": {
                        "categories": {
                            "C": {"children": [], "name": "C"},
                            "D": {"children": [], "name": "D"},
                        },
                        "input": "radio",
                    },
                    "instruction": "Class",
                    "mlTask": "CLASSIFICATION",
                    "required": 1,
                    "isChild": False,
                },
            }
        },
    }
    mocker.patch(
        "kili.services.export.format.base.fetch_assets",
        return_value=[
            asset
            for asset in json.load(
                open("./tests/unit/services/export/fakes/pdf_project_assets.json")
            )
        ],
    )
    mocker.patch.object(AbstractExporter, "_check_and_ensure_asset_access", return_value=None)

    kili = LabelClientMethods()
    kili.api_endpoint = "https://"  # type: ignore
    kili.api_key = ""  # type: ignore
    kili.kili_api_gateway = mocker.MagicMock()
    kili.kili_api_gateway.get_project.return_value = get_project_return_val
    kili.graphql_client = mocker.MagicMock()  # pyright: ignore[reportGeneralTypeIssues]
    kili.http_client = mocker.MagicMock()  # pyright: ignore[reportGeneralTypeIssues]

    with TemporaryDirectory() as export_folder:
        export_filename = str(Path(export_folder) / "export_pixel_coords_kili_pdf.zip")

        kili.export_labels(
            "fake_proj_id", export_filename, fmt="kili", normalized_coordinates=False
        )

        with TemporaryDirectory() as extract_folder:
            with ZipFile(export_filename, "r") as z_f:
                # extract in a temp dir
                z_f.extractall(extract_folder)

            assert Path(f"{extract_folder}/README.kili.txt").is_file()
            assert Path(f"{extract_folder}/labels").is_dir()
            assert Path(f"{extract_folder}/labels/Cas_technique_n9.pdf.json").is_file()

            with Path(f"{extract_folder}/labels/Cas_technique_n9.pdf.json").open() as f:
                output = json.load(f)

    assert output == pdf_project_asset_unnormalized


def test_kili_export_labels_non_normalized_image(mocker: pytest_mock.MockerFixture):
    get_project_return_val = {
        "id": "fake_proj_id",
        "title": "hgfhfg",
        "dataConnections": None,
        "inputType": "IMAGE",
        "jsonInterface": {
            "jobs": {
                "OBJECT_DETECTION_JOB": {
                    "content": {
                        "categories": {"A": {"children": [], "color": "#472CED", "name": "A"}},
                        "input": "radio",
                    },
                    "instruction": "BBOX",
                    "mlTask": "OBJECT_DETECTION",
                    "required": 1,
                    "tools": ["rectangle"],
                    "isChild": False,
                },
                "OBJECT_DETECTION_JOB_0": {
                    "content": {
                        "categories": {"B": {"children": [], "color": "#5CE7B7", "name": "B"}},
                        "input": "radio",
                    },
                    "instruction": "POINT",
                    "mlTask": "OBJECT_DETECTION",
                    "required": 1,
                    "tools": ["marker"],
                    "isChild": False,
                },
                "OBJECT_DETECTION_JOB_1": {
                    "content": {
                        "categories": {"C": {"children": [], "color": "#D33BCE", "name": "C"}},
                        "input": "radio",
                    },
                    "instruction": "POLYGON",
                    "mlTask": "OBJECT_DETECTION",
                    "required": 1,
                    "tools": ["polygon"],
                    "isChild": False,
                },
                "OBJECT_DETECTION_JOB_2": {
                    "content": {
                        "categories": {"D": {"children": [], "color": "#FB753C", "name": "D"}},
                        "input": "radio",
                    },
                    "instruction": "LINE",
                    "mlTask": "OBJECT_DETECTION",
                    "required": 1,
                    "tools": ["polyline"],
                    "isChild": False,
                },
                "OBJECT_DETECTION_JOB_3": {
                    "content": {
                        "categories": {"E": {"children": [], "color": "#3BCADB", "name": "E"}},
                        "input": "radio",
                    },
                    "instruction": "SEMANTIC",
                    "mlTask": "OBJECT_DETECTION",
                    "required": 1,
                    "tools": ["semantic"],
                    "isChild": False,
                },
                "POSE_ESTIMATION_JOB": {
                    "content": {
                        "categories": {
                            "HEAD": {
                                "children": [],
                                "name": "Head",
                                "color": "#733AFB",
                                "points": [
                                    {
                                        "code": "RIGHT_EARBASE",
                                        "name": "Right earbase",
                                        "id": "point53",
                                    },
                                    {"code": "RIGHT_EYE", "name": "Right eye", "id": "point54"},
                                    {"code": "NOSE", "name": "Nose", "id": "point55"},
                                    {"code": "LEFT_EYE", "name": "Left eye", "id": "point56"},
                                    {
                                        "code": "LEFT_EARBASE",
                                        "name": "Left earbase",
                                        "id": "point57",
                                    },
                                ],
                                "id": "category58",
                            }
                        },
                        "input": "radio",
                    },
                    "instruction": "Body parts from the animal point of view",
                    "isChild": False,
                    "tools": ["pose"],
                    "mlTask": "OBJECT_DETECTION",
                    "models": {},
                    "isVisible": True,
                    "required": 1,
                    "isNew": False,
                },
            }
        },
    }

    mocker.patch(
        "kili.services.export.format.base.fetch_assets",
        return_value=[
            asset
            for asset in json.load(
                open("./tests/unit/services/export/fakes/image_project_assets.json")
            )
        ],
    )
    mocker.patch.object(AbstractExporter, "_check_and_ensure_asset_access", return_value=None)

    kili = LabelClientMethods()
    kili.api_endpoint = "https://"  # type: ignore
    kili.api_key = ""  # type: ignore
    kili.kili_api_gateway = mocker.MagicMock()
    kili.kili_api_gateway.get_project.return_value = get_project_return_val
    kili.graphql_client = mocker.MagicMock()  # pyright: ignore[reportGeneralTypeIssues]
    kili.http_client = mocker.MagicMock()  # pyright: ignore[reportGeneralTypeIssues]

    with TemporaryDirectory() as export_folder:
        export_filename = str(Path(export_folder) / "export_pixel_coords_kili_image.zip")
        kili.export_labels(
            "fake_proj_id",
            export_filename,
            fmt="kili",
            normalized_coordinates=False,
        )

        with TemporaryDirectory() as extract_folder:
            with ZipFile(export_filename, "r") as z_f:
                # extract in a temp dir
                z_f.extractall(extract_folder)

            assert Path(f"{extract_folder}/README.kili.txt").is_file()
            assert Path(f"{extract_folder}/labels").is_dir()
            assert Path(
                f"{extract_folder}/labels/42015077eed072c50d59232dcc0ad0b1.jpg.json"
            ).is_file()

            with Path(
                f"{extract_folder}/labels/42015077eed072c50d59232dcc0ad0b1.jpg.json"
            ).open() as f:
                output = json.load(f)

    assert output == image_project_asset_unnormalized


def test_kili_export_labels_non_normalized_video(mocker: pytest_mock.MockerFixture):
    get_project_return_val = {
        "jsonInterface": {
            "jobs": {
                "OBJECT_DETECTION_JOB": {
                    "content": {
                        "categories": {"A": {"children": [], "color": "#472CED", "name": "A"}},
                        "input": "radio",
                    },
                    "instruction": "BBOX",
                    "mlTask": "OBJECT_DETECTION",
                    "required": 1,
                    "tools": ["rectangle"],
                    "isChild": False,
                    "models": {"tracking": {}},
                }
            }
        },
        "inputType": "VIDEO",
        "title": "Object tracking on video",
        "description": "Use bounding-box to track objects across video frames.",
        "id": "fake_proj_id",
        "dataConnections": None,
    }

    mocker.patch(
        "kili.services.export.format.base.fetch_assets",
        return_value=[
            asset
            for asset in json.load(
                open("./tests/unit/services/export/fakes/video_project_assets.json")
            )
        ],
    )
    mocker.patch.object(AbstractExporter, "_check_and_ensure_asset_access", return_value=None)
    kili = LabelClientMethods()
    kili.api_endpoint = "https://"  # type: ignore
    kili.api_key = ""  # type: ignore
    kili.kili_api_gateway = mocker.MagicMock()
    kili.kili_api_gateway.get_project.return_value = get_project_return_val
    kili.graphql_client = mocker.MagicMock()  # pyright: ignore[reportGeneralTypeIssues]
    kili.http_client = mocker.MagicMock()  # pyright: ignore[reportGeneralTypeIssues]

    with TemporaryDirectory() as export_folder:
        export_filename = str(Path(export_folder) / "export_pixel_coords_kili_video.zip")

        kili.export_labels(
            "fake_proj_id",
            export_filename,
            fmt="kili",
            normalized_coordinates=False,
        )

        with TemporaryDirectory() as extract_folder:
            with ZipFile(export_filename, "r") as z_f:
                # extract in a temp dir
                z_f.extractall(extract_folder)

            assert Path(f"{extract_folder}/README.kili.txt").is_file()
            assert Path(f"{extract_folder}/labels").is_dir()
            assert Path(f"{extract_folder}/labels/Click_here_to_start.json").is_file()

            with Path(f"{extract_folder}/labels/Click_here_to_start.json").open() as f:
                output = json.load(f)

    assert output == video_project_asset_unnormalized


def test_save_assets_export_with_external_id_containing_slash(
    mocker: pytest_mock.MockerFixture, tmp_path: Path
):
    mocker.patch.object(KiliExporter, "__init__", return_value=None)
    exporter = KiliExporter()  # type: ignore  # pylint: disable=no-value-for-parameter
    exporter.normalized_coordinates = False
    exporter.logger = mocker.MagicMock()
    exporter.with_assets = True
    exporter.single_file = False
    exporter.export_root_folder = tmp_path
    exporter.label_format = "kili"
    exporter.project_id = "fake_proj_id"  # type: ignore
    exporter.export_type = "latest"
    exporter.project = {
        "id": "fake_proj_id",
        "title": "fake_proj_title",
        "description": "fake_proj_description",
        "organizationId": "fake_organization_id",
        "inputType": "IMAGE",
        "jsonInterface": {
            "jobs": {
                "OBJECT_DETECTION_JOB": {
                    "content": {
                        "categories": {"A": {"children": [], "color": "#472CED", "name": "A"}},
                        "input": "radio",
                    },
                    "instruction": "BBOX",
                    "mlTask": "OBJECT_DETECTION",
                    "required": 1,
                    "tools": ["rectangle"],
                    "isChild": False,
                    "models": {"tracking": {}},
                }
            }
        },
    }
    with NamedTemporaryFile() as f:
        f.write(b"")
        assets = [
            {
                "externalId": "a/b.png",
                "content": f.name,
                "jsonContent": f.name,
            }
        ]
        export_folder = tmp_path / "export_folder"
        exporter._save_assets_export(assets, Path(export_folder))  # pylint: disable=protected-access
        assert Path(exporter.base_folder / "labels/a/b.png.json").is_file()


def test_kili_export_labels_geojson(mocker: pytest_mock.MockerFixture):
    def mocked_graphql_execute(query, variables=None, **kwargs):
        if "projects(" in query:
            return {
                "data": [
                    {
                        "inputType": "IMAGE",
                        "title": "",
                        "id": "fake_geojson_project_id",
                        "jsonInterface": test_case_13.json_interface,
                    }
                ]
            }

        if "countProjects(" in query:
            return {"data": 1}

        if "countLabels(" in query:
            return {"data": 1}

        if "countAssets(" in query:
            return {"data": 1}

        if "assets(" in query:
            return {"data": test_case_13.assets}

        if "viewer" in query:
            return {"data": {"email": "test+admin@kili-technology.com"}}

        raise NotImplementedError

    mocker.patch.object(AbstractExporter, "_check_and_ensure_asset_access", return_value=None)
    graphql_client = mocker.MagicMock()
    graphql_client.execute.side_effect = mocked_graphql_execute
    http_client = mocker.MagicMock()

    kili = LabelClientMethods()
    kili.api_endpoint = "https://"  # type: ignore
    kili.api_key = ""  # type: ignore
    kili.kili_api_gateway = KiliAPIGateway(graphql_client=graphql_client, http_client=http_client)
    kili.graphql_client = graphql_client  # pyright: ignore[reportGeneralTypeIssues]
    kili.http_client = http_client  # pyright: ignore[reportGeneralTypeIssues]

    with TemporaryDirectory() as export_folder:
        export_filename = str(Path(export_folder) / "export_kili_geojson.zip")

        kili.export_labels(
            "fake_geojson_label_id",
            export_filename,
            fmt="geojson",
            layout="merged",
            with_assets=False,
        )

        with TemporaryDirectory() as extract_folder:
            with ZipFile(export_filename, "r") as z_f:
                # extract in a temp dir
                z_f.extractall(extract_folder)

            assert Path(f"{extract_folder}/README.kili.txt").is_file()
            assert Path(f"{extract_folder}/labels").is_dir()
            assert Path(f"{extract_folder}/labels/Click_here_to_start.geojson").is_file()

            with Path(f"{extract_folder}/labels/Click_here_to_start.geojson").open() as f:
                output = json.load(f)

    # Asset/export-level metadata sits once at the root under properties.kili (not per-feature).
    # Assert it, then strip it (exportDate is dynamic) before comparing against the static fixture.
    root_kili = output.pop("properties")["kili"]
    assert root_kili["assetId"] == "clrrybpj800003b75o7ykp3st"
    assert root_kili["author"] == "test+admin@kili-technology.com"
    assert root_kili["exportDate"]

    assert output == geojson_project_asset
