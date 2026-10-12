"""Queue domain namespace: a project member's script served its assets like a teammate.

The labeling interface hands a person one asset at a time, keeps it theirs while they work on it,
and moves on when they submit, skip or leave it. This namespace hands a script the same assets,
through the same requests, so people and scripts can work on one project side by side.
"""

import atexit
import json
import signal
import threading
import time
import warnings
import weakref
from collections.abc import Generator, Iterator
from contextlib import contextmanager
from types import TracebackType
from typing import Any, Optional

from typeguard import typechecked

from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
from kili.domain.asset import AssetId
from kili.domain.label import LabelId
from kili.domain.project import ProjectId
from kili.domain_api.base import DomainNamespace
from kili.exceptions import QueueError
from kili.use_cases.queue import (
    EMPTY_QUEUE_CHECK_EVERY_SECONDS,
    EMPTY_QUEUE_CHECKS,
    LockKeeper,
    QueueContext,
    QueueMode,
    QueueUseCases,
    describe_lock_refusal,
    seconds_since,
)

# The assets this process holds: given back when it exits, as the interface gives its asset back when
# its tab closes, rather than left locked until the lock expires.
_HELD_ASSETS: "weakref.WeakSet[QueueAsset]" = weakref.WeakSet()


@atexit.register
def _release_held_assets() -> None:
    for asset in list(_HELD_ASSETS):
        if asset.held:
            try:
                asset.release()
            except Exception:  # pylint: disable=broad-exception-caught
                pass  # exiting: the lock expires on its own within minutes


@contextmanager
def _interrupts_deferred() -> Iterator[None]:
    """Hold Ctrl-C back while an asset changes hands, then let it through.

    Kili locks an asset as it answers a next-asset request: a KeyboardInterrupt raised before the
    SDK knows which asset that is would leave it locked to nobody's code until the lock expires.
    Signals are only handled in the main thread: elsewhere this changes nothing.
    """
    if threading.current_thread() is not threading.main_thread():
        yield
        return
    previous = signal.getsignal(signal.SIGINT)
    if previous is None:  # a handler installed outside Python: left as it is
        yield
        return
    interrupted: list[int] = []
    signal.signal(signal.SIGINT, lambda signum, _frame: interrupted.append(signum))
    try:
        yield
    finally:
        signal.signal(signal.SIGINT, previous)
        if interrupted:
            signal.raise_signal(signal.SIGINT)


def _parsed(value: Any) -> Any:
    """A JSON string the API returns, decoded; anything else as it is."""
    if isinstance(value, str):
        try:
            return json.loads(value)
        except ValueError:
            return value
    return value


