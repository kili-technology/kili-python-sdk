"""Example script for recording legacy API requests.

This script demonstrates how to record requests from the legacy Kili client
for later replay against v2 implementations.
"""

import os

# Add parent directory to path for imports
import sys
from pathlib import Path

from kili.client import Kili

sys.path.insert(0, str(Path(__file__).parent.parent))

from recorder import RequestRecorder  # noqa: E402


def main():
    """Record sample legacy API requests."""
    # Initialize legacy client
    api_key = os.getenv("KILI_API_KEY")
    if not api_key:
        print("Error: KILI_API_KEY environment variable not set")
        return

    kili = Kili(api_key=api_key)

    # Initialize recorder
    recordings_dir = Path(__file__).parent / "recordings"
    recorder = RequestRecorder(storage_dir=recordings_dir)

    # Get a test project (use your actual project ID)
    project_id = os.getenv("KILI_TEST_PROJECT_ID")
    if not project_id:
        # Try to get first project
        projects = list(kili.projects(first=1))
        if projects:
            project_id = projects[0]["id"]
        else:
            print("No projects found. Please set KILI_TEST_PROJECT_ID")
            return

    print(f"Recording requests for project: {project_id}")

    # Record: count_assets
    print("\nRecording: count_assets")
    try:
        response = kili.count_assets(project_id=project_id)
        recorder.record(
            method_name="count_assets",
            kwargs={"project_id": project_id},
            response=response,
            context={"project_id": project_id},
        )
        print(f"  ✓ Recorded: {response} assets")
    except Exception as e:  # pylint: disable=broad-except
        recorder.record(
            method_name="count_assets",
            kwargs={"project_id": project_id},
            exception=e,
            context={"project_id": project_id},
        )
        print(f"  ✗ Error: {e}")

    # Record: assets (list)
    print("\nRecording: assets (first 10)")
    try:
        response = list(kili.assets(project_id=project_id, first=10))
        recorder.record(
            method_name="assets",
            kwargs={"project_id": project_id, "first": 10},
            response=response,
            context={"project_id": project_id},
        )
        print(f"  ✓ Recorded: {len(response)} assets")
    except Exception as e:  # pylint: disable=broad-except
        recorder.record(
            method_name="assets",
            kwargs={"project_id": project_id, "first": 10},
            exception=e,
            context={"project_id": project_id},
        )
        print(f"  ✗ Error: {e}")

    # Record: assets with pagination
    print("\nRecording: assets with pagination (skip 5, first 5)")
    try:
        response = list(kili.assets(project_id=project_id, skip=5, first=5))
        recorder.record(
            method_name="assets",
            kwargs={"project_id": project_id, "skip": 5, "first": 5},
            response=response,
            context={"project_id": project_id},
        )
        print(f"  ✓ Recorded: {len(response)} assets")
    except Exception as e:  # pylint: disable=broad-except
        recorder.record(
            method_name="assets",
            kwargs={"project_id": project_id, "skip": 5, "first": 5},
            exception=e,
            context={"project_id": project_id},
        )
        print(f"  ✗ Error: {e}")

    # Record: count_labels
    print("\nRecording: count_labels")
    try:
        response = kili.count_labels(project_id=project_id)
        recorder.record(
            method_name="count_labels",
            kwargs={"project_id": project_id},
            response=response,
            context={"project_id": project_id},
        )
        print(f"  ✓ Recorded: {response} labels")
    except Exception as e:  # pylint: disable=broad-except
        recorder.record(
            method_name="count_labels",
            kwargs={"project_id": project_id},
            exception=e,
            context={"project_id": project_id},
        )
        print(f"  ✗ Error: {e}")

    # Record: projects (list)
    print("\nRecording: projects (first 5)")
    try:
        response = list(kili.projects(first=5))
        recorder.record(
            method_name="projects",
            kwargs={"first": 5},
            response=response,
        )
        print(f"  ✓ Recorded: {len(response)} projects")
    except Exception as e:  # pylint: disable=broad-except
        recorder.record(
            method_name="projects",
            kwargs={"first": 5},
            exception=e,
        )
        print(f"  ✗ Error: {e}")

    # Save recordings
    print("\nSaving recordings...")
    filepath = recorder.save("legacy_api_requests", format="json")
    print(f"  ✓ Saved to: {filepath}")

    # Print summary
    print("\nRecording Summary:")
    summary = recorder.get_summary()
    print(f"  Total recordings: {summary['total_recordings']}")
    print("  Methods recorded:")
    for method, stats in summary["methods"].items():
        print(
            f"    - {method}: {stats['count']} calls ({stats['success']} success, {stats['errors']} errors)"
        )


if __name__ == "__main__":
    main()
