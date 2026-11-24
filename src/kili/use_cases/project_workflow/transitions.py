"""Use cases of the transitions of a project workflow, for the domain client."""

from kili.domain.project import ProjectId
from kili.use_cases.base import BaseUseCases
from kili.use_cases.project_workflow.helpers import conditional_routing_required

TRANSITION_FIELDS = (
    "id",
    "fromStepId",
    "fromStepGroupId",
    "toStepId",
    "priority",
    "condition.type",
    "condition.percentage",
    "condition.jobName",
    "condition.categories",
    "condition.quantifier",
    "condition.value",
)


WORKFLOW_FIELDS = (
    "enforceStepSeparation",
    "usesConditionalRouting",
    "canEditTransitions",
    "steps.id",
    "steps.name",
    "steps.type",
    "steps.stepGroupId",
    "steps.sendBackStepId",
    "steps.sendBackToPreviousStep",
    "steps.stepCoverage",
    "steps.consensusCoverage",
    "steps.numberOfExpectedLabelsForConsensus",
    "steps.useHoneypot",
    "steps.assignees.id",
    "steps.assignees.email",
    "stepGroups.id",
    "stepGroups.name",
    "stepGroups.order",
    "stepGroups.allowedJobNames",
    *(f"workflowTransitions.{field}" for field in TRANSITION_FIELDS),
)


class WorkflowTransitionUseCases(BaseUseCases):
    """Transition use cases of the domain client."""

    def get_workflow(self, project_id: ProjectId) -> dict[str, object]:
        """Get the whole workflow of a project: its steps, step groups and transitions."""
        with conditional_routing_required("kili.projects.workflow.get()"):
            return self._kili_api_gateway.get_workflow(project_id, WORKFLOW_FIELDS)
