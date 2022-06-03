"""
Tests for the creation and query of a project from the client
"""

import os
import pytest
from kili.client import Kili
from kili.exceptions import NotFound
from kili.project import Project
from .mutations.test_asset import create_video_project


api_key = os.getenv('KILI_USER_API_KEY')
api_endpoint = os.getenv('KILI_API_ENDPOINT')
kili = Kili(api_key=api_key, api_endpoint=api_endpoint)


class TestGetProject():
    """
    test the get_project function
    """

    def test_get_unexisting_project(self):
        """Test that get_project on a unexisting project_id raises a NotFound Error."""
        with pytest.raises(NotFound):
            kili.get_project('this_project_id_do_not_exist')

    def test_get_existing_project(self, create_video_project):
        """Test that get_project on an existing project_id return a Project with the right id."""
        project_id = create_video_project
        print(project_id)
        project = kili.get_project(project_id)
        assert isinstance(project, Project)
        assert project.project_id == project_id
