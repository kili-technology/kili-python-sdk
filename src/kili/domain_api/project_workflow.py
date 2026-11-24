"""Workflow namespaces of the projects domain, for the Kili Python SDK."""

from functools import cached_property
from typing import TYPE_CHECKING, Any, List, Optional

from typeguard import typechecked

from kili.domain.project import (
    ProjectId,
    WorkflowStepDesignation,
    WorkflowStepGroupToCreate,
    WorkflowStepGroupToUpdate,
    WorkflowStepToCreate,
    WorkflowStepUpdate,
)
from kili.use_cases.project_workflow import ProjectWorkflowUseCases
from kili.use_cases.project_workflow.step_groups import WorkflowStepGroupUseCases
from kili.utils.logcontext import for_all_methods, log_call_in_namespace

if TYPE_CHECKING:
    from kili.adapters.kili_api_gateway.kili_api_gateway import KiliAPIGateway
    from kili.client import Kili as KiliLegacy


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
    def groups(self) -> WorkflowGroupsNamespace:
        """Access the step groups of the workflow: `kili.projects.workflow.groups`.

        Returns:
            WorkflowGroupsNamespace instance for step group operations
        """
        return WorkflowGroupsNamespace(self._gateway)

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
    ) -> dict[str, Any]:
        """Update properties of a project workflow, its steps and its step groups, in one call.

        The server applies the changes in this order: step deletions, group deletions, group
        updates, step updates, group creations with their steps, step creations. It saves them all
        or none. The labeling interface settings of the workflow (navigation, skip, automatic
        assignment) are changed with `kili.projects.update_workflow_settings()`.

        Args:
            project_id: Id of the project.
            enforce_step_separation: Prevents the same user from being assigned to
                multiple steps in the workflow for a same asset,
                ensuring independent review and labeling processes
            create_steps: List of steps to create in the project workflow, assignees given by user
                id. In the multi-group workflow, each step gives the `step_group_id` of the group
                to create it in, and consensus can only be set on the labeling step of the first
                group. A step can be given an `id` (see below), for a step created after it to
                send back to it in `send_back_step_id`.
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

        The `id` given to a step or a group created is its id in Kili: it must be unique across
        Kili, and 5 to 32 characters long, such as `uuid.uuid4().hex`. Without one, the server
        chooses it.

        Returns:
            A dict with the changed properties which indicates if the mutation was successful,
                else an error message.

        Examples:
            >>> import uuid
            >>> kili.projects.workflow.update(
            ...     project_id="my_project",
            ...     create_step_groups=[
            ...         {
            ...             "id": uuid.uuid4().hex,
            ...             "name": "Experts",
            ...             "steps": [
            ...                 {"type": "DEFAULT", "name": "Labeling", "assignees": [labeler_id]},
            ...                 {
            ...                     "type": "REVIEW",
            ...                     "name": "Review",
            ...                     "assignees": [reviewer_id],
            ...                     "step_coverage": 100,
            ...                 },
            ...             ],
            ...         }
            ...     ],
            ... )
        """
        return ProjectWorkflowUseCases(self._gateway).update_project_workflow(
            project_id=ProjectId(project_id),
            enforce_step_separation=enforce_step_separation,
            create_steps=create_steps,
            update_steps=update_steps,
            delete_steps=delete_steps,
            create_step_groups=create_step_groups,
            update_step_groups=update_step_groups,
            delete_step_groups=delete_step_groups,
        )

    @typechecked
    def list(self, project_id: str) -> list[dict[str, Any]]:
        """Get steps in a project workflow.

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
