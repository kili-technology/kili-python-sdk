"""Mixin extending Kili API Gateway class with Projects related operations."""

import warnings

from kili.adapters.kili_api_gateway.base import BaseOperationMixin
from kili.adapters.kili_api_gateway.helpers.queries import (
    QueryOptions,
    fragment_builder,
)
from kili.core.graphql.operations.project_user.queries import ProjectUserQuery, ProjectUserWhere
from kili.domain.project import ProjectId
from kili.domain.types import ListOrTuple
from kili.exceptions import NotFound

from .common import get_assignees_to_add_ids
from .mappers import (
    add_review_step_input_mapper,
    delete_step_input_mapper,
    project_input_mapper,
    rename_step_input_mapper,
    update_labeling_step_properties_input_mapper,
    update_review_step_properties_input_mapper,
)
from .operations import (
    get_add_review_step_mutation,
    get_delete_step_mutation,
    get_rename_step_mutation,
    get_steps_query,
    get_update_labeling_step_properties_mutation,
    get_update_project_workflow_mutation,
    get_update_review_step_properties_mutation,
)
from .types import (
    AddReviewStepInput,
    DeleteStepInput,
    ProjectWorkflowDataKiliAPIGatewayInput,
    RenameStepInput,
    UpdateLabelingStepPropertiesInput,
    UpdateReviewStepPropertiesInput,
)


