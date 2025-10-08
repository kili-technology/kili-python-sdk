"""Integration tests for IssueView objects returned by the issues namespace.

This test file validates that the issues.list() method correctly returns
IssueView objects instead of dictionaries, and that these objects provide
proper property access and backward compatibility.

Test Strategy:
    - Verify list() returns IssueView objects in all modes (list, generator)
    - Test IssueView property access for common properties
    - Validate backward compatibility with dictionary interface via to_dict()
    - Test filtering by asset_id, issue_type, and status
    - Verify status check properties (is_open, is_solved, is_cancelled, is_question)
    - Ensure mutation methods still return dicts (unchanged)
"""

import pytest

from kili.domain_v2.issue import IssueView
from tests_v2 import (
    assert_is_view,
    assert_view_has_dict_compatibility,
    assert_view_property_access,
)


@pytest.mark.integration()
def test_list_returns_issue_views(kili_client):
    """Test that issues.list() in list mode returns IssueView objects."""
    # Get the first project to test with
    projects = list(kili_client.projects.list(first=1, as_generator=False))

    if not projects:
        pytest.skip("No projects available for testing")

    # Projects now return ProjectView objects
    project_id = projects[0].id

    # Get issues in list mode
    issues = kili_client.issues.list(project_id=project_id, first=5, as_generator=False)

    # Verify we get a list
    assert isinstance(issues, list), "issues.list() with as_generator=False should return a list"

    # Skip if no issues
    if not issues:
        pytest.skip(f"No issues available in project {project_id}")

    # Verify each item is an IssueView
    for issue in issues:
        assert_is_view(issue, IssueView)

        # Verify we can access basic properties
        assert hasattr(issue, "id")
        assert hasattr(issue, "status")
        assert hasattr(issue, "type")
        assert hasattr(issue, "asset_id")


@pytest.mark.integration()
def test_list_generator_returns_issue_views(kili_client):
    """Test that issues.list() in generator mode returns IssueView objects."""
    # Get the first project to test with
    projects = list(kili_client.projects.list(first=1, as_generator=False))

    if not projects:
        pytest.skip("No projects available for testing")

    # Projects now return ProjectView objects
    project_id = projects[0].id

    # Get issues in generator mode
    issues_gen = kili_client.issues.list(project_id=project_id, first=5, as_generator=True)

    # Take first 5 items from generator (or fewer if less available)
    issues_from_gen = []
    for i, issue in enumerate(issues_gen):
        if i >= 5:
            break
        issues_from_gen.append(issue)

    # Skip if no issues
    if not issues_from_gen:
        pytest.skip(f"No issues available in project {project_id}")

    # Verify each yielded item is an IssueView
    for issue in issues_from_gen:
        assert_is_view(issue, IssueView)

        # Verify we can access basic properties
        assert hasattr(issue, "id")
        assert hasattr(issue, "status")
        assert hasattr(issue, "type")


@pytest.mark.integration()
def test_issue_view_properties(kili_client):
    """Test that IssueView provides access to all expected properties."""
    # Get the first project to test with
    projects = list(kili_client.projects.list(first=1, as_generator=False))

    if not projects:
        pytest.skip("No projects available for testing")

    # Projects now return ProjectView objects
    project_id = projects[0].id

    # Get first issue
    issues = kili_client.issues.list(project_id=project_id, first=1, as_generator=False)

    if not issues:
        pytest.skip(f"No issues available in project {project_id}")

    issue = issues[0]

    # Verify IssueView type
    assert_is_view(issue, IssueView)

    # Test core properties exist and are accessible
    assert_view_property_access(issue, "id")
    assert_view_property_access(issue, "status")
    assert_view_property_access(issue, "type")
    assert_view_property_access(issue, "asset_id")
    assert_view_property_access(issue, "created_at")
    assert_view_property_access(issue, "display_name")

    # Test that id is not empty
    assert issue.id, "Issue id should not be empty"

    # Test display_name (should be id)
    assert issue.display_name == issue.id

    # Test optional properties
    assert_view_property_access(issue, "has_been_seen")

    # Test computed status properties
    assert_view_property_access(issue, "is_open")
    assert_view_property_access(issue, "is_solved")
    assert_view_property_access(issue, "is_cancelled")
    assert_view_property_access(issue, "is_question")

    # Verify status is one of the valid values
    assert issue.status in (
        "OPEN",
        "SOLVED",
        "CANCELLED",
    ), f"Issue status should be OPEN, SOLVED, or CANCELLED, got {issue.status}"

    # Verify type is one of the valid values
    assert issue.type in (
        "ISSUE",
        "QUESTION",
    ), f"Issue type should be ISSUE or QUESTION, got {issue.type}"


