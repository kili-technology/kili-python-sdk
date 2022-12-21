import pytest

from kili.client import Kili
from kili.services.copy_project import CopyProject


@pytest.fixture
def kili() -> Kili:
    return Kili()


@pytest.fixture()
def src_project(kili):
    interface = {
        "jobs": {
            "DETECTION": {
                "mlTask": "OBJECT_DETECTION",
                "tools": ["rectangle"],
                "instruction": "Is there a defect ? Where ? What kind ?",
                "required": 0,
                "isChild": False,
                "content": {
                    "categories": {
                        "DEFECT_CLASS_1": {"name": "defect of class 1"},
                        "DEFECT_CLASS_2": {"name": "defect of class 2"},
                        "DEFECT_CLASS_3": {"name": "defect of class 3"},
                        "DEFECT_CLASS_4": {"name": "defect of class 4"},
                    },
                    "input": "radio",
                },
            }
        }
    }

    project = kili.create_project(
        input_type="IMAGE",
        json_interface=interface,
        title="Test for ML-755",
        description="Test for ML-755",
    )

    kili.update_properties_in_project(
        project_id=project["id"],
        consensus_tot_coverage=0,
        min_consensus_size=1,
        review_coverage=0,
    )

    yield project

    kili.delete_project(project["id"])


def test_copy_project_e2e_no_assets_no_labels(kili, src_project):
    new_proj_id = kili.copy_project(
        from_project_id=src_project["id"], description="new description"
    )

    proj_fields = (
        CopyProject.FIELDS_PROJECT
        + CopyProject.FIELDS_QUALITY_SETTINGS
        + CopyProject.FIELDS_JSON_INTERFACE
    )

    src_proj = kili.projects(project_id=src_project["id"], fields=proj_fields)[0]  # type: ignore
    new_proj = kili.projects(project_id=new_proj_id, fields=proj_fields)[0]  # type: ignore

    members_src = kili.project_users(
        project_id=src_proj["id"],
        fields=["activated", "role", "user.email", "invitationStatus"],
    )
    members_new = kili.project_users(
        project_id=new_proj_id,
        fields=["activated", "role", "user.email", "invitationStatus"],
    )

    kili.delete_project(new_proj_id)

    assert new_proj["title"].startswith(src_proj["title"])
    assert "copy" in new_proj["title"]
    assert new_proj["description"] == "new description"
    assert new_proj["inputType"] == src_proj["inputType"]
    assert new_proj["jsonInterface"] == src_proj["jsonInterface"]

    for field_name in CopyProject.FIELDS_QUALITY_SETTINGS:
        assert new_proj[field_name] == src_proj[field_name]

    assert members_src == members_new