class ProjectWorkflowOperationMixin(BaseOperationMixin):
    """Mixin extending Kili API Gateway class with Projects workflow related operations."""

    def update_project_workflow(
        self,
        project_id: ProjectId,
        project_workflow_data: ProjectWorkflowDataKiliAPIGatewayInput,
    ) -> dict:
        """Update properties in a project workflow."""
        project_workflow_input = project_input_mapper(data=project_workflow_data)

        fields = ["enforceStepSeparation", "steps{id}"]
        fragment = fragment_builder(fields)
        mutation = get_update_project_workflow_mutation(fragment)

        project_workflow_input["projectId"] = project_id

        variables = {"input": project_workflow_input}
        result = self.graphql_client.execute(mutation, variables)
        return result["data"]

    def get_steps(self, project_id: str, fields: ListOrTuple[str]) -> list[dict]:
        """Get steps in a project workflow."""
        fragment = fragment_builder(fields)
        query = get_steps_query(fragment)
        variables = {"where": {"id": project_id}, "first": 1, "skip": 0}
        result = self.graphql_client.execute(query, variables)
        project = result["data"]

        if len(project) == 0:
            raise NotFound(f"project ID: {project_id}. The project does not exist.")

        steps = project[0].get("steps")

        if len(steps) == 0:
            raise NotFound(
                f"project ID: {project_id}. The workflow v2 is not activated on this project."
            )

        return steps

    def count_activated_project_users(self, project_id: str) -> int:
        """Count project users with ACTIVATED status."""
        where = ProjectUserWhere(project_id=project_id, status="ACTIVATED", deleted=False)
        return ProjectUserQuery(self.graphql_client, self.http_client).count(where)

    def list_activated_project_users(self, project_id: str) -> list[dict]:
        """List project users with ACTIVATED status, returning role and user id."""
        where = ProjectUserWhere(project_id=project_id, status="ACTIVATED", deleted=False)
        return list(
            ProjectUserQuery(self.graphql_client, self.http_client)(
                where=where,
                fields=["role", "user.id", "user.email"],
                options=QueryOptions(disable_tqdm=True),
            )
        )

    def add_reviewers_to_step(
        self, project_id: str, step_name: str, emails: list[str]
    ) -> list[str]:
        """Add reviewers to a specific step."""
        existing_members = ProjectUserQuery(self.graphql_client, self.http_client)(
            where=ProjectUserWhere(project_id=project_id, status="ACTIVATED", deleted=False),
            fields=["role", "user.email", "user.id", "activated"],
            options=QueryOptions(None),
        )
        members_by_email = {m["user"]["email"]: m for m in (existing_members or [])}
        assignees_to_add = []
        assignees_added = []
        assignees_not_added = []
        for email in emails:
            member = members_by_email.get(email)

            if member and member.get("role") != "LABELER":
                user_id = member["user"]["id"]
                assignees_to_add.append(user_id)
                assignees_added.append(email)
            else:
                assignees_not_added.append(email)
        if assignees_not_added:
            warnings.warn(
                "These emails were not added (not found or can not review): "
                + ", ".join(assignees_not_added)
            )
        steps = self.get_steps(
            project_id, fields=["steps.id", "steps.name", "steps.type", "steps.assignees.id"]
        )
        target_step = next((s for s in steps if s.get("name") == step_name), None)
        if not target_step:
            raise ValueError(f"Step '{step_name}' not found in project workflow")
        if target_step.get("type") == "DEFAULT":
            raise ValueError("The step must be a review step, can't add reviewers to a label step")
        current_ids = [a["id"] for a in target_step.get("assignees", [])]

        merged_ids = list(dict.fromkeys(current_ids + assignees_to_add))

        self.update_project_workflow(
            project_id=ProjectId(project_id),
            project_workflow_data=ProjectWorkflowDataKiliAPIGatewayInput(
                None, None, [{"id": target_step["id"], "assignees": merged_ids}], None
            ),
        )
        return assignees_added

    def remove_reviewers_from_step(
        self, project_id: str, step_name: str, emails: list[str]
    ) -> list[str]:
        """Remove reviewers from a specific step."""
        steps = self.get_steps(
            project_id,
            fields=[
                "steps.id",
                "steps.name",
                "steps.type",
                "steps.assignees.id",
                "steps.assignees.email",
            ],
        )
        target_step = next((s for s in steps if s.get("name") == step_name), None)
        if not target_step:
            raise ValueError(f"Step '{step_name}' not found in project workflow")
        if target_step.get("type") == "DEFAULT":
            raise ValueError(
                "The step must be a review step, can't remove reviewers from a label step"
            )
        assignees = target_step.get("assignees", [])
        email_to_id = {a["email"]: a["id"] for a in assignees}
        removed_emails = []
        not_removed_emails = []
        ids_to_remove = []
        for email in emails:
            user_id = email_to_id.get(email)
            if not user_id:
                not_removed_emails.append(email)
                continue
            removed_emails.append(email)
            ids_to_remove.append(user_id)

        if ids_to_remove:
            new_assignees_ids = [
                a["id"] for a in assignees if a.get("id") and a["id"] not in ids_to_remove
            ]

            self.update_project_workflow(
                project_id=ProjectId(project_id),
                project_workflow_data=ProjectWorkflowDataKiliAPIGatewayInput(
                    None, None, [{"id": target_step["id"], "assignees": new_assignees_ids}], None
                ),
            )

        if not_removed_emails:
            warnings.warn(
                "These emails were not removed because they are not assigned to this step: "
                + ", ".join(not_removed_emails),
            )

        return removed_emails

    def add_review_step(self, data: AddReviewStepInput) -> dict:
        """Add a review step to a project workflow."""
        existing_members = self.list_activated_project_users(data.project_id)
        assignees_to_add = get_assignees_to_add_ids(existing_members, data.assignees)
        data.assignees = assignees_to_add
        variables = {"input": add_review_step_input_mapper(data)}
        mutation = get_add_review_step_mutation()
        result = self.graphql_client.execute(mutation, variables)
        steps = result.get("data", {}).get("steps", [])
        step = next((step for step in steps if step.get("name") == data.step_name), None)
        if not step:
            raise NotFound(f"Could not find the stepId of the step {data.step_name}.")
        return step

    def update_labeling_step_properties(self, data: UpdateLabelingStepPropertiesInput) -> dict:
        """Update properties of a labeling step."""
        variables = {"input": update_labeling_step_properties_input_mapper(data)}
        mutation = get_update_labeling_step_properties_mutation()
        result = self.graphql_client.execute(mutation, variables)
        steps = result.get("data", {}).get("steps", [])
        step = next((step for step in steps if step.get("id") == data.step_id), None)
        if not step:
            raise NotFound(f"Could not find the step with id {data.step_id}.")
        return step

    def update_review_step_properties(self, data: UpdateReviewStepPropertiesInput) -> dict:
        """Update properties of a review step."""
        if data.assignees is not None:
            existing_members = self.list_activated_project_users(data.project_id)
            assignees_to_add = get_assignees_to_add_ids(existing_members, data.assignees)
            data.assignees = assignees_to_add
        variables = {"input": update_review_step_properties_input_mapper(data)}
        mutation = get_update_review_step_properties_mutation()
        result = self.graphql_client.execute(mutation, variables)
        steps = result.get("data", {}).get("steps", [])
        step = next((step for step in steps if step.get("id") == data.step_id), None)
        if not step:
            raise NotFound(f"Could not find the step with id {data.step_id}.")
        return step

    def delete_step(self, data: DeleteStepInput) -> dict:
        """Delete a step from a project workflow."""
        variables = {"input": delete_step_input_mapper(data)}
        mutation = get_delete_step_mutation()
        result = self.graphql_client.execute(mutation, variables)
        return result["data"]

    def rename_step(self, data: RenameStepInput) -> dict:
        """Rename a step in a project workflow."""
        variables = {"input": rename_step_input_mapper(data)}
        mutation = get_rename_step_mutation()
        result = self.graphql_client.execute(mutation, variables)
        steps = result.get("data", {}).get("steps", [])
        step = next((step for step in steps if step.get("id") == data.step_id), None)
        if not step:
            raise NotFound(f"Could not find the step with id {data.step_id}.")
        return step