# the asset's own fields, the ones the interface shows, are its attributes
class QueueAsset:  # pylint: disable=too-many-instance-attributes
    """An asset of your queue, yours until you submit, approve, send back, skip or release it.

    While you hold it, nobody else is served it: its lock is renewed in the background, as the
    labeling interface renews it while a person has the asset open — for as long as your code
    takes. Use it as a context manager to give it back if your code raises. An asset your code
    drops without acting on it is given back within 30 s, and those still held when Python exits
    at once.

    Attributes:
        id: The asset's id.
        external_id: The asset's external id.
        content: The asset's content: a URL to download it from (`read_content()` does it), or
            the text itself.
        json_content: The asset's JSON content (rich text, video frames, ...), decoded, or None.
        metadata: The asset's metadata, as a dict.
        label: The label the interface opens the asset with, or None: when labeling, your own
            label sent back to you for correction, or a model's prediction; when reviewing, the
            label to review. A dict with `id`, `json_response`, `label_type`, `author` (`id`,
            `email`), `is_sent_back_to_queue` and `created_at`.
        project_id: The project the asset belongs to.
        mode: `"label"` for an asset to label, `"review"` for one to review.
        outcome: None while you hold the asset, then what you did with it: `"submitted"`,
            `"approved"`, `"sent back"`, `"skipped"` or `"released"`.
    """

    def __init__(
        self,
        use_cases: QueueUseCases,
        context: QueueContext,
        asset: dict,
        label: Optional[dict],
    ) -> None:
        """Hold an asset just handed over; its lock is renewed from now on."""
        self._use_cases = use_cases
        self._context = context
        self._started_at = time.monotonic()
        self.id = AssetId(asset["id"])
        self.external_id: str = asset.get("externalId") or ""
        self.content: str = asset.get("content") or ""
        self.json_content: Any = _parsed(asset.get("jsonContent")) or None
        self.metadata: dict = _parsed(asset.get("jsonMetadata")) or {}
        self.label: Optional[dict] = (
            {
                "id": label["id"],
                "json_response": _parsed(label.get("jsonResponse")) or {},
                "label_type": label.get("labelType"),
                "author": label.get("author") or {},
                "is_sent_back_to_queue": label.get("isSentBackToQueue"),
                "created_at": label.get("createdAt"),
            }
            if label
            else None
        )
        # what a submit refers to, as the interface decides it (appendToLabels.ts): the label the
        # asset was opened with — or, for an autosave or a correction, the label that one is based on
        self._reference_id: Optional[LabelId] = None
        if label:
            based_on = (label.get("referencedLabel") or {}).get("id")
            is_derived = label.get("labelType") == "AUTOSAVE" or label.get("isCorrected")
            self._reference_id = LabelId(based_on if is_derived and based_on else label["id"])
        self.project_id: ProjectId = context.project_id
        self.mode: QueueMode = context.mode
        self.outcome: Optional[str] = None
        self._keeper = LockKeeper(use_cases, context, self.id, owner=self)
        self._keeper.start()
        _HELD_ASSETS.add(self)

    @property
    def held(self) -> bool:
        """Whether the asset is still yours: not submitted, approved, sent back, skipped or released."""
        return self.outcome is None

    @property
    def seconds_held(self) -> float:
        """Seconds since the asset was handed to you: the time a submit records as yours."""
        return seconds_since(self._started_at)

    def read_content(self) -> bytes:
        """Download the asset's content: the file `content` points to, or the text it holds.

        Returns:
            The content's bytes — `.decode("utf-8")` them for a text asset.
        """
        return self._use_cases.read_content(self.content)

    def submit(self, json_response: dict) -> str:
        """Submit your label: the asset moves on as after a submit in the labeling interface.

        The label is yours, with the time since the asset was handed to you; the asset goes to its
        next step (a review step, or done) with the status that step gives it. In a consensus step
        it stays until every expected labeler has submitted.

        Args:
            json_response: The label, in Kili's json response format.

        Returns:
            The id of the label created.
        """
        self._check_held("submit", "label")
        label = self._use_cases.submit(
            self._context,
            self.id,
            json_response,
            seconds_to_label=self.seconds_held,
            referenced_label_id=self._reference_id,
        )
        self._let_go("submitted")
        return label["id"]

    def approve(self, json_response: Optional[dict] = None) -> str:
        """Approve the asset you review, with or without corrections, as the review interface does.

        Args:
            json_response: Your corrected label. Without it, the label under review is approved
                as it is.

        Returns:
            The id of the review label created.
        """
        self._check_held("approve", "review")
        if self.label is None and json_response is None:
            raise QueueError(
                f"Asset {self.id} carries no label to approve: pass the label to approve as"
                " json_response, or send it back."
            )
        reviewed = self.label["json_response"] if self.label else {}
        label = self._use_cases.submit(
            self._context,
            self.id,
            json_response if json_response is not None else reviewed,
            seconds_to_label=self.seconds_held,
            referenced_label_id=self._reference_id,
        )
        self._let_go("approved")
        return label["id"]

    def send_back(self) -> None:
        """Send the asset you review back to its labelers, as the review dialog's Send back does."""
        self._check_held("send back", "review")
        self._use_cases.send_back(
            self._context, self.id, LabelId(self.label["id"]) if self.label else None
        )
        self._let_go("sent back")

    def skip(self, reason: str) -> None:
        """Skip the asset you cannot label, with a reason — as the labeling interface's Skip.

        As in the app, a skipped asset leaves the queue — yours and everyone's — with your reason,
        until someone unskips it (`kili.assets.unskip`). Refused when the project does not let its
        members skip, and on an asset held for review, which the review interface cannot skip.

        Args:
            reason: Why the asset cannot be labeled; shown with the asset in Kili.
        """
        self._check_held("skip", None)
        self._use_cases.skip(self._context, self.id, reason)
        self._let_go("skipped")

    def release(self) -> None:
        """Give the asset back without labeling it: the next member who asks is served it at once."""
        if not self.held:
            raise QueueError(f"Asset {self.id} was already {self.outcome}: it is no longer yours.")
        self._keeper.stop()
        self.outcome = "released"
        self._use_cases.release(self._context, self.id)

    def __enter__(self) -> "QueueAsset":
        """Hold the asset for the block."""
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """Give the asset back if the block ends without submitting, skipping or releasing it."""
        if self.held:
            self.release()

    def __repr__(self) -> str:
        """Return a short description of the held asset."""
        return (
            f"QueueAsset(id={self.id!r}, external_id={self.external_id!r}, mode={self.mode!r},"
            f" outcome={self.outcome!r})"
        )

    def _check_held(self, action: str, mode: Optional[QueueMode]) -> None:
        if not self.held:
            raise QueueError(
                f"Asset {self.id} was already {self.outcome}: it is no longer yours to {action}."
            )
        if mode is not None and mode != self.mode:
            alternatives = (
                "submit(), skip() or release()"
                if self.mode == "label"
                else "approve(), send_back() or release()"
            )
            raise QueueError(
                f"Asset {self.id} is held to {self.mode}, not to {mode}: use {alternatives}."
            )
        if self._keeper.lost_reasons:
            raise QueueError(
                f"Asset {self.id} is no longer yours:"
                f" {describe_lock_refusal(self._keeper.lost_reasons)}."
                " Give it back with release() and ask for your next asset."
            )

    def _let_go(self, outcome: str) -> None:
        # the action went through: stop holding the asset, and leave it as the interface does
        self._keeper.stop()
        self.outcome = outcome
        try:
            self._use_cases.release(self._context, self.id)
        except Exception as error:  # pylint: disable=broad-exception-caught
            # the action went through: a lock left behind expires on its own within minutes
            warnings.warn(
                f"Asset {self.id} was {outcome}, but its lock could not be released: {error}.",
                stacklevel=3,
            )


