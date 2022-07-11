"""CLI's project list subcommand"""

from typing import Dict, List, Optional, cast
import click

import numpy as np
import pandas as pd
from tabulate import tabulate

from kili.client import Kili
from kili.cli.common_args import Options

ROLE_ORDER = {
    v: i for i, v in enumerate(["ADMIN", "TEAM_MANAGER", "LABELER", "REVIEWER"])
}


def role_order(col: pd.Series) -> pd.Series:
    out = col
    # apply custom sorting only to column one:
    if col.name == "ROLE":
        out = col.map(ROLE_ORDER)
    # default text sorting is about to be applied
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
        kili project member list --project-id <project_id> --format pretty
        ```

    """
    kili = Kili(api_key=api_key, api_endpoint=endpoint)
    users = kili.project_users(
        project_id=project_id,
        fields=[
            'id', 'role', 'activated',
            'user.email', 'user.id',
            'user.firstname', 'user.lastname',
            'user.organization.name', 'user.organizationRole'
        ]
    )
    users = pd.DataFrame(users)
    users.rename(columns={'id': 'ROLE_ID', 'role': 'ROLE',
                 'activated': 'ACTIVATED'}, inplace=True)
    users = pd.concat([users.drop(['user'], axis=1),
                      users['user'].apply(pd.Series)], axis=1)
    users = pd.concat([users.drop(['organization'], axis=1),
                      users['organization'].apply(pd.Series)], axis=1)
    users['ORGANIZATION'] = users['name']
    users['NAME'] = users['lastname'].str.title() + ' ' + \
        users['firstname'].str.title()
    users.rename(columns={'email': 'EMAIL', 'id': 'ID'}, inplace=True)
    users = users[['ROLE', 'NAME', 'EMAIL', 'ID',
                   'ORGANIZATION', 'ROLE_ID', 'ACTIVATED']]
    users = users.sort_values(
        by=["ROLE", "NAME"],
        ascending=True,
        key=role_order,
    )
    print(tabulate(users, headers='keys', tablefmt=tablefmt, showindex=False))
