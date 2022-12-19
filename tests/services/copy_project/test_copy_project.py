import json

import pytest

from kili.client import Kili
from kili.exceptions import NotFound
from kili.project import Project
from kili.services.copy_project import CopyProject

# test name copied or set
# test description set
# test json interface copied
# test quality settings copied
# test members properly copied

# quel projet source?
# on peut en créer un

# on fait un test avec un vrai projet sur le staging

# et un qu'on peut mocker pour les assets


def test_copy_project_e2e_no_assets_no_labels():
    project_fixture = json.load(open("tests/fixtures/object_detection_project_fixture.json"))[0]

    kili = Kili()

    src_proj = kili.create_project(
        title=project_fixture["title"],
        description="",
        input_type=project_fixture["inputType"],
        json_interface=project_fixture["jsonInterface"],
    )

    kili.update_properties_in_project(
        project_id=src_proj["id"],
        consensus_tot_coverage=project_fixture["consensusTotCoverage"],
        min_consensus_size=project_fixture["minConsensusSize"],
        review_coverage=project_fixture["reviewCoverage"],
    )

    new_proj_id = kili.copy_project(from_project_id=src_proj["id"], description="new description")

    proj_fields = CopyProject.FIELDS_PROJECT + CopyProject.FIELDS_QUALITY_SETTINGS

    src_proj = kili.projects(project_id=src_proj["id"], fields=proj_fields)[0]  # type: ignore
    new_proj = kili.projects(project_id=new_proj_id, fields=proj_fields)[0]  # type: ignore

    kili.delete_project(src_proj["id"])
    kili.delete_project(new_proj_id)

    assert new_proj["title"].startswith(src_proj["title"])
    assert "copy" in new_proj["title"]
    assert new_proj["description"] == "new description"
    assert new_proj["inputType"] == src_proj["inputType"]
    assert new_proj["jsonInterface"] == src_proj["jsonInterface"]

    for field_name in CopyProject.FIELDS_QUALITY_SETTINGS:
        assert new_proj[field_name] == src_proj[field_name]
