"""Tests for the labeling mode of a created or copied project."""

from unittest.mock import MagicMock

import pytest

from kili.domain.project import ProjectId
from kili.use_cases.project.project import ProjectUseCases


@pytest.fixture()
def mock_gateway():
    gateway = MagicMock()
    gateway.create_project.return_value = "new-project"
    gateway.list_tags_by_project.return_value = []
    gateway.list_tags_by_org.return_value = []
    return gateway


@pytest.fixture()
def use_cases(mock_gateway):
    return ProjectUseCases(mock_gateway)


def _source_project(labeling_crs_code: str | None = None) -> dict:
    return {
        "geospatialSettings": (
            {"labelingCRSCode": labeling_crs_code} if labeling_crs_code else None
        ),
        "inputType": "GEOSPATIAL",
        "instructions": None,
        "jsonInterface": {"jobs": {}},
    }


def _copy(use_cases, mock_gateway, source, **kwargs) -> str:
    mock_gateway.get_project.return_value = source
    return use_cases.create_project(
        title="a copy",
        description="",
        compliance_tags=None,
        from_demo_project=None,
        project_id=ProjectId("source-project"),
        **kwargs,
    )


def test_copying_a_pixel_labeled_project_keeps_the_mode(use_cases, mock_gateway):
    """The mode is settable at creation only, so a copy losing it could never be repaired."""
    _copy(use_cases, mock_gateway, _source_project("PIXEL"))

    assert mock_gateway.create_project.call_args.kwargs["pixel_labeling"] is True


def test_copying_a_reprojected_project_does_not_invent_the_mode(use_cases, mock_gateway):
    _copy(use_cases, mock_gateway, _source_project("EPSG:3857"))

    assert mock_gateway.create_project.call_args.kwargs["pixel_labeling"] is False


def test_copying_a_project_without_geospatial_settings(use_cases, mock_gateway):
    _copy(use_cases, mock_gateway, _source_project())

    assert mock_gateway.create_project.call_args.kwargs["pixel_labeling"] is False


def test_asking_for_pixel_labeling_on_a_copy_is_refused(use_cases, mock_gateway):
    """It used to pass the client guard, `input_type` being None, then be discarded."""
    with pytest.raises(ValueError, match="cannot be set when copying"):
        _copy(use_cases, mock_gateway, _source_project(), pixel_labeling=True)

    mock_gateway.create_project.assert_not_called()


def test_asking_for_pixel_labeling_on_a_demo_project_is_refused(use_cases, mock_gateway):
    """`input_type` is None there too, so the mode used to reach the wire on a demo project."""
    with pytest.raises(ValueError, match="cannot be set when creating a project from a demo"):
        use_cases.create_project(
            title="a demo project",
            description="",
            compliance_tags=None,
            from_demo_project="DEMO_COMPUTER_VISION_TUTORIAL",
            pixel_labeling=True,
        )

    mock_gateway.create_project.assert_not_called()


def test_asking_for_pixel_labeling_on_a_non_geospatial_project_is_refused(use_cases, mock_gateway):
    with pytest.raises(ValueError, match="only available for `GEOSPATIAL`"):
        use_cases.create_project(
            title="an image project",
            description="",
            compliance_tags=None,
            from_demo_project=None,
            input_type="IMAGE",
            json_interface={"jobs": {}},
            pixel_labeling=True,
        )

    mock_gateway.create_project.assert_not_called()


def test_creating_a_project_forwards_the_mode(use_cases, mock_gateway):
    use_cases.create_project(
        title="a project",
        description="",
        compliance_tags=None,
        from_demo_project=None,
        input_type="GEOSPATIAL",
        json_interface={"jobs": {}},
        pixel_labeling=True,
    )

    assert mock_gateway.create_project.call_args.kwargs["pixel_labeling"] is True