class _QueueSession:
    """The assets one member was served, kept across next calls as the interface keeps them."""

    def __init__(self, use_cases: QueueUseCases, context: QueueContext) -> None:
        self._use_cases = use_cases
        self._context = context
        self.viewed: list[AssetId] = []
        self.given_back: list[AssetId] = []

    def hand_over(self) -> Optional[QueueAsset]:
        """The next asset, locked and read, or None when the queue is empty."""
        while True:
            asset_id = self._use_cases.next_asset(self._context, self.viewed, self.given_back)
            if asset_id is None:
                return None
            self.viewed.append(asset_id)
            try:
                # the interface renews the lock as it opens the asset; on a consensus step, that
                # is where the number of labels the asset takes is decided
                refused = self._use_cases.renew_lock(self._context, asset_id)
                read = None if refused else self._use_cases.read_asset(self._context, asset_id)
            except BaseException:  # a failure or an interrupt: the asset is locked, give it back
                self._use_cases.release(self._context, asset_id)
                raise
            if read is None:
                self._use_cases.release(self._context, asset_id)
                self.given_back.append(asset_id)
                continue
            asset, label = read
            return QueueAsset(self._use_cases, self._context, asset, label)


def _hand_over(session: _QueueSession) -> Optional[QueueAsset]:
    """The session's next asset, handed over whole or given back, whatever interrupts it."""
    asset = None
    try:
        with _interrupts_deferred():
            asset = session.hand_over()
    except BaseException:
        if asset is not None and asset.held:
            with _interrupts_deferred():
                asset.release()
        raise
    return asset


