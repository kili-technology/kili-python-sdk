"""
Tests for the creation and query of a project from the client
"""


import json

import pytest

from kili.client import Kili
from kili.exceptions import NotFound
from kili.project import Project


def mocked__projects(project_id, **_):
    """Simulates a project call and return an object detection project if
    the given project_id is the one of the fixture."""
    project_fixture = json.load(open("test/fixtures/object_detection_project_fixture.json"))
    if project_id == project_fixture[0]["id"]:
        return json.load(open("test/fixtures/object_detection_project_fixture.json"))
    else:
        return []


class TestGetProject:
    """
    test the get_project function
    """

    def test_get_unexisting_project(self, mocker):
        """Test that get_project on a unexisting project_id raises a NotFound Error."""
        mocker.patch("kili.client.Kili.__init__", return_value=None)
        mocker.patch("kili.client.Kili.projects", side_effect=mocked__projects)
        kili = Kili()
        with pytest.raises(NotFound):
            kili.get_project("this_project_id_do_not_exist")

    def test_get_existing_project(self, mocker):
        """Test that get_project on an existing project_id return a Project with the right id."""
        mocker.patch("kili.client.Kili.__init__", return_value=None)
        mocker.patch("kili.client.Kili.projects", side_effect=mocked__projects)
        kili = Kili()
        project = kili.get_project("cl0wihlop3rwc0mtj9np28ti2")
        assert isinstance(project, Project)
        assert project.project_id == "cl0wihlop3rwc0mtj9np28ti2"
