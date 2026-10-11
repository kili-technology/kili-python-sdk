"""Queue use cases: a project member served their assets as the labeling interface serves them.

The interface is the reference for every step — which asset comes next (`loadAsset.ts`), how long it
stays the member's (`useRenewLock.ts`), what a submit, a skip, an approval or a send back sends — so
a script working through its queue is, to Kili and to the people beside it, one more member.
"""

import threading
import time
import warnings
from dataclasses import dataclass, field
from typing import Literal, Optional

from kili.domain.asset import AssetId
from kili.domain.label import LabelId
from kili.domain.project import ProjectId
from kili.domain.user import UserId
from kili.exceptions import GraphQLError, QueueError
from kili.use_cases.base import BaseUseCases
from kili.use_cases.label import LOCK_ERRORS, LabelUseCases
from kili.use_cases.label.types import LabelToCreateUseCaseInput

QueueMode = Literal["label", "review"]

# The interface renews its lock every 30 s (label-frontend's DEFAULT_RENEW_LOCK_INTERVAL); a lock
# that is not renewed expires after 5 minutes and the asset is served to someone else.
RENEW_LOCK_EVERY_SECONDS = 30.0

# An empty answer is not always an empty queue: an asset a member has just been served counts one
# seat until their interface renews its lock, which is when a consensus step decides how many labels
# it takes. The queue page asks again every second, five times (label-frontend's useHasNextAsset.ts),
# so a loop does the same before it calls the queue empty.
EMPTY_QUEUE_CHECKS = 5
EMPTY_QUEUE_CHECK_EVERY_SECONDS = 1.0

STEP_TYPE_OF_MODE: dict[QueueMode, str] = {"label": "DEFAULT", "review": "REVIEW"}
ROLES_WHO_REVIEW = ("REVIEWER", "TEAM_MANAGER", "ADMIN")

ASSET_FIELDS = ("id", "externalId", "content", "jsonContent", "jsonMetadata")
LABEL_FIELDS = (
    "id",
    "jsonResponse",
    "labelType",
    "author.id",
    "author.email",
    "isSentBackToQueue",
    "createdAt",
)

LOCK_REJECT_REASONS = {
    "AlreadyAssigned": "the asset is assigned to someone else",
    "AlreadyLocked": "someone else is working on the asset",
    "NotInStepAssignees": "you are not assigned to the asset's current step",
    "AlreadyHaveLabelOnCurrentStep": "you already submitted a label on the asset's current step",
    "AssetInDoneStepStatus": "the asset's current step is already done",
    "BlockedByEnforceStepSeparation": "you already worked on the asset in another step",
}


@dataclass
class QueueContext:
    """Who works on which project's queue, and what that project lets them do."""

    project_id: ProjectId
    project_title: str
    user_id: UserId
    user_email: str
    role: str
    mode: QueueMode
    can_skip_asset: bool
    steps: list[dict] = field(default_factory=list)