class QueueNamespace(DomainNamespace):
    """Your project queue, served to your script as the labeling interface serves it to you.

    Ask for your next asset to label or to review — the one the interface would open for you:
    same priorities, same assignments, same workflow step. It stays yours, and nobody else's,
    until you submit, approve, send back, skip or release it. The `iter_*` methods do it in a
    loop until your queue is empty.

    It works as the account of the API key: give your bot an account of its own, a member of
    the project with the labeler or reviewer role, assigned to the workflow steps it works on.

    Examples:
        >>> for asset in kili.queue.iter_to_label(project_id="my_project"):
        ...     asset.submit(json_response=my_model(asset.content))
    """

    def __init__(self, client, gateway: KiliAPIGateway) -> None:
        """Initialize the queue namespace.

        Args:
            client: The Kili client instance
            gateway: The KiliAPIGateway instance for API operations
        """
        super().__init__(client, gateway, "queue")

    @typechecked
    def next_to_label(self, project_id: str) -> Optional[QueueAsset]:
        """Get your next asset to label, held by you until you act on it.

        The asset is the one the labeling interface would open for you now. Give it back with
        `release()` if you do not label it: until then, nobody else is served it. Each call starts
        afresh, as the interface's Start Labeling: an asset just released is the next one served
        again — the `iter_*` loops pass over what they gave back.

        Args:
            project_id: The project's id.

        Returns:
            The asset, or None when nothing is free for you to label at this moment. An asset
            another member has just been handed can free a seat a second later on a consensus
            step: `iter_to_label` asks again before it ends.

        Raises:
            QueueError: When your account cannot label on the project — not a member, or on none
                of its labeling steps.
        """
        return _hand_over(self._session(ProjectId(project_id), "label"))

    @typechecked
    def next_to_review(self, project_id: str) -> Optional[QueueAsset]:
        """Get your next asset to review, held by you until you act on it.

        The asset is the one the review interface would open for you now, with the label to
        review in `label`.

        Args:
            project_id: The project's id.

        Returns:
            The asset, or None when nothing is free for you to review at this moment.

        Raises:
            QueueError: When your account cannot review on the project — a labeler role, or on
                none of its review steps.
        """
        return _hand_over(self._session(ProjectId(project_id), "review"))

    @typechecked
    def iter_to_label(
        self,
        project_id: str,
        max_assets: Optional[int] = None,
        max_seconds: Optional[float] = None,
    ) -> Generator[QueueAsset, None, None]:
        """Go through your labeling queue, one asset after the other, until it is empty.

        The loop ends once Kili has had nothing for you five times in five seconds, as the queue
        page asks again before it greys out its button — or earlier, after `max_assets` assets,
        or once `max_seconds` have passed: a bot run on a schedule stops on its own. Each asset is
        yours while your code works on it. Submit or skip it in the loop's body; one left
        undecided, or released, is given back and not served again in this loop. If your code
        raises — Ctrl-C included — the asset is given back at once and the exception goes on,
        when the loop runs over the call itself, as below. A loop kept in a variable is only
        closed once the variable goes: give the asset back with `with asset:` around the body
        instead.

        Args:
            project_id: The project's id.
            max_assets: The most assets the loop hands over. None: no limit.
            max_seconds: No asset is handed over once this many seconds have passed since the
                loop started; the asset your code is working on is not cut short. None: no limit.

        Returns:
            An iterator over your assets to label, handed over one at a time.

        Raises:
            QueueError: When your account cannot label on the project.
            ValueError: When `max_assets` or `max_seconds` is not positive.

        Examples:
            >>> for asset in kili.queue.iter_to_label(project_id="my_project"):
            ...     prediction = my_model(asset.content)
            ...     if prediction is None:
            ...         asset.skip(reason="Unreadable document")
            ...     else:
            ...         asset.submit(json_response=prediction)

            Run every hour, a bot that stops after 500 assets or 50 minutes:

            >>> for asset in kili.queue.iter_to_label(
            ...     project_id="my_project", max_assets=500, max_seconds=50 * 60
            ... ):
            ...     asset.submit(json_response=my_model(asset.content))
        """
        return self._iterate(ProjectId(project_id), "label", max_assets, max_seconds)

    @typechecked
    def iter_to_review(
        self,
        project_id: str,
        max_assets: Optional[int] = None,
        max_seconds: Optional[float] = None,
    ) -> Generator[QueueAsset, None, None]:
        """Go through your review queue, one asset after the other, until it is empty.

        Approve or send back each asset in the loop's body; one left undecided, or released, is
        given back. If your code raises — Ctrl-C included — the asset is given back at once and
        the exception goes on, when the loop runs over the call itself, as for `iter_to_label`.
        `max_assets` and `max_seconds` stop the loop earlier, as for `iter_to_label`.

        Args:
            project_id: The project's id.
            max_assets: The most assets the loop hands over. None: no limit.
            max_seconds: No asset is handed over once this many seconds have passed since the
                loop started; the asset your code is working on is not cut short. None: no limit.

        Returns:
            An iterator over your assets to review, handed over one at a time, each with the
            label to review in `label`.

        Raises:
            QueueError: When your account cannot review on the project.
            ValueError: When `max_assets` or `max_seconds` is not positive.
        """
        return self._iterate(ProjectId(project_id), "review", max_assets, max_seconds)

    def _session(self, project_id: ProjectId, mode: QueueMode) -> _QueueSession:
        use_cases = QueueUseCases(self._gateway)
        return _QueueSession(use_cases, use_cases.get_context(project_id, mode))

    def _iterate(
        self,
        project_id: ProjectId,
        mode: QueueMode,
        max_assets: Optional[int],
        max_seconds: Optional[float],
    ) -> Generator[QueueAsset, None, None]:
        # checked as the loop is made, not at its first turn
        if max_assets is not None and max_assets < 1:
            raise ValueError(f"max_assets must be 1 or more, not {max_assets}.")
        if max_seconds is not None and max_seconds <= 0:
            raise ValueError(f"max_seconds must be more than 0, not {max_seconds}.")
        return self._loop(project_id, mode, max_assets, max_seconds)

    def _loop(
        self,
        project_id: ProjectId,
        mode: QueueMode,
        max_assets: Optional[int],
        max_seconds: Optional[float],
    ) -> Generator[QueueAsset, None, None]:
        session = self._session(project_id, mode)
        deadline = None if max_seconds is None else time.monotonic() + max_seconds
        handed = 0
        while max_assets is None or handed < max_assets:
            asset = None
            try:
                asset = _next_before(session, deadline)
                if asset is None:
                    return
                handed += 1
                yield asset
            finally:
                # reached when the body moves on, raises or breaks: an asset left undecided is
                # given back, and the next calls pass it over as the interface passes over one
                # left without a submit
                if asset is not None:
                    with _interrupts_deferred():
                        if asset.held:
                            asset.release()
                    if asset.outcome == "released":
                        session.given_back.append(asset.id)


def _next_before(session: _QueueSession, deadline: Optional[float]) -> Optional[QueueAsset]:
    """The next asset, asked again a few times before the queue is called empty; None past the deadline."""
    for check in range(EMPTY_QUEUE_CHECKS + 1):
        if check:
            pause = EMPTY_QUEUE_CHECK_EVERY_SECONDS
            if deadline is not None:
                pause = min(pause, max(0.0, deadline - time.monotonic()))
            time.sleep(pause)
        if deadline is not None and time.monotonic() >= deadline:
            return None
        asset = _hand_over(session)
        if asset is not None:
            return asset
    return None
