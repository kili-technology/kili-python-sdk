"""
Helpers for the project queries.
"""

from typing import List, Tuple


def get_project_metrics(project: dict) -> Tuple[List[list], List[list], List[list]]:
    """Get metrics for a project.

    Args:
        project: a project with its statistics fields

    Return:
        info, dataset_metrics, quality_metrics: arrays that contain
        the project infos and progress metrics
    """
    progress = round(
        (1 - project['numberOfRemainingAssets'] / project['numberOfAssets']) * 100, 1)

    infos = [['Title', project['title']], [
        'Description', project['description']]]
    dataset_metrics = [['Total number of assets', project['numberOfAssets']],
                       ['Number of remaining assets',
                           project['numberOfRemainingAssets']],
                       ['Skipped assets', project['numberOfAssetsWithSkippedLabels']],
                       ['Progress', str(progress)+'%']]
    quality_metrics = [['Project consensus', project['consensusMark'] or 'N/A'],
                       ['Project honeypot', project['honeypotMark'] or 'N/A'],
                       ['Number of reviewed assets',
                        project['numberOfReviewedAssets']],
                       ['Number of open issues', project['numberOfOpenIssues']],
                       ['Number of solved issues',
                        project['numberOfSolvedIssues']],
                       ['Number of open questions',
                        project['numberOfOpenQuestions']],
                       ['Number of solved questions', project['numberOfSolvedQuestions']]]
    return infos, dataset_metrics, quality_metrics
