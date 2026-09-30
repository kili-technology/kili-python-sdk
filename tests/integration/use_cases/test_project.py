from types import GeneratorType

import pytest

from kili.adapters.kili_api_gateway.helpers.queries import QueryOptions
from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.adapters.kili_api_gateway.project.types import ProjectDataKiliAPIGatewayInput
from kili.domain.project import ProjectFilters, ProjectId
from kili.domain.types import ListOrTuple
from kili.exceptions import GraphQLError
from kili.use_cases.project.project import ProjectUseCases

interface = {
    "jobs": {
        "JOB_0": {
            "content": {
                "categories": {
                    "OBJECT_A": {"children": [], "name": "Object A"},
                    "OBJECT_B": {"children": [], "name": "Object B"},
                },
                "input": "radio",
            },
            "instruction": "Categories",
            "isChild": False,
            "mlTask": "CLASSIFICATION",
            "models": {},
            "isVisible": True,
            "required": 1,
        }
    }
}


def test_when_create_project_it_works(kili_api_gateway: KiliAPIGateway):
    kili_api_gateway.create_project.return_value = "fake_project_id"

    # When
    project_id = ProjectUseCases(kili_api_gateway).create_project(
        input_type="TEXT",
        json_interface={},
        title="test",
        description="description",
        project_id=None,
        compliance_tags=None,
        from_demo_project=None,
    )

    # Then
    assert project_id == "fake_project_id"


def test_when_create_project_without_inputType_or_jsonInterface_it_throw_an_error(
    kili_api_gateway: KiliAPIGateway,
):
    kili_api_gateway.create_project.return_value = "fake_project_id"

    # When
    project_use_cases = ProjectUseCases(kili_api_gateway)

    # Then
    with pytest.raises(
        ValueError,
        match="Arguments `input_type` and `json_interface` must be set if neither `from_demo_project` nor `project_id` is provided",
    ):
        project_use_cases.create_project(
            title="test",
            description="description",
            compliance_tags=None,
            from_demo_project=None,
        )


def test_when_create_project_with_project_id_it_works(kili_api_gateway: KiliAPIGateway):
    # Given
    tags = [
        {"id": "tag1_id", "label": "tag1"},
        {"id": "tag2_id", "label": "tag2"},
    ]
    kili_api_gateway.create_project.return_value = "fake_copied_project_id"
    kili_api_gateway.get_project.return_value = {
        "jsonInterface": interface,
        "instructions": "fake_instructions",
        "inputType": "TEXT",
    }
    kili_api_gateway.list_tags_by_project.return_value = tags
    kili_api_gateway.list_tags_by_org.return_value = tags

    # When
    project_id = ProjectUseCases(kili_api_gateway).create_project(
        title="test",
        description="description",
        project_id=ProjectId("fake_project_id"),
        compliance_tags=None,
        from_demo_project=None,
    )

    # Then
    assert project_id == "fake_copied_project_id"


def test_when_create_project_with_project_id_it_throw_an_error_if_tags_do_not_belong_to_the_same_organisation(
    kili_api_gateway: KiliAPIGateway,
):
    # Given
    tags = [
        {"id": "tag1_id", "label": "tag1"},
    ]
    org_tags = [
        {"id": "tag2_id", "label": "tag2"},
    ]
    kili_api_gateway.create_project.return_value = "fake_copied_project_id"
    kili_api_gateway.get_project.return_value = {
        "jsonInterface": interface,
        "instructions": "fake_instructions",
        "inputType": "TEXT",
    }
    kili_api_gateway.list_tags_by_project.return_value = tags
    kili_api_gateway.list_tags_by_org.return_value = org_tags

    # When
    project_use_cases = ProjectUseCases(kili_api_gateway)
    with pytest.raises(
        ValueError,
        match="Tag tag1_id doesn't belong to your organization and was not copied.",
    ):
        project_use_cases.create_project(
            title="test",
            description="description",
            project_id=ProjectId("fake_project_id"),
            compliance_tags=None,
            from_demo_project=None,
        )


