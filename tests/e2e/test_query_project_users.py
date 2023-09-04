import uuid

import pytest

from kili.client import Kili


@pytest.fixture()
def kili() -> Kili:
    return Kili()


@pytest.fixture()
def project_id_suspended_user_email(kili: Kili):
    project = kili.create_project(
        input_type="TEXT", title="test_query_project_users.py sdk", json_interface={"jobs": {}}
    )

    # add a user that we desactivate
    suspended_user_email = f"john.doe{uuid.uuid4()}+desactivated@kili-technology.com"
    kili.append_to_roles(
        project_id=project["id"],
        user_email=suspended_user_email,
        role="LABELER",
    )
    kili.update_properties_in_user(email=suspended_user_email, activated=False)

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
    all_users = kili.project_users(project_id=project_id, fields=fields, status_in=None)

    # Then
    assert len(all_users) > 0

    # When
    activated_users = kili.project_users(
        project_id=project_id, fields=fields, status_in=["ACTIVATED"]
    )

    # Then, only one activated user: the api user
    assert len(activated_users) == 1, activated_users
    assert activated_users[0]["user"]["email"] == api_user["email"], activated_users

    # When
    admin_users = kili.project_users(project_id=project_id, fields=fields, status_in=["ORG_ADMIN"])

    # Then, admin users are not api user or disabled user
    for proj_user in admin_users:
        assert proj_user["user"]["email"] not in {
            api_user["email"],
            suspended_user_email,
        }, admin_users

    # When
    disabled_users = kili.project_users(
        project_id=project_id, fields=fields, status_in=["ORG_SUSPENDED"]
    )

    # Then, the user we desactivated is disabled
    assert suspended_user_email in {
        user["user"]["email"] for user in disabled_users
    }, disabled_users
