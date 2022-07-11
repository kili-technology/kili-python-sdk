"""CLI's project member list subcommand"""

from typing import Dict, List, Optional, cast
import click

import pandas as pd
from tabulate import tabulate

from kili.client import Kili
from kili.cli.common_args import Options

ROLE_ORDER = {
    v: i for i, v in enumerate(["ADMIN", "TEAM_MANAGER", "REVIEWER", "LABELER"])
}


def role_order(col: pd.Series) -> pd.Series:
    """ordering pandas series by custom role order"""
    out = col
    if col.name == "ROLE":
        out = col.map(ROLE_ORDER)
    return out


@click.command()
@Options.api_key
@Options.endpoint
@click.option('--project-id', type=str, required=True,
              help='Id of the project to list members of')
@Options.tablefmt
def list_members(api_key: Optional[str],
                 endpoint: Optional[str],
                 project_id: str,
                 tablefmt: str):
    """
    List the members of the project

    \b
    !!! Examples
        ```
        kili project member list --project-id <project_id> --stdout-format pretty
        ```

    """
    kili = Kili(api_key=api_key, api_endpoint=endpoint)
    users = cast(
        List[Dict], kili.project_users(
            project_id=project_id,
            fields=[
                'role', 'activated',
                'user.email', 'user.id',
                'user.firstname', 'user.lastname',
                'user.organization.name',
            ],
            disable_tqdm=True))
    users = pd.DataFrame(users)
    users = pd.concat([users.drop(['user'], axis=1),
                      users['user'].apply(pd.Series)], axis=1)
    users = pd.concat([users.drop(['organization'], axis=1),
                      users['organization'].apply(pd.Series)], axis=1)
    users = users.loc[users['activated']]
    users.rename(columns={'role': 'ROLE', 'email': 'EMAIL',
                 'id': 'ID', 'name': 'ORGANIZATION'}, inplace=True)
    users = users.sort_values(
        by=["ROLE", "lastname"],
        ascending=True,
        key=role_order,
    )
    users['NAME'] = users['firstname'].str.title() + ' ' + \
        users['lastname'].str.title()
    users = users[['ROLE', 'NAME', 'EMAIL', 'ID',
                   'ORGANIZATION']]
    print(tabulate(users, headers='keys', tablefmt=tablefmt, showindex=False))
