"""
Helpers for the project queries.
"""

from typing import List, Tuple


def get_project_url(project_id: str, api_endpoint: str):
    """
    Get the project url from the project id and the api_endpoint

    Args:
        project_id: the project id
        api_endpoint: Kili's API endpoint
    """
    domain = api_endpoint.replace("/api/label/v2/graphql", "")
    return domain + f"/label/projects/{project_id}/"


def get_project_metadata(project: dict, api_endpoint: str) -> List[Tuple]:
    """Get project metadata.

    Args:
        project: a project with its statistics fields

    Return:
        a list of metadata (key, value)
    """
    return [
        ("Title", project["title"]),
        ("Description", project["description"]),
        ("URL", get_project_url(project["id"], api_endpoint)),
    ]


def get_project_metrics(project: dict) -> Tuple[List[Tuple], List[Tuple]]:
    """Get project metrics.

    Args:
        project: a project with its statistics fields

    Return:
        dataset_metrics, quality_metrics: arrays that contain
        the project infos and progress metrics
    """

    if project["numberOfAssets"]:
        progress = round(
            (1 - project["numberOfRemainingAssets"] / project["numberOfAssets"]) * 100,
            1,
        )
    else:
        progress = 0

    dataset_metrics = [
        ("Total number of assets", project["numberOfAssets"]),
        ("Number of remaining assets", project["numberOfRemainingAssets"]),
        ("Skipped assets", project["numberOfSkippedAssets"]),
        ("Progress", str(progress) + "%"),
    ]
    quality_metrics = [
        ("Project consensus", project["consensusMark"] or "N/A"),
        ("Project honeypot", project["honeypotMark"] or "N/A"),
        ("Number of reviewed assets", project["numberOfReviewedAssets"]),
        ("Number of open issues", project["numberOfOpenIssues"]),
        ("Number of solved issues", project["numberOfSolvedIssues"]),
        ("Number of open questions", project["numberOfOpenQuestions"]),
        ("Number of solved questions", project["numberOfSolvedQuestions"]),
    ]
    return dataset_metrics, quality_metrics
