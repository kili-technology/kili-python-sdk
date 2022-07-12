"""CLI's project member add subcommand"""

import csv
import re
from typing import Dict, List, Optional, cast
import warnings
import click

from kili.client import Kili
from kili.cli.common_args import Options


REGEX_EMAIL = re.compile(
    r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
ROLES = ["ADMIN", "TEAM_MANAGER", "REVIEWER", "LABELER"]


def collect_members_from_csv(csv_path: str, role: Optional[str]):
    """read a csv with to collect members and role"""
    rows = []
    with open(csv_path, 'r', encoding="utf-8") as file:
        csvreader = csv.reader(file)
        header = next(csvreader)
        for row in csvreader:
            rows.append(row)

    use_individual_role = (len(header) > 1)

    if use_individual_role and role is not None:
        raise ValueError(
            '--role cannot be used if the argument passed is '
            'a path to a csv file with roles')
    if not use_individual_role and role is None:
        role = 'LABELER'

    members_to_add = []

    def get_member_from_row(row: List[str],
                            use_individual_role: bool,
                            is_header: bool,
                            role: str):
        if re.search(REGEX_EMAIL, row[0]):
            if use_individual_role:
                if row[1].strip().upper() in ROLES:
                    members_to_add.append(
                        {'email': row[0], 'role':  row[1]})
                else:
                    warnings.warn(
                        f'{row[1]} is not a valid role,'
                        f'{row[0]} will not be added.')
            else:
                members_to_add.append(
                    {'email': row[0], 'role':  role})
        else:
            if not is_header:
                warnings.warn(f'{row[0]} is not a valid email address,')

    get_member_from_row(header, use_individual_role, True, role)
    for row in rows:
        get_member_from_row(row, use_individual_role, False, role)

    if len(members_to_add) == 0:
        raise ValueError(
            f'No valid email address were found in csc {csv_path}')

    return members_to_add


def collect_members_from_project(kili, project_id_source: str, role: Optional[str]):
    """copy members from project of id project_id_source"""
    members_to_add = []

    if role is not None:
        raise ValueError(
            '--role cannot be used if the argument passed is a Kili project_id')

    try:
        users = cast(
            List[Dict], kili.project_users(
                project_id=project_id_source,
                fields=[
                    'role',
                    'user.email',
                    'activated'
                ],
                disable_tqdm=True))
        for user in users:
            if user['activated']:
                members_to_add.append(
                    {'email': user['user']['email'], 'role': user['role']})
    except:
        # pylint: disable=raise-missing-from
        raise ValueError(
            f'{project_id_source} is not recognized as a Kili project_id')

    if len(members_to_add) == 0:
        raise ValueError(
            f'No active member were found in project with id {project_id_source}')

    return members_to_add


def collect_members_from_emails(emails: List[str], role: Optional[str]):
    """collect members with email address from emails"""
    if role is None:
        role = 'LABELER'
    members_to_add = []
    for email in emails:
        if re.search(REGEX_EMAIL, email):
            members_to_add.append({'email': email, 'role': role})
        else:
            warnings.warn(f'{email} is not a valid email address,')

    if len(members_to_add) == 0:
        raise ValueError('No valid email adresses were provided')

    return members_to_add


# pylint: disable=too-many-arguments
@click.command()
@Options.api_key
@Options.endpoint
@click.argument('emails', type=str, required=False, nargs=-1)
@click.option('--project-id', type=str, required=True,
              help='Id of the project to add members to')
@click.option('--role', type=click.Choice(ROLES), default=None,
              show_default='LABELER',
              help='Project role of the added user(s).')
@ click.option('--from-csv', 'csv_path', type=click.Path(),
               help=('path to a csv file with email in the first column.'
               ' A second column can be used to use one-to-one role.')
               )
@click.option('--from-project', 'project_id_src', type=str,
              help='project_id of another Kili project to copy the users from')
def add_member(api_key: Optional[str],
               endpoint: Optional[str],
               emails: Optional[str],
               project_id: str,
               role: Optional[str],
               csv_path:  Optional[str],
               project_id_src: Optional[str],
               ):
    """Add members to a Kili project

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
    kili = Kili(api_key=api_key, api_endpoint=endpoint)
    if ((csv_path is not None) + (project_id_src is not None) + (len(emails) > 0)) > 1:
        raise ValueError(
            'Options --from-csv, --from-project and emails are exclusive.')

    if csv_path is not None:
        members_to_add = collect_members_from_csv(csv_path, role)
    elif project_id_src is not None:
        members_to_add = collect_members_from_project(
            kili, project_id_src, role)
    else:
        members_to_add = collect_members_from_emails(emails, role)

    count = 0
    existing_members = kili.project_users(
        project_id=project_id, disable_tqdm=True)
    existing_members = [member['user']['email']
                        for member in existing_members if member['activated']]

    for member in members_to_add:
        if member['email'] in existing_members:
            already_member = member['email']
            warnings.warn(f'{already_member} is already an active member of the project.'
                          ' Use kili project member update to update role.')
        else:
            kili.append_to_roles(project_id=project_id,
                                 user_email=member['email'], role=member['role'])
            count += 1

    print(f'{count} users have been successfully added to project: {project_id}')
