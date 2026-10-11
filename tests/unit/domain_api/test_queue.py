"""The queue namespace hands over held assets, and lets them go as the interface does."""

from unittest.mock import MagicMock

import pytest

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.client import Kili
from kili.domain_api import queue as queue_module
from kili.domain_api.queue import QueueAsset, QueueNamespace, _release_held_assets
from kili.exceptions import QueueError

PROJECT = {
    "title": "Bot project",
    "canSkipAsset": True,
    "steps": [
        {"id": "s1", "name": "Label", "type": "DEFAULT", "assignees": [{"id": "me"}]},
        {"id": "s2", "name": "Review", "type": "REVIEW", "assignees": [{"id": "me"}]},
    ],
}


@pytest.fixture()
def gateway() -> MagicMock:
    gateway = MagicMock(spec=KiliAPIGateway)
    gateway.get_current_user.return_value = {"id": "me", "email": "bot@acme.com"}
    gateway.get_project_user.return_value = {"role": "REVIEWER", "activated": True}
    gateway.get_project.return_value = PROJECT
    gateway.renew_asset_lock.return_value = {"lockSucceeded": True, "reasons": None}
    gateway.get_asset_by_id.side_effect = lambda asset_id, fields: {
        "id": asset_id,
        "externalId": f"ext-{asset_id}",
        "content": f"https://storage/{asset_id}",
        "jsonContent": None,
        "jsonMetadata": '{"source": "scanner"}',
    }
    gateway.get_label_opened_with.return_value = None
    gateway.append_to_labels.return_value = {"id": "label-1"}
    gateway.append_many_labels.return_value = [{"id": "review-1"}]
    return gateway


@pytest.fixture()
def queue(gateway: MagicMock, monkeypatch: pytest.MonkeyPatch) -> QueueNamespace:
    monkeypatch.setattr(queue_module, "EMPTY_QUEUE_CHECK_EVERY_SECONDS", 0)
    return QueueNamespace(MagicMock(spec=Kili), gateway)


def _serve(gateway: MagicMock, *answers):
    """Kili's answers to the next-asset requests, in order; nothing once they run out."""
    remaining = list(answers)
    gateway.get_next_asset_to_work_on.side_effect = lambda **_: (
        remaining.pop(0) if remaining else None
    )


def test_it_hands_over_the_next_asset_locked_and_read(queue, gateway):
    # Given
    _serve(gateway, "a")

    # When
    asset = queue.next_to_label(project_id="project")

    # Then
    assert isinstance(asset, QueueAsset)
    assert (asset.id, asset.external_id, asset.content) == ("a", "ext-a", "https://storage/a")
    assert asset.metadata == {"source": "scanner"}
    assert asset.label is None
    assert asset.held
    gateway.renew_asset_lock.assert_called_with("project", "a")
    asset.release()


def test_it_hands_over_the_label_the_asset_comes_back_with(queue, gateway):
    # Given
    _serve(gateway, "a")
    gateway.get_label_opened_with.return_value = {
        "id": "label-0",
        "jsonResponse": '{"JOB": {"categories": [{"name": "A"}]}}',
        "labelType": "DEFAULT",
        "author": {"id": "me", "email": "bot@acme.com"},
        "isSentBackToQueue": True,
        "createdAt": "2026-10-12T00:00:00Z",
    }

    # When
    asset = queue.next_to_label(project_id="project")

    # Then
    assert asset is not None
    assert asset.label is not None
    assert asset.label["json_response"] == {"JOB": {"categories": [{"name": "A"}]}}
    assert asset.label["is_sent_back_to_queue"] is True
    asset.release()


def test_it_returns_nothing_on_an_empty_queue(queue, gateway):
    # Given
    _serve(gateway)

    # When
    asset = queue.next_to_review(project_id="project")

    # Then
    assert asset is None


def test_it_passes_over_an_asset_whose_lock_is_refused(queue, gateway):
    # Given
    _serve(gateway, "taken", "free")
    gateway.renew_asset_lock.side_effect = [
        {"lockSucceeded": False, "reasons": ["AlreadyLocked"]},
        {"lockSucceeded": True, "reasons": None},
        {"lockSucceeded": True, "reasons": None},
    ]

    # When
    asset = queue.next_to_label(project_id="project")

    # Then
    assert asset is not None
    assert asset.id == "free"
    gateway.delete_asset_locks.assert_called_once_with("project", "taken")
    second_ask = gateway.get_next_asset_to_work_on.call_args_list[1].kwargs
    assert second_ask["viewed_asset_ids"] == ["taken", "free"]
    assert second_ask["given_back_asset_ids"] == ["taken"]
    asset.release()


