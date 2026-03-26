"""GraphQL Project Workflow operations."""


def get_update_project_workflow_mutation(fragment: str) -> str:
    """Return the GraphQL editProjectWorkflowSettings mutation."""
    return f"""
        mutation editProjectWorkflowSettings($input: EditProjectWorkflowSettingsInput!) {{
            data: editProjectWorkflowSettings(input: $input) {{
                {fragment}
            }}
        }}
        """


def get_steps_query(fragment: str) -> str:
    """Return the GraphQL getSteps query."""
    return f"""
        query getSteps($where: ProjectWhere!, $first: PageSize!, $skip: Int!) {{
            data: projects(where: $where, first: $first, skip: $skip) {{
            {fragment}
            }}
        }}
        """


def get_add_review_step_mutation() -> str:
    """Return the GraphQL addReviewStep mutation."""
    return """
        mutation addReviewStep($input: AddReviewStepInput!) {
            data: addReviewStep(input: $input) {
                id
                name
            }
        }
        """


def get_update_labeling_step_properties_mutation() -> str:
    """Return the GraphQL updateLabelingStepProperties mutation."""
    return """
        mutation updateLabelingStepProperties($input: UpdateLabelingStepPropertiesInput!) {
            data: updateLabelingStepProperties(input: $input) {
                id
                name
            }
        }
        """


def get_update_review_step_properties_mutation() -> str:
    """Return the GraphQL updateReviewStepProperties mutation."""
    return """
        mutation updateReviewStepProperties($input: UpdateReviewStepPropertiesInput!) {
            data: updateReviewStepProperties(input: $input) {
                id
                name
            }
        }
        """


def get_delete_step_mutation() -> str:
    """Return the GraphQL deleteStep mutation."""
    return """
        mutation deleteStep($input: DeleteStepInput!) {
            data: deleteStep(input: $input) {
                id
            }
        }
        """


def get_rename_step_mutation() -> str:
    """Return the GraphQL renameStep mutation."""
    return """
        mutation renameStep($input: RenameStepInput!) {
            data: renameStep(input: $input) {
                id
                name
            }
        }
        """
