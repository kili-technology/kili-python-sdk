"""CLI's project member add subcommand"""

import csv
import os
import re
from typing import Dict, List, Optional, cast
import warnings
import click

from kili.client import Kili
from kili.cli.common_args import Options


REGEX_EMAIL = re.compile(
    r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
ROLES = ["ADMIN", "TEAM_MANAGER", "REVIEWER", "LABELER"]


def read_csv_user(csv_path: str, emails: List[str], roles: List[str]):
    """read a csv with a user list and update emails and roles """
    with open(csv_path, 'r', encoding="utf-8") as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            if re.search(REGEX_EMAIL, row[0]):
                emails.append(row[0])
            if len(row) > 1 and (row[1].strip().upper() in ROLES):
                roles.append(row[1].strip().upper())


def extract_project_user(kili, project_id: str, emails: List[str], roles: List[str]):
    """extract user list from project_id and update emails and roles """
    try:
        users = cast(
            List[Dict], kili.project_users(
                project_id=project_id,
                fields=[
                    'role',
                    'user.email'
                ],
                disable_tqdm=True))
        for user in users:
            if user['activated']:
                emails.append(user['user']['email'])
                roles.append(user['role'])
    except:
        # pylint: disable=raise-missing-from
        raise ValueError(
            f'{project_id} is not recognized as a csv file path '
            'nor an email adress nor a Kili project_id')


def add_list_of_users(kili, project_id: str, emails: List[str], roles: List[str]):
    """add user listed in emails in project_id"""
    count = 0
    for email, role in zip(emails, roles):
        existing_user = kili.project_users(
            project_id=project_id, email=email, disable_tqdm=True)
        if (len(existing_user) > 0 and existing_user[0]['activated']):
            warnings.warn(f'{email} is already an active member of the project.'
                          ' Use kili project member update to update role.')
        else:
            kili.append_to_roles(project_id=project_id,
                                 user_email=email, role=role)
            count += 1
    return count


@click.command()
@Options.api_key
@Options.endpoint
@click.argument('inputs', type=str, required=True, nargs=-1)
@ click.option('--project-id', type=str, required=True,
               help='Id of the project to add members to')
@ click.option('--role', type=str, default=None,
               show_default='LABELER',
               help='Project role of the added user(s).')
# pylint: disable=too-many-branches
def add_member(api_key: Optional[str],
               endpoint: Optional[str],
               inputs: str,
               project_id: str,
               role: Optional[str],
               ):
    """Add members to a Kili project

    Arguments can be: \n
        - string (with email format) \n
        - path to a csv file with email in the first column \n
            + optional: role in the second column \n
        - a project_id of another kili project \n

    If the argument is the project_id of another Kili project,
    copy the user from this project (and their role).

    You need to be an ADMIN of the organization or at
    least a TEAM_MANAGER in the project(s) involved.

    \b
    !!! Examples
        ```
        kili project member add \\
            john.doe@test.com \\
            --role REVIEWER \\
            --project-id <project_id>
        ```
        ```
        kili project member add \\
            path/to/members.csv \\
            --project-id <project_id>
        ```
        ```
        kili project member add \\
            another_project_id \\
            --project-id <project_id>
        ```
    """
    kili = Kili(api_key=api_key, api_endpoint=endpoint)
    emails = []
    roles = []
    for input_ in inputs:
        if os.path.exists(input_):
            read_csv_user(input_, emails, roles)
        elif re.search(REGEX_EMAIL, input_):
            emails.append(input_)
        else:
            extract_project_user(kili, input_, emails, roles)

    if len(roles) == 0:
        if role is None:
            role = 'LABELER'
        roles = [role] * len(emails)
    elif len(roles) == len(emails):
        if role is not None:
            raise ValueError(
                '--role cannot be used if the argument passed is '
                'a path to a csv file with roles or a Kili project_id')
    else:
        raise ValueError(
            'number of roles identified does not match the number of email adresses'
            ', check the csv file')

    count = add_list_of_users(kili, project_id, emails, roles)

    print(f'{count} users have been successfully added to project: {project_id}')