class QueueUseCases(BaseUseCases):
    """Queue use cases."""

    def get_context(self, project_id: ProjectId, mode: QueueMode) -> QueueContext:
        """Check that the member can work on the project's queue, and say why not otherwise.

        The interface only greys its button out on an empty queue; a script is told the cause —
        no membership, a role that cannot review, no workflow step of that kind assigned to it.
        """
        me = self._kili_api_gateway.get_current_user(fields=("id", "email"))
        user_id, email = UserId(me["id"]), me["email"]
        project_user = self._kili_api_gateway.get_project_user(project_id, user_id)
        if project_user is None:
            raise QueueError(
                f"{email} is not a member of project {project_id}, or the project does not exist:"
                " ask one of its admins to add this account to the project."
            )
        project = self._kili_api_gateway.get_project(
            project_id,
            fields=(
                "title",
                "canSkipAsset",
                "steps.id",
                "steps.name",
                "steps.type",
                "steps.assignees.id",
            ),
        )
        title = project.get("title") or project_id
        if project_user.get("activated") is False:
            raise QueueError(
                f"{email} is deactivated on project '{title}' ({project_id}): ask one of its"
                " admins to activate this account again."
            )
        role = project_user["role"]
        if mode == "review" and role not in ROLES_WHO_REVIEW:
            raise QueueError(
                f"{email} is {role} on project '{title}' ({project_id}): reviewing needs one of"
                " the REVIEWER, TEAM_MANAGER or ADMIN roles. Ask a project admin to change it, or"
                " work on the labeling queue instead."
            )
        steps = project.get("steps") or []
        if steps:  # a workflow with steps serves a member only the steps they are assigned to
            step_type = STEP_TYPE_OF_MODE[mode]
            steps_of_mode = [step for step in steps if step.get("type") == step_type]
            kind = "labeling" if mode == "label" else "review"
            if not steps_of_mode:
                raise QueueError(
                    f"Project '{title}' ({project_id}) has no {kind} step: there is nothing to"
                    f" {mode} in its workflow."
                )
            if not any(
                user_id in {assignee["id"] for assignee in step.get("assignees") or []}
                for step in steps_of_mode
            ):
                names = ", ".join(f"'{step['name']}'" for step in steps_of_mode)
                raise QueueError(
                    f"{email} is assigned to none of the {kind} steps of project '{title}'"
                    f" ({project_id}): {names}. Ask a project admin to add this account to one."
                )
        return QueueContext(
            project_id=project_id,
            project_title=title,
            user_id=user_id,
            user_email=email,
            role=role,
            mode=mode,
            can_skip_asset=bool(project.get("canSkipAsset")),
            steps=steps,
        )

    def next_asset(
        self,
        context: QueueContext,
        viewed_asset_ids: list[AssetId],
        given_back_asset_ids: list[AssetId],
    ) -> Optional[AssetId]:
        """The member's next asset, already locked to them, or None when their queue is empty."""
        return self._kili_api_gateway.get_next_asset_to_work_on(
            project_id=context.project_id,
            review=context.mode == "review",
            viewed_asset_ids=viewed_asset_ids,
            given_back_asset_ids=given_back_asset_ids,
        )

    def read_asset(self, context: QueueContext, asset_id: AssetId) -> tuple[dict, Optional[dict]]:
        """The asset as the interface opens it: its content and metadata, and the label it carries."""
        asset = self._kili_api_gateway.get_asset_by_id(asset_id, fields=ASSET_FIELDS)
        label = self._kili_api_gateway.get_label_opened_with(
            asset_id, context.user_id, review=context.mode == "review", fields=LABEL_FIELDS
        )
        return asset, label

    def read_content(self, content: str) -> bytes:
        """The asset's content: the file its URL points to, or the text it holds.

        A URL of Kili's own storage is downloaded with the API key, as the SDK's other downloads.
        """
        if not content.startswith(("http://", "https://")):
            return content.encode("utf-8")
        response = self._kili_api_gateway.http_client.get(content, timeout=60)
        response.raise_for_status()
        return response.content

    def renew_lock(self, context: QueueContext, asset_id: AssetId) -> list[str]:
        """Take or renew the member's lock on the asset; the reasons it was refused, if it was."""
        result = self._kili_api_gateway.renew_asset_lock(context.project_id, asset_id)
        if result.get("lockSucceeded"):
            return []
        return list(result.get("reasons") or ["AlreadyLocked"])

    def release(self, context: QueueContext, asset_id: AssetId) -> None:
        """Release the member's lock: the asset is served to the next member who asks."""
        self._kili_api_gateway.delete_asset_locks(context.project_id, asset_id)

    def submit(
        self,
        context: QueueContext,
        asset_id: AssetId,
        json_response: dict,
        seconds_to_label: float,
        reviewed_label_id: Optional[LabelId] = None,
    ) -> dict:
        """Submit the member's label — DEFAULT when labeling, REVIEW when reviewing.

        Either moves the asset on in its workflow as the interface's submit does. A label goes
        through `appendToLabels`, addressed by the asset's id as the interface addresses it: the
        mutations addressing assets by a list of ids only reach those a labeler already labeled.
        A review goes through the mutation of `kili.labels.create_review`, which links it to the
        label it reviews. A lock someone else holds is refused by both.
        """
        label_use_cases = LabelUseCases(self._kili_api_gateway)
        try:
            if context.mode == "label":
                return label_use_cases.append_to_labels(
                    author_id=context.user_id,
                    json_response=json_response,
                    label_type="DEFAULT",
                    seconds_to_label=round(seconds_to_label),
                    asset_id=asset_id,
                    fields=("id",),
                )
            return label_use_cases.append_labels(
                labels=[
                    LabelToCreateUseCaseInput(
                        asset_external_id=None,
                        asset_id=asset_id,
                        author_id=context.user_id,
                        json_response=json_response,
                        label_type="REVIEW",
                        model_name=None,
                        referenced_label_id=reviewed_label_id,
                        seconds_to_label=round(seconds_to_label),
                    )
                ],
                label_type="REVIEW",
                overwrite=False,
                project_id=context.project_id,
                fields=("id",),
                disable_tqdm=True,
            )[0]
        except GraphQLError as error:
            reason = (error.context or {}).get("reason")
            if reason in LOCK_ERRORS:
                raise QueueError(
                    f"Asset {asset_id} could not be submitted: {LOCK_ERRORS[reason]}"
                ) from error
            raise

    def skip(self, context: QueueContext, asset_id: AssetId, reason: str) -> None:
        """Skip the asset with a reason — refused where the labeling interface would not skip."""
        if context.mode == "review":
            raise QueueError(
                "Only an asset held to label can be skipped, as in the app: the review interface"
                " has no skip. Approve it, send it back, or give it back with release()."
            )
        if not context.can_skip_asset:
            raise QueueError(
                f"Project '{context.project_title}' ({context.project_id}) does not let its members"
                " skip assets. Submit a label, or give the asset back with release(); a project"
                " admin can allow skipping in the project's settings."
            )
        if not reason.strip():
            raise QueueError("A skip needs a reason: say why the asset cannot be labeled.")
        self._kili_api_gateway.skip_asset_with_reason(context.project_id, asset_id, reason)

    def send_back(
        self, context: QueueContext, asset_id: AssetId, label_id: Optional[LabelId]
    ) -> None:
        """Send the reviewed asset back to its labelers, as the review dialog's Send back does."""
        outcome = self._kili_api_gateway.send_asset_back_to_queue(
            context.project_id, asset_id, label_id
        )
        if outcome.get("failed"):
            raise QueueError(
                f"Sending asset {asset_id} back failed: {outcome['failed'][0].get('details')}."
                " Its state is unchanged; try again."
            )
        if outcome.get("declined"):
            raise QueueError(
                f"Asset {asset_id} cannot be sent back from where it stands in the workflow"
                " (it is still to be labeled, or skipped)."
            )


