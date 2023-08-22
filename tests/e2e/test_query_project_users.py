import uuid
from typing import Dict

import pytest
import pytest_mock

from kili.client import Kili


@pytest.fixture()
def kili() -> Kili:
    return Kili()


@pytest.fixture()
def project_id_suspended_user_email(kili: Kili):
    project = kili.create_project(
        input_type="TEXT", title="test_query_project_users.py sdk", json_interface={"jobs": {}}
    )

    # We add some users to both the orga and the project
    # for role in ("LABELER", "TEAM_MANAGER", "REVIEWER", "ADMIN"):
    #     kili.append_to_roles(
    #         project_id=project["id"],
    #         user_email=f"john.doe+{role}@kili-technology.com",
    #         role=role,
    #     )

    # add a user that we will desactivate
    suspended_user_email = f"john.doe{uuid.uuid4()}+desactivated@kili-technology.com"
    kili.append_to_roles(
        project_id=project["id"],
        user_email=suspended_user_email,
        role="LABELER",
    )
    # project_users = kili.project_users(project_id=project["id"], fields=["id", "user.email"])
    # user = [user for user in project_users if user["user"]["email"] == suspended_user_email][0]

    kili.update_properties_in_user(email=suspended_user_email, activated=False)
    # kili.delete_from_roles(user["id"])
    # query = """
    #     mutation updatePropertiesInProjectUser($data: ProjectUserData!, $where: ProjectUserWhere!) {
    #         data: updatePropertiesInProjectUser(data: $data, where: $where) {
    #             id activated
    #         }
    #     }
    #     """
    # kili.graphql_client.execute(
    #     query=query,
    #     variables={
    #         "where": {"project": {"id": project["id"]}, "user": {"email": suspended_user_email}},
    #         "data": {"activated": False},
    #     },
    # )

    yield project["id"], suspended_user_email

    kili.delete_project(project_id=project["id"])


def test_given_project_when_querying_project_users_it_works(
    kili: Kili, project_id_suspended_user_email
):
    # Given
    project_id, suspended_user_email = project_id_suspended_user_email
    api_user = kili.get_user()
    fields = ["activated", "deletedAt", "id", "role", "user.email", "user.id", "status"]

    # When
    all_users = kili.project_users(project_id=project_id, fields=fields, status=None)

    # Then
    assert len(all_users) > 0

    # When
    activated_users = kili.project_users(project_id=project_id, fields=fields, status="ACTIVATED")

    # Then, only one activated user: the api user
    for proj_user in activated_users:
        assert proj_user["user"]["email"] in {api_user["email"]}

    # When
    admin_users = kili.project_users(project_id=project_id, fields=fields, status="ORG_ADMIN")

    # Then, admin users are not api user or disabled user
    for proj_user in admin_users:
        assert proj_user["user"]["email"] not in {api_user["email"], suspended_user_email}

    # When
    disabled_users = kili.project_users(
        project_id=project_id, fields=fields, status="ORG_SUSPENDED"
    )

    # Then, only one disabled user
    for proj_user in disabled_users:
        assert proj_user["user"]["email"] in {suspended_user_email}