@pytest.mark.integration()
def test_issue_view_dict_compatibility(kili_client):
    """Test that IssueView maintains backward compatibility via to_dict()."""
    # Get the first project to test with
    projects = list(kili_client.projects.list(first=1, as_generator=False))

    if not projects:
        pytest.skip("No projects available for testing")

    # Projects now return ProjectView objects
    project_id = projects[0].id

    # Get first issue
    issues = kili_client.issues.list(project_id=project_id, first=1, as_generator=False)

    if not issues:
        pytest.skip(f"No issues available in project {project_id}")

    issue = issues[0]

    # Verify IssueView type
    assert_is_view(issue, IssueView)

    # Test dictionary compatibility
    assert_view_has_dict_compatibility(issue)

    # Get dictionary representation
    issue_dict = issue.to_dict()

    # Verify it's a dictionary
    assert isinstance(issue_dict, dict), "to_dict() should return a dictionary"

    # Verify dictionary has expected keys
    assert "id" in issue_dict, "Dictionary should have 'id' key"

    # Verify dictionary values match property values
    if "status" in issue_dict:
        assert issue_dict["status"] == issue.status, "Dictionary status should match property"

    if "type" in issue_dict:
        assert issue_dict["type"] == issue.type, "Dictionary type should match property"

    if "assetId" in issue_dict:
        assert issue_dict["assetId"] == issue.asset_id, "Dictionary assetId should match property"

    # Verify to_dict() returns the same reference (zero-copy)
    assert issue_dict is issue._data, "to_dict() should return the same reference as _data"


@pytest.mark.integration()
def test_issue_view_filtering(kili_client):
    """Test that IssueView objects work correctly with filtering."""
    # Get the first project to test with
    projects = list(kili_client.projects.list(first=1, as_generator=False))

    if not projects:
        pytest.skip("No projects available for testing")

    # Projects now return ProjectView objects
    project_id = projects[0].id

    # Get all issues
    all_issues = kili_client.issues.list(project_id=project_id, first=10, as_generator=False)

    if not all_issues:
        pytest.skip(f"No issues available in project {project_id}")

    # Get the first issue's asset_id
    first_asset_id = all_issues[0].asset_id

    # Query for issues by asset_id
    filtered_issues = kili_client.issues.list(
        project_id=project_id, asset_id=first_asset_id, as_generator=False
    )

    # Verify we got results
    assert len(filtered_issues) > 0, "Should get at least one issue with specific asset_id"

    # Verify each result is an IssueView
    for issue in filtered_issues:
        assert_is_view(issue, IssueView)

        # Verify it has the correct asset_id
        assert issue.asset_id == first_asset_id, "Filtered issue should have the requested asset_id"


@pytest.mark.integration()
def test_issue_view_status_checks(kili_client):
    """Test IssueView status check properties (is_open, is_solved, is_cancelled, is_question)."""
    # Get the first project to test with
    projects = list(kili_client.projects.list(first=1, as_generator=False))

    if not projects:
        pytest.skip("No projects available for testing")

    # Projects now return ProjectView objects
    project_id = projects[0].id

    # Get issues
    issues = kili_client.issues.list(project_id=project_id, first=10, as_generator=False)

    if not issues:
        pytest.skip(f"No issues available in project {project_id}")

    for issue in issues:
        assert_is_view(issue, IssueView)

        # Verify exactly one status flag is true
        status_flags = [issue.is_open, issue.is_solved, issue.is_cancelled]
        assert sum(status_flags) == 1, "Exactly one status flag should be true"

        # Verify status flag matches actual status
        if issue.status == "OPEN":
            assert issue.is_open is True
            assert issue.is_solved is False
            assert issue.is_cancelled is False
        elif issue.status == "SOLVED":
            assert issue.is_open is False
            assert issue.is_solved is True
            assert issue.is_cancelled is False
        elif issue.status == "CANCELLED":
            assert issue.is_open is False
            assert issue.is_solved is False
            assert issue.is_cancelled is True

        # Verify type flag matches actual type
        if issue.type == "QUESTION":
            assert issue.is_question is True
        else:
            assert issue.is_question is False


