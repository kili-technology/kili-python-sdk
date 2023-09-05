"""CLI's project member add subcommand."""

import warnings
from typing import Iterable, Optional

import click

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.core.graphql.operations.project_user.queries import (
    ProjectUserQuery,
    ProjectUserWhere,
)
from kili.entrypoints.cli.common_args import Arguments, Options, from_csv
from kili.entrypoints.cli.helpers import get_kili_client
from kili.entrypoints.cli.project.member.helpers import (
    check_exclusive_options,
    collect_members_from_csv,
    collect_members_from_emails,
    collect_members_from_project,
)


# pylint: disable=too-many-arguments
@click.command(name="add")
@Options.api_key
@Options.endpoint
@Arguments.emails
@Options.project_id
@Options.role
@from_csv(["email"], ["role"])
@Options.from_project
def add_member(
    api_key: Optional[str],
    endpoint: Optional[str],
    emails: Optional[Iterable[str]],
    project_id: str,
    role: Optional[str],
    csv_path: Optional[str],
    project_id_src: Optional[str],
):
    """Add members to a Kili project.

    Emails can be passed directly as arguments.
    You can provide several emails separated by spaces.

    \b
    !!! Examples
        ```
        kili project member add \\
            --project-id <project_id> \\
            --role REVIEWER \\
            john.doe@test.com jane.doe@test.com
        ```
        ```
        kili project member add \\
            --project-id <project_id> \\
            --from-csv path/to/members.csv
        ```
        ```
        kili project member add \\
            --project-id <project_id> \\
            --from-project <project_id_scr>
        ```
    """
    kili = get_kili_client(api_key=api_key, api_endpoint=endpoint)
    check_exclusive_options(csv_path, project_id_src, emails, None)

    if csv_path is not None:
        members_to_add = collect_members_from_csv(csv_path, role)
    elif project_id_src is not None:
        members_to_add = collect_members_from_project(kili, project_id_src, role)
    else:
        assert emails, (
            "When `--csv-path` and `--from-project` are not specified, you must add several email"
            " addresses as arguments."
        )
        members_to_add = collect_members_from_emails(emails, role)

    count = 0
    existing_members = ProjectUserQuery(kili.graphql_client, kili.http_client)(
        where=ProjectUserWhere(project_id=project_id),
        fields=[
            "activated",
            "user.email",
        ],
        options=QueryOptions(disable_tqdm=True),
    )
    existing_member_emails = {
        member["user"]["email"] for member in existing_members if member["activated"]
    }

    for member in members_to_add:
        if member["email"] in existing_member_emails:
            already_member = member["email"]
            warnings.warn(
                f"{already_member} is already an active member of the project."
                " Use kili project member update to update role.",
                stacklevel=1,
            )
        else:
            kili.append_to_roles(
                project_id=project_id, user_email=member["email"], role=member["role"]
            )
            count += 1

    print(f"{count} member(s) have been successfully added to project: {project_id}")