def test_when_i_query_projects_i_get_a_generator_of_projects(kili_api_gateway: KiliAPIGateway):
    # Given
    kili_projects = [
        {
            "title": f"fake_proj_title_{i}",
            "id": f"fake_project_id_{i}",
            "jsonInterface": {},
            "inputType": "TEXT",
        }
        for i in range(3)
    ]
    kili_api_gateway.list_projects.return_value = (proj for proj in kili_projects)

    # When
    retrieved_projects = ProjectUseCases(kili_api_gateway).list_projects(
        ProjectFilters(
            id=None,
            archived=None,
            search_query=None,
            should_relaunch_kpi_computation=None,
            starred=None,
            updated_at_gte=None,
            updated_at_lte=None,
            created_at_gte=None,
            created_at_lte=None,
            tag_ids=None,
        ),
        fields=("id", "title", "jsonInterface", "inputType"),
        options=QueryOptions(disable_tqdm=None, first=None, skip=0),
    )

    # Then
    assert isinstance(retrieved_projects, GeneratorType)
    assert list(retrieved_projects) == kili_projects


def test_given_a_project_when_update_its_properties_then_it_updates_project_props(
    kili_api_gateway: KiliAPIGateway,
):
    # Given
    def mocked_update_properties_in_project(
        project_id: ProjectId,
        project_data: ProjectDataKiliAPIGatewayInput,
        fields: ListOrTuple[str],
    ):
        return {field: f"{field}_value" for field in fields}

    kili_api_gateway.update_properties_in_project.side_effect = mocked_update_properties_in_project

    # When
    project = ProjectUseCases(kili_api_gateway).update_properties_in_project(
        project_id=ProjectId("fake_proj_id"),
        title="new_title",
        can_navigate_between_assets=None,
        can_skip_asset=None,
        compliance_tags=None,
        consensus_mark=None,
        consensus_tot_coverage=None,
        description=None,
        honeypot_mark=None,
        instructions=None,
        json_interface=None,
        min_consensus_size=None,
        review_coverage=None,
        should_relaunch_kpi_computation=None,
        use_honeypot=None,
        metadata_types=None,
    )

    # Then
    assert "id" in project
    assert project == {"title": "title_value", "id": "id_value"}


def _updated(project_id: str, author_id: str = "new_author_id") -> dict:
    return {"id": project_id, "author": {"id": author_id}}


def test_when_i_transfer_the_projects_of_an_author_then_the_refused_ones_are_reported(
    kili_api_gateway: KiliAPIGateway,
):
    # Given
    kili_api_gateway.list_projects.return_value = (
        {"id": project_id} for project_id in ("project_1", "project_2", "project_3")
    )
    refusal = GraphQLError("Only project admins can be made project owners.")
    kili_api_gateway.update_properties_in_project.side_effect = [
        _updated("project_1"),
        refusal,
        _updated("project_3"),
    ]

    # When
    outcome = ProjectUseCases(kili_api_gateway).transfer_projects_authorship(
        "former_author_id", "new_author_id"
    )

    # Then
    assert outcome == {
        "transferred": ["project_1", "project_3"],
        "failed": [{"id": "project_2", "error": str(refusal)}],
    }
    filters = kili_api_gateway.list_projects.call_args.args[0]
    assert filters.author_id == "former_author_id"
    assert kili_api_gateway.update_properties_in_project.call_count == 3
    for call in kili_api_gateway.update_properties_in_project.call_args_list:
        assert call.args[1].author == "new_author_id"
        assert call.args[2] == ("author.id", "id")


def test_when_a_project_fails_for_any_reason_then_the_others_are_still_transferred(
    kili_api_gateway: KiliAPIGateway,
):
    # Given a connection that drops on the first project
    kili_api_gateway.list_projects.return_value = (
        {"id": pid} for pid in ("project_1", "project_2")
    )
    kili_api_gateway.update_properties_in_project.side_effect = [
        ConnectionError("connection dropped"),
        _updated("project_2"),
    ]

    # When
    outcome = ProjectUseCases(kili_api_gateway).transfer_projects_authorship(
        "former_author_id", "new_author_id"
    )

    # Then
    assert outcome == {
        "transferred": ["project_2"],
        "failed": [{"id": "project_1", "error": "connection dropped"}],
    }


def test_when_the_server_does_not_apply_the_new_author_then_the_project_is_reported_failed(
    kili_api_gateway: KiliAPIGateway,
):
    # Given a server that answers OK and keeps the former author
    kili_api_gateway.list_projects.return_value = iter([{"id": "project_1"}])
    kili_api_gateway.update_properties_in_project.return_value = _updated(
        "project_1", author_id="former_author_id"
    )

    # When
    outcome = ProjectUseCases(kili_api_gateway).transfer_projects_authorship(
        "former_author_id", "new_author_id"
    )

    # Then
    assert outcome["transferred"] == []
    assert outcome["failed"] == [
        {"id": "project_1", "error": "The server did not change the author."}
    ]


