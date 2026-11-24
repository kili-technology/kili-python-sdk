"""Workflow namespaces of the projects domain, for the Kili Python SDK."""

import warnings
from functools import cached_property
from typing import TYPE_CHECKING, Any, List, Literal, Optional, Union

from typeguard import typechecked
from typing_extensions import deprecated

from kili.domain.project import (
    ProjectId,
    WorkflowStepDesignation,
    WorkflowStepGroupToCreate,
    WorkflowStepGroupToUpdate,
    WorkflowStepToCreate,
    WorkflowStepUpdate,
    WorkflowTransitionToCreate,
    WorkflowTransitionToUpdate,
)
from kili.use_cases.project_workflow import ProjectWorkflowUseCases
from kili.use_cases.project_workflow.step_groups import WorkflowStepGroupUseCases
from kili.use_cases.project_workflow.steps import WorkflowStepUseCases
from kili.use_cases.project_workflow.transitions import WorkflowTransitionUseCases
from kili.utils.logcontext import for_all_methods, log_call_in_namespace

if TYPE_CHECKING:
    from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
    from kili.client import Kili as KiliLegacy

STEP_COVERAGE_DEPRECATION = (
    "The step_coverage key of kili.projects.workflow.update() is deprecated and will be removed: a"
    " review's percentage is set at its creation by"
    " kili.projects.workflow.steps.create(sample_percentage=...), and changed by"
    " kili.projects.workflow.transitions.update() on the SAMPLE transition leading to it."
)
WORKFLOW_LIST_DEPRECATION = (
    "kili.projects.workflow.list() is deprecated and will be removed: use"
    " kili.projects.workflow.steps.list() instead, which answers the same."
)


