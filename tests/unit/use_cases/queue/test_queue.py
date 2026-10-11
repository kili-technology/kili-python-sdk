"""Who may work on a queue, and what a held asset may become."""

import threading

import pytest

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.domain.asset import AssetId
from kili.domain.label import LabelId
from kili.domain.project import ProjectId
from kili.domain.user import UserId
from kili.exceptions import GraphQLError, QueueError
from kili.use_cases.queue import LockKeeper, QueueContext, QueueUseCases

LABEL_STEP = {"id": "s1", "name": "Label", "type": "DEFAULT", "assignees": [{"id": "me"}]}
REVIEW_STEP = {"id": "s2", "name": "Review", "type": "REVIEW", "assignees": [{"id": "boss"}]}


def _context(mode="label", can_skip_asset=True) -> QueueContext:
    return QueueContext(
        project_id=ProjectId("project"),
        project_title="Bot project",
        user_id=UserId("me"),
        user_email="bot@acme.com",
        role="LABELER",
        mode=mode,
        can_skip_asset=can_skip_asset,
    )


def _given_member(kili_api_gateway: KiliAPIGateway, role="LABELER", steps=None, activated=True):
    kili_api_gateway.get_current_user.return_value = {"id": "me", "email": "bot@acme.com"}
    kili_api_gateway.get_project_user.return_value = {"role": role, "activated": activated}
    kili_api_gateway.get_project.return_value = {
        "title": "Bot project",
        "canSkipAsset": False,
        "steps": [LABEL_STEP, REVIEW_STEP] if steps is None else steps,
    }


def test_it_gives_the_context_of_a_labeler_on_a_labeling_step(kili_api_gateway):
    # Given
    _given_member(kili_api_gateway)

    # When
    context = QueueUseCases(kili_api_gateway).get_context(ProjectId("project"), "label")

    # Then
    assert context.role == "LABELER"
    assert context.user_id == "me"
    assert context.can_skip_asset is False


def test_it_lets_a_project_without_steps_serve_any_member(kili_api_gateway):
    # Given
    _given_member(kili_api_gateway, role="REVIEWER", steps=[])

    # When
    context = QueueUseCases(kili_api_gateway).get_context(ProjectId("project"), "review")

    # Then
    assert context.mode == "review"


def test_it_says_when_the_account_is_not_a_member(kili_api_gateway):
    # Given
    _given_member(kili_api_gateway)
    kili_api_gateway.get_project_user.return_value = None

    # When / Then
    with pytest.raises(QueueError, match="bot@acme.com is not a member of project project"):
        QueueUseCases(kili_api_gateway).get_context(ProjectId("project"), "label")
    kili_api_gateway.get_project.assert_not_called()


def test_it_says_when_the_member_is_deactivated(kili_api_gateway):
    # Given
    _given_member(kili_api_gateway, activated=False)

    # When / Then
    with pytest.raises(QueueError, match="is deactivated on project 'Bot project'"):
        QueueUseCases(kili_api_gateway).get_context(ProjectId("project"), "label")


def test_it_says_a_labeler_cannot_review(kili_api_gateway):
    # Given
    _given_member(kili_api_gateway, role="LABELER")

    # When / Then
    with pytest.raises(QueueError, match="is LABELER on project 'Bot project'.*REVIEWER"):
        QueueUseCases(kili_api_gateway).get_context(ProjectId("project"), "review")


def test_it_names_the_steps_the_member_is_not_assigned_to(kili_api_gateway):
    # Given
    _given_member(kili_api_gateway, role="REVIEWER")

    # When / Then
    with pytest.raises(QueueError, match="assigned to none of the review steps.*'Review'"):
        QueueUseCases(kili_api_gateway).get_context(ProjectId("project"), "review")


def test_it_says_when_the_workflow_has_no_step_of_the_kind(kili_api_gateway):
    # Given
    _given_member(kili_api_gateway, role="ADMIN", steps=[LABEL_STEP])

    # When / Then
    with pytest.raises(QueueError, match="has no review step"):
        QueueUseCases(kili_api_gateway).get_context(ProjectId("project"), "review")


def test_it_submits_a_label_addressed_by_the_asset_id(kili_api_gateway):
    # Given
    kili_api_gateway.append_to_labels.return_value = {"id": "label-1"}

    # When
    label = QueueUseCases(kili_api_gateway).submit(
        _context(), AssetId("a"), {"JOB": {}}, seconds_to_label=12.6
    )

    # Then
    assert label == {"id": "label-1"}
    data = kili_api_gateway.append_to_labels.call_args.kwargs["data"]
    assert (data.author_id, data.label_type, data.seconds_to_label) == ("me", "DEFAULT", 13)
    assert kili_api_gateway.append_to_labels.call_args.kwargs["asset_id"] == "a"
    kili_api_gateway.append_many_labels.assert_not_called()


def test_it_submits_a_review_linked_to_the_label_it_reviews(kili_api_gateway):
    # Given
    kili_api_gateway.append_many_labels.return_value = [{"id": "review-1"}]

    # When
    label = QueueUseCases(kili_api_gateway).submit(
        _context(mode="review"),
        AssetId("a"),
        {"JOB": {}},
        seconds_to_label=3,
        reviewed_label_id=LabelId("label-1"),
    )

    # Then
    assert label == {"id": "review-1"}
    data = kili_api_gateway.append_many_labels.call_args.kwargs["data"]
    assert data.label_type == "REVIEW"
    assert data.labels_data[0].referenced_label_id == "label-1"
    assert data.labels_data[0].author_id == "me"


