"""CLI's project member list subcommand."""

from typing import Optional

import click
import pandas as pd
from tabulate import tabulate

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.core.graphql.operations.project_user.queries import (
    ProjectUserQuery,
    ProjectUserWhere,
)
from kili.entrypoints.cli.common_args import Arguments, Options
from kili.entrypoints.cli.helpers import get_kili_client

ROLE_ORDER = {v: i for i, v in enumerate(["ADMIN", "TEAM_MANAGER", "REVIEWER", "LABELER"])}


@click.command(name="list")
@Options.api_key
@Options.endpoint
@Arguments.project_id
@Options.tablefmt
def list_members(api_key: Optional[str], endpoint: Optional[str], project_id: str, tablefmt: str):
    """List the members of the project.

    \b
    !!! Examples
        ```
        kili project member list <project_id> --stdout-format pretty
        ```
    """
    kili = get_kili_client(api_key=api_key, api_endpoint=endpoint)
    members_list = list(
        ProjectUserQuery(kili.graphql_client, kili.http_client)(
            where=ProjectUserWhere(project_id=project_id),
            fields=[
                "role",
                "activated",
                "user.email",
                "user.id",
                "user.firstname",
                "user.lastname",
                "user.organization.name",
            ],
            options=QueryOptions(disable_tqdm=True),
        )
    )
    members = pd.DataFrame(members_list)
    # pylint: disable=line-too-long
    members = pd.concat([members.drop(["user"], axis=1), members["user"].apply(pd.Series)], axis=1)  # type: ignore
    members = pd.concat(
        [members.drop(["organization"], axis=1), members["organization"].apply(pd.Series)],
        axis=1,
    )
    members = members.loc[members["activated"]]
    members = members.rename(
        columns={"role": "ROLE", "email": "EMAIL", "id": "ID", "name": "ORGANIZATION"},
    )
    members["NAME"] = members["firstname"].str.title() + " " + members["lastname"].str.title()
    members = members.sort_values(
        by=["ROLE", "lastname"],
        ascending=True,
        key=lambda column: column.map(ROLE_ORDER) if column.name == "ROLE" else column,
    )
    members = members[["ROLE", "NAME", "EMAIL", "ID", "ORGANIZATION"]]
    print(tabulate(members, headers="keys", tablefmt=tablefmt, showindex=False))  # type: ignore
