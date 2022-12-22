import pytest

from kili.client import Kili
from kili.services.copy_project import CopyProject


@pytest.mark.parametrize(
    "existing_projects, expected",
    [
        ([{"title": "Title"}], "Title (copy)"),
        ([{"title": "Title"}, {"title": "Title (copy)"}], "Title (copy 1)"),
        ([{"title": "Title (copy)"}, {"title": "Title (copy 1)"}], "Title (copy 2)"),
    ],
)
def test__generate_project_title(existing_projects, expected, mocker):
    kili = Kili()
    copy_proj = CopyProject(kili.auth)
    mocker.patch.object(copy_proj, "projects", return_value=existing_projects)
    assert copy_proj._generate_project_title("Title") == expected
