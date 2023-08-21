"""Test copy project service."""
import pytest

from kili.services.copy_project import ProjectCopier


@pytest.mark.parametrize(
    "existing_projects, expected",
    [
        ([{"title": "Title"}], "Title (copy)"),
        ([{"title": "Title"}, {"title": "Title (copy)"}], "Title (copy 1)"),
        ([{"title": "Title (copy)"}, {"title": "Title (copy 1)"}], "Title (copy 2)"),
    ],
)
def test__generate_project_title(existing_projects, expected, mocker):
    kili = mocker.MagicMock()
    kili.projects.return_value = existing_projects
    copy_proj = ProjectCopier(kili)  # type: ignore
    assert copy_proj._generate_project_title("Title") == expected
