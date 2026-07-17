"""Tests for the project workflow gateway common helpers."""

import pytest

from kili.adapters.kili_api_gateway.project_workflow.common import find_step_by_name


def _v3_project() -> dict:
    return {
        "workflowVersion": "V3",
        "steps": [
            {"id": "s-g1-label", "name": "Labeling", "type": "DEFAULT", "stepGroupId": "grp-1"},
            {"id": "s-g1-review", "name": "Review", "type": "REVIEW", "stepGroupId": "grp-1"},
            {"id": "s-g2-label", "name": "Labeling", "type": "DEFAULT", "stepGroupId": "grp-2"},
            {"id": "s-g2-review", "name": "Review", "type": "REVIEW", "stepGroupId": "grp-2"},
        ],
        "stepGroups": [
            {"id": "grp-1", "name": "Group 1"},
            {"id": "grp-2", "name": "Group 2"},
        ],
    }


def _v2_project() -> dict:
    return {
        "workflowVersion": "V2",
        "steps": [
            {"id": "s-label", "name": "Labeling", "type": "DEFAULT", "stepGroupId": None},
            {"id": "s-review", "name": "Review", "type": "REVIEW", "stepGroupId": None},
        ],
        "stepGroups": [],
    }


def test_find_step_by_name_without_group_returns_unique_match():
    step = find_step_by_name(_v2_project(), "Review", None)

    assert step["id"] == "s-review"


def test_find_step_by_name_without_group_missing_step_raises():
    with pytest.raises(ValueError, match="Step 'Missing' not found in project workflow"):
        find_step_by_name(_v2_project(), "Missing", None)


def test_find_step_by_name_without_group_ambiguous_raises():
    with pytest.raises(ValueError, match="Multiple steps named 'Review'"):
        find_step_by_name(_v3_project(), "Review", None)


def test_find_step_by_name_with_group_scopes_to_group():
    step = find_step_by_name(_v3_project(), "Review", "Group 2")

    assert step["id"] == "s-g2-review"


def test_find_step_by_name_with_group_on_v2_raises():
    with pytest.raises(ValueError, match="group_name is only supported on workflow V3 projects"):
        find_step_by_name(_v2_project(), "Review", "Group 1")


def test_find_step_by_name_with_unknown_group_raises():
    with pytest.raises(ValueError, match="Group 'Missing' not found in project workflow"):
        find_step_by_name(_v3_project(), "Review", "Missing")


def test_find_step_by_name_with_step_not_in_group_raises():
    project = _v3_project()
    project["stepGroups"].append({"id": "grp-3", "name": "Group 3"})

    with pytest.raises(ValueError, match="Step 'Review' not found in group 'Group 3'"):
        find_step_by_name(project, "Review", "Group 3")