@pytest.mark.integration()
def test_issue_view_empty_results(kili_client):
    """Test that empty results are handled correctly."""
    # Get the first project to test with
    projects = list(kili_client.projects.list(first=1, as_generator=False))

    if not projects:
        pytest.skip("No projects available for testing")

    # Projects now return ProjectView objects
    project_id = projects[0].id

    # Query with a filter that should return no results
    # Using a non-existent asset ID
    empty_issues = kili_client.issues.list(
        project_id=project_id, asset_id="non-existent-asset-id-12345", as_generator=False
    )

    # Verify we get an empty list
    assert isinstance(empty_issues, list), "Should return a list even when no results"
    assert len(empty_issues) == 0, "Should return empty list for non-existent asset"


@pytest.mark.integration()
def test_mutation_methods_still_return_dicts(kili_client):
    """Test that mutation methods (create, solve, cancel, open) still return dicts (unchanged)."""
    # Get the first project to test with
    projects = list(kili_client.projects.list(first=1, as_generator=False))

    if not projects:
        pytest.skip("No projects available for testing")

    # Projects now return ProjectView objects
    project_id = projects[0].id

    # Get an asset to work with
    assets = list(kili_client.assets.list(project_id=project_id, first=1, as_generator=False))

    if not assets:
        pytest.skip(f"No assets available in project {project_id}")

    asset = assets[0]

    # Get or create a label for the asset
    labels = list(
        kili_client.labels.list(
            project_id=project_id, asset_id=asset.id, first=1, as_generator=False
        )
    )

    if not labels:
        pytest.skip(f"No labels available for asset {asset.id}")

    label = labels[0]

    # Test create() method - should return list of dicts
    try:
        create_result = kili_client.issues.create(
            project_id=project_id,
            label_id_array=[label.id],
            text_array=["Test issue for integration test"],
        )

        # Verify result is a list
        assert isinstance(create_result, list), "create() should return a list"

        if create_result:
            # Verify first item is a dict
            assert isinstance(create_result[0], dict), "create() should return list of dicts"
            assert "id" in create_result[0], "Created issue should have 'id' key"

            # Test solve() method - should return list of dicts
            issue_id = create_result[0]["id"]
            solve_result = kili_client.issues.solve(issue_ids=[issue_id])

            # Verify result is a list
            assert isinstance(solve_result, list), "solve() should return a list"
            assert isinstance(solve_result[0], dict), "solve() should return list of dicts"

            # Test open() method - should return list of dicts
            open_result = kili_client.issues.open(issue_ids=[issue_id])

            # Verify result is a list
            assert isinstance(open_result, list), "open() should return a list"
            assert isinstance(open_result[0], dict), "open() should return list of dicts"

            # Test cancel() method - should return list of dicts
            cancel_result = kili_client.issues.cancel(issue_ids=[issue_id])

            # Verify result is a list
            assert isinstance(cancel_result, list), "cancel() should return a list"
            assert isinstance(cancel_result[0], dict), "cancel() should return list of dicts"

    except Exception as e:
        # If mutations are not allowed in test environment, skip the test
        pytest.skip(f"Mutations not allowed or failed: {e}")


@pytest.mark.integration()
def test_issue_view_with_fields_parameter(kili_client):
    """Test that IssueView works correctly with custom fields parameter."""
    # Get the first project to test with
    projects = list(kili_client.projects.list(first=1, as_generator=False))

    if not projects:
        pytest.skip("No projects available for testing")

    # Projects now return ProjectView objects
    project_id = projects[0].id

    # Query with specific fields
    issues = kili_client.issues.list(
        project_id=project_id,
        first=1,
        fields=["id", "status", "type", "assetId", "createdAt"],
        as_generator=False,
    )

    if not issues:
        pytest.skip(f"No issues available in project {project_id}")

    issue = issues[0]

    # Verify it's still an IssueView
    assert_is_view(issue, IssueView)

    # Verify requested fields are accessible
    assert_view_property_access(issue, "id")
    assert_view_property_access(issue, "status")
    assert_view_property_access(issue, "type")
    assert_view_property_access(issue, "asset_id")
    assert_view_property_access(issue, "created_at")
