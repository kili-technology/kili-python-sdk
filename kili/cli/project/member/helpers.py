
"""CLI's Porject Member common functions"""

import csv
import re
from typing import Any, Dict, List, Optional, cast
import warnings

REGEX_EMAIL = re.compile(
    r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
ROLES = ["ADMIN", "TEAM_MANAGER", "REVIEWER", "LABELER"]

# pylint: disable=consider-using-f-string


def dict_type_check(dict_: Dict[str, Any], type_check):
    """check if elements in row have correct type and return [row]"""
    warnings_message = ''
    for key, value in dict_.items():
        warnings_message += type_check(key, value)
    if len(warnings_message) == 0:
        return [dict_]

    warnings.warn(warnings_message +
                  '{} will not be added.'.format(list(dict_.values())[0]))
    return []


def collect_from_csv(csv_path: str,
                     required_columns: List[str],
                     optional_columns: Optional[List[str]],
                     type_check_function):
    """read a csv to collect required_columns and optional_columns"""
    out = []
    with open(csv_path, 'r', encoding='utf-8') as csv_file:
        csvreader = csv.DictReader(csv_file)
        headers = csvreader.fieldnames
        missing_columns = list(set(required_columns) - set(headers))
        if len(missing_columns) > 0:
            raise ValueError(
                f"{missing_columns} must be headers of the csv file: {csv_path}")
        for row in csvreader:
            out += dict_type_check(
                dict_={k: v for k, v in row.items() if k in required_columns +
                       optional_columns},
                type_check=type_check_function
            )

    return out


def type_check_member(key, value):
    """type check value based on key """
    if key == 'email' and not re.search(REGEX_EMAIL, value):
        return f'{value} is not a valid email address, '

    if key == 'role' and not value in ROLES:
        return f'{value} is not a valid role, '

    return ''


def collect_members_from_csv(csv_path: str, role: Optional[str]):
    """read a csv with to collect members and role"""
    members_to_add = collect_from_csv(
        csv_path=csv_path,
        required_columns=['email'],
        optional_columns=['role'],
        type_check_function=type_check_member)

    if len(members_to_add) == 0:
        raise ValueError(
            f'No active member were found in csv: {csv_path}')

    if 'role' in members_to_add[0].keys():
        if role is not None:
            raise ValueError(
                '--role cannot be used if the argument passed is '
                'a path to a csv file with roles')
    else:
        if role is None:
            role = 'LABELER'
        for member in members_to_add:
            member['role'] = role

    return members_to_add


def collect_members_from_project(kili, project_id_source: str, role: Optional[str]):
    """copy members from project of id project_id_source"""
    members = []

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
                members.append(
                    {'email': user['user']['email'], 'role': user['role']})
    except:
        # pylint: disable=raise-missing-from
        raise ValueError(
            f'{project_id_source} is not recognized as a Kili project_id')

    if len(members) == 0:
        raise ValueError(
            f'No active member were found in project with id {project_id_source}')

    return members


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
