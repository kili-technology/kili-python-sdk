"""CLI's project list subcommand."""

from typing import Optional

import click
import numpy as np
import pandas as pd
from tabulate import tabulate

from kili.core.graphql import QueryOptions
from kili.core.graphql.operations.project.queries import ProjectQuery, ProjectWhere
from kili.entrypoints.cli.common_args import Options
from kili.entrypoints.cli.helpers import get_kili_client


@click.command(name="list")
@Options.api_key
@Options.endpoint
@Options.tablefmt
@click.option(
    "--max",
    "first",
    type=int,
    help="Maximum number of project to display.",
    default=100,
)
def list_projects(api_key: Optional[str], endpoint: Optional[str], tablefmt: str, first: int):
    """List your projects.

    \b
    !!! Examples
        ```
        kili project list --max 10 --stdout-format pretty
        ```
    """
    kili = get_kili_client(api_key=api_key, api_endpoint=endpoint)
    projects = list(
        ProjectQuery(kili.graphql_client, kili.http_client)(
            ProjectWhere(),
            [
                "title",
                "id",
                "description",
                "numberOfAssets",
                "numberOfRemainingAssets",
                "numberOfReviewedAssets",
            ],
            QueryOptions(disable_tqdm=True, first=first),
        ),
    )
    projects = pd.DataFrame(projects)
    projects["progress"] = projects.apply(
        lambda x: (
            round((1 - x["numberOfRemainingAssets"] / x["numberOfAssets"]) * 100, 1)
            if x["numberOfAssets"] != 0
            else np.nan
        ),
        axis=1,
    )

    # Add '%' to PROGRESS if PROGRESS is not nan
    # pylint: disable=line-too-long
    projects["PROGRESS"] = [
        (str(progress) + "%") if progress >= 0 else progress for progress in projects["progress"]  # type: ignore
    ]
    # If description or title has more than 50 characters, truncate after 47 and add '...'
    projects["DESCRIPTION"] = [
        (description[:47] + "...").replace("\n", "") if len(description) > 50 else description
        for description in projects["description"]  # type: ignore
    ]
    # pylint: disable=line-too-long
    projects["TITLE"] = [
        (title[:47] + "...") if len(title) > 50 else title for title in projects["title"]  # type: ignore
    ]
    projects["ID"] = projects["id"]

    projects = projects[["TITLE", "ID", "PROGRESS", "DESCRIPTION"]]
    print(
        tabulate(
            projects,  # type: ignore
            headers="keys",
            tablefmt=tablefmt,
            showindex=False,
            colalign=("left", "left", "right", "left"),
        )
    )