def test_it_releases_an_asset_it_could_not_read(queue, gateway):
    # Given
    _serve(gateway, "a")
    gateway.get_asset_by_id.side_effect = ConnectionError("network down")

    # When / Then
    with pytest.raises(ConnectionError):
        queue.next_to_label(project_id="project")
    gateway.delete_asset_locks.assert_called_once_with("project", "a")


def test_a_submit_records_the_label_then_leaves_the_asset(queue, gateway):
    # Given
    _serve(gateway, "a")
    asset = queue.next_to_label(project_id="project")
    assert asset is not None

    # When
    label_id = asset.submit(json_response={"JOB": {}})

    # Then
    assert label_id == "label-1"
    assert asset.outcome == "submitted"
    assert not asset.held
    gateway.delete_asset_locks.assert_called_once_with("project", "a")


def test_an_approval_without_corrections_approves_the_label_under_review(queue, gateway):
    # Given
    _serve(gateway, "a")
    gateway.get_label_opened_with.return_value = {"id": "label-0", "jsonResponse": '{"JOB": 1}'}
    asset = queue.next_to_review(project_id="project")
    assert asset is not None

    # When
    review_id = asset.approve()

    # Then
    assert review_id == "review-1"
    label = gateway.append_many_labels.call_args.kwargs["data"].labels_data[0]
    assert (label.json_response, label.referenced_label_id) == ({"JOB": 1}, "label-0")
    assert asset.outcome == "approved"


def test_an_approval_with_corrections_submits_them(queue, gateway):
    # Given
    _serve(gateway, "a")
    gateway.get_label_opened_with.return_value = {"id": "label-0", "jsonResponse": '{"JOB": 1}'}
    asset = queue.next_to_review(project_id="project")
    assert asset is not None

    # When
    asset.approve(json_response={"JOB": 2})

    # Then
    label = gateway.append_many_labels.call_args.kwargs["data"].labels_data[0]
    assert label.json_response == {"JOB": 2}


def test_a_send_back_sends_the_label_under_review_back(queue, gateway):
    # Given
    _serve(gateway, "a")
    gateway.get_label_opened_with.return_value = {"id": "label-0", "jsonResponse": "{}"}
    gateway.send_asset_back_to_queue.return_value = {
        "succeeded": [{"assetId": "a"}],
        "declined": [],
        "failed": [],
    }
    asset = queue.next_to_review(project_id="project")
    assert asset is not None

    # When
    asset.send_back()

    # Then
    gateway.send_asset_back_to_queue.assert_called_once_with("project", "a", "label-0")
    assert asset.outcome == "sent back"


def test_a_skip_records_the_reason(queue, gateway):
    # Given
    _serve(gateway, "a")
    asset = queue.next_to_label(project_id="project")
    assert asset is not None

    # When
    asset.skip(reason="blurry")

    # Then
    gateway.skip_asset_with_reason.assert_called_once_with("project", "a", "blurry")
    assert asset.outcome == "skipped"


@pytest.mark.parametrize(
    ("mode", "action", "message"),
    [
        ("label", lambda asset: asset.approve(), "held to label, not to review"),
        ("label", lambda asset: asset.send_back(), "held to label, not to review"),
        ("review", lambda asset: asset.submit({}), "held to review, not to label"),
    ],
)
def test_an_action_of_the_other_mode_is_refused(queue, gateway, mode, action, message):
    # Given
    _serve(gateway, "a")
    asset = queue.next_to_label("project") if mode == "label" else queue.next_to_review("project")
    assert asset is not None

    # When / Then
    with pytest.raises(QueueError, match=message):
        action(asset)
    assert asset.held
    asset.release()


def test_an_asset_let_go_cannot_be_acted_on_again(queue, gateway):
    # Given
    _serve(gateway, "a")
    asset = queue.next_to_label(project_id="project")
    assert asset is not None
    asset.submit(json_response={})

    # When / Then
    with pytest.raises(QueueError, match="was already submitted"):
        asset.submit(json_response={})
    with pytest.raises(QueueError, match="was already submitted"):
        asset.release()
    gateway.append_to_labels.assert_called_once()