def describe_lock_refusal(reasons: list[str]) -> str:
    """The backend's lock refusal reasons, in words."""
    return "; ".join(LOCK_REJECT_REASONS.get(reason, reason) for reason in reasons)


class LockKeeper:
    """Keeps a held asset locked to the member while their code works on it, however long it takes.

    The interface renews its lock every 30 s while the asset is open; a script's code may run for
    minutes on one asset, so a daemon thread does the renewing until the asset is let go.
    """

    def __init__(
        self,
        use_cases: QueueUseCases,
        context: QueueContext,
        asset_id: AssetId,
        every_seconds: float = RENEW_LOCK_EVERY_SECONDS,
    ) -> None:
        self._use_cases = use_cases
        self._context = context
        self._asset_id = asset_id
        self._every_seconds = every_seconds
        self._stopped = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self.lost_reasons: list[str] = []

    def start(self) -> None:
        """Start renewing in the background."""
        self._thread = threading.Thread(
            target=self._run, name=f"kili-queue-lock-{self._asset_id}", daemon=True
        )
        self._thread.start()

    def stop(self) -> None:
        """Stop renewing; returns once no renewal is in flight."""
        self._stopped.set()
        if self._thread is not None and self._thread is not threading.current_thread():
            self._thread.join()

    def _run(self) -> None:
        while not self._stopped.wait(self._every_seconds):
            try:
                reasons = self._use_cases.renew_lock(self._context, self._asset_id)
            except Exception as error:  # pylint: disable=broad-exception-caught
                # a network blip must not kill the thread: the lock outlives several missed renewals
                warnings.warn(
                    f"Could not renew the lock on asset {self._asset_id}: {error}. Retrying in"
                    f" {self._every_seconds:.0f} s.",
                    stacklevel=1,
                )
                continue
            if reasons and not self.lost_reasons:
                self.lost_reasons = reasons
                warnings.warn(
                    f"Asset {self._asset_id} is no longer yours: {describe_lock_refusal(reasons)}."
                    " Submitting it will be refused; give it back with release().",
                    stacklevel=1,
                )


def seconds_since(started_at: float) -> float:
    """Seconds elapsed since a `time.monotonic()` reading."""
    return time.monotonic() - started_at
