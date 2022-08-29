"""CLI's project member list subcommand"""

from typing import Dict, List, Optional, cast

import click
import pandas as pd
from tabulate import tabulate

from kili.cli.common_args import Arguments, Options
from kili.cli.helpers import get_kili_client

ROLE_ORDER = {v: i for i, v in enumerate(["ADMIN", "TEAM_MANAGER", "REVIEWER", "LABELER"])}


@click.command(name="list")
@Options.api_key
@Options.endpoint
@Arguments.project_id
@Options.tablefmt
def list_members(api_key: Optional[str], endpoint: Optional[str], project_id: str, tablefmt: str):
    """
    List the members of the project

    \b
    !!! Examples
        ```
        kili project member list <project_id> --stdout-format pretty
        ```

    """
    kili = get_kili_client(api_key=api_key, api_endpoint=endpoint)
    users = cast(
        List[Dict],
        kili.project_users(
            project_id=project_id,
            fields=[
                "role",
                "activated",
                "user.email",
                "user.id",
                "user.firstname",
                "user.lastname",
                "user.organization.name",
            ],
            disable_tqdm=True,
        ),
    )
    users = pd.DataFrame(users)
    users = pd.concat([users.drop(["user"], axis=1), users["user"].apply(pd.Series)], axis=1)
    users = pd.concat(
        [users.drop(["organization"], axis=1), users["organization"].apply(pd.Series)],
        axis=1,
    )
    users = users.loc[users["activated"]]
    users.rename(
        columns={"role": "ROLE", "email": "EMAIL", "id": "ID", "name": "ORGANIZATION"},
        inplace=True,
    )
    users["NAME"] = users["firstname"].str.title() + " " + users["lastname"].str.title()
    users = users.sort_values(
        by=["ROLE", "lastname"],
        ascending=True,
        key=lambda column: column.map(ROLE_ORDER) if column.name == "ROLE" else column,
    )
    users = users[["ROLE", "NAME", "EMAIL", "ID", "ORGANIZATION"]]
    print(tabulate(users, headers="keys", tablefmt=tablefmt, showindex=False))