def test_when_the_author_has_no_project_then_the_transfer_is_empty(
    kili_api_gateway: KiliAPIGateway,
):
    # Given
    kili_api_gateway.list_projects.return_value = iter([])

    # When
    outcome = ProjectUseCases(kili_api_gateway).transfer_projects_authorship(
        "former_author_id", "new_author_id"
    )

    # Then
    assert outcome == {"transferred": [], "failed": []}
    kili_api_gateway.update_properties_in_project.assert_not_called()


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"author_id": "user_id", "new_author_id": "user_id"}, "must be different users"),
        (
            {"author_email": "Jane@Acme.com", "new_author_email": "jane@acme.COM"},
            "must be different users",
        ),
        ({"author_id": "user_id", "new_author_id": ""}, "`new_author_id` must not be empty"),
        ({"author_id": "", "new_author_id": "user_id"}, "`author_id` must not be empty"),
        (
            {"author_email": "", "new_author_id": "user_id"},
            "`author_email` must not be empty",
        ),
        (
            {"author_id": "a", "author_email": "a@acme.com", "new_author_id": "b"},
            "`author_id` or as `author_email`, one of the two",
        ),
        (
            {"author_id": "a", "new_author_id": "b", "new_author_email": "b@acme.com"},
            "`new_author_id` or as `new_author_email`, one of the two",
        ),
        ({"author_id": "a"}, "`new_author_id` or as `new_author_email`, one of the two"),
        ({"new_author_id": "b"}, "`author_id` or as `author_email`, one of the two"),
    ],
)
def test_when_the_users_of_a_transfer_are_not_two_users_then_it_is_refused_before_any_call(
    kili_api_gateway: KiliAPIGateway, kwargs: dict, message: str
):
    with pytest.raises(ValueError, match=message):
        ProjectUseCases(kili_api_gateway).transfer_projects_authorship(**kwargs)

    kili_api_gateway.list_projects.assert_not_called()
    kili_api_gateway.update_properties_in_project.assert_not_called()


def _project(project_id: str, members: dict[str, str], author: str = "former_author_id") -> dict:
    """A project of the listing: its author and its members, by id and email."""
    return {
        "id": project_id,
        "author": {"id": author},
        "roles": [{"user": {"id": id_, "email": email}} for id_, email in members.items()],
    }


def test_when_i_transfer_by_email_then_the_author_is_listed_by_email_and_the_new_one_is_found_among_the_members(
    kili_api_gateway: KiliAPIGateway,
):
    # Given a project the new author, written in another case, is a member of
    kili_api_gateway.list_projects.return_value = iter(
        [_project("project_1", {"new_author_id": "New.Owner@Acme.com", "other_id": "o@acme.com"})]
    )
    kili_api_gateway.update_properties_in_project.return_value = _updated("project_1")

    # When
    outcome = ProjectUseCases(kili_api_gateway).transfer_projects_authorship(
        author_email="leaving@acme.com", new_author_email="new.owner@acme.com"
    )

    # Then
    assert outcome == {"transferred": ["project_1"], "failed": []}
    list_args = kili_api_gateway.list_projects.call_args
    assert list_args.args[0].author_email == "leaving@acme.com"
    assert list_args.args[0].author_id is None
    assert list_args.args[1] == ("id", "author.id", "roles.user.id", "roles.user.email")
    update_args = kili_api_gateway.update_properties_in_project.call_args.args
    assert update_args[1].author == "new_author_id"


def test_when_the_new_author_is_not_a_member_of_a_project_then_it_is_reported_and_left_alone(
    kili_api_gateway: KiliAPIGateway,
):
    # Given a first project the new author is a member of, and a second they are not
    kili_api_gateway.list_projects.return_value = iter(
        [
            _project("project_1", {"new_author_id": "new.owner@acme.com"}),
            _project("project_2", {"other_id": "other@acme.com"}),
        ]
    )
    kili_api_gateway.update_properties_in_project.return_value = _updated("project_1")

    # When
    outcome = ProjectUseCases(kili_api_gateway).transfer_projects_authorship(
        author_id="former_author_id", new_author_email="new.owner@acme.com"
    )

    # Then
    assert outcome["transferred"] == ["project_1"]
    assert [failure["id"] for failure in outcome["failed"]] == ["project_2"]
    assert "new.owner@acme.com" in outcome["failed"][0]["error"]
    assert kili_api_gateway.update_properties_in_project.call_count == 1


