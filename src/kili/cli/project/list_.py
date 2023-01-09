"""
    CLI's project list subcommand
"""

from typing import Dict, List, Optional, cast

import click
import numpy as np
import pandas as pd
from tabulate import tabulate

from kili.cli.common_args import Options
from kili.cli.helpers import get_kili_client
from kili.graphql import QueryOptions
from kili.graphql.operations.project.queries import ProjectQuery, ProjectWhere


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
    """
    List your projects

    \b
    !!! Examples
        ```
        kili project list --max 10 --stdout-format pretty
        ```

    """
    kili = get_kili_client(api_key=api_key, api_endpoint=endpoint)
    projects = cast(
        List[Dict],
        ProjectQuery(kili.auth.client)(
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
        lambda x: round((1 - x["numberOfRemainingAssets"] / x["numberOfAssets"]) * 100, 1)
        if x["numberOfAssets"] != 0
        else np.nan,
        axis=1,
    )

    # Add '%' to PROGRESS if PROGRESS is not nan
    projects["PROGRESS"] = [
        (str(progress) + "%") if progress >= 0 else progress for progress in projects["progress"]
    ]
    # If description or title has more than 50 characters, truncate after 47 and add '...'
    projects["DESCRIPTION"] = [
        (description[:47] + "...").replace("\n", "") if len(description) > 50 else description
        for description in projects["description"]
    ]
    projects["TITLE"] = [
        (title[:47] + "...") if len(title) > 50 else title for title in projects["title"]
    ]
    projects["ID"] = projects["id"]

    projects = projects[["TITLE", "ID", "PROGRESS", "DESCRIPTION"]]
    print(
        tabulate(
            projects,
            headers="keys",
            tablefmt=tablefmt,
            showindex=False,
            colalign=("left", "left", "right", "left"),
        )
    )