def test_the_context_manager_gives_the_asset_back_when_the_code_fails(queue, gateway):
    # Given
    _serve(gateway, "a")
    asset = queue.next_to_label(project_id="project")
    assert asset is not None

    # When
    with pytest.raises(ValueError, match="model crashed"), asset:
        raise ValueError("model crashed")

    # Then
    assert asset.outcome == "released"
    gateway.delete_asset_locks.assert_called_once_with("project", "a")


def test_the_loop_serves_every_asset_until_the_queue_is_empty(queue, gateway):
    # Given
    _serve(gateway, "a", "b")

    # When
    outcomes = []
    for asset in queue.iter_to_label(project_id="project"):
        asset.submit(json_response={})
        outcomes.append((asset.id, asset.outcome))

    # Then
    assert outcomes == [("a", "submitted"), ("b", "submitted")]
    asks = [call.kwargs for call in gateway.get_next_asset_to_work_on.call_args_list]
    assert [ask["viewed_asset_ids"] for ask in asks] == [["a", "b"]] * 8
    assert all(ask["given_back_asset_ids"] == [] for ask in asks)


def test_the_loop_asks_again_before_calling_the_queue_empty(queue, gateway):
    # Given an asset that frees up after two empty answers, as a consensus seat does
    _serve(gateway, "a", None, None, "b")

    # When
    served = []
    for asset in queue.iter_to_label(project_id="project"):
        served.append(asset.id)
        asset.submit(json_response={})

    # Then
    assert served == ["a", "b"]
    assert gateway.get_next_asset_to_work_on.call_count == 4 + 1 + 5


def test_a_single_ask_answers_at_once(queue, gateway):
    # Given
    _serve(gateway)

    # When
    asset = queue.next_to_label(project_id="project")

    # Then
    assert asset is None
    gateway.get_next_asset_to_work_on.assert_called_once()


def test_the_loop_gives_back_an_asset_left_undecided_and_is_not_served_it_again(queue, gateway):
    # Given
    _serve(gateway, "a", "b")

    # When
    served = [asset for asset in queue.iter_to_label(project_id="project")]

    # Then
    assert [asset.outcome for asset in served] == ["released", "released"]
    last_ask = gateway.get_next_asset_to_work_on.call_args_list[-1].kwargs
    assert last_ask["given_back_asset_ids"] == ["a", "b"]


def test_the_loop_gives_the_asset_back_at_once_when_the_code_fails(queue, gateway):
    # Given
    _serve(gateway, "a", "b")
    released_when_raised = []

    # When
    try:
        for _asset in queue.iter_to_label(project_id="project"):
            raise ValueError("model crashed")
    except ValueError:
        released_when_raised.append(gateway.delete_asset_locks.call_count)

    # Then
    assert released_when_raised == [1]
    gateway.delete_asset_locks.assert_called_once_with("project", "a")
    assert gateway.get_next_asset_to_work_on.call_count == 1


def test_a_with_block_in_a_loop_kept_aside_gives_the_asset_back_when_the_code_fails(queue, gateway):
    # Given
    _serve(gateway, "a", "b")
    loop = queue.iter_to_label(project_id="project")

    # When
    with pytest.raises(ValueError, match="model crashed"):
        for asset in loop:
            with asset:
                raise ValueError("model crashed")

    # Then
    gateway.delete_asset_locks.assert_called_once_with("project", "a")
    loop.close()


def test_the_assets_still_held_are_given_back_when_the_process_exits(queue, gateway):
    # Given
    _serve(gateway, "a", "b")
    held = queue.next_to_label(project_id="project")
    done = queue.next_to_label(project_id="project")
    assert held is not None
    assert done is not None
    done.submit(json_response={})
    gateway.delete_asset_locks.reset_mock()

    # When
    _release_held_assets()

    # Then
    gateway.delete_asset_locks.assert_called_once_with("project", "a")
    assert held.outcome == "released"


def test_the_loop_says_why_the_account_cannot_review(queue, gateway):
    # Given
    gateway.get_project_user.return_value = {"role": "LABELER", "activated": True}

    # When / Then
    with pytest.raises(QueueError, match="is LABELER on project"):
        next(queue.iter_to_review(project_id="project"))
    gateway.get_next_asset_to_work_on.assert_not_called()
