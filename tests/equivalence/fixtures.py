"""Test fixtures for equivalence testing.

This module provides common test fixtures and data for equivalence tests.
"""

from typing import List

from .harness import TestCase

# Asset-related test cases
ASSET_TEST_CASES: List[TestCase] = [
    TestCase(
        name="count_assets_basic",
        method_name="count_assets",
        legacy_method_path="count_assets",
        v2_method_path="assets.count",
        kwargs={"project_id": "test_project_id"},
        description="Count all assets in a project",
    ),
    TestCase(
        name="count_assets_with_status_filter",
        method_name="count_assets",
        legacy_method_path="count_assets",
        v2_method_path="assets.count",
        kwargs={
            "project_id": "test_project_id",
            "status_in": ["TODO", "ONGOING"],
        },
        description="Count assets filtered by status",
    ),
    TestCase(
        name="assets_list_basic",
        method_name="assets",
        legacy_method_path="assets",
        v2_method_path="assets.list",
        kwargs={
            "project_id": "test_project_id",
            "first": 10,
        },
        description="List first 10 assets",
    ),
    TestCase(
        name="assets_list_with_pagination",
        method_name="assets",
        legacy_method_path="assets",
        v2_method_path="assets.list",
        kwargs={
            "project_id": "test_project_id",
            "first": 50,
            "skip": 100,
        },
        description="List assets with pagination",
    ),
    TestCase(
        name="assets_list_with_external_id_filter",
        method_name="assets",
        legacy_method_path="assets",
        v2_method_path="assets.list",
        kwargs={
            "project_id": "test_project_id",
            "external_id_contains": ["image", "photo"],
        },
        description="List assets filtered by external ID",
    ),
    TestCase(
        name="assets_list_with_metadata_filter",
        method_name="assets",
        legacy_method_path="assets",
        v2_method_path="assets.list",
        kwargs={
            "project_id": "test_project_id",
            "metadata_where": {"camera": "drone"},
        },
        description="List assets filtered by metadata",
    ),
]


# Label-related test cases
LABEL_TEST_CASES: List[TestCase] = [
    TestCase(
        name="count_labels_basic",
        method_name="count_labels",
        legacy_method_path="count_labels",
        v2_method_path="labels.count",
        kwargs={"project_id": "test_project_id"},
        description="Count all labels in a project",
    ),
    TestCase(
        name="count_labels_by_asset",
        method_name="count_labels",
        legacy_method_path="count_labels",
        v2_method_path="labels.count",
        kwargs={
            "project_id": "test_project_id",
            "asset_id": "test_asset_id",
        },
        description="Count labels for a specific asset",
    ),
    TestCase(
        name="labels_list_basic",
        method_name="labels",
        legacy_method_path="labels",
        v2_method_path="labels.list",
        kwargs={
            "project_id": "test_project_id",
            "first": 10,
        },
        description="List first 10 labels",
    ),
    TestCase(
        name="labels_list_by_author",
        method_name="labels",
        legacy_method_path="labels",
        v2_method_path="labels.list",
        kwargs={
            "project_id": "test_project_id",
            "author_in": ["user1@example.com"],
        },
        description="List labels filtered by author",
    ),
]


# Project-related test cases
PROJECT_TEST_CASES: List[TestCase] = [
    TestCase(
        name="count_projects_basic",
        method_name="count_projects",
        legacy_method_path="count_projects",
        v2_method_path="projects.count",
        kwargs={},
        description="Count all projects",
    ),
    TestCase(
        name="count_projects_archived",
        method_name="count_projects",
        legacy_method_path="count_projects",
        v2_method_path="projects.count",
        kwargs={"archived": True},
        description="Count archived projects",
    ),
    TestCase(
        name="projects_list_basic",
        method_name="projects",
        legacy_method_path="projects",
        v2_method_path="projects.list",
        kwargs={"first": 10},
        description="List first 10 projects",
    ),
    TestCase(
        name="projects_list_by_input_type",
        method_name="projects",
        legacy_method_path="projects",
        v2_method_path="projects.list",
        kwargs={
            "input_type_in": ["IMAGE", "VIDEO"],
        },
        description="List projects filtered by input type",
    ),
]


# User-related test cases
USER_TEST_CASES: List[TestCase] = [
    TestCase(
        name="count_users_basic",
        method_name="count_users",
        legacy_method_path="count_users",
        v2_method_path="users.count",
        kwargs={"organization_id": "test_org_id"},
        description="Count all users in organization",
    ),
    TestCase(
        name="users_list_basic",
        method_name="users",
        legacy_method_path="users",
        v2_method_path="users.list",
        kwargs={
            "organization_id": "test_org_id",
            "first": 10,
        },
        description="List first 10 users",
    ),
]


# Error scenario test cases
ERROR_TEST_CASES: List[TestCase] = [
    TestCase(
        name="count_assets_invalid_project",
        method_name="count_assets",
        legacy_method_path="count_assets",
        v2_method_path="assets.count",
        kwargs={"project_id": "non_existent_project"},
        description="Count assets with invalid project ID (should raise error)",
    ),
    TestCase(
        name="assets_list_invalid_pagination",
        method_name="assets",
        legacy_method_path="assets",
        v2_method_path="assets.list",
        kwargs={
            "project_id": "test_project_id",
            "first": -1,  # Invalid pagination
        },
        description="List assets with invalid pagination (should raise error)",
    ),
]


# Comprehensive test suite combining all test cases
ALL_TEST_CASES = (
    ASSET_TEST_CASES + LABEL_TEST_CASES + PROJECT_TEST_CASES + USER_TEST_CASES + ERROR_TEST_CASES
)


def get_crud_test_cases(entity: str) -> List[TestCase]:
    """Get CRUD test cases for a specific entity.

    Args:
        entity: Entity name ("asset", "label", "project", or "user")

    Returns:
        List of test cases for CRUD operations
    """
    entity_lower = entity.lower()

    if entity_lower == "asset":
        return ASSET_TEST_CASES
    if entity_lower == "label":
        return LABEL_TEST_CASES
    if entity_lower == "project":
        return PROJECT_TEST_CASES
    if entity_lower == "user":
        return USER_TEST_CASES
    raise ValueError(f"Unknown entity: {entity}")


def get_test_cases_by_category(category: str) -> List[TestCase]:
    """Get test cases by category.

    Args:
        category: Category name ("crud", "pagination", "filtering", "error")

    Returns:
        List of test cases in the category
    """
    if category == "crud":
        return ALL_TEST_CASES
    if category == "pagination":
        return [tc for tc in ALL_TEST_CASES if "pagination" in tc.description.lower()]
    if category == "filtering":
        return [tc for tc in ALL_TEST_CASES if "filter" in tc.description.lower()]
    if category == "error":
        return ERROR_TEST_CASES
    raise ValueError(f"Unknown category: {category}")
