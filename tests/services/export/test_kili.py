import json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import pytest_mock

from kili.entrypoints.queries.label import QueriesLabel
from kili.orm import Asset
from kili.services.export.format.base import AbstractExporter
from kili.services.export.format.kili import KiliExporter
from tests.fakes.fake_data import (
    kili_format_expected_frame_asset_output,
    kili_format_frame_asset,
)


def test_preprocess_assets(mocker: pytest_mock.MockFixture):
    mocker_exporter = mocker.MagicMock()
    clean_assets = AbstractExporter.preprocess_assets(
        mocker_exporter, [Asset(**kili_format_frame_asset)], "raw"
    )
    assert len(clean_assets) == 1
    assert clean_assets[0] == kili_format_expected_frame_asset_output


def test_kili_exporter_convert_to_pixel_coords_pdf(mocker: pytest_mock.MockerFixture):
    mocker.patch.object(KiliExporter, "__init__", return_value=None)
    exporter = KiliExporter()  # type: ignore  # pylint: disable=no-value-for-parameter
    exporter.project = {
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
    scaled_asset = exporter.convert_to_pixel_coords(asset)  # type: ignore

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


def test_kili_export_labels_non_normalized_pdf(mocker: pytest_mock.MockerFixture):
    get_project_return_val = {
        "inputType": "PDF",
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
    mocker.patch("kili.services.export.get_project", return_value=get_project_return_val)
    mocker.patch("kili.entrypoints.queries.label.get_project", return_value=get_project_return_val)
    mocker.patch(
        "kili.services.export.format.base.get_project", return_value=get_project_return_val
    )
    mocker.patch(
        "kili.entrypoints.queries.asset.media_downloader.ProjectQuery.__call__",
        return_value=(i for i in [get_project_return_val]),
    )
    mocker.patch(
        "kili.services.export.format.base.fetch_assets",
        return_value=[
            Asset(asset)
            for asset in json.load(open("./tests/services/export/fakes/pdf_project_assets.json"))
        ],
    )

    kili = QueriesLabel()
    kili.api_endpoint = "https://"  # type: ignore
    kili.api_key = ""  # type: ignore
    kili.graphql_client = mocker.MagicMock()

    kili.export_labels(
        "fake_proj_id", "export_pixel_coords_kili_pdf.zip", fmt="kili", normalized_coordinates=False
    )

    with TemporaryDirectory() as extract_folder:
        with ZipFile("export_pixel_coords_kili_pdf.zip", "r") as z_f:
            # extract in a temp dir
            z_f.extractall(extract_folder)

        assert Path(f"{extract_folder}/README.kili.txt").is_file()
        assert Path(f"{extract_folder}/labels").is_dir()
        assert Path(f"{extract_folder}/labels/Cas_technique_n9.pdf.json").is_file()

        with Path(f"{extract_folder}/labels/Cas_technique_n9.pdf.json").open() as f:
            output = json.load(f)

    assert output == {
        "content": "https://storage.googleapis.com/label-backend-staging/projects/cljo5b3jjd31f9k8blj7/assets/cljo5b4dcf",
        "externalId": "Cas technique n9.pdf",
        "id": "cljo5b42500042a6akiuy79o7",
        "jsonContent": "",
        "jsonMetadata": {},
        "latestLabel": {
            "author": {
                "email": "test+admin+1@kili-technology.com",
                "firstname": "Feat1",
                "id": "user-feat1-1",
                "lastname": "Test Admin",
            },
            "createdAt": "2023-07-04T10:40:52.065Z",
            "isLatestLabelForUser": True,
            "jsonResponse": {
                "CLASSIFICATION_JOB": {"categories": [{"confidence": 100, "name": "C"}]},
                "OBJECT_DETECTION_JOB": {
                    "annotations": [
                        {
                            "annotations": [
                                {
                                    "boundingPoly": [
                                        {
                                            "normalizedVertices": [
                                                [
                                                    {
                                                        "x": 0.024123653461525008,
                                                        "y": 0.009304248327663437,
                                                    },
                                                    {
                                                        "x": 0.024123653461525008,
                                                        "y": 0.13956372491495156,
                                                    },
                                                    {
                                                        "x": 0.1864100494754205,
                                                        "y": 0.13956372491495156,
                                                    },
                                                    {
                                                        "x": 0.1864100494754205,
                                                        "y": 0.009304248327663437,
                                                    },
                                                ]
                                            ],
                                            "vertices": [
                                                [
                                                    {
                                                        "x": 0.024123653461525008 * 595,
                                                        "y": 0.009304248327663437 * 842,
                                                    },
                                                    {
                                                        "x": 0.024123653461525008 * 595,
                                                        "y": 0.13956372491495156 * 842,
                                                    },
                                                    {
                                                        "x": 0.1864100494754205 * 595,
                                                        "y": 0.13956372491495156 * 842,
                                                    },
                                                    {
                                                        "x": 0.1864100494754205 * 595,
                                                        "y": 0.009304248327663437 * 842,
                                                    },
                                                ]
                                            ],
                                        }
                                    ],
                                    "pageNumberArray": [1],
                                    "polys": [
                                        {
                                            "normalizedVertices": [
                                                [
                                                    {
                                                        "x": 0.024123653461525008,
                                                        "y": 0.009304248327663437,
                                                    },
                                                    {
                                                        "x": 0.024123653461525008,
                                                        "y": 0.13956372491495156,
                                                    },
                                                    {
                                                        "x": 0.1864100494754205,
                                                        "y": 0.13956372491495156,
                                                    },
                                                    {
                                                        "x": 0.1864100494754205,
                                                        "y": 0.009304248327663437,
                                                    },
                                                ]
                                            ],
                                            "vertices": [
                                                [
                                                    {
                                                        "x": 0.024123653461525008 * 595,
                                                        "y": 0.009304248327663437 * 842,
                                                    },
                                                    {
                                                        "x": 0.024123653461525008 * 595,
                                                        "y": 0.13956372491495156 * 842,
                                                    },
                                                    {
                                                        "x": 0.1864100494754205 * 595,
                                                        "y": 0.13956372491495156 * 842,
                                                    },
                                                    {
                                                        "x": 0.1864100494754205 * 595,
                                                        "y": 0.009304248327663437 * 842,
                                                    },
                                                ]
                                            ],
                                        }
                                    ],
                                }
                            ],
                            "categories": [{"confidence": 100, "name": "A"}],
                            "children": {},
                            "content": "",
                            "mid": "20230704124040213-29399",
                        },
                        {
                            "annotations": [
                                {
                                    "boundingPoly": [
                                        {
                                            "normalizedVertices": [
                                                [
                                                    {
                                                        "x": 0.7785360889855797,
                                                        "y": 0.831179517271267,
                                                    },
                                                    {
                                                        "x": 0.7785360889855797,
                                                        "y": 0.9180191683294592,
                                                    },
                                                    {
                                                        "x": 0.8816098810484593,
                                                        "y": 0.9180191683294592,
                                                    },
                                                    {
                                                        "x": 0.8816098810484593,
                                                        "y": 0.831179517271267,
                                                    },
                                                ]
                                            ],
                                            "vertices": [
                                                [
                                                    {
                                                        "x": 0.7785360889855797 * 595,
                                                        "y": 0.831179517271267 * 842,
                                                    },
                                                    {
                                                        "x": 0.7785360889855797 * 595,
                                                        "y": 0.9180191683294592 * 842,
                                                    },
                                                    {
                                                        "x": 0.8816098810484593 * 595,
                                                        "y": 0.9180191683294592 * 842,
                                                    },
                                                    {
                                                        "x": 0.8816098810484593 * 595,
                                                        "y": 0.831179517271267 * 842,
                                                    },
                                                ]
                                            ],
                                        }
                                    ],
                                    "pageNumberArray": [1],
                                    "polys": [
                                        {
                                            "normalizedVertices": [
                                                [
                                                    {
                                                        "x": 0.7785360889855797,
                                                        "y": 0.831179517271267,
                                                    },
                                                    {
                                                        "x": 0.7785360889855797,
                                                        "y": 0.9180191683294592,
                                                    },
                                                    {
                                                        "x": 0.8816098810484593,
                                                        "y": 0.9180191683294592,
                                                    },
                                                    {
                                                        "x": 0.8816098810484593,
                                                        "y": 0.831179517271267,
                                                    },
                                                ]
                                            ],
                                            "vertices": [
                                                [
                                                    {
                                                        "x": 0.7785360889855797 * 595,
                                                        "y": 0.831179517271267 * 842,
                                                    },
                                                    {
                                                        "x": 0.7785360889855797 * 595,
                                                        "y": 0.9180191683294592 * 842,
                                                    },
                                                    {
                                                        "x": 0.8816098810484593 * 595,
                                                        "y": 0.9180191683294592 * 842,
                                                    },
                                                    {
                                                        "x": 0.8816098810484593 * 595,
                                                        "y": 0.831179517271267 * 842,
                                                    },
                                                ]
                                            ],
                                        }
                                    ],
                                }
                            ],
                            "categories": [{"confidence": 100, "name": "B"}],
                            "children": {},
                            "content": "",
                            "mid": "20230704124043531-11579",
                        },
                        {
                            "annotations": [
                                {
                                    "boundingPoly": [
                                        {
                                            "normalizedVertices": [
                                                [
                                                    {
                                                        "x": 0.7646922448406724,
                                                        "y": 0.13165433196683027,
                                                    },
                                                    {
                                                        "x": 0.7646922448406724,
                                                        "y": 0.21722964774526993,
                                                    },
                                                    {
                                                        "x": 0.9076834776157575,
                                                        "y": 0.21722964774526993,
                                                    },
                                                    {
                                                        "x": 0.9076834776157575,
                                                        "y": 0.13165433196683027,
                                                    },
                                                ]
                                            ],
                                            "vertices": [
                                                [
                                                    {
                                                        "x": 0.7646922448406724 * 420,
                                                        "y": 0.13165433196683027 * 595,
                                                    },
                                                    {
                                                        "x": 0.7646922448406724 * 420,
                                                        "y": 0.21722964774526993 * 595,
                                                    },
                                                    {
                                                        "x": 0.9076834776157575 * 420,
                                                        "y": 0.21722964774526993 * 595,
                                                    },
                                                    {
                                                        "x": 0.9076834776157575 * 420,
                                                        "y": 0.13165433196683027 * 595,
                                                    },
                                                ]
                                            ],
                                        }
                                    ],
                                    "pageNumberArray": [2],
                                    "polys": [
                                        {
                                            "normalizedVertices": [
                                                [
                                                    {
                                                        "x": 0.7646922448406724,
                                                        "y": 0.13165433196683027,
                                                    },
                                                    {
                                                        "x": 0.7646922448406724,
                                                        "y": 0.21722964774526993,
                                                    },
                                                    {
                                                        "x": 0.9076834776157575,
                                                        "y": 0.21722964774526993,
                                                    },
                                                    {
                                                        "x": 0.9076834776157575,
                                                        "y": 0.13165433196683027,
                                                    },
                                                ]
                                            ],
                                            "vertices": [
                                                [
                                                    {
                                                        "x": 0.7646922448406724 * 420,
                                                        "y": 0.13165433196683027 * 595,
                                                    },
                                                    {
                                                        "x": 0.7646922448406724 * 420,
                                                        "y": 0.21722964774526993 * 595,
                                                    },
                                                    {
                                                        "x": 0.9076834776157575 * 420,
                                                        "y": 0.21722964774526993 * 595,
                                                    },
                                                    {
                                                        "x": 0.9076834776157575 * 420,
                                                        "y": 0.13165433196683027 * 595,
                                                    },
                                                ]
                                            ],
                                        }
                                    ],
                                }
                            ],
                            "categories": [{"confidence": 100, "name": "B"}],
                            "children": {},
                            "content": "",
                            "mid": "20230704124045705-1891",
                        },
                    ]
                },
            },
            "labelType": "DEFAULT",
            "modelName": None,
        },
        "pageResolutions": [
            {"height": 842, "pageNumber": 1, "rotation": 0, "width": 595},
            {"height": 595, "pageNumber": 2, "rotation": 0, "width": 420},
        ],
    }


def test_kili_export_labels_non_normalized_image(mocker: pytest_mock.MockerFixture):
    get_project_return_val = {
        "id": "fake_proj_id",
        "title": "hgfhfg",
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
            }
        },
    }

    mocker.patch("kili.services.export.get_project", return_value=get_project_return_val)
    mocker.patch("kili.entrypoints.queries.label.get_project", return_value=get_project_return_val)
    mocker.patch(
        "kili.services.export.format.base.get_project", return_value=get_project_return_val
    )
    mocker.patch(
        "kili.entrypoints.queries.asset.media_downloader.ProjectQuery.__call__",
        return_value=(i for i in [get_project_return_val]),
    )
    mocker.patch(
        "kili.services.export.format.base.fetch_assets",
        return_value=[
            Asset(asset)
            for asset in json.load(open("./tests/services/export/fakes/image_project_assets.json"))
        ],
    )

    kili = QueriesLabel()
    kili.api_endpoint = "https://"  # type: ignore
    kili.api_key = ""  # type: ignore
    kili.graphql_client = mocker.MagicMock()

    kili.export_labels(
        "fake_proj_id",
        "export_pixel_coords_kili_image.zip",
        fmt="kili",
        normalized_coordinates=False,
    )

    with TemporaryDirectory() as extract_folder:
        with ZipFile("export_pixel_coords_kili_image.zip", "r") as z_f:
            # extract in a temp dir
            z_f.extractall(extract_folder)

        assert Path(f"{extract_folder}/README.kili.txt").is_file()
        assert Path(f"{extract_folder}/labels").is_dir()
        assert Path(f"{extract_folder}/labels/42015077eed072c50d59232dcc0ad0b1.jpg.json").is_file()

        with Path(f"{extract_folder}/labels/42015077eed072c50d59232dcc0ad0b1.jpg.json").open() as f:
            output = json.load(f)

    assert output == {
        "content": "https://storage.googleapis.com/label-backend-staging/projects/clk8fq8edf38d13",
        "externalId": "42015077eed072c50d59232dcc0ad0b1.jpg",
        "id": "clk8fq9ow00022a69icovadtq",
        "jsonContent": "",
        "jsonMetadata": {},
        "latestLabel": {
            "author": {
                "email": "jonas.maison@kili-technology.com",
                "firstname": "Jonas",
                "id": "123456",
                "lastname": "Maison",
            },
            "createdAt": "2023-07-18T15:24:11.433Z",
            "isLatestLabelForUser": True,
            "jsonResponse": {
                "OBJECT_DETECTION_JOB": {
                    "annotations": [
                        {
                            "boundingPoly": [
                                {
                                    "normalizedVertices": [
                                        {"x": 0.7412807669633257, "y": 0.11831185681407619},
                                        {"x": 0.7412807669633257, "y": 0.07455291056382807},
                                    ],
                                    "vertices": [
                                        {
                                            "x": 0.7412807669633257 * 474,
                                            "y": 0.11831185681407619 * 842,
                                        },
                                        {
                                            "x": 0.7412807669633257 * 474,
                                            "y": 0.07455291056382807 * 842,
                                        },
                                    ],
                                }
                            ],
                            "categories": [{"name": "A"}],
                            "children": {},
                            "mid": "20230718172351536-92877",
                            "type": "rectangle",
                        }
                    ]
                },
                "OBJECT_DETECTION_JOB_0": {
                    "annotations": [
                        {
                            "categories": [{"name": "B"}],
                            "children": {},
                            "mid": "20230718172353363-53863",
                            "point": {"x": 0.8727983223923027 * 474, "y": 0.2035857007889187 * 842},
                            "type": "marker",
                        }
                    ]
                },
                "OBJECT_DETECTION_JOB_1": {
                    "annotations": [
                        {
                            "boundingPoly": [
                                {
                                    "normalizedVertices": [
                                        {"x": 0.7891053325738627, "y": 0.2955916903407224},
                                        {"x": 0.6456316357422514, "y": 0.3483268306935856},
                                    ],
                                    "vertices": [
                                        {
                                            "x": 0.7891053325738627 * 474,
                                            "y": 0.2955916903407224 * 842,
                                        },
                                        {
                                            "x": 0.6456316357422514 * 474,
                                            "y": 0.3483268306935856 * 842,
                                        },
                                    ],
                                }
                            ],
                            "categories": [{"name": "C"}],
                            "children": {},
                            "mid": "20230718172356733-32196",
                            "type": "polygon",
                        }
                    ]
                },
                "OBJECT_DETECTION_JOB_2": {
                    "annotations": [
                        {
                            "categories": [{"name": "D"}],
                            "children": {},
                            "mid": "20230718172359896-17202",
                            "polyline": [
                                {"x": 0.6555950869111132 * 474, "y": 0.2574428654046088 * 842},
                                {"x": 0.5659240263913562 * 474, "y": 0.17890116700672754 * 842},
                            ],
                            "type": "polyline",
                        }
                    ]
                },
                "OBJECT_DETECTION_JOB_3": {
                    "annotations": [
                        {
                            "boundingPoly": [
                                {
                                    "normalizedVertices": [
                                        {"x": 0.3686485611814346, "y": 0.410038},
                                        {"x": 0.3806035400843882, "y": 0.410038},
                                    ],
                                    "vertices": [
                                        {"x": 0.3686485611814346 * 474, "y": 0.410038 * 842},
                                        {"x": 0.3806035400843882 * 474, "y": 0.410038 * 842},
                                    ],
                                }
                            ],
                            "categories": [{"name": "E"}],
                            "children": {},
                            "mid": "20230718172405691-91771",
                            "type": "semantic",
                        }
                    ]
                },
            },
            "labelType": "DEFAULT",
            "modelName": None,
        },
        "pageResolutions": None,
        "resolution": {"height": 842, "width": 474},
    }