@for_all_methods(log_call_in_namespace("projects.workflow.groups"), exclude=["__init__"])
class WorkflowGroupsNamespace:
    """Nested namespace for the step groups of a project workflow.

    Step groups only exist in the multi-group workflow: the server refuses to create, update or
    delete one on any other project. Each group has one labeling step, first, followed by at least
    one review. A group is given by its id or by its name.
    """

    def __init__(self, gateway: "KiliAPIGateway") -> None:
        """Initialize the step groups namespace.

        Args:
            gateway: The KiliAPIGateway instance for API operations
        """
        self._gateway = gateway

    @typechecked
    def list(self, project_id: str) -> list[dict[str, Any]]:
        """List the step groups of a project workflow.

        Args:
            project_id: Id of the project.

        Returns:
            One dict per group: its `id`, `name`, `order`, `allowedJobNames`, and its `steps`,
                each with its `id`, `name` and `type`.

        Examples:
            >>> kili.projects.workflow.groups.list(project_id="my_project")
        """
        return WorkflowStepGroupUseCases(self._gateway).list_step_groups(ProjectId(project_id))

    @typechecked
    def create(
        self,
        project_id: str,
        name: str,
        labeling_step_name: str,
        labelers: List[str],
        review_step_name: str,
        reviewers: List[str],
        sample_percentage: int,
        allowed_job_names: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """Create a step group after the last one, with its labeling step and its first review.

        The server saves a group only with its labeling step and at least one review, so both are
        created in the same call. Add other reviews with `kili.projects.workflow.steps.create()`.
        Multi-group workflow only.

        Args:
            project_id: Id of the project.
            name: Name of the group, unique in the project.
            labeling_step_name: Name of the labeling step of the group.
            labelers: Emails of the project members to assign to the labeling step.
            review_step_name: Name of the review step of the group.
            reviewers: Emails of the project members to assign to the review. Labelers cannot
                review: they are left out, with a warning.
            sample_percentage: Percentage of the assets labeled in the group that the review
                samples, from 0 to 100.
            allowed_job_names: Names of the jobs the steps of the group annotate. Every job when
                not given.

        Returns:
            The created group: its `id`, `name`, `order`, `allowedJobNames`, and its `steps`, each
                with its `id`, `name` and `type`.

        Examples:
            >>> kili.projects.workflow.groups.create(
            ...     project_id="my_project",
            ...     name="Experts",
            ...     labeling_step_name="Expert labeling",
            ...     labelers=["expert@acme.com"],
            ...     review_step_name="Expert review",
            ...     reviewers=["lead@acme.com"],
            ...     sample_percentage=100,
            ... )
        """
        return WorkflowStepGroupUseCases(self._gateway).create_step_group(
            ProjectId(project_id),
            name=name,
            labeling_step_name=labeling_step_name,
            labelers=labelers,
            review_step_name=review_step_name,
            reviewers=reviewers,
            sample_percentage=sample_percentage,
            allowed_job_names=allowed_job_names,
        )

    @typechecked
    def update(
        self,
        project_id: str,
        group: str,
        name: Optional[str] = None,
        allowed_job_names: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """Rename a step group, or change the jobs its steps annotate.

        Multi-group workflow only.

        Args:
            project_id: Id of the project.
            group: Id or name of the group.
            name: New name of the group, unique in the project.
            allowed_job_names: Names of the jobs the steps of the group annotate. An empty list
                allows every job.

        Returns:
            The updated group: its `id`, `name`, `order`, `allowedJobNames`, and its `steps`, each
                with its `id`, `name` and `type`.

        Examples:
            >>> kili.projects.workflow.groups.update(
            ...     project_id="my_project", group="Experts", allowed_job_names=["CLASSIFICATION"]
            ... )
        """
        return WorkflowStepGroupUseCases(self._gateway).update_step_group(
            ProjectId(project_id), group, name=name, allowed_job_names=allowed_job_names
        )

    @typechecked
    def delete(self, project_id: str, group: str) -> dict[str, str]:
        """Delete a step group with its steps.

        A project keeps at least one group. Multi-group workflow only.

        Args:
            project_id: Id of the project.
            group: Id or name of the group.

        Returns:
            A dict with the `id` of the deleted group.

        Examples:
            >>> kili.projects.workflow.groups.delete(project_id="my_project", group="Experts")
        """
        return WorkflowStepGroupUseCases(self._gateway).delete_step_group(
            ProjectId(project_id), group
        )


@for_all_methods(log_call_in_namespace("projects.workflow.steps"), exclude=["__init__"])
class WorkflowStepsNamespace:
    """Nested namespace for the steps of a project workflow.

    A step is given by its id, by its name when no other step of the project has it, or as
    `{"name": ..., "group_name": ...}`. Its assignees are changed with
    `kili.projects.workflow.add_reviewers()`, `add_labelers()` and their `remove_` pairs.
    """

    def __init__(self, gateway: "KiliAPIGateway") -> None:
        """Initialize the steps namespace.

        Args:
            gateway: The KiliAPIGateway instance for API operations
        """
        self._gateway = gateway

    @typechecked
    def list(self, project_id: str) -> list[dict[str, Any]]:
        """List the steps of a project workflow.

        Args:
            project_id: Id of the project.

        Returns:
            One dict per step: its `id`, `name`, `type` (`DEFAULT` for a labeling step, or
                `REVIEW`), `stepGroupId`, and its `assignees`, each with its `id` and `email`.

        Examples:
            >>> kili.projects.workflow.steps.list(project_id="my_project")
        """
        return WorkflowStepUseCases(self._gateway).list_steps(ProjectId(project_id))

    @typechecked
    def create(
        self,
        project_id: str,
        name: str,
        assignees: List[str],
        group_name: Optional[str] = None,
        type: Literal["DEFAULT", "REVIEW"] = "REVIEW",
        sample_percentage: Optional[int] = None,
        send_back_to_step: Optional[Union[str, WorkflowStepDesignation]] = None,
        consensus_coverage: Optional[int] = None,
        number_of_expected_labels_for_consensus: Optional[int] = None,
        use_honeypot: Optional[bool] = None,
        send_back_to_previous_step: Optional[bool] = None,
    ) -> dict[str, Any]:
        """Create a step at the end of its group.

        A review samples `sample_percentage` % of the assets completing the last step of its
        group; the others go on as before. A labeling step is accepted by the server only in a
        group that has no step yet, which it opens: a new group is created with its steps by
        `kili.projects.workflow.groups.create()`.

        Args:
            project_id: Id of the project.
            name: Name of the step, unique in its group.
            assignees: Emails of the project members to assign to the step. Labelers cannot
                review: they are left out of a review, with a warning.
            group_name: Name of the group to add the step to, in the multi-group workflow.
                Required when the project has several groups.
            type: `REVIEW`, or `DEFAULT` for a labeling step.
            sample_percentage: For a review, which requires it: the percentage of the assets it
                samples, from 0 to 100.
            send_back_to_step: For a review: the step to send its rejected assets back to, by
                id, by name, or as `{"name": ..., "group_name": ...}`.
            consensus_coverage: For a labeling step: percentage of the assets labeled for
                consensus, from 0 to 100. Only on the labeling step of the first group.
            number_of_expected_labels_for_consensus: For a labeling step: the number of labels
                each consensus asset gets.
            use_honeypot: For a review: whether it uses honeypot. Set a labeling step's with
                `update()` once it exists.
            send_back_to_previous_step: For a review: whether it sends its rejected assets back
                to the step each came from, which differs per asset where several steps lead to
                it. Not with `send_back_to_step`.

        Returns:
            The created step: its `id`, `name`, `type`, `stepGroupId` and `assignees`.

        Examples:
            >>> kili.projects.workflow.steps.create(
            ...     project_id="my_project",
            ...     name="Second review",
            ...     assignees=["reviewer@acme.com"],
            ...     group_name="Experts",
            ...     sample_percentage=20,
            ... )
        """
        return WorkflowStepUseCases(self._gateway).create_step(
            ProjectId(project_id),
            name=name,
            assignees=assignees,
            group_name=group_name,
            step_type=type,
            sample_percentage=sample_percentage,
            send_back_to_step=send_back_to_step,
            consensus_coverage=consensus_coverage,
            number_of_expected_labels_for_consensus=number_of_expected_labels_for_consensus,
            use_honeypot=use_honeypot,
            send_back_to_previous_step=send_back_to_previous_step,
        )

    @typechecked
    def update(
        self,
        project_id: str,
        step: Union[str, WorkflowStepDesignation],
        name: Optional[str] = None,
        consensus_coverage: Optional[int] = None,
        number_of_expected_labels_for_consensus: Optional[int] = None,
        use_honeypot: Optional[bool] = None,
        send_back_to_step: Optional[Union[str, WorkflowStepDesignation]] = None,
        send_back_to_previous_step: Optional[bool] = None,
    ) -> dict[str, Any]:
        """Update the properties of a step, in one call.

        A property that does not fit the step's type is refused. The assignees are changed with
        `kili.projects.workflow.add_reviewers()`, `add_labelers()` and their `remove_` pairs.

        Args:
            project_id: Id of the project.
            step: The step, by id, by name, or as `{"name": ..., "group_name": ...}`.
            name: New name of the step, unique in its group.
            consensus_coverage: For a labeling step: percentage of the assets labeled for
                consensus, from 0 to 100. Only on the labeling step of the first group.
            number_of_expected_labels_for_consensus: For a labeling step: the number of labels
                each consensus asset gets.
            use_honeypot: Whether the step uses honeypot. One step of the project at most does.
            send_back_to_step: For a review: the step to send its rejected assets back to, by
                id, by name, or as `{"name": ..., "group_name": ...}`.
            send_back_to_previous_step: For a review: whether it sends its rejected assets back
                to the step each came from, which differs per asset where several steps lead to
                it. Naming a step in `send_back_to_step` turns it off. Not `True` with
                `send_back_to_step`.

        Returns:
            The updated step: its `id`, `name`, `type`, `stepGroupId` and `assignees`.

        Examples:
            >>> kili.projects.workflow.steps.update(
            ...     project_id="my_project",
            ...     step={"name": "Review", "group_name": "Experts"},
            ...     name="Expert review",
            ...     send_back_to_step={"name": "Labeling", "group_name": "Experts"},
            ... )
        """
        return WorkflowStepUseCases(self._gateway).update_step(
            ProjectId(project_id),
            step,
            name=name,
            consensus_coverage=consensus_coverage,
            number_of_expected_labels_for_consensus=number_of_expected_labels_for_consensus,
            use_honeypot=use_honeypot,
            send_back_to_step=send_back_to_step,
            send_back_to_previous_step=send_back_to_previous_step,
        )

    @typechecked
    def delete(self, project_id: str, step: Union[str, WorkflowStepDesignation]) -> dict[str, str]:
        """Delete a step, wherever it is in its group.

        The server refuses a deletion that leaves a group without its labeling step or without a
        review: delete the group with `kili.projects.workflow.groups.delete()` instead.

        Args:
            project_id: Id of the project.
            step: The step, by id, by name, or as `{"name": ..., "group_name": ...}`.

        Returns:
            A dict with the `id` of the deleted step.

        Examples:
            >>> kili.projects.workflow.steps.delete(project_id="my_project", step="Second review")
        """
        return WorkflowStepUseCases(self._gateway).delete_step(ProjectId(project_id), step)


@for_all_methods(log_call_in_namespace("projects.workflow.transitions"), exclude=["__init__"])
class WorkflowTransitionsNamespace:
    """Nested namespace for the transitions of a project workflow.

    A transition says where an asset goes when a step completes, or when it reaches the end of a
    group: the transitions leaving a step are tried by priority, and the first whose condition
    holds is taken. Transitions are saved on projects of the multi-group workflow only. Saving
    transitions that route by conditions requires the organization's conditional routing feature
    (`lab_conditional_routing`); those keeping a chain of steps per group, such as a `SAMPLE`
    percentage changed, need nothing.

    Each method here sends every transition of the workflow, and the server then wires nothing
    itself: see `kili.projects.workflow.update()`.
    """

    def __init__(self, gateway: "KiliAPIGateway") -> None:
        """Initialize the transitions namespace.

        Args:
            gateway: The KiliAPIGateway instance for API operations
        """
        self._gateway = gateway

    @typechecked
    def list(self, project_id: str) -> list[dict[str, Any]]:
        """List the transitions of a project workflow.

        Args:
            project_id: Id of the project.

        Returns:
            One dict per transition: its `id`, the step it leaves (`fromStepId`) or the group
                whose end it leaves (`fromStepGroupId`), the step it leads to (`toStepId`, null
                when the asset leaves the workflow), its `priority`, and its `condition`: `type`,
                `percentage`, `jobName`, `categories`, `quantifier`, `value`.

        Examples:
            >>> kili.projects.workflow.transitions.list(project_id="my_project")
        """
        return WorkflowTransitionUseCases(self._gateway).list_transitions(ProjectId(project_id))

    @typechecked
    def create(
        self, project_id: str, transitions: List[WorkflowTransitionToCreate]
    ) -> dict[str, Any]:
        """Create transitions, keeping the stored ones.

        Args:
            project_id: Id of the project.
            transitions: The transitions to create, each from a step (`from_step`) or from the
                end of a group (`from_step_group`), to a step (`to_step`, or none to leave the
                workflow), with its `priority` and its `condition`, in snake_case (`type`,
                `percentage`, `job_name`, `categories`, `quantifier`, `value`). A step is given by
                id, by name, or as `{"name": ..., "group_name": ...}`; a group by id or name.

        Returns:
            A dict with the `transitions` of the workflow after the call, and the `warnings` of
                the server: what the change did beyond what it asked for.

        Examples:
            >>> kili.projects.workflow.transitions.create(
            ...     project_id="my_project",
            ...     transitions=[
            ...         {
            ...             "from_step": {"name": "Labeling", "group_name": "Team"},
            ...             "to_step": {"name": "Review", "group_name": "Experts"},
            ...             "priority": 1,
            ...             "condition": {
            ...                 "type": "CLASSIFICATION_INCLUDES",
            ...                 "job_name": "QUALITY",
            ...                 "categories": ["DOUBTFUL"],
            ...             },
            ...         }
            ...     ],
            ... )
        """
        return ProjectWorkflowUseCases(self._gateway).update_project_workflow(
            ProjectId(project_id), create_transitions=transitions
        )

    @typechecked
    def update(
        self, project_id: str, transitions: List[WorkflowTransitionToUpdate]
    ) -> dict[str, Any]:
        """Change the priority or the condition of stored transitions.

        A transition keeps its source and target: to change them, delete it and create another.
        It keeps its id too, and with it the outcomes of its samplings: an asset already drawn is
        not drawn again. A review's percentage is changed here, on the `SAMPLE` transition leading
        to it.

        Args:
            project_id: Id of the project.
            transitions: The transitions to change, each given by its `id`, with its new
                `priority` or `condition`.

        Returns:
            A dict with the `transitions` of the workflow after the call, and the `warnings` of
                the server: what the change did beyond what it asked for.

        Examples:
            >>> kili.projects.workflow.transitions.update(
            ...     project_id="my_project",
            ...     transitions=[
            ...         {"id": transition_id, "condition": {"type": "SAMPLE", "percentage": 50}}
            ...     ],
            ... )
        """
        return ProjectWorkflowUseCases(self._gateway).update_project_workflow(
            ProjectId(project_id), update_transitions=transitions
        )

    @typechecked
    def delete(self, project_id: str, transition_ids: List[str]) -> dict[str, Any]:
        """Delete transitions, keeping the others.

        Args:
            project_id: Id of the project.
            transition_ids: Ids of the transitions to delete.

        Returns:
            A dict with the `transitions` of the workflow after the call, and the `warnings` of
                the server: what the change did beyond what it asked for.

        Examples:
            >>> kili.projects.workflow.transitions.delete(
            ...     project_id="my_project", transition_ids=[transition_id]
            ... )
        """
        return ProjectWorkflowUseCases(self._gateway).update_project_workflow(
            ProjectId(project_id), delete_transitions=transition_ids
        )


@for_all_methods(log_call_in_namespace("projects.workflow"), exclude=["__init__"])
class WorkflowNamespace:
    """Nested namespace for project workflow operations."""

    def __init__(self, client: "KiliLegacy", gateway: Optional["KiliAPIGateway"] = None) -> None:
        """Initialize workflow namespace.

        Args:
            client: The Kili client instance
            gateway: The KiliAPIGateway instance for API operations, the client's by default
        """
        self._client = client
        self._gateway = gateway if gateway is not None else client.kili_api_gateway

    @cached_property
    def steps(self) -> WorkflowStepsNamespace:
        """Access the steps of the workflow: `kili.projects.workflow.steps`.

        Returns:
            WorkflowStepsNamespace instance for step operations
        """
        return WorkflowStepsNamespace(self._gateway)

    @cached_property
    def groups(self) -> WorkflowGroupsNamespace:
        """Access the step groups of the workflow: `kili.projects.workflow.groups`.

        Returns:
            WorkflowGroupsNamespace instance for step group operations
        """
        return WorkflowGroupsNamespace(self._gateway)

    @cached_property
    def transitions(self) -> WorkflowTransitionsNamespace:
        """Access the transitions of the workflow: `kili.projects.workflow.transitions`.

        Returns:
            WorkflowTransitionsNamespace instance for transition operations
        """
        return WorkflowTransitionsNamespace(self._gateway)

    @typechecked
    def get(self, project_id: str) -> dict[str, Any]:
        """Get the whole workflow of a project, in one query.

        Args:
            project_id: Id of the project.

        Returns:
            A dict with:

            - `steps`: each with its `id`, `name`, `type` (`DEFAULT` for a labeling step, or
              `REVIEW`), `stepGroupId`, `sendBackStepId`, `sendBackToPreviousStep`,
              `stepCoverage`, `consensusCoverage`, `numberOfExpectedLabelsForConsensus`,
              `useHoneypot` and `assignees`.
            - `stepGroups`: each with its `id`, `name`, `order` and `allowedJobNames`.
            - `workflowTransitions`: where an asset goes when a step completes, or when it
              reaches the end of a group. Each has its `id`, the step it leaves (`fromStepId`) or
              the group whose end it leaves (`fromStepGroupId`), the step it leads to
              (`toStepId`, null when the asset leaves the workflow), its `priority`, and its
              `condition`: `type`, `percentage`, `jobName`, `categories`, `quantifier`, `value`.
            - `usesConditionalRouting`: whether the project routes its assets otherwise than a
              chain of steps per group, which only a user who `canEditTransitions` edits.
            - `canEditTransitions`: whether you can save transitions that route by conditions.
            - `enforceStepSeparation`.

        Examples:
            >>> workflow = kili.projects.workflow.get(project_id="my_project")
            >>> workflow["workflowTransitions"]
        """
        return WorkflowTransitionUseCases(self._gateway).get_workflow(ProjectId(project_id))

    @typechecked
    def update(
        self,
        project_id: str,
        enforce_step_separation: Optional[bool] = None,
        create_steps: Optional[list[WorkflowStepToCreate]] = None,
        update_steps: Optional[list[WorkflowStepUpdate]] = None,
        delete_steps: Optional[list[str | WorkflowStepDesignation]] = None,
        create_step_groups: Optional[list[WorkflowStepGroupToCreate]] = None,
        update_step_groups: Optional[list[WorkflowStepGroupToUpdate]] = None,
        delete_step_groups: Optional[list[str]] = None,
        create_transitions: Optional[list[WorkflowTransitionToCreate]] = None,
        update_transitions: Optional[list[WorkflowTransitionToUpdate]] = None,
        delete_transitions: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """Update a project workflow, its steps, its step groups and its transitions, in one call.

        The server applies the changes in this order: step deletions, group deletions, group
        updates, step updates, group creations with their steps, step creations, then the
        transitions. It saves them all or none. The labeling interface settings of the workflow
        (navigation, skip, automatic assignment) are changed with
        `kili.projects.update_workflow_settings()`.

        A call is in one of two modes:

        - Without any transition list, the server wires every step and group change itself: a
          new review is sampled after the last step of its group, a new group is reached after
          the last one, what followed a deleted step follows what preceded it.
        - With one, even empty, the call is explicit for all its changes: the server wires
          nothing, and saves the transitions as the call leaves them. The call then gives the
          transition into each review it creates, the entry and the default (`ALWAYS`)
          transition of each group it creates, and reconnects what followed a step it deletes.
          It gives no `step_coverage`: a percentage is a `SAMPLE` condition. The SDK sends the
          stored transitions with their ids, less those deleted and those leaving or entering a
          step or group deleted, with their updates, and the created ones.

        Transitions are saved on projects of the multi-group workflow only. Saving transitions
        that route by conditions requires the organization's conditional routing feature
        (`lab_conditional_routing`); those keeping a chain of steps per group, such as a `SAMPLE`
        percentage changed, need nothing.

        Args:
            project_id: Id of the project.
            enforce_step_separation: Prevents the same user from being assigned to
                multiple steps in the workflow for a same asset,
                ensuring independent review and labeling processes
            create_steps: List of steps to create in the project workflow, assignees given by user
                id. In the multi-group workflow, each step gives the `step_group_id` of the group
                to create it in, and consensus can only be set on the labeling step of the first
                group. A step can be given an `id` (see below), for a step created after it to
                send back to it in `send_back_step_id`. Its `step_coverage` is deprecated, here
                and in `update_steps`: see `kili.projects.workflow.steps.create()` and
                `kili.projects.workflow.transitions.update()`.
            update_steps: List of steps to update in the project workflow, each given by its `id`,
                or by its `name` with `group_name` when several groups use that name.
            delete_steps: List of steps to delete from the project workflow, each given by its ID,
                by its name, or as `{"name": ..., "group_name": ...}` when several groups use
                that name.
            create_step_groups: List of step groups to create after the last one, in the
                multi-group workflow, each with its `name`, its `steps` (its labeling step, then at
                least one review, as in `create_steps` without `step_group_id`), and optionally
                its `allowed_job_names` and an `id` (see below), for a step of `create_steps` to
                name the group in `step_group_id`.
            update_step_groups: List of step groups to update, each given by its `id`, with its
                new `name` or `allowed_job_names`.
            delete_step_groups: List of step groups to delete with their steps, each given by its
                id or its name.
            create_transitions: List of transitions to create, as in
                `kili.projects.workflow.transitions.create()`. A step or a group created in the
                same call is named by its `id`, or by its name.
            update_transitions: List of stored transitions to change, as in
                `kili.projects.workflow.transitions.update()`.
            delete_transitions: List of the ids of stored transitions to delete.

        The `id` given to a step or a group created is its id in Kili: it must be unique across
        Kili, and 5 to 32 characters long, such as `uuid.uuid4().hex`. Without one, the server
        chooses it.

        Returns:
            A dict with the changed properties which indicates if the mutation was successful,
                else an error message. With a transition list, it also has the `transitions` of
                the workflow after the call, and the `warnings` of the server: what the change
                did beyond what it asked for.

        Examples:
            >>> # Without transitions: the server wires the changes
            >>> kili.projects.workflow.update(
            ...     project_id="my_project",
            ...     update_steps=[{"id": step_id, "name": "Expert review"}],
            ...     delete_step_groups=["Juniors"],
            ... )
            >>> # With them: a new group, which the end of "Experts" leads to for doubtful assets
            >>> kili.projects.workflow.update(
            ...     project_id="my_project",
            ...     create_step_groups=[
            ...         {
            ...             "name": "Audit",
            ...             "steps": [
            ...                 {"type": "DEFAULT", "name": "Audit labeling", "assignees": [labeler]},
            ...                 {"type": "REVIEW", "name": "Audit review", "assignees": [reviewer]},
            ...             ],
            ...         }
            ...     ],
            ...     update_transitions=[{"id": experts_default_transition_id, "priority": 2}],
            ...     create_transitions=[
            ...         {
            ...             "from_step_group": "Experts",
            ...             "to_step": "Audit labeling",
            ...             "priority": 1,
            ...             "condition": {
            ...                 "type": "CLASSIFICATION_INCLUDES",
            ...                 "job_name": "QUALITY",
            ...                 "categories": ["DOUBTFUL"],
            ...             },
            ...         },
            ...         {
            ...             "from_step": "Audit labeling",
            ...             "to_step": "Audit review",
            ...             "priority": 1,
            ...             "condition": {"type": "SAMPLE", "percentage": 100},
            ...         },
            ...         {
            ...             "from_step_group": "Audit",
            ...             "priority": 1,
            ...             "condition": {"type": "ALWAYS"},
            ...         },
            ...     ],
            ... )
        """
        steps_given = [
            *(create_steps or []),
            *(update_steps or []),
            *(step for group in create_step_groups or [] for step in group["steps"]),
        ]
        if any(step.get("step_coverage") is not None for step in steps_given):
            # Past the logging wrapper, to the caller's line
            warnings.warn(STEP_COVERAGE_DEPRECATION, DeprecationWarning, stacklevel=3)
        return ProjectWorkflowUseCases(self._gateway).update_project_workflow(
            project_id=ProjectId(project_id),
            enforce_step_separation=enforce_step_separation,
            create_steps=create_steps,
            update_steps=update_steps,
            delete_steps=delete_steps,
            create_step_groups=create_step_groups,
            update_step_groups=update_step_groups,
            delete_step_groups=delete_step_groups,
            create_transitions=create_transitions,
            update_transitions=update_transitions,
            delete_transitions=delete_transitions,
        )

    @deprecated(WORKFLOW_LIST_DEPRECATION)
    @typechecked
    def list(self, project_id: str) -> list[dict[str, Any]]:
        """Get steps in a project workflow.

        Deprecated: use `kili.projects.workflow.steps.list()`, which answers the same.

        Args:
            project_id: Id of the project.

        Returns:
            A list with the steps of the project workflow.
        """
        return self._client.get_steps(project_id=project_id)

    @typechecked
    def add_reviewers(
        self,
        project_id: str,
        step_name: Optional[str] = None,
        emails: Optional[List[str]] = None,
        group_name: Optional[str] = None,
        step_id: Optional[str] = None,
    ) -> List[str]:
        """Add reviewers to a specific step.

        Args:
            project_id: Id of the project.
            step_name: Name of the step. Exclusive with `step_id`.
            emails: List of emails to add.
            group_name: Name of the group containing the step named `step_name`, in the multi-group
                workflow.
                Required when several groups have a step with the same name.
            step_id: Id of the step. Exclusive with `step_name` and `group_name`.

        Returns:
            A list with emails added to the step.
        """
        return self._client.add_reviewers_to_step(
            project_id=project_id,
            step_name=step_name,
            emails=emails,
            group_name=group_name,
            step_id=step_id,
        )

    @typechecked
    def remove_reviewers(
        self,
        project_id: str,
        step_name: Optional[str] = None,
        emails: Optional[List[str]] = None,
        group_name: Optional[str] = None,
        step_id: Optional[str] = None,
    ) -> List[str]:
        """Remove reviewers from a specific step.

        Args:
            project_id: Id of the project.
            step_name: Name of the step. Exclusive with `step_id`.
            emails: List of emails to remove.
            group_name: Name of the group containing the step named `step_name`, in the multi-group
                workflow.
                Required when several groups have a step with the same name.
            step_id: Id of the step. Exclusive with `step_name` and `group_name`.

        Returns:
            A list with emails removed from the step.
        """
        return self._client.remove_reviewers_from_step(
            project_id=project_id,
            step_name=step_name,
            emails=emails,
            group_name=group_name,
            step_id=step_id,
        )

    @typechecked
    def add_labelers(
        self,
        project_id: str,
        step_name: Optional[str] = None,
        emails: Optional[List[str]] = None,
        group_name: Optional[str] = None,
        step_id: Optional[str] = None,
    ) -> List[str]:
        """Add labelers to a specific labeling step.

        Only the multi-group workflow supports assigning labelers to a step, and the target step
        must be a labeling step.

        Args:
            project_id: Id of the project.
            step_name: Name of the labeling step. Exclusive with `step_id`.
            emails: List of emails to add.
            group_name: Name of the group containing the step named `step_name`, in the multi-group
                workflow.
                Required when several groups have a step with the same name.
            step_id: Id of the step. Exclusive with `step_name` and `group_name`.

        Returns:
            A list with emails added to the step.
        """
        return self._client.add_labelers_to_step(
            project_id=project_id,
            step_name=step_name,
            emails=emails,
            group_name=group_name,
            step_id=step_id,
        )

    @typechecked
    def remove_labelers(
        self,
        project_id: str,
        step_name: Optional[str] = None,
        emails: Optional[List[str]] = None,
        group_name: Optional[str] = None,
        step_id: Optional[str] = None,
    ) -> List[str]:
        """Remove labelers from a specific labeling step.

        Only the multi-group workflow supports removing labelers from a step, and the target step
        must be a labeling step. Removing a labeler also clears their asset-step assignments and
        step queue for that step.

        Args:
            project_id: Id of the project.
            step_name: Name of the labeling step. Exclusive with `step_id`.
            emails: List of emails to remove.
            group_name: Name of the group containing the step named `step_name`, in the multi-group
                workflow.
                Required when several groups have a step with the same name.
            step_id: Id of the step. Exclusive with `step_name` and `group_name`.

        Returns:
            A list with emails removed from the step.
        """
        return self._client.remove_labelers_from_step(
            project_id=project_id,
            step_name=step_name,
            emails=emails,
            group_name=group_name,
            step_id=step_id,
        )

    @typechecked
    def copy_from_project(
        self,
        destination_project_id: str,
        source_project_id: str,
    ) -> dict[str, Any]:
        """Copy the workflow from a source project to a destination project.

        Copies all workflow steps with their configurations (consensus, coverage,
        sendBackStepId) from the source project. Assignees are not copied.

        The destination project must have no labels. Existing workflow steps in the
        destination project will be deleted and replaced by the source workflow.

        Args:
            destination_project_id: Id of the destination project to copy the workflow to.
            source_project_id: Id of the source project to copy the workflow from.

        Returns:
            A dict with the workflow data which indicates if the mutation was successful,
                else an error message.

        Raises:
            ValueError: If the source project has no workflow steps, or if the
                destination project already has labels.

        Examples:
            >>> kili.projects.workflow.copy_from_project(
            ...     destination_project_id="destination_project_id",
            ...     source_project_id="source_project_id",
            ... )
        """
        return self._client.copy_workflow_from_project(
            destination_project_id=destination_project_id,
            source_project_id=source_project_id,
        )