def test_it_explains_a_submit_refused_on_the_lock(kili_api_gateway):
    # Given
    kili_api_gateway.append_to_labels.side_effect = GraphQLError(
        "refused", context={"reason": "AssetAlreadyLocked"}
    )

    # When / Then
    with pytest.raises(QueueError, match="currently being edited by another user"):
        QueueUseCases(kili_api_gateway).submit(_context(), AssetId("a"), {}, seconds_to_label=1)


def test_it_lets_other_submit_errors_through(kili_api_gateway):
    # Given
    kili_api_gateway.append_to_labels.side_effect = GraphQLError("invalid json response")

    # When / Then
    with pytest.raises(GraphQLError, match="invalid json response"):
        QueueUseCases(kili_api_gateway).submit(_context(), AssetId("a"), {}, seconds_to_label=1)


def test_it_skips_with_the_reason(kili_api_gateway):
    # When
    QueueUseCases(kili_api_gateway).skip(_context(), AssetId("a"), "blurry")

    # Then
    kili_api_gateway.skip_asset_with_reason.assert_called_once_with("project", "a", "blurry")


@pytest.mark.parametrize(
    ("context", "reason", "message"),
    [
        (_context(can_skip_asset=False), "blurry", "does not let its members skip"),
        (_context(mode="review"), "blurry", "the review interface has no skip"),
        (_context(), "  ", "A skip needs a reason"),
    ],
)
def test_it_refuses_a_skip_the_interface_would_refuse(kili_api_gateway, context, reason, message):
    # When / Then
    with pytest.raises(QueueError, match=message):
        QueueUseCases(kili_api_gateway).skip(context, AssetId("a"), reason)
    kili_api_gateway.skip_asset_with_reason.assert_not_called()


@pytest.mark.parametrize(
    ("outcome", "message"),
    [
        ({"succeeded": [], "declined": [], "failed": [{"details": "boom"}]}, "failed: boom"),
        ({"succeeded": [], "declined": [{"assetId": "a"}], "failed": []}, "cannot be sent back"),
    ],
)
def test_it_says_when_a_send_back_did_not_apply(kili_api_gateway, outcome, message):
    # Given
    kili_api_gateway.send_asset_back_to_queue.return_value = outcome

    # When / Then
    with pytest.raises(QueueError, match=message):
        QueueUseCases(kili_api_gateway).send_back(
            _context(mode="review"), AssetId("a"), LabelId("l1")
        )


def test_it_reports_why_a_lock_was_refused(kili_api_gateway):
    # Given
    kili_api_gateway.renew_asset_lock.side_effect = [
        {"lockSucceeded": True, "reasons": None},
        {"lockSucceeded": False, "reasons": ["AlreadyLocked"]},
    ]
    use_cases = QueueUseCases(kili_api_gateway)

    # When
    held = use_cases.renew_lock(_context(), AssetId("a"))
    lost = use_cases.renew_lock(_context(), AssetId("a"))

    # Then
    assert held == []
    assert lost == ["AlreadyLocked"]


def test_the_lock_keeper_renews_until_stopped(kili_api_gateway):
    # Given
    renewed = threading.Event()
    kili_api_gateway.renew_asset_lock.side_effect = lambda *_: (
        renewed.set() or {"lockSucceeded": True}
    )
    keeper = LockKeeper(QueueUseCases(kili_api_gateway), _context(), AssetId("a"), 0.01)

    # When
    keeper.start()
    assert renewed.wait(5)
    keeper.stop()
    calls = kili_api_gateway.renew_asset_lock.call_count

    # Then
    assert calls >= 1
    assert keeper.lost_reasons == []
    assert kili_api_gateway.renew_asset_lock.call_count == calls


def test_the_lock_keeper_warns_once_the_lock_is_lost(kili_api_gateway):
    # Given
    lost = threading.Event()

    def renew(*_):
        lost.set()
        return {"lockSucceeded": False, "reasons": ["AlreadyLocked"]}

    kili_api_gateway.renew_asset_lock.side_effect = renew
    keeper = LockKeeper(QueueUseCases(kili_api_gateway), _context(), AssetId("a"), 0.01)

    # When
    with pytest.warns(
        UserWarning, match="is no longer yours: someone else is working on the asset"
    ):
        keeper.start()
        assert lost.wait(5)
        keeper.stop()

    # Then
    assert keeper.lost_reasons == ["AlreadyLocked"]


def test_the_lock_keeper_survives_a_failed_renewal(kili_api_gateway):
    # Given
    calls = []
    done = threading.Event()

    def renew(*_):
        calls.append(1)
        if len(calls) == 1:
            raise ConnectionError("network down")
        done.set()
        return {"lockSucceeded": True}

    kili_api_gateway.renew_asset_lock.side_effect = renew
    keeper = LockKeeper(QueueUseCases(kili_api_gateway), _context(), AssetId("a"), 0.01)

    # When
    with pytest.warns(UserWarning, match="Could not renew the lock on asset a: network down"):
        keeper.start()
        assert done.wait(5)
        keeper.stop()

    # Then
    assert keeper.lost_reasons == []


def test_it_downloads_the_content_with_the_sdk_http_client(kili_api_gateway):
    # Given
    kili_api_gateway.http_client.get.return_value.content = b"invoice n 42"

    # When
    content = QueueUseCases(kili_api_gateway).read_content("https://cloud/files?id=a")

    # Then
    assert content == b"invoice n 42"
    kili_api_gateway.http_client.get.assert_called_once_with("https://cloud/files?id=a", timeout=60)
    kili_api_gateway.http_client.get.return_value.raise_for_status.assert_called_once()


def test_it_reads_a_content_held_as_text(kili_api_gateway):
    # When
    content = QueueUseCases(kili_api_gateway).read_content("plain text")

    # Then
    assert content == b"plain text"
    kili_api_gateway.http_client.get.assert_not_called()
