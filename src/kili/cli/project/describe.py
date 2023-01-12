"""CLI's project describe command"""

from typing import Optional

import click
from tabulate import tabulate

from kili import services
from kili.cli.common_args import Arguments, Options
from kili.cli.helpers import get_kili_client
from kili.queries.project.helpers import get_project_metadata, get_project_metrics


@click.command(name="describe")
@Arguments.project_id
@Options.api_key
@Options.endpoint
def describe_project(api_key: Optional[str], endpoint: Optional[str], project_id: str):
    """Show project description and analytics.
    \b
    !!! Examples
        ```
        kili project describe --project-id <project_id>
        ```
    """
    kili = get_kili_client(api_key=api_key, api_endpoint=endpoint)
    query_fields = [
        "title",
        "id",
        "description",
        "numberOfAssets",
        "numberOfRemainingAssets",
        "numberOfReviewedAssets",
        "numberOfSkippedAssets",
        "honeypotMark",
        "consensusMark",
        "numberOfOpenIssues",
        "numberOfSolvedIssues",
        "numberOfOpenQuestions",
        "numberOfSolvedQuestions",
    ]
    project = services.get_project(kili, project_id, query_fields)
    metadata = get_project_metadata(project, kili.auth.client.endpoint)
    dataset_metrics, quality_metrics = get_project_metrics(project)

    print(tabulate(metadata, tablefmt="plain"), end="\n" * 2)
    print("Dataset KPIs", end="\n" + "-" * len("Dataset KPIs") + "\n")
    print(tabulate(dataset_metrics, tablefmt="plain"), end="\n" * 2)
    print("Quality KPIs", end="\n" + "-" * len("Quality KPIs") + "\n")
    print(tabulate(quality_metrics, tablefmt="plain"))
