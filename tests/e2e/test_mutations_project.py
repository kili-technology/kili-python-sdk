import pytest

from kili.client import Kili


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
        title="test_mutations_project",
        description="test_mutations_project",
    )

    yield project

    kili.delete_project(project["id"])


def test_update_properties_in_project(kili, src_project):
    ret = kili.update_properties_in_project(
        project_id=src_project["id"], review_coverage=42, instructions="todo", can_skip_asset=True
    )
    assert ret == {
        "id": src_project["id"],
        "reviewCoverage": 42,
        "instructions": "todo",
        "canSkipAsset": True,
    }


def test_append_to_roles(kili: Kili, src_project):
    added_user = kili.append_to_roles(
        src_project["id"], user_email="test_append_to_roles@kili-technology.com", role="LABELER"
    )

    mutated_user = kili.append_to_roles(
        src_project["id"], user_email="test_append_to_roles@kili-technology.com", role="REVIEWER"
    )

    assert added_user["role"] == "LABELER"
    assert mutated_user["role"] == "REVIEWER"

    assert (
        added_user["user"]["email"]
        == mutated_user["user"]["email"]
        == "test_append_to_roles@kili-technology.com"
    )
    assert (
        added_user["user"]["id"] is not None
        and mutated_user["user"]["id"] == added_user["user"]["id"]
    )
