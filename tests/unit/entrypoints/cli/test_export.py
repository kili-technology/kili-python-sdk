import importlib

import pytest_mock
from click.testing import CliRunner

from kili.services.export.exceptions import NotCompatibleOptions

# The module, not `kili.entrypoints.cli.project.export`'s dotted path: on Python 3.10 mock resolves
# that path by attribute, and the click group named `project` shadows the package
export_module = importlib.import_module("kili.entrypoints.cli.project.export")


def _export(*options: str):
    return CliRunner().invoke(
        export_module.export_labels,
        ["--project-id", "project", "--output-file", "export.zip", *options],
    )


def test_the_export_passes_how_to_write_the_bounding_boxes(mocker: pytest_mock.MockerFixture):
    mocker.patch.object(export_module, "get_kili_client")
    service = mocker.patch.object(export_module, "service_export_labels")

    result = _export("--output-format", "yolo", "--bbox-as", "obb")

    assert result.exit_code == 0, result.output
    assert service.call_args.kwargs["label_format"] == "yolo"
    assert service.call_args.kwargs["bbox_as"] == "obb"


def test_the_export_refuses_a_bounding_boxes_choice_it_does_not_know():
    result = _export("--output-format", "yolo_v8", "--bbox-as", "OBB")

    assert result.exit_code != 0


def test_the_export_says_a_bounding_boxes_choice_does_not_fit_the_format(
    mocker: pytest_mock.MockerFixture,
):
    mocker.patch.object(export_module, "get_kili_client")
    mocker.patch.object(
        export_module,
        "service_export_labels",
        side_effect=NotCompatibleOptions('bbox_as="obb" is only available for the "yolo" format.'),
    )

    result = _export("--output-format", "yolo_v4", "--bbox-as", "obb")

    # A usage error, its message alone: no traceback
    assert result.exit_code == 2
    assert 'bbox_as="obb" is only available' in result.output
    assert "Traceback" not in result.output