def test_when_the_new_author_already_is_the_author_of_a_project_then_it_is_reported(
    kili_api_gateway: KiliAPIGateway,
):
    # Given a project whose author is the user the email designates
    kili_api_gateway.list_projects.return_value = iter(
        [_project("project_1", {"new_author_id": "new.owner@acme.com"}, author="new_author_id")]
    )

    # When
    outcome = ProjectUseCases(kili_api_gateway).transfer_projects_authorship(
        author_email="leaving@acme.com", new_author_email="new.owner@acme.com"
    )

    # Then
    assert outcome["transferred"] == []
    assert outcome["failed"] == [
        {"id": "project_1", "error": "This user is already the author of the project."}
    ]
    kili_api_gateway.update_properties_in_project.assert_not_called()


def test_when_both_an_id_and_an_email_name_the_author_of_the_projects_then_it_is_refused():
    # Given an id and an email for the author
    # When the filters are built
    # Then they are refused
    with pytest.raises(ValueError, match="`author_id` or as `author_email`, not both"):
        ProjectFilters(id=None, author_id="user_id", author_email="user@acme.com")


def test_when_two_members_have_the_email_in_other_cases_then_the_exact_one_is_chosen_or_it_is_ambiguous(
    kili_api_gateway: KiliAPIGateway,
):
    # Given a project holding two users whose addresses differ by case, and one holding two other ones
    kili_api_gateway.list_projects.return_value = iter(
        [
            _project("project_1", {"lower_id": "jane@acme.com", "upper_id": "Jane@acme.com"}),
            _project("project_2", {"mixed_id": "JANE@acme.com", "upper_id": "Jane@acme.com"}),
        ]
    )
    kili_api_gateway.update_properties_in_project.return_value = _updated("project_1", "lower_id")

    # When the new author is given as the lower-case address
    outcome = ProjectUseCases(kili_api_gateway).transfer_projects_authorship(
        author_id="former_author_id", new_author_email="jane@acme.com"
    )

    # Then the exact address wins where there is one, and the other project is reported ambiguous
    assert outcome["transferred"] == ["project_1"]
    assert kili_api_gateway.update_properties_in_project.call_args.args[1].author == "lower_id"
    assert [failure["id"] for failure in outcome["failed"]] == ["project_2"]
    assert "Several members" in outcome["failed"][0]["error"]


def test_when_the_email_of_the_author_names_several_users_then_nothing_is_moved(
    kili_api_gateway: KiliAPIGateway,
):
    # Given projects authored by two users whose addresses differ only by case
    kili_api_gateway.list_projects.return_value = iter(
        [
            _project("project_1", {}, author="lower_id"),
            _project("project_2", {}, author="upper_id"),
        ]
    )

    # When the hand-over is asked by that address
    with pytest.raises(ValueError, match="Several users have the email"):
        ProjectUseCases(kili_api_gateway).transfer_projects_authorship(
            author_email="jane@acme.com", new_author_id="new_author_id"
        )

    # Then no project was touched
    kili_api_gateway.update_properties_in_project.assert_not_called()


def test_when_the_author_is_given_by_email_and_is_the_new_author_by_id_then_it_is_reported(
    kili_api_gateway: KiliAPIGateway,
):
    # Given a project whose author is the user the new id designates
    kili_api_gateway.list_projects.return_value = iter(
        [_project("project_1", {}, author="new_author_id")]
    )

    # When the author is named by email and the new author by id
    outcome = ProjectUseCases(kili_api_gateway).transfer_projects_authorship(
        author_email="leaving@acme.com", new_author_id="new_author_id"
    )

    # Then the project is reported and left alone
    assert outcome["failed"] == [
        {"id": "project_1", "error": "This user is already the author of the project."}
    ]
    kili_api_gateway.update_properties_in_project.assert_not_called()


def test_when_the_users_are_given_by_id_then_the_members_of_the_projects_are_not_fetched(
    kili_api_gateway: KiliAPIGateway,
):
    # Given
    kili_api_gateway.list_projects.return_value = iter([])

    # When
    ProjectUseCases(kili_api_gateway).transfer_projects_authorship(
        author_id="former_author_id", new_author_id="new_author_id"
    )

    # Then only what the hand-over reads is requested
    assert kili_api_gateway.list_projects.call_args.args[1] == ("id", "author.id")
