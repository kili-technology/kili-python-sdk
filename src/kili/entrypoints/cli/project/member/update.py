"""CLI's project member update subcommand."""

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


@click.command(name="update")
@Options.api_key
@Options.endpoint
@Arguments.emails
@Options.project_id
@Options.role
@from_csv(["email"], ["role"])
@Options.from_project
# pylint: disable=too-many-arguments
def update_member(
    api_key: Optional[str],
    endpoint: Optional[str],
    emails: Optional[Iterable[str]],
    project_id: str,
    role: Optional[str],
    csv_path: Optional[str],
    project_id_src: Optional[str],
):
    """Update member's role of a Kili project.

    Emails can be passed directly as arguments.
    You can provide several emails separated by spaces.

    \b
    !!! Examples
        ```
        kili project member update\\
            --project-id <project_id> \\
            --role REVIEWER \\
            john.doe@test.com
        ```
        ```
        kili project member update \\
            --project-id <project_id> \\
            --from-csv path/to/members.csv
        ```
        ```
        kili project member update \\
            --project-id <project_id> \\
            --from-project <project_id_scr>
        ```
    """
    kili = get_kili_client(api_key=api_key, api_endpoint=endpoint)

    check_exclusive_options(csv_path, project_id_src, emails, None)

    if csv_path is not None:
        members_to_update = collect_members_from_csv(csv_path, role)
    elif project_id_src is not None:
        members_to_update = collect_members_from_project(kili, project_id_src, role)
    else:
        assert emails is not None, (
            "When --csv-path and --from-project are not specified, you must add several email"
            " addresses as arguments."
        )
        members_to_update = collect_members_from_emails(emails, role)

    count = 0

    existing_members_gen = ProjectUserQuery(kili.graphql_client, kili.http_client)(
        where=ProjectUserWhere(project_id=project_id),
        fields=["role", "activated", "user.email", "id", "user.id"],
        options=QueryOptions(disable_tqdm=True),
    )
    existing_members = {
        member["user"]["email"]: {
            "role_id": member["id"],
            "user_id": member["user"]["id"],
            "role": member["role"],
        }
        for member in existing_members_gen
        if member["activated"]
    }

    for member in members_to_update:
        email = member["email"]
        if email in existing_members:
            if existing_members[email]["role"] != member["role"]:
                kili.update_properties_in_role(
                    role_id=existing_members[email]["role_id"],
                    project_id=project_id,
                    user_id=existing_members[email]["user_id"],
                    role=member["role"],
                )
                count += 1
            else:
                warnings.warn(
                    f"{email} is already an active member of the project with the same role.",
                    stacklevel=1,
                )
        else:
            warnings.warn(
                f"{email} is not an active member of the project."
                " Use kili project member add to add member.",
                stacklevel=1,
            )

    print(f"{count} member's role(s) have been successfully updated in project: {project_id}")
